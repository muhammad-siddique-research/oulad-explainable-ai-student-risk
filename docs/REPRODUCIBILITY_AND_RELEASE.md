# Reproducibility and Release Protocol

## Two separate things a reader can reproduce

**A. Committed aggregated research evidence (no individual data needed)**

~~~bash
python -m pip install -r requirements.txt
python -m scripts.audit_published_results
python -m scripts.build_published_figures
python -m unittest discover -s tests -p test_aggregate_audit.py -v
~~~

These commands check consistency of **previously committed aggregate results** and draw two public-safe SVGs from those tables. They cannot independently reproduce the coefficients, trained models or source archive identity.

**B. Underlying study (local original OULAD archive required)**

~~~bash
python scripts/download_official_oulad.py --destination data/raw
python -m src.prepare_oulad --data-dir data/raw --output data/processed/oulad_day28.csv --cutoff-day 28
python -m src.empirical --input data/processed/oulad_day28.csv --output-dir outputs/real_oulad
python -m src.robustness --input data/processed/oulad_day28.csv --output-dir outputs/real_robustness
~~~

Run full software tests using python -m pytest -q. Validate seven original tables, local archive SHA-256, date assumptions, prespecified cohort flow, exact data lineage, environment versions, model seeds, group identities, hyperparameter settings and independent published-table agreement.

## Before a peer-reviewed manuscript or a public research release

- [ ] Compare original archive SHA-256 with reported prior provenance.
- [ ] Independently reproduce the sample flow and all reported primary performance values from unmodified original CSVs.
- [ ] Reconcile the archived regression coefficients and clustered intervals to source code and the same specified estimation sample.
- [ ] Add direct held-out calibration curves and intercept/slope evaluations; distinguish them from Brier scoring.
- [ ] Verify SHAP rank stability, interpretation and distribution changes on contextual holdouts.
- [ ] Produce adequately supported and privacy-protected subgroup fairness statistics.
- [ ] Evaluate capacity-constrained top-k alerts, false-positive cost, transparency and human review only as prospective extensions.
- [ ] Audit all APA reference metadata and ensure venue-specific methods transparency and ethics statements.
- [ ] Rerun tests and regenerate figures from frozen package dependencies.
- [ ] Ensure working manuscript matches code, existing aggregate tables, and verified original source attribution.

**Repository visibility:** The source repository is currently private. A private GitHub link cannot be evaluated by outsiders without the owner's permission. Public release requires a deliberate repository-visibility action and prior review of code, provenance, any personal data, and author rights.

**Result-reporting rule:** An independently reproducible research claim requires more than numerical agreement among committed CSVs. See [Reproducibility Audit](REPRODUCIBILITY_AUDIT.md).
