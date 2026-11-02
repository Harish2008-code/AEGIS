from django.contrib import admin
from .models import Application,Document,Rule,Finding,AuditEvent,AgentRun
for model in [Application,Document,Rule,Finding,AuditEvent,AgentRun]: admin.site.register(model)

from .models import DocumentPage,ExtractedField,VerificationRecord
for model in [DocumentPage,ExtractedField,VerificationRecord]: admin.site.register(model)
