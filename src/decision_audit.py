"""Post-hoc decision-reliability audit for OULAD held-out predictions.

The audit is not an intervention, causal estimator, fairness certificate or
claim that a risk-score threshold is safe to deploy. It consumes the locally
ignored holdout_predictions.csv from src.empirical and writes aggregate-only
statistics. Original student identifiers are never written to output files.

An accompanying manifest.json is mandatory. Synthetic fixtures require the
explicit --demo flag so invented examples cannot be mistaken for OULAD results.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit
from sklearn.metrics import (
    average_precision_score, brier_score_loss, log_loss, roc_auc_score,
)

MODEL_COLUMNS = ("p_prevalence", "p_logistic_l2", "p_random_forest", "p_xgboost")
KEY_COLUMNS = {"student_id", "course_presentation", "y_true"}
REAL_STATUS = "HISTORICAL_OULAD_OBSERVATIONAL_ANALYSIS"
DEMO_STATUS = "SYNTHETIC_SOFTWARE_DEMONSTRATION_ONLY"


def _valid(frame: pd.DataFrame) -> list[str]:
    required = KEY_COLUMNS | {"p_logistic_l2", "p_xgboost"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    unexpected = set(frame.columns) - KEY_COLUMNS - set(MODEL_COLUMNS)
    if unexpected:
        raise ValueError(
            "Input must contain predictions and partition keys only; "
            f"unexpected columns: {sorted(unexpected)}"
        )
    if frame.isna().any().any():
        raise ValueError("No missing IDs, groups, outcomes or probabilities allowed")
    if frame.student_id.astype(str).duplicated().any():
        raise ValueError("Holdout must contain only one row per student")
    if frame.course_presentation.astype(str).nunique() < 2:
        raise ValueError("At least two independent presentation groups required")
    labels = frame["y_true"].to_numpy()
    if not set(np.unique(labels)).issubset({0, 1}) or len(np.unique(labels)) != 2:
        raise ValueError("Binary outcomes of both classes are required")
    models = [column for column in MODEL_COLUMNS if column in frame]
    for name in models:
        p = frame[name].to_numpy(dtype=float)
        if not (np.isfinite(p).all() and ((0 <= p) & (p <= 1)).all()):
            raise ValueError(f"{name}: probabilities must be finite and within [0,1]")
    return models


def tie_averaged_top_k(y_true: np.ndarray, probabilities: np.ndarray, k: int) -> dict:
    """Expected hits if boundary ties are broken uniformly at random.

    This avoids arbitrary ordering of identical model probabilities. It is a
    descriptive mathematical expectation, not a causal intervention estimate.
    """
    y = np.asarray(y_true, dtype=float)
    p = np.asarray(probabilities, dtype=float)
    if not 1 <= k <= len(y):
        raise ValueError("k must be between one and sample size")
    threshold = float(np.partition(p, len(p) - k)[len(p) - k])
    above = p > threshold
    equal = p == threshold
    remaining = int(k - above.sum())
    expected_hits = float(y[above].sum() + remaining * y[equal].mean())
    positives = y.sum()
    return {
        "alerts": int(k),
        "score_boundary": threshold,
        "boundary_ties": int(equal.sum()),
        "expected_true_positives": expected_hits,
        "expected_ppv": expected_hits / k,
        "expected_recall": expected_hits / positives if positives else np.nan,
    }


def calibration_intercept_slope(y_true: np.ndarray, probabilities: np.ndarray) -> tuple:
    """Fit logistic recalibration as a diagnostic on held-out scores only.

    Apparent diagnostic intercept/slope; no updated probabilities are deployed.
    Models with nearly constant scores cannot identify the slope.
    """
    p = np.clip(np.asarray(probabilities, dtype=float), 1e-6, 1 - 1e-6)
    logits = np.log(p / (1 - p))
    if np.std(logits) < 1e-8:
        return np.nan, np.nan
    y = np.asarray(y_true, dtype=float)
    x = np.column_stack([np.ones(len(y)), logits])

    def loss(theta: np.ndarray) -> tuple[float, np.ndarray]:
        linear = x @ theta
        negative_ll = np.logaddexp(0, linear).sum() - np.dot(y, linear)
        gradient = x.T @ (expit(linear) - y)
        return float(negative_ll), gradient

    result = minimize(
        loss, x0=np.array([0., 1.]), method="L-BFGS-B",
        jac=True, options={"maxiter": 500},
    )
    if not result.success:
        return np.nan, np.nan
    return float(result.x[0]), float(result.x[1])


def _scores(y: np.ndarray, p: np.ndarray) -> dict:
    record = {
        "n": int(len(y)),
        "prevalence": float(np.mean(y)),
        "predicted_mean": float(np.mean(p)),
        "observed_minus_predicted": float(np.mean(y) - np.mean(p)),
        "average_precision": float(average_precision_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
    }
    record["roc_auc"] = float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else np.nan
    return record


def _paired_cluster_bootstrap(
    frame: pd.DataFrame, *, replicates: int, seed: int,
) -> pd.DataFrame:
    """Presentation-resampled paired differences; few-cluster warning applies."""
    groups = frame.course_presentation.astype(str).to_numpy()
    unique = np.unique(groups)
    if len(unique) < 3:
        raise ValueError("At least three groups required for exploratory bootstrap")
    partitions = {g: np.flatnonzero(groups == g) for g in unique}
    labels = frame.y_true.to_numpy(dtype=int)
    lr = frame.p_logistic_l2.to_numpy(dtype=float)
    xgb = frame.p_xgboost.to_numpy(dtype=float)
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(replicates):
        sampled_groups = rng.choice(unique, size=len(unique), replace=True)
        ix = np.concatenate([partitions[group] for group in sampled_groups])
        y = labels[ix]
        if y.min() == y.max():
            continue
        rows.append({
            "ap_delta_xgb_minus_logistic": float(
                average_precision_score(y, xgb[ix]) -
                average_precision_score(y, lr[ix])
            ),
            "brier_delta_xgb_minus_logistic": float(
                brier_score_loss(y, xgb[ix]) -
                brier_score_loss(y, lr[ix])
            ),
        })
    if len(rows) < max(10, math.ceil(0.50 * replicates)):
        raise ValueError("Too many bootstrap draws contained only one outcome class")
    return pd.DataFrame(rows)


def audit_predictions(
    frame: pd.DataFrame,
    *,
    capacity_fractions: tuple[float, ...] = (0.05, 0.10, 0.20),
    min_bin_n: int = 30,
    min_course_n: int = 100,
    bootstrap_replicates: int = 400,
    seed: int = 2026,
) -> dict[str, pd.DataFrame]:
    """Return aggregate-only tables without learner identifiers.

    The caller must validate the accompanying input provenance manifest before
    publishing these outputs; this function does not infer data authenticity.
    """
    models = _valid(frame)
    if not all(0 < k <= 1 for k in capacity_fractions):
        raise ValueError("Capacity fractions must be in (0,1]")
    if min_bin_n < 30 or min_course_n < 30:
        raise ValueError("Minimum reported aggregate cell size must be >=30")
    if bootstrap_replicates < 30:
        raise ValueError("Need at least 30 bootstrap replicates")

    y = frame.y_true.to_numpy(dtype=int)
    sample_n = len(y)
    metrics, allocation, bins, courses = [], [], [], []

    for model in models:
        p = frame[model].to_numpy(dtype=float)
        intercept, slope = calibration_intercept_slope(y, p)
        metrics.append({
            "model": model[2:], **_scores(y, p),
            "calibration_intercept_diagnostic": intercept,
            "calibration_slope_diagnostic": slope,
        })
        for fraction in capacity_fractions:
            k = max(1, math.ceil(sample_n * fraction))
            row = tie_averaged_top_k(y, p, k)
            allocation.append({
                "model": model[2:], "capacity_fraction": fraction,
                **row, "lift_over_prevalence": row["expected_ppv"] / y.mean(),
                "decision_scope": "RANKING_AUDIT_NO_INTERVENTION_ESTIMATE",
            })

        bin_index = np.minimum(np.floor(p * 10).astype(int), 9)
        for bin_number in range(10):
            selection = bin_index == bin_number
            if int(selection.sum()) < min_bin_n:
                continue
            bins.append({
                "model": model[2:],
                "bin_lower": bin_number / 10,
                "bin_upper": (bin_number + 1) / 10,
                "n": int(selection.sum()),
                "mean_prediction": float(p[selection].mean()),
                "observed_rate": float(y[selection].mean()),
                "absolute_gap": float(abs(p[selection].mean() - y[selection].mean())),
            })

        for group, subset in frame.groupby("course_presentation", dropna=False):
            yy = subset.y_true.to_numpy(dtype=int)
            if len(yy) < min_course_n or min(yy.sum(), len(yy) - yy.sum()) < 10:
                continue
            pp = subset[model].to_numpy(dtype=float)
            courses.append({
                "model": model[2:],
                "course_presentation": str(group), **_scores(yy, pp),
                "note": "HISTORICAL_OULAD_WITHIN_DATASET_HOLDOUT",
            })

    boot = _paired_cluster_bootstrap(
        frame, replicates=bootstrap_replicates, seed=seed,
    )
    diff_summary = []
    for name in boot:
        vals = boot[name].to_numpy()
        yy = y
        main = (
            average_precision_score(yy, frame.p_xgboost) -
            average_precision_score(yy, frame.p_logistic_l2)
            if name.startswith("ap_") else
            brier_score_loss(yy, frame.p_xgboost) -
            brier_score_loss(yy, frame.p_logistic_l2)
        )
        diff_summary.append({
            "metric": name,
            "point_difference": float(main),
            "bootstrap_2_5_percent": float(np.quantile(vals, .025)),
            "bootstrap_median": float(np.quantile(vals, .5)),
            "bootstrap_97_5_percent": float(np.quantile(vals, .975)),
            "valid_replicates": int(len(vals)),
            "heldout_presentations": int(frame.course_presentation.nunique()),
            "uncertainty_label": "EXPLORATORY_SMALL_NUMBER_OF_CLUSTERS",
        })
    return {
        "model_summaries": pd.DataFrame(metrics),
        "capacity_audit": pd.DataFrame(allocation),
        "calibration_bins": pd.DataFrame(bins),
        "course_diagnostics": pd.DataFrame(courses),
        "paired_cluster_bootstrap": pd.DataFrame(diff_summary),
    }


def run(
    predictions_path: Path, output_dir: Path, *,
    manifest_path: Path | None = None, demo: bool = False,
    bootstrap_replicates: int = 400, seed: int = 2026,
) -> dict:
    predictions_path = Path(predictions_path)
    manifest_path = Path(manifest_path or predictions_path.parent / "manifest.json")
    if not manifest_path.exists():
        raise FileNotFoundError("Study provenance manifest.json is required")
    origin = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_status = DEMO_STATUS if demo else REAL_STATUS
    if origin.get("study_status") != expected_status:
        raise ValueError(
            "Prediction source status and --demo flag disagree. "
            "Never report synthetic software fixtures as empirical evidence."
        )
    frame = pd.read_csv(predictions_path, dtype={"student_id": str})
    _valid(frame)
    if len(frame) != int(origin.get("n_test", -1)):
        raise ValueError("Holdout count disagrees with original empirical manifest")
    if frame.course_presentation.nunique() != int(
        origin.get("n_heldout_presentations", -1)
    ):
        raise ValueError("Presentation count disagrees with original empirical manifest")
    tables = audit_predictions(
        frame, bootstrap_replicates=bootstrap_replicates, seed=seed,
    )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_csv(output_dir / f"{name}.csv", index=False)
    sha = hashlib.sha256(predictions_path.read_bytes()).hexdigest()
    report = {
        "analysis": "heldout_decision_reliability_audit",
        "data_status": expected_status,
        "synthetic_demo": bool(demo),
        "no_intervention_causal_fairness_or_deployment_claim": True,
        "source_manifest": str(manifest_path),
        "input_predictions_sha256": sha,
        "records": int(len(frame)),
        "heldout_presentations": int(frame.course_presentation.nunique()),
        "capacity_fractions": [0.05, 0.10, 0.20],
        "tie_method": "EXPECTED_HITS_UNDER_UNIFORM_BOUNDARY_TIE_BREAKING",
        "minimum_reported_probability_bin_n": 30,
        "minimum_reported_course_n": 100,
        "cluster_bootstrap_replicates": bootstrap_replicates,
        "cluster_bootstrap_seed": seed,
        "cluster_bootstrap_caveat": (
            "Presentation resampling is exploratory; few independent clusters "
            "limit inferential reliability. No causal intervention benefit."
        ),
        "privacy": "Only aggregate CSV tables written; student IDs never exported.",
    }
    (output_dir / "AUDIT_MANIFEST.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/decision_audit"))
    parser.add_argument("--bootstrap-replicates", type=int, default=400)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(
        args.predictions, args.output_dir, manifest_path=args.manifest,
        demo=args.demo, bootstrap_replicates=args.bootstrap_replicates, seed=args.seed,
    ), indent=2))
