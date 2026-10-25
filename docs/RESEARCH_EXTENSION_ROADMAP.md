# A Three-Track Research Extension Roadmap

**Purpose:** Expand the OULAD repository into a coherent research program while separating an executable prototype from future empirically tested hypotheses. All feasibility ratings are editorial judgments, not measured probabilities.

| Rank | Research extension | Scientific novelty (provisional) | Potential impact | Feasibility / data | Cost |
|---|---|---|---|---|---|
| **1 — implement now** | **Capacity, calibration and context-reliability audit**, including transparent rank-tie handling and small-cluster uncertainty | **Moderate-to-low:** individual components appeared in 2025–2026 OULAD literature; transparent integration may add methodological value | High for defensible research practice | High once real held-out predictions are regenerated from OULAD | Low; Python only |
| **2 — research next** | **Hierarchical cross-course recalibration and drift early warning**, evaluated with truly unseen module/presentation contexts | **Unverified/moderate:** cross-domain calibration is an active area and priorities must be checked against recent work | Potentially high for portability | Medium; only seven original modules constrain identification | Low–moderate computational cost |
| **3 — ambitious** | **Need versus benefit:** Does a support intervention help the students the model ranks highest, or would a different rule deliver more equitable gains? | **Unverified/potentially high** for this exact empirical setting | Very high, directly policy-relevant | Low without new institutional partner and ethically approved assignment | High; organizational and governance costs |

## Immediate experiment: reliability-aware decision audit

**Research question:** Under capacity limits, do XGBoost and Logistic Regression maintain their principal performance ordering when evaluated by top-k PPV, recall, calibration diagnostics and contextual bootstrap differences?

**Hypotheses:** Some model rankings will change across budget levels and course presentations; calibration slope and Brier can disagree with AP. Treat as **proposed**, not as verified empirical conclusions.

**Data:** original OULAD 2013–2014 (local only); day-28 retained-learner cohort and non-overlapping course-presentation held-out predictions.

**Methods:** train-fitted Logistic, Random Forest and XGBoost; audit top-5/10/20% selection, probability calibration, per-presentation performance and paired presentation-bootstrap variability.

**Baselines:** a constant-prevalence model with **tie-averaged** capacity allocation and conventional L2 Logistic Regression.

**Metrics:** AP, AUC, Brier, log loss, calibration intercept/slope, PPV@k, recall@k, lift@k, fraction of unseen presentations with each model preferred, and bootstrap intervals with a small-cluster caution.

**Robustness:** alternative prespecified cutoffs, repeated whole-presentation splits, module-level external-within-dataset tests, demographic-feature ablation and model-score ties. The current historical sample cannot provide external contemporary U.S. validity.

**Limitations and refutation:** No intervention effects or proven fairness; if differences fail independent-split replication or vanish with a credible calibration adjustment, substantive conclusions about reliability fragility should be weakened.

**First milestone:** Run the [decision audit script](../src/decision_audit.py) on freshly regenerated authentic held-out predictions, independently verify provenance and check the output against the original main model metrics before including any numbers in a paper.

**Second milestone:** Evaluate cross-module calibration strategies on independent holdouts without using test outcomes to refit models. Use predeclared success criteria and account for how few independent modules exist.

**Third milestone:** Seek an institutional partner and design consent/governance before proposing randomized or quasi-experimental learner-support evaluations.

**Originality warning:** [Wu et al. (2026)](https://doi.org/10.1371/journal.pone.0352867) already address capacity, fairness and selective prediction on OULAD; [Opoku et al. (2025)](https://doi.org/10.18608/jla.2025.8543) address fairness–accuracy trade-offs. The repository demonstrates credible computational research practice; it does **not** claim globally novel algorithms or empirically established effects from the new extension.
