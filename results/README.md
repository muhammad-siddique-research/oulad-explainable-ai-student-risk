# Archived Aggregate Results: What Can and Cannot Be Inferred

All six committed CSVs are **aggregate statistics reported from an earlier OULAD analysis**. They contain no individual learner predictions. The present documentation and visualization pass **does not claim to have independently rerun OULAD models**. Check [the evidence audit](../docs/REPRODUCIBILITY_AUDIT.md) before interpreting any number as independently replicated.

| File | Content | Interpretive caution |
|---|---|---|
| primary_models.csv | Same n=7,239 test: baseline, Logistic, Forest, XGBoost; AP, AUC, Brier, log loss | Single grouped outer holdout; scores are not impacts |
| econometric_associations.csv | LPM coefficients, HC3 and presentation-cluster intervals | Cluster-estimation path not yet source-data reconciled |
| leave_one_module_out.csv | Seven entire-module holdouts, Logistic/XGBoost metrics | Event prevalence and course size vary by module; no universal ranking |
| temporal_2013_to_2014.csv | Chronological transfer with n-train and n-test | Not contemporary external institutional validation |
| feature_ablation.csv | All available predictors versus behavioral features alone | No measured fairness impact of including/excluding demographics |
| prediction_cutoff_sensitivity.csv | 14- and 42-day eligible cohorts | Cohort composition differs; not a causal time effect |

**Built-in consistency test:** run python -m scripts.audit_published_results from repository root. It checks values, pair completeness and simple invariants; it cannot certify raw provenance or unbiased model selection.

**Figure provenance:** figures/heldout_model_comparison.svg and figures/module_transportability.svg are created by python -m scripts.build_published_figures using only primary_models.csv and leave_one_module_out.csv.

**Reporting convention:** AP = average precision; AUC = ROC area; Brier = mean squared probability error; LPM = linear probability model; HC3 = heteroskedasticity-robust covariance. Higher AP/AUC and lower Brier/log loss are favorable. SHAP is model attribution, not a causal mechanism. All tables report historical UK data.
