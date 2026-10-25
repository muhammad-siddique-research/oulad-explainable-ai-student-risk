# Manuscript Evidence Tracker — October 2026

| Item | Status | Evidence or remaining work |
|---|---|---|
| OULAD historical source and descriptor | Source verified | docs/OFFICIAL_DATA_SOURCES.md; Kuzilek et al. (2017) |
| Raw archive SHA-256 | Recorded, recheck pending | Existing source-archive digest; must hash locally obtained original ZIP |
| Day-28 cohort N and outcome distribution | **Archived** | Reported 24,835 learners; raw-data audit pending |
| Main XGBoost, Logistic and Random Forest comparison | **Archived** | results/primary_models.csv; aggregate audit passes |
| Chronological, cutoff, module and ablation comparisons | **Archived** | Five additional CSVs; cohort comparability caveats |
| HC3 econometric coefficients | **Archived** | results/econometric_associations.csv; independent fit pending |
| Presentation-clustered intervals | **Archived, not independently verified** | Reconcile code path, exact regression sample, cluster count, small-cluster behavior |
| Independent original-data replication | **Pending** | Freeze dataset, environment, group splits and estimates |
| Probability calibration curves/intercept/slope | **Pending** | Overall Brier alone insufficient |
| Held-out SHAP numerical reproducibility and stability | **Pending** | No committed aggregation trace |
| Subgroup fairness and capacity audits | **Pending** | Min-cell suppression and explicit alert policy |
| Scholarly Results and Discussion, APA bibliography | **Drafted** | docs/RESULTS_AND_DISCUSSION_APA7.md and docs/REFERENCES_APA7.md |
| Journal-ready paper | **Working document only** | Authorship review, raw-data replication, journal requirements |

**No synthetic test output is treated as real-data evidence.** The original OULAD source contains historical distance-learning behavior, not a Robotic Teaching Assistant or intervention outcome.
