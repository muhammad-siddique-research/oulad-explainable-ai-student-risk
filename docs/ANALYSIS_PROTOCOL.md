# Prespecified quantitative research protocol

## Research questions and hypotheses
**RQ1:** What associations exist between early learner activity and later academic failure or withdrawal after adjusting for recorded characteristics and course context?  
**H1:** Greater day 0–27 VLE activity is associated with lower later academic-risk likelihood, conditional on recorded variables; this is an association, not a treatment effect.

**RQ2:** Does XGBoost improve out-of-presentation predictive discrimination compared with L2-regularized Logistic Regression?  
**H2:** XGBoost yields higher held-out average precision; uncertainty and group differences must be evaluated before making a superiority claim.

**RQ3:** How calibrated and stable are model probabilities and SHAP attributions across course presentations, cutoff windows, and sufficiently sized subgroups? This is a diagnostic question, with no forced directional hypothesis.

## Cohort and target
- Unit: anonymized student–module–presentation enrollment, from the historical 2013–2014 OULAD release.
- Decision time: 28 days after course start, exclusive feature horizon 0–27.
- Eligible learner: registered before decision time and not already unregistered.
- Outcome: end-of-course Fail or Withdrawn (1) versus Pass or Distinction (0).
- Repeated students: first retained presentation per student in primary analysis; alternative retained-enrollment sensitivity analysis.

## Predictors and validity safeguards
- Early VLE total clicks, active days, submission-count indicators, and baseline demographic/course variables.
- Do **not** include later VLE events, end-course grade, unregistration after decision time, future scores, or assessment feedback with unknown release date.
- Keep human-interpretable statistical associations distinct from causal effects. Timing and grouping limitations must be prominently stated.

## Validation
- Outer held-out split by entire course presentations, excluding overlapping student identifiers.
- Transformations fitted on training data only; inner group-based hyperparameter selection within training.
- Prevalence baseline, L2 Logistic Regression, Random Forest, XGBoost.
- Primary predictive metric: average precision; secondary AUROC, Brier, log loss and prevalence.
- Quantify repeated grouped-split variability. Repeated splits overlap and are **not** independent randomized trials.
- Analyze calibration and subgroup error with meaningful support thresholds; suppress cells with fewer than 30 records.

## Statistical inference
An exploratory linear probability model with HC3-robust standard errors, course-presentation indicators, logged clicks and recorded covariates is included. For journal-standard uncertainty, add presentation-clustered inference with a sufficiently large effective number of groups and transparent small-cluster limitations. These coefficients remain observational associations.

## Model explanation
Tree SHAP calculated only for held-out predictions. Mean absolute SHAP values are measures of fitted model reliance; they are not causal effects. Re-evaluate across outer holdouts to assess attribution stability.

## Interpretation boundary
No physical or virtual Robotic Teaching Assistant was deployed, no experimental treatment occurred, and transferability to present-day U.S. education is unestablished.
