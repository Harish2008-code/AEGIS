from django.core.management.base import BaseCommand
from django.contrib.auth.models import User,Group
from django.utils import timezone
from datetime import date,timedelta
from core.models import Application,Document,Finding,Rule,AuditEvent
class Command(BaseCommand):
    help='Create idempotent synthetic demonstration records; no real institutions or certificates.'
    def handle(self,*args,**kwargs):
        user,created=User.objects.get_or_create(username='demo.reviewer',defaults={'first_name':'Ananya Rao','is_staff':True})
        if created: user.set_unusable_password();user.save()
        for name in ['Reviewers','Institution users']: Group.objects.get_or_create(name=name)
        for code,title,kind,severity in [('DOC-001','Previous approval evidence required','eoa','Warning'),('DOC-002','Institution undertaking required','affidavit','Warning'),('DOC-003','Fire safety evidence required','fire','Critical'),('DOC-004','Infrastructure evidence required','building','Info')]:
            Rule.objects.get_or_create(code=code,defaults={'title':title,'document_kind':kind,'severity':severity,'source_reference':'Synthetic demonstration requirement · handbook mapping pending','version':'Demo 1.0'})
        records=[('Meridian Institute of Technology','Tamil Nadu','Extension of Approval','Needs attention'),('Northfield College of Engineering','Maharashtra','Extension of Approval','Ready for review'),('Crestview Technical Institute','Karnataka','Increase in Intake','Needs attention'),('Riverstone School of Technology','Telangana','New Programme','Pending validation'),('Westbridge College of Engineering','Kerala','Extension of Approval','Needs attention'),('Oakridge Polytechnic Institute','Gujarat','Extension of Approval','Ready for review'),('Horizon Institute of Engineering','Rajasthan','Change of Name','Pending validation'),('Silverbrook Technical College','Odisha','Extension of Approval','Needs attention')]
        for i,(name,state,category,status) in enumerate(records):
            app,created=Application.objects.get_or_create(reference=f'APP-26-{1048-i}',defaults={'institution':name,'institution_id':f'SYNTH-1000{i+1}','state':state,'category':category,'status':status,'owner':user,'validated_at':timezone.now() if status!='Pending validation' else None})
            if not created: continue
            for kind,filename in [('eoa','Previous_approval_2025.pdf'),('affidavit','Institution_undertaking.pdf'),('fire','Fire_safety_certificate.pdf')]:
                Document.objects.create(application=app,kind=kind,name=filename,reference_number=f'SYNTH-{i+1}-{kind}',expires_on=date(2026,9,30) if i==0 and kind=='fire' else date(2027,9,30),status='Expired' if i==0 and kind=='fire' else 'Manual review required',extracted_text=f'SYNTHETIC DEMONSTRATION RECORD — NOT A REAL CERTIFICATE\nInstitution: {name}\nInstitution ID: {app.institution_id}\nReference: SYNTH-{i+1}-{kind}\nDocument type: {kind}\nNo authority verification has been performed.')
            if status=='Needs attention':
                if i==0:
                    Finding.objects.create(application=app,document=app.documents.get(kind='fire'),title='Fire safety certificate expired',detail='The declared validity ended before the current application review. Request current evidence and confirm with the issuing authority.',severity='Critical',agent='Document agent',evidence='Synthetic fire safety record · Expiry: 30 September 2026. No original source verification.')
                elif i==2:
                    Finding.objects.create(application=app,title='Infrastructure evidence missing',detail='Additional infrastructure evidence is required for review of this synthetic intake-change application.',severity='Warning',agent='Checklist agent',evidence='No building or infrastructure evidence submitted. Illustrative rule DOC-004.',rule_code='DOC-004')
                else:
                    Finding.objects.create(application=app,title='Issuing-authority confirmation pending',detail='No authorized connector is configured. Route the certificate for manual source confirmation.',severity='Warning',agent='Verification workflow',evidence='Source response: not requested. No live authority integration.')
            AuditEvent.objects.create(application=app,actor='Demo initializer',action='Synthetic application loaded',detail='Fabricated institution and document metadata for prototype evaluation. No real authority verification.')
        from core.models import DocumentPage
        from core.extraction import labelled_candidates
        for doc in Document.objects.filter(file='',extracted_text__contains='SYNTHETIC'):
            if not doc.pages.exists():
                DocumentPage.objects.create(document=doc,number=1,text=doc.extracted_text,method='Synthetic seed text')
                doc.extraction_status='Synthetic text — needs review';doc.save(update_fields=['extraction_status'])
                labelled_candidates(doc)
        self.stdout.write(self.style.SUCCESS('Synthetic workspace ready. Sign in with the demo button (DEMO_MODE=1).'))
