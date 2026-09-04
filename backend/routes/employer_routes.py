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
    """Employer dashboard displaying search for Outcome ID and past verifications."""
    employer_id = session.get('employer_id')
    employer = query_db("SELECT * FROM employers WHERE id = %s", (employer_id,), one=True)

    # Fetch recent verifications performed by this employer
    verifications = query_db(
        """
        SELECT 
            ev.*,
            t.outcome_id,
            t.first_name,
            t.last_name,
            c.course_name,
            ef.technical_skills_rating,
            ef.missing_skills_text
        FROM employer_verifications ev
        JOIN trainees t ON ev.trainee_id = t.id
        LEFT JOIN training_records tr ON t.id = tr.trainee_id
        LEFT JOIN courses c ON tr.course_id = c.id
        LEFT JOIN employer_feedback ef ON ev.trainee_id = ef.trainee_id AND ef.employer_id = ev.employer_id
        WHERE ev.employer_id = %s
        ORDER BY ev.verified_at DESC
        """,
        (employer_id,)
    )

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
        searched_trainee=searched_trainee,
        existing_verification=existing_verification,
        search_query=search_query
    )


@employer_bp.route('/verify', methods=['POST'])
@login_required
@role_required('employer')
def verify_trainee():
    """Submits official employer verification for a trainee's Outcome ID."""
    employer_id = session.get('employer_id')
    outcome_id = request.form.get('outcome_id', '').strip().upper()
    status = request.form.get('verification_status', 'verified')
    verified_role = request.form.get('verified_role', '').strip()
    verified_joining_date = request.form.get('verified_joining_date')
    verified_salary_range = request.form.get('verified_salary_range', '').strip()
    remarks = request.form.get('remarks', '').strip()

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
            (status, verified_role, verified_joining_date, verified_salary_range, remarks, now_str, existing['id'])
        )
    else:
        execute_db(
            """
            INSERT INTO employer_verifications (
                employer_id, trainee_id, outcome_id, verification_status, verified_role,
                verified_joining_date, verified_salary_range, remarks, verified_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (employer_id, trainee_id, outcome_id, status, verified_role, verified_joining_date, verified_salary_range, remarks, now_str)
        )

    flash(f"Verification successfully submitted for {outcome_id}! Badge: Employment Verified ✓", 'success')
    return redirect(url_for('employer.feedback', outcome_id=outcome_id))


@employer_bp.route('/feedback/<outcome_id>', methods=['GET', 'POST'])
@login_required
@role_required('employer')
def feedback(outcome_id):
    """Submits 6-dimensional skill ratings and workplace missing skills feedback."""
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
        prac = request.form.get('practical_skills_rating', type=int) or 4
        prob = request.form.get('problem_solving_rating', type=int) or 3
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
                SET technical_skills_rating = %s, communication_rating = %s, practical_skills_rating = %s,
                    problem_solving_rating = %s, digital_skills_rating = %s, industry_readiness_rating = %s,
                    missing_skills_text = %s, general_feedback = %s, feedback_date = %s
                WHERE id = %s
                """,
                (tech, comm, prac, prob, digi, read, missing_skills, general, now_str, existing['id'])
            )
        else:
            execute_db(
                """
                INSERT INTO employer_feedback (
                    employer_id, trainee_id, technical_skills_rating, communication_rating, practical_skills_rating,
                    problem_solving_rating, digital_skills_rating, industry_readiness_rating,
                    missing_skills_text, general_feedback, feedback_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (employer_id, trainee_id, tech, comm, prac, prob, digi, read, missing_skills, general, now_str)
            )

        flash(f"Employer feedback and skill gap analysis recorded for {clean_id}!", 'success')
        return redirect(url_for('employer.dashboard'))

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
