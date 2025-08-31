import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, time
from models import db, User, JobOffer, JobApplication, JobCandidats, Interview
from routes.pages import pages_bp
from routes.api import api_bp

def create_app():
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')
    CORS(app)

    # Secret key
    app.config['SECRET_KEY'] = 'selectiq-secret-key-2024-change-in-production'

    # Use Render PostgreSQL ONLY
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set! Cannot start app.")
    # Ensure correct prefix and SSL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    db_url += "?sslmode=require"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True  # Log SQL queries

    # Session config
    app.config['SESSION_COOKIE_NAME'] = 'selectiq_session'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Initialize DB
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    # Auto-create tables and default data
    with app.app_context():
        db.create_all()
        create_admin_user()
        create_default_job_offers()
        create_interview_table()

    # Debug route to see tables
    @app.route("/debug-tables")
    def debug_tables():
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        return jsonify({"tables": tables})

    return app


def create_admin_user():
    try:
        admin_email = "hazemturki66@gmail.com"
        admin_password = "selectiqin@123"

        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(username="admin", email=admin_email)
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Admin user created: {admin_email}")
        else:
            if not admin.check_password(admin_password):
                admin.set_password(admin_password)
                db.session.commit()
                print("✅ Admin password reset successfully")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.session.rollback()


def create_default_job_offers():
    try:
        if JobOffer.query.count() == 0:
            default_offers = [
                JobOffer(title="Développeur Frontend React",
                         company="CodingCity Inc.",
                         description="Opportunité pour un développeur frontend passionné par React et les interfaces modernes."),
                JobOffer(title="Data Analyst Junior",
                         company="DataLab",
                         description="Poste pour analyste débutant avec compétences en Python et visualisation de données."),
                JobOffer(title="Ingénieur IA",
                         company="AI Corp",
                         description="Recherche ingénieur en intelligence artificielle avec expérience en machine learning.")
            ]
            for offer in default_offers:
                db.session.add(offer)
            db.session.commit()
            print("✅ Default job offers created")
    except Exception as e:
        print(f"❌ Error creating default job offers: {e}")
        db.session.rollback()


def create_interview_table():
    try:
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        if 'interview' not in tables:
            Interview.__table__.create(db.engine)
            sample_interview = Interview(
                candidate_name="John Doe",
                interview_date=datetime.now().date(),
                interview_time=time(14, 30),
                interviewer="Sarah Johnson",
                interview_type="Online",
                status="Scheduled"
            )
            db.session.add(sample_interview)
            db.session.commit()
            print("✅ Interview table created with sample data")
    except Exception as e:
        print(f"❌ Error creating interview table: {e}")
        db.session.rollback()


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
