"""Repeat course-presentation-level group holdouts as a descriptive check.

Do not interpret dependent repeated splits as independent experimental trials.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from src.empirical import (
    TARGET, make_preprocessor, metrics, split_data, validate,
)


def run_sensitivity(
    input_path, output_dir, *,
    seeds=(2026, 2027, 2028, 2029, 2030), demo=False,
):
    df = pd.read_csv(input_path)
    nums, cats = validate(df)
    origin = str(df.data_origin.iloc[0])
    synthetic = "SYNTHETIC" in origin.upper()
    if synthetic and not demo:
        raise ValueError("Synthetic source requires --demo")
    if not synthetic and demo:
        raise ValueError("Do not mislabel authentic source as fictional")

    predictors = nums + cats
    dest = Path(output_dir)
    dest.mkdir(parents=True, exist_ok=True)
    rows, partitions = [], []

    for seed in seeds:
        train_idx, test_idx = split_data(df, int(seed))
        train, test = df.iloc[train_idx], df.iloc[test_idx]
        if train[TARGET].nunique() != 2 or test[TARGET].nunique() != 2:
            raise ValueError(f"Seed {seed}: missing outcome class in split")
        training_groups = sorted(train.course_presentation.unique().tolist())
        heldout_groups = sorted(test.course_presentation.unique().tolist())
        assert not set(training_groups).intersection(heldout_groups)
        assert not set(train.student_id.astype(str)).intersection(
            set(test.student_id.astype(str))
        )

        def pipeline(model):
            return Pipeline([
                ("preprocess", make_preprocessor(nums, cats)),
                ("classifier", model),
            ])

        models = {
            "prevalence": DummyClassifier(strategy="prior"),
            "logistic_l2": LogisticRegression(
                max_iter=2500, random_state=int(seed)
            ),
            "random_forest": RandomForestClassifier(
                n_estimators=150, min_samples_leaf=5,
                n_jobs=1, random_state=int(seed),
            ),
            "xgboost": XGBClassifier(
                n_estimators=175, max_depth=3, learning_rate=0.05,
                subsample=0.85, colsample_bytree=0.9, reg_lambda=3,
                eval_metric="logloss", n_jobs=1, random_state=int(seed),
            ),
        }
        for name, algorithm in models.items():
            model = pipeline(algorithm)
            model.fit(train[predictors], train[TARGET])
            probabilities = model.predict_proba(test[predictors])[:, 1]
            rows.append({
                "seed": int(seed), "model": name,
                "n_train": len(train), "n_test": len(test),
                "n_train_presentations": len(training_groups),
                "n_test_presentations": len(heldout_groups),
                **metrics(test[TARGET], probabilities),
            })
        partitions.append({
            "seed": int(seed),
            "training_presentations": training_groups,
            "heldout_presentations": heldout_groups,
            "n_train_students": int(train.student_id.nunique()),
            "n_test_students": int(test.student_id.nunique()),
        })

    scored = pd.DataFrame(rows)
    scored.to_csv(dest / "repeated_holdout_metrics.csv", index=False)
    summary = scored.groupby("model")[
        ["average_precision", "roc_auc", "brier", "log_loss"]
    ].agg(["mean", "std", "min", "max"])
    summary.to_csv(dest / "repeated_holdout_descriptive_summary.csv")
    manifest = {
        "data_origin": origin, "cutoff_day": int(df.cutoff_day.iloc[0]),
        "seeds": [int(s) for s in seeds],
        "n_records": len(df), "outer_partitions": partitions,
        "status": (
            "SYNTHETIC_SOFTWARE_CHECK_ONLY"
            if synthetic else "HISTORICAL_OULAD_OBSERVATIONAL"
        ),
        "caveat": (
            "Repeated presentation holdouts overlap. Variation across splits "
            "is descriptive, not independent-trial uncertainty. "
            "No causal effect or U.S. field validation is implied."
        ),
    }
    (dest / "robustness_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True)
    p.add_argument("--output-dir", default="outputs/robustness")
    p.add_argument("--seeds", default="2026,2027,2028,2029,2030")
    p.add_argument("--demo", action="store_true")
    args = p.parse_args()
    seeds = [int(i) for i in args.seeds.split(",") if i.strip()]
    if not seeds:
        raise SystemExit("Specify at least one seed")
    print(json.dumps(run_sensitivity(
        args.input, args.output_dir, seeds=seeds, demo=args.demo,
    ), indent=2))
