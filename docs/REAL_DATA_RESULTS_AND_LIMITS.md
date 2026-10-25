# Empirical results and interpretive limits

**Current scope:** Archived aggregate outputs reported from authentic historical OULAD analyses, retained in this repository. See the [full Results and Discussion](RESULTS_AND_DISCUSSION_APA7.md) for manuscript-ready reporting, tables, comparative synthesis, limitations and specific numerical provenance.

## Primary research findings (archived summary)

- **Analytic population:** 24,835 distinct eligible day-28 learners, retained from 27,490 eligible enrollment records; 10,638 (42.83%) subsequently Fail/Withdrawn.
- **Main test:** 7,239 held-out learners from six whole course presentations; remaining 17,596 training learners from 16 presentations; student IDs are separated between sets.
- **Main AP:** XGBoost 0.685175, Logistic Regression 0.663090, Random Forest 0.678167, prevalence 0.422296.
- **Main Brier:** XGBoost 0.204065, Logistic Regression 0.209106, Random Forest 0.205708, prevalence 0.244035.
- **Leave-one-module-out:** XGBoost higher AP on 6/7 modules, while Logistic Regression lower Brier on 5/7.
- **Adjusted associations:** Negative archived Linear Probability Model coefficients for logged clicks (−0.037472), active days (−0.013788) and early submissions (−0.141791). HC3 and cluster intervals are stored in results/econometric_associations.csv; the clustered interval generation pathway needs independent reconciliation.
- **Chronological validation:** 2013 training to 2014 test, XGBoost AP 0.650027 versus Logistic Regression AP 0.619063.
- **Behavior-only XGBoost:** AP 0.602942 versus all-feature AP 0.685175.
- **Cutoff sensitivity:** XGBoost day-14 AP 0.661962 and day-42 AP 0.700813, **on different eligible populations**.

## Critical scope limits

These are **observational predictive findings**, not causal effects of learner activity or of any support intervention. SHAP values describe a fitted model, not educational treatment mechanisms. The source consists of 2013–2014 UK distance-learning records; no physical or virtual robotic tutor was evaluated, and no contemporary U.S. college validation occurred.

The present revision checked the committed aggregate table schemas and numerical claims via python -m scripts.audit_published_results. This does **not** establish that every archive result can be reconstructed from original learner-level data; independent source-data verification and direct model calibration/subgroup audit are still required. See [Reproducibility Audit](REPRODUCIBILITY_AUDIT.md).

The source archive SHA-256 reported in project records is f2ed1902616c1fe8d2824d872c0b7d2d72be435bf0124d077044fe4be2c6d3e4, but the current revision has **not independently checked the raw archive**.

**Publication status:** Unreviewed working research; no peer-reviewed or accepted manuscript is claimed.

**Relevant independently published work:** Opoku, Pei, and Xing (2025) and Wu, Duan, and Luo (2026) examine related OULAD fairness and calibrated early-warning issues. The project does not claim novelty for early student-risk prediction itself. Complete sources: [APA 7 References](REFERENCES_APA7.md).
