import unittest
import json
from app import create_app
from models import db, User, HealthRecord, DoctorAccess, ConsultationSummary, AuditLog

class PHRMSCoreTestSuite(unittest.TestCase):
    def setUp(self):
        # Configure test application with in-memory database
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        self.client = self.app.test_client()

    def test_01_database_seeding(self):
        """Verify initial database seeding of personas and medical records."""
        with self.app.app_context():
            # Check users
            self.assertGreaterEqual(User.query.count(), 6)
            amara = User.query.filter_by(email='amara.perera@health.lk').first()
            self.assertIsNotNone(amara)
            self.assertEqual(amara.role, 'PATIENT')
            self.assertEqual(amara.blood_group, 'O+')
            self.assertIn('Penicillin', amara.known_allergies)

            dr_bandara = User.query.filter_by(email='dr.bandara@hospital.lk').first()
            self.assertIsNotNone(dr_bandara)
            self.assertEqual(dr_bandara.role, 'DOCTOR')

            malini = User.query.filter_by(email='malini.fernando@phrms.gov.lk').first()
            self.assertIsNotNone(malini)
            self.assertEqual(malini.role, 'REVIEWER')

            # Check records
            approved_records = HealthRecord.query.filter_by(status='APPROVED').all()
            self.assertGreaterEqual(len(approved_records), 3)

    def test_02_rbac_unauthenticated_redirection(self):
        """Verify unauthenticated requests to protected portals redirect to login."""
        endpoints = [
            '/patient/dashboard',
            '/reviewer/workspace',
            '/doctor/dashboard',
            '/admin/console'
        ]
        for ep in endpoints:
            res = self.client.get(ep)
            self.assertEqual(res.status_code, 302)
            self.assertIn('/login', res.headers['Location'])

    def test_03_instant_demo_switcher(self):
        """Verify one-click demo switcher successfully switches session and redirects."""
        # Switch to patient
        res = self.client.get('/demo/switch/patient', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Amara Perera', res.data)
        self.assertIn(b'Longitudinal Health Timeline', res.data)

        # Switch to reviewer
        res = self.client.get('/demo/switch/reviewer', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Malini Fernando', res.data)
        self.assertIn(b'Review Intake Queue', res.data)

        # Switch to doctor
        res = self.client.get('/demo/switch/doctor', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Dr. Nalin Bandara', res.data)

    def test_04_patient_document_upload(self):
        """Verify patient can submit a medical document and it enters PENDING status."""
        self.client.get('/demo/switch/patient')
        res = self.client.post('/patient/records/new', data={
            'title': 'Automated Test Blood Glucose Curve',
            'category': 'Lab Report',
            'provider_name': 'Central City Pathology',
            'record_date': '2026-10-25',
            'clinical_summary': 'Glucose values evaluated over 2 hours post-load.'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        with self.app.app_context():
            rec = HealthRecord.query.filter_by(title='Automated Test Blood Glucose Curve').first()
            self.assertIsNotNone(rec)
            self.assertEqual(rec.status, 'PENDING')
            self.assertEqual(rec.provider_name, 'Central City Pathology')

    def test_05_reviewer_approval_workflow(self):
        """Verify reviewer can inspect and approve a pending record, transitioning it to APPROVED."""
        with self.app.app_context():
            pending = HealthRecord.query.filter_by(status='PENDING').first()
            self.assertIsNotNone(pending)
            pending_id = pending.id

        self.client.get('/demo/switch/reviewer')
        res = self.client.post(f'/reviewer/records/{pending_id}/decide', data={
            'decision': 'APPROVED',
            'review_notes': 'Affirmed 3 criteria. Clear calibration.'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        with self.app.app_context():
            updated = db.session.get(HealthRecord, pending_id)
            self.assertEqual(updated.status, 'APPROVED')
            self.assertIsNotNone(updated.reviewed_at)

    def test_06_doctor_authorization_gate(self):
        """Verify Doctor Access Gate: Authorized patient loads (200), Unauthorized patient yields 403."""
        with self.app.app_context():
            amara = User.query.filter_by(email='amara.perera@health.lk').first()
            rohan = User.query.filter_by(email='rohan.silva@health.lk').first()
            dr_bandara = User.query.filter_by(email='dr.bandara@hospital.lk').first()

            # Ensure Amara consented to Dr. Bandara
            access = DoctorAccess.query.filter_by(patient_id=amara.id, doctor_id=dr_bandara.id).first()
            if not access:
                access = DoctorAccess(patient_id=amara.id, doctor_id=dr_bandara.id, is_active=True)
                db.session.add(access)
                db.session.commit()
            else:
                access.is_active = True
                db.session.commit()

            # Ensure Rohan did NOT consent to Dr. Bandara
            rohan_access = DoctorAccess.query.filter_by(patient_id=rohan.id, doctor_id=dr_bandara.id).first()
            if rohan_access:
                rohan_access.is_active = False
                db.session.commit()

            amara_id = amara.id
            rohan_id = rohan.id

        # Switch to Doctor
        self.client.get('/demo/switch/doctor')

        # Access authorized patient -> HTTP 200
        res_auth = self.client.get(f'/doctor/patient/{amara_id}')
        self.assertEqual(res_auth.status_code, 200)
        self.assertIn(b'Amara Perera', res_auth.data)
        self.assertIn(b'KNOWN ALLERGIES', res_auth.data)

        # Access unauthorized patient -> HTTP 403 Forbidden
        res_unauth = self.client.get(f'/doctor/patient/{rohan_id}')
        self.assertEqual(res_unauth.status_code, 403)
        self.assertIn(b'Access Denied', res_unauth.data)

    def test_07_patient_grant_and_revoke_access(self):
        """Verify patient can grant and revoke doctor access, updating permissions in real time."""
        with self.app.app_context():
            amara = User.query.filter_by(email='amara.perera@health.lk').first()
            dr_kavindi = User.query.filter_by(email='dr.jayasinghe@hospital.lk').first()
            kavindi_id = dr_kavindi.id

        # Log in as Amara
        self.client.get('/demo/switch/patient')

        # Grant access to Dr. Kavindi
        res_grant = self.client.post('/patient/access', data={
            'doctor_id': kavindi_id,
            'action': 'grant',
            'access_notes': 'Authorized for general review'
        }, follow_redirects=True)
        self.assertEqual(res_grant.status_code, 200)

        with self.app.app_context():
            grant = DoctorAccess.query.filter_by(patient_id=amara.id, doctor_id=kavindi_id).first()
            self.assertTrue(grant.is_active)

        # Revoke access
        res_revoke = self.client.post('/patient/access', data={
            'doctor_id': kavindi_id,
            'action': 'revoke'
        }, follow_redirects=True)
        self.assertEqual(res_revoke.status_code, 200)

        with self.app.app_context():
            grant = DoctorAccess.query.filter_by(patient_id=amara.id, doctor_id=kavindi_id).first()
            self.assertFalse(grant.is_active)

    def test_08_consultation_summary_generation_and_print(self):
        """Verify patient can generate consultation summary and view printable briefing sheet."""
        with self.app.app_context():
            amara = User.query.filter_by(email='amara.perera@health.lk').first()
            records = HealthRecord.query.filter_by(patient_id=amara.id, status='APPROVED').all()
            record_ids = [str(r.id) for r in records[:2]]

        self.client.get('/demo/switch/patient')
        res = self.client.post('/patient/summary/new', data={
            'title': 'Cardiology Pre-Op Evaluation Summary',
            'chief_complaint': 'Mild shortness of breath on exertion; review prior ECG and lipid metrics.',
            'selected_records': record_ids
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Cardiology Pre-Op Evaluation Summary', res.data)
        self.assertIn(b'Section 1: Chief Complaint', res.data)
        self.assertIn(b'Print / Export PDF', res.data)

    def test_09_audit_trail_logging(self):
        """Verify central audit logging records events in the audit_logs table."""
        with self.app.app_context():
            initial_count = AuditLog.query.count()
            self.assertGreater(initial_count, 0)

        self.client.get('/demo/switch/patient')
        with self.app.app_context():
            new_count = AuditLog.query.count()
            self.assertGreater(new_count, initial_count)
            latest = AuditLog.query.order_by(AuditLog.timestamp.desc()).first()
            self.assertEqual(latest.action, 'DEMO_ROLE_SWITCH')

if __name__ == '__main__':
    unittest.main()
