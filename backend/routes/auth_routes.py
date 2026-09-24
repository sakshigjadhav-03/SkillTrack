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
                'government': 'provider@maharashtra-skills.org'  # Graceful fallback to provider intelligence
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
    """Multi-step New Trainee Registration Flow with Course & Provider connection."""
    from datetime import datetime

    def _get_registration_context():
        districts = query_db("SELECT id, name FROM districts ORDER BY name") or []
        providers = query_db("SELECT id, provider_code, name FROM training_providers ORDER BY name") or []
        courses = query_db("SELECT id, course_code, course_name, sector, duration_hours FROM courses ORDER BY course_name") or []
        skills = query_db("SELECT id, skill_name, category FROM skills ORDER BY category, skill_name") or []
        employers = query_db("SELECT id, company_name, industry FROM employers ORDER BY company_name") or []
        return {
            'districts': districts,
            'providers': providers,
            'courses': courses,
            'skills': skills,
            'employers': employers
        }

    if request.method == 'POST':
        # Step 1: Personal Information
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        dob = request.form.get('dob', '').strip() or None
        gender = request.form.get('gender', 'Other')
        country = request.form.get('country', 'India').strip()
        state = request.form.get('state', 'Maharashtra').strip()
        city = request.form.get('city', '').strip()
        district_id = request.form.get('district_id', type=int) or 1

        # Step 2: Education
        highest_education = request.form.get('highest_education', '').strip()
        field_of_study = request.form.get('field_of_study', '').strip()
        institution = request.form.get('institution', '').strip()
        graduation_year = request.form.get('graduation_year', type=int) or None

        # Step 3: Training Information
        provider_id = request.form.get('provider_id', type=int) or None
        course_id = request.form.get('course_id', type=int) or None
        training_start = request.form.get('training_start_date', '').strip() or datetime.now().strftime('%Y-%m-%d')
        training_end = request.form.get('training_completion_date', '').strip() or datetime.now().strftime('%Y-%m-%d')
        selected_skills = request.form.getlist('skills_learned')

        # Step 4: Employment Status
        raw_emp_status = request.form.get('employment_status', 'looking_for_employment').strip()
        status_mapping = {
            'employed': 'employed',
            'looking_for_employment': 'unemployed',
            'self_employed': 'self_employed',
            'further_training': 'further_education',
            'not_seeking': 'unemployed'
        }
        current_emp_status = status_mapping.get(raw_emp_status, 'unemployed')
        employer_name = request.form.get('employer_name', '').strip()
        employer_id = request.form.get('employer_id', type=int) or None
        job_role = request.form.get('job_role', '').strip()
        emp_location = request.form.get('employment_location', '').strip()
        emp_start_date = request.form.get('employment_start_date', '').strip() or datetime.now().strftime('%Y-%m-%d')
        salary_monthly = request.form.get('salary_monthly', type=float) or 0.0

        # Step 5: Account Creation
        username = request.form.get('username', '').strip()
        if not username:
            username = email.split('@')[0] if '@' in email else f"trainee_{int(datetime.now().timestamp())}"
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not first_name or not email or not password:
            flash('Please complete all required fields.', 'warning')
            return render_template('register.html', **_get_registration_context())

        if password != confirm_password:
            flash('Passwords do not match. Please verify your password.', 'danger')
            return render_template('register.html', **_get_registration_context())

        existing_user = query_db("SELECT id FROM users WHERE email = %s OR username = %s", (email, username), one=True)
        if existing_user:
            flash('An account with this email or username already exists. Please log in.', 'danger')
            return redirect(url_for('auth.login'))

        # 1. Create User Record
        pwd_hash = generate_password_hash(password)
        res_u = execute_db(
            "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, 'trainee')",
            (username, email, pwd_hash)
        )
        user_id = res_u['lastrowid']

        # 2. Generate Unique Permanent Outcome ID
        outcome_id = generate_outcome_id()
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 3. Create Trainee Profile
        res_t = execute_db(
            """
            INSERT INTO trainees (
                user_id, outcome_id, first_name, last_name, gender, dob, phone, email,
                district_id, country, state, city, highest_education, field_of_study, institution,
                graduation_year, consent_status, consent_date, consent_version,
                current_employment_status, identity_token, identity_verified
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'agreed', %s, 'v1.0', %s, %s, 1)
            """,
            (
                user_id, outcome_id, first_name, last_name, gender, dob, phone, email,
                district_id, country, state, city or 'Pune', highest_education, field_of_study, institution,
                graduation_year, now_str, current_emp_status, f"DEMO-ID-{outcome_id.split('-')[-1]}"
            )
        )
        trainee_id = res_t['lastrowid']

        # 4. Record Consent
        ip_addr = request.remote_addr or '127.0.0.1'
        execute_db(
            "INSERT INTO consents (trainee_id, consent_version, consent_given, ip_address, agreed_at) VALUES (%s, 'v1.0', 1, %s, %s)",
            (trainee_id, ip_addr, now_str)
        )

        # 5. Connect Training Provider & Course (Makes trainee visible in Provider's list)
        if course_id and provider_id:
            execute_db(
                """
                INSERT INTO training_records (
                    trainee_id, course_id, provider_id, start_date, completion_date,
                    certification_status, certificate_number, grade
                ) VALUES (%s, %s, %s, %s, %s, 'certified', %s, 'A')
                """,
                (trainee_id, course_id, provider_id, training_start, training_end, f"CERT-MH-{outcome_id.split('-')[-1]}")
            )

        # 6. Associate Selected Skills
        for sk in selected_skills:
            try:
                execute_db(
                    "INSERT INTO trainee_skills (trainee_id, skill_id, proficiency_level) VALUES (%s, %s, 'Intermediate')",
                    (trainee_id, int(sk))
                )
            except Exception:
                pass

        # 7. Record Employment if currently employed
        if current_emp_status == 'employed' and (employer_name or job_role):
            execute_db(
                """
                INSERT INTO employment_records (
                    trainee_id, employer_id, employer_name, job_role, employment_type,
                    joining_date, salary_monthly, location_district_id
                ) VALUES (%s, %s, %s, %s, 'Full-time', %s, %s, %s)
                """,
                (trainee_id, employer_id, employer_name or 'Hiring Enterprise', job_role or 'Associate', emp_start_date, salary_monthly or 18000.0, district_id)
            )

        # 8. Seed Longitudinal Follow-up Milestones
        for m in [3, 6, 12, 24]:
            is_comp = (m == 3 and current_emp_status == 'employed')
            status = 'completed' if is_comp else 'upcoming'
            ret_stat = 'retained' if (is_comp and current_emp_status == 'employed') else 'not_applicable'
            sal = salary_monthly if is_comp else 0.0
            execute_db(
                """
                INSERT INTO followups (
                    trainee_id, milestone_months, status, due_date, completed_date,
                    employment_status, current_salary, salary_growth_pct, retention_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, 0.0, %s)
                """,
                (trainee_id, m, status, training_end, training_end if is_comp else None, current_emp_status, sal, ret_stat)
            )

        # 9. Establish Session for Immediate Auto-Login to New Personal Profile
        session.clear()
        session['user_id'] = user_id
        session['username'] = username
        session['email'] = email
        session['role'] = 'trainee'
        session['trainee_id'] = trainee_id
        session['outcome_id'] = outcome_id
        session['consent_status'] = 'agreed'

        flash(f"Welcome to SkillTrack, {first_name}! Your personal profile has been created with Unique Outcome ID: {outcome_id}.", "success")
        return redirect(url_for('trainee.dashboard'))

    return render_template('register.html', **_get_registration_context())


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
