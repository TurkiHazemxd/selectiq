from flask import Blueprint, render_template, session, redirect, url_for

pages_bp = Blueprint('pages', __name__)

# Route for each HTML page
@pages_bp.route('/')
def index():
    return render_template('joboffers.html')

@pages_bp.route('/joboffers')
def joboffers():
    return render_template('joboffers.html')

@pages_bp.route('/login')
def login():
    return render_template('login.html')

@pages_bp.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')

@pages_bp.route('/dashboard')
def dashboard():
    # Check if user is authenticated
    if 'user_id' not in session:
        return redirect(url_for('pages.login'))
    return render_template('dashboard.html')

@pages_bp.route('/candidates')
def candidates():
    # Check if user is authenticated
    if 'user_id' not in session:
        return redirect(url_for('pages.login'))
    return render_template('candidates.html')

@pages_bp.route('/apps')
def apps():
    # Check if user is authenticated
    if 'user_id' not in session:
        return redirect(url_for('pages.login'))
    return render_template('apps.html')

# Add a catch-all route for your HTML files
@pages_bp.route('/<path:page_name>')
def serve_page(page_name):
    if page_name.endswith('.html'):
        return render_template(page_name)
    return redirect(url_for('pages.index'))
@pages_bp.route('/interviews')
def interviews():
    # Check if user is authenticated
    if 'user_id' not in session:
        return redirect(url_for('pages.login'))
    return render_template('s.html')  # or rename s.html to interviews.html