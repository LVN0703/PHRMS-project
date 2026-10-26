from flask import Blueprint, render_template, abort

from models import db, User, HealthRecord, DoctorAccess, ConsultationSummary
from auth import login_required, get_current_user, log_audit

summary_bp = Blueprint('summary', __name__, url_prefix='/summary')

@summary_bp.route('/<int:summary_id>')
@login_required
def view_summary(summary_id):
    current_user = get_current_user()
    summary = db.get_or_404(ConsultationSummary, summary_id)
    patient = db.get_or_404(User, summary.patient_id)
    
    # Check access permission
    is_owner = (current_user.id == patient.id)
    is_admin = (current_user.role == 'ADMIN')
    is_authorized_doctor = False
    
    if current_user.role == 'DOCTOR':
        grant = DoctorAccess.query.filter_by(
            patient_id=patient.id,
            doctor_id=current_user.id,
            is_active=True
        ).first()
        if grant:
            is_authorized_doctor = True
            
    if not (is_owner or is_admin or is_authorized_doctor):
        log_audit(
            action='UNAUTHORIZED_ACCESS_ATTEMPT',
            details=f"User {current_user.full_name} ({current_user.role}) denied access to Consultation Summary #{summary.id}.",
            patient_id=patient.id,
            actor_id=current_user.id
        )
        abort(403)
        
    records = summary.get_records()
    
    return render_template(
        'summary/sheet.html',
        summary=summary,
        patient=patient,
        records=records,
        current_user=current_user
    )
