from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from backend.database import query_db, execute_db
from backend.utils.decorators import login_required, role_required
from backend.services.outcome_id_service import lookup_by_outcome_id
from backend.services.skill_matcher import SkillMatcher

trainee_bp = Blueprint('trainee', __name__, url_prefix='/trainee')

@trainee_bp.route('/dashboard')
@login_required
@role_required('trainee')
def dashboard():
    """Trainee home dashboard displaying Outcome ID, consent status, profile, and timeline."""
    trainee_id = session.get('trainee_id')
    trainee = query_db(
        """
        SELECT 
            t.*,
            d.name AS district_name,
            c.course_name,
            c.sector,
            c.duration_hours,
            c.description AS course_description,
            tp.name AS provider_name,
            tr.start_date AS training_start,
            tr.completion_date AS training_end,
            tr.certification_status,
            tr.certificate_number,
            tr.grade
        FROM trainees t
        LEFT JOIN districts d ON t.district_id = d.id
        LEFT JOIN training_records tr ON t.id = tr.trainee_id
        LEFT JOIN courses c ON tr.course_id = c.id
        LEFT JOIN training_providers tp ON tr.provider_id = tp.id
        WHERE t.id = %s
        """,
        (trainee_id,),
        one=True
    )

    if not trainee:
        flash('Trainee profile not found.', 'danger')
        return redirect(url_for('auth.logout'))

    # If consent has not been given, redirect to consent page
    if trainee['consent_status'] != 'agreed':
        return redirect(url_for('trainee.consent'))

    # Retrieve skills acquired
    skills = query_db(
        """
        SELECT s.skill_name, s.category, ts.proficiency_level
        FROM trainee_skills ts
        JOIN skills s ON ts.skill_id = s.id
        WHERE ts.trainee_id = %s
        """,
        (trainee_id,)
    )

    # Retrieve active employment record
    employment = query_db(
        """
        SELECT er.*, d.name AS location_name, e.company_name AS registered_employer
        FROM employment_records er
        LEFT JOIN districts d ON er.location_district_id = d.id
        LEFT JOIN employers e ON er.employer_id = e.id
        WHERE er.trainee_id = %s
        ORDER BY er.id DESC LIMIT 1
        """,
        (trainee_id,),
        one=True
    )

    # Retrieve follow-ups
    followups = query_db(
        "SELECT * FROM followups WHERE trainee_id = %s ORDER BY milestone_months ASC",
        (trainee_id,)
    )

    # Retrieve employer verification status
    verification = query_db(
        """
        SELECT ev.*, e.company_name
        FROM employer_verifications ev
        JOIN employers e ON ev.employer_id = e.id
        WHERE ev.trainee_id = %s
        ORDER BY ev.id DESC LIMIT 1
        """,
        (trainee_id,),
        one=True
    )

    # Retrieve employer feedback & skill gaps
    feedback = query_db(
        """
        SELECT ef.*, e.company_name
        FROM employer_feedback ef
        JOIN employers e ON ef.employer_id = e.id
        WHERE ef.trainee_id = %s
        ORDER BY ef.id DESC LIMIT 1
        """,
        (trainee_id,),
        one=True
    )

    # Skill Relevance Calculation
    curriculum_skills = [s['skill_name'] for s in skills] if skills else ['Basic Excel', 'Data Entry', 'Communication']
    workplace_skills = []
    if feedback and feedback.get('missing_skills_text'):
        workplace_skills.extend(feedback['missing_skills_text'].split(','))
    if employment and employment.get('skills_used_text'):
        workplace_skills.extend(employment['skills_used_text'].split(','))

    relevance_data = SkillMatcher.calculate_relevance(curriculum_skills, workplace_skills)

    # Build Outcome Timeline Events
    timeline_events = _build_timeline(trainee, followups, employment, verification)

    return render_template(
        'trainee/dashboard.html',
        trainee=trainee,
        skills=skills,
        employment=employment,
        followups=followups,
        verification=verification,
        feedback=feedback,
        relevance=relevance_data,
        timeline=timeline_events
    )


def _build_timeline(trainee, followups, employment, verification):
    """Constructs sequential milestone events for the Outcome Timeline."""
    events = [
        {
            'stage': 'Training Started',
            'status': 'completed',
            'date': trainee.get('training_start') or '2023-05-01',
            'title': f"Enrolled in {trainee.get('course_name') or 'Vocational Training'}",
            'badge': 'Enrolled'
        },
        {
            'stage': 'Training Completed',
            'status': 'completed',
            'date': trainee.get('training_end') or '2023-08-15',
            'title': f"Course Completed ({trainee.get('duration_hours', 240)} Hours)",
            'badge': 'Completed'
        },
        {
            'stage': 'Certification',
            'status': 'completed' if trainee.get('certification_status') == 'certified' else 'in_progress',
            'date': trainee.get('training_end') or '2023-08-20',
            'title': f"Certified (Grade {trainee.get('grade', 'A')}) — Certificate #{trainee.get('certificate_number', 'CERT-MH')}",
            'badge': 'Certified'
        }
    ]

    # Milestones (3, 6, 12 months)
    milestones_map = {f['milestone_months']: f for f in followups}
    for m in [3, 6, 12]:
        f_rec = milestones_map.get(m)
        if f_rec:
            sal_text = f"₹{int(f_rec['current_salary']):,}/mo" if f_rec.get('current_salary') else "N/A"
            growth_text = f" (+{f_rec['salary_growth_pct']}%)" if f_rec.get('salary_growth_pct') else ""
            events.append({
                'stage': f"{m} Month Follow-up",
                'status': 'completed',
                'date': f_rec.get('completed_date') or f_rec.get('due_date'),
                'title': f"Status: {f_rec['employment_status'].replace('_', ' ').title()} — Salary: {sal_text}{growth_text}",
                'badge': 'Verified' if f_rec['retention_status'] == 'retained' else 'At Risk',
                'badge_class': 'success' if f_rec['retention_status'] == 'retained' else 'warning'
            })
        else:
            events.append({
                'stage': f"{m} Month Follow-up",
                'status': 'upcoming',
                'date': 'Scheduled',
                'title': f"{m}-Month Post-Training Livelihood Review",
                'badge': 'Upcoming',
                'badge_class': 'secondary'
            })

    # Employer Verification Badge
    if verification and verification['verification_status'] == 'verified':
        events.append({
            'stage': 'Employer Verified',
            'status': 'completed',
            'date': str(verification.get('verified_at', ''))[:10],
            'title': f"Verified by {verification.get('company_name', 'Employer')} ✓",
            'badge': 'Employment Verified ✓',
            'badge_class': 'primary'
        })

    return events


@trainee_bp.route('/consent', methods=['GET', 'POST'])
@login_required
@role_required('trainee')
def consent():
    """Informed consent collection page before post-training tracking begins."""
    trainee_id = session.get('trainee_id')
    if request.method == 'POST':
        action = request.form.get('consent_action')
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ip_addr = request.remote_addr or '127.0.0.1'

        if action == 'agree':
            execute_db(
                "UPDATE trainees SET consent_status = 'agreed', consent_date = %s, consent_version = 'v1.0' WHERE id = %s",
                (now_str, trainee_id)
            )
            execute_db(
                "INSERT INTO consents (trainee_id, consent_version, consent_given, ip_address, agreed_at) VALUES (%s, 'v1.0', 1, %s, %s)",
                (trainee_id, ip_addr, now_str)
            )
            session['consent_status'] = 'agreed'
            flash('Thank you! Your consent has been recorded. Post-training tracking and Outcome ID are now active.', 'success')
            return redirect(url_for('trainee.dashboard'))
        else:
            execute_db(
                "UPDATE trainees SET consent_status = 'declined', consent_date = %s, consent_version = 'v1.0' WHERE id = %s",
                (now_str, trainee_id)
            )
            execute_db(
                "INSERT INTO consents (trainee_id, consent_version, consent_given, ip_address, agreed_at) VALUES (%s, 'v1.0', 0, %s, %s)",
                (trainee_id, ip_addr, now_str)
            )
            session['consent_status'] = 'declined'
            flash('You have opted out of post-training employment outcome tracking. You can change this anytime.', 'info')
            return redirect(url_for('trainee.dashboard'))

    trainee = query_db("SELECT * FROM trainees WHERE id = %s", (trainee_id,), one=True)
    return render_template('trainee/consent.html', trainee=trainee)


@trainee_bp.route('/followup', methods=['GET', 'POST'])
@login_required
@role_required('trainee')
def followup():
    """Milestone follow-up questionnaire submission (3, 6, 12, 24 months)."""
    trainee_id = session.get('trainee_id')
    trainee = query_db("SELECT * FROM trainees WHERE id = %s", (trainee_id,), one=True)

    if trainee['consent_status'] != 'agreed':
        flash('You must provide consent before completing follow-up surveys.', 'warning')
        return redirect(url_for('trainee.consent'))

    if request.method == 'POST':
        milestone = request.form.get('milestone_months', type=int)
        emp_status = request.form.get('employment_status')
        current_salary = request.form.get('current_salary', type=float) or 0.0
        company_name = request.form.get('company_name', '').strip()
        job_role = request.form.get('job_role', '').strip()
        non_placement_reason = request.form.get('non_placement_reason', '').strip()
        attrition_reason = request.form.get('attrition_reason', '').strip()
        notes = request.form.get('notes', '').strip()

        # Calculate salary growth percentage compared to 3-month baseline
        growth_pct = 0.0
        baseline_followup = query_db(
            "SELECT current_salary FROM followups WHERE trainee_id = %s AND milestone_months = 3",
            (trainee_id,),
            one=True
        )
        if baseline_followup and baseline_followup.get('current_salary') and baseline_followup['current_salary'] > 0:
            growth_pct = round(((current_salary - baseline_followup['current_salary']) / baseline_followup['current_salary']) * 100, 1)

        retention_status = 'retained' if emp_status in ('employed', 'self_employed', 'apprentice') else 'left_job'
        today_str = datetime.now().strftime('%Y-%m-%d')

        # Insert or update followup record
        execute_db(
            """
            INSERT INTO followups (
                trainee_id, milestone_months, status, due_date, completed_date, employment_status,
                current_salary, salary_growth_pct, retention_status, non_placement_reason, attrition_reason, notes
            ) VALUES (%s, %s, 'completed', %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (trainee_id, milestone, today_str, today_str, emp_status, current_salary, growth_pct, retention_status, non_placement_reason, attrition_reason, notes)
        )

        # Update trainee current employment status
        execute_db("UPDATE trainees SET current_employment_status = %s WHERE id = %s", (emp_status, trainee_id))

        # If employed, record employment entry
        if emp_status == 'employed' and company_name and job_role:
            execute_db(
                """
                INSERT INTO employment_records (
                    trainee_id, employer_name, job_role, employment_type, joining_date, salary_monthly
                ) VALUES (%s, %s, %s, 'Full-time', %s, %s)
                """,
                (trainee_id, company_name, job_role, today_str, current_salary)
            )

        flash(f'Thank you! Your {milestone}-month outcome follow-up has been submitted.', 'success')
        return redirect(url_for('trainee.dashboard'))

    return render_template('trainee/followup.html', trainee=trainee)
