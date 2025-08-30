from flask import Blueprint, request, jsonify
from models import db, JobApplication
import requests

forms_bp = Blueprint('forms', __name__)

@forms_bp.route('/google-forms-callback', methods=['POST'])
def google_forms_callback():
    try:
        # This would receive data from Google Forms webhook
        # You need to set up Google Forms to send data to this endpoint
        data = request.get_json()
        
        print(f"📋 Google Forms submission: {data}")
        
        # Extract data from Google Forms response
        # This depends on your form structure
        form_data = {
            'full_name': data.get('entry.877086558', ''),  # Replace with actual field IDs
            'email': data.get('entry.1498135098', ''),
            'job_title': data.get('entry.1424661284', ''),
            'education_level': data.get('entry.920170201', ''),
            'cv_url': data.get('entry.1082753663', '')
        }
        
        # Create or update application
        application_id = request.args.get('app_id')
        if application_id:
            # Update existing application
            application = JobApplication.query.get(application_id)
            if application:
                application.full_name = form_data['full_name']
                application.email = form_data['email']
                application.education_level = form_data['education_level']
                application.status = 'completed'
                application.cv_url = form_data['cv_url']
        else:
            # Create new application
            application = JobApplication(
                full_name=form_data['full_name'],
                email=form_data['email'],
                job_title=form_data['job_title'],
                education_level=form_data['education_level'],
                status='completed',
                cv_url=form_data['cv_url']
            )
            db.session.add(application)
        
        db.session.commit()
        
        return jsonify({'success': True, 'application_id': application.id})
        
    except Exception as e:
        print(f"❌ Google Forms callback error: {e}")
        return jsonify({'error': 'Failed to process form submission'}), 500