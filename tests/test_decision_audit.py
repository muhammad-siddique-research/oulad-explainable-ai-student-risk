"""Only fictional predictions are used in these unit tests."""
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit

from src.decision_audit import (
    DEMO_STATUS, REAL_STATUS, audit_predictions, run, tie_averaged_top_k,
)


def fictional_predictions() -> pd.DataFrame:
    rng = np.random.default_rng(20261025)
    n = 800
    score = rng.normal(size=n)
    labels = rng.binomial(1, expit(score))
    return pd.DataFrame({
        "student_id": [f"FICTIONAL_{i:04d}" for i in range(n)],
        "course_presentation": np.repeat(
            ["AAA_2013J", "BBB_2013J", "CCC_2014B", "DDD_2014J"],
            n // 4,
        ),
        "y_true": labels,
        "p_prevalence": np.full(n, float(labels.mean())),
        "p_logistic_l2": expit(0.75 * score),
        "p_random_forest": expit(0.9 * score + 0.15),
        "p_xgboost": expit(1.05 * score + 0.15),
    })


class DecisionAuditTest(unittest.TestCase):
    def test_capacity_cutoff_ties_are_averaged_not_arbitrarily_ordered(self):
        y = np.array([1, 0, 1, 0])
        p = np.array([0.9, 0.5, 0.5, 0.1])
        outcome = tie_averaged_top_k(y, p, k=2)
        self.assertEqual(outcome["boundary_ties"], 2)
        self.assertAlmostEqual(outcome["expected_true_positives"], 1.5)
        self.assertAlmostEqual(outcome["expected_ppv"], 0.75)
        self.assertAlmostEqual(outcome["expected_recall"], 0.75)

    def test_aggregate_tables_keep_predictions_and_identity_out_of_output(self):
        df = fictional_predictions()
        records = audit_predictions(
            df, bootstrap_replicates=35, seed=41,
        )
        self.assertEqual(len(records["model_summaries"]), 4)
        self.assertEqual(len(records["capacity_audit"]), 12)
        self.assertEqual(len(records["paired_cluster_bootstrap"]), 2)
        for tab in records.values():
            self.assertFalse({"student_id", "y_true"}.intersection(tab.columns))
        self.assertTrue(
            (records["capacity_audit"].expected_ppv.between(0, 1)).all()
        )
        self.assertTrue(
            (records["calibration_bins"].n >= 30).all()
        )

    def test_invalid_prediction_and_student_identity_are_rejected(self):
        df = fictional_predictions()
        bad = df.copy()
        bad.loc[0, "p_xgboost"] = 1.2
        with self.assertRaisesRegex(ValueError, "probabilities"):
            audit_predictions(bad, bootstrap_replicates=30)
        bad = df.copy()
        bad.loc[1, "student_id"] = bad.loc[0, "student_id"]
        with self.assertRaisesRegex(ValueError, "one row per student"):
            audit_predictions(bad, bootstrap_replicates=30)
        bad = df.copy()
        bad["gender"] = "F"
        with self.assertRaisesRegex(ValueError, "unexpected columns"):
            audit_predictions(bad, bootstrap_replicates=30)

    def test_demo_flag_and_manifest_prevent_false_authenticity(self):
        with tempfile.TemporaryDirectory() as location:
            directory = Path(location)
            df = fictional_predictions()
            path = directory / "holdout_predictions.csv"
            df.to_csv(path, index=False)
            manifest = directory / "manifest.json"
            manifest.write_text(json.dumps({
                "study_status": DEMO_STATUS,
                "n_test": len(df),
                "n_heldout_presentations": 4,
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "flag disagree"):
                run(path, directory / "wrong", bootstrap_replicates=30)
            output = directory / "SYNTHETIC_DEMO"
            report = run(path, output, demo=True, bootstrap_replicates=30)
            self.assertTrue(report["synthetic_demo"])
            self.assertEqual(report["data_status"], DEMO_STATUS)
            self.assertTrue((output / "AUDIT_MANIFEST.json").exists())
            for p in output.glob("*.csv"):
                self.assertNotIn("student_id", p.read_text(encoding="utf-8"))
                self.assertNotIn("FICTIONAL_", p.read_text(encoding="utf-8"))
            manifest.write_text(json.dumps({
                "study_status": REAL_STATUS,
                "n_test": len(df),
                "n_heldout_presentations": 4,
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "flag disagree"):
                run(path, directory / "wrong2", demo=True, bootstrap_replicates=30)


if __name__ == "__main__":
    unittest.main()
