from datetime import date
from django.utils import timezone

def review_checks(app,flag):
    approved={}
    for doc in app.documents.prefetch_related('fields').all():
        from .schemas import SCHEMAS
        fields={f.key:f for f in doc.fields.all() if f.review_status=='Confirmed' and f.key in SCHEMAS[doc.kind]['properties']}
        if 'institution_name' in fields:
            f=fields['institution_name']
            if ' '.join(str(f.value).lower().split())!=' '.join(app.institution.lower().split()):
                flag('Institution name differs from application','Confirmed extraction differs from the application name. Review naming variations and document ownership.',f'Application: {app.institution}; document: {f.value}; page {f.page}.',agent='Structured consistency agent',document=doc)
        if 'expiry_date' in fields:
            f=fields['expiry_date']
            try:
                if date.fromisoformat(f.value)<timezone.localdate():
                    flag('Confirmed extracted validity has expired','A reviewer-confirmed expiry is in the past. Review the scope, conditions and any subsequent authorized extension.',f'Page {f.page}: {f.evidence}',agent='Structured validity agent',severity='Critical',document=doc)
            except (ValueError,TypeError):pass
        if doc.kind in ['nba','naac','accreditation'] and 'programmes' in fields:
            for row in fields['programmes'].value:
                try:
                    until=row.get('valid_until')
                    if until and date.fromisoformat(until)<timezone.localdate():
                        name=row.get('course_name','Unnamed programme')
                        flag('Programme validity expired: '+name[:150],'Confirmed programme-specific validity is in the past. This finding is limited to that programme; check conditions and any subsequent extension.',f'{name}; valid until {until}; document {doc.name}; page {fields["programmes"].page}.',agent='Structured validity agent',severity='Critical',document=doc)
                except (ValueError,TypeError):pass
        if doc.kind in ['eoa','intake','course_record'] and 'programmes' in fields:
            for row in fields['programmes'].value:
                name=row.get('course_name','').strip().lower();year=row.get('academic_year')
                if name and year and row.get('approved_intake') is not None:
                    key=(name,year,row.get('level','').lower());val=row['approved_intake']
                    if key in approved and approved[key][0]!=val:
                        flag('Approved intake differs across records','Confirmed records show different approved intake for the same named course, level and academic year. Determine whether a corrigendum or superseding approval applies.',f'{key}: {approved[key][0]} in document {approved[key][1]}; {val} in {doc.name}.',agent='Structured consistency agent',document=doc)
                    approved[key]=(val,doc.name)
