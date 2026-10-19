# Reproducibility and future publication

## On your Windows computer (recommended)
1. Clone this **private** repository through your authenticated GitHub session. Do not paste credentials into chats.
2. Install Python 3.11 or 3.12 and run:
   - `python -m venv .venv`
   - `.venv\Scripts\Activate.ps1` in PowerShell
   - `python -m pip install -r requirements.txt`
   - `python -m pytest -q`
3. Download original data using `python scripts/download_official_oulad.py --destination data/raw`, or manually download https://doi.org/10.6084/m9.figshare.5081998 and extract the seven CSV tables to `data/raw/`.
4. Confirm the seven original tables and `dataset_provenance.json` (when obtained through the script).
5. Build the day-28 cohort:
   `python -m src.prepare_oulad --data-dir data/raw --output data/processed/oulad_day28.csv --cutoff-day 28`
6. Run authentic preliminary analyses:
   `python -m src.empirical --input data/processed/oulad_day28.csv --output-dir outputs/real_oulad`
7. Run repeated held-out sensitivity:
   `python -m src.robustness --input data/processed/oulad_day28.csv --output-dir outputs/real_robustness`
8. Record exact Python/package versions (`python -m pip freeze`), raw archive SHA-256, execution date, cohort counts, random seeds, course presentations, model selection and limitations.

## Before any journal submission
- [ ] Actual OULAD archive obtained, seven CSVs checked and citations recorded.
- [ ] Actual sample flow diagram and missingness tables created.
- [ ] Predictions generated only after prespecified cutoff, no post-outcome features.
- [ ] Independent second run reproduces model tables.
- [ ] More than one held-out course-presentation scenario examined.
- [ ] HC3-robust versus course-clustered uncertainty sensitivity described.
- [ ] Average precision, calibration, AUROC and uncertainty compared to baselines.
- [ ] Sensitivity to cutoff day, course presentation and repeated learners tested.
- [ ] Only adequately supported subgroup comparisons reported.
- [ ] SHAP model-attribution limitations reported, rank stability checked.
- [ ] APA references independently verified and manuscript condensed to journal rules.
- [ ] Original authors and CC BY 4.0 data attribution retained.
- [ ] Current findings never misrepresented as contemporary U.S. or experimental evidence.

**This repository is private until you choose to make the software public.** A private link cannot be viewed by job committees or other third parties who lack GitHub access. Publish it only after checking data provenance, research claims and any pending authorship or institutional requirements.
