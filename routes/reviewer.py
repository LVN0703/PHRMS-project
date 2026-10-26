from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from models import db, User, HealthRecord, AuditLog
from auth import login_required, role_required, get_current_user, log_audit

reviewer_bp = Blueprint('reviewer', __name__, url_prefix='/reviewer')

@reviewer_bp.route('/workspace')
@reviewer_bp.route('/dashboard')
@login_required
@role_required('REVIEWER')
def workspace():
    reviewer = get_current_user()
    
    # All pending submissions for the triage queue
    pending_queue = HealthRecord.query.filter_by(status='PENDING').order_by(HealthRecord.submitted_at.asc()).all()
    
    # Completed review history (recent 15)
    recent_reviews = HealthRecord.query.filter(HealthRecord.status.in_(['APPROVED', 'CORRECTION_REQUIRED', 'REJECTED']))\
        .order_by(HealthRecord.reviewed_at.desc()).limit(15).all()
    
    # Active item being inspected
    selected_id = request.args.get('select', type=int)
    active_record = None
    if selected_id:
        active_record = db.session.get(HealthRecord, selected_id)
    if not active_record and pending_queue:
        active_record = pending_queue[0]
        
    return render_template(
        'reviewer/workspace.html',
        reviewer=reviewer,
        pending_queue=pending_queue,
        recent_reviews=recent_reviews,
        active_record=active_record
    )

@reviewer_bp.route('/records/<int:record_id>/decide', methods=['POST'])
@login_required
@role_required('REVIEWER')
def decide_record(record_id):
    reviewer = get_current_user()
    record = db.get_or_404(HealthRecord, record_id)
    
    decision = request.form.get('decision', '').strip().upper()
    review_notes = request.form.get('review_notes', '').strip()
    
    if decision not in ['APPROVED', 'CORRECTION_REQUIRED', 'REJECTED']:
        flash('Invalid administrative decision type.', 'error')
        return redirect(url_for('reviewer.workspace'))
        
    if decision in ['CORRECTION_REQUIRED', 'REJECTED'] and not review_notes:
        flash('Mandatory reviewer notes are required when requesting correction or rejecting a document.', 'error')
        return redirect(url_for('reviewer.workspace', select=record.id))
        
    record.status = decision
    record.reviewer_id = reviewer.id
    record.review_notes = review_notes or 'Document verified and administratively approved.'
    record.reviewed_at = datetime.now(timezone.utc)
    
    db.session.commit()
    
    action_type = f"RECORD_{decision}"
    log_audit(
        action=action_type,
        details=f"Registrar {reviewer.full_name} actioned '{record.title}' (ID #{record.id}) to {decision}. Notes: {record.review_notes}",
        patient_id=record.patient_id,
        actor_id=reviewer.id
    )
    
    if decision == 'APPROVED':
        flash(f"Record '{record.title}' APPROVED! Added to patient chronological timeline.", 'success')
    elif decision == 'CORRECTION_REQUIRED':
        flash(f"Correction requested for '{record.title}'. Patient has been notified with instructions.", 'info')
    else:
        flash(f"Record '{record.title}' has been REJECTED and archived.", 'warning')
        
    return redirect(url_for('reviewer.workspace'))
