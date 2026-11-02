from django.core.management.base import BaseCommand
from core.models import Application
from core.archives import institution_key,rebuild_institution_archive
class Command(BaseCommand):
    help='Rebuild one private ZIP per institution ID from stored originals; metadata-only records go in the manifest.'
    def handle(self,*args,**kwargs):
        seen=set();count=0
        for app in Application.objects.all():
            key=institution_key(app)
            if key in seen:continue
            seen.add(key)
            try:
                rebuild_institution_archive(app);count+=1
                self.stdout.write(f'Updated institution archive for application {app.pk}')
            except Exception as exc:self.stderr.write(f'Failed application {app.pk}: {type(exc).__name__}')
        self.stdout.write(self.style.SUCCESS(f'{count} institution ZIP(s) rebuilt.'))
