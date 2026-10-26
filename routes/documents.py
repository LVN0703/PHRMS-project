import os
from flask import Blueprint, render_template, send_file, abort, current_app

from models import db, HealthRecord, DoctorAccess, User
from auth import login_required, get_current_user

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')

@documents_bp.route('/preview/<int:record_id>')
@login_required
def preview_document(record_id):
    current_user = get_current_user()
    record = db.get_or_404(HealthRecord, record_id)
    patient = db.get_or_404(User, record.patient_id)
    
    # Permission verification
    is_patient_owner = (current_user.id == record.patient_id)
    is_reviewer = (current_user.role == 'REVIEWER')
    is_admin = (current_user.role == 'ADMIN')
    is_authorized_doctor = False
    
    if current_user.role == 'DOCTOR':
        # Check active consent
        grant = DoctorAccess.query.filter_by(
            patient_id=record.patient_id,
            doctor_id=current_user.id,
            is_active=True
        ).first()
        if grant and record.status == 'APPROVED':
            is_authorized_doctor = True

    if not (is_patient_owner or is_reviewer or is_admin or is_authorized_doctor):
        abort(403)
        
    return render_template(
        'documents/preview.html',
        record=record,
        patient=patient,
        current_user=current_user
    )

@documents_bp.route('/download/<int:record_id>')
@login_required
def download_document(record_id):
    current_user = get_current_user()
    record = HealthRecord.query.get_or_404(record_id)
    
    # Permission verification
    is_patient_owner = (current_user.id == record.patient_id)
    is_reviewer = (current_user.role == 'REVIEWER')
    is_admin = (current_user.role == 'ADMIN')
    is_authorized_doctor = False
    
    if current_user.role == 'DOCTOR':
        grant = DoctorAccess.query.filter_by(
            patient_id=record.patient_id,
            doctor_id=current_user.id,
            is_active=True
        ).first()
        if grant and record.status == 'APPROVED':
            is_authorized_doctor = True

    if not (is_patient_owner or is_reviewer or is_admin or is_authorized_doctor):
        abort(403)
        
    if record.file_path:
        full_path = os.path.join(current_app.root_path, 'static', record.file_path)
        if os.path.exists(full_path):
            return send_file(full_path, as_attachment=True, download_name=record.file_name or 'document.pdf')
            
    # Fallback to preview if no physical file on disk
    return preview_document(record_id)
