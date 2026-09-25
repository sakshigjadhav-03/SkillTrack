from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import query_db, execute_db
from backend.services.outcome_id_service import generate_outcome_id

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login requiring valid username/email and password."""
    selected_role = request.args.get('role', request.form.get('role', 'trainee')).lower()
    if selected_role not in ('trainee', 'provider', 'employer', 'administrator', 'admin'):
        selected_role = 'trainee'

    if request.method == 'POST':
        identifier = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not identifier or not password:
            flash('Please provide both username/email and password.', 'warning')
            return render_template('login.html', selected_role=selected_role)

        user = query_db(
            "SELECT * FROM users WHERE (email = %s OR username = %s) AND is_active = 1",
            (identifier, identifier),
            one=True
        )

        if user and check_password_hash(user['password_hash'], password):
            # Check verification status for Provider
            if user['role'] == 'provider':
                provider = query_db("SELECT id, verification_status FROM training_providers WHERE user_id = %s", (user['id'],), one=True)
                v_status = provider.get('verification_status', 'verified') if provider else 'verified'
                if v_status == 'pending':
                    flash('Your account is awaiting Administrator verification. You will be able to access the dashboard after your account is verified.', 'warning')
                    return render_template('login.html', selected_role=selected_role)
                elif v_status == 'rejected':
                    flash('Your account verification was rejected. Please contact the Administrator for further information.', 'danger')
                    return render_template('login.html', selected_role=selected_role)

            # Check verification status for Employer
            elif user['role'] == 'employer':
                employer = query_db("SELECT id, verification_status FROM employers WHERE user_id = %s", (user['id'],), one=True)
                v_status = employer.get('verification_status', 'verified') if employer else 'verified'
                if v_status == 'pending':
                    flash('Your account is awaiting Administrator verification. You will be able to access the dashboard after your account is verified.', 'warning')
                    return render_template('login.html', selected_role=selected_role)
                elif v_status == 'rejected':
                    flash('Your account verification was rejected. Please contact the Administrator for further information.', 'danger')
                    return render_template('login.html', selected_role=selected_role)

            return _setup_session_and_redirect(user)
        else:
            flash('Invalid username/email or password. Please try again.', 'danger')
            return render_template('login.html', selected_role=selected_role)

    return render_template('login.html', selected_role=selected_role)


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

    elif user['role'] in ('government', 'admin', 'administrator'):
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

        # Normalize and validate LinkedIn URL
        if linkedin_url:
            if not linkedin_url.startswith('http'):
                linkedin_url = 'https://' + linkedin_url
            if 'linkedin.com/' not in linkedin_url.lower():
                flash('Please provide a valid LinkedIn URL.', 'warning')
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
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'agreed', 'unemployed', %s, 1)
            """,
            (user_id, outcome_id, first_name, last_name, gender, phone, email, district_id, linkedin_url, f"DEMO-ID-{outcome_id.split('-')[-1]}")
        )

        user = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
        flash(f'Registration successful! Welcome, {first_name}. Your Outcome ID is {outcome_id}.', 'success')
        return _setup_session_and_redirect(user)

    districts = query_db("SELECT id, name FROM districts ORDER BY name")
    return render_template('register.html', districts=districts)


@auth_bp.route('/register-provider', methods=['GET', 'POST'])
def register_provider():
    """Training Provider registration with administrator verification workflow."""
    if request.method == 'POST':
        provider_name = request.form.get('provider_name', '').strip()
        registration_id = request.form.get('registration_id', '').strip()
        authorized_person = request.form.get('authorized_person', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        district_id = request.form.get('district_id', type=int) or 1
        state = request.form.get('state', 'Maharashtra').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not provider_name or not registration_id or not authorized_person or not email or not password:
            flash('Please fill in all required fields.', 'warning')
            districts = query_db("SELECT id, name FROM districts ORDER BY name")
            return render_template('register_provider.html', districts=districts)

        if password != confirm_password:
            flash('Passwords do not match. Please verify and try again.', 'danger')
            districts = query_db("SELECT id, name FROM districts ORDER BY name")
            return render_template('register_provider.html', districts=districts)

        # Check existing user / provider
        existing_user = query_db("SELECT id FROM users WHERE email = %s", (email,), one=True)
        existing_code = query_db("SELECT id FROM training_providers WHERE provider_code = %s", (registration_id,), one=True)
        if existing_user or existing_code:
            flash('This email address or Registration ID is already registered. Please log in.', 'danger')
            return redirect(url_for('auth.login', role='provider'))

        # Create provider user account
        username = 'prv_' + email.split('@')[0].replace('.', '_').replace('-', '_')
        u_count = 1
        base_username = username
        while query_db("SELECT id FROM users WHERE username = %s", (username,), one=True):
            username = f"{base_username}_{u_count}"
            u_count += 1

        pwd_hash = generate_password_hash(password)
        res_u = execute_db(
            "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, 'provider')",
            (username, email, pwd_hash)
        )
        user_id = res_u['lastrowid']

        # Create training_providers record with pending verification
        execute_db(
            """
            INSERT INTO training_providers (
                user_id, provider_code, name, authorized_person, district_id,
                address, state, contact_email, phone, rating, verification_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 4.0, 'pending')
            """,
            (user_id, registration_id, provider_name, authorized_person, district_id, address, state, email, phone)
        )

        flash('Registration successful. Your Training Provider account is pending Administrator verification.', 'success')
        return redirect(url_for('auth.login', role='provider'))

    districts = query_db("SELECT id, name FROM districts ORDER BY name")
    return render_template('register_provider.html', districts=districts)


@auth_bp.route('/register-employer', methods=['GET', 'POST'])
def register_employer():
    """Employer / Enterprise Partner self-registration with administrator verification workflow."""
    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        industry = request.form.get('industry', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        phone = request.form.get('phone', '').strip()
        company_email = request.form.get('company_email', '').strip().lower()
        registration_id = request.form.get('registration_id', '').strip()
        address = request.form.get('address', '').strip()
        state = request.form.get('state', 'Maharashtra').strip()
        district_id = request.form.get('district_id', type=int) or 1
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not company_name or not company_email or not password or not contact_person or not registration_id:
            flash('Please complete all required employer registration fields.', 'warning')
            districts = query_db("SELECT id, name FROM districts ORDER BY name")
            return render_template('register_employer.html', districts=districts)

        if password != confirm_password:
            flash('Passwords do not match. Please verify and try again.', 'danger')
            districts = query_db("SELECT id, name FROM districts ORDER BY name")
            return render_template('register_employer.html', districts=districts)

        # Check existing user
        existing = query_db("SELECT id FROM users WHERE email = %s", (company_email,), one=True)
        if existing:
            flash('This corporate email is already registered. Please log in directly.', 'danger')
            return redirect(url_for('auth.login', role='employer'))

        # Create employer user account
        username = 'emp_' + company_email.split('@')[0].replace('.', '_').replace('-', '_')
        u_count = 1
        base_username = username
        while query_db("SELECT id FROM users WHERE username = %s", (username,), one=True):
            username = f"{base_username}_{u_count}"
            u_count += 1

        pwd_hash = generate_password_hash(password)
        res_u = execute_db(
            "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, 'employer')",
            (username, company_email, pwd_hash)
        )
        user_id = res_u['lastrowid']

        # Create employer enterprise record with pending verification
        execute_db(
            """
            INSERT INTO employers (
                user_id, company_name, industry, district_id, contact_person,
                contact_email, phone, address, state, registration_id, is_verified, verification_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, 'pending')
            """,
            (user_id, company_name, industry, district_id, contact_person, company_email, phone, address, state, registration_id)
        )

        flash('Registration successful. Your Employer account is pending Administrator verification.', 'success')
        return redirect(url_for('auth.login', role='employer'))

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
