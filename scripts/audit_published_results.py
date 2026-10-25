"""Validate committed aggregate OULAD tables; do not infer raw-data replication.

This module deliberately relies on the Python standard library and checks
schema, ranges, repeated comparison keys, and numerical consistency only.
Passing these checks cannot establish the origin or correctness of the models.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def rows(filename: str) -> list[dict[str, str]]:
    with (RESULTS / filename).open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def number(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    if not math.isfinite(value):
        raise ValueError(f"Nonfinite {key} in {row}")
    return value


def audit() -> dict[str, object]:
    primary = rows("primary_models.csv")
    by_model = {r["model"]: r for r in primary}
    expected = {"prevalence", "logistic_l2", "random_forest", "xgboost"}
    assert set(by_model) == expected and len(primary) == 4
    n_test = {int(r["n"]) for r in primary}
    assert n_test == {7239}, n_test
    prevalence = number(by_model["prevalence"], "prevalence")
    assert all(abs(number(r, "prevalence") - prevalence) < 1e-9 for r in primary)
    for r in primary:
        for metric in ("AP", "AUC", "Brier", "LogLoss"):
            assert 0 <= number(r, metric) <= 1, (r["model"], metric)
    assert abs(number(by_model["prevalence"], "AP") - prevalence) < 1e-6
    ap_delta = number(by_model["xgboost"], "AP") - number(by_model["logistic_l2"], "AP")
    brier_delta = number(by_model["xgboost"], "Brier") - number(by_model["logistic_l2"], "Brier")
    assert 0.021 < ap_delta < 0.023
    assert -0.006 < brier_delta < -0.004

    transfer = rows("leave_one_module_out.csv")
    modules = {}
    for r in transfer:
        modules.setdefault(r["heldout_module"], {})[r["model"]] = r
        for metric in ("AP", "AUC", "Brier"):
            assert 0 <= number(r, metric) <= 1
    assert len(transfer) == 14 and set(modules) == {letter * 3 for letter in "ABCDEFG"}
    ap_wins_xgb, brier_wins_logistic = 0, 0
    for module, pair in modules.items():
        assert set(pair) == {"logistic_l2", "xgboost"}, module
        assert int(pair["logistic_l2"]["n"]) == int(pair["xgboost"]["n"])
        ap_wins_xgb += number(pair["xgboost"], "AP") > number(pair["logistic_l2"], "AP")
        brier_wins_logistic += number(pair["xgboost"], "Brier") > number(pair["logistic_l2"], "Brier")
    assert (ap_wins_xgb, brier_wins_logistic) == (6, 5)

    associations = rows("econometric_associations.csv")
    assert len(associations) == 3
    for r in associations:
        estimate = number(r, "LPM_beta")
        assert number(r, "HC3_CI_lower") <= estimate <= number(r, "HC3_CI_upper")
        assert number(r, "cluster_CI_lower") <= estimate <= number(r, "cluster_CI_upper")

    ablation = rows("feature_ablation.csv")
    assert len(ablation) == 4
    assert {r["feature_set"] for r in ablation} == {"all", "behavior_only"}
    assert {r["model"] for r in ablation} == {"xgboost", "logistic_l2"}
    for r in ablation:
        for metric in ("AP", "AUC", "Brier"):
            assert 0 <= number(r, metric) <= 1

    sensitivity = rows("prediction_cutoff_sensitivity.csv")
    assert len(sensitivity) == 4
    assert {int(r["cutoff_day"]) for r in sensitivity} == {14, 42}
    assert {r["model"] for r in sensitivity} == {"xgboost", "logistic_l2"}

    temporal = rows("temporal_2013_to_2014.csv")
    assert len(temporal) == 2
    assert {r["model"] for r in temporal} == {"xgboost", "logistic_l2"}
    assert {int(r["train_n"]) for r in temporal} == {11685}
    assert {int(r["test_n"]) for r in temporal} == {13150}

    return {
        "verification_scope": "AGGREGATE_TABLE_CONSISTENCY_ONLY",
        "raw_data_replication_performed": False,
        "n_holdout": 7239,
        "holdout_prevalence": prevalence,
        "ap_delta_xgboost_minus_logistic": ap_delta,
        "brier_delta_xgboost_minus_logistic": brier_delta,
        "modules_xgboost_better_AP": ap_wins_xgb,
        "modules_logistic_better_Brier": brier_wins_logistic,
        "files_validated": 6,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
