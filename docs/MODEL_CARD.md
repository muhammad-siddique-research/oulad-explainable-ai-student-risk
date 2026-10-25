# Research Model Card: OULAD Day-28 Academic-Risk Prediction

**Author:** Muhammad Siddique, Ph.D.  
**Version:** Working research documentation, October 2026.  
**Status:** Archival, non-operational secondary-data modeling; no peer-reviewed or prospective institutional validation.

## Intended scope

| Field | Description |
|---|---|
| **Population** | OULAD learners still registered at day 28; one eligible record retained per anonymized person |
| **Target** | End-course Fail/Withdrawn = 1 versus Pass/Distinction = 0 |
| **When predicted** | Day 28, using days 0–27 only |
| **Inputs** | Early VLE click count, active VLE days, early assessment submission count; prior attempts, credits and recorded demographic/background categories |
| **Benchmarks** | Training prevalence, L2 Logistic Regression, Random Forest, tuned XGBoost |
| **Splits** | Whole course presentations held out; no students shared across the principal outer train/test partition |
| **Primary metric** | Average precision, interpreted relative to observed event prevalence |
| **Secondary metrics** | ROC-AUC, Brier, log loss, module transfer, chronological transfer, feature ablation |
| **Explanations** | Intended Tree SHAP for held-out fitted predictions; no causal meaning |
| **Current use** | Scholarly benchmark, research design critique and software replication only |

## Aggregate empirical evidence

The recorded main holdout comprises **7,239** learners. AP / AUC / Brier for XGBoost: **0.6852 / 0.7245 / 0.2041**; for Logistic Regression: **0.6631 / 0.7168 / 0.2091**. In leave-one-module-out evaluations, Logistic Regression had lower Brier score on five of seven modules. The group sizes and methods do not establish universal predictive superiority.

The code is available; the original learner-level source and row-level model predictions are **not** committed. A second independent raw-data replication is still required. Publicly displayed charts are regenerated only from committed aggregate CSVs.

**Additional software, not an additional historical finding:** [src/decision_audit.py](../src/decision_audit.py) supports a post-hoc reliability and capacity assessment on locally held-out predictions. Top-k PPV and recall, score-bin calibration diagnostics, course-level variation and exploratory paired presentation resampling can be reported without exporting learner IDs. No actual historical decision-audit numbers have been committed. The code's rank selection is not an institutional outreach recommendation or a treatment-benefit model.

## Known limitations and failure modes

- **Construct validity:** click activity is not equivalent to attention, learning, access or motivation. Baseline demographics can encode historical inequity.
- **Selection:** the model excludes learners who have already withdrawn by the day-28 cutoff.
- **Distribution shift:** course content, assessment designs, study expectations and cohorts differ; AP superiority need not imply reliable probabilities.
- **Calibration:** an overall Brier score does not demonstrate satisfactory calibration in every group; direct reliability curves and intercept/slope summaries are required before any operational inference.
- **Fairness:** no verified aggregate subgroup-error audit is committed. The behavior-only model is less accurate overall but neither variant has been validated against harms or disparate allocation of support.
- **Explainability:** SHAP attributions can reflect correlated features or learned proxies and cannot identify the causal influence of individual learner actions.
- **Dependence:** clustered uncertainty in the archived result tables has not yet been independently regenerated from the visible code path.
- **External validity:** 2013–2014 UK distance education does not establish validity in a 2026 U.S. college or another modality.

## Explicitly prohibited uses

Do **not** use the research scores to penalize students, deny enrollment, automatically restrict academic opportunities, rank educators, substitute for human judgment, infer disability/mental health status, or assert that a robotic/AI tutor is effective. No operational threshold is endorsed.

## Minimum prerequisites for a supported pilot

1. Establish locally lawful data processing, meaningful transparency, consent/notice when appropriate, student data minimization and institutional governance.
2. Conduct external temporal and course validation at the intended institution with population flow and missingness disclosed.
3. Measure subgroup discrimination, calibration and false-alert burden with uncertainty and protect small cells from disclosure.
4. Compare models with reduced demographic access and examine proxy behavior; document equity and privacy trade-offs.
5. Predefine staff capacity, top-k alert precision, error costs and safe human review channels; make support opt-in where feasible.
6. Use an approved evaluation design to test whether offered assistance changes *student outcomes* without stigmatizing or removing opportunities.

## Monitoring and maintenance

There is **no deployed service, monitoring dashboard or drift response plan**. Any future application should assign an accountable owner, preserve a model/version manifest, monitor drift and calibration, audit interventions and allow individuals to contest decisions.

**Methodological and ethical sources:** [APA 7 references](REFERENCES_APA7.md); [research protocol](ANALYSIS_PROTOCOL.md); [reproducibility audit](REPRODUCIBILITY_AUDIT.md).
