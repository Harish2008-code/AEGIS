"""One canonical private archive per normalized institution ID; originals remain OCR sources."""
import hashlib,json,os,tempfile,zipfile
from pathlib import Path
from django.conf import settings
from django.db.models.functions import Lower,Trim
from django.utils import timezone
from django.utils.text import slugify
from filelock import FileLock
from .models import Application

UNASSIGNED={'','unconfirmed','unknown','n/a'}
def institution_key(app):
    value=app.institution_id.strip().casefold()
    # Unassigned/reference cases must never combine unrelated institutions.
    return 'institution:'+value if value not in UNASSIGNED else f'unassigned-application:{app.pk}'

def institution_applications(app):
    value=app.institution_id.strip().casefold()
    if value in UNASSIGNED:return Application.objects.filter(pk=app.pk)
    return Application.objects.annotate(normalized_id=Lower(Trim('institution_id'))).filter(normalized_id=value).order_by('pk')

def archive_path(app):
    key=hashlib.sha256(institution_key(app).encode()).hexdigest()
    directory=Path(settings.MEDIA_ROOT)/'institution_archives'
    directory.mkdir(parents=True,exist_ok=True)
    return directory/(key+'.zip')

def safe_filename(name):
    # Normalize both OS separator conventions. Keep filenames flat within document folder.
    name=name.replace('\\','/').split('/')[-1]
    name=''.join(c for c in name if c.isprintable() and c not in '/\\')[:180]
    return name if name not in ['', '.', '..'] else 'document.bin'

def rebuild_institution_archive(app):
    path=archive_path(app)
    with FileLock(str(path)+'.lock',timeout=60):
        # Snapshot under lock, so overlapping uploads cannot publish an older snapshot last.
        apps=list(institution_applications(app).prefetch_related('documents'))
        manifest={'format_version':1,'institution_id':app.institution_id.strip(),'institution_name':app.institution,'generated_at':timezone.now().isoformat(),'notice':'Submitted originals only. Inclusion does not establish authenticity, validity or regulatory approval.','applications':[],'documents':[]}
        handle,tmp=tempfile.mkstemp(prefix='archive-',suffix='.tmp',dir=path.parent);os.close(handle)
        try:
            with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as bundle:
                for application in apps:
                    manifest['applications'].append({'id':application.pk,'reference':application.reference,'institution_name':application.institution,'category':application.category,'academic_year':application.year})
                    folder=f'applications/{application.pk}-{slugify(application.reference) or "application"}'
                    for doc in application.documents.all():
                        record={'document_id':doc.pk,'application_id':application.pk,'name':doc.name,'type':doc.kind,'sha256':doc.sha256,'uploaded_at':doc.uploaded.isoformat(),'archive_path':None,'included':False}
                        if doc.file:
                            entry=f'{folder}/{doc.pk}/{safe_filename(doc.name)}'
                            # Missing originals fail the rebuild, preserving previous complete ZIP.
                            with doc.file.open('rb') as source, bundle.open(entry,'w',force_zip64=True) as target:
                                import shutil
                                shutil.copyfileobj(source,target,length=1024*1024)
                            record.update({'archive_path':entry,'included':True})
                        else:record['reason']='Metadata-only record; no original attached.'
                        manifest['documents'].append(record)
                bundle.writestr('manifest.json',json.dumps(manifest,indent=2,ensure_ascii=False))
                bundle.writestr('README.txt','Institution document archive\n\nEach original is under applications/<application>/<document ID>/.\nmanifest.json lists included files and metadata-only records.\nNo authentication or regulatory approval is asserted.\n')
            os.chmod(tmp,0o600)
            os.replace(tmp,path)
        except Exception:
            Path(tmp).unlink(missing_ok=True);raise
    return path
