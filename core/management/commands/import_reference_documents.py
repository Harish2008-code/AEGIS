"""Explicit private import; never execute implicitly during migrations or demo seed."""
from pathlib import Path
import hashlib
from django.conf import settings
from django.core.management.base import BaseCommand,CommandError
from django.contrib.auth.models import User
from django.core.files import File
from core.models import Application,Document,AuditEvent
from core.extraction import process_document
FILES=[('Affidavit-1.pdf','affidavit_1'),('Affidavit-2.pdf','affidavit_2'),('Undertaking.pdf','undertaking'),('NBA.jpg','nba'),('NAC.jpg','naac'),('Affiliation3.pdf','affiliation'),('TER-Payment-Receipt.pdf','ter_payment'),('EOA Issued From AICTE – Takshshila.pdf','eoa')]
class Command(BaseCommand):
    help='Import the supplied reference set into isolated review cases. Requires DEMO_MODE=0 and explicit authorization.'
    def add_arguments(self,p):
        p.add_argument('--directory',required=True);p.add_argument('--owner',required=True);p.add_argument('--confirm-authorized',action='store_true')
    def handle(self,*args,**opts):
        if settings.DEMO_MODE:raise CommandError('Disable public demo entry with DEMO_MODE=0 and restart all web processes before importing real/reference records.')
        if not opts['confirm_authorized']:raise CommandError('Confirm authorization with --confirm-authorized. This does not establish authenticity.')
        try:user=User.objects.get(username=opts['owner'])
        except User.DoesNotExist:raise CommandError('Owner must be an existing institution user.')
        if user.is_staff or not user.is_active:raise CommandError('Use an active, non-staff owner dedicated to authorized reference review.')
        directory=Path(opts['directory'])
        missing=[name for name,_ in FILES if not (directory/name).is_file()]
        if missing:raise CommandError('Missing files: '+', '.join(missing))
        for name,kind in FILES:
            path=directory/name;digest=hashlib.sha256(path.read_bytes()).hexdigest();ref='REF-'+digest[:12].upper()
            app,created=Application.objects.get_or_create(reference=ref,defaults={'institution':'UNASSIGNED REFERENCE — '+name[:150],'institution_id':'UNCONFIRMED','state':'Unconfirmed','owner':user,'category':'Reference document review'})
            if not created:
                self.stdout.write(f'Skipped existing {ref}');continue
            with path.open('rb') as handle:
                doc=Document.objects.create(application=app,name=name,kind=kind,file=File(handle,name=name))
            process_document(doc,user.username)
            from core.archives import rebuild_institution_archive
            rebuild_institution_archive(app)
            AuditEvent.objects.create(application=app,actor=user.username,action='Authorized reference imported',detail='Separate unassigned review case; institution ownership and authenticity must be confirmed. '+name)
            self.stdout.write(f'{ref}: {name} → {kind}; {doc.extraction_status}')
