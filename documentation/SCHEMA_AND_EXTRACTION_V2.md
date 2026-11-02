# AEGIS v2 — Structured extraction and source-review guide

This upgrade extends the existing Django/SQLite prototype. It does not certify the documents, determine legal applicability or add access to restricted authorities.

## Upgrade

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py test
python manage.py runserver 0.0.0.0:8000
```

Stop/restart the running server after upgrading. Back up the SQLite database and private files first. Existing document records remain compatible. To create page records for older originals, use **Retry OCR / text extraction** in their structured review workspace.

### OCR prerequisites

Install the separate Tesseract executable using your approved system installer. Linux commonly uses `sudo apt install tesseract-ocr`. Windows can set:

```powershell
$env:TESSERACT_CMD = 'C:\Program Files\Tesseract-OCR\tesseract.exe'
$env:OCR_LANG = 'eng'
```

`OCR_LANG` supports installed language packs, for example `eng+hin` or `eng+tam`. Missing packs cause explicit extraction errors. Configuration is read from the process environment, not automatically from `.env`.

## 27 supported document types

- Previous EoA; general NOC / Permission; general Affidavit / Undertaking.
- Affidavit I; Affidavit II; institution letter of undertaking.
- Fire Safety NOC / Certificate; Pollution Control NOC / Consent; State Government NOC / Permission; New Course / Intake Increase NOC.
- Building / Infrastructure; general Accreditation certificate; NBA programme accreditation; NAAC institutional accreditation.
- University / State affiliation; Government approval order.
- Approved intake letter; course-wise approval records.
- Faculty list; faculty appointment letter; faculty qualification certificate; Principal / Director qualification proof.
- Trust / Society registration and resolution.
- Past deficiency records; self-disclosure compliance checklist.
- TER payment receipt; full application history.

The authoritative field contracts are in `core/schemas.py` and `documentation/schemas/*.json`. Inspect/download them through **Document library → Schema catalogue**. Schemas use JSON Schema, typed strings/numbers/integers/arrays, ISO dates and restricted table column names. No field is automatically required for statutory compliance; applicability must be separately approved in regulatory rules.

### Schema coverage

| Category | Included structured fields |
|---|---|
| Affidavit / undertaking | Institution/address/ID, signatory/designation, stamp value/serial, execution date, notary/registration, clause content, template reference |
| Accreditation | Number/reference, issuer, institution, programme rows, status, programme-specific dates, grade/CGPA/scale, issue/expiry, visible seal observation, conditions |
| NOCs | NOC/consent/reference, issuer/state board/department/signatory, premises, issue/expiry, year, course and proposed/approved intake rows |
| EoA | Application/file/permanent institution IDs, year, date, programme/level/intake rows, deficiency remarks, QR/signature observations |
| Affiliation / government order | University/issuer, affiliation/reference/order number, year, order/issue/validity dates, programme rows |
| Intake / course records | Current approved/requested intake, programme/level/year, affiliating body, NRI/international quota declarations |
| Faculty / personnel | Name/designation/department, qualification/specialization, joining/appointment, university/passing year, letterhead observation, declared faculty/student counts |
| Trust/society | Registered name/number/date, resolution number, meeting date, signatories |
| Deficiencies / self disclosure | Category/description/deadline/status/resolution reference rows; item/status/supporting-reference rows |
| TER | Application/transaction/reference, amount/date/year/currency/gateway/status, repeatable payment rows with separate part-payment and declared-total amounts |
| History | Per-cycle application/file/year/status/corrigendum/date/resolution rows |

## Database design

- `Document`: retains original fields, plus schema version, extraction status/log/time and structured-agent status.
- `DocumentPage`: page number, text, extraction method and optional mean OCR token confidence. Unique per document/page.
- `ExtractedField`: key, typed JSON value, source page/excerpt, method, review state, reviewer/time/rationale. Unique per document/key. Arrays contain typed rows under the document's field schema.
- `VerificationRecord`: outcome, source name, evidence reference, checked time, result notes, actor and manual method; timestamped history rather than a single overwritten source result.

These are SQLite tables through Django ORM, not a separate MongoDB/document store. JSON fields allow document-specific typed data without a sparse table with hundreds of unused columns. UI writes validate the relevant field schema. Direct database/admin edits can bypass the workflow and require governance.

## End-to-end review

1. Create the correct institution application; do not mix unrelated institutions.
2. Upload a supported PDF/PNG/JPEG, choosing the specific subtype.
3. Select **Structured extraction & verification** on its application document row, or open its review arrow from Document library.
4. Review **Source pages**, extraction status/log and any OCR confidence. Embedded text has no OCR confidence score.
5. Use **Retry OCR / text extraction** for an existing file if OCR was previously unavailable. Previously confirmed values become **Recheck required**.
6. Use **Extract fields with Ollama** for prose and tables. This optional server-side call is bounded and can be unavailable; it does not fabricate a result when offline.
7. Expand a field, correct the typed value, identify a source page and excerpt, record a rationale and choose **Confirmed**, **Needs review** or **Rejected**. Scalars use plain text; number fields use a JSON number; tables use JSON arrays.
8. Confirmed values are transcription/review outcomes, not authenticity outcomes.
9. Run application validation to check confirmed names, dates, programme-specific validity and matched course/year/level intake consistency.
10. If an authorized manual source confirmation is actually obtained, record its source, evidence reference, checked time, matched scope and result. A Verified outcome additionally requires explicit attestation.

### Example programme table

```json
[
  {
    "course_name": "Civil Engineering",
    "level": "UG",
    "approved_intake": 60,
    "requested_intake": 90,
    "academic_year": "2026-27",
    "accreditation_status": "Accredited",
    "valid_from": "2023-07-01",
    "valid_until": "2026-06-30"
  }
]
```

Illustrative values only. Omit unknown columns rather than guessing or using zero as unknown. A table field currently has one evidence page/excerpt; for multi-page tables record the additional page references in the rationale and inspect originals. A production cell-level multi-page evidence model is not implemented.

### Example faculty table

```json
[
  {
    "name": "Synthetic Faculty One",
    "designation": "Assistant Professor",
    "department": "Computer Science",
    "qualification": "M.Tech",
    "specialization": "Computer Science",
    "joining_date": "2025-07-01"
  }
]
```

Confirmed faculty-list rows are counted for display. When declared faculty and student counts are both confirmed, the UI derives students per faculty. It does not validate staff eligibility, workload, duplicate appointments or any normative faculty-student threshold.

## Actual extraction behavior and limits

- PDFs: embedded text if at least 300 trimmed characters on the page; otherwise rasterize and try Tesseract. This heuristic can miss image-heavy pages containing substantial boilerplate. Review the original and page evidence.
- Rasterization: pypdfium2 at scale 2; images are orientation-normalized with Pillow.
- Image OCR: Tesseract word data reconstructed into lines; token-average confidence recorded. Confidence measures OCR recognition, not truth/authenticity.
- Default maximum 20 pages (`OCR_MAX_PAGES`); text budget 120,000 characters; 25-million-pixel limit; OCR timeout 30 seconds per page. Logs state truncation and failures. Extraction is still synchronous, not a job queue.
- Deterministic field extraction recognizes conservative labels and selected accreditation/payment patterns. It intentionally leaves unknown/template fields empty; it is not a universal layout parser.
- Structured Ollama input: first 12 extracted pages, up to 6,000 characters each, 45-second request timeout. Up to 70 candidates considered. Values must match the field JSON schema and cite an exact excerpt from their page. Confirmed/recheck fields are not overwritten.
- Quote matching grounds the excerpt, not the semantic correctness of the value. Every AI field still needs human review. There is no guaranteed table-extraction accuracy, automatic layout/cell reconstruction or complete cross-page table coverage.
- Template placeholders do not establish executed affidavits. Clause/template-reference fields are available, but comparison to an officially approved affidavit template and legal execution verification are not implemented.
- QR/signature/seal fields store observations only. No QR dereferencing, cryptographic signature check or seal authentication is implemented.

## Consistency and outcomes

Confirmed extraction enables:

- Institution-name comparison with the application; normalization is limited to case/whitespace, so legitimate naming variations need review.
- Expiry checks from confirmed document-level dates.
- Programme-specific expiry checks; these do not generalize NBA programme accreditation to the whole institution.
- Approved-intake comparisons for matching course name, level and exact academic-year text in EoA/intake/course records. It does not resolve superseding approvals or normalize all synonyms/year formats.

Existing declared expiry/fingerprint/checklist checks still operate. Generic affidavit/accreditation/NOC presence rules recognize the corresponding supported subtypes. Rules remain illustrative and must not be assumed applicable to every category. Existing findings still require explicit human reconciliation/resolution.

Manual source outcomes: Verification pending, Verified, Mismatch detected, Expired, Source unavailable, Manual review required. Verification-pending/mismatch/source-unavailable states are now preserved during normal validation instead of being blindly reset. Declared expiry checks can still flag/mark expired documents. Previous source outcome records remain in history.

There is **no live AICTE/NBA/NAAC/bank/NOC source adapter**. A manual Verified record is a reviewer's attestation of separately obtained authorized confirmation, not a machine-verified issuer response. Evidence references are stored but not fetched, and there is no sealed response-attachment store or dual authorization. Use this only under an approved confirmation/retention process. Verification of one document does not approve the application.

## Supplied reference attachments

Eight attachments were technically extracted in an isolated local review database, not added to the public demo. See `Reference_Extraction_Report.md` for counts. Full reference data/database/originals are not included in the source archive.

The references include different institutions, templates, programme accreditation, institutional accreditation, affiliation evidence, payment rows and a website EoA printout. They must not be treated as a single application. To import your authorized copies into a restricted deployment:

1. Disable `DEMO_MODE=0` in **all** web/process environments and restart. Confirm demo entry is denied.
2. Create an active non-staff institution/reference-review owner through administration.
3. Place the eight original files in an authorized local directory, preserving supplied filenames.
4. Execute:

```bash
python manage.py import_reference_documents --directory /approved/reference/files --owner reference_user --confirm-authorized
```

The command refuses demo mode, requires existing non-staff ownership and explicit authorization, checks the file set, and creates **one isolated UNASSIGNED REFERENCE case per file**. It does not infer institution ownership from filenames or combine unrelated records. Staff should confirm the institution/ownership before reassigning or using the records. Reimport skips existing file-digest references.

Use the included original files already provided by the user; they are intentionally not redistributed inside the downloadable source package. Never run the private evaluation script or import against a public/restricted-data deployment without reviewing configuration and authorization.

## Known production gaps

Fine-grained reviewer assignment, MFA, malware scanning, sandboxed asynchronous extraction, immutable storage, official authorized adapters, dual review, trusted digital-signature validation, automatic clause comparison and reliable complete table parsing remain future work. SQLite and the development server retain the original prototype operational limitations. Human review, legal applicability and final statutory decisions remain outside AI authority.
