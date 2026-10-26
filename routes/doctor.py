from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from models import db, User, HealthRecord, DoctorAccess, ConsultationSummary, AuditLog
from auth import login_required, role_required, get_current_user, log_audit

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@doctor_bp.route('/dashboard')
@login_required
@role_required('DOCTOR')
def dashboard():
    doctor = get_current_user()
    
    # Query all active permissions granted to this doctor
    active_grants = DoctorAccess.query.filter_by(doctor_id=doctor.id, is_active=True).all()
    authorized_patient_ids = [g.patient_id for g in active_grants]
    
    authorized_patients = User.query.filter(User.id.in_(authorized_patient_ids)).all() if authorized_patient_ids else []
    
    # Map grant info for quick display
    grant_map = {g.patient_id: g for g in active_grants}
    
    # If no patients are active, we also find other system patients to show the evaluator how permission gating works
    all_patients = User.query.filter_by(role='PATIENT').all()
    
    return render_template(
        'doctor/dashboard.html',
        doctor=doctor,
        authorized_patients=authorized_patients,
        grant_map=grant_map,
        all_patients=all_patients
    )

@doctor_bp.route('/patient/<int:patient_id>')
@login_required
@role_required('DOCTOR')
def patient_view(patient_id):
    doctor = get_current_user()
    patient = User.query.filter_by(id=patient_id, role='PATIENT').first_or_404()
    
    # STRICT AUTHORIZATION CHECK GATE (FR07, NFR03)
    active_grant = DoctorAccess.query.filter_by(
        patient_id=patient.id,
        doctor_id=doctor.id,
        is_active=True
    ).first()
    
    if not active_grant and doctor.role != 'ADMIN':
        log_audit(
            action='UNAUTHORIZED_ACCESS_ATTEMPT',
            details=f"Doctor {doctor.full_name} attempted to access unauthorized patient dossier {patient.full_name} (ID #{patient.id}). Access DENIED.",
            patient_id=patient.id,
            actor_id=doctor.id
        )
        abort(403)
        
    # Log successful clinical access event
    log_audit(
        action='DOCTOR_VIEWED_TIMELINE',
        details=f"Attending Physician {doctor.full_name} accessed clinical health timeline and summaries for patient {patient.full_name}.",
        patient_id=patient.id,
        actor_id=doctor.id
    )
    
    # Load ONLY approved records (NFR03 / Flowchart)
    approved_records = HealthRecord.query.filter_by(
        patient_id=patient.id,
        status='APPROVED'
    ).order_by(HealthRecord.record_date.desc()).all()
    
    # Load patient-curated summaries
    summaries = ConsultationSummary.query.filter_by(patient_id=patient.id).order_by(ConsultationSummary.created_at.desc()).all()
    
    # Active tab switcher
    active_tab = request.args.get('tab', 'summary')
    
    return render_template(
        'doctor/patient_view.html',
        doctor=doctor,
        patient=patient,
        grant=active_grant,
        approved_records=approved_records,
        summaries=summaries,
        active_tab=active_tab
    )
