from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import query_db, execute_db
from backend.services.outcome_id_service import generate_outcome_id

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login supporting email & password or quick 1-click demo login."""
    if request.method == 'POST':
        # Check if 1-click demo login or quick company email was clicked
        quick_role = request.form.get('quick_role')
        quick_email = request.form.get('quick_email')
        if quick_email:
            user = query_db("SELECT * FROM users WHERE email = %s AND is_active = 1", (quick_email,), one=True)
            if user:
                return _setup_session_and_redirect(user)
            flash('Demo company account not found.', 'danger')
            return redirect(url_for('auth.login'))

        if quick_role:
            role_emails = {
                'trainee': 'trainee@skilltrack.in',
                'employer': 'employer@tcs.in',
                'provider': 'provider@maharashtra-skills.org',
                'government': 'admin@skilltrack.gov.in'
            }
            email = role_emails.get(quick_role)
            user = query_db("SELECT * FROM users WHERE email = %s AND is_active = 1", (email,), one=True)
            if user:
                return _setup_session_and_redirect(user)
            flash('Demo user not found. Please initialize the database first.', 'danger')
            return redirect(url_for('auth.login'))

        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please provide both email and password.', 'warning')
            return render_template('login.html')

        user = query_db("SELECT * FROM users WHERE email = %s AND is_active = 1", (email,), one=True)
        if user and check_password_hash(user['password_hash'], password):
            return _setup_session_and_redirect(user)
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')


def _setup_session_and_redirect(user):
    """Sets session data and redirects to the appropriate role-based dashboard."""
    session.clear()
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['email'] = user['email']
    session['role'] = user['role']

    # Attach role-specific entity IDs
    if user['role'] == 'trainee':
        trainee = query_db("SELECT id, outcome_id, consent_status FROM trainees WHERE user_id = %s", (user['id'],), one=True)
        if trainee:
            session['trainee_id'] = trainee['id']
            session['outcome_id'] = trainee['outcome_id']
            session['consent_status'] = trainee['consent_status']
        return redirect(url_for('trainee.dashboard'))

    elif user['role'] == 'employer':
        employer = query_db("SELECT id, company_name FROM employers WHERE user_id = %s", (user['id'],), one=True)
        if employer:
            session['employer_id'] = employer['id']
            session['company_name'] = employer['company_name']
        return redirect(url_for('employer.dashboard'))

    elif user['role'] == 'provider':
        provider = query_db("SELECT id, name FROM training_providers WHERE user_id = %s", (user['id'],), one=True)
        if provider:
            session['provider_id'] = provider['id']
            session['provider_name'] = provider['name']
        return redirect(url_for('provider.dashboard'))

    elif user['role'] in ('government', 'admin'):
        return redirect(url_for('government.dashboard'))

    return redirect(url_for('index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Trainee self-registration with optional LinkedIn profile."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        gender = request.form.get('gender', 'Other')
        district_id = request.form.get('district_id', type=int) or 1
        phone = request.form.get('phone', '').strip()
        linkedin_url = request.form.get('linkedin_url', '').strip()

        # Validate LinkedIn URL if provided
        if linkedin_url and not ('linkedin.com/' in linkedin_url.lower()):
            flash('Please provide a valid LinkedIn URL (e.g. https://www.linkedin.com/in/username).', 'warning')
            districts = query_db("SELECT id, name FROM districts ORDER BY name")
            return render_template('register.html', districts=districts)

        if not username or not email or not password or not first_name:
            flash('Please fill in all required fields.', 'warning')
            districts = query_db("SELECT id, name FROM districts ORDER BY name")
            return render_template('register.html', districts=districts)

        # Check existing user
        existing = query_db("SELECT id FROM users WHERE email = %s OR username = %s", (email, username), one=True)
        if existing:
            flash('Username or email is already registered. Please login.', 'danger')
            return redirect(url_for('auth.login'))

        # Create user
        pwd_hash = generate_password_hash(password)
        res_u = execute_db(
            "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, 'trainee')",
            (username, email, pwd_hash)
        )
        user_id = res_u['lastrowid']

        # Generate unique outcome ID
        outcome_id = generate_outcome_id()

        # Create trainee profile
        execute_db(
            """
            INSERT INTO trainees (
                user_id, outcome_id, first_name, last_name, gender, phone, email, district_id,
                linkedin_url, consent_status, current_employment_status, identity_token, identity_verified
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', 'unemployed', %s, 1)
            """,
            (user_id, outcome_id, first_name, last_name, gender, phone, email, district_id, linkedin_url, f"DEMO-ID-{outcome_id.split('-')[-1]}")
        )

        flash(f'Registration successful! Your Unique Outcome ID is {outcome_id}. Please log in to provide tracking consent.', 'success')
        return redirect(url_for('auth.login'))

    districts = query_db("SELECT id, name FROM districts ORDER BY name")
    return render_template('register.html', districts=districts)


@auth_bp.route('/register-employer', methods=['GET', 'POST'])
def register_employer():
    """Employer / Enterprise Partner self-registration (Prototype Demo Account)."""
    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        company_email = request.form.get('company_email', '').strip().lower()
        industry = request.form.get('industry', '').strip()
        district_id = request.form.get('district_id', type=int) or 1
        contact_person = request.form.get('contact_person', '').strip()
        designation = request.form.get('designation', '').strip()
        password = request.form.get('password', '')

        if not company_name or not company_email or not password or not contact_person:
            flash('Please complete all required employer registration fields.', 'warning')
            districts = query_db("SELECT id, name FROM districts ORDER BY name")
            return render_template('register_employer.html', districts=districts)

        # Check existing user
        existing = query_db("SELECT id FROM users WHERE email = %s", (company_email,), one=True)
        if existing:
            flash('This corporate email is already registered. Please log in directly.', 'danger')
            return redirect(url_for('auth.login'))

        # Create employer user account
        username = 'emp_' + company_email.split('@')[0].replace('.', '_').replace('-', '_')
        pwd_hash = generate_password_hash(password)
        res_u = execute_db(
            "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, 'employer')",
            (username, company_email, pwd_hash)
        )
        user_id = res_u['lastrowid']

        # Create employer enterprise record
        execute_db(
            """
            INSERT INTO employers (
                user_id, company_name, industry, district_id, contact_person, contact_email, phone, is_verified
            ) VALUES (%s, %s, %s, %s, %s, %s, '+91 20 66000000', 1)
            """,
            (user_id, company_name, industry, district_id, f"{contact_person} ({designation})" if designation else contact_person, company_email)
        )

        flash(f'Prototype Employer Account for "{company_name}" created successfully! Please sign in.', 'success')
        return redirect(url_for('auth.login'))

    districts = query_db("SELECT id, name FROM districts ORDER BY name")
    return render_template('register_employer.html', districts=districts)


@auth_bp.route('/logout')
def logout():
    """Logs the user out and clears session."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/api/auth/me')
def me():
    """API endpoint returning active session status."""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user_id': session.get('user_id'),
            'username': session.get('username'),
            'role': session.get('role'),
            'outcome_id': session.get('outcome_id')
        })
    return jsonify({'authenticated': False}), 401
