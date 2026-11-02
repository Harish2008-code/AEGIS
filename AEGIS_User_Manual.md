# AEGIS
## Complete Prototype User & Administrator Manual

**AI-assisted application validation and evidence review**  
**Edition:** 1.0 · 30 October 2026  
**Applies to:** the Django/SQLite AEGIS prototype supplied in this workspace  
**Audience:** institution users, authorized reviewers, system administrators and evaluators

> **Important:** AEGIS is an independent demonstration prototype, not an official AICTE portal, certified compliance product or approval authority. All sample institutions and document records are synthetic. Its rules are illustrative. AI observations are advisory; statutory scrutiny, physical inspection and final regulatory decisions remain with competent authorities.

---

> **Version 2 upgrade:** For the expanded 27-type catalogue, scanned-PDF OCR, structured field review and manual verification outcomes, see `documentation/SCHEMA_AND_EXTRACTION_V2.md`. That guide supersedes the corresponding v1 limitations and pending-status behavior below.

> **Version 2.1:** The upload Reference number input has been removed. Uploads now maintain one private ZIP per institution ID. See `documentation/INSTITUTION_ZIP_GUIDE.md` for the current workflow; it supersedes older upload-reference instructions below.

> **Version 2.2:** Uploads automatically run PDF → images → OCR → Ollama. Seven common fields and protected source-page images are shown in review. See `documentation/AUTOMATIC_OCR_PIPELINE.md`; it supersedes earlier extraction/retry instructions.

> **Version 2.3:** Features now follow the selected document schema, not a universal seven-field list. EoA no longer displays expiry. Use Refresh fields from existing OCR + retry Ollama to populate existing readable OCR. See `documentation/DOCUMENT_SPECIFIC_FEATURES_V2_3.md`.

## Contents

1. Purpose and scope
2. Five-minute quick start
3. User roles and permissions
4. Sign-in, navigation and sign-out
5. Overview dashboard
6. Creating and locating applications
7. Uploading and reviewing documents
8. Running validation and understanding the agents
9. Findings, rectification and reviewer resolutions
10. Source verification workflow
11. Document library and review inbox
12. Status and severity reference
13. Compliance-rule administration
14. AI agent workspace and Ollama setup
15. Audit trail and report export
16. Installation and configuration
17. Account administration and data ownership
18. Backup, restore and routine operations
19. Demonstration and evaluation walkthrough
20. Troubleshooting
21. Security, privacy and safe operating procedures
22. Current limitations and production-readiness checklist
23. Glossary and support checklist

---

## 1. Purpose and scope

AEGIS brings institution-submitted applications, supporting documents, preliminary checks, review findings and activity history into one workspace.

### What the prototype does

- Creates application records in SQLite.
- Stores PDF, PNG and JPEG documents in private filesystem storage.
- Extracts embedded PDF text and, when configured, performs image OCR.
- Checks required document-type presence using enabled category/date-specific rules.
- Checks declared expiry dates and the presence of an institution identifier in extracted text.
- Detects identical-file fingerprints using SHA-256.
- Sends bounded extracted-text evidence to an optional Ollama model for advisory observations.
- Links findings to an application, evidence and, where applicable, a document and rule.
- Records source-confirmation requests without pretending an authority has verified anything.
- Allows staff reviewers to record a rationale and resolve findings.
- Provides a dashboard, in-app inbox, CSV export and activity/audit history.

### What it does not do

There is no live AICTE portal connection, issuing-authority integration, automatic statutory approval, conclusive forgery detection, digital-signature verification, QR verification or physical infrastructure certification. There is no trained infrastructure computer-vision model, automated email/SMS notification service, online fee verification or restricted-record synchronization.

Use authorized, anonymized or synthetic data for evaluation. Do not treat a successful validation run as legal compliance or document authentication.

## 2. Five-minute quick start

### Using the running preview

1. Open the AEGIS live preview provided with the application.
2. On the sign-in screen, click **Explore demo workspace**.
3. Review **Overview** and its summary cards.
4. Open **Applications** and search for `Meridian`.
5. Open **Meridian Institute of Technology**.
6. Review the synthetic documents, declared expiry and evidence-linked finding.
7. Click **Run validation** as the demo reviewer.
8. Read the run summary. If Ollama is unavailable, deterministic checks still complete and the application says that no AI conclusion was generated.
9. Open **Review inbox** to inspect unresolved findings.
10. Open **Audit trail** to see recorded activity.

**Demo access:** The demo account is `demo.reviewer`. It has no usable password. Use the demo button rather than trying to sign in with a guessed password. The button works only when `DEMO_MODE=1` and the demo seed has been created.

**Synthetic files:** Seeded document records contain fabricated metadata and extracted text, not attached original files. Clicking a seeded document name may display an informational message instead of downloading a file. Upload your own authorized test PDF/image to demonstrate original-file download and hashing.

## 3. User roles and permissions

| Capability | Institution user | Staff reviewer | Superuser administrator |
|---|---|---|---|
| Sign in with an assigned account | Yes | Yes | Yes |
| Create an application | Yes | Yes | Yes |
| View applications | Own records only | All prototype applications | All prototype applications |
| Upload/view/download documents | Own applications | All applications | All applications |
| See findings and application activity | Own applications | All applications | All applications |
| Run validation | No | Yes | Yes |
| Request source verification | No | Yes | Yes |
| Resolve findings with rationale | No | Yes | Yes |
| Open AI agents / compliance rules | No | Yes | Yes |
| Enable/disable rules | No | Yes | Yes |
| Define/edit rules through administration | Not by default | Only if separately granted admin model permissions | Yes |
| Export application register | Own applications | All applications | All applications |
| Manage users and ownership | No | Only with specific admin permissions | Yes |

### Important permission details

- Reviewer authorization is currently determined by Django's **Staff status** (`is_staff`). Staff can review all applications; there is no regional or case-assignment restriction.
- Non-staff access is based on the application's **Owner** user, not its institution ID, email domain or a shared institutional team.
- The seeded **Reviewers** and **Institution users** group names do not themselves enforce the application's access rules.
- The demo reviewer is staff, but is not a superuser and cannot administer all model records by default.
- Some overview links may lead to staff-only pages. An institution user opening a reviewer-only route will receive a permission-denied response.

## 4. Sign-in, navigation and sign-out

### Regular sign-in

1. Open `/login/` on your deployment.
2. Enter your administrator-assigned username and password.
3. Select **Sign in**.
4. If credentials are rejected, check spelling and contact the administrator. There is no self-service registration or password-reset screen in this prototype.

### Main navigation

| Menu | Purpose |
|---|---|
| Overview | Summary of accessible applications, documents and priority signals |
| Applications | Search, filter, create and open application records |
| Document library | Search and inspect uploaded-document metadata |
| Review inbox | Unresolved advisory findings |
| AI agents | Staff-only connection status, agent explanations and inference history |
| Compliance rules | Staff-only checklist configuration and enable/disable controls |
| Audit trail | Latest accessible recorded events |

On narrower screens, the sidebar uses icons rather than full labels. Tables may scroll horizontally. Application content and forms adapt to the available width.

### Sign-out

Use the arrow-shaped **Sign out** button beside your profile at the bottom of the sidebar. Closing a tab is not equivalent to signing out. On shared machines, sign out and close the browser when finished.

## 5. Overview dashboard

The dashboard summarizes the records accessible to the signed-in user.

### Summary cards

- **Total applications:** number of accessible application records.
- **Ready for review:** application status indicates that a previous validation found no unresolved findings. This is not an approval count or verified-document count.
- **Needs attention:** applications with that recorded validation status.
- **Documents received:** number of document records, including synthetic metadata-only seed records.

### Other dashboard areas

- **Recent applications:** five most recently created applications. Click an institution name or row arrow to open its workspace.
- **Requires attention:** up to three unresolved findings, with Critical before Warning before other severities, then most recent first within priority.
- **Purpose-built agent workflow:** explains the extraction → validation → authentication routing → human review journey. It is not a live progress indicator.
- **Export report:** downloads the scoped application-register CSV.
- **New application:** opens intake.

The dashboard is refreshed when a page is requested; it does not use background push updates. Refresh or navigate back after changes.

**Status freshness:** Resolving findings or uploading documents does not automatically recompute the application status. A staff reviewer must rerun validation. Synthetic initial statuses are demonstration data, not evidence that a real validation or source check took place.

## 6. Creating and locating applications

### Create an application

1. Select **New application** from Overview or Applications.
2. Complete the form:

| Field | Guidance |
|---|---|
| Institution name | Required. Use the institution's consistent name. Maximum 220 characters. |
| AICTE institution ID | Required. Maximum 60 characters. For tests, use an explicitly synthetic identifier such as `SYNTH-EXAMPLE-001`. No live AICTE ID lookup is performed. |
| State / Union territory | Required by the intake form. Enter the appropriate location. |
| Application category | Select Extension of Approval, Increase in Intake, New Programme, Change of Name or New Institution. |
| Institutional contact email | Optional contact metadata. The prototype does not send emails. |

3. Select **Create application**.
4. A unique reference such as `APP-26-ABC123` is assigned.
5. The application workspace opens with **Pending validation** status.
6. Upload the required evidence.

The default academic year is **2026–27**. The current form does not allow choosing another year. An administrator can edit the stored year; a production workflow needs controlled year selection.

**Ownership:** The signed-in creator becomes the owner. If staff create a record for an institution, the intended institution user will not see it until an administrator assigns the owner.

### Search and filter

1. Open **Applications**.
2. Enter part of an institution name, application reference or institution ID.
3. Optionally select a validation status.
4. Select **Apply filters**.
5. Select **Clear** to remove active filters.
6. Select an institution name or arrow to open the record.

Search is case-insensitive. Application category is not currently a list filter.

### Editing or deleting applications

There is no general edit/delete form in the main workspace. Authorized administrators can use Django administration to correct fields. Administrative deletion can cascade to related records and is not a normal rectification workflow. Back up data before administrative maintenance and avoid deleting review evidence.

## 7. Uploading and reviewing documents

### Supported types

- Previous EoA
- NOC / Permission
- Affidavit / Undertaking
- Fire safety certificate
- Building / Infrastructure
- Accreditation certificate

The user selects the type. Automatic semantic document classification is not implemented.

### File requirements

- PDF, PNG or JPEG content.
- Maximum **15 MB per file** (15 × 1,024 × 1,024 bytes).
- A readable, authorized test document.
- No videos, spreadsheets, Word files, archives or arbitrary URLs.

The application checks initial file signatures. Renaming a non-PDF file to `.pdf` does not make it acceptable. File-signature checks are not malware scanning or proof of authenticity.

### Upload steps

1. Open the application workspace.
2. Locate **Add supporting evidence**.
3. Choose a **Document type**.
4. Choose the **Document file**.
5. Optionally enter the issuing-authority **Reference number**.
6. Enter the declared **Expiry date** if applicable; leave it blank for a genuinely non-expiring document.
7. Select **Upload document**.
8. Confirm that a new row appears in **Supporting documents**.
9. Expand **View extracted evidence** to inspect the extracted text and SHA-256 fingerprint.

Expiry and reference metadata are declared by the uploader; they are not independently extracted or authenticated. A blank expiry date is not proof of validity.

### Extraction behavior

- Text-bearing PDFs: extracts text from up to the first **60 pages**, retaining up to **60,000 characters**.
- PNG/JPEG: uses Tesseract through pytesseract when both are installed; retains up to 60,000 characters.
- Scanned/image-only PDFs: no integrated PDF-rendering/OCR fallback is supplied. Request a readable version or manually review the original.
- Poor-quality, encrypted, unsupported or damaged documents may produce empty text and an **Extraction needs review** finding when validated.
- There are no OCR confidence scores or page-coordinate evidence highlights.

Upload extraction runs synchronously. A message may mention review/queuing, but no background OCR job queue is implemented.

### Download originals

Select a document name in Supporting documents or Document library. The server checks access, records the file-access event and downloads the attachment. Seeded metadata-only documents have no attached original.

### Correcting a submission

Upload a new evidence file rather than assuming an old file has been replaced. The main interface does not replace/delete documents or automatically supersede older submissions. Clearly identify the current evidence in the review rationale. Ask an administrator to correct mistaken metadata if necessary, and keep the review history intact.

## 8. Running validation and understanding the agents

**Available to:** staff reviewers and administrators.

### Run validation

1. Open the application.
2. Check document types, uploaded evidence and declared dates.
3. Select **Run validation** once.
4. Wait for the request to finish. The button displays a running message.
5. Read **Agent run summary**, application status and **Evidence-linked findings**.
6. Review document statuses and activity entries.
7. For inference history, open **AI agents**.

Validation is synchronous. The Ollama request has a 25-second timeout; extraction and model processing add to total time. Do not repeatedly click the button or resubmit a request that is still processing.

### Checks performed

| Component | Actual behavior | Reviewer caution |
|---|---|---|
| Checklist agent | Applies enabled rules matching `All` or the exact application category, within effective dates; checks document-type presence | Presence does not prove that the content is adequate or genuine |
| Document agent | Checks the submitted expiry date and whether text extraction is empty | Dates are uploader-declared; expiry is flagged only when earlier than the current local date |
| Consistency check | Looks for the exact institution-ID string in extracted text | OCR, punctuation or formatting can cause a false positive; absence is not proof of misconduct |
| Integrity agent | Compares SHA-256 against other document records | Identical files can be legitimate; this is not visual tampering detection |
| Infrastructure triage | Flags building/infrastructure documents for human review | Does not calculate areas, verify facilities or replace inspection |
| Ollama agent | Reviews bounded extracted text and may propose exact-quote-linked observations | AI reasoning can be mistaken even when a quote is genuine |

Duplicate-file matching currently checks the document database as a whole. Findings do not disclose the other record's institution or content. Production cross-institution comparisons require an approved access and privacy policy.

### Ollama input and output limits

Each document contributes its first **2,500 extracted characters** to the model request, together with the institution ID and application category. This is not a full-document guarantee. Up to 12 returned observations are considered. A stored AI finding requires a matching submitted document and a quote longer than five characters present in that document's extracted text.

There are no autonomous browser tools or external lookups for the model. The model's summary remains advisory and must be checked independently. Exact-quote checking grounds the quoted evidence, not the correctness of the conclusion.

### When AI is offline

Deterministic checks still run. A run is recorded as **Unavailable** and the summary says no AI conclusion was generated. Do not report that an offline run used AI successfully.

## 9. Findings, rectification and reviewer resolutions

### Read a finding

Each finding shows its severity or resolved state, originating agent, title, explanation and evidence. A checklist finding may include a rule code, rule version and source reference.

Review the original evidence when available. Do not rely solely on OCR or an AI explanation.

### Resolve a finding

1. Open the relevant application.
2. Find the unresolved item under **Evidence-linked findings**.
3. Check the source document and any additional evidence.
4. Enter a review rationale of at least **10 characters**.
5. Select **Resolve finding**.
6. Confirm the finding is marked **Resolved** and the activity log records the action.

A useful rationale identifies what was checked and why the concern is addressed. Example:

> Reviewed the newly uploaded readable copy and located institution ID SYNTH-EXAMPLE-001 in the header. The extraction warning is resolved; source authentication remains pending.

Avoid unsupported statements such as “genuine,” “approved” or “all compliant” when no authorized evidence establishes them.

### Rectification and reruns

- Institution users can upload additional documents but cannot resolve findings.
- Missing-document findings are **not automatically cleared** after upload. A reviewer must examine and resolve them.
- Reruns preserve existing findings and resolutions; they do not reset the case history.
- The pipeline deduplicates findings by application, title, document and rule code. It does not comprehensively reconcile changing evidence or automatically reopen resolved findings.
- The main interface has no reopen button. A superuser can correct a finding record in administration with appropriate external change documentation.
- Resolving all findings does not itself change the application status. Rerun validation to recompute it.
- Even informational unresolved findings cause **Needs attention**.

Resolution closes an advisory observation only. It does not authenticate a document, issue an approval or authorize adverse regulatory action.

## 10. Source verification workflow

**Available to:** staff reviewers and administrators.

### Request source confirmation

1. Open the application.
2. Locate the document in **Supporting documents**.
3. Select **Verify source ↗**.
4. Read the message explaining that no authorized connector is configured.
5. Inspect the document status and application activity.

### What actually happens

- A source-verification request is recorded in the audit history.
- A non-expired document is marked **Verification pending**.
- A document already marked **Expired** retains that state.
- No portal, API, QR URL, registry or issuing authority is contacted.
- No email or external case assignment is dispatched.
- No verified timestamp or authenticated authority response is created.

The workflow is an internal routing record, not completed verification. Manual confirmation must take place through a separately authorized process. The main interface does not provide a final authority-response capture/approval screen.

**Rerun caveat:** Validation currently resets non-expired, non-Verified document statuses to **Manual review required**. A previously displayed pending status can therefore change after validation. The source-request event remains in the audit trail. Use both the history and the latest status when reviewing.

Do not use administrative status editing to make a document appear verified without an authorized evidentiary process. Stored `source` and `verified_at` fields exist for future integration, but no completed source-authentication workflow is supplied.

## 11. Document library and review inbox

### Document library

1. Select **Document library**.
2. Search by document name or institution name.
3. Select **Search**.
4. Review the document type, institution, verification status and declared expiry.
5. Select the filename to download an attached original, or the institution/arrow to open the application.

Only permitted application records are shown. There is no full-text document search or separate status filter.

### Review inbox

1. Select **Review inbox**.
2. Read the unresolved finding cards.
3. Select **Review →** to open the application.
4. Examine evidence and record a reviewer resolution if authorized.

The inbox shows unresolved findings, generally newest first. Unlike the Overview priority panel, it is not a complete severity-sorted task-assignment system. There are no case owners, deadlines, notification subscriptions or email/SMS delivery controls.

## 12. Status and severity reference

### Application statuses

| Status | Meaning | What it does not mean |
|---|---|---|
| Pending validation | Default for a newly created application | Not automatically an institutional deficiency |
| Needs attention | At least one unresolved finding existed at the last validation | Not rejection, misconduct or proven noncompliance |
| Ready for review | No unresolved findings existed at the last validation | Not approval, authenticated evidence or a complete statutory assessment |

Status reflects the last run and can become stale after uploads or resolutions. Check the **Last validation** timestamp.

### Document statuses used in the normal prototype workflow

| Status | Meaning |
|---|---|
| Manual review required | Default or validation-routed state; human inspection/source work remains necessary |
| Expired | Declared expiry is earlier than today's date, or the synthetic seed explicitly carries that state |
| Verification pending | A reviewer requested source confirmation; no authority response has been obtained by this app |

`Verified` is recognized in code but is not produced by the supplied user workflow. Dedicated mismatch/source-unavailable outcomes require a future authorized connector; do not assume they have been implemented simply because the problem statement requests them.

### Finding severity and resolution

- **Critical:** higher-priority concern, such as a declared expired certificate.
- **Warning:** review needed, such as missing evidence or an absent identifier in extracted text.
- **Info:** advisory routing, such as infrastructure evidence requiring human assessment.
- **Resolved:** a reviewer recorded a rationale. The original severity and evidence remain stored.

Severity is not a confidence score, legal finding or proof of forgery.

### Inference-run statuses

- **Completed:** a model response was processed. It may yield no stored observations.
- **Unavailable:** connection, timeout, response or parsing failure prevented a usable AI result.

An **Ollama connected** badge indicates that the server's model-list endpoint responded; it does not guarantee that the configured model is installed, can fit in memory or will complete inference successfully.

## 13. Compliance-rule administration

### Enable or disable an existing rule

1. Sign in as staff.
2. Select **Compliance rules**.
3. Review requirement, category, source/version and status.
4. Select **Disable** or **Enable** for the intended rule.
5. Inspect **Audit trail** for the configuration event.
6. Rerun affected applications when appropriate.

Rule changes do not automatically validate existing cases or remove previous findings.

### Define or edit a rule

1. Sign in as a superuser.
2. Open `/admin/`.
3. Open **Rules**, or select **Manage rule definitions ↗** on Compliance rules.
4. Create or edit the record.
5. Complete the following fields:

| Field | Meaning |
|---|---|
| Code | Unique identifier, such as `DEMO-FIRE-001` |
| Title | Human-readable requirement/explanation |
| Category | `All`, or the exact application-category text |
| Document kind | Required supported document type |
| Severity | Use consistent values: Critical, Warning or Info |
| Source reference | Approved handbook/clause/instruction citation; explicitly label demo rules |
| Version | Version identifier for the rule definition |
| Enabled | Whether the rule may run |
| Effective from / to | Inclusive dates; blank leaves that side of the range open |

### Applicability logic

A rule runs only when enabled, category equals `All` or the application's exact category, and the current local date falls within its effective range. Dates are evaluated against the run date, not automatically against the academic year or original submission date.

The present rule engine checks document-type presence. It does not execute arbitrary numeric thresholds, faculty ratios, intake limits, infrastructure measurements, fee formulas or legal reasoning. Entering such language in a rule title does not implement that calculation.

Seeded rules require previous approval evidence, undertaking, fire evidence and infrastructure evidence for demonstration. Their `All` applicability is illustrative, not a statement of actual requirements for every AICTE application category.

**Governance:** Map rules to officially approved sources before operational use. Administrative edits do not create immutable rule snapshots, dual-approval workflows or a complete regulatory version-control system.

## 14. AI agent workspace and Ollama setup

### Use the agent workspace

1. Sign in as staff and select **AI agents**.
2. Inspect the Ollama connected/offline badge.
3. Check the configured model name and available model list.
4. Select **Check connection** to reload the connection check.
5. Review component descriptions and the latest 15 inference runs.
6. Select an application reference to inspect its evidence.

The page does not start Ollama, download models or queue a run. Run validation from an application workspace.

### Configure Ollama — administrator

Install Ollama on the Django server or an approved inference host. Obtain the model through your authorized environment.

```bash
ollama serve
```

If Ollama is already running as a service, do not start a second instance. In another terminal:

```bash
ollama pull qwen2.5:7b
ollama list
```

Set the Django environment before starting the application:

```bash
export OLLAMA_URL=http://127.0.0.1:11434
export OLLAMA_MODEL=qwen2.5:7b
```

PowerShell equivalent:

```powershell
$env:OLLAMA_URL = 'http://127.0.0.1:11434'
$env:OLLAMA_MODEL = 'qwen2.5:7b'
```

Restart Django, open AI agents, check connectivity, then run validation on authorized test evidence.

Memory and storage requirements depend on the model and quantization; choose a model that fits the host. A smaller installed model can be selected with `OLLAMA_MODEL`, but output quality and JSON behavior must be evaluated.

The model request is server-side. In a container or remote deployment, `127.0.0.1` refers to that container/server, not the user's laptop. Configure a reachable approved host and protect the inference endpoint. Do not expose an unprotected Ollama service to the internet.

## 15. Audit trail and report export

### Audit trail

Select **Audit trail** to view up to the latest **200** accessible events, newest first. Fields include time, action, actor, application and details. Times use the configured Asia/Kolkata timezone.

Recorded application workflows include:

- Synthetic application initialization and application creation.
- Document upload and SHA-256 digest.
- Original-document access/download.
- Validation completion and number of applicable checklist rules.
- Source-verification requests.
- Reviewer finding resolutions and rationale.
- Rule enable/disable actions.
- CSV export actions.

The application workspace also shows up to eight recent application events. AI runs have their own history.

Not every read, login or administration change is represented in the main audit screen. Staff see global events; institution users see only events linked to owned applications. Global events such as exports may not appear in an institution user's scoped trail.

Prototype audit records are ordinary editable database records, not an immutable or cryptographically signed ledger. Django administration has its own admin action history, which is separate from the main Audit trail.

### Export the register

1. Select **Export report** on Overview or **Export CSV** on Applications.
2. Save `validation-report.csv`.
3. Open it with an approved spreadsheet or CSV tool.
4. Handle the file according to your data-access policy.

Columns: Application, Institution, Status, Open findings, Validated at, Advisory notice.

**Scope:** Export includes all applications accessible to the signed-in user. It does not apply the current Applications search/status filters. It does not include document text, individual finding details, source responses or a full audit export. CSV fields beginning with formula-like characters are escaped for spreadsheet safety.

## 16. Installation and configuration

### Prerequisites

- Python 3.11 or later recommended.
- pip and virtual-environment support.
- A modern browser.
- Write permission to the application directory for SQLite and private uploads.
- Network access to install dependencies, unless using an approved offline package repository.
- Optional Ollama/model and optional Tesseract for image OCR.

### Install from the source archive

1. Extract `aegis-django.zip` into a dedicated directory.
2. Open a terminal there.
3. Create and activate a virtual environment.

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If activation is restricted by your organization's policy, use the virtual environment's Python executable directly or consult your administrator; do not bypass organizational security controls.

4. Install dependencies and create the database:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
```

5. For a synthetic demo only:

```bash
python manage.py seed_demo
```

6. Create an administrator if required:

```bash
python manage.py createsuperuser
```

7. Start the development server:

```bash
python manage.py runserver 0.0.0.0:8000
```

8. Open `http://localhost:8000` on the server machine, or the supplied workspace preview URL. On a separate computer, localhost refers to that computer; use the server's approved address.

The source archive excludes the database, uploaded private files and credentials. `migrate` and `seed_demo` reconstruct the schema and synthetic workspace. Repeating `seed_demo` does not reset existing records or their review changes.

### Optional Tesseract setup

On a supported Debian/Ubuntu host:

```bash
sudo apt install tesseract-ocr
```

Use an administrator-approved installation process on other systems. Confirm `tesseract --version` works in the environment running Django. Required language packs and explicit multi-language OCR configuration are separate work; the current image call uses Tesseract's default configuration.

### Environment settings

| Variable | Prototype default | Guidance |
|---|---|---|
| DEMO_MODE | `1` | Enables public demo-reviewer access. Use `0` before any restricted-data deployment. |
| DJANGO_DEBUG | `1` | Development errors. Use `0` outside a controlled development environment. |
| DJANGO_SECRET_KEY | Development fallback | Replace with a strong random secret; keep it outside source control. |
| DJANGO_ALLOWED_HOSTS | `*` | Preview convenience. Set explicit comma-separated hosts for deployment. |
| OLLAMA_URL | `http://127.0.0.1:11434` | Trusted inference service, reached from Django. |
| OLLAMA_MODEL | `qwen2.5:7b` | Must match an installed model tag. |

`.env.example` is a reference file only. The application does **not** automatically load `.env`; export variables in the shell or configure the process environment. Restart the server after changes.

The configured SQLite file is `db.sqlite3`; uploaded originals are under `private_documents/`. Media files are not published through a public media route. CSRF trust is configured for the preview environment; custom HTTPS deployments need appropriate trusted-origin/security configuration.

### Checks

```bash
python manage.py check
python manage.py test
```

The supplied test suite contains 12 tests for key workflows and access controls. Passing tests does not certify regulatory compliance, production security or model accuracy.

## 17. Account administration and data ownership

### Create an institution user

1. Sign in to `/admin/` as a superuser.
2. Open **Users** and add a username/password.
3. Leave **Staff status** and **Superuser status** unchecked.
4. Ensure **Active** is enabled.
5. Save and distribute credentials securely.
6. Have the user create applications, or assign existing applications to that user as Owner.

### Create a reviewer

1. Create a regular active user.
2. Enable **Staff status**.
3. Leave **Superuser status** disabled unless full administration is genuinely needed.
4. Save.

Staff status alone grants broad reviewer access in the main app. It does not automatically grant all Django admin model permissions.

### Transfer application ownership

1. Open **Applications** in administration.
2. Select the application.
3. Change **Owner** to the intended institution account.
4. Save.
5. Verify visibility while signed in as the intended user.
6. Document the transfer through your approved change process; no dedicated ownership-transfer workflow exists in the main UI.

### Passwords and deactivation

Administrators can reset passwords through Django's user-management forms. To suspend an account, disable **Active** rather than deleting the user. User deletion sets application owners to null; staff can still see those records, but no institution owner will have access until reassigned.

There is no multi-user institution membership model, self-service password reset, MFA or SSO in this prototype.

## 18. Backup, restore and routine operations

### Backup scope

Back up the following together:

- `db.sqlite3` — application data, users, rules, findings, audit records and run history.
- `private_documents/` — uploaded originals, if present.
- Source code and migrations.
- Securely stored deployment configuration/secrets, managed separately from downloadable source.

The source ZIP is not a data backup.

### Simple offline backup procedure

1. Schedule a maintenance window and stop the Django server with Ctrl+C, or stop its managed process.
2. Ensure no other application process is writing to SQLite.
3. Copy the database and private-document directory into restricted, preferably encrypted backup storage.
4. Preserve matching timestamps/backup identifiers for the database and files.
5. Restart the server.
6. Verify sign-in, application visibility and an original-file download.

For live backups, use an administrator-reviewed SQLite backup method rather than copying a database during active writes. Protect any SQLite journal/WAL state appropriately if the deployment enables it.

### Restore

1. Stop the application and preserve the current state before overwriting it.
2. Restore the matching database and private-document directory.
3. Restore compatible source/configuration and file permissions.
4. Run `python manage.py check`; review schema compatibility before any migration.
5. Start the server in a restricted environment.
6. Verify users, application counts, findings, activity history and attached-file access.
7. Reopen access only after validation.

Do not delete the database to fix routine login or model issues. There is no automated restore, retention cleanup, soft-delete or document-deletion workflow.

### Routine operator checklist

- Check disk space and backup success.
- Inspect pending findings and source requests.
- Confirm Ollama availability and installed model when AI is required.
- Verify Tesseract availability when testing images.
- Review user access and application ownership.
- Review rule applicability, effective dates and source references.
- Test recovery periodically and review logs for unexpected errors.

## 19. Demonstration and evaluation walkthrough

Use synthetic files and keep a record of expected outcomes.

| Step | Action | Expected behavior |
|---|---|---|
| 1 | Enter the demo workspace | Staff reviewer dashboard opens |
| 2 | Create a new synthetic EoA application | Reference assigned; Pending validation |
| 3 | Run validation without documents | Missing-document findings for applicable enabled demo rules |
| 4 | Upload a readable PDF containing the exact synthetic institution ID | Text and SHA-256 available; no source authenticity is claimed |
| 5 | Upload a certificate with yesterday's declared expiry | Next run creates an expired-document concern |
| 6 | Upload the same file twice | Next run can flag identical SHA-256 fingerprints |
| 7 | Upload building evidence | Next run creates human infrastructure-review routing |
| 8 | Select Verify source | Pending/manual-confirmation message; no live authority response |
| 9 | Run with Ollama stopped | Deterministic checks complete; inference recorded Unavailable |
| 10 | Run with installed Ollama model available | Model response processed; observations depend on model output and quote checks |
| 11 | Resolve a finding with a meaningful rationale | Resolved state and review event recorded |
| 12 | Rerun and inspect history | Existing resolutions retained; current status recomputed |
| 13 | Export CSV | Scoped register downloaded; filters not applied |
| 14 | Test a non-staff account | Only owned applications accessible; reviewer actions denied |

**Do not promise a particular AI finding.** Model outputs vary, and not all inconsistencies are detected. Evaluate extraction accuracy, discrepancy precision/recall, false positives, run latency and reviewer effort using independently labeled test records. There is no benchmark dashboard or measured accuracy guarantee in this build.

## 20. Troubleshooting

| Symptom | Likely cause / action |
|---|---|
| Demo button missing | `DEMO_MODE=0`, or a different deployment. Use assigned credentials; do not re-enable demo on real data. |
| Demo entry fails | Demo user may not exist. In a synthetic development environment, run `python manage.py seed_demo`. |
| Cannot sign in as demo.reviewer | It intentionally has no usable password. Use the demo button when permitted. |
| Regular login fails | Verify credentials and account Active status; ask the administrator to reset the password. |
| 403 / permission denied | Role does not permit the action, or CSRF/session is invalid. Sign in again and use the actual form. Staff-only actions cannot be used by institution users. |
| 404 opening an application | Incorrect reference/URL or the application is owned by another user. Ask the administrator to check ownership without bypassing access controls. |
| Institution user sees no applications | No records are assigned to that owner. Institution ID/email matching alone does not grant access. |
| Upload rejected | Check actual file content, supported type and 15 MB limit. A renamed extension is insufficient. |
| Image extraction empty | Tesseract/pytesseract unavailable, unreadable image or OCR failure. Confirm installation and inspect the original. |
| Scanned PDF has no text | Integrated scanned-PDF OCR is not implemented. Provide an authorized readable image/text PDF or conduct manual review. |
| Identifier warning despite a correct document | OCR or formatting differs from the exact ID string. Review original evidence and explain the result in a rationale. |
| Seeded document will not download | Seed records contain metadata and synthetic text only; upload an actual test file. |
| Ollama offline | Check service state, OLLAMA_URL reachability from Django and network policy. Restart Django after environment changes. |
| Connected badge, but inference unavailable | Configured model missing, memory limits, long processing, timeout or unusable JSON. Check `ollama list`, server logs and the selected model tag. |
| AI run slow | Model loading/inference or extraction is synchronous. Wait for completion; do not submit repeated runs. Use appropriate hardware/model sizing. |
| Findings remain after upload | Reruns do not auto-resolve old findings. A reviewer must inspect and resolve each concern. |
| Status still Needs attention after resolution | Rerun validation; any unresolved finding, including Info, keeps Needs attention. |
| Pending verification changed after validation | Current pipeline resets non-expired/non-Verified documents to Manual review required; consult the source-request audit event. |
| Rule did not run | Check Enabled, exact category/All, current effective dates and whether a document of that type already exists. |
| CSV ignores filters | Current export intentionally includes all authorized applications, not only filtered results. |
| Email/alert not received | Only in-app findings exist; there is no email/SMS delivery service. |
| SQLite database locked | Concurrent writes or another process may hold the database. Reduce concurrent prototype activity and ask the administrator to investigate; do not delete files blindly. |
| `no such table` | Run migrations in the correct application directory/environment. |
| Environment file changes have no effect | `.env` is not auto-loaded; export values and restart the process. |
| Port already in use | Stop the previous server or run on an approved different port, such as `python manage.py runserver 0.0.0.0:8001`. |

## 21. Security, privacy and safe operating procedures

### All users

- Use synthetic/anonymized evaluation data unless live-data use is explicitly authorized.
- Upload only necessary evidence and avoid unnecessary personal details.
- Never share credentials, exports or original documents publicly.
- Treat OCR/model outputs as fallible; inspect evidence before recording a decision.
- Do not characterize duplicate files or anomalies as proven forgery.
- Sign out on shared devices and protect downloaded copies.
- Use only authorized channels for issuing-authority confirmation.

### Administrators

- Disable demo access before storing any restricted records. Demo entry grants a shared staff account broad visibility.
- Restrict staff status, superuser access, filesystem access and database copies.
- Use a strong secret, HTTPS, explicit host/origin settings and approved session security.
- Add rate limiting, malware scanning, sandboxed parsing, request/resource limits and an appropriate production server before deployment.
- Protect the Ollama host; an operator-selected remote endpoint receives institution IDs, categories and extracted text snippets.
- Define lawful purpose, notices, retention/deletion, incident handling and access reviews with responsible authorities.
- Encrypt approved data stores/backups and manage keys separately.
- Remember that private download routes and CSRF do not constitute a complete security program.

The prototype does not automatically encrypt SQLite/files at rest, enforce an approved retention schedule, provide immutable logs or establish compliance with all applicable laws.

## 22. Current limitations and production-readiness checklist

### Implemented versus not implemented

| Area | Implemented now | Not implemented / requires extension |
|---|---|---|
| Application intake | Basic institution/category record | Full AICTE form schema, portal synchronization and institutional history |
| Documents | Private uploads, PDF text, optional image OCR | Semantic classification, robust multi-language/scanned-PDF pipeline and confidence review |
| Rules | Required document type by category/date | Certified handbook rule pack and complex numeric compliance logic |
| Consistency | Exact identifier and duplicate bytes | Authorized historical/faculty/intake/TER/accreditation reconciliation |
| AI | Bounded Ollama advisory text review | Reliable autonomous regulatory reasoning or full-document coverage guarantees |
| Authentication | Source-request record and pending state | Authorized source API, signature/QR verification, complete response capture |
| Forensics | Duplicate fingerprint signal | Proven forgery, manipulation detector or forensic confidence calibration |
| Infrastructure | Human-review routing | Automated measurements, facility recognition or remote proof of physical compliance |
| Alerts | In-app unresolved findings | Email/SMS, SLAs, assigned tasks or scheduled escalation |
| Audit | Application events and model-run records | Immutable storage, complete access telemetry and regulatory evidence snapshots |
| Reporting | Scoped application CSV | Detailed case PDF, filtered export, source-evidence bundle and analytics |
| Access | Staff/non-staff with individual ownership | SSO/MFA, institutional teams, regional reviewers and fine-grained assignments |
| Operations | Development server, SQLite | Production hosting design, queue, scale testing and certified recovery controls |

### Before any real deployment

1. Obtain competent-authority approval for workflow scope and data access.
2. Replace illustrative rules with reviewed, versioned official requirements and applicability logic.
3. Implement only authorized portal/source integrations and explicit unavailable/mismatch outcomes.
4. Establish legal/privacy requirements, retention, security ownership and human escalation.
5. Remove public demo access and configure production identity, HTTPS and secrets.
6. Add secure parsing, malware controls and bounded asynchronous job execution.
7. Implement robust evidence reconciliation, reopening/supersession, rule snapshots and review accountability.
8. Deploy append-only audit storage and validated backups/restore.
9. Conduct independent security, accessibility, performance and AI accuracy evaluation.
10. Keep adverse action, inspection and final approval with competent human authorities.

The current Django development server must not be treated as a production hosting solution.

## 23. Glossary and support checklist

| Term | Meaning |
|---|---|
| EoA | Extension of Approval |
| NOC | No Objection Certificate / permission evidence |
| OCR | Optical character recognition: converting image text into machine-readable text |
| Ollama | Local/self-hosted model runtime used for optional advisory inference |
| Deterministic check | A programmed rule/check rather than a model-generated judgment |
| SHA-256 | A file fingerprint for matching identical byte content; not proof of authenticity |
| Finding | A recorded preliminary observation with explanation and evidence |
| Rationale | A reviewer's documented reason for resolving a finding |
| Source verification | Confirmation through an original issuing authority or officially authorized mechanism; not performed automatically here |
| SQLite | The file-based relational database used by this prototype |
| Owner | The individual user account whose non-staff access includes that application |
| Staff | Django user flag that grants reviewer capabilities in this build |

### Information to collect when requesting support

- Screen/menu and action that failed.
- Application reference and document name, without unnecessary sensitive content.
- Time of the problem and user role.
- Exact displayed message or a redacted screenshot.
- Whether Ollama/Tesseract were available.
- Model name and relevant inference-run status.
- Whether the issue repeats with an authorized synthetic test record.
- Relevant redacted server logs for the administrator.

Never include passwords, secret keys, unrestricted database copies or confidential originals in an ordinary support message.

---

**Final operating principle:** AEGIS helps organize evidence and direct attention. A finding is not a verdict, a resolved item is not an authenticated document, and Ready for review is not regulatory approval.
