import csv,json,uuid
from datetime import date
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Case, When, Value, IntegerField
from django.http import HttpResponse,FileResponse,JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_POST
from .models import Application,Document,Finding,Rule,AuditEvent,AgentRun
from .agents import run_validation,extract_document

def staff(user):
    if not user.is_staff: raise PermissionDenied

def apps_for(user):
    return Application.objects.all() if user.is_staff else Application.objects.filter(owner=user)

def signin(request):
    if request.method=='POST':
        user=authenticate(request,username=request.POST.get('username',''),password=request.POST.get('password',''))
        if user: login(request,user); return redirect('/')
        messages.error(request,'The username or password is incorrect.')
    return render(request,'core/login.html',{'page':'Sign in'})

@require_POST
def demo_login(request):
    if not settings.DEMO_MODE: raise PermissionDenied
    from django.contrib.auth.models import User
    user=User.objects.get(username='demo.reviewer');login(request,user,backend='django.contrib.auth.backends.ModelBackend')
    return redirect('/')

@require_POST
def signout(request):
    logout(request);return redirect('/login/')

@login_required
def dashboard(request):
    apps=apps_for(request.user)
    findings=Finding.objects.filter(application__in=apps,resolved=False).annotate(priority=Case(When(severity='Critical',then=Value(0)),When(severity='Warning',then=Value(1)),default=Value(2),output_field=IntegerField())).order_by('priority','-created')
    return render(request,'core/dashboard.html',{'page':'Overview','nav':'overview','apps':apps[:5],'total':apps.count(),'attention':apps.filter(status='Needs attention').count(),'ready':apps.filter(status='Ready for review').count(),'docs':Document.objects.filter(application__in=apps).count(),'findings':findings.select_related('application')[:3],'events':AuditEvent.objects.filter(application__in=apps)[:4],'critical':findings.filter(severity='Critical').count()})

@login_required
def applications(request):
    apps=apps_for(request.user);q=request.GET.get('q','');status=request.GET.get('status','')
    if q: apps=apps.filter(Q(institution__icontains=q)|Q(reference__icontains=q)|Q(institution_id__icontains=q))
    if status: apps=apps.filter(status=status)
    return render(request,'core/applications.html',{'page':'Applications','nav':'applications','apps':apps,'q':q,'status':status})

@login_required
def create_application(request):
    if request.method=='POST':
        institution=request.POST.get('institution','').strip(); iid=request.POST.get('institution_id','').strip()
        if not institution or not iid: messages.error(request,'Institution name and ID are required.')
        else:
            app=Application.objects.create(reference='APP-26-'+uuid.uuid4().hex[:6].upper(),institution=institution[:220],institution_id=iid[:60],state=request.POST.get('state','')[:80],category=request.POST.get('category','Extension of Approval')[:80],contact_email=request.POST.get('contact_email','')[:254],owner=request.user)
            AuditEvent.objects.create(application=app,actor=request.user.username,action='Application created',detail='Submitted through prototype intake.')
            messages.success(request,'Application created. Upload supporting documents to begin validation.')
            return redirect('detail',app.pk)
    return render(request,'core/create.html',{'page':'New application','nav':'applications'})

@login_required
def detail(request,pk):
    app=get_object_or_404(apps_for(request.user),pk=pk)
    from .schemas import SCHEMAS
    expiry_kinds=[kind for kind,schema in SCHEMAS.items() if 'expiry_date' in schema['properties']]
    return render(request,'core/detail.html',{'expiry_kinds':expiry_kinds,'page':'Application workspace','nav':'applications','app':app,'types':Document.TYPES})

@login_required
@require_POST
def validate(request,pk):
    staff(request.user);app=get_object_or_404(apps_for(request.user),pk=pk)
    run_validation(app,request.user.username);messages.success(request,'Validation completed. Findings are advisory and require authorized review.');return redirect('detail',pk)

@login_required
@require_POST
def upload(request,pk):
    app=get_object_or_404(apps_for(request.user),pk=pk);f=request.FILES.get('file')
    kind=request.POST.get('kind','')
    if not f or f.size>15*1024*1024 or kind not in dict(Document.TYPES):
        messages.error(request,'Choose a valid document type and a PDF, PNG or JPEG up to 15 MB.');return redirect('detail',pk)
    head=f.read(8);f.seek(0)
    if not (head.startswith(b'%PDF') or head.startswith(b'\x89PNG\r\n\x1a\n') or head.startswith(b'\xff\xd8\xff')):
        messages.error(request,'File content must be PDF, PNG or JPEG.');return redirect('detail',pk)
    try: expires=date.fromisoformat(request.POST['expires_on']) if request.POST.get('expires_on') else None
    except ValueError: messages.error(request,'Invalid expiry date.');return redirect('detail',pk)
    from .schemas import SCHEMAS
    if 'expiry_date' not in SCHEMAS[kind]['properties']:expires=None
    doc=Document.objects.create(application=app,name=f.name[:220],file=f,kind=kind,expires_on=expires)
    from .extraction import process_document
    process_document(doc,request.user.username)
    AuditEvent.objects.create(application=app,actor=request.user.username,action='Document uploaded',detail=doc.name+' · SHA-256 '+doc.sha256)
    from .archives import rebuild_institution_archive
    try:
        rebuild_institution_archive(app)
        AuditEvent.objects.create(application=app,actor=request.user.username,action='Institution ZIP updated',detail='Original upload included in the private archive grouped by institution ID.')
        messages.success(request,'Document saved and institution ZIP updated. PDF → image → OCR → Ollama pipeline finished; review the stage status and extracted fields.')
    except Exception:
        import logging
        logging.getLogger(__name__).exception('Institution ZIP rebuild failed for application %s',app.pk)
        messages.warning(request,'Original document was saved, but the institution ZIP could not be updated. Ask an administrator to rebuild it; retrying the ZIP download also triggers a rebuild.')
    return redirect('document_workspace',doc.pk)

@login_required
def download(request,pk):
    doc=get_object_or_404(Document,pk=pk,application__in=apps_for(request.user))
    if not doc.file: messages.info(request,'This synthetic record has no original file attached.');return redirect('detail',doc.application_id)
    AuditEvent.objects.create(application=doc.application,actor=request.user.username,action='Document accessed',detail=doc.name)
    return FileResponse(doc.file.open('rb'),as_attachment=True,filename=doc.name)

@login_required
@require_POST
def resolve(request,pk):
    staff(request.user);finding=get_object_or_404(Finding,pk=pk)
    note=request.POST.get('note','').strip()
    if len(note)<10: messages.error(request,'A review rationale of at least 10 characters is required.')
    else:
        finding.resolved=True;finding.resolution=note;finding.save()
        AuditEvent.objects.create(application=finding.application,actor=request.user.username,action='Finding resolved by reviewer',detail=f'{finding.title}: {note}')
        messages.success(request,'Review recorded. This does not constitute regulatory approval.')
    return redirect('detail',finding.application_id)

@login_required
@require_POST
def verify(request,pk):
    staff(request.user);doc=get_object_or_404(Document,pk=pk)
    # No fabricated authority connection; routing recorded explicitly.
    if doc.status!='Expired': doc.status='Verification pending'
    doc.save();AuditEvent.objects.create(application=doc.application,actor=request.user.username,action='Source verification requested',detail=doc.name+' · No authorized source connector configured; routed for manual confirmation.')
    messages.info(request,'Manual confirmation requested. No authorized issuing-authority connector is configured; the document has NOT been verified.')
    return redirect('detail',doc.application_id)

@login_required
def documents(request):
    docs=Document.objects.filter(application__in=apps_for(request.user)).select_related('application')
    q=request.GET.get('q','')
    if q: docs=docs.filter(Q(name__icontains=q)|Q(application__institution__icontains=q))
    return render(request,'core/documents.html',{'page':'Document library','nav':'documents','documents':docs,'q':q})

@login_required
def alerts(request):
    return render(request,'core/alerts.html',{'page':'Review inbox','nav':'alerts','findings':Finding.objects.filter(application__in=apps_for(request.user),resolved=False).select_related('application','document')})

@login_required
def rules(request):
    staff(request.user)
    return render(request,'core/rules.html',{'page':'Compliance rules','nav':'rules','rules':Rule.objects.all()})

@login_required
@require_POST
def toggle_rule(request,pk):
    staff(request.user);rule=get_object_or_404(Rule,pk=pk);rule.enabled=not rule.enabled;rule.save()
    AuditEvent.objects.create(actor=request.user.username,action='Rule configuration changed',detail=f'{rule.code}: enabled={rule.enabled}; {rule.version}')
    return redirect('rules')

@login_required
def audit(request):
    events=AuditEvent.objects.all() if request.user.is_staff else AuditEvent.objects.filter(application__in=apps_for(request.user))
    return render(request,'core/audit.html',{'page':'Audit trail','nav':'audit','events':events[:200]})

@login_required
def agents(request):
    staff(request.user);connected=False;models=[]
    try:
        r=requests.get(settings.OLLAMA_URL+'/api/tags',timeout=2);r.raise_for_status();models=[m['name'] for m in r.json().get('models',[])];connected=True
    except (requests.RequestException,ValueError,KeyError): pass
    return render(request,'core/agents.html',{'page':'Agent workspace','nav':'agents','connected':connected,'models':models,'runs':AgentRun.objects.select_related('application')[:15]})

@login_required
def export(request):
    response=HttpResponse(content_type='text/csv');response['Content-Disposition']='attachment; filename="validation-report.csv"'
    writer=csv.writer(response);writer.writerow(['Application','Institution','Status','Open findings','Validated at','Advisory notice'])
    for a in apps_for(request.user):
        safe=lambda s: "'"+str(s) if str(s).startswith(('=','+','-','@')) else str(s)
        writer.writerow([safe(a.reference),safe(a.institution),a.status,a.open_findings,a.validated_at,'Decision support only; not regulatory approval'])
    AuditEvent.objects.create(actor=request.user.username,action='Validation report exported')
    return response

@login_required
def document_workspace(request,pk):
    from .schemas import SCHEMAS
    doc=get_object_or_404(Document,pk=pk,application__in=apps_for(request.user))
    schema=SCHEMAS[doc.kind];existing={f.key:f for f in doc.fields.all()};rows=[]
    for key,spec in schema['properties'].items():
        f=existing.get(key)
        rows.append({'key':key,'label':spec['title'],'type':spec['type'],'spec':json.dumps(spec,indent=2),'field':f,'value':json.dumps(f.value,ensure_ascii=False,indent=2) if f else '', 'complex':spec['type'] in ['array','object']})
    derived=[]
    if doc.kind=='faculty_list':
        confirmed={f.key:f.value for f in existing.values() if f.review_status=='Confirmed'}
        rows_count=len(confirmed.get('faculty',[]))
        if rows_count:derived.append(f'{rows_count} confirmed faculty table rows (not a verified eligible-faculty count).')
        count=confirmed.get('declared_faculty_count');students=confirmed.get('declared_student_count')
        if isinstance(count,int) and count>0 and isinstance(students,int) and students>=0:
            derived.append(f'Derived from confirmed declared counts: 1 faculty : {students/count:.2f} students. No normative threshold or faculty eligibility test has been applied.')
    return render(request,'core/document_workspace.html',{'core_rows':rows,'derived':derived,'page':'Structured evidence review','nav':'documents','doc':doc,'rows':rows,'schema_json':json.dumps(schema,indent=2),'verification_outcomes':__import__('core.models',fromlist=['VerificationRecord']).VerificationRecord.OUTCOMES})

@login_required
@require_POST
def retry_extraction(request,pk):
    staff(request.user);doc=get_object_or_404(Document,pk=pk)
    from .extraction import process_document
    process_document(doc,request.user.username)
    AuditEvent.objects.create(application=doc.application,actor=request.user.username,action='Document re-extracted',detail=doc.name+' · '+doc.extraction_status)
    messages.info(request,'PDF → image → OCR → Ollama pipeline retried. Previously confirmed values require recheck.');return redirect('document_workspace',pk)

@login_required
@require_POST
def extract_structured(request,pk):
    staff(request.user);doc=get_object_or_404(Document,pk=pk)
    from .extraction import structured_extract,labelled_candidates,document_patterns
    # Reuse existing OCR; do not force a slow render/OCR rerun to refresh extraction.
    doc.fields.exclude(review_status__in=['Confirmed','Recheck required']).delete()
    labelled_candidates(doc);document_patterns(doc)
    structured_extract(doc,request.user.username);messages.info(request,doc.structured_agent_status);return redirect('document_workspace',pk)

@login_required
@require_POST
def save_field(request,pk):
    staff(request.user);doc=get_object_or_404(Document,pk=pk)
    from .models import ExtractedField
    from .schemas import SCHEMAS
    from .extraction import validate_value
    from django.utils import timezone
    key=request.POST.get('key','');spec=SCHEMAS[doc.kind]['properties'].get(key)
    if not spec:raise PermissionDenied
    try:
        raw=request.POST.get('value','')
        value=json.loads(raw) if spec['type']!='string' else raw.strip()
        validate_value(spec,value)
        if value=='' or value==[]:raise ValueError('Provide a nonempty value; leave unknown fields unconfirmed.')
        page=int(request.POST.get('page',''))
        if not doc.pages.filter(number=page).exists():raise ValueError('Choose an extracted page number.')
        note=request.POST.get('review_note','').strip();evidence=request.POST.get('evidence','').strip()
        if len(note)<10 or len(evidence)<6:raise ValueError('Provide a source excerpt and review rationale (at least 10 characters).')
        status=request.POST.get('review_status','Needs review')
        if status not in ['Confirmed','Needs review','Rejected']:raise ValueError('Invalid review status.')
        old=doc.fields.filter(key=key).first();before=old.value if old else None
        ExtractedField.objects.update_or_create(document=doc,key=key,defaults={'value':value,'page':page,'evidence':evidence,'review_status':status,'review_note':note,'reviewed_by':request.user.username,'reviewed_at':timezone.now(),'method':'Human-reviewed entry'})
        AuditEvent.objects.create(application=doc.application,actor=request.user.username,action='Structured field reviewed',detail=json.dumps({'document':doc.pk,'field':key,'before':before,'after':value,'status':status,'page':page,'rationale':note},ensure_ascii=False))
        messages.success(request,'Field review saved. Confirmed extraction is not source authentication.')
    except Exception as exc:
        from jsonschema.exceptions import ValidationError
        text='Value does not match the field schema (type, date format or table columns).' if isinstance(exc,ValidationError) else str(exc)
        messages.error(request,text[:300])
    return redirect('document_workspace',pk)

@login_required
@require_POST
def record_verification(request,pk):
    staff(request.user);doc=get_object_or_404(Document,pk=pk)
    from .models import VerificationRecord
    from django.utils import timezone
    from django.utils.dateparse import parse_datetime
    status=request.POST.get('status','');source=request.POST.get('source_name','').strip();reference=request.POST.get('source_reference','').strip();notes=request.POST.get('notes','').strip()
    checked=parse_datetime(request.POST.get('checked_at',''))
    if checked and timezone.is_naive(checked):checked=timezone.make_aware(checked)
    if status not in dict(VerificationRecord.OUTCOMES) or len(source)<3 or len(reference)<5 or len(notes)<20 or not checked or checked>timezone.now():
        messages.error(request,'Provide an outcome, authority/source, evidence reference, past/current checked time and at least 20 characters of result notes.');return redirect('document_workspace',pk)
    if status=='Verified' and request.POST.get('attestation')!='yes':
        messages.error(request,'Attest that you personally obtained authorized authority confirmation before marking Verified.');return redirect('document_workspace',pk)
    record=VerificationRecord.objects.create(document=doc,status=status,source_name=source[:200],source_reference=reference[:500],checked_at=checked,result_notes=notes,actor=request.user.username)
    doc.status=status;doc.source=source[:250];doc.verified_at=checked if status=='Verified' else None;doc.save()
    AuditEvent.objects.create(application=doc.application,actor=request.user.username,action='Manual source outcome recorded',detail=f'Verification record {record.pk}; document {doc.pk}; outcome {status}; source {source}; reference {reference}; notes {notes}')
    messages.success(request,'Manual authority-confirmation record saved. No external portal/API was contacted by this application.');return redirect('document_workspace',pk)

@login_required
def schema_catalog(request):
    from .schemas import CATALOG
    return render(request,'core/schemas.html',{'page':'Document schema catalogue','nav':'documents','catalog':[{'kind':k,'label':label,'schema':json.dumps(s,indent=2)} for k,label,s in CATALOG]})

@login_required
def schema_download(request,kind):
    from .schemas import SCHEMAS
    from django.http import Http404
    if kind not in SCHEMAS:raise Http404
    response=JsonResponse(SCHEMAS[kind]);response['Content-Disposition']=f'attachment; filename="{kind}-schema.json"';return response


@login_required
def institution_archive(request,pk):
    from .archives import institution_applications,rebuild_institution_archive
    from django.utils.text import slugify
    app=get_object_or_404(apps_for(request.user),pk=pk)
    grouped=institution_applications(app)
    # A shared institution ID must not grant an owner access to other users' cases.
    if not request.user.is_staff and grouped.exclude(owner=request.user).exists():
        messages.error(request,'This institution archive contains applications outside your account. Ask an authorized reviewer for access; institution ID alone does not grant permission.')
        return redirect('detail',pk)
    try:
        path=rebuild_institution_archive(app)
        handle=path.open('rb')
    except Exception:
        import logging
        logging.getLogger(__name__).exception('Institution archive download failed for application %s',app.pk)
        messages.error(request,'The complete institution ZIP could not be built. Originals remain available individually; contact the administrator.')
        return redirect('detail',pk)
    AuditEvent.objects.create(application=app,actor=request.user.username,action='Institution ZIP downloaded',detail=f'{grouped.count()} application(s); original documents grouped by institution ID.')
    filename=(slugify(app.institution)[:90] or 'institution')+'-documents.zip'
    response=FileResponse(handle,as_attachment=True,filename=filename,content_type='application/zip')
    response['Cache-Control']='private, no-store'
    return response


@login_required
def document_page_image(request,pk,number):
    from .models import DocumentPage
    from django.http import Http404
    doc=get_object_or_404(Document,pk=pk,application__in=apps_for(request.user))
    page=get_object_or_404(DocumentPage,document=doc,number=number)
    if not page.image:raise Http404('No rendered image. Retry the OCR pipeline for this document.')
    AuditEvent.objects.create(application=doc.application,actor=request.user.username,action='OCR page image accessed',detail=f'Document {doc.pk}, page {number}')
    response=FileResponse(page.image.open('rb'),content_type='image/png')
    response['Cache-Control']='private, no-store'
    return response
