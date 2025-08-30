from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class JobOffer(db.Model):
    __tablename__ = 'job_offer'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

# In models.py - Ensure JobApplication model exists
class JobApplication(db.Model):
    __tablename__ = 'job_application'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    education_level = db.Column(db.String(200))
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cv_url = db.Column(db.String(500))
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'job_title': self.job_title,
            'education_level': self.education_level,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'cv_url': self.cv_url,
            'date': self.created_at.strftime('%d/%m/%Y'),
            'time': self.created_at.strftime('%H:%M')
        }
# In models.py - Add this JobCandidats model
class JobCandidats(db.Model):
    __tablename__ = 'job_candidates'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'job_title': self.job_title,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
class Interview(db.Model):
    __tablename__ = 'interview'
    
    id = db.Column(db.Integer, primary_key=True)
    candidate_name = db.Column(db.String(200), nullable=False)
    interview_date = db.Column(db.Date, nullable=False)
    interview_time = db.Column(db.Time, nullable=False)
    interviewer = db.Column(db.String(200), nullable=False)
    interview_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='Scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Add this field for comments
    comments = db.Column(db.Text, default='')
    
    def to_dict(self):
        return {
            'id': self.id,
            'candidate_name': self.candidate_name,
            'interview_date': self.interview_date.isoformat() if self.interview_date else '',
            'interview_time': self.interview_time.strftime('%H:%M') if self.interview_time else '',
            'interviewer': self.interviewer,
            'interview_type': self.interview_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else '',
            'comments': self.comments  # Include comments in the response
        }