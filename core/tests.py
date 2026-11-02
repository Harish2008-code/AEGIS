from unittest.mock import patch
from django.test import TestCase,override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Application,Document,Rule,Finding,AuditEvent,AgentRun
from .agents import run_validation
import requests
class WorkspaceTests(TestCase):
    def setUp(self):
        self.staff=User.objects.create_user('reviewer',password='test-only-long-password',is_staff=True)
        self.user=User.objects.create_user('institution',password='test-only-long-password')
        self.other=User.objects.create_user('other',password='test-only-long-password')
        self.app=Application.objects.create(reference='APP-TEST',institution='Synthetic Institute',institution_id='SYNTH-1',state='Tamil Nadu',owner=self.user)
    def test_login_required(self):
        self.assertEqual(self.client.get('/').status_code,302)
    def test_all_pages_render(self):
        self.client.force_login(self.staff)
        for url in ['/','/applications/','/applications/new/',f'/applications/{self.app.pk}/','/documents/','/alerts/','/rules/','/audit/','/agents/','/export/']:
            with self.subTest(url=url): self.assertEqual(self.client.get(url).status_code,200)
    def test_owner_isolation(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(f'/applications/{self.app.pk}/').status_code,404)
        self.assertNotContains(self.client.get('/applications/'),'Synthetic Institute')
    def test_nonstaff_cannot_validate_or_configure(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(f'/applications/{self.app.pk}/validate/').status_code,403)
        self.assertEqual(self.client.get('/rules/').status_code,403)
    def test_validation_is_post_only(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(f'/applications/{self.app.pk}/validate/').status_code,405)
    @patch('core.agents.requests.post',side_effect=requests.ConnectionError)
    def test_offline_validation_and_idempotence(self,mock):
        Rule.objects.create(code='DOC-1',title='Require fire evidence',document_kind='fire',source_reference='Demo only')
        run_validation(self.app,'reviewer');run_validation(self.app,'reviewer')
        self.assertEqual(Finding.objects.count(),1)
        self.assertEqual(AgentRun.objects.filter(status='Unavailable').count(),2)
        self.app.refresh_from_db();self.assertEqual(self.app.status,'Needs attention')
    def test_bad_upload_rejected(self):
        self.client.force_login(self.user)
        self.client.post(f'/applications/{self.app.pk}/upload/',{'kind':'eoa','file':SimpleUploadedFile('bad.pdf',b'not-a-pdf')})
        self.assertEqual(Document.objects.count(),0)
    def test_verification_never_fakes_verified(self):
        doc=Document.objects.create(application=self.app,kind='eoa',name='synthetic.pdf')
        self.client.force_login(self.staff);self.client.post(f'/documents/{doc.pk}/verify/')
        doc.refresh_from_db();self.assertEqual(doc.status,'Verification pending');self.assertIsNone(doc.verified_at)
    @override_settings(DEMO_MODE=False)
    def test_demo_disabled(self): self.assertEqual(self.client.post('/demo-login/').status_code,403)
    def test_resolution_rationale_required(self):
        f=Finding.objects.create(application=self.app,title='Test',detail='Test',evidence='Synthetic')
        self.client.force_login(self.staff);self.client.post(f'/findings/{f.pk}/resolve/',{'note':'short'})
        f.refresh_from_db();self.assertFalse(f.resolved)
    def test_create_application(self):
        self.client.force_login(self.user)
        self.client.post('/applications/new/',{'institution':'New synthetic','institution_id':'SYNTH-2','state':'Kerala','category':'Extension of Approval'})
        self.assertTrue(Application.objects.filter(institution_id='SYNTH-2',owner=self.user).exists())
    def test_csrf_required(self):
        from django.test import Client
        c=Client(enforce_csrf_checks=True);c.force_login(self.staff)
        self.assertEqual(c.post(f'/applications/{self.app.pk}/validate/').status_code,403)

class StructuredEvidenceTests(TestCase):
    def setUp(self):
        self.reviewer=User.objects.create_user('structured-reviewer',password='test-password',is_staff=True)
        self.owner=User.objects.create_user('structured-owner',password='test-password')
        self.app=Application.objects.create(reference='STRUCT-1',institution='Example Institute',institution_id='SYNTH-1',state='Tamil Nadu',owner=self.owner)
        self.doc=Document.objects.create(application=self.app,name='test.pdf',kind='naac')
        from .models import DocumentPage
        DocumentPage.objects.create(document=self.doc,number=1,text='Institution name: Example Institute\nGrade: A+\nCGPA: 3.35\nExpiry date: 2028-12-20',method='PDF embedded text')
    def test_catalogue_and_all_schemas_valid(self):
        from .schemas import SCHEMAS
        from jsonschema import Draft202012Validator
        self.assertEqual(len(SCHEMAS),27)
        for schema in SCHEMAS.values():Draft202012Validator.check_schema(schema)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get('/schemas/').status_code,200)
        self.assertEqual(self.client.get('/schemas/naac.json').status_code,200)
        self.assertEqual(self.client.get(f'/documents/{self.doc.pk}/review/').status_code,200)
    def test_label_extraction(self):
        from .extraction import labelled_candidates
        labelled_candidates(self.doc)
        self.assertEqual(self.doc.fields.get(key='score').value,3.35)
        self.assertEqual(self.doc.fields.get(key='expiry_date').value,'2028-12-20')
        self.assertEqual(self.doc.fields.get(key='institution_name').review_status,'Needs review')
    def test_invalid_typed_value_rejected(self):
        self.client.force_login(self.reviewer)
        self.client.post(f'/documents/{self.doc.pk}/field/',{'key':'score','value':'"not numeric"','page':1,'evidence':'CGPA: 3.35','review_note':'Checked original page','review_status':'Confirmed'})
        self.assertFalse(self.doc.fields.exists())
    def test_confirmed_value_and_audit(self):
        self.client.force_login(self.reviewer)
        self.client.post(f'/documents/{self.doc.pk}/field/',{'key':'score','value':'3.35','page':1,'evidence':'CGPA: 3.35','review_note':'Checked the original certificate','review_status':'Confirmed'})
        self.assertEqual(self.doc.fields.get(key='score').review_status,'Confirmed')
        self.assertTrue(AuditEvent.objects.filter(action='Structured field reviewed').exists())
    def test_verified_requires_attestation(self):
        from django.utils import timezone
        self.client.force_login(self.reviewer)
        data={'status':'Verified','source_name':'Authorized authority','source_reference':'CONFIRM-123','checked_at':timezone.now().isoformat(),'notes':'Authorized confirmation matched certificate scope and dates.'}
        self.client.post(f'/documents/{self.doc.pk}/verification/',data)
        self.doc.refresh_from_db();self.assertNotEqual(self.doc.status,'Verified')
        data['attestation']='yes';self.client.post(f'/documents/{self.doc.pk}/verification/',data)
        self.doc.refresh_from_db();self.assertEqual(self.doc.status,'Verified')
        self.assertEqual(self.doc.verifications.get().method,'Manual authority confirmation')
    def test_owner_cannot_confirm(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.post(f'/documents/{self.doc.pk}/field/',{}).status_code,403)
        self.assertEqual(self.client.post(f'/documents/{self.doc.pk}/verification/',{}).status_code,403)
    def test_unowned_document_hidden(self):
        other=User.objects.create_user('unrelated-user',password='test-password');self.client.force_login(other)
        self.assertEqual(self.client.get(f'/documents/{self.doc.pk}/review/').status_code,404)
    @patch('core.extraction.requests.post')
    def test_ungrounded_ai_field_rejected(self,mock):
        from .extraction import structured_extract
        mock.return_value.json.return_value={'message':{'content':'{"fields":[{"key":"score","value":4.0,"page":1,"evidence":"Nonexistent quote here"}]}'}}
        structured_extract(self.doc,'reviewer');self.assertFalse(self.doc.fields.exists())
    def test_scoped_subtype_satisfies_affidavit_rule(self):
        from .agents import run_validation
        self.doc.kind='affidavit_1';self.doc.extracted_text='SYNTH-1';self.doc.save()
        Rule.objects.create(code='AFF-TEST',title='Affidavit',document_kind='affidavit',source_reference='Test only')
        with patch('core.agents.requests.post',side_effect=requests.ConnectionError):run_validation(self.app,'reviewer')
        self.assertFalse(self.app.findings.filter(rule_code='AFF-TEST').exists())
    def test_retry_ocr_records_page_and_invalidates_confirmation(self):
        import io,tempfile
        from PIL import Image
        from .extraction import extract_document
        from .models import ExtractedField
        raw=io.BytesIO();Image.new('RGB',(100,100),'white').save(raw,format='PNG')
        with tempfile.TemporaryDirectory() as temp:
            with override_settings(MEDIA_ROOT=temp):
                self.doc.file.save('test.png',SimpleUploadedFile('test.png',raw.getvalue()))
                ExtractedField.objects.create(document=self.doc,key='grade',value='A+',review_status='Confirmed')
                with patch('core.extraction.image_ocr',return_value=('Institution name: Example Institute\nGrade: A+',91.5)):
                    extract_document(self.doc)
                self.assertEqual(self.doc.pages.get().confidence,91.5)
                self.assertEqual(self.doc.fields.get(key='grade').review_status,'Recheck required')
    @patch('core.agents.requests.post',side_effect=requests.ConnectionError)
    def test_pending_source_status_survives_validation(self,mock):
        self.doc.extracted_text='SYNTH-1';self.doc.status='Verification pending';self.doc.save()
        run_validation(self.app,'reviewer');self.doc.refresh_from_db()
        self.assertEqual(self.doc.status,'Verification pending')
    @patch('core.agents.requests.post',side_effect=requests.ConnectionError)
    def test_confirmed_programme_expiry_flag(self,mock):
        from .models import ExtractedField
        self.doc.extracted_text='SYNTH-1';self.doc.save()
        ExtractedField.objects.create(document=self.doc,key='programmes',value=[{'course_name':'Civil Engineering','valid_until':'2020-06-30'}],review_status='Confirmed',page=1)
        run_validation(self.app,'reviewer')
        self.assertTrue(self.app.findings.filter(title__startswith='Programme validity expired').exists())

class InstitutionArchiveTests(TestCase):
    def setUp(self):
        import tempfile
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.override=override_settings(MEDIA_ROOT=self.temp.name);self.override.enable();self.addCleanup(self.override.disable)
        self.owner=User.objects.create_user('zip-owner',password='test-password')
        self.other=User.objects.create_user('zip-other',password='test-password')
        self.reviewer=User.objects.create_user('zip-reviewer',password='test-password',is_staff=True)
        self.app=Application.objects.create(reference='ZIP-A',institution='Synthetic University',institution_id='SYNTH-ZIP-1',state='Tamil Nadu',owner=self.owner)
        self.second=Application.objects.create(reference='ZIP-B',institution='Synthetic University',institution_id=' synth-zip-1 ',state='Tamil Nadu',owner=self.owner)
    def add_document(self,app,name='same.pdf',content=b'%PDF-test-content'):
        return Document.objects.create(application=app,name=name,kind='eoa',file=SimpleUploadedFile(name,content))
    def test_same_institution_one_zip_and_unique_entries(self):
        import zipfile,json
        from .archives import rebuild_institution_archive,archive_path
        d1=self.add_document(self.app);d2=self.add_document(self.second)
        path=rebuild_institution_archive(self.app)
        self.assertEqual(path,archive_path(self.second))
        with zipfile.ZipFile(path) as z:
            manifest=json.loads(z.read('manifest.json'))
            docs=manifest['documents'];self.assertEqual(len(docs),2)
            self.assertNotEqual(docs[0]['archive_path'],docs[1]['archive_path'])
            self.assertEqual(len(z.namelist()),4)
        self.assertEqual(len(list(path.parent.glob('*.zip'))),1)
    def test_other_university_not_included(self):
        import json,zipfile
        from .archives import rebuild_institution_archive
        unrelated=Application.objects.create(reference='ZIP-C',institution='Other University',institution_id='OTHER-ID',state='Kerala',owner=self.other)
        self.add_document(self.app);self.add_document(unrelated)
        with zipfile.ZipFile(rebuild_institution_archive(self.app)) as z:
            self.assertEqual(len(json.loads(z.read('manifest.json'))['documents']),1)
    def test_nonowner_denied(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(f'/applications/{self.app.pk}/institution-archive/').status_code,404)
    def test_shared_id_does_not_grant_other_owner_access(self):
        self.second.owner=self.other;self.second.save()
        self.client.force_login(self.owner)
        response=self.client.get(f'/applications/{self.app.pk}/institution-archive/')
        self.assertEqual(response.status_code,302)
        self.assertFalse(AuditEvent.objects.filter(action='Institution ZIP downloaded').exists())
    def test_staff_can_download_and_audit(self):
        self.add_document(self.app)
        self.client.force_login(self.reviewer)
        response=self.client.get(f'/applications/{self.app.pk}/institution-archive/')
        self.assertEqual(response.status_code,200);self.assertEqual(response['Content-Type'],'application/zip')
        response.close();self.assertTrue(AuditEvent.objects.filter(action='Institution ZIP downloaded').exists())
    def test_reference_upload_input_removed(self):
        self.client.force_login(self.owner)
        response=self.client.get(f'/applications/{self.app.pk}/')
        self.assertNotContains(response,'name="reference_number"')
        self.assertContains(response,'Download institution ZIP')
    def test_rebuild_replaces_instead_of_accumulating(self):
        import zipfile,json
        from .archives import rebuild_institution_archive
        self.add_document(self.app);path=rebuild_institution_archive(self.app)
        self.add_document(self.second,name='second.pdf');self.assertEqual(rebuild_institution_archive(self.second),path)
        with zipfile.ZipFile(path) as z:self.assertEqual(len(json.loads(z.read('manifest.json'))['documents']),2)
        self.assertEqual(len(list(path.parent.glob('*.zip'))),1)
    def test_unassigned_reference_cases_stay_separate(self):
        from .archives import archive_path
        self.app.institution_id='UNCONFIRMED';self.app.save()
        self.second.institution_id='UNCONFIRMED';self.second.save()
        self.assertNotEqual(archive_path(self.app),archive_path(self.second))

class AutomaticOcrPipelineTests(TestCase):
    def setUp(self):
        import tempfile
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.settings_override=override_settings(MEDIA_ROOT=self.temp.name);self.settings_override.enable();self.addCleanup(self.settings_override.disable)
        self.reviewer=User.objects.create_user('pipeline-reviewer',password='test-password',is_staff=True)
        self.owner=User.objects.create_user('pipeline-owner',password='test-password')
        self.app=Application.objects.create(reference='PIPE-1',institution='Synthetic University',institution_id='SYNTH-PIPE',state='Tamil Nadu',owner=self.owner)
    def make_pdf(self,pages=2):
        from pypdf import PdfWriter
        import io
        writer=PdfWriter()
        for _ in range(pages):writer.add_blank_page(width=300,height=300)
        stream=io.BytesIO();writer.write(stream)
        return SimpleUploadedFile('pipeline.pdf',stream.getvalue(),content_type='application/pdf')
    @patch('core.extraction.requests.post')
    @patch('core.extraction.image_ocr')
    def test_pdf_pages_always_images_then_ocr_then_ollama(self,ocr,post):
        import json
        from .extraction import process_document
        ocr.return_value=('Institution name: Synthetic University\nInstitution ID: SYNTH-PIPE',95.0)
        post.return_value.json.return_value={'message':{'content':json.dumps({'fields':[{'key':'institution_name','value':'Synthetic University','page':1,'evidence':'Institution name: Synthetic University'}]})}}
        doc=Document.objects.create(application=self.app,name='pipeline.pdf',kind='eoa',file=self.make_pdf())
        with patch('pypdf.PdfReader',side_effect=AssertionError('Embedded text reader must not run')):process_document(doc,self.reviewer.username)
        self.assertEqual(ocr.call_count,2);post.assert_called_once()
        self.assertEqual(doc.pages.count(),2)
        self.assertTrue(all(p.image and p.image.storage.exists(p.image.name) for p in doc.pages.all()))
        self.assertTrue(all(p.method=='Tesseract OCR' for p in doc.pages.all()))
        self.assertEqual(doc.pipeline_state['ollama'],'Completed — review required')
        self.assertEqual(doc.fields.get(key='institution_name').method,'Ollama candidate')
    @patch('core.extraction.requests.post')
    @patch('core.extraction.image_ocr',side_effect=RuntimeError('OCR engine unavailable'))
    def test_failed_ocr_skips_ollama_but_retains_page_image(self,ocr,post):
        from .extraction import process_document
        doc=Document.objects.create(application=self.app,name='pipeline.pdf',kind='eoa',file=self.make_pdf(1))
        process_document(doc,self.reviewer.username)
        post.assert_not_called();self.assertEqual(doc.pipeline_state['ocr'],'Failed')
        self.assertTrue(doc.pages.get().image)
        self.assertEqual(doc.extracted_text.strip(),'[Page 1]')
        self.assertEqual(doc.fields.count(),0)
    @patch('core.extraction.requests.post',side_effect=requests.ConnectionError)
    @patch('core.extraction.image_ocr',return_value=('Institution name: Synthetic University',92.0))
    def test_offline_ollama_keeps_ocr_and_explicit_state(self,ocr,post):
        from .extraction import process_document
        doc=Document.objects.create(application=self.app,name='pipeline.pdf',kind='eoa',file=self.make_pdf(1))
        process_document(doc,self.reviewer.username)
        self.assertEqual(doc.pipeline_state['ollama'],'Unavailable')
        self.assertEqual(doc.fields.get(key='institution_name').method,'Label extraction')
    @patch('core.extraction.requests.post',side_effect=requests.ConnectionError)
    @patch('core.extraction.image_ocr',return_value=('Institution name: Synthetic University',92.0))
    def test_upload_automatically_processes_and_archives(self,ocr,post):
        from .archives import archive_path
        self.client.force_login(self.owner)
        response=self.client.post(f'/applications/{self.app.pk}/upload/',{'kind':'eoa','file':self.make_pdf(1)})
        doc=self.app.documents.get()
        self.assertRedirects(response,f'/documents/{doc.pk}/review/')
        self.assertEqual(doc.pipeline_state['ollama'],'Unavailable')
        self.assertTrue(archive_path(self.app).exists())
        self.assertEqual(doc.reference_number,'')
    def test_schemas_use_only_applicable_features(self):
        from .schemas import SCHEMAS
        for kind in ['eoa','affidavit','undertaking','ter_payment','faculty_list','state_noc','course_noc']:
            self.assertNotIn('expiry_date',SCHEMAS[kind]['properties'])
        for kind in ['nba','naac','fire','pollution_noc']:
            self.assertIn('expiry_date',SCHEMAS[kind]['properties'])
    @patch('core.extraction.image_ocr',return_value=('Synthetic OCR text',90.0))
    def test_page_image_access_is_scoped(self,ocr):
        from .extraction import extract_document
        doc=Document.objects.create(application=self.app,name='pipeline.pdf',kind='eoa',file=self.make_pdf(1));extract_document(doc)
        self.client.force_login(self.owner)
        response=self.client.get(f'/documents/{doc.pk}/pages/1/image/')
        self.assertEqual(response.status_code,200);self.assertEqual(response['Content-Type'],'image/png');response.close()
        other=User.objects.create_user('pipeline-other',password='test-password');self.client.force_login(other)
        self.assertEqual(self.client.get(f'/documents/{doc.pk}/pages/1/image/').status_code,404)

class DocumentSpecificFeatureTests(TestCase):
    def setUp(self):
        from pathlib import Path
        from .models import DocumentPage
        self.user=User.objects.create_user('feature-reviewer',password='test-password',is_staff=True)
        self.app=Application.objects.create(reference='FEATURE-1',institution='Takshshila reference test',institution_id='UNCONFIRMED',state='Madhya Pradesh',owner=self.user)
        self.doc=Document.objects.create(application=self.app,name='reference.pdf',kind='eoa')
        self.text=(Path(__file__).parent/'fixtures/eoa_ocr_example.txt').read_text()
        DocumentPage.objects.create(document=self.doc,number=2,text=self.text,method='Tesseract OCR')
    def test_eoa_patterns_from_user_supplied_ocr(self):
        from .extraction import document_patterns
        document_patterns(self.doc)
        values={f.key:f.value for f in self.doc.fields.all()}
        self.assertEqual(values['file_number'],'Central/1-44641957809/2025/EOA')
        self.assertEqual(values['application_id'],'1-44641957809')
        self.assertEqual(values['academic_year'],'2025-26')
        self.assertEqual(values['approval_date'],'2025-04-30')
        self.assertEqual(values['institution_name'],'TAKSHSHILA INSTITUTE OF ENGINEERING & TECHNOLOGY, JABALPUR')
        self.assertEqual(values['issuing_authority'],'All India Council for Technical Education')
        self.assertNotIn('expiry_date',values)
        self.assertNotIn('institution_id',values)  # application ID is not a Permanent ID
        self.assertNotIn('institution_address',values)  # mixed columns must not become false clean address
    @patch('core.extraction.requests.post',side_effect=requests.ConnectionError)
    def test_field_retry_reuses_ocr_and_fills_eoa_candidates_offline(self,post):
        self.client.force_login(self.user)
        self.client.post(f'/documents/{self.doc.pk}/structured/')
        self.assertEqual(self.doc.fields.get(key='approval_date').value,'2025-04-30')
        self.doc.refresh_from_db();self.assertEqual(self.doc.pipeline_state['ollama'],'Unavailable')
    def test_summary_has_document_specific_fields_without_expiry(self):
        self.client.force_login(self.user)
        response=self.client.get(f'/documents/{self.doc.pk}/review/')
        self.assertContains(response,'Date of approval')
        self.assertContains(response,'File number / F.No.')
        self.assertNotContains(response,'Expiry date')
    def test_whitespace_normalized_quote_keeps_actual_source(self):
        from .extraction import match_source_quote
        self.assertEqual(match_source_quote('Academic\nYear 2025-26','Academic Year 2025-26'),'Academic\nYear 2025-26')
        self.assertIsNone(match_source_quote('Academic Year 2025-26','Academic Year 2026-27'))
    def test_affidavit_has_execution_not_expiry(self):
        from .schemas import SCHEMAS
        props=SCHEMAS['affidavit_1']['properties']
        self.assertIn('execution_date',props);self.assertIn('notary_details',props)
        self.assertNotIn('expiry_date',props);self.assertNotIn('issue_date',props)
