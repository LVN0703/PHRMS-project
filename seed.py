import json
from datetime import datetime, date, timedelta, timezone
from models import db, User, HealthRecord, DoctorAccess, ConsultationSummary, AuditLog

def seed_database(app):
    with app.app_context():
        # Create all tables
        db.create_all()

        # Check if already seeded
        if User.query.first():
            print("Database already contains data. Skipping seeding.")
            return

        print("Seeding initial PHRMS clinical personas and records...")

        # 1. Create Users
        # Patient 1: Amara Perera
        amara = User(
            full_name="Amara Perera",
            email="amara.perera@health.lk",
            role="PATIENT",
            national_id="199182302481",
            date_of_birth=date(1991, 11, 12),
            blood_group="O+",
            known_allergies="Penicillin (Severe Anaphylactoid), Dust Mites",
            primary_facility="Asiri Central Hospital Colombo"
        )
        amara.set_password("password123")

        # Patient 2: Rohan Silva
        rohan = User(
            full_name="Rohan Silva",
            email="rohan.silva@health.lk",
            role="PATIENT",
            national_id="198418903310",
            date_of_birth=date(1984, 6, 25),
            blood_group="B+",
            known_allergies="Sulfa Drugs",
            primary_facility="Nawaloka Hospital Colombo"
        )
        rohan.set_password("password123")

        # Doctor 1: Dr. Nalin Bandara
        dr_bandara = User(
            full_name="Dr. Nalin Bandara",
            email="dr.bandara@hospital.lk",
            role="DOCTOR",
            specialization="Consultant Cardiologist",
            slmc_reg_no="SLMC #18420"
        )
        dr_bandara.set_password("password123")

        # Doctor 2: Dr. Kavindi Jayasinghe
        dr_kavindi = User(
            full_name="Dr. Kavindi Jayasinghe",
            email="dr.jayasinghe@hospital.lk",
            role="DOCTOR",
            specialization="Consultant Physician",
            slmc_reg_no="SLMC #22910"
        )
        dr_kavindi.set_password("password123")

        # Reviewer: Malini Fernando
        malini = User(
            full_name="Malini Fernando",
            email="malini.fernando@phrms.gov.lk",
            role="REVIEWER",
            staff_id="REG-88410"
        )
        malini.set_password("password123")

        # Admin: K. Wickramasinghe
        admin = User(
            full_name="K. Wickramasinghe",
            email="admin.sec@phrms.gov.lk",
            role="ADMIN",
            staff_id="SEC-01-CISO"
        )
        admin.set_password("password123")

        db.session.add_all([amara, rohan, dr_bandara, dr_kavindi, malini, admin])
        db.session.commit()

        # 2. Create Health Records for Amara Perera
        r1 = HealthRecord(
            patient_id=amara.id,
            title="Fasting Lipid Profile & Glycated Hemoglobin (HbA1c)",
            category="Lab Report",
            provider_name="Asiri Central Hospital Laboratory",
            record_date=date(2026, 10, 14),
            clinical_summary="Fasting Blood Glucose: 94 mg/dL (Optimal), HbA1c: 5.6% (Non-Diabetic), Total Cholesterol: 198 mg/dL (Borderline), Triglycerides: 132 mg/dL (Normal).",
            file_path="uploads/Lab_Report_Lipid_HbA1c.pdf",
            file_name="Lab_Report_Lipid_HbA1c.pdf",
            file_size_kb=1420,
            status="APPROVED",
            reviewer_id=malini.id,
            review_notes="Verified against official laboratory accreditation seal. All numeric ranges legible.",
            reviewed_at=datetime(2026, 10, 15, 9, 30, tzinfo=timezone.utc),
            submitted_at=datetime(2026, 10, 14, 10, 42, tzinfo=timezone.utc)
        )

        r2 = HealthRecord(
            patient_id=amara.id,
            title="Atorvastatin & Metformin Maintenance Regimen",
            category="Prescription",
            provider_name="Colombo Heart & Vascular Center",
            record_date=date(2026, 9, 28),
            clinical_summary="Atorvastatin Calcium 10mg Oral nightly before sleep (30 Days); Metformin Hydrochloride 500mg ER post-breakfast (60 Days). Safety cross-check: No Penicillin derivatives in formulation.",
            file_path="uploads/Prescription_Atorvastatin_Metformin.pdf",
            file_name="Prescription_Atorvastatin_Metformin.pdf",
            file_size_kb=890,
            status="APPROVED",
            reviewer_id=malini.id,
            review_notes="Clinician SLMC license verified. Dosage and signature clear.",
            reviewed_at=datetime(2026, 9, 29, 14, 15, tzinfo=timezone.utc),
            submitted_at=datetime(2026, 9, 28, 11, 20, tzinfo=timezone.utc)
        )

        r3 = HealthRecord(
            patient_id=amara.id,
            title="Comprehensive 12-Lead Electrocardiogram (ECG) Review",
            category="Consultation Note",
            provider_name="Cardiology Outpatient Department",
            record_date=date(2026, 8, 12),
            clinical_summary="Resting Heart Rate: 72 bpm, Normal Sinus Rhythm. Calibration: 25mm/s, 10mm/mV. PR interval: 142ms, QRS duration: 88ms, QTc: 412ms. Diagnostic conclusion: Normal variant, no ischemic ST changes.",
            file_path="uploads/ECG_12Lead_Cardiac_Review.pdf",
            file_name="ECG_12Lead_Cardiac_Review.pdf",
            file_size_kb=2100,
            status="APPROVED",
            reviewer_id=malini.id,
            review_notes="Full 12-lead calibration grids verified. Clear trace quality.",
            reviewed_at=datetime(2026, 8, 13, 11, 0, tzinfo=timezone.utc),
            submitted_at=datetime(2026, 8, 12, 16, 45, tzinfo=timezone.utc)
        )

        r4 = HealthRecord(
            patient_id=amara.id,
            title="Cardiac Ultrasound Echocardiogram Scan Report",
            category="Imaging / Scan",
            provider_name="Nawaloka Heart Centre",
            record_date=date(2026, 10, 26),
            clinical_summary="Transthoracic echocardiogram to assess left ventricular function following 4 weeks of statin therapy. Ejection fraction recorded at 62%.",
            file_path="uploads/Echo_Scan_Amara_Perera.pdf",
            file_name="Echo_Scan_Amara_Perera.pdf",
            file_size_kb=3450,
            status="PENDING",
            submitted_at=datetime(2026, 10, 26, 14, 10, tzinfo=timezone.utc)
        )

        r5 = HealthRecord(
            patient_id=amara.id,
            title="Renal Electrolytes & Serum Creatinine Analysis",
            category="Lab Report",
            provider_name="Lanka Diagnostic Laboratories",
            record_date=date(2026, 10, 20),
            clinical_summary="Serum Creatinine: 0.9 mg/dL, eGFR: >90 mL/min/1.73m², Potassium: 4.2 mmol/L, Sodium: 139 mmol/L.",
            file_path="uploads/Renal_Panel_LankaLabs.pdf",
            file_name="Renal_Panel_LankaLabs.pdf",
            file_size_kb=620,
            status="CORRECTION_REQUIRED",
            reviewer_id=malini.id,
            review_notes="Hospital lab official authorization stamp and pathologist signature are obscured in upload. Please re-upload a clear scan.",
            reviewed_at=datetime(2026, 10, 21, 10, 30, tzinfo=timezone.utc),
            submitted_at=datetime(2026, 10, 20, 15, 0, tzinfo=timezone.utc)
        )

        # Records for Rohan Silva
        r6 = HealthRecord(
            patient_id=rohan.id,
            title="Annual Full Blood Count & Hemogram",
            category="Lab Report",
            provider_name="Durdans Hospital Diagnostic Center",
            record_date=date(2026, 9, 15),
            clinical_summary="Hemoglobin: 14.5 g/dL, Total White Blood Cell Count: 6,800 /uL, Platelets: 245,000 /uL.",
            file_path="uploads/FBC_Hemogram_Rohan.pdf",
            file_name="FBC_Hemogram_Rohan.pdf",
            file_size_kb=820,
            status="APPROVED",
            reviewer_id=malini.id,
            review_notes="Verified and authenticated.",
            reviewed_at=datetime(2026, 9, 16, 9, 0, tzinfo=timezone.utc),
            submitted_at=datetime(2026, 9, 15, 11, 30, tzinfo=timezone.utc)
        )

        db.session.add_all([r1, r2, r3, r4, r5, r6])
        db.session.commit()

        # 3. Doctor Access Permissions
        # Amara grants access to Dr. Bandara (Cardiologist)
        acc1 = DoctorAccess(
            patient_id=amara.id,
            doctor_id=dr_bandara.id,
            is_active=True,
            access_notes="Authorized for ongoing Cardiology follow-up and statin titration (14 days remaining)",
            duration_days=30,
            granted_at=datetime(2026, 10, 16, 10, 0, tzinfo=timezone.utc)
        )

        # Rohan grants access to Dr. Kavindi Jayasinghe
        acc2 = DoctorAccess(
            patient_id=rohan.id,
            doctor_id=dr_kavindi.id,
            is_active=True,
            access_notes="Authorized for general medical evaluation",
            duration_days=60,
            granted_at=datetime(2026, 9, 20, 8, 30, tzinfo=timezone.utc)
        )

        db.session.add_all([acc1, acc2])
        db.session.commit()

        # 4. Consultation Summary
        sum1 = ConsultationSummary(
            patient_id=amara.id,
            title="Pre-Consultation Summary: Cardiology Follow-Up Visit",
            chief_complaint="Experiencing occasional palpitations after new lipid medication; bringing recent HbA1c, Lipid Profile, and ECG for review.",
            selected_record_ids=json.dumps([r1.id, r2.id, r3.id]),
            created_at=datetime(2026, 10, 18, 15, 30, tzinfo=timezone.utc)
        )
        db.session.add(sum1)
        db.session.commit()

        # 5. Realistic Seed Audit Logs
        logs = [
            AuditLog(actor_id=admin.id, patient_id=None, action="SYSTEM_INITIALIZATION", details="PHRMS core system initialized with 256-bit encryption and role matrix.", timestamp=datetime(2026, 8, 1, 8, 0, tzinfo=timezone.utc)),
            AuditLog(actor_id=amara.id, patient_id=amara.id, action="RECORD_SUBMITTED", details="Patient submitted 'Comprehensive 12-Lead Electrocardiogram (ECG) Review'.", timestamp=datetime(2026, 8, 12, 16, 45, tzinfo=timezone.utc)),
            AuditLog(actor_id=malini.id, patient_id=amara.id, action="RECORD_APPROVED", details="Registrar Malini Fernando approved record #3 (12-Lead ECG). Published to timeline.", timestamp=datetime(2026, 8, 13, 11, 0, tzinfo=timezone.utc)),
            AuditLog(actor_id=amara.id, patient_id=amara.id, action="ACCESS_GRANTED", details="Patient Amara Perera granted clinical access to Dr. Nalin Bandara.", timestamp=datetime(2026, 10, 16, 10, 0, tzinfo=timezone.utc)),
            AuditLog(actor_id=amara.id, patient_id=amara.id, action="SUMMARY_GENERATED", details="Patient generated Consultation Summary #1 for Cardiology Follow-Up.", timestamp=datetime(2026, 10, 18, 15, 30, tzinfo=timezone.utc)),
            AuditLog(actor_id=dr_bandara.id, patient_id=amara.id, action="DOCTOR_VIEWED_TIMELINE", details="Dr. Nalin Bandara viewed clinical dossier and consultation summary for Amara Perera.", timestamp=datetime(2026, 10, 19, 14, 20, tzinfo=timezone.utc)),
            AuditLog(actor_id=malini.id, patient_id=amara.id, action="RECORD_CORRECTION_REQUESTED", details="Registrar requested clarification on obscured seal for record #5.", timestamp=datetime(2026, 10, 21, 10, 30, tzinfo=timezone.utc)),
            AuditLog(actor_id=amara.id, patient_id=amara.id, action="RECORD_SUBMITTED", details="Patient submitted 'Cardiac Ultrasound Echocardiogram Scan Report' into review queue.", timestamp=datetime(2026, 10, 26, 14, 10, tzinfo=timezone.utc)),
        ]
        db.session.add_all(logs)
        db.session.commit()

        print("PHRMS seeding completed successfully!")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    seed_database(app)
