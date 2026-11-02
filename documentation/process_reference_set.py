"""Local attachment evaluation in a separate DB, not served by the public demo."""
import os,sys,json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root));os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
from django.conf import settings
settings.DATABASES['default']['NAME']=str(root/'private_reference_review.sqlite3')
settings.MEDIA_ROOT=root/'reference_review_files';settings.DEMO_MODE=False
import django
django.setup()
from django.core.management import call_command
from django.contrib.auth.models import User
call_command('migrate',verbosity=0)
u,created=User.objects.get_or_create(username='private-reference-review',defaults={'is_staff':False})
if created:u.set_unusable_password();u.save()
call_command('import_reference_documents',directory=str(root/'uploads'),owner=u.username,confirm_authorized=True)
from core.models import Document
out=[]
for d in Document.objects.all():
 out.append({'filename':d.name,'type':d.kind,'status':d.extraction_status,'pages':d.pages.count(),'characters':len(d.extracted_text),'methods':list(d.pages.values_list('method',flat=True).distinct()),'candidate_fields':list(d.fields.values('key','value','page','evidence','review_status')),'limitations':d.extraction_log})
(root/'reference_extraction_results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False))
lines=['# Attached reference set — extraction smoke test','','Processed in a separate local SQLite database; not imported into the public demo. This tests technical extraction, not authenticity or regulatory compliance. No authority was contacted and no record was marked Verified.','','| File | Type | Pages | Text characters | Candidate fields | Result |','|---|---|---:|---:|---:|---|']
for r in out:lines.append(f"| {r['filename']} | {r['type']} | {r['pages']} | {r['characters']} | {len(r['candidate_fields'])} | {r['status']} |")
lines+=['','## Interpretation','','- Label-based extraction is intentionally conservative; few or zero candidates does not mean the document has no fields. Use Ollama extraction or human-reviewed entry for prose, complex dates and tables.','- OCR text/confidence are not authentication results. Check names, scope, programme-specific validity and original pages.','- Supplied documents concern different institutions and/or contain unfilled templates. Each file is isolated in an UNASSIGNED REFERENCE case until ownership is confirmed.','- The EoA attachment is a website printout with embedded material; classify and verify each actual letter/year rather than treating the whole printout as one official approval.','- The supplied NBA image indicates programme-specific validity up to 30 June 2026. The NAAC image shows validity up to 20 December 2028. These are visual observations only, not authorized source confirmations; conditions and subsequent extensions require review.','- Full raw extraction and candidates are retained locally in reference_extraction_results.json; they are excluded from the downloadable source bundle.']
(root/'Reference_Extraction_Report.md').write_text('\n'.join(lines))
print('Separate reference evaluation complete.')
