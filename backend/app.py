from flask import Flask, render_template, jsonify, request, session
from routes.pages import pages_bp
from routes.api import api_bp
from models import db, User, JobOffer, JobApplication,JobCandidats,Interview
import os
from datetime import datetime
from flask_cors import CORS

def create_app():
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    CORS(app)  # Add this line
    # Configuration
    app.config['SECRET_KEY'] = 'selectiq-secret-key-2024-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True  # This will show SQL queries in console
    
    # Session configuration
    app.config['SESSION_COOKIE_NAME'] = 'selectiq_session'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
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
        db.create_all()
        create_admin_user()
        create_default_job_offers()
    
    return app

def create_admin_user():
    """Create admin user if it doesn't exist"""
    try:
        admin_email = "hazemturki66@gmail.com"
        admin_password = "selectiqin@123"
        
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
            
            print(f"✅ Admin user created successfully: {admin_email}")
            print(f"   Password set to: {admin_password}")
            
            # Verify the password was set correctly
            verified = admin.check_password(admin_password)
            print(f"   Password verification: {verified}")
            
        else:
            print(f"ℹ️ Admin user already exists: {admin_email}")
            
            # Verify the password is correct
            password_correct = admin.check_password(admin_password)
            print(f"   Password verification: {password_correct}")
            
            if not password_correct:
                print("⚠️  Admin password is incorrect! Resetting...")
                admin.set_password(admin_password)
                db.session.commit()
                print("✅ Admin password reset successfully")
                
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()

def create_default_job_offers():
    """Create default job offers if none exist"""
    try:
        offer_count = JobOffer.query.count()
        print(f"📋 Current job offers in database: {offer_count}")
        
        if offer_count == 0:
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
            print(f"📊 Total offers now: {JobOffer.query.count()}")
        else:
            print(f"ℹ️ Job offers already exist: {offer_count} offers")
            
    except Exception as e:
        print(f"❌ Error creating default job offers: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()

if __name__ == '__main__':
    app = create_app()
    
    # Test database connection
    with app.app_context():
        print("🧪 Testing database connection...")
        try:
            offers = JobOffer.query.all()
            print(f"✅ Database connected. Job offers: {len(offers)}")
            
            users = User.query.all()
            print(f"✅ Users in database: {len(users)}")
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
    
    app.run(debug=True, port=5000)
# Add this to app.py (temporary solution)
# In app.py - Add this function
def create_missing_tables():
    with app.app_context():
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        # Create job_candidates table if it doesn't exist
        if 'job_candidates' not in existing_tables:
            print("🛠️ Creating missing job_candidates table...")
            JobCandidats.__table__.create(db.engine)
            print("✅ job_candidates table created successfully")
        else:
            print("✅ job_candidates table already exists")

# Call this function after db.create_all()
with app.app_context():
    db.create_all()
    create_admin_user()
    create_default_job_offers()
    create_missing_tables()  # Add this line
    create_interview_table()
    check_database_tables()  # Verify tables
def create_interview_table():
    """Create interview table if it doesn't exist"""
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'interviews' not in existing_tables:
                print("🛠️ Creating missing interview table...")
                # Drop the table if it exists with wrong schema
                db.engine.execute('DROP TABLE IF EXISTS interview')
                db.session.commit()
                
                # Create the table with correct schema
                Interview.__table__.create(db.engine)
                print("✅ interview table created successfully")
                
                # Add a sample interview for testing
                from datetime import datetime, time
                sample_interview = Interview(
                    candidate_name="John Doe",
                    interview_date=datetime.now().date(),
                    interview_time=time(14, 30),  # 2:30 PM
                    interviewer="Sarah Johnson",
                    interview_type="Online",
                    status="Scheduled"
                )
                db.session.add(sample_interview)
                db.session.commit()
                print("✅ Sample interview added")
            else:
                print("✅ interview table already exists")
                
                # Verify the table structure
                columns = inspector.get_columns('interview')
                print("📋 Interview table columns:")
                for column in columns:
                    print(f"  - {column['name']}: {column['type']}")
                    
        except Exception as e:
            print(f"❌ Error creating interview table: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
