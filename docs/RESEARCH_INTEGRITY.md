# Research Integrity, Interpretation and Disclosure

## Evidence classification

1. **Original, historical OULAD data:** authentic UK 2013–2014 source under the original authors' CC BY 4.0 terms; the source is not U.S. student data.
2. **Archived aggregate empirical results:** six CSV files reporting cohort-specific performance, regression and sensitivity. Their arithmetic has been checked, but raw source-to-table replication is not yet independently verified.
3. **Software unit tests:** rely on intentionally fictional fixtures; passing tests does **not** prove any OULAD estimate.
4. **Proposed analyses:** calibrated risk thresholds, capacity-limited alerting, SHAP stability, full subgroup parity/harms, prospective and causal validation remain unverified or future work.

## Nonnegotiable interpretation limits

- This is **quantitative retrospective observational research**. A click or submission coefficient is not a treatment effect.
- No robot, AI classroom assistant, live teacher feedback, randomized educational treatment, measured advising intervention or proof of U.S. program effectiveness appears in the source.
- Held-out ranking metrics, Brier scores, HC3 regression and model SHAP address **different** research questions; none alone establishes fair, reliable operational decisions.
- Course-presentation grouping and repeated persons introduce dependence. Cluster-robust confidence intervals require an independently checked estimation sample and transparent small-cluster qualification.
- No subgroup performance table is currently committed. Do not assert a measured fairness improvement or publish small subgroup estimates without privacy review.
- The project was not demonstrated to be publicly preregistered and no venue has accepted or peer reviewed it. The 2025–2026 OULAD literature already contains overlapping risk prediction and fairness approaches; do not claim to be the first.
- Do not add row-level fitted scores, raw CSVs, person IDs, restricted data, credentials or sensitive individual narratives to the repository.
- Original OULAD attribution and CC BY 4.0 licensing remain distinct from the MIT software license.
- Document authorship, institutional affiliation, research support, conflicts, tool assistance, ethics and journal-specific disclosure requirements truthfully before submission.

## Responsible use

No human or automated adverse educational decision should use these archived models. Before a real student-support pilot, establish legal and institutional permission, consent/notice as applicable, human oversight, appeal pathways, privacy minimization, prospective calibration and fairness audits, and an intervention design that measures student outcomes. See [Model Card](MODEL_CARD.md) and [Reproducibility Audit](REPRODUCIBILITY_AUDIT.md).
