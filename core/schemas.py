"""Versioned extraction contracts, not statutory document requirements."""
SCHEMA_VERSION='2.3'
def field(label, type='string', **extra): return {'title':label,'type':type,**extra}
COMMON={'institution_name':field('Institution name'),'institution_address':field('Institution address'),'institution_id':field('Institution permanent ID'),'reference_number':field('Reference / certificate number'),'issuing_authority':field('Issuing authority'),'issue_date':field('Issue date',format='date'),'expiry_date':field('Expiry date',format='date')}
PROGRAMMES={'course_name':field('Course / branch'),'level':field('Level'),'approved_intake':field('Approved intake','integer'),'requested_intake':field('Requested intake','integer'),'academic_year':field('Academic year'),'accreditation_status':field('Accreditation status'),'valid_from':field('Valid from',format='date'),'valid_until':field('Valid until',format='date')}
def table(title, props): return field(title,'array',items={'type':'object','properties':props,'additionalProperties':False})
def schema(title, props): return {'$schema':'https://json-schema.org/draft/2020-12/schema','title':title,'version':SCHEMA_VERSION,'type':'object','properties':props,'additionalProperties':False}
def common(*keys): return {k:COMMON[k] for k in keys}
AFF=schema('Affidavit / Undertaking',{**COMMON,'signatory_name':field('Signatory name'),'signatory_designation':field('Signatory designation'),'stamp_paper_value':field('Stamp paper value','number'),'stamp_paper_serial':field('Stamp serial number'),'execution_date':field('Execution date',format='date'),'notary_details':field('Notary details'),'registration_details':field('Registration details'),'clause_content':field('Clause content'),'template_reference':field('Template reference')})
ACC=schema('Accreditation / Certification',{**COMMON,'accreditation_number':field('Accreditation number'),'grade':field('Grade'),'score':field('Score / CGPA','number'),'score_scale':field('Score scale','number'),'programmes':table('Programme accreditation',PROGRAMMES),'seal_observation':field('Visible seal text / observation'),'conditions':field('Conditions / limitations')})
NOC=schema('NOC / Permission',{**COMMON,'noc_number':field('NOC / consent number'),'state_board_name':field('Issuing state board'),'issuing_department':field('Issuing department'),'signatory_name':field('Signatory'),'premises_address':field('Premises covered'),'academic_year':field('Academic year'),'courses':table('Courses / proposed intake',PROGRAMMES)})
EOA=schema('Previous AICTE EoA',{**COMMON,'application_id':field('Application ID'),'file_number':field('File number'),'academic_year':field('Academic year'),'approval_date':field('Approval date',format='date'),'programmes':table('Approved programmes / intake',PROGRAMMES),'deficiency_remarks':field('Deficiency remarks'),'qr_observation':field('QR presence / visible text'),'digital_signature_observation':field('Signature metadata / observation')})
FACULTY_ROW={'name':field('Faculty name'),'designation':field('Designation'),'department':field('Department'),'qualification':field('Qualification'),'specialization':field('Specialization'),'joining_date':field('Joining date',format='date')}
FAC=schema('Faculty list',{**common('institution_name','institution_id'),'faculty':table('Faculty records',FACULTY_ROW),'declared_student_count':field('Declared student count','integer'),'declared_faculty_count':field('Declared faculty count','integer'),'faculty_student_ratio':field('Faculty : student ratio (students per faculty)','number')})
PERSON=schema('Appointment / Qualification',{**COMMON,'person_name':field('Person name'),'designation':field('Designation'),'department':field('Department'),'degree':field('Degree / highest qualification'),'specialization':field('Specialization'),'university':field('University'),'passing_year':field('Year of passing','integer'),'appointment_date':field('Appointment date',format='date'),'letterhead_observation':field('Letterhead observation')})
TRUST=schema('Trust / Society registration and resolution',{**COMMON,'registered_name':field('Registered name'),'registration_number':field('Registration number'),'registration_date':field('Registration date',format='date'),'resolution_number':field('Resolution number'),'meeting_date':field('Meeting date',format='date'),'signatories':field('Signatories')})
DEF=schema('Past deficiency record',{**common('institution_name','institution_id','reference_number'),'deficiencies':table('Deficiency records',{'category':field('Category'),'description':field('Description'),'deadline':field('Compliance deadline',format='date'),'status':field('Declared resolution status'),'supporting_reference':field('Resolution reference')})})
SELF=schema('Self-disclosure checklist',{**common('institution_name','institution_id'),'checklist':table('Self disclosure items',{'item_name':field('Item'),'status':field('Yes / No / Partial'),'supporting_reference':field('Supporting reference')})})
TER=schema('TER payment receipt',{**common('institution_name','institution_id','reference_number','issuing_authority'),'application_id':field('Application ID'),'payments':table('Payment transactions',{'payment_id':field('Payment ID'),'payment_mode':field('Payment mode'),'transaction_id':field('Transaction ID'),'part_payment_amount':field('Part payment amount','number'),'total_amount':field('Declared total amount','number'),'payment_date':field('Transaction date',format='date')}),'transaction_id':field('Transaction ID'),'amount_paid':field('Amount paid','number'),'currency':field('Currency'),'payment_date':field('Payment date',format='date'),'academic_year':field('Academic year'),'bank_gateway_reference':field('Bank / gateway reference'),'payment_status':field('Declared payment status')})
HISTORY=schema('Application history',{**common('institution_name','institution_id'),'cycles':table('Application cycles',{'application_id':field('Application ID'),'file_number':field('File number'),'academic_year':field('Academic year'),'status':field('Cycle status'),'corrigendum_number':field('Corrigendum number'),'corrigendum_date':field('Corrigendum date',format='date'),'deficiency_resolution':field('Deficiency resolution reference')})})
AFFILIATION=schema('University / State affiliation',{**COMMON,'university_name':field('University name'),'academic_year':field('Academic year'),'valid_from':field('Valid from',format='date'),'programmes':table('Affiliated programmes',PROGRAMMES)})
INTAKE=schema('Approved intake / course records',{**COMMON,'academic_year':field('Academic year'),'affiliating_body':field('Affiliating body'),'nri_quota_status':field('NRI quota status'),'international_quota_status':field('International quota status'),'programmes':table('Course intake',PROGRAMMES)})
BUILD=schema('Infrastructure evidence',{**COMMON,'declared_facilities':field('Declared facilities'),'floor_plan_reference':field('Floor-plan reference'),'certificate_reference':field('Certificate reference')})
CATALOG=[('eoa','Previous EoA',EOA),('noc','NOC / Permission',NOC),('affidavit','Affidavit / Undertaking',AFF),('affidavit_1','Affidavit I',AFF),('affidavit_2','Affidavit II',AFF),('undertaking','Institution letter of undertaking',AFF),('fire','Fire Safety NOC / Certificate',NOC),('pollution_noc','Pollution Control NOC / Consent',NOC),('state_noc','State Government NOC / Permission',NOC),('course_noc','New Course / Intake Increase NOC',NOC),('building','Building / Infrastructure',BUILD),('accreditation','Accreditation certificate',ACC),('nba','NBA programme accreditation',ACC),('naac','NAAC institutional accreditation',ACC),('affiliation','University / State affiliation',AFFILIATION),('government_order','Government approval order',schema('Government approval order',{**NOC['properties'],'order_number':field('Order number'),'order_date':field('Order date',format='date')})),('intake','Approved intake letter',INTAKE),('course_record','Course-wise approval records',INTAKE),('faculty_list','Faculty list',FAC),('faculty_appointment','Faculty appointment letter',PERSON),('qualification','Faculty qualification certificate',PERSON),('principal','Principal / Director qualification proof',PERSON),('trust','Trust / Society registration & resolution',TRUST),('deficiency','Past deficiency records',DEF),('self_disclosure','Self-disclosure compliance checklist',SELF),('ter_payment','TER payment receipt',TER),('application_history','Full application history',HISTORY)]
DOCUMENT_TYPES=[(k,label) for k,label,_ in CATALOG]
SCHEMAS={k:s for k,_,s in CATALOG}

# Document-specific extraction/display contracts; no universal expiry field.
from copy import deepcopy
AFF_KEYS=['institution_name','institution_address','signatory_name','signatory_designation','stamp_paper_value','stamp_paper_serial','execution_date','notary_details','registration_details','clause_content','template_reference']
ACC_KEYS=['accreditation_number','reference_number','institution_name','programmes','grade','score','score_scale','issue_date','expiry_date','issuing_authority','seal_observation','conditions']
FEATURE_KEYS={
'eoa':['institution_name','institution_address','institution_id','application_id','file_number','academic_year','programmes','approval_date','deficiency_remarks','issuing_authority','qr_observation','digital_signature_observation'],
'affidavit':AFF_KEYS,'affidavit_1':AFF_KEYS,'affidavit_2':AFF_KEYS,'undertaking':AFF_KEYS,
'accreditation':ACC_KEYS,'nba':ACC_KEYS,'naac':ACC_KEYS,
'noc':['noc_number','reference_number','issuing_authority','issue_date','premises_address','academic_year','courses'],
'fire':['noc_number','issuing_authority','issue_date','expiry_date','premises_address'],
'pollution_noc':['noc_number','state_board_name','issue_date','expiry_date'],
'state_noc':['reference_number','courses','academic_year','issuing_department','signatory_name'],
'course_noc':['courses','reference_number','issue_date','issuing_authority'],
'affiliation':['reference_number','university_name','academic_year','programmes','validity_period','valid_from','valid_until'],
'government_order':['order_number','order_date','institution_name','courses','issuing_department'],
'intake':['programmes','academic_year','nri_quota_status','international_quota_status','affiliating_body'],
'course_record':['programmes','affiliating_body'],
'faculty_list':['faculty','declared_student_count','declared_faculty_count','faculty_student_ratio'],
'faculty_appointment':['person_name','degree','university','passing_year','appointment_date','designation','letterhead_observation'],
'qualification':['person_name','degree','specialization','university','passing_year','letterhead_observation'],
'principal':['person_name','degree','specialization','appointment_date'],
'trust':['registration_number','registration_date','registered_name','resolution_number','meeting_date','signatories'],
'deficiency':['deficiencies'],'self_disclosure':['checklist'],
'ter_payment':['institution_name','institution_id','application_id','transaction_id','reference_number','amount_paid','payment_date','academic_year','bank_gateway_reference','payments','currency','payment_status'],
'application_history':['cycles'],
'building':['institution_name','institution_address','declared_facilities','floor_plan_reference','certificate_reference'],
}
_new=[]
for _kind,_label,_old in CATALOG:
    _s=deepcopy(_old)
    _extra={'validity_period':field('Validity period (as stated)'),'valid_until':field('Valid until',format='date')}
    _s['properties']={key:deepcopy(_old['properties'].get(key,_extra.get(key))) for key in FEATURE_KEYS[_kind]}
    if _kind=='eoa':
        _s['properties']['file_number']['title']='File number / F.No.'
        _s['properties']['approval_date']['title']='Date of approval'
    if _kind in ['eoa','intake','course_record','affiliation']:
        allowed=['course_name','level','approved_intake','requested_intake','academic_year']
        if _kind=='eoa':allowed.remove('requested_intake')
        if _kind=='affiliation':allowed=['course_name','level','academic_year']
        _s['properties']['programmes']['items']['properties']={k:deepcopy(PROGRAMMES[k]) for k in allowed}
    _new.append((_kind,_label,_s))
CATALOG=_new
SCHEMAS={k:s for k,_,s in CATALOG}
