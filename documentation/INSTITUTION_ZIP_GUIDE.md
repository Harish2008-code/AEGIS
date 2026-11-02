# AEGIS v2.1 — One institution, one ZIP

## Changes

- Removed the **Reference number** input from document upload. Upload requests no longer accept that field into the document record.
- Reference numbers may still be extracted from the original and reviewed in structured schemas. Existing stored reference data is not deleted.
- Each successful document upload rebuilds the institution's private ZIP, combining documents across its application records.
- The application workspace has **Download institution ZIP**. Download rebuilds the ZIP so it also includes older stored originals.
- Original files remain privately stored for OCR and individual download. ZIPs are maintained alongside them, not used as the sole OCR storage format.

## Grouping rule

An institution/university is identified by its **institution ID**, ignoring case and leading/trailing spaces. Applications with the same ID are combined into one canonical ZIP; different IDs remain separate even if their names are identical. Use consistent IDs and confirm ownership. This is not parent-university/affiliated-college grouping: such a relationship would require an explicit reviewed hierarchy.

Unassigned reference cases with blank/UNCONFIRMED/UNKNOWN/N/A IDs remain isolated by application, preventing unrelated documents from being merged. Correct their IDs only after authorized ownership review.

## ZIP structure

```text
manifest.json
README.txt
applications/
  <application-id>-<reference>/
    <document-id>/
      original-filename.pdf
```

`manifest.json` records institution metadata, application references, document IDs/types/names, upload timestamps, SHA-256 values when available, and archive paths. Synthetic metadata-only records are listed as not included because no original exists. Duplicate filenames remain distinct through their document-ID folders.

The ZIP contains submitted originals, not an authenticated evidence bundle. It does not include extracted text, reviewer rationales or a full audit export. Inclusion does not establish authenticity or approval.

## Private storage and access

ZIPs are in `private_documents/institution_archives/` under the default configuration (or `<MEDIA_ROOT>/institution_archives/`). A stable hashed institution key is used for the stored filename. Archive writes use a file lock, temporary file and atomic replacement rather than accumulating versions.

Staff reviewers can download the complete institution archive. A non-staff owner can download it only when **all applications in the grouped institution belong to that user**. Shared institution IDs do not grant access to another account's records. Unauthorized users get no ZIP. No public archive/media URL is configured. Downloads are logged and marked private/no-store.

## Existing uploads / upgrade

Back up both the database and media storage, install updated requirements, and restart Django:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py rebuild_institution_archives
python manage.py runserver 0.0.0.0:8000
```

No new schema migration is required for this change. The rebuild command creates/replaces one ZIP per stored institution grouping and reports failures. A ZIP download also rebuilds on demand. If an admin changes an institution ID, run the rebuild command and review stale archive cleanup separately; old hashed ZIPs are not automatically deleted after ID changes. Direct admin deletions/reassignments also require a rebuild before relying on saved archives.

## Failure handling and limitations

If archiving fails after an upload, the original remains saved; the screen warns the user and logs the server error. Retry the download or ask an administrator to rebuild. Missing stored originals fail the rebuild instead of silently omitting attached records. The previous complete ZIP is preserved on rebuild errors.

Back up archives with the original files. ZIP creation is synchronous and unencrypted; use approved encryption/access controls at the filesystem/backup layer. Large multi-application collections need a background queue, quotas, storage monitoring and a production retention policy. Do not expose MEDIA_ROOT through a public web server.
