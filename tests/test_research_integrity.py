"""Tests exercise invented fixtures only, never assert empirical effects."""
import json
import zipfile
import pandas as pd
import pytest

from scripts.download_official_oulad import EXPECTED, safe_extract
from src.empirical import empirical, split_data, validate
from src.generate_synthetic import generate
from src.prepare_oulad import prepare
from src.robustness import run_sensitivity


def test_synthetic_requires_explicit_demo(tmp_path):
    generate(tmp_path, n_groups=9, per_group=10)
    with pytest.raises(ValueError, match="explicit --demo"):
        empirical(tmp_path / "synthetic_cutoff_features.csv", tmp_path / "bad")


def test_holdout_separates_students_and_course_presentations(tmp_path):
    generate(tmp_path, n_groups=9, per_group=25)
    df = pd.read_csv(tmp_path / "synthetic_cutoff_features.csv")
    validate(df)
    train_ids, test_ids = split_data(df)
    assert not (
        set(df.iloc[train_ids].student_id) & set(df.iloc[test_ids].student_id)
    )
    assert not (
        set(df.iloc[train_ids].course_presentation)
        & set(df.iloc[test_ids].course_presentation)
    )


def test_future_and_target_field_guard(tmp_path):
    generate(tmp_path, n_groups=9, per_group=10)
    df = pd.read_csv(tmp_path / "synthetic_cutoff_features.csv")
    df["final_result"] = "Fail"
    with pytest.raises(ValueError, match="Forbidden"):
        validate(df)


def test_source_features_exclude_future_activity_and_grades(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    key = {
        "code_module": ["AAA", "AAA"],
        "code_presentation": ["2013J", "2013J"],
        "id_student": [111, 222],
    }
    pd.DataFrame({
        **key, "gender": ["F", "M"], "region": ["X", "X"],
        "highest_education": ["A", "A"],
        "imd_band": ["0-10%", "10-20%"], "age_band": ["0-35", "0-35"],
        "num_of_prev_attempts": [0, 0],
        "studied_credits": [60, 60], "disability": ["N", "N"],
        "final_result": ["Pass", "Fail"],
    }).to_csv(raw / "studentInfo.csv", index=False)
    pd.DataFrame({
        **key, "date_registration": [-4, -2],
        "date_unregistration": [None, None],
    }).to_csv(raw / "studentRegistration.csv", index=False)
    pd.DataFrame({
        "code_module": ["AAA"] * 4,
        "code_presentation": ["2013J"] * 4,
        "id_student": [111, 111, 222, 222],
        "date": [10, 31, 15, 40],
        "sum_click": [4, 400, 5, 500],
    }).to_csv(raw / "studentVle.csv", index=False)
    pd.DataFrame({
        "id_assessment": [1], "code_module": ["AAA"],
        "code_presentation": ["2013J"],
    }).to_csv(raw / "assessments.csv", index=False)
    pd.DataFrame({
        "id_assessment": [1, 1], "id_student": [111, 222],
        "date_submitted": [16, 29], "score": [100, 100],
    }).to_csv(raw / "studentAssessment.csv", index=False)
    summary = prepare(raw, tmp_path / "out.csv", cutoff_day=28, chunk_size=2)
    df = pd.read_csv(tmp_path / "out.csv").sort_values("student_id")
    assert summary["rows"] == 2
    assert df.lms_clicks_by_cutoff.tolist() == [4, 5]
    assert df.tasks_completed_by_cutoff.tolist() == [1, 0]
    assert "score" not in df.columns


def test_archive_rejects_path_traversal(tmp_path):
    malicious = tmp_path / "bad.zip"
    with zipfile.ZipFile(malicious, "w") as archive:
        archive.writestr("../escape.csv", "unsafe")
    with pytest.raises(ValueError, match="Unsafe ZIP path"):
        safe_extract(malicious, tmp_path / "safe")


def test_archive_normalizes_seven_official_tables(tmp_path):
    original = tmp_path / "original.zip"
    with zipfile.ZipFile(original, "w") as archive:
        for name in EXPECTED:
            archive.writestr("OULAD/" + name, "col\nvalue\n")
    extracted = safe_extract(original, tmp_path / "raw")
    assert set(extracted) == EXPECTED
    assert all((tmp_path / "raw" / name).exists() for name in EXPECTED)


def test_repeated_holdout_does_not_claim_empirical_results(tmp_path):
    generate(tmp_path, n_groups=9, per_group=18)
    path = tmp_path / "synthetic_cutoff_features.csv"
    with pytest.raises(ValueError, match="Synthetic source requires"):
        run_sensitivity(path, tmp_path / "rejected", seeds=(2026,))
    record = run_sensitivity(
        path, tmp_path / "accepted", seeds=(2026,), demo=True
    )
    assert record["status"] == "SYNTHETIC_SOFTWARE_CHECK_ONLY"
    assert (
        len(pd.read_csv(tmp_path / "accepted" / "repeated_holdout_metrics.csv"))
        == 4
    )
    assert json.loads(
        (tmp_path / "accepted" / "robustness_manifest.json").read_text()
    )["seeds"] == [2026]
