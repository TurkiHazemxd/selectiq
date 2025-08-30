from flask import Blueprint, request, jsonify, session
from models import db, User, JobOffer, JobApplication,JobCandidats,Interview
from werkzeug.security import check_password_hash
from datetime import datetime
import json  # Add this import

api_bp = Blueprint('api', __name__)

# Authentication endpoints
@api_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        print(f"🔐 Login attempt received")
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            session.permanent = True
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict()
            })
        
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500
@api_bp.route('/job-offers', methods=['POST'])
def create_job_offer():
    print("=" * 50)
    print("🎯 CREATE JOB OFFER ENDPOINT CALLED")
    print("=" * 50)
    
    # Debug session and headers
    print(f"🔐 Session: {dict(session)}")
    print(f"📋 Headers: {dict(request.headers)}")
    print(f"🌐 Method: {request.method}")
    print(f"🔗 URL: {request.url}")
    
    # Check authentication
    if 'user_id' not in session:
        print("❌ Unauthorized: User not logged in")
        return jsonify({'error': 'Unauthorized'}), 401
    
    print(f"✅ User authenticated: {session.get('user_id')}")
    
    try:
        # Get request data
        print("📦 Getting request JSON...")
        data = request.get_json()
        print(f"✅ Received data: {data}")
        
        if not data:
            print("❌ No data provided")
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['title', 'company', 'description']
        print(f"🔍 Checking required fields: {required_fields}")
        
        missing_fields = []
        for field in required_fields:
            field_value = data.get(field, '')
            print(f"   {field}: '{field_value}' (type: {type(field_value)})")
            if not field_value or not str(field_value).strip():
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
        
        print("✅ All required fields present")
        
        # Create the job offer
        print("🛠️ Creating JobOffer object...")
        offer = JobOffer(
            title=str(data['title']).strip(),
            company=str(data['company']).strip(),
            description=str(data['description']).strip()
        )
        
        print(f"📝 Offer object created: {offer.title} at {offer.company}")
        
        # Add to database
        print("💾 Adding to database session...")
        db.session.add(offer)
        print("✅ Added to session")
        
        print("💾 Committing to database...")
        db.session.commit()
        print(f"✅ Database commit successful - Offer ID: {offer.id}")
        
        result = offer.to_dict()
        print(f"✅ Returning result: {result}")
        
        return jsonify(result), 201
        
    except Exception as e:
        print("❌ EXCEPTION OCCURRED:")
        print(f"🔧 Error type: {type(e).__name__}")
        print(f"🔧 Error message: {str(e)}")
        print("📋 Full traceback:")
        import traceback
        traceback.print_exc()
        
        db.session.rollback()
        print("✅ Database transaction rolled back")
        
        return jsonify({'error': 'Failed to create job offer'}), 500
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR creating job offer: {str(e)}")
        print(f"🔧 Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()  # This will show the full error traceback
        return jsonify({'error': 'Failed to create job offer'}), 500

@api_bp.route('/job-offers', methods=['GET'])
def get_job_offers():
    try:
        offers = JobOffer.query.filter_by(is_active=True).order_by(JobOffer.created_at.desc()).all()
        return jsonify([offer.to_dict() for offer in offers])
    except Exception as e:
        print(f"❌ Error getting job offers: {e}")
        return jsonify({'error': 'Failed to get job offers'}), 500

# Job applications endpoints - CRITICAL FOR YOUR ISSUE
@api_bp.route('/applications', methods=['POST'])
def create_application():
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            data = request.get_json()
            print(f"📝 Creating application (attempt {attempt + 1}): {data}")
            
            # Validate required fields
            required_fields = ['full_name', 'email', 'job_title']
            missing_fields = []
            for field in required_fields:
                if field not in data or not str(data.get(field, '')).strip():
                    missing_fields.append(field)
            
            if missing_fields:
                return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
            
            # Create and save the application
            application = JobApplication(
                full_name=str(data['full_name']).strip(),
                email=str(data['email']).strip(),
                job_title=str(data['job_title']).strip(),
                education_level=str(data.get('education_level', '')).strip(),
                cv_url=str(data.get('cv_url', '')).strip(),
                status=data.get('status', 'pending')
            )
            
            db.session.add(application)
            db.session.commit()  # This is where the lock happens
            
            print(f"✅ Application created successfully: ID {application.id}")
            return jsonify({
                'success': True,
                'message': 'Application created successfully',
                'application': application.to_dict()
            }), 201
            
        except OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                print(f"🔄 Database locked, retrying in {retry_delay}s...")
                db.session.rollback()
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                db.session.rollback()
                print(f"❌ Database error after {max_retries} attempts: {e}")
                return jsonify({'error': 'Database busy, please try again'}), 503
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating application: {e}")
            return jsonify({'error': 'Failed to create application'}), 500
            
@api_bp.route('/applications', methods=['GET'])
def get_applications():
    #if 'user_id' not in session:
    #    return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        applications = JobApplication.query.order_by(JobApplication.created_at.desc()).all()
        return jsonify([app.to_dict() for app in applications])
    except Exception as e:
        print(f"❌ Error getting applications: {e}")
        return jsonify({'error': 'Failed to get applications'}), 500

# Other necessary endpoints
@api_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@api_bp.route('/check-auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({'authenticated': True, 'user': user.to_dict()})
    return jsonify({'authenticated': False})

@api_bp.route('/dashboard-stats', methods=['GET'])
def dashboard_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        total_offers = JobOffer.query.count()
        total_applications = JobApplication.query.count()
        pending_applications = JobApplication.query.filter_by(status='pending').count()
        interview_applications = JobApplication.query.filter_by(status='interview').count()
        
        return jsonify({
            'total_offers': total_offers,
            'total_applications': total_applications,
            'pending_applications': pending_applications,
            'interview_applications': interview_applications
        })
    except Exception as e:
        print(f"❌ Error getting dashboard stats: {e}")
        return jsonify({'error': 'Failed to get dashboard stats'}), 500
@api_bp.route('/job-offers/<int:id>', methods=['PUT'])
def update_job_offer(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        offer = JobOffer.query.get_or_404(id)
        data = request.get_json()
        
        offer.title = data.get('title', offer.title)
        offer.company = data.get('company', offer.company)
        offer.description = data.get('description', offer.description)
        
        db.session.commit()
        return jsonify(offer.to_dict())
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating job offer: {e}")
        return jsonify({'error': 'Failed to update job offer'}), 500

@api_bp.route('/job-offers/<int:id>', methods=['DELETE'])
def delete_job_offer(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        offer = JobOffer.query.get_or_404(id)
        db.session.delete(offer)
        db.session.commit()
        
        return jsonify({'message': 'Job offer deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error deleting job offer: {e}")
        return jsonify({'error': 'Failed to delete job offer'}), 500
# api.py - Add this new route
# In your api.py - ensure this endpoint works correctly
@api_bp.route('/google-form-submission', methods=['POST'])
def google_form_submission():
    try:
        data = request.get_json()
        print(f"Google Form submission received: {data}")
        
        # Create application in database
        application = JobApplication(
            full_name=data.get('full_name', ''),
            email=data.get('email', ''),
            job_title=data.get('job_title', ''),
            education_level=data.get('education_level', ''),
            cv_url=data.get('cv_url', ''),
            status='pending'
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Application received successfully',
            'application_id': application.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error processing submission: {e}")
        return jsonify({'error': 'Failed to process application'}), 500
# In api.py - Add these routes for candidates
@api_bp.route('/candidates', methods=['GET'])
def get_candidates():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        candidates = JobCandidats.query.order_by(JobCandidats.created_at.desc()).all()
        return jsonify([candidate.to_dict() for candidate in candidates])
    except Exception as e:
        print(f"❌ Error getting candidates: {e}")
        return jsonify({'error': 'Failed to get candidates'}), 500

@api_bp.route('/candidates', methods=['POST'])
def create_candidate():
    try:
        data = request.get_json()
        print(f"📝 Creating candidate with data: {data}")
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'job_title']
        missing_fields = []
        for field in required_fields:
            if field not in data or not str(data.get(field, '')).strip():
                missing_fields.append(field)
        
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
        
        # Check if candidate already exists
        existing_candidate = JobCandidats.query.filter_by(
            email=data['email'],
            job_title=data['job_title']
        ).first()
        
        if existing_candidate:
            return jsonify({
                'success': True,
                'message': 'Candidate already exists',
                'candidate': existing_candidate.to_dict()
            }), 200
        
        # Create and save the candidate
        candidate = JobCandidats(
            full_name=str(data['full_name']).strip(),
            email=str(data['email']).strip(),
            job_title=str(data['job_title']).strip(),
            status=data.get('status', 'pending')
        )
        
        db.session.add(candidate)
        db.session.commit()
        
        print(f"✅ Candidate created successfully: ID {candidate.id} - {candidate.full_name}")
        return jsonify({
            'success': True,
            'message': 'Candidate created successfully',
            'candidate': candidate.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating candidate: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to create candidate', 'details': str(e)}), 500

# In api.py - Update the delete_application endpoint
@api_bp.route('/applications/<application_identifier>', methods=['DELETE'])
def delete_application(application_identifier):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Try to find by ID first (if it's a number)
        if application_identifier.isdigit():
            application = JobApplication.query.get_or_404(int(application_identifier))
        else:
            # If it's not a number, try to find by email
            application = JobApplication.query.filter_by(email=application_identifier).first()
            if not application:
                return jsonify({'error': 'Application not found'}), 404
        
        db.session.delete(application)
        db.session.commit()
        
        return jsonify({'message': 'Application deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error deleting application: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to delete application'}), 500
# Add to api.py
@api_bp.route('/interviews', methods=['GET'])
def get_interviews():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Check if interview table exists
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'interview' not in tables:
            print("ℹ️ Interview table doesn't exist yet - returning empty array")
            return jsonify([])  # Return empty array instead of error
        
        # Try to query the table
        interviews = Interview.query.order_by(Interview.interview_date.desc()).all()
        
        # Convert to list of dictionaries
        interviews_list = []
        for interview in interviews:
            interviews_list.append({
                'id': interview.id,
                'candidate_name': interview.candidate_name,
                'interview_date': interview.interview_date.isoformat() if interview.interview_date else '',
                'interview_time': interview.interview_time.strftime('%H:%M') if interview.interview_time else '',
                'interviewer': interview.interviewer,
                'interview_type': interview.interview_type,
                'status': interview.status,
                'created_at': interview.created_at.isoformat() if interview.created_at else ''
            })
        
        return jsonify(interviews_list)
        
    except Exception as e:
        print(f"❌ Error getting interviews: {e}")
        import traceback
        traceback.print_exc()
        # Return empty array instead of error to prevent frontend issues
        return jsonify([])

@api_bp.route('/interviews', methods=['POST'])
def create_interview():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        print(f"📝 Creating interview with data: {data}")
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['candidate_name', 'interview_date', 'interview_time', 'interviewer', 'interview_type']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
        
        # Parse date and time
        try:
            interview_date = datetime.strptime(data['interview_date'], '%Y-%m-%d').date()
            interview_time = datetime.strptime(data['interview_time'], '%H:%M').time()
        except ValueError as e:
            return jsonify({'error': f'Invalid date or time format: {str(e)}'}), 400
        
        # Create interview
        interview = Interview(
            candidate_name=data['candidate_name'],
            interview_date=interview_date,
            interview_time=interview_time,
            interviewer=data['interviewer'],
            interview_type=data['interview_type'],
            status=data.get('status', 'Scheduled')
        )
        
        db.session.add(interview)
        db.session.commit()
        
        print(f"✅ Interview created successfully: ID {interview.id}")
        return jsonify({
            'success': True,
            'message': 'Interview created successfully',
            'interview': interview.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating interview: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to create interview', 'details': str(e)}), 500

@api_bp.route('/interviews/<int:id>', methods=['PUT'])
def update_interview(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        interview = Interview.query.get_or_404(id)
        data = request.get_json()
        
        interview.candidate_name = data.get('candidate_name', interview.candidate_name)
        interview.interview_date = datetime.strptime(data.get('interview_date', interview.interview_date.isoformat()), '%Y-%m-%d').date()
        interview.interview_time = datetime.strptime(data.get('interview_time', interview.interview_time.strftime('%H:%M')), '%H:%M').time()
        interview.interviewer = data.get('interviewer', interview.interviewer)
        interview.interview_type = data.get('interview_type', interview.interview_type)
        interview.status = data.get('status', interview.status)
        
        db.session.commit()
        
        return jsonify(interview.to_dict())
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating interview: {e}")
        return jsonify({'error': 'Failed to update interview'}), 500

@api_bp.route('/interviews/<int:id>', methods=['DELETE'])
def delete_interview(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        interview = Interview.query.get_or_404(id)
        db.session.delete(interview)
        db.session.commit()
        
        return jsonify({'message': 'Interview deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error deleting interview: {e}")
        return jsonify({'error': 'Failed to delete interview'}), 500
@api_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        print(f"🔐 Password reset request: {data}")
        
        email = data.get('email')
        new_password = data.get('newPassword')
        
        if not email or not new_password:
            return jsonify({'success': False, 'message': 'Email et nouveau mot de passe requis'}), 400
        
        # Find the user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ User not found: {email}")
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404
        
        # Update the password
        user.set_password(new_password)
        db.session.commit()
        
        print(f"✅ Password updated for user: {email}")
        return jsonify({'success': True, 'message': 'Mot de passe mis à jour avec succès'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error resetting password: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500
@api_bp.route('/interviews/<int:id>', methods=['GET'])
def get_interview(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        interview = Interview.query.get_or_404(id)
        return jsonify(interview.to_dict())
        
    except Exception as e:
        print(f"❌ Error getting interview: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to get interview'}), 500

@api_bp.route('/interviews/<int:id>/comments', methods=['GET'])
def get_interview_comments(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        interview = Interview.query.get_or_404(id)
        
        # Return the raw comment text
        comments = interview.comments or ""
        
        # Split by separator if it exists
        if "---\n" in comments:
            comment_list = comments.split("---\n")
        else:
            comment_list = [comments] if comments else []
        
        return jsonify({'comments': comment_list})
        
    except Exception as e:
        print(f"❌ Error getting interview comments: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to get comments'}), 500
@api_bp.route('/interviews/<int:id>/comments', methods=['POST'])
def add_interview_comment(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        comment_text = data.get('comment', '').strip()
        
        if not comment_text:
            return jsonify({'error': 'Comment cannot be empty'}), 400
        
        interview = Interview.query.get_or_404(id)
        
        # Store only the comment text, not JSON metadata
        if interview.comments:
            # Append new comment to existing ones with a separator
            interview.comments = interview.comments + "\n---\n" + comment_text
        else:
            # First comment
            interview.comments = comment_text
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Comment added successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error adding comment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to add comment'}), 500
@api_bp.route('/interviews/<int:id>/comments/<int:comment_index>', methods=['DELETE'])
def delete_interview_comment(id, comment_index):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        interview = Interview.query.get_or_404(id)
        
        if not interview.comments:
            return jsonify({'error': 'No comments found'}), 404
        
        # Split comments by separator
        comments = interview.comments.split("---\n")
        
        # Check if comment index is valid
        if comment_index < 0 or comment_index >= len(comments):
            return jsonify({'error': 'Invalid comment index'}), 400
        
        # Remove the comment at the specified index
        del comments[comment_index]
        
        # Join remaining comments back together
        interview.comments = "---\n".join(comments)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Comment deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error deleting comment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to delete comment'}), 500