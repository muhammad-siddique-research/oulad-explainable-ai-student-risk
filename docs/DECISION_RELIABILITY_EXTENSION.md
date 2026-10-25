# From Accuracy to Responsible Decisions: A Reliability-Aware Early-Warning Audit

**Author:** Muhammad Siddique, Ph.D.  
**Research status:** Proposed post-hoc extension with executable, tested analysis code; **no new authentic OULAD decision-audit outputs are committed or claimed**.  
**Software:** [src/decision_audit.py](../src/decision_audit.py) · [Fictional unit tests](../tests/test_decision_audit.py) · [Main empirical source](../src/empirical.py).

## Research contribution and originality boundary

The existing project demonstrates that XGBoost's small primary holdout advantage in Average Precision does not imply superior Brier performance for every unseen module. The next question is **whether ranking, absolute-risk reliability, and staff capacity would lead to the same preferred model when academic-support decisions are considered**.

This extension operationalizes that question with one testable and auditable evaluation pathway:

1. **Probability reliability:** report Brier score, calibration intercept and slope, and coarse score-versus-outcome bins, while distinguishing evaluation on a holdout from training or deploying a recalibrated model.
2. **Resource allocation:** report mathematically tie-averaged expected precision, recall and lift when only the highest-risk 5%, 10% or 20% of eligible learners can be offered contact.
3. **Context sensitivity:** compare model accuracy and mean predicted risk by held-out course presentation, with minimum group-size safeguards.
4. **Uncertainty:** resample **entire held-out presentations** to construct exploratory paired differences between XGBoost and Logistic Regression in Average Precision and Brier score.
5. **Evidence provenance:** require a companion manifest describing whether the predictions came from historical OULAD or fictional software fixtures; never write learner identifiers into the derived audit files.

**Important novelty limitation.** Calibrated early-warning prediction, fairness auditing, selective prediction and top-percentage outreach are **not new ideas**; Wu, Duan, and Luo (2026) have already examined them on OULAD. Opoku, Pei, and Xing (2025) also address accuracy–fairness trade-offs. Accordingly, this repository claims no priority for inventing those methods. Its distinctive *engineering contribution* is transparent source-status gating, tie-aware resource evaluation and a paired presentation-cluster uncertainty pathway integrated with Siddique's existing Econometric and transportability audit. Whether this combination contributes sufficient **scientific novelty for a paper** requires independent, up-to-date comparative review and authentic-data findings.

## Testable questions, mechanisms and pre-analysis hypotheses

| Question | Proposed test | Hypothesis (not a result) |
|---|---|---|
| **RQ5: Decision capacity** | Compare AP-ranked model selection with top-k PPV, recall and lift at k = 5%, 10% and 20% | H5: best overall AP does not necessarily yield uniformly preferable capacity-limited outreach profiles |
| **RQ6: Probability reliability** | Compute holdout calibration slope/intercept and observed-versus-predicted bins | H6: model rankings by Brier and calibration slope vary by course context |
| **RQ7: Contextual uncertainty** | Paired presentation-resampled AP and Brier differences between XGBoost and Logistic Regression | H7: uncertainty and sign changes limit strong winner-takes-all conclusions based on one grouped holdout |

These hypotheses must be **frozen before viewing the new numerical audit results** if they are to be treated as confirmatory. Otherwise the exercise is transparently exploratory.

### Theory of change versus causal identification

An instructor or advising office has finite time and may wish to identify learners who could benefit from academic support. A model ranks expected risk; a capacity rule determines whom a team *might* contact. The true welfare contribution additionally depends on outreach costs, students' needs, voluntary participation, support availability, intervention quality, and heterogeneous treatment response.

**This repository measures only prediction and hypothetical selection, not outreach effectiveness**. A high-risk group need not be a high-*benefit* group. The analyses cannot identify effects of tutoring or treatment from observational OULAD histories. No optimal outreach policy is asserted.

## Statistical and computational definitions

Given an actual held-out sample of size N, true binary outcome y_i, and historical fitted prediction p_i:

**Average Precision (AP):** a precision–recall ranking summary; interpret relative to held-out outcome prevalence.

**Brier score:** mean squared error N⁻¹ Σ(y_i − p_i)²; lower is preferable.

**Calibration-in-the-large (descriptive difference):** observed prevalence minus average predicted risk, not itself a logistic calibration intercept.

**Logistic calibration diagnostic:** estimate α and β in logit{Pr(Y=1)} = α + β logit(p). Ideal external calibration has α near 0 and β near 1. This is fitted only as a *holdout diagnostic*; the code does **not** replace or recalibrate individual predictions.

**Capacity k:** choose ceil(kN) learners based on risk ranking. If a score tie straddles the boundary, assign the selected share of that tied group its **expected true-positive count under uniform random tie resolution**. Therefore capacity metrics are reproducible and independent of original row ordering.

**Presentation cluster bootstrap:** resample the full set of course-presentation IDs with replacement; retain all learner rows per sampled cluster; compute paired XGBoost-minus-Logistic AP and Brier differences. The reported 2.5th and 97.5th percentiles are **exploratory descriptive intervals**, especially precarious because the principal test has only six held-out presentation clusters. They are not a guarantee of external validity or a validated small-cluster significance test.

## Data requirements and secure workflow

**Do not commit original learner-level predictions.** Run this workflow locally *after* the authentic OULAD analysis. The prior empirical module writes holdout predictions and manifest to an ignored output directory:

~~~bash
python -m src.empirical --input data/processed/oulad_day28.csv --output-dir outputs/real_oulad
python -m src.decision_audit \
    --predictions outputs/real_oulad/holdout_predictions.csv \
    --output-dir outputs/real_decision_audit \
    --bootstrap-replicates 400 --seed 2026
~~~

On Windows PowerShell these lines can be entered separately, with no backslash continuations. The audit automatically reads **outputs/real_oulad/manifest.json** and requires the authentic-analysis study-status marker.

To check code functionality using **invented data only**, first generate the repository's explicitly fictional fixture and run the original empirical module in demonstration mode:

~~~bash
python -m src.generate_synthetic --output-dir data/synthetic
python -m src.empirical --input data/synthetic/synthetic_cutoff_features.csv --output-dir outputs/SYNTHETIC_DEMO --demo
python -m src.decision_audit --predictions outputs/SYNTHETIC_DEMO/holdout_predictions.csv --output-dir outputs/SYNTHETIC_DECISION_AUDIT --demo
~~~

**The demonstration outputs are fictional.** They cannot be substituted for historical student results in a manuscript.

### Aggregate output contract

| Local output | What it provides | What it does not establish |
|---|---|---|
| model_summaries.csv | AP, AUC, Brier, log loss, prevalence, observed–predicted mean difference, diagnostic calibration intercept/slope | Improvement in student persistence |
| capacity_audit.csv | Expected top-k PPV, recall, lift, threshold ties and absolute number of hypothetical alerts | Who would benefit most from support |
| calibration_bins.csv | Only bins with at least 30 observations, showing observed/mean predicted risk | Reliable fine-grained subgroup calibration |
| course_diagnostics.csv | Only sufficiently supported course presentations (default n ≥100, at least 10 outcomes of each class) | External institutional generalization |
| paired_cluster_bootstrap.csv | Exploratory paired XGBoost–Logistic differences and presentation-bootstrap quantiles | Asymptotically valid confidence intervals with six clusters |
| AUDIT_MANIFEST.json | Source-status flag, input-file SHA-256, sample count, seed, capacities and interpretation limits | Independent original OULAD provenance verification |

Only aggregates and metadata are written by the audit. Student IDs and row-level outcomes remain in ignored local source files. Additional fairness stratification would require separately governed demographic access and more robust small-cell, calibration and error-rate checks.

## Baselines and metrics for a future paper

- **Performance:** event prevalence, AP, ROC-AUC, Brier, log loss and logistic calibration intercept/slope.
- **Decision limits:** top-5%, top-10% and top-20% precision, recall and lift; compare to a prevalence-only tie-random benchmark.
- **Context:** per-presentation sample size, prevalence, mean prediction and Brier, with course/presentation IDs kept as evaluation keys rather than model inputs.
- **Uncertainty:** paired cluster bootstrap; repeat over several independently chosen presentation splits, but never count overlapping split replicates as independent experimental units.
- **Sensitivity:** compare fixed k and sensitivity to score ties; inspect baseline-only versus behavior-only covariates; document missingness, shifting eligibility and model calibration differences.
- **Refutation:** if all models exhibit stable calibration, closely aligned capacity metrics and context-invariant ordering under credible independent replication, the hypothesis of consequential ranking–reliability divergence would not be supported.

## Ethical and implementation constraints

Top-k ranking is **not a deployment recommendation**. Before a pilot, institutional research approval, student notice, privacy controls, teacher/adviser participation, consent or other lawful basis, small-cell suppression, opportunity to question flags, and evaluation of harms are required. Fairness cannot be certified by removing one sensitive variable or by comparable overall AP. The model should not be used to deny resources, discipline learners or label ability.

A genuinely ambitious subsequent study would use several colleges to evaluate **where predicted need and the causal benefit of optional academic support diverge**. This would require consent and a credible assignment design—ideally an ethically approved randomized encouragement or phased-support trial with sufficient power and capacity. OULAD alone cannot identify this question.

## Publication-readiness checklist

- [x] Executable post-hoc audit script with deterministic tie handling and synthetic-only tests.
- [x] Provenance-aware empirical/demo separation and no new person-level output writes.
- [ ] Real OULAD predictions regenerated, archive and manifests independently checked.
- [ ] Capacity and calibration results actually computed on the original historical data.
- [ ] Course-cluster dependence and calibration uncertainty evaluated with credible small-cluster alternatives.
- [ ] Equity review completed without small-cell disclosure or ungrounded fairness certification.
- [ ] A comparison table with recent OULAD studies completed before making a scientific novelty claim.
- [ ] A prospective institutional intervention study designed if causal student-support claims are sought.

## Verified primary references (APA 7th edition)

Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2017). Open University Learning Analytics dataset. *Scientific Data, 4*, Article 170171. https://doi.org/10.1038/sdata.2017.171

Opoku, R. A., Pei, B., & Xing, W. (2025). Unveiling accuracy–fairness trade-offs: Investigating machine learning models in student performance prediction. *Journal of Learning Analytics, 12*(2), 125–139. https://doi.org/10.18608/jla.2025.8543

Van Calster, B., McLernon, D. J., van Smeden, M., Wynants, L., & Steyerberg, E. W. (2019). Calibration: The Achilles heel of predictive analytics. *BMC Medicine, 17*, Article 230. https://doi.org/10.1186/s12916-019-1466-7

Wu, S., Duan, J., & Luo, M. (2026). Calibrated early-warning models with fairness auditing and selective prediction for course withdrawal risk: Evidence from OULAD. *PLOS ONE, 21*(7), Article e0352867. https://doi.org/10.1371/journal.pone.0352867

Wu, S., Duan, J., & Luo, M. (2026). Correction: Calibrated early-warning models with fairness auditing and selective prediction for course withdrawal risk: Evidence from OULAD. *PLOS ONE, 21*(8), Article e0355736. https://doi.org/10.1371/journal.pone.0355736
