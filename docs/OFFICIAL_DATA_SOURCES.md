# Original data sources, provenance and attribution

**Dataset:** Open University Learning Analytics Dataset (OULAD), historical UK distance-education observations (2013–2014). Original records are not U.S. campus data and contain no deployed robot or AI treatment.

1. **Original university source:** https://research.stem.open.ac.uk/ouanalyse/dataset/
2. **Original Figshare deposit (authors):** https://doi.org/10.6084/m9.figshare.5081998
3. **Figshare public metadata API:** https://api.figshare.com/v2/articles/5081998
4. **UCI Machine Learning Repository dataset 349:** https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset
5. **UCI accession DOI:** https://doi.org/10.24432/C5KK69
6. **Original peer-reviewed data descriptor:** Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2017). Open University Learning Analytics dataset. *Scientific Data, 4*, Article 170171. https://doi.org/10.1038/sdata.2017.171
7. **CC BY 4.0 reuse and attribution:** https://creativecommons.org/licenses/by/4.0/

Dataset-reported total: 32,593 student-course registrations, 22 module presentations, and 10,655,280 daily VLE interactions. These are source totals, *not* the analytic sample under the day-28 restrictions.

## Acquisition and audit
Run `python scripts/download_official_oulad.py --destination data/raw`. The downloader calls the official Figshare public API, validates a deposit-provided MD5 hash if available, computes SHA-256 digests, checks the seven CSV names, and writes `data/raw/dataset_provenance.json`. If download fails, use the original Figshare or UCI page to obtain and locally extract the official archive.

**No raw source dataset is committed here.** Six aggregate CSV result tables are archived in this research repository and described as findings from previous authentic OULAD analysis. This update audited those aggregate values for internal consistency but did **not** independently rerun the original source-data pipeline. Original archive/hash confirmation, exact raw-to-output reconciliation and selected calibration/fairness analyses remain open; see [the evidence audit](REPRODUCIBILITY_AUDIT.md). The official data belong to their original creators; cite them independently of this software.
