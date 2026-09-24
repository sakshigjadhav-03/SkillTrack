from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from backend.database import query_db, execute_db
from backend.utils.decorators import login_required, role_required
from backend.services.outcome_score import OutcomeScoreCalculator
from backend.services.skill_matcher import SkillMatcher

provider_bp = Blueprint('provider', __name__, url_prefix='/provider')

@provider_bp.route('/dashboard')
@login_required
@role_required('provider')
def dashboard():
    """Training Provider dashboard showing cohort analytics, curriculum gaps, and feedback."""
    provider_id = session.get('provider_id') or 1
    provider = query_db("SELECT * FROM training_providers WHERE id = %s", (provider_id,), one=True)

    # Provider cohorts & courses summary
    courses_summary = query_db(
        """
        SELECT 
            c.id AS course_id,
            c.course_code,
            c.course_name,
            c.sector,
            COUNT(DISTINCT tr.trainee_id) AS enrolled_count,
            SUM(CASE WHEN tr.certification_status = 'certified' THEN 1 ELSE 0 END) AS certified_count,
            SUM(CASE WHEN t.current_employment_status IN ('employed', 'self_employed', 'apprentice') THEN 1 ELSE 0 END) AS placed_count
        FROM training_records tr
        JOIN courses c ON tr.course_id = c.id
        JOIN trainees t ON tr.trainee_id = t.id
        WHERE tr.provider_id = %s
        GROUP BY c.id, c.course_code, c.course_name, c.sector
        """,
        (provider_id,)
    )

    # Calculate overall KPIs for this provider
    total_trained = sum(c['enrolled_count'] for c in courses_summary) if courses_summary else 0
    total_placed = sum(c['placed_count'] for c in courses_summary) if courses_summary else 0
    placement_rate = round((total_placed / total_trained * 100), 1) if total_trained > 0 else 0.0

    # 6-Month Retention Rate
    retention_stat = query_db(
        """
        SELECT 
            COUNT(*) AS total_6m,
            SUM(CASE WHEN f.retention_status = 'retained' THEN 1 ELSE 0 END) AS retained_6m
        FROM followups f
        JOIN training_records tr ON f.trainee_id = tr.trainee_id
        WHERE tr.provider_id = %s AND f.milestone_months = 6
        """,
        (provider_id,),
        one=True
    )
    retention_rate = 74.5
    if retention_stat and (retention_stat.get('total_6m') or 0) > 0:
        ret_6m = retention_stat.get('retained_6m') or 0
        retention_rate = round((ret_6m / retention_stat['total_6m']) * 100, 1)

    # Trainees under this provider
    trainees = query_db(
        """
        SELECT 
            t.id AS trainee_id,
            t.outcome_id,
            t.first_name,
            t.last_name,
            t.current_employment_status,
            c.course_name,
            tr.completion_date,
            tr.certification_status,
            ev.verification_status,
            ev.token AS verification_token,
            er.employer_name AS company_name,
            er.job_role,
            er.joining_date,
            er.salary_monthly,
            f.current_salary,
            f.salary_growth_pct,
            f.retention_status,
            78.5 AS job_relevance_score
        FROM training_records tr
        JOIN trainees t ON tr.trainee_id = t.id
        JOIN courses c ON tr.course_id = c.id
        LEFT JOIN employment_records er ON t.id = er.trainee_id
        LEFT JOIN employer_verifications ev ON t.id = ev.trainee_id
        LEFT JOIN followups f ON t.id = f.trainee_id AND f.milestone_months = 12
        WHERE tr.provider_id = %s
        ORDER BY t.id DESC
        """,
        (provider_id,)
    )

    # Attach Risk Radar analysis to each trainee
    from backend.services.risk_radar import OutcomeRiskRadar
    for t in trainees:
        risk_res = OutcomeRiskRadar.evaluate_trainee_risk(
            employment_status=t.get('current_employment_status') or 'unemployed',
            retention_status=t.get('retention_status') or 'unknown',
            salary_growth_pct=float(t.get('salary_growth_pct') or 0.0),
            job_relevance_pct=float(t.get('job_relevance_score') or 60.0),
            employer_rating=4.0,
            missing_skills_text=''
        )
        t['risk_level'] = risk_res['risk_level']
        t['risk_color'] = risk_res['badge_class']
        t['recommended_action'] = risk_res['recommended_intervention']

    # Employer feedback for this provider's graduates
    feedbacks = query_db(
        """
        SELECT 
            ef.*,
            e.company_name,
            t.outcome_id,
            t.first_name,
            t.last_name,
            c.course_name
        FROM employer_feedback ef
        JOIN trainees t ON ef.trainee_id = t.id
        JOIN training_records tr ON t.id = tr.trainee_id
        JOIN courses c ON tr.course_id = c.id
        JOIN employers e ON ef.employer_id = e.id
        WHERE tr.provider_id = %s
        ORDER BY ef.feedback_date DESC
        """,
        (provider_id,)
    )

    # Aggregate missing skill frequency
    skill_gaps = []
    gap_counts = {}
    for fb in feedbacks:
        if fb.get('missing_skills_text'):
            for sk in fb['missing_skills_text'].split(','):
                item = sk.strip()
                if item:
                    gap_counts[item] = gap_counts.get(item, 0) + 1
    
    sorted_gaps = sorted(gap_counts.items(), key=lambda x: x[1], reverse=True)

    # Prototype Outcome Score calculation for this provider
    outcome_score = OutcomeScoreCalculator.calculate_score(
        employment_rate=placement_rate,
        retention_rate=retention_rate,
        job_relevance=80.0,
        avg_salary_growth_pct=24.0,
        employer_satisfaction_pct=82.0
    )

    return render_template(
        'provider/dashboard.html',
        provider=provider,
        courses=courses_summary,
        trainees=trainees,
        feedbacks=feedbacks,
        skill_gaps=sorted_gaps[:5],
        placement_rate=placement_rate,
        retention_rate=retention_rate,
        total_trained=total_trained,
        outcome_score=outcome_score
    )


@provider_bp.route('/request-verification/<int:trainee_id>', methods=['POST'])
@login_required
@role_required('provider')
def request_verification(trainee_id):
    """
    Generates a secure verification link for a trainee's reported employment outcome.
    Initiated by the Training Provider.
    """
    token, verify_url, trainee, er = _generate_verification_request(trainee_id)
    if not token:
        flash("Could not generate verification request for this trainee.", "danger")
        return redirect(url_for('provider.dashboard'))
    
    flash(f"Verification request generated for {trainee['first_name']} {trainee['last_name']}! Secure link ready to share.", "success")
    return redirect(url_for('provider.dashboard'))


@provider_bp.route('/api/request-verification', methods=['POST'])
@login_required
@role_required('provider')
def api_request_verification():
    """
    JSON API for Training Provider to asynchronously generate a secure employer verification link.
    """
    data = request.get_json(silent=True) or request.form
    trainee_id = data.get('trainee_id')
    if not trainee_id:
        return jsonify({'success': False, 'message': 'trainee_id is required'}), 400
    
    token, verify_url, trainee, er = _generate_verification_request(int(trainee_id))
    if not token:
        return jsonify({'success': False, 'message': 'Trainee or employment record not found'}), 404
    
    return jsonify({
        'success': True,
        'token': token,
        'verify_url': verify_url,
        'trainee_name': f"{trainee['first_name']} {trainee['last_name']}",
        'outcome_id': trainee['outcome_id'],
        'company_name': er['employer_name'] if er else 'Hiring Employer',
        'job_role': er['job_role'] if er else 'Designated Role',
        'salary_monthly': er['salary_monthly'] if er else None,
        'joining_date': str(er['joining_date']) if er and er.get('joining_date') else None
    })


def _generate_verification_request(trainee_id: int):
    import uuid
    from datetime import datetime
    trainee = query_db("SELECT * FROM trainees WHERE id = %s", (trainee_id,), one=True)
    if not trainee:
        return None, None, None, None
    
    er = query_db("SELECT * FROM employment_records WHERE trainee_id = %s ORDER BY id DESC", (trainee_id,), one=True)
    
    # Check if verification record already exists
    ev = query_db("SELECT * FROM employer_verifications WHERE trainee_id = %s", (trainee_id,), one=True)
    
    if ev and ev.get('token'):
        token = ev['token']
    else:
        token = f"EV-{uuid.uuid4().hex[:12].upper()}"
        if ev:
            execute_db("UPDATE employer_verifications SET token = %s WHERE id = %s", (token, ev['id']))
        else:
            employer_id = er['employer_id'] if er and er.get('employer_id') else 1
            verified_role = er['job_role'] if er else 'Trainee Graduate'
            verified_date = er['joining_date'] if er else datetime.now().strftime('%Y-%m-%d')
            sal_monthly = er['salary_monthly'] if er and er.get('salary_monthly') else 20000.0
            sal_range = f"₹{int(sal_monthly):,} / month"
            execute_db(
                """
                INSERT INTO employer_verifications (
                    employer_id, trainee_id, outcome_id, token, verification_status,
                    verified_role, verified_joining_date, verified_salary_range, remarks
                ) VALUES (%s, %s, %s, %s, 'pending', %s, %s, %s, 'Verification requested by Training Provider')
                """,
                (employer_id, trainee_id, trainee['outcome_id'], token, verified_role, verified_date, sal_range)
            )

    verify_url = url_for('employer.verify_request', token=token, _external=True)
    return token, verify_url, trainee, er
