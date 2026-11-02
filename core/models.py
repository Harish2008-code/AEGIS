from django.db import models
from django.contrib.auth.models import User
class Application(models.Model):
    reference=models.CharField(max_length=40,unique=True)
    institution=models.CharField(max_length=220)
    institution_id=models.CharField(max_length=60)
    category=models.CharField(max_length=80,default='Extension of Approval')
    state=models.CharField(max_length=80)
    year=models.CharField(max_length=20,default='2026–27')
    status=models.CharField(max_length=30,default='Pending validation')
    contact_email=models.EmailField(blank=True)
    owner=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    submitted=models.DateTimeField(auto_now_add=True)
    validated_at=models.DateTimeField(null=True,blank=True)
    agent_summary=models.TextField(blank=True)
    class Meta: ordering=['-submitted']
    @property
    def open_findings(self): return self.findings.filter(resolved=False).count()
class Document(models.Model):
    from .schemas import DOCUMENT_TYPES
    TYPES=DOCUMENT_TYPES
    application=models.ForeignKey(Application,on_delete=models.CASCADE,related_name='documents')
    name=models.CharField(max_length=220)
    kind=models.CharField(max_length=40,choices=TYPES)
    file=models.FileField(upload_to='documents/%Y/%m/',blank=True)
    sha256=models.CharField(max_length=64,blank=True,db_index=True)
    extracted_text=models.TextField(blank=True)
    reference_number=models.CharField(max_length=100,blank=True)
    expires_on=models.DateField(null=True,blank=True)
    status=models.CharField(max_length=40,default='Manual review required')
    source=models.CharField(max_length=250,blank=True)
    verified_at=models.DateTimeField(null=True,blank=True)
    uploaded=models.DateTimeField(auto_now_add=True)
    schema_version=models.CharField(max_length=20,default='2.3')
    extraction_status=models.CharField(max_length=40,default='Not extracted')
    extraction_log=models.TextField(blank=True)
    extracted_at=models.DateTimeField(null=True,blank=True)
    structured_agent_status=models.CharField(max_length=200,blank=True)
    pipeline_state=models.JSONField(default=dict,blank=True)
    @property
    def schema_definition(self):
        from .schemas import SCHEMAS
        return SCHEMAS[self.kind]

class Rule(models.Model):
    code=models.CharField(max_length=50,unique=True)
    title=models.CharField(max_length=200)
    category=models.CharField(max_length=80,default='All')
    document_kind=models.CharField(max_length=40,choices=Document.TYPES)
    severity=models.CharField(max_length=20,default='Warning')
    source_reference=models.CharField(max_length=300)
    version=models.CharField(max_length=30,default='Prototype v1')
    enabled=models.BooleanField(default=True)
    effective_from=models.DateField(null=True,blank=True)
    effective_to=models.DateField(null=True,blank=True)
class Finding(models.Model):
    application=models.ForeignKey(Application,on_delete=models.CASCADE,related_name='findings')
    document=models.ForeignKey(Document,on_delete=models.SET_NULL,null=True,blank=True)
    title=models.CharField(max_length=250)
    detail=models.TextField()
    severity=models.CharField(max_length=20,default='Warning')
    agent=models.CharField(max_length=60,default='Validation agent')
    evidence=models.TextField()
    rule_code=models.CharField(max_length=50,blank=True)
    resolved=models.BooleanField(default=False)
    resolution=models.TextField(blank=True)
    created=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['resolved','-created']
class AuditEvent(models.Model):
    application=models.ForeignKey(Application,on_delete=models.SET_NULL,null=True,blank=True,related_name='events')
    actor=models.CharField(max_length=150)
    action=models.CharField(max_length=250)
    detail=models.TextField(blank=True)
    created=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created']
class AgentRun(models.Model):
    application=models.ForeignKey(Application,on_delete=models.CASCADE,related_name='runs')
    model=models.CharField(max_length=100)
    status=models.CharField(max_length=40)
    detail=models.TextField()
    created=models.DateTimeField(auto_now_add=True)

class DocumentPage(models.Model):
    document=models.ForeignKey(Document,on_delete=models.CASCADE,related_name='pages')
    number=models.PositiveIntegerField()
    text=models.TextField(blank=True)
    method=models.CharField(max_length=40)
    image=models.FileField(upload_to='page_images/',blank=True)
    confidence=models.FloatField(null=True,blank=True)
    class Meta:
        ordering=['number']
        constraints=[models.UniqueConstraint(fields=['document','number'],name='unique_document_page')]

class ExtractedField(models.Model):
    document=models.ForeignKey(Document,on_delete=models.CASCADE,related_name='fields')
    key=models.CharField(max_length=100)
    value=models.JSONField(null=True,blank=True)
    page=models.PositiveIntegerField(null=True,blank=True)
    evidence=models.TextField(blank=True)
    method=models.CharField(max_length=40,default='Manual')
    review_status=models.CharField(max_length=30,default='Needs review')
    reviewed_by=models.CharField(max_length=150,blank=True)
    reviewed_at=models.DateTimeField(null=True,blank=True)
    review_note=models.TextField(blank=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['document','key'],name='unique_document_field')]

class VerificationRecord(models.Model):
    OUTCOMES=[('Verification pending','Verification pending'),('Verified','Verified — manual authority confirmation'),('Mismatch detected','Mismatch detected'),('Expired','Expired'),('Source unavailable','Source unavailable'),('Manual review required','Manual review required')]
    document=models.ForeignKey(Document,on_delete=models.CASCADE,related_name='verifications')
    status=models.CharField(max_length=40,choices=OUTCOMES)
    source_name=models.CharField(max_length=200)
    source_reference=models.CharField(max_length=500)
    checked_at=models.DateTimeField()
    result_notes=models.TextField()
    actor=models.CharField(max_length=150)
    method=models.CharField(max_length=80,default='Manual authority confirmation')
    created=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created']
