from django.conf import settings
from .models import Finding

def shell(request):
    findings=Finding.objects.filter(resolved=False)
    if not request.user.is_authenticated:
        count=0
    elif request.user.is_staff:
        count=findings.count()
    else:
        count=findings.filter(application__owner=request.user).count()
    return {'demo_mode':settings.DEMO_MODE,'alert_count':count,'ollama_model':settings.OLLAMA_MODEL}
