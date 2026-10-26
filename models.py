import json
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False)  # 'PATIENT', 'REVIEWER', 'DOCTOR', 'ADMIN'
    
    # Doctor specific fields
    specialization = db.Column(db.String(120), nullable=True)
    slmc_reg_no = db.Column(db.String(50), nullable=True)  # Sri Lanka Medical Council Registration
    
    # Patient specific fields
    national_id = db.Column(db.String(50), nullable=True)  # NIC / Passport
    date_of_birth = db.Column(db.Date, nullable=True)
    blood_group = db.Column(db.String(10), nullable=True)
    known_allergies = db.Column(db.Text, nullable=True)
    primary_facility = db.Column(db.String(150), nullable=True)
    
    # Staff specific fields
    staff_id = db.Column(db.String(50), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    records = db.relationship('HealthRecord', backref='patient', foreign_keys='HealthRecord.patient_id', lazy='dynamic')
    reviewed_records = db.relationship('HealthRecord', backref='reviewer', foreign_keys='HealthRecord.reviewer_id', lazy='dynamic')
    summaries = db.relationship('ConsultationSummary', backref='patient', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'specialization': self.specialization,
            'national_id': self.national_id,
            'blood_group': self.blood_group,
            'known_allergies': self.known_allergies
        }


class HealthRecord(db.Model):
    __tablename__ = 'health_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(60), nullable=False)  # 'Lab Report', 'Prescription', 'Consultation Note', 'Imaging / Scan', 'Vaccination / Vitals'
    provider_name = db.Column(db.String(150), nullable=False)
    record_date = db.Column(db.Date, nullable=False, index=True)
    clinical_summary = db.Column(db.Text, nullable=False)
    
    # File attachment
    file_path = db.Column(db.String(255), nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    file_size_kb = db.Column(db.Integer, default=512)
    
    # Administrative state machine
    status = db.Column(db.String(30), default='PENDING', nullable=False, index=True)  # 'PENDING', 'APPROVED', 'CORRECTION_REQUIRED', 'REJECTED'
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    review_notes = db.Column(db.Text, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'title': self.title,
            'category': self.category,
            'provider_name': self.provider_name,
            'record_date': self.record_date.isoformat() if self.record_date else None,
            'clinical_summary': self.clinical_summary,
            'file_name': self.file_name,
            'status': self.status,
            'review_notes': self.review_notes,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None
        }


class DoctorAccess(db.Model):
    __tablename__ = 'doctor_access'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    access_notes = db.Column(db.String(255), nullable=True)
    duration_days = db.Column(db.Integer, default=30)
    
    granted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    revoked_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    patient_user = db.relationship('User', foreign_keys=[patient_id], backref='doctor_authorizations_given')
    doctor_user = db.relationship('User', foreign_keys=[doctor_id], backref='patient_authorizations_received')


class ConsultationSummary(db.Model):
    __tablename__ = 'consultation_summaries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    title = db.Column(db.String(150), nullable=False)
    chief_complaint = db.Column(db.Text, nullable=False)
    selected_record_ids = db.Column(db.Text, nullable=False)  # JSON-encoded array: "[1, 2, 4]"
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def get_selected_ids(self):
        try:
            return json.loads(self.selected_record_ids)
        except Exception:
            return []

    def get_records(self):
        ids = self.get_selected_ids()
        if not ids:
            return []
        return HealthRecord.query.filter(HealthRecord.id.in_(ids), HealthRecord.status == 'APPROVED').order_by(HealthRecord.record_date.desc()).all()


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    action = db.Column(db.String(100), nullable=False, index=True)
    details = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    actor = db.relationship('User', foreign_keys=[actor_id])
    patient = db.relationship('User', foreign_keys=[patient_id])
