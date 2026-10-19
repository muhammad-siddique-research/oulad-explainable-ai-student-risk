# Explainable AI for Early Academic Risk
### Robust Econometrics · XGBoost · SHAP · Higher Education Learning Analytics

**Researcher:** Muhammad Siddique, Ph.D.  
**Project type:** Observational computational education research | Reproducible Python methods | UK Open University Learning Analytics Dataset (OULAD)

> **Research status — October 2026:** Empirical analyses on the authentic UCI OULAD archive have now been executed and checked. A 50-page, 47-reference scholarly working manuscript reports results and limitations. **This research is not yet peer-reviewed or accepted for publication, and no robotic AI intervention was evaluated.** The source archive SHA-256 is `f2ed1902616c1fe8d2824d872c0b7d2d72be435bf0124d077044fe4be2c6d3e4`.

## Authentic empirical results

- **24,835 distinct eligible learners**, 22 course presentations, 42.8% later Fail/Withdrawn.
- Six full presentations held out for primary testing (**7,239 learners**).
- **XGBoost:** AP **0.685**, ROC-AUC **0.724**, Brier **0.204**.
- **L2 Logistic Regression:** AP **0.663**, ROC-AUC **0.717**, Brier **0.209**.
- XGBoost's advantage is **modest**; under leave-one-module-out validation its Brier score is worse than Logistic Regression on **five of seven modules**, highlighting distribution-shift and calibration risks.
- HC3 and course-presentation clustered Econometric estimates associate early activity with subsequent risk; these **are not causal effects**.
- See [verified results and scope limitations](docs/REAL_DATA_RESULTS_AND_LIMITS.md) and [aggregate numerical tables](results/primary_models.csv).

## Research contribution
This project examines whether **early digital learning activity** can help estimate subsequent academic risk using a combined econometric and machine-learning framework. It explicitly separates **conditional statistical associations**, **out-of-sample prediction**, and **model explanation**.

| Research question | Approach | Output |
|---|---|---|
| RQ1: What early-activity patterns are associated with later academic risk? | Prespecified statistical models, robust uncertainty, sensitivity checks | Associational estimates, diagnostics |
| RQ2: Does gradient-boosted learning improve held-out prediction? | Logistic Regression, Random Forest, XGBoost and prevalence baseline | Average precision, AUROC, log loss, Brier score |
| RQ3: Are explanations reliable across learning contexts? | Held-out Tree SHAP, calibration, presentation and subgroup checks | Descriptive attribution and stability summaries |

**Outcome:** `Fail` or `Withdrawn` versus `Pass` or `Distinction`, among learners still registered at the study cutoff.  
**Information horizon:** first **28 course days** (day 0–27), with planned 14/42-day sensitivity analyses.  
**Generalization:** held-out course-presentation groups and non-overlapping students, rather than random row splitting.

## Authentic sources and citation

**Original institutional source:** [Open University OULAD](https://research.stem.open.ac.uk/ouanalyse/dataset/)  
**Original dataset deposit:** [Figshare](https://doi.org/10.6084/m9.figshare.5081998)  
**Archived release:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset) — [DOI](https://doi.org/10.24432/C5KK69)  
**Peer-reviewed dataset descriptor:** Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2017). Open University learning analytics dataset. *Scientific Data, 4*, Article 170171. https://doi.org/10.1038/sdata.2017.171  
**Original dataset license:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

The original data describe **32,593 learner–module registrations**, **22 module presentations**, and **10,655,280 daily virtual learning environment interaction records**. These are **published source totals, not the filtered research sample**. Cite and acknowledge the original authors. The present analysis is not endorsed by the Open University.

See [source provenance](docs/OFFICIAL_DATA_SOURCES.md), [analysis protocol](docs/ANALYSIS_PROTOCOL.md), [data dictionary](docs/DATA_DICTIONARY.md), and [research integrity](docs/RESEARCH_INTEGRITY.md).

## Reproduction (Python 3.11+)

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

**Obtain the original data** via the institutional Figshare deposit or the official UCI archive; archive size is approximately 44.6 MB. Place the seven original CSVs in `data/raw/`, which is excluded from version control.

```bash
python scripts/download_official_oulad.py --destination data/raw
python -m src.prepare_oulad --data-dir data/raw --output data/processed/oulad_day28.csv --cutoff-day 28
python -m src.empirical --input data/processed/oulad_day28.csv --output-dir outputs/real_oulad
python -m src.robustness --input data/processed/oulad_day28.csv --output-dir outputs/real_robustness
```

**Offline, fictional test data (never empirical evidence):**
```bash
python -m src.generate_synthetic --output-dir data/synthetic
python -m src.empirical --input data/synthetic/synthetic_cutoff_features.csv --output-dir outputs/SYNTHETIC_DEMO --demo
```

For any publication, preserve exact environment and data hashes, document exclusions, rerun independent split and sensitivity checks, audit subgroup cell sizes, and populate manuscript tables **only from actual OULAD results**.

## Repository navigation
- `src/prepare_oulad.py`: prospective cutoff and pre-outcome data construction
- `src/empirical.py`: modeling, validation, model explanations and robust association
- `src/robustness.py`: repeated held-out group sensitivity
- `src/generate_synthetic.py`: unmistakably fictitious software-test fixtures
- `scripts/download_official_oulad.py`: Figshare acquisition and source checksums
- `tests/`: leakage, split, and provenance integrity checks
- `docs/`: protocol, provenance, data dictionary, limits, publication readiness

## Research integrity
The study is **quantitative** and **retrospective**; its analytic results are not causal. No proprietary student datasets, private student records, or authentic subject-level predictions are included in this repository. SHAP describes fitted predictive contributions, **not educational interventions or mechanisms**. Discriminatory use of academic-risk scores for punitive decisions is outside the scope of this research.

**Manuscript status:** an extended scholarly working draft exists; its Results section is awaiting real-data computation, independent verification, and journal-specific finalization. Do not describe the draft as a published or peer-reviewed article.

---
*Econometric rigor × Reproducible ML × Human-centered Educational Research.*
