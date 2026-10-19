"""Grouped, leakage-aware OULAD ML benchmark and observational econometrics.

No deployment, randomized intervention, robotic teaching assistant or
causal effect is estimated by this code.
"""
import argparse
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score, roc_auc_score, brier_score_loss, log_loss,
)
from sklearn.model_selection import GroupKFold, GroupShuffleSplit, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

NUMERIC = [
    "lms_clicks_by_cutoff", "active_days_by_cutoff",
    "tasks_completed_by_cutoff", "num_of_prev_attempts", "studied_credits",
]
CATEGORICAL = ["gender", "highest_education", "imd_band", "age_band", "disability"]
TARGET = "final_risk_label"
FORBIDDEN = {
    "final_result", "date_unregistration", "score", "total_clicks_full_term",
    "end_grade", "outcome", "future_clicks", "dropout_day",
    "date_submitted_after_cutoff",
}


def validate(df):
    required = {
        "student_id", "course_presentation", "cutoff_day", "data_origin", TARGET,
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing dataset columns: {sorted(missing)}")
    if len(df) < 50 or df.course_presentation.nunique() < 6:
        raise ValueError("Require 50+ records and at least six course presentations")
    if df.duplicated(["student_id", "course_presentation"]).any():
        raise ValueError("Duplicate student-course enrollment")
    if not set(df[TARGET].dropna().unique()).issubset({0, 1}):
        raise ValueError("The outcome must be binary (0, 1)")
    if FORBIDDEN.intersection(df.columns):
        raise ValueError("Forbidden potential outcome/postcutoff feature supplied")
    if df.cutoff_day.nunique() != 1:
        raise ValueError("Do not pool different decision times")
    if df.data_origin.nunique() != 1:
        raise ValueError("Do not combine authentic OULAD and synthetic samples")
    nums = [name for name in NUMERIC if name in df.columns]
    cats = [name for name in CATEGORICAL if name in df.columns]
    if len(nums) < 3:
        raise ValueError("Too few valid pre-cutoff predictors")
    return nums, cats


def split_data(df, seed=2026):
    """Hold out complete course presentations, excluding student overlaps."""
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=seed)
    train_indices, test_indices = next(
        splitter.split(df, df[TARGET], groups=df.course_presentation)
    )
    test_students = set(df.iloc[test_indices].student_id.astype(str))
    train_indices = np.asarray([
        idx for idx in train_indices
        if str(df.iloc[idx].student_id) not in test_students
    ])
    assert not (
        set(df.iloc[train_indices].student_id)
        & set(df.iloc[test_indices].student_id)
    )
    assert not (
        set(df.iloc[train_indices].course_presentation)
        & set(df.iloc[test_indices].course_presentation)
    )
    return train_indices, test_indices


def make_preprocessor(numeric, categorical):
    blocks = [
        ("numeric", Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]), numeric),
    ]
    if categorical:
        blocks.append(
            ("categorical", Pipeline([
                ("impute", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(
                    handle_unknown="ignore", sparse_output=False
                )),
            ]), categorical)
        )
    return ColumnTransformer(blocks, sparse_threshold=0)


def metrics(y_true, probabilities):
    y, p = np.asarray(y_true), np.asarray(probabilities)
    return {
        "average_precision": float(average_precision_score(y, p)),
        "roc_auc": float(roc_auc_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "base_rate": float(np.mean(y)),
    }


def empirical(input_path, output_dir, seed=2026, allow_synthetic=False):
    df = pd.read_csv(input_path)
    numeric, categorical = validate(df)
    origin = str(df.data_origin.iloc[0])
    synthetic = "SYNTHETIC" in origin.upper()
    if synthetic and not allow_synthetic:
        raise ValueError("Synthetic data require explicit --demo, never research claims")
    if allow_synthetic and not synthetic:
        raise ValueError("Do not use --demo with authentic observations")

    train_ids, test_ids = split_data(df, seed)
    train, test = df.iloc[train_ids], df.iloc[test_ids]
    if train[TARGET].nunique() != 2 or test[TARGET].nunique() != 2:
        raise ValueError("Both outcome classes required in train and holdout")
    if train.course_presentation.nunique() < 3:
        raise ValueError("At least three training course presentations required")

    predictors = numeric + categorical
    models = {
        "prevalence": DummyClassifier(strategy="prior"),
        "logistic_l2": LogisticRegression(
            max_iter=2000, random_state=seed
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=160, min_samples_leaf=5,
            n_jobs=1, random_state=seed,
        ),
        "xgboost": XGBClassifier(
            n_estimators=175, max_depth=3, learning_rate=0.05,
            subsample=0.85, colsample_bytree=0.9,
            reg_lambda=3, n_jobs=1, random_state=seed,
            eval_metric="logloss",
        ),
    }
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    results = []
    predictions = pd.DataFrame({
        "student_id": test.student_id.astype(str).values,
        "course_presentation": test.course_presentation.values,
        "y_true": test[TARGET].values,
    })
    fitted = {}

    for name, estimator in models.items():
        pipeline = Pipeline([
            ("preprocess", make_preprocessor(numeric, categorical)),
            ("classifier", estimator),
        ])
        if name == "xgboost":
            cv = GroupKFold(
                n_splits=min(3, train.course_presentation.nunique())
            )
            search = RandomizedSearchCV(
                pipeline,
                {
                    "classifier__max_depth": [2, 3, 4],
                    "classifier__min_child_weight": [1, 3],
                    "classifier__learning_rate": [0.03, 0.05, 0.08],
                    "classifier__reg_lambda": [1, 3, 6],
                },
                n_iter=6, cv=cv, scoring="average_precision",
                n_jobs=1, random_state=seed,
            )
            search.fit(
                train[predictors], train[TARGET],
                groups=train.course_presentation,
            )
            fitted_pipeline = search.best_estimator_
        else:
            fitted_pipeline = pipeline.fit(train[predictors], train[TARGET])

        probabilities = fitted_pipeline.predict_proba(test[predictors])[:, 1]
        scores = metrics(test[TARGET], probabilities)
        scores.update(
            model=name, n_train=len(train), n_test=len(test),
            train_groups=int(train.course_presentation.nunique()),
            test_groups=int(test.course_presentation.nunique()),
        )
        results.append(scores)
        predictions[f"p_{name}"] = probabilities
        fitted[name] = fitted_pipeline

        if name == "xgboost":
            try:
                import shap
                transformed = fitted_pipeline.named_steps[
                    "preprocess"
                ].transform(test[predictors])
                estimator = fitted_pipeline.named_steps["classifier"]
                explanation = shap.TreeExplainer(estimator)
                values = np.asarray(explanation.shap_values(transformed))
                features = fitted_pipeline.named_steps[
                    "preprocess"
                ].get_feature_names_out()
                pd.DataFrame({
                    "feature": features,
                    "mean_abs_shap": np.abs(values).mean(axis=0),
                }).sort_values(
                    "mean_abs_shap", ascending=False
                ).to_csv(output / "global_shap.csv", index=False)
            except Exception as error:
                warnings.warn("SHAP not available: " + repr(error))

    pd.DataFrame(results).to_csv(
        output / "model_comparison.csv", index=False
    )
    # Row-level predicted probabilities stay only in ignored local outputs.
    predictions.to_csv(output / "holdout_predictions.csv", index=False)

    group_results = []
    for field in ["gender", "disability", "age_band"]:
        if field not in test:
            continue
        for label, subset in test.groupby(field, dropna=False):
            if len(subset) < 30 or subset[TARGET].nunique() != 2:
                continue
            p = fitted["xgboost"].predict_proba(
                subset[predictors]
            )[:, 1]
            group_results.append({
                "attribute": field, "category": str(label),
                "n": len(subset), **metrics(subset[TARGET], p),
            })
    pd.DataFrame(group_results).to_csv(
        output / "subgroup_metrics.csv", index=False
    )

    try:
        import statsmodels.formula.api as smf
        controls = [
            field for field in ("num_of_prev_attempts", "studied_credits")
            if field in train.columns
        ]
        demographics = [
            field for field in CATEGORICAL if field in train.columns
        ]
        columns = [
            TARGET, "lms_clicks_by_cutoff", "active_days_by_cutoff",
            "tasks_completed_by_cutoff", "course_presentation",
        ] + controls + demographics
        reg = train[columns].copy()
        reg["log_clicks"] = np.log1p(
            reg.lms_clicks_by_cutoff.clip(lower=0)
        )
        for field in demographics:
            reg[field] = reg[field].fillna("Missing").astype(str)
        terms = [
            "log_clicks", "active_days_by_cutoff",
            "tasks_completed_by_cutoff",
        ] + controls + [
            "C(" + name + ")" for name in demographics
        ] + ["C(course_presentation)"]
        robust = smf.ols(
            TARGET + " ~ " + " + ".join(terms), data=reg,
        ).fit(cov_type="HC3")
        (output / "robust_linear_probability_model_HC3.txt").write_text(
            robust.summary().as_text(), encoding="utf-8"
        )
    except Exception as error:
        warnings.warn("Robust regression failed: " + repr(error))

    manifest = {
        "origin": origin, "seed": int(seed),
        "cutoff_day": int(df.cutoff_day.iloc[0]),
        "n_total": len(df), "n_train": len(train), "n_test": len(test),
        "n_heldout_presentations": int(
            test.course_presentation.nunique()
        ),
        "features": predictors,
        "label": (
            "End-course Fail/Withdrawn versus Pass/Distinction "
            "conditional on being registered at the cutoff"
        ),
        "study_status": (
            "SYNTHETIC_SOFTWARE_DEMONSTRATION_ONLY"
            if synthetic else "HISTORICAL_OULAD_OBSERVATIONAL_ANALYSIS"
        ),
        "limitations": [
            "SHAP is a model attribution, not a causal explanation",
            "One outer split: additional independent robustness needed",
            "Historical UK education; no U.S. or contemporary intervention",
            "HC3 coefficient uncertainty is descriptive; "
            "group-clustered sensitivity should follow",
        ],
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", default="outputs/real_oulad")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    print(json.dumps(empirical(
        args.input, args.output_dir,
        seed=args.seed, allow_synthetic=args.demo,
    ), indent=2))
