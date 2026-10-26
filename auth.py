from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort, g
from models import db, User, AuditLog

auth_bp = Blueprint('auth', __name__)

def get_current_user():
    """Retrieve the currently authenticated user from session, or None."""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return db.session.get(User, user_id)

def login_user(user):
    """Store user in session."""
    session['user_id'] = user.id
    session['user_name'] = user.full_name
    session['user_role'] = user.role
    session['user_email'] = user.email

def logout_user():
    """Clear session data."""
    session.clear()

def log_audit(action, details, patient_id=None, actor_id=None):
    """Log an immutable audit entry."""
    if not actor_id:
        current = get_current_user()
        actor_id = current.id if current else 1
    
    log = AuditLog(
        actor_id=actor_id,
        patient_id=patient_id,
        action=action,
        details=details
    )
    db.session.add(log)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please authenticate to enter the clinical workspace.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('user_id'):
                flash('Please log in to access this workspace.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            user_role = session.get('user_role')
            if user_role not in allowed_roles and user_role != 'ADMIN':
                # Log unauthorized attempt for audit
                log_audit(
                    action='UNAUTHORIZED_ACCESS_ATTEMPT',
                    details=f'User role {user_role} attempted to access route {request.path} requiring {allowed_roles}',
                    actor_id=session.get('user_id')
                )
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            log_audit('USER_LOGIN', f'User {user.full_name} ({user.role}) logged in successfully.')
            flash(f'Welcome back, {user.full_name}! Authenticated as {user.role}.', 'success')
            
            # Role-based redirection
            if user.role == 'PATIENT':
                return redirect(url_for('patient.dashboard'))
            elif user.role == 'DOCTOR':
                return redirect(url_for('doctor.dashboard'))
            elif user.role == 'REVIEWER':
                return redirect(url_for('reviewer.workspace'))
            elif user.role == 'ADMIN':
                return redirect(url_for('admin.console'))
            return redirect(url_for('index'))
        else:
            flash('Invalid clinical credentials. Please verify your email and password.', 'error')
            
    # List pre-seeded demo personas for instant one-click login
    demo_users = User.query.order_by(User.id).all()
    return render_template('auth/login.html', demo_users=demo_users)

@auth_bp.route('/logout')
def logout():
    user = get_current_user()
    if user:
        log_audit('USER_LOGOUT', f'User {user.full_name} signed out.')
    logout_user()
    flash('You have been securely signed out of PHRMS.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/demo/switch/<role>')
def demo_switch(role):
    """Instant academic demo switcher: switches active session to a representative persona of the requested role."""
    role_upper = role.upper()
    user = User.query.filter_by(role=role_upper).first()
    
    if not user:
        flash(f'No demo user found for role: {role}', 'error')
        return redirect(url_for('auth.login'))
        
    login_user(user)
    log_audit('DEMO_ROLE_SWITCH', f'Academic demonstration switched session to {user.full_name} ({user.role}).')
    flash(f'Switched to {user.full_name} ({user.role}) for demonstration.', 'info')
    
    if user.role == 'PATIENT':
        return redirect(url_for('patient.dashboard'))
    elif user.role == 'DOCTOR':
        return redirect(url_for('doctor.dashboard'))
    elif user.role == 'REVIEWER':
        return redirect(url_for('reviewer.workspace'))
    elif user.role == 'ADMIN':
        return redirect(url_for('admin.console'))
    return redirect(url_for('index'))
