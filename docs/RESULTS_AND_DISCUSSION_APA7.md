# Results and Discussion
### Explainable Academic-Risk Prediction and Cross-Course Reliability in the Open University Learning Analytics Dataset

**Author:** Muhammad Siddique, Ph.D.  
**Document status:** Working-paper section; research reported from committed aggregate tables; not independently source-data replicated, peer-reviewed, accepted, or published.  
**Data period:** Historical UK Open University records, 2013–2014.

> **Evidence key:** Statements labeled *archived empirical estimate* use CSV tables committed to this repository. Statements labeled *interpretation* are reasoned assessments of those estimates. *Not established* denotes questions the available repository does not answer. The paper's numbers should be rechecked by a second analyst against the original OULAD before journal submission.

## Abstract

**Background.** Prediction of academic withdrawal and failure from digital traces is a widely studied task, but portability between courses and reliable probability estimation are less obvious than a single area-under-the-curve score might suggest. **Objective.** To evaluate whether early-course activity and baseline information predict eventual failure or withdrawal, and how predictive model rankings change under more demanding contextual tests. **Design.** A historical, observational secondary-data study of OULAD with a day-28 information cutoff, course-presentation-based held-out evaluation, regression associations, gradient boosting, sensitivity analyses and explainability checks. **Results.** The archived analytic cohort contains 24,835 unique eligible learners; 7,239 were held out across six course presentations. XGBoost achieved average precision (AP) 0.6852, ROC-AUC 0.7245 and Brier score 0.2041, compared with 0.6631, 0.7168 and 0.2091 for L2 Logistic Regression. The AP advantage was 0.0221 points. However, Logistic Regression had lower Brier error in five of seven leave-one-module-out tests. Adjusted early-activity coefficients were negative in a linear probability model, but do not identify causal effects. **Conclusion.** The results support early signals as potentially useful predictive correlates while cautioning that model complexity, portability, probability reliability, privacy and decision capacity must be evaluated together. This study did not test an educational intervention.

## 1. Research setting, cohort and outcome

The original OULAD release reports 32,593 student–module registrations and 10,655,280 virtual learning environment (VLE) interaction records across 22 presentations of seven modules (Kuzilek et al., 2017). These are original-source counts, not observations in the analysis. The study's recorded eligibility protocol requires registration before day 28 and excludes students who had already withdrawn by that cutoff. From 27,490 eligible enrollment records, one eligible enrollment was retained per learner, resulting in **24,835 distinct learners**. Among them, **10,638 (42.83%)** later received a Fail or Withdrawn result; **14,197** received Pass or Distinction.

The prediction task is therefore conditional: **among learners still registered at day 28, estimate their subsequent probability of Fail or Withdrawn**. It is not a prediction of all withdrawal events from enrollment day, because early withdrawals have been deliberately excluded. Activity features use days 0–27; their contemporaneous availability is central to interpretation. Course-level summaries and institution-specific outcomes cannot be inferred from a nonrepresentative selection of courses without further external validation.

The primary held-out partition contains **7,239 learners from six course presentations** with a 0.422296 observed risk prevalence. The remaining **17,596** learners in 16 presentations form the recorded training partition. Learner identifiers do not overlap across those two partitions. Group separation better approximates the challenge of unfamiliar courses than a random split of learner rows, but it is still internal validation within one historical institution and period.

## 2. Primary predictive comparison

**Table 1. Archived main held-out prediction results**

| Model | AP ↑ | ROC-AUC ↑ | Brier ↓ | Log loss ↓ |
|---|---:|---:|---:|---:|
| Training-prevalence benchmark | 0.422296 | 0.500000 | 0.244035 | 0.681171 |
| L2 Logistic Regression | 0.663090 | 0.716776 | 0.209106 | 0.606377 |
| Random Forest | 0.678167 | 0.721754 | 0.205708 | 0.597453 |
| XGBoost | **0.685175** | **0.724472** | **0.204065** | **0.593518** |

*Source: results/primary_models.csv; all four models evaluated on the same recorded n = 7,239 holdout. Arrows indicate preferred direction. AP should be interpreted with the stated event prevalence (Saito & Rehmsmeier, 2015).*

**Archived empirical estimate.** XGBoost minus L2 Logistic Regression yielded **+0.022085 AP**, **+0.007696 ROC-AUC**, **−0.005041 Brier**, and **−0.012859 log loss**. The random forest fell between the two fitted models on these main test criteria. All three trained classifiers outperformed the prevalence-only benchmark.

**Interpretation.** The differences are consistent in direction but small compared with the larger shift from the prevalence baseline to either trained model. They do not justify an unqualified claim that boosting is the superior algorithm, and they do not establish that an AI warning would change attendance, persistence or learning. Estimation after hyperparameter selection may also favor the model optimized against related inner-fold outcomes. A previously reported paired cluster-bootstrap AP interval (~0.005 to 0.050) is not included as a independently reproducible artifact and should be independently regenerated before use in a peer-reviewed statistical-superiority statement.

**Probability error is not a complete calibration diagnosis.** The Brier score is a proper overall accuracy score and includes aspects of discrimination and calibration. Without group-level reliability curves, calibration slope/intercept, or examination of score shifts, the table does not establish well-calibrated individualized probabilities. See Van Calster et al. (2019) for the importance of direct calibration assessment.

## 3. Cross-module transportability: when model rankings reverse

**Table 2. Leave-one-module-out differences: XGBoost minus Logistic Regression**

| Unseen module | Holdout n | Δ AP (higher favors XGBoost) | Δ Brier (lower favors XGBoost) |
|---|---:|---:|---:|
| AAA | 686 | +0.025774 | −0.002083 |
| BBB | 6,243 | +0.044044 | +0.013962 |
| CCC | 2,345 | +0.016664 | +0.002017 |
| DDD | 4,852 | +0.006017 | −0.005783 |
| EEE | 2,080 | −0.022678 | +0.025485 |
| FFF | 6,198 | +0.014711 | +0.000176 |
| GGG | 2,431 | +0.031008 | +0.099618 |

*Source: results/leave_one_module_out.csv; values calculated by subtraction of its existing rounded six-decimal results. The seven holdout populations differ in size and event prevalence; the table is not seven independent randomized experiments.*

**Archived empirical estimate.** XGBoost had higher AP in **six of seven** module evaluations, but L2 Logistic Regression recorded the **lower Brier score in five of seven**. The largest divergence occurred for module GGG: XGBoost Brier 0.374910 compared with 0.275292 for Logistic Regression. For module EEE, Logistic Regression also performed better in AP (0.607208 versus 0.584530) and Brier (0.214095 versus 0.239580).

**Interpretation.** A model can rank high-risk students somewhat better yet assign less accurate probabilities when moved to a new teaching context. Such disagreement is consequential when proposed interventions depend on estimated absolute risk and limited staff capacity. Average Precision and Brier answer different questions and need not move together. Seven modules also provide little independent evidence for fine-grained claims about generalization. Published work on fairness and validation using OULAD underscores that student-risk prediction is not a new field and that accuracy alone is an insufficient deployment criterion (Opoku et al., 2025; Wu et al., 2026).

**Not established.** The archive does not document module-specific calibration curves or a prospective external institution; the phrase *external validation* would be too strong for these held-out OULAD modules. No direct reweighting, recalibration or domain-adaptation experiment is presented in the committed results.

## 4. Adjusted econometric associations

**Table 3. Archived adjusted linear-probability associations**

| Early-course predictor | Coefficient | HC3 95% CI | Presentation-cluster 95% CI |
|---|---:|---:|---:|
| log(1 + VLE clicks) | −0.037472 | [−0.043205, −0.031739] | [−0.047199, −0.027745] |
| Recorded active VLE days | −0.013788 | [−0.015037, −0.012540] | [−0.015569, −0.012008] |
| Distinct submitted assessments | −0.141791 | [−0.153665, −0.129917] | [−0.184736, −0.098846] |

*Source: results/econometric_associations.csv. The current public-facing analytical script can emit an HC3 regression summary but does not, in its archived version, regenerate the separate presentation-clustered intervals shown here. Treat clustered values as **reported, pending raw-run provenance verification**, not independently audited uncertainty. The precise estimation population and any dependence correction must be reconciled before publication.*

**Archived empirical estimate.** All three conditional coefficients are negative. A unit difference in logged early clicks corresponds to a −0.0375 difference in modeled probability, holding other included predictors constant. This is a model-based contrast, not evidence that causing a learner to generate more clicks would reduce academic risk by 3.75 percentage points.

**Interpretation.** Engagement measures may proxy opportunity to study, course structure, self-regulation, preparation, health, accessibility and competing work or care obligations. Submissions and active days can be jointly influenced by unobserved factors; their inclusion together can create difficult-to-interpret partial coefficients. Moreover, the small number of independent course-presentation groups (22 across the dataset) warrants caution about asymptotic clustered intervals. HC3 corrects for heteroskedasticity, not necessarily dependence within learning contexts (Cameron & Miller, 2015; MacKinnon & White, 1985).

**Not established.** No randomized engagement intervention, instrumental variable, credible natural experiment or causal identification design is present. No claim that high click volumes cause achievement gains is supported.

## 5. Temporal transfer, feature removal and decision horizon

### 5.1 Chronological transfer

On the archived **2013 training → 2014 testing** evaluation (training *n* = 11,685; testing *n* = 13,150), XGBoost achieved **AP 0.650027, ROC-AUC 0.702807 and Brier 0.211013**. Logistic Regression reached **AP 0.619063, ROC-AUC 0.699088 and Brier 0.215138**. This is consistent with the main split's direction but uses distinct groups and does not substitute for validation in another university or present-day student population.

### 5.2 Behavior-only specification

On the main recorded evaluation, a model using **behavior-only features** (excluding recorded background covariates) produced XGBoost AP **0.602942**, ROC-AUC **0.661463** and Brier **0.222739**. The all-feature XGBoost model produced **0.685175**, **0.724472** and **0.204065**, respectively. This **0.082233 AP decrease** reflects a meaningful predictive trade-off in the archived comparison.

Background attributes may encode social inequality or introduce privacy and discrimination risks. Their omission can reduce the information available for accurate predictions while also changing who receives support. Neither approach becomes ethically defensible solely by improving overall AP. Equity requires subgroup errors, alert allocations, safeguards against stigmatization, involvement of students and staff, and attention to the consequences of intervention decisions (Pardo & Siemens, 2014; Opoku et al., 2025).

### 5.3 Prediction timing

For the archived day-14 eligible population (*N* = 25,228), XGBoost achieved AP **0.661962** and Brier **0.209305**; for day 42 (*N* = 24,500), AP **0.700813** and Brier **0.196757**. These are **not a longitudinal causal contrast**, because eligibility, remaining risk and available information all change with the cutoff. A fair time-horizon comparison would also report how many at-risk learners are already lost before action and the marginal opportunities for intervention.

## 6. Explainability, disparities and intended use

The existing result narrative reports that mean absolute held-out Tree SHAP importance is prominent for active VLE days, baseline education, early submissions, studied credits and a gender indicator. Those are **model attributions**, not experimental evidence of a feature's influence on student behavior or final grades (Lundberg & Lee, 2017). A ranked list also provides no independent reassurance that model dependence is stable across modules, correlated features, or demographics.

The current committed aggregate table set contains no externally inspectable subgroup score or false-positive-rate table, no alert-capacity evaluation and no feature-attribution CSV. Although the code contains procedures to produce some of these locally, absence of verified derived files means the repository **does not yet substantiate quantitative fairness, SHAP stability or outreach-impact claims**. Sensitive attributes can be useful for detecting differential performance but require carefully justified access, minimization and secure governance.

## 7. Discussion: contribution, limitations and falsification

### 7.1 Contribution

The purpose of this independent analysis is not to introduce the first early-warning algorithm. It connects **early information timing**, **econometric uncertainty**, **group-separated predictive comparison**, **course-level transportability**, and **human-centered constraints** in one auditable workflow. Its most instructive observation is the dissociation between the minor main-split boosting advantage and poorer module-level probability scores. That result motivates future work on calibration transfer and decision consequences rather than optimizing one global accuracy statistic.

### 7.2 Limitations

1. **Single historical source.** UK courses in 2013–2014 cannot stand in for modern U.S. online, blended or community-college programs.
2. **Selection at the cutoff.** Only students still registered by day 28 are represented; excluded early withdrawals may be a disproportionately vulnerable group.
3. **One retained enrollment per person.** Duplicate-student exclusion changes the target population and may not reflect multi-course advising scenarios.
4. **Observational dependence and confounding.** Engagement predictors, course design and learner outcomes are not experimentally assigned. The archived clustered-inference pathway requires verification.
5. **Small contextual support.** Seven modules and 22 course presentations do not support strong transport conclusions or precision in cluster-based uncertainty.
6. **Calibration and subgroup gaps.** Overall Brier differences cannot alone establish calibration; published aggregated subgroup, SHAP stability and threshold-capacity audits are incomplete.
7. **Reproduction status.** Checked-in CSV metrics are present, but source data, all model-selection manifests and exact reproducibility fingerprints are not contained here. The independent raw-to-table comparison remains open.
8. **No intervention outcomes.** Neither the educational benefit nor the potential harm of acting on an alert is observed.

### 7.3 Evidence that would challenge these conclusions

The tentative argument that portability matters would weaken if a separately preregistered set of new courses showed stable calibration, consistent model ordering, and negligible sensitivity to feature composition. The claim of usable early risk signal would weaken if external prospective evaluation found that predictive discrimination collapsed after accounting for cohort shifts, data quality or access inequities. The broader human-centered rationale would fail if deploying flags measurably worsened learner autonomy, discrimination or student outcomes despite acceptable model metrics.

### 7.4 Next study: actionable evaluation without causal overreach

A prospective replication should prespecify learner eligibility and outreach capacity, use several independent institutions, separate model fitting from temporal and institutional validation, estimate calibration intercepts/slopes and reliability curves with uncertainty, assess subgroup disparities without publishing small cells, and measure resource-constrained precision (e.g., positive predictive value in the highest-risk 5% or 10%). Only after validated operational safety should an independently approved experiment compare **support strategies**, not just prediction scores, with consent and governance appropriate to the setting.

## 8. Transparency and citation

All displayed numerical estimates were transcribed from the original committed, aggregate evidence tables. This revision has **not invented observations, rerun undisclosed analyses or asserted novel causal effects**. Scripts for auditing tabulated values and regenerating aggregate-only SVG figures are in the repository. The [reproducibility ledger](REPRODUCIBILITY_AUDIT.md) identifies any inferential or raw-data-to-output checks that remain open.

**Data attribution:** Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2017). Open University Learning Analytics dataset. *Scientific Data, 4*, Article 170171. https://doi.org/10.1038/sdata.2017.171

**Full verified scholarly references:** [REFERENCES_APA7.md](REFERENCES_APA7.md).

**Manuscript status:** not peer-reviewed or accepted; no DOI is assigned to the present working project. Original OULAD authors and The Open University do not endorse this analysis.
