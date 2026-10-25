# Reproducibility and Evidence Audit

**Scope:** This audit distinguishes authentic-source *provenance*, publicly inspectable *archived aggregate outputs*, software *unit checks*, and an independent *raw-to-result replication*. These are not equivalent achievements.

## Evidence ledger (October 2026)

| Claim / output | Repository evidence | Verification status |
|---|---|---|
| OULAD is a historical UK dataset | Kuzilek et al. (2017); UCI/Figshare source links | Independently traceable bibliographic source |
| Official original record counts | Original descriptor and repository source note | Source-reported; not this project's filtered cohort |
| Archive SHA-256 | Hex digest quoted in archived project docs | Recorded, **not independently rehashed** in this revision |
| Analytic N=24,835 and n-test=7,239 | Results narrative, original preparation code, model table | Committed/reported; requires independent local raw-data replication |
| Model AP/AUC/Brier/log-loss | results/primary_models.csv | **Committed aggregate numbers**, audited for table invariants |
| Module and temporal sensitivity | results/leave_one_module_out.csv; results/temporal_2013_to_2014.csv | Committed aggregate numbers; not independently refit in this revision |
| Feature ablation and cutoff comparisons | results/feature_ablation.csv; results/prediction_cutoff_sensitivity.csv | Committed aggregate numbers, with distinct-cohort caveat |
| HC3 and presentation-cluster confidence intervals | results/econometric_associations.csv | Committed report; **clustered-inference code path / estimation sample requires reconciliation** |
| SHAP attribution ranking | Narrative and the ability to output global_shap.csv | **Numerical SHAP summary not committed**; ranking not independently audited |
| Group fairness and calibration curves | Code supports local subgroup summaries; no committed comprehensive audit | **Pending** verified aggregate diagnostics |
| Software invariants | tests/ with fictional fixtures; CI | Software tests, **not** confirmation of OULAD effects |
| Manuscript publication | Working paper notes | **Unreviewed / not accepted / not published** |

## Independent audit of aggregate tables

~~~bash
python -m scripts.audit_published_results
python -m scripts.build_published_figures
~~~

The audit checks the CSV schema, finite metric ranges, model and module pairs, matching held-out sample denominators, explicit AP/Brier win counts, and coefficients' interval containment. It **does not** recompute model estimates from original student records and must never be described as empirical replication.

The publication charts use aggregate results exclusively, making them safe to include in a methodological README without exposing student records. Reported files should remain unchanged until an evidence-backed rerun establishes a correction.

## Underlying raw-data replication pathway

1. Follow [Official Sources](OFFICIAL_DATA_SOURCES.md) to download the unmodified seven CSV tables from the OULAD deposit.
2. Record the downloaded archive SHA-256, acquisition date, extraction tool, package versions and exact data-use license. Reconcile the existing recorded hash.
3. Run the preparation pipeline at the prespecified day-28 horizon and export a **cohort-flow table** documenting registrations, preregistered inclusions, early withdrawals, missing source fields and repeated learners.
4. Rebuild the outer holdout with exact seed, presentation groups and student-exclusion manifest; regenerate primary model scores with no leakage.
5. Independently reproduce the econometric model on the **same explicitly defined analytic observations**. Generate both HC3 and presentation-clustered uncertainty with the number of groups and a small-cluster discussion. Trace any difference to published CSVs.
6. Retain only aggregate or suitably suppressed SHAP, calibration and subgroup outputs for public release, with clear timestamps for prediction and grade availability.
7. Re-run at least one additional contextual holdout and compare fully held-out module performance. Report uncertainty and no empirical precision beyond available independent groups.
8. Only then freeze environment, table/figure hashes and manuscript results for journal submission.

## Independence and version considerations

The visible empirical.py source outputs HC3 regression summaries, prediction tables and potentially SHAP summaries to ignored local outputs. The separately committed summary CSVs appear to represent a broader analysis program than the current single-script output schema; raw-to-committed-table provenance therefore **needs explicit verification**, not an assumption of identity.

Earlier manuscripts and notes had mutually inconsistent statements about whether real-data results were still pending. This revision standardizes the distinction: **committed real-data results exist as reported aggregate files, but independent verification and some audits remain pending**.

## Privacy, ethics and release

OULAD is anonymized and historically public, but republishing person-level records or model predictions is unnecessary. Keep raw archives in ignored local directories, suppress small subgroup cells (minimum 30 as the current protocol), avoid deficit framing, and separate prediction quality from intervention effectiveness. The repository is **private**: outside reviewers cannot access the code without permission until the owner chooses to change visibility.

**Pass/fail rule for a journal submission:** all substantive numerical findings in a manuscript should map to an independent run, archived provenance, a versioned script, an inspectable aggregate table and appropriately qualified uncertainty; otherwise present them as provisional reported results.
