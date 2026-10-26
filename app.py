import os
from flask import Flask, render_template
from models import db
from auth import auth_bp
from routes.patient import patient_bp
from routes.reviewer import reviewer_bp
from routes.doctor import doctor_bp
from routes.summary import summary_bp
from routes.admin import admin_bp
from routes.documents import documents_bp
from seed import seed_database

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Base configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'phrms-mis4500-capstone-secret-key-2026'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///phrms.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=25 * 1024 * 1024,  # 25 MB max upload
    )

    if test_config is not None:
        app.config.update(test_config)

    # Ensure uploads directory exists
    uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(reviewer_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(summary_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(documents_bp)

    # Home route
    @app.route('/')
    def index():
        return render_template('index.html')

    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    # Auto-seed database if empty on launch
    with app.app_context():
        seed_database(app)

    return app

if __name__ == '__main__':
    app = create_app()
    print("=" * 70)
    print("  PHRMS - Personal Health Record Management & Sharing System")
    print("  MIS 4500 Technology Capstone Project (Fall 2026)")
    print("  Running locally on http://127.0.0.1:5000")
    print("=" * 70)
    app.run(debug=True, port=5000)
