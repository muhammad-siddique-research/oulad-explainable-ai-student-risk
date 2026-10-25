"""Standard-library tests of published-aggregate consistency only."""

import unittest

from scripts.audit_published_results import audit


class AggregateAuditTest(unittest.TestCase):
    def test_archived_results_are_consistent_with_claimed_directions(self):
        result = audit()
        self.assertEqual(result["verification_scope"], "AGGREGATE_TABLE_CONSISTENCY_ONLY")
        self.assertFalse(result["raw_data_replication_performed"])
        self.assertEqual(result["n_holdout"], 7239)
        self.assertEqual(result["modules_xgboost_better_AP"], 6)
        self.assertEqual(result["modules_logistic_better_Brier"], 5)
        self.assertEqual(result["files_validated"], 6)


if __name__ == "__main__":
    unittest.main()
