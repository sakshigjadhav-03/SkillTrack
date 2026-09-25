from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from backend.database import query_db, execute_db
from backend.utils.decorators import login_required, role_required
from backend.services.outcome_id_service import lookup_by_outcome_id
from backend.services.skill_matcher import SkillMatcher

employer_bp = Blueprint('employer', __name__, url_prefix='/employer')

@employer_bp.route('/dashboard')
@login_required
@role_required('employer')
def dashboard():
    """Employer dashboard displaying pending verification requests, feedback, requirements, and history."""
    employer_id = session.get('employer_id')
    if not employer_id:
        emp = query_db("SELECT id, company_name FROM employers WHERE user_id = %s", (session.get('user_id'),), one=True)
        if emp:
            employer_id = emp['id']
            session['employer_id'] = emp['id']
            session['company_name'] = emp['company_name']
        else:
            emp = query_db("SELECT id, company_name FROM employers LIMIT 1", one=True)
            if emp:
                employer_id = emp['id']
                session['employer_id'] = emp['id']
                session['company_name'] = emp['company_name']
            else:
                employer_id = 1

    employer = query_db("SELECT * FROM employers WHERE id = %s", (employer_id,), one=True)
    if employer:
        v_status = employer.get('verification_status', 'verified')
        if v_status == 'pending':
            flash('Your account is awaiting Administrator verification. You will be able to access the dashboard after your account is verified.', 'warning')
            return redirect(url_for('auth.login', role='employer'))
        elif v_status == 'rejected':
            flash('Your account verification was rejected. Please contact the Administrator for further information.', 'danger')
            return redirect(url_for('auth.login', role='employer'))

    # Fetch all verification requests and records for this employer
    verifications = query_db(
        """
        SELECT 
            ev.*,
            t.id AS trainee_id,
            t.outcome_id,
            t.first_name,
            t.last_name,
            t.current_employment_status,
            c.course_name,
            tp.name AS provider_name,
            ef.technical_skills_rating,
            ef.communication_rating,
            ef.problem_solving_rating,
            ef.teamwork_rating,
            ef.missing_skills_text,
            ef.general_feedback,
            ef.feedback_date
        FROM employer_verifications ev
        JOIN trainees t ON ev.trainee_id = t.id
        LEFT JOIN training_records tr ON t.id = tr.trainee_id
        LEFT JOIN courses c ON tr.course_id = c.id
        LEFT JOIN training_providers tp ON tr.provider_id = tp.id
        LEFT JOIN employer_feedback ef ON ev.trainee_id = ef.trainee_id AND ef.employer_id = ev.employer_id
        WHERE ev.employer_id = %s
        ORDER BY 
            CASE WHEN ev.verification_status = 'pending' THEN 0 
                 WHEN ev.verification_status = 'correction_requested' THEN 1
                 WHEN ev.verification_status = 'verified' THEN 2 
                 ELSE 3 END,
            ev.id DESC
        """,
        (employer_id,)
    )

    # Segment verifications into relevant lifecycle buckets
    pending_requests = [v for v in verifications if v['verification_status'] == 'pending']
    verified_records = [v for v in verifications if v['verification_status'] == 'verified']
    correction_requests = [v for v in verifications if v['verification_status'] == 'correction_requested']
    unable_records = [v for v in verifications if v['verification_status'] in ('unable_to_verify', 'rejected')]
    feedback_submitted = [v for v in verifications if v.get('technical_skills_rating') is not None]

    # Aggregate reported missing workplace skills for this employer
    missing_skills_set = set()
    for v in verifications:
        if v.get('missing_skills_text'):
            for sk in v['missing_skills_text'].split(','):
                item = sk.strip()
                if item:
                    missing_skills_set.add(item)

    search_query = request.args.get('outcome_id', '').strip().upper()
    searched_trainee = None
    existing_verification = None

    if search_query:
        searched_trainee = lookup_by_outcome_id(search_query)
        if searched_trainee:
            existing_verification = query_db(
                "SELECT * FROM employer_verifications WHERE employer_id = %s AND trainee_id = %s",
                (employer_id, searched_trainee['trainee_id']),
                one=True
            )
        else:
            flash(f"Outcome ID '{search_query}' not found or trainee has not provided consent.", 'warning')

    return render_template(
        'employer/dashboard.html',
        employer=employer,
        verifications=verifications,
        pending_requests=pending_requests,
        verified_records=verified_records,
        correction_requests=correction_requests,
        unable_records=unable_records,
        feedback_submitted=feedback_submitted,
        missing_skills_list=sorted(list(missing_skills_set)),
        searched_trainee=searched_trainee,
        existing_verification=existing_verification,
        search_query=search_query
    )


@employer_bp.route('/verify', methods=['POST'])
@login_required
@role_required('employer')
def verify_trainee():
    """Processes employer verification actions: Confirm (Verify), Request Correction, or Unable to Verify."""
    employer_id = session.get('employer_id')
    outcome_id = request.form.get('outcome_id', '').strip().upper()
    action = request.form.get('action') or request.form.get('verification_status', 'verified')
    verified_role = request.form.get('verified_role', '').strip() or 'Associate Trainee'
    verified_joining_date = request.form.get('verified_joining_date') or datetime.now().strftime('%Y-%m-%d')
    verified_salary_range = request.form.get('verified_salary_range', '').strip() or '₹18,000 - ₹22,000'
    remarks = request.form.get('remarks', '').strip()

    # Normalize action / status
    if action in ('confirm', 'verified'):
        final_status = 'verified'
    elif action in ('correction', 'correction_requested'):
        final_status = 'correction_requested'
        if not remarks:
            remarks = 'Correction requested on candidate designation or joining date details.'
    elif action in ('unable', 'unable_to_verify', 'rejected'):
        final_status = 'unable_to_verify'
        if not remarks:
            remarks = 'Candidate records could not be verified on enterprise rolls.'
    else:
        final_status = 'verified'

    trainee = lookup_by_outcome_id(outcome_id)
    if not trainee:
        flash('Invalid Outcome ID.', 'danger')
        return redirect(url_for('employer.dashboard'))

    trainee_id = trainee['trainee_id']
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Record or update verification
    existing = query_db(
        "SELECT id FROM employer_verifications WHERE employer_id = %s AND trainee_id = %s",
        (employer_id, trainee_id),
        one=True
    )

    if existing:
        execute_db(
            """
            UPDATE employer_verifications 
            SET verification_status = %s, verified_role = %s, verified_joining_date = %s,
                verified_salary_range = %s, remarks = %s, verified_at = %s
            WHERE id = %s
            """,
            (final_status, verified_role, verified_joining_date, verified_salary_range, remarks, now_str, existing['id'])
        )
    else:
        token = f"EV-{outcome_id.split('-')[-1] if '-' in outcome_id else outcome_id}"
        execute_db(
            """
            INSERT INTO employer_verifications (
                employer_id, trainee_id, outcome_id, verification_status, verified_role,
                verified_joining_date, verified_salary_range, remarks, verified_at, token
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (employer_id, trainee_id, outcome_id, final_status, verified_role, verified_joining_date, verified_salary_range, remarks, now_str, token)
        )

    # If confirmed verified, update trainee employment status to 'employed'
    if final_status == 'verified':
        execute_db(
            "UPDATE trainees SET current_employment_status = 'employed' WHERE id = %s",
            (trainee_id,)
        )
        flash(f"Employment verified ✓ for {outcome_id}! Badge: Employment Verified. You can now provide workplace skill feedback.", 'success')
        return redirect(url_for('employer.feedback', outcome_id=outcome_id))
    elif final_status == 'correction_requested':
        flash(f"Correction request submitted for candidate {outcome_id}. Feedback logged for Training Provider.", 'info')
        return redirect(url_for('employer.dashboard') + '#verification-history')
    else:
        flash(f"Status recorded as 'Unable to Verify' for candidate {outcome_id}.", 'warning')
        return redirect(url_for('employer.dashboard') + '#verification-history')


@employer_bp.route('/feedback/<outcome_id>', methods=['GET', 'POST'])
@login_required
@role_required('employer')
def feedback(outcome_id):
    """Submits workplace competency ratings and missing skills requirements."""
    employer_id = session.get('employer_id')
    clean_id = outcome_id.strip().upper()
    trainee = lookup_by_outcome_id(clean_id)

    if not trainee:
        flash('Trainee not found.', 'danger')
        return redirect(url_for('employer.dashboard'))

    trainee_id = trainee['trainee_id']

    if request.method == 'POST':
        tech = request.form.get('technical_skills_rating', type=int) or 4
        comm = request.form.get('communication_rating', type=int) or 4
        prob = request.form.get('problem_solving_rating', type=int) or 3
        team = request.form.get('teamwork_rating', type=int) or 4
        prac = request.form.get('practical_skills_rating', type=int) or 4
        digi = request.form.get('digital_skills_rating', type=int) or 3
        read = request.form.get('industry_readiness_rating', type=int) or 4
        missing_skills = request.form.get('missing_skills_text', '').strip()
        general = request.form.get('general_feedback', '').strip()

        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert or update feedback
        existing = query_db(
            "SELECT id FROM employer_feedback WHERE employer_id = %s AND trainee_id = %s",
            (employer_id, trainee_id),
            one=True
        )

        if existing:
            execute_db(
                """
                UPDATE employer_feedback
                SET technical_skills_rating = %s, communication_rating = %s, problem_solving_rating = %s,
                    teamwork_rating = %s, practical_skills_rating = %s, digital_skills_rating = %s,
                    industry_readiness_rating = %s, missing_skills_text = %s, general_feedback = %s, feedback_date = %s
                WHERE id = %s
                """,
                (tech, comm, prob, team, prac, digi, read, missing_skills, general, now_str, existing['id'])
            )
        else:
            execute_db(
                """
                INSERT INTO employer_feedback (
                    employer_id, trainee_id, technical_skills_rating, communication_rating, problem_solving_rating,
                    teamwork_rating, practical_skills_rating, digital_skills_rating, industry_readiness_rating,
                    missing_skills_text, general_feedback, feedback_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (employer_id, trainee_id, tech, comm, prob, team, prac, digi, read, missing_skills, general, now_str)
            )

        flash(f"Workplace skill feedback and employer requirements recorded for {clean_id}! These updates directly inform SkillTrack's Skill Gap Analysis.", 'success')
        return redirect(url_for('employer.dashboard') + '#skill-feedback')

    # Load existing feedback if any
    existing_feedback = query_db(
        "SELECT * FROM employer_feedback WHERE employer_id = %s AND trainee_id = %s",
        (employer_id, trainee_id),
        one=True
    )

    return render_template(
        'employer/feedback.html',
        trainee=trainee,
        feedback=existing_feedback,
        outcome_id=clean_id
    )


@employer_bp.route('/skill-requirements', methods=['POST'])
@login_required
@role_required('employer')
def submit_skill_requirements():
    """Submits workplace skill requirements and deficiencies that feed into Skill Gap Analysis."""
    employer_id = session.get('employer_id')
    missing_skills = request.form.get('missing_skills_text', '').strip()
    notes = request.form.get('general_feedback', '').strip()

    if not missing_skills:
        flash('Please specify at least one skill requirement or deficiency.', 'warning')
        return redirect(url_for('employer.dashboard') + '#skill-requirements')

    # Associate with first verified trainee for this employer or default
    first_v = query_db("SELECT trainee_id FROM employer_verifications WHERE employer_id = %s LIMIT 1", (employer_id,), one=True)
    trainee_id = first_v['trainee_id'] if first_v else 1
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    existing = query_db("SELECT id FROM employer_feedback WHERE employer_id = %s AND trainee_id = %s", (employer_id, trainee_id), one=True)
    if existing:
        execute_db(
            "UPDATE employer_feedback SET missing_skills_text = %s, general_feedback = %s, feedback_date = %s WHERE id = %s",
            (missing_skills, notes, now_str, existing['id'])
        )
    else:
        execute_db(
            """
            INSERT INTO employer_feedback (
                employer_id, trainee_id, technical_skills_rating, communication_rating, problem_solving_rating,
                teamwork_rating, practical_skills_rating, digital_skills_rating, industry_readiness_rating,
                missing_skills_text, general_feedback, feedback_date
            ) VALUES (%s, %s, 4, 4, 4, 4, 4, 3, 4, %s, %s, %s)
            """,
            (employer_id, trainee_id, missing_skills, notes, now_str)
        )

    flash("Workplace skill requirements successfully saved! SkillTrack's Skill Gap Analysis has integrated your requirements.", 'success')
    return redirect(url_for('employer.dashboard') + '#skill-requirements')
