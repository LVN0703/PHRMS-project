import os
import json
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from werkzeug.utils import secure_filename

from models import db, User, HealthRecord, DoctorAccess, ConsultationSummary, AuditLog
from auth import login_required, role_required, get_current_user, log_audit

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'dicom'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@patient_bp.route('/dashboard')
@login_required
@role_required('PATIENT')
def dashboard():
    patient = get_current_user()
    
    # Fetch all records for this patient
    all_records = HealthRecord.query.filter_by(patient_id=patient.id).order_by(HealthRecord.record_date.desc()).all()
    approved_records = [r for r in all_records if r.status == 'APPROVED']
    pending_records = [r for r in all_records if r.status == 'PENDING']
    correction_records = [r for r in all_records if r.status == 'CORRECTION_REQUIRED']
    rejected_records = [r for r in all_records if r.status == 'REJECTED']
    
    # Active doctor permissions
    active_doctor_grants = DoctorAccess.query.filter_by(patient_id=patient.id, is_active=True).all()
    
    # All registered doctors for the access directory
    all_doctors = User.query.filter_by(role='DOCTOR').order_by(User.full_name).all()
    granted_doctor_ids = {g.doctor_id for g in active_doctor_grants}
    
    # Existing consultation summaries
    summaries = ConsultationSummary.query.filter_by(patient_id=patient.id).order_by(ConsultationSummary.created_at.desc()).all()
    
    return render_template(
        'patient/dashboard.html',
        patient=patient,
        all_records=all_records,
        approved_records=approved_records,
        pending_records=pending_records,
        correction_records=correction_records,
        rejected_records=rejected_records,
        active_doctor_grants=active_doctor_grants,
        all_doctors=all_doctors,
        granted_doctor_ids=granted_doctor_ids,
        summaries=summaries
    )

@patient_bp.route('/records/new', methods=['POST'])
@login_required
@role_required('PATIENT')
def upload_record():
    patient = get_current_user()
    
    title = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()
    provider_name = request.form.get('provider_name', '').strip()
    record_date_str = request.form.get('record_date', '').strip()
    clinical_summary = request.form.get('clinical_summary', '').strip()
    
    if not (title and category and provider_name and record_date_str):
        flash('Please fill in all mandatory fields (Title, Category, Healthcare Provider, and Date).', 'error')
        return redirect(url_for('patient.dashboard'))
        
    try:
        record_date = datetime.strptime(record_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
        return redirect(url_for('patient.dashboard'))
        
    # Handle file upload
    file = request.files.get('file')
    saved_filename = None
    file_path = None
    file_size_kb = 350
    
    if file and file.filename != '':
        if allowed_file(file.filename):
            orig_filename = secure_filename(file.filename)
            timestamp_prefix = datetime.now().strftime('%Y%m%d%H%M%S')
            saved_filename = f"{timestamp_prefix}_{orig_filename}"
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            full_path = os.path.join(upload_dir, saved_filename)
            file.save(full_path)
            file_path = f"uploads/{saved_filename}"
            file_size_kb = max(1, round(os.path.getsize(full_path) / 1024))
        else:
            flash('Unsupported file type. Please upload a PDF, PNG, JPG, or DICOM document.', 'error')
            return redirect(url_for('patient.dashboard'))
    else:
        # If no file uploaded, assign a realistic simulated clinical document name
        saved_filename = f"CLINICAL_{category.replace(' ', '_').upper()}_{record_date.strftime('%Y%m%d')}.pdf"
        file_path = f"uploads/{saved_filename}"

    new_record = HealthRecord(
        patient_id=patient.id,
        title=title,
        category=category,
        provider_name=provider_name,
        record_date=record_date,
        clinical_summary=clinical_summary or f"Patient reported record from {provider_name}.",
        file_path=file_path,
        file_name=saved_filename,
        file_size_kb=file_size_kb,
        status='PENDING'
    )
    
    db.session.add(new_record)
    db.session.commit()
    
    log_audit(
        action='RECORD_SUBMITTED',
        details=f"Patient {patient.full_name} submitted document '{title}' ({category}) for administrative review.",
        patient_id=patient.id,
        actor_id=patient.id
    )
    
    flash(f"Document '{title}' submitted successfully! It is now queued for registrar review.", 'success')
    return redirect(url_for('patient.dashboard'))

@patient_bp.route('/records/<int:record_id>/resubmit', methods=['POST'])
@login_required
@role_required('PATIENT')
def resubmit_record(record_id):
    patient = get_current_user()
    record = db.get_or_404(HealthRecord, record_id)
    
    if record.patient_id != patient.id:
        abort(403)
        
    title = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()
    provider_name = request.form.get('provider_name', '').strip()
    record_date_str = request.form.get('record_date', '').strip()
    clinical_summary = request.form.get('clinical_summary', '').strip()
    
    if title: record.title = title
    if category: record.category = category
    if provider_name: record.provider_name = provider_name
    if record_date_str:
        try:
            record.record_date = datetime.strptime(record_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    if clinical_summary: record.clinical_summary = clinical_summary
    
    # Check for replacement file
    file = request.files.get('file')
    if file and file.filename != '' and allowed_file(file.filename):
        orig_filename = secure_filename(file.filename)
        timestamp_prefix = datetime.now().strftime('%Y%m%d%H%M%S')
        saved_filename = f"resubmit_{timestamp_prefix}_{orig_filename}"
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        full_path = os.path.join(upload_dir, saved_filename)
        file.save(full_path)
        record.file_path = f"uploads/{saved_filename}"
        record.file_name = saved_filename
        record.file_size_kb = max(1, round(os.path.getsize(full_path) / 1024))

    # Reset state to PENDING in accordance with Flowchart Figure 2
    record.status = 'PENDING'
    db.session.commit()
    
    log_audit(
        action='RECORD_RESUBMITTED',
        details=f"Patient {patient.full_name} addressed reviewer notes and resubmitted '{record.title}' (ID #{record.id}). Status reset to PENDING.",
        patient_id=patient.id,
        actor_id=patient.id
    )
    
    flash(f"Record '{record.title}' has been successfully updated and returned to the review queue.", 'success')
    return redirect(url_for('patient.dashboard'))

@patient_bp.route('/access', methods=['POST'])
@login_required
@role_required('PATIENT')
def toggle_doctor_access():
    patient = get_current_user()
    doctor_id = request.form.get('doctor_id', type=int)
    action = request.form.get('action', '').strip()  # 'grant' or 'revoke'
    access_notes = request.form.get('access_notes', '').strip()
    
    doctor = User.query.filter_by(id=doctor_id, role='DOCTOR').first_or_404()
    
    access_entry = DoctorAccess.query.filter_by(patient_id=patient.id, doctor_id=doctor.id).first()
    
    if action == 'grant':
        if not access_entry:
            access_entry = DoctorAccess(
                patient_id=patient.id,
                doctor_id=doctor.id,
                is_active=True,
                access_notes=access_notes or 'Authorized for clinical consultation & review'
            )
            db.session.add(access_entry)
        else:
            access_entry.is_active = True
            access_entry.access_notes = access_notes or access_entry.access_notes
            access_entry.granted_at = datetime.now(timezone.utc)
            access_entry.revoked_at = None
            
        log_audit(
            action='ACCESS_GRANTED',
            details=f"Patient {patient.full_name} GRANTED clinical record access to {doctor.full_name} ({doctor.specialization}).",
            patient_id=patient.id,
            actor_id=patient.id
        )
        flash(f"Clinical record access GRANTED to {doctor.full_name}.", 'success')
        
    elif action == 'revoke':
        if access_entry:
            access_entry.is_active = False
            access_entry.revoked_at = datetime.now(timezone.utc)
            
        log_audit(
            action='ACCESS_REVOKED',
            details=f"Patient {patient.full_name} REVOKED clinical record access from {doctor.full_name}.",
            patient_id=patient.id,
            actor_id=patient.id
        )
        flash(f"Clinical record access REVOKED from {doctor.full_name}.", 'warning')
        
    db.session.commit()
    return redirect(url_for('patient.dashboard'))

@patient_bp.route('/summary/new', methods=['POST'])
@login_required
@role_required('PATIENT')
def create_summary():
    patient = get_current_user()
    title = request.form.get('title', '').strip()
    chief_complaint = request.form.get('chief_complaint', '').strip()
    selected_ids = request.form.getlist('selected_records')
    
    if not (title and chief_complaint and selected_ids):
        flash('Please provide a Summary Title, Chief Complaint, and select at least one approved record.', 'error')
        return redirect(url_for('patient.dashboard'))
        
    # Verify that all selected records belong to patient and are approved
    valid_ids = [int(i) for i in selected_ids if i.isdigit()]
    verified_records = HealthRecord.query.filter(
        HealthRecord.id.in_(valid_ids),
        HealthRecord.patient_id == patient.id,
        HealthRecord.status == 'APPROVED'
    ).all()
    
    if not verified_records:
        flash('None of the selected records are approved or valid for summary compilation.', 'error')
        return redirect(url_for('patient.dashboard'))
        
    final_ids = [r.id for r in verified_records]
    
    summary = ConsultationSummary(
        patient_id=patient.id,
        title=title,
        chief_complaint=chief_complaint,
        selected_record_ids=json.dumps(final_ids)
    )
    
    db.session.add(summary)
    db.session.commit()
    
    log_audit(
        action='SUMMARY_GENERATED',
        details=f"Patient {patient.full_name} compiled Consultation-Ready Summary '{title}' with {len(final_ids)} records.",
        patient_id=patient.id,
        actor_id=patient.id
    )
    
    flash(f"Consultation Summary '{title}' compiled successfully! You can now view and print the briefing document.", 'success')
    return redirect(url_for('summary.view_summary', summary_id=summary.id))

@patient_bp.route('/audit-log')
@login_required
@role_required('PATIENT')
def audit_log():
    patient = get_current_user()
    # Fetch logs concerning this patient
    logs = AuditLog.query.filter(
        (AuditLog.patient_id == patient.id) | (AuditLog.actor_id == patient.id)
    ).order_by(AuditLog.timestamp.desc()).all()
    
    return render_template('patient/audit_log.html', patient=patient, logs=logs)
