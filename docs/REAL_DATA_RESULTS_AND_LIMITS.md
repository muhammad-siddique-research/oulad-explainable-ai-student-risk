# Authentic OULAD results — reproducible secondary-data research

**Dataset:** historical 2013–2014 Open University Learning Analytics Dataset (UK).
**Archive SHA-256:** `f2ed1902616c1fe8d2824d872c0b7d2d72be435bf0124d077044fe4be2c6d3e4`.
**Source:** [Official UCI OULAD dataset #349](https://doi.org/10.24432/C5KK69); [peer-reviewed source descriptor](https://doi.org/10.1038/sdata.2017.171); [Figshare](https://doi.org/10.6084/m9.figshare.5081998).
**Data license:** CC BY 4.0. Neither the university nor dataset authors endorse this analysis.

## Original sample and day-28 eligible sample

- Original course enrollments: **32,593** (28,785 distinct IDs; 22 course presentations)
- Original timestamped VLE interactions: **10,655,280**
- Eligible, registered and not withdrawn by day 28: **27,490 enrollment records**
- Primary analytic cohort after retaining a single eligible course record per anonymized person: **24,835 distinct learners**
- Later Fail or Withdrawn: **10,638 (42.83%)**; Pass or Distinction: 14,197
- Course-presentation held-out test: **7,239 learners from six presentations**; model training: 17,596 from 16 presentations

The risk definition is conditional on still being enrolled at the early cutoff. Source missing-date sentinel `?` is parsed as missing. Precourse VLE events, full-semester outcomes and assessment scores were not used as prediction inputs.

## Primary held-out comparison

| Model | Average precision ↑ | ROC-AUC ↑ | Brier ↓ | Log loss ↓ |
|---|---:|---:|---:|---:|
| Prevalence benchmark | .422 | .500 | .244 | .681 |
| L2 Logistic Regression | .663 | .717 | .209 | .606 |
| Random Forest | .678 | .722 | .206 | .597 |
| Tuned XGBoost | **.685** | **.724** | **.204** | **.594** |

**Research interpretation:** XGBoost's primary advantage over Logistic Regression is only **0.022 AP**, not overwhelming evidence of general superiority. Six held-out course-presentation clusters provide limited uncertainty information. Paired cluster-bootstrap AP difference: ~0.023 (exploratory 95% interval ~0.005–0.050).

## Adjusted econometric associations

Linear probability model including presentation fixed effects and recorded baseline controls:

| Early behavior | Conditional coefficient | HC3 95% CI | Presentation-cluster 95% CI |
|---|---:|---:|---:|
| log(1 + VLE clicks) | −.0375 | [−.0432, −.0317] | [−.0472, −.0277] |
| Recorded active VLE days | −.0138 | [−.0150, −.0125] | [−.0156, −.0120] |
| Distinct early assessment submissions | −.1418 | [−.1537, −.1299] | [−.1847, −.0988] |

The regression estimates adjusted **associations, not the causal effect of clicks or assignments**. There are 22 presentation clusters and unmeasured determinants of both engagement and outcomes.

## Transport and sensitivity

- **2013 → 2014 test:** XGBoost AP .650, ROC-AUC .703, Brier .211; Logistic Regression AP .619, AUC .699, Brier .215.
- **Behavior-only XGBoost:** AP .603, AUC .661, Brier .223 vs all-feature XGBoost .685, .724, .204. Removing group and academic-background features has a measurable performance cost, but this does **not** license unreviewed sensitive-data use.
- **Repeated presentation splits (five overlapping seeds):** mean AP XGBoost .677 vs Logistic .648; overlapping splits are not independent experiments.
- **Unseen-module transfer:** XGBoost AP is greater on six of seven modules, but Logistic Regression has the better ROC-AUC on five and Brier score on five. This is evidence of context-sensitive generalization, not universally superior model quality.
- **Cutoff sensitivity:** day-14 XGBoost AP .662; day-42 AP .701. Eligible cohorts differ by time; do not interpret these differences as a causal benefit of waiting.

## Explainability and ethical limits

The primary fitted model relied most on active VLE days, baseline highest-education category, early submissions, studied credits, and a gender category under mean absolute held-out Tree SHAP. SHAP is an attribution to a **predictive model** and is not causal inference.

**Not studied:** Robotic teaching assistant, U.S. institutional outcomes, experimentally assigned AI advice, or deployment effects.

**Publication status:** Original empirical models have been executed on the real dataset and the manuscript includes their findings; this is a **working research manuscript**, not a peer-reviewed or accepted paper. All code and bibliography should be independently reviewed before public release/submission.

**Relevant contemporary literature:** Wu, M., Jia, J., & Pham, T. T. (2026). Early warning of academic risk from the first four weeks of online learning activity and assessment performance. *Frontiers in Education, 11*, Article 1917092. https://doi.org/10.3389/feduc.2026.1917092. This recent article studies overlapping OULAD evaluation ideas. The present project does not claim novelty for early-risk prediction itself.
