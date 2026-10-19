"""Construct a leakage-aware prospective cutoff cohort from authentic OULAD CSVs.

The outcome is retrospective final course status. No robot or AI intervention
is observed. Data: Kuzilek et al. (2017), Scientific Data 4:170171.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

REQUIRED = (
    "studentInfo.csv", "studentRegistration.csv", "studentVle.csv",
    "studentAssessment.csv", "assessments.csv",
)
KEYS = ["code_module", "code_presentation", "id_student"]


def prepare(raw_dir, output_path, cutoff_day=28, chunk_size=500_000, unique_students=True):
    raw_dir = Path(raw_dir)
    missing = [name for name in REQUIRED if not (raw_dir / name).exists()]
    if missing:
        raise FileNotFoundError("Original OULAD CSV files missing: " + ", ".join(missing))
    if cutoff_day not in (14, 28, 42):
        raise ValueError("Predeclared horizons are days 14, 28 and 42")

    info = pd.read_csv(raw_dir / "studentInfo.csv")
    registration = pd.read_csv(raw_dir / "studentRegistration.csv")
    fields = KEYS + [
        "gender", "region", "highest_education", "imd_band", "age_band",
        "num_of_prev_attempts", "studied_credits", "disability", "final_result",
    ]
    if not set(fields).issubset(info.columns):
        raise ValueError("Unexpected studentInfo table schema")
    base = info[fields].merge(
        registration[KEYS + ["date_registration", "date_unregistration"]],
        on=KEYS, how="left", validate="one_to_one",
    )
    base = base[
        base.date_registration.notna()
        & (base.date_registration < cutoff_day)
        & (base.date_unregistration.isna() | (base.date_unregistration >= cutoff_day))
    ].copy()
    if base.duplicated(KEYS).any():
        raise ValueError("Duplicate student-course identifiers")
    if unique_students:
        base = (
            base.sort_values(["code_presentation", "code_module", "id_student"])
            .drop_duplicates("id_student", keep="first")
        )
    base["course_presentation"] = (
        base.code_module.astype(str) + "_" + base.code_presentation.astype(str)
    )
    base["student_id"] = base.id_student.astype(str)

    # Only interactions observed during course days [0, cutoff_day).
    aggregates = []
    for chunk in pd.read_csv(
        raw_dir / "studentVle.csv", chunksize=chunk_size,
        usecols=KEYS + ["date", "sum_click"],
    ):
        early_chunk = chunk.loc[chunk.date.ge(0) & chunk.date.lt(cutoff_day)]
        if not early_chunk.empty:
            aggregates.append(
                early_chunk.groupby(KEYS + ["date"], as_index=False)["sum_click"].sum()
            )
    if not aggregates:
        raise ValueError("No VLE records within the study horizon")
    activity = (
        pd.concat(aggregates, ignore_index=True)
        .groupby(KEYS + ["date"], as_index=False)["sum_click"].sum()
        .groupby(KEYS, as_index=False)
        .agg(lms_clicks_by_cutoff=("sum_click", "sum"),
             active_days_by_cutoff=("date", "nunique"))
    )

    assessments = pd.read_csv(raw_dir / "assessments.csv")
    submissions = pd.read_csv(raw_dir / "studentAssessment.csv")
    linked = submissions.merge(
        assessments[["id_assessment", "code_module", "code_presentation"]],
        on="id_assessment", how="inner", validate="many_to_one",
    )
    linked = linked.loc[
        linked.date_submitted.ge(0) & linked.date_submitted.lt(cutoff_day)
    ]
    early = linked.groupby(KEYS, as_index=False).agg(
        tasks_completed_by_cutoff=("id_assessment", "nunique")
    )
    # Do not include assessment scores: actual feedback availability is unknown.
    frame = (
        base.merge(activity, on=KEYS, how="left", validate="one_to_one")
        .merge(early, on=KEYS, how="left", validate="one_to_one")
    )
    early_features = [
        "lms_clicks_by_cutoff", "active_days_by_cutoff", "tasks_completed_by_cutoff",
    ]
    frame[early_features] = frame[early_features].fillna(0)
    frame["final_risk_label"] = (
        frame.final_result.isin(["Fail", "Withdrawn"]).astype(int)
    )
    frame["cutoff_day"] = int(cutoff_day)
    frame["data_origin"] = "OULAD_PUBLIC_DATA_NOT_ROBOTIC_INTERVENTION"

    columns = ["student_id", "course_presentation", "cutoff_day"] + early_features + [
        "gender", "region", "highest_education", "imd_band", "age_band",
        "num_of_prev_attempts", "studied_credits", "disability",
        "final_risk_label", "data_origin",
    ]
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame[columns].to_csv(destination, index=False)
    return {
        "rows": len(frame),
        "presentations": int(frame.course_presentation.nunique()),
        "unique_students": int(frame.student_id.nunique()),
        "cutoff_exclusive": cutoff_day,
        "missing_imd_band": int(frame.imd_band.isna().sum()),
        "label_counts": {
            str(k): int(v) for k, v in frame.final_risk_label.value_counts().items()
        },
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", default="data/raw")
    p.add_argument("--output", default="data/processed/oulad_day28.csv")
    p.add_argument("--cutoff-day", type=int, default=28)
    p.add_argument("--include-repeated-students", action="store_true")
    a = p.parse_args()
    print(prepare(
        a.data_dir, a.output, a.cutoff_day,
        unique_students=not a.include_repeated_students,
    ))
