from flask import Blueprint, render_template, request, redirect, url_for, flash

from models import db, User, HealthRecord, DoctorAccess, AuditLog
from auth import login_required, role_required, get_current_user, log_audit

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Simulated global security policy lockdown flag
EMERGENCY_LOCKDOWN_ACTIVE = False

@admin_bp.route('/console')
@admin_bp.route('/dashboard')
@login_required
@role_required('ADMIN')
def console():
    admin = get_current_user()
    
    # User breakdown statistics
    total_users = User.query.count()
    patient_count = User.query.filter_by(role='PATIENT').count()
    doctor_count = User.query.filter_by(role='DOCTOR').count()
    reviewer_count = User.query.filter_by(role='REVIEWER').count()
    admin_count = User.query.filter_by(role='ADMIN').count()
    
    # Record statistics
    total_records = HealthRecord.query.count()
    approved_count = HealthRecord.query.filter_by(status='APPROVED').count()
    pending_count = HealthRecord.query.filter_by(status='PENDING').count()
    correction_count = HealthRecord.query.filter_by(status='CORRECTION_REQUIRED').count()
    rejected_count = HealthRecord.query.filter_by(status='REJECTED').count()
    
    # Active consents
    active_consents_count = DoctorAccess.query.filter_by(is_active=True).count()
    
    # Audit log inspection ledger (recent 50)
    audit_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(50).all()
    
    return render_template(
        'admin/console.html',
        admin=admin,
        total_users=total_users,
        patient_count=patient_count,
        doctor_count=doctor_count,
        reviewer_count=reviewer_count,
        admin_count=admin_count,
        total_records=total_records,
        approved_count=approved_count,
        pending_count=pending_count,
        correction_count=correction_count,
        rejected_count=rejected_count,
        active_consents_count=active_consents_count,
        audit_logs=audit_logs,
        lockdown_active=EMERGENCY_LOCKDOWN_ACTIVE
    )

@admin_bp.route('/toggle-lockdown', methods=['POST'])
@login_required
@role_required('ADMIN')
def toggle_lockdown():
    global EMERGENCY_LOCKDOWN_ACTIVE
    admin = get_current_user()
    EMERGENCY_LOCKDOWN_ACTIVE = not EMERGENCY_LOCKDOWN_ACTIVE
    
    state_str = "ENABLED" if EMERGENCY_LOCKDOWN_ACTIVE else "DISABLED"
    log_audit(
        action='GOVERNANCE_POLICY_LOCKDOWN',
        details=f"Admin {admin.full_name} set Emergency Institutional Policy Lock to {state_str}.",
        actor_id=admin.id
    )
    
    flash(f"Emergency Policy Lockdown is now {state_str}.", 'warning' if EMERGENCY_LOCKDOWN_ACTIVE else 'info')
    return redirect(url_for('admin.console'))
