# AEGIS v2.3 — Document-specific features and EoA extraction repair

This update replaces v2.2's seven universal features with the fields appropriate to each selected document category. The PDF → image → OCR → Ollama flow and one-institution ZIP remain unchanged.

## Why readable OCR could still show blank features

OCR and structured extraction are separate stages. Earlier deterministic patterns largely expected `Label: value`; AI candidates could also be unavailable or rejected by field-schema/exact-quote checks. EoA letters have wrapped lines, approval dates such as `30-Apr-2025`, file-number prefixes and mixed institution/trust table columns that do not match those simple labels.

The update adds conservative EoA extraction from existing OCR for file number, application ID, Permanent ID when explicitly stated, academic year, approval date, issuing authority and supported institution-name layouts. Ambiguous interleaved addresses remain unknown for manual/Ollama review rather than being asserted as clean addresses. Garbled intake rows remain unknown instead of being invented.

## Dynamic display/schema

**Extracted institution features** now displays every field in the selected type's schema, including tables, rather than just the first seven universal rows.

- Affidavits/undertakings: institution/address, signatory/designation, stamp value/serial, execution date, notary/registration, clauses/template reference. No issue/expiry field.
- Accreditation: number/reference, institution, programme accreditation, grade/score/scale, issue and expiry, issuer/seal observation, conditions.
- Fire NOC: NOC number, issuer, issue/expiry, premises.
- Pollution NOC: consent/NOC number, state board, issue/expiry.
- State permission: reference, courses, academic year, department/signatory. No generic expiry.
- New-course/intake NOC: courses/proposed intake, reference, issue date, approving authority. No generic expiry.
- Previous EoA: institution/address, Permanent ID, application ID, F.No., academic year, programmes/intake, **date of approval**, deficiency remarks and QR/signature observations. **No expiry or generic issue-date field.**
- Affiliation: reference, university, year, programmes and stated validity period/from/until.
- Government order: order number/date, institution, courses, department.
- Intake/course records: programme/level/current/requested intake/year and applicable affiliation/quota declarations. No generic expiry.
- Faculty/personnel: appropriate faculty rows, qualifications, dates, counts and ratio declarations; no generic expiry.
- Trust/society: registration, resolution, meeting and signatories.
- Deficiencies/self-disclosure: status and supporting-reference rows.
- TER receipt: payment/app/institution identifiers, amounts/dates/year/gateway and repeatable transaction rows. No generic expiry.
- Application history: per-cycle identifiers, years, outcomes, corrigenda and deficiency resolution.

Expiry remains available for accreditation and Fire/Pollution NOCs because it was requested there. A programme-specific validity date is not generalized to institutional validity. An academic year, website timestamp or print date is not treated as an expiry.

Upload expiry input now appears only when the selected type supports `expiry_date`; inapplicable posted expiry is ignored. Existing legacy declared expiry values on other types are not used by the automated expiry rule. Legacy extracted keys no longer in a type's schema are hidden and excluded from confirmed-field checks, not silently presented as applicable evidence.

## Existing readable OCR — no need to upload again

1. Install the update and restart Django.
2. Open the document's Structured evidence review.
3. Select **Refresh fields from existing OCR + retry Ollama** (the former Ollama-only retry action).
4. The app reuses saved OCR, runs the improved deterministic patterns and attempts Ollama again.
5. Review candidates and their source pages. If Ollama is offline, pattern candidates can still appear.

A complete pipeline retry remains available when the underlying OCR itself needs improvement. It is not necessary merely to repair field mapping.

Whitespace-only line-wrap differences in AI quotations are now accepted while retaining the actual source substring. Fabricated or semantically different quotations are still rejected. The agent reports accepted/rejected candidate counts and uses only the selected schema. Confirmed/recheck fields are not overwritten by the refresh action.

## What can be extracted from the supplied EoA excerpt

| Field | Candidate from the excerpt |
|---|---|
| Institution | TAKSHSHILA INSTITUTE OF ENGINEERING & TECHNOLOGY, JABALPUR |
| F.No. | Central/1-44641957809/2025/EOA |
| Application ID | 1-44641957809 |
| Academic year | 2025-26 |
| Date of approval | 2025-04-30 |
| Issuing authority | All India Council for Technical Education |
| Permanent ID | Unknown unless explicitly present in another source section |
| Institution address | Requires cleanup because institution and trust address columns are interleaved |
| Intake table | Requires careful page-image/Ollama/manual review because supplied OCR is garbled |
| Expiry date | Not an EoA feature in this schema; not displayed or inferred |

These are unconfirmed transcriptions, not authority verification. The application ID must not be substituted for Permanent ID. If a file contains different letters/years, reviewers must separate the records and not combine unrelated letter fields. The deterministic fallback keeps first-pattern candidates; it is not a complete multi-letter segmentation engine.

Also confirm application ownership: an affiliation to a university does not make a college's EoA an approval issued to that university. Do not rename document institutions to match the application merely to clear a discrepancy.

## Upgrade

Back up the SQLite database and media directory, then:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Run `python manage.py test` for the supplied automated regression suite. Authoritative schemas are in `core/schemas.py`, downloadable through `/schemas/`, and exported to `documentation/schemas/*.json`.

No live issuing-authority verification, complete OCR table parsing, automated clause-template comparison or final regulatory approval is introduced by this update.
