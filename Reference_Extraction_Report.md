# Attached reference set — extraction smoke test

Processed in a separate local SQLite database; not imported into the public demo. This tests technical extraction, not authenticity or regulatory compliance. No authority was contacted and no record was marked Verified.

| File | Type | Pages | Text characters | Candidate fields | Result |
|---|---|---:|---:|---:|---|
| Affidavit-1.pdf | affidavit_1 | 1 | 2013 | 0 | Extracted — needs review |
| Affidavit-2.pdf | affidavit_2 | 3 | 8929 | 0 | Extracted — needs review |
| Undertaking.pdf | undertaking | 1 | 815 | 0 | Extracted — needs review |
| NBA.jpg | nba | 1 | 2055 | 3 | Extracted — needs review |
| NAC.jpg | naac | 1 | 572 | 4 | Extracted — needs review |
| Affiliation3.pdf | affiliation | 3 | 3736 | 0 | Extracted — needs review |
| TER-Payment-Receipt.pdf | ter_payment | 1 | 1139 | 5 | Extracted — needs review |
| EOA Issued From AICTE – Takshshila.pdf | eoa | 11 | 18793 | 0 | Extracted — needs review |

## Interpretation

- Label-based extraction is intentionally conservative; few or zero candidates does not mean the document has no fields. Use Ollama extraction or human-reviewed entry for prose, complex dates and tables.
- OCR text/confidence are not authentication results. Check names, scope, programme-specific validity and original pages.
- Supplied documents concern different institutions and/or contain unfilled templates. Each file is isolated in an UNASSIGNED REFERENCE case until ownership is confirmed.
- The EoA attachment is a website printout with embedded material; classify and verify each actual letter/year rather than treating the whole printout as one official approval.
- The supplied NBA image indicates programme-specific validity up to 30 June 2026. The NAAC image shows validity up to 20 December 2028. These are visual observations only, not authorized source confirmations; conditions and subsequent extensions require review.
- Full raw extraction and candidates are retained locally in reference_extraction_results.json; they are excluded from the downloadable source bundle.