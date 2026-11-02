# AEGIS v2.2 — PDF → images → OCR → Ollama → reviewed fields

This guide supersedes the v2 heuristic PDF-text extraction behavior.

## New upload flow

```text
Upload a PDF / PNG / JPEG
       ↓
PDF: rasterize every processed page to a PNG image with pypdfium2
Image: open/orientation-normalize the supplied image
       ↓
Tesseract OCR on each image
       ↓
Save page image, recognized text and average token confidence
       ↓
Automatically call the Ollama structured-extraction agent
       ↓
Validate typed candidates and exact page-linked quotations
       ↓
Show institution features, document-specific fields and stage states
       ↓
Human correction / confirmation and separate authority verification
```

**No embedded-PDF-text shortcut or fallback is used for newly processed PDFs.** A digital/text-bearing PDF is rasterized and OCRed in the same way as a scanned PDF. This trades text fidelity and speed for the requested consistent image-first pipeline. The original file is retained for download and the institution ZIP.

## Seven core features on all 27 document schemas

| Display field | Stored key |
|---|---|
| Institution name | `institution_name` |
| Institution address | `institution_address` |
| Institution permanent ID | `institution_id` |
| Reference / certificate number | `reference_number` |
| Issuing authority | `issuing_authority` |
| Issue date | `issue_date` |
| Expiry date | `expiry_date` |

Dates use ISO `YYYY-MM-DD`. Unknown fields stay unknown, not application-form defaults. Other document-specific fields and tables remain supported. No reference-number upload input has been reintroduced: the value is extracted or corrected in evidence review.

## Using it

1. Open the correct application and upload the document under its matching type.
2. Wait for processing. Upload now performs rendering, OCR, Ollama and institution ZIP rebuild synchronously.
3. The browser opens **Structured evidence review** automatically.
4. Inspect the stage strip and seven-feature summary.
5. Expand **Source pages** to compare the rendered image and recognized OCR text. Click an image to view it at full size.
6. Review/correct candidates in **Typed fields & tables**, providing page, evidence excerpt and rationale.
7. A staff reviewer can select **Retry complete OCR → Ollama pipeline** to redo both stages, or **Retry Ollama fields only** after correcting the inference service.
8. Rerun application validation when confirmed fields should be checked for consistency or validity.

New uploads and authorized reference imports automatically invoke the pipeline. A validation run invokes it for an attached original that has not yet been fingerprinted/extracted. Previously processed records are **not silently reprocessed** on upgrade: staff should use the complete-pipeline retry button.

## Dependencies and configuration

```bash
python -m pip install -r requirements.txt
python manage.py migrate
```

Install Tesseract separately, install the desired language packs, and ensure its executable is on the server PATH. Windows PowerShell example:

```powershell
$env:TESSERACT_CMD = 'C:\Program Files\Tesseract-OCR\tesseract.exe'
$env:OCR_LANG = 'eng'
$env:OLLAMA_URL = 'http://127.0.0.1:11434'
$env:OLLAMA_MODEL = 'qwen2.5:7b'
python manage.py runserver
```

Install/start Ollama separately and pull the matching model:

```bash
ollama serve
ollama pull qwen2.5:7b
```

Do not start a second Ollama instance if it is already a managed service. Restart Django after changing environment configuration. `.env` is still not auto-loaded.

| Setting | Default |
|---|---|
| OCR_MAX_PAGES | 20 |
| OCR_RENDER_SCALE | 2 (approximately 144 DPI for standard PDF points) |
| OCR_MAX_PIXELS | 25,000,000 per page/image |
| OCR_MAX_CHARACTERS | 120,000 per document |
| OCR_LANG | eng |
| Tesseract OCR timeout | 30 seconds per page |
| Structured Ollama timeout | 45 seconds per request |
| Structured agent input | First 12 page records; first 6,000 characters each |

The default pipeline does not guarantee full coverage of documents exceeding those limits. Stage counts and logs expose failed, partial or truncated processing. No live progress polling/background queue is implemented; the stage strip reflects saved state when the page loads. Large PDFs can make requests slow and may exceed hosting/proxy timeouts; production needs an asynchronous bounded worker pipeline.

## Failure states and review safety

- Render failure: no embedded-text fallback is used. Inspect the original or ask for a readable replacement.
- OCR failure: retain rendered images where available, mark OCR failed/partial, and skip Ollama if no readable page text exists.
- Ollama offline/invalid response: retain OCR and conservative pattern candidates, mark Ollama **Unavailable**, and do not assert AI results.
- Exact-quote checks ground the evidence excerpt, not the correctness of the interpretation. Every candidate needs human confirmation.
- Retries delete stale unconfirmed candidates, retain previously confirmed values as **Recheck required**, and replace page images. Historical field-review audit records remain, but this is not an immutable versioned image archive.
- Rejected fields may be proposed anew after a full retry; the current prototype is not a complete evidence-reconciliation workflow.
- Issue/expiry values are not automatically written into uploader-declared metadata. Confirmed extracted expiry participates in separate validation checks. Do not infer institution-wide validity from a programme-specific date.

## Private storage and archives

`DocumentPage.image` stores PNGs under `<MEDIA_ROOT>/page_images/`. Images are served only through the authenticated, owner/staff-scoped page-image endpoint; access is logged and responses are private/no-store. No public media route is enabled. Back up page images along with original files and SQLite.

One private ZIP per institution ID remains maintained. It includes original uploads and a manifest, not rendered images, OCR text or reviewer notes. Authorized downloads retain the previous access controls.

## Implementation files

- `core/extraction.py`: render/OCR and automatic `process_document()` orchestration.
- `core/schemas.py`: seven shared fields and document-specific contracts.
- `core/models.py`: document pipeline state and private page-image storage.
- `core/views.py`: automatic upload processing, retry, field summary and protected page images.
- `templates/core/document_workspace.html`: pipeline strip, common features, page-image/OCR review and existing field/verification forms.
- `core/migrations/0003_*` and `0004_*`: additive schema upgrades.

Extraction and manual field confirmation are not document authentication. No live authority connector or automatic regulatory decision is introduced by this upgrade.
