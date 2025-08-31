from flask import Flask, render_template, jsonify, request, session
from routes.pages import pages_bp
from routes.api import api_bp
from models import db, User, JobOffer, JobApplication, JobCandidats, Interview
import os
from datetime import datetime
from flask_cors import CORS

def create_app():
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # ✅ FIXED: Configuration for Render
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'selectiq-secret-key-2024-change-in-production')
    
    # ✅ FIXED: Database configuration for Render
    if os.environ.get('DATABASE_URL'):
        # Use Render's database URL if available
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
    else:
        # Fallback to SQLite for local development
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False  # ✅ Disable in production
    
    # ✅ FIXED: Session configuration for production
    app.config['SESSION_COOKIE_NAME'] = 'selectiq_session'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = True  # ✅ Enable for HTTPS
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # ✅ FIXED: Initialize CORS properly
    CORS(app, origins=[
        "https://script.google.com",
        "https://*.google.com",
        "https://*.googleusercontent.com"
    ])
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Add error handling for database operations
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
    
    # Create admin user and default data
    with app.app_context():
        try:
            db.create_all()
            create_admin_user()
            create_default_job_offers()
            create_missing_tables()
            print("✅ Database initialization complete")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            import traceback
            traceback.print_exc()
    
    return app

def create_admin_user():
    """Create admin user if it doesn't exist"""
    try:
        admin_email = os.environ.get('ADMIN_EMAIL', 'hazemturki66@gmail.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'selectiqin@123')
        
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            print(f"👤 Creating admin user: {admin_email}")
            
            admin = User(
                username="admin",
                email=admin_email
            )
            admin.set_password(admin_password)
            
            db.session.add(admin)
            db.session.commit()
            
            print(f"✅ Admin user created successfully")
            
        else:
            print(f"ℹ️ Admin user already exists")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.session.rollback()

def create_default_job_offers():
    """Create default job offers if none exist"""
    try:
        if JobOffer.query.count() == 0:
            default_offers = [
                JobOffer(
                    title="Développeur Frontend React",
                    company="CodingCity Inc.",
                    description="Opportunité pour un développeur frontend passionné par React et les interfaces modernes."
                ),
                JobOffer(
                    title="Data Analyst Junior",
                    company="DataLab",
                    description="Poste pour analyste débutant avec compétences en Python et visualisation de données."
                ),
                JobOffer(
                    title="Ingénieur IA",
                    company="AI Corp",
                    description="Recherche ingénieur en intelligence artificielle avec expérience en machine learning."
                )
            ]
            
            for offer in default_offers:
                db.session.add(offer)
            
            db.session.commit()
            print("✅ Default job offers created")
            
    except Exception as e:
        print(f"❌ Error creating default job offers: {e}")
        db.session.rollback()

def create_missing_tables():
    """Create missing tables if they don't exist"""
    try:
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        # Create missing tables
        if 'job_candidates' not in existing_tables:
            JobCandidats.__table__.create(db.engine)
            print("✅ Created job_candidates table")
            
        if 'interview' not in existing_tables:
            Interview.__table__.create(db.engine)
            print("✅ Created interview table")
            
    except Exception as e:
        print(f"❌ Error creating missing tables: {e}")

# ✅ FIXED: Remove duplicate code and fix execution logic
if __name__ == '__main__':
    app = create_app()
    
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)  # ✅ debug=False for production
