"""Generate FICTIONAL student-course samples for software verification only."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def generate(out_dir, seed=2026, n_groups=12, per_group=45):
    rng = np.random.default_rng(seed)
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    rows, weekly = [], []
    for group_id in range(n_groups):
        presentation = f"FICTIONAL_COURSE_{group_id + 1:02d}"
        group_effect = rng.normal(0, 0.42)
        for index in range(per_group):
            student = f"FAKE_{group_id:02d}_{index:03d}"
            baseline = rng.normal()
            category = rng.choice(["fictional_A", "fictional_B"])
            cumulative_clicks = 0
            cumulative_tasks = 0
            assessment_scores = []
            for week in range(1, 9):
                weekly_clicks = int(rng.poisson(
                    max(2, 22 + 8 * baseline + 1.8 * week + group_effect * 3)
                ))
                weekly_tasks = int(rng.binomial(
                    3, 1 / (1 + np.exp(-(0.6 + baseline * 0.7)))
                ))
                fictional_score = float(np.clip(
                    rng.normal(68 + 10 * baseline, 12), 0, 100
                ))
                cumulative_clicks += weekly_clicks
                cumulative_tasks += weekly_tasks
                assessment_scores.append(fictional_score)
                weekly.append({
                    "student_id": student, "course_presentation": presentation,
                    "week": week, "lms_clicks": weekly_clicks,
                    "tasks": weekly_tasks, "FICTIONAL_score": fictional_score,
                    "data_origin": "SYNTHETIC_DEMONSTRATION_ONLY",
                })
                if week == 4:
                    early_clicks = cumulative_clicks
                    early_tasks = cumulative_tasks
                    early_mean = float(np.mean(assessment_scores))
            logit = (
                -1.05 - 0.025 * (early_mean - 67)
                - 0.005 * (early_clicks - 118)
                - 0.08 * (early_tasks - 7)
                + group_effect + rng.normal(0, 0.3)
            )
            later_risk = int(rng.random() < 1 / (1 + np.exp(-logit)))
            rows.append({
                "student_id": student, "course_presentation": presentation,
                "cutoff_day": 28, "lms_clicks_by_cutoff": early_clicks,
                "tasks_completed_by_cutoff": early_tasks,
                "active_days_by_cutoff": min(28, max(0, early_clicks // 7)),
                "synthetic_group": category,
                "final_risk_label": later_risk,
                "data_origin": "SYNTHETIC_DEMONSTRATION_ONLY",
            })
    pd.DataFrame(rows).to_csv(
        output / "synthetic_cutoff_features.csv", index=False
    )
    pd.DataFrame(weekly).to_csv(
        output / "synthetic_student_week.csv", index=False
    )
    return len(rows), len(weekly)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="data/synthetic")
    parser.add_argument("--seed", type=int, default=2026)
    a = parser.parse_args()
    print("SYNTHETIC ONLY", generate(a.output_dir, a.seed))
