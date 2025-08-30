import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, JobOffer, JobApplication

def test_flask_database():
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing Flask-SQLAlchemy operations...")
        
        # Test 1: Count existing offers
        offer_count = JobOffer.query.count()
        print(f"📋 Initial job offers: {offer_count}")
        
        # Test 2: Create a new offer
        try:
            new_offer = JobOffer(
                title="Test Flask Offer",
                company="Test Flask Company",
                description="This is a test offer created through Flask-SQLAlchemy"
            )
            
            db.session.add(new_offer)
            db.session.commit()
            print("✅ Flask offer created successfully!")
            print(f"   Offer ID: {new_offer.id}")
            
        except Exception as e:
            print(f"❌ Failed to create Flask offer: {e}")
            db.session.rollback()
            return False
        
        # Test 3: Verify the offer was saved
        verified_offer = JobOffer.query.get(new_offer.id)
        if verified_offer:
            print(f"✅ Offer verified in database: {verified_offer.title}")
        else:
            print("❌ Offer not found in database after creation!")
            return False
        
        # Test 4: Count offers again
        new_offer_count = JobOffer.query.count()
        print(f"📋 Job offers after creation: {new_offer_count}")
        
        # Test 5: Test applications
        app_count = JobApplication.query.count()
        print(f"📝 Initial applications: {app_count}")
        
        # Test 6: Create a test application
        try:
            new_app = JobApplication(
                full_name="Test User",
                email="test@example.com",
                job_title="Test Flask Offer",
                education_level="Bachelor's Degree"
            )
            
            db.session.add(new_app)
            db.session.commit()
            print("✅ Flask application created successfully!")
            
        except Exception as e:
            print(f"❌ Failed to create Flask application: {e}")
            db.session.rollback()
        
        return True

if __name__ == "__main__":
    test_flask_database()