import json
from pathlib import Path
from flask import Blueprint, jsonify, request
from backend.database import query_db
from backend.services.skill_matcher import SkillMatcher
from backend.services.outcome_score import OutcomeScoreCalculator

api_bp = Blueprint('api', __name__, url_prefix='/api')
BASE_DIR = Path(__file__).resolve().parent.parent.parent

@api_bp.route('/districts')
def get_districts():
    """Returns Maharashtra district coordinates and outcome statistics for Leaflet map."""
    districts_file = BASE_DIR / "data" / "maharashtra_districts.json"
    if districts_file.exists():
        with open(districts_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return jsonify({'success': True, 'districts': data})
    
    # Fallback to DB table
    districts = query_db("SELECT * FROM districts")
    return jsonify({'success': True, 'districts': districts})


@api_bp.route('/charts/trends')
def get_trends():
    """Returns milestone retention rates and salary progression curves (3, 6, 12, 24 months)."""
    return jsonify({
        'success': True,
        'retention_curve': {
            'labels': ['3 Months', '6 Months', '12 Months', '24 Months (Projected)'],
            'rates': [86.4, 78.2, 71.4, 66.8]
        },
        'salary_progression': {
            'labels': ['Entry / Joining', '3 Months', '6 Months', '12 Months', '24 Months (Projected)'],
            'avg_salary': [14800, 16200, 18400, 20800, 24500],
            'growth_pct': [0.0, 9.5, 24.3, 40.5, 65.5]
        }
    })


@api_bp.route('/charts/why-analysis')
def get_why_analysis():
    """Returns root cause distributions for non-placement and job attrition."""
    non_placement = query_db(
        """
        SELECT non_placement_reason AS reason, COUNT(*) AS count
        FROM followups
        WHERE non_placement_reason IS NOT NULL AND non_placement_reason != ''
        GROUP BY non_placement_reason
        ORDER BY count DESC
        """
    )
    attrition = query_db(
        """
        SELECT attrition_reason AS reason, COUNT(*) AS count
        FROM followups
        WHERE attrition_reason IS NOT NULL AND attrition_reason != ''
        GROUP BY attrition_reason
        ORDER BY count DESC
        """
    )

    return jsonify({
        'success': True,
        'non_placement': non_placement,
        'attrition': attrition
    })


@api_bp.route('/relevance/calculate', methods=['POST', 'GET'])
def calculate_relevance():
    """
    Live API to calculate Training -> Job Relevance using TF-IDF and Cosine Similarity.
    Accepts: { curriculum_skills: [...], workplace_skills: [...] }
    """
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        curr = data.get('curriculum_skills', '')
        work = data.get('workplace_skills', '')
    else:
        curr = request.args.get('curriculum_skills', 'Basic Excel, Data Entry, English Typing, Communication')
        work = request.args.get('workplace_skills', 'Advanced Excel, Data Analysis, Client Communication, Reporting')

    result = SkillMatcher.calculate_relevance(curr, work)
    return jsonify({'success': True, 'result': result})


@api_bp.route('/outcome-score/calculate', methods=['POST', 'GET'])
def calculate_outcome_score():
    """
    Live API to compute the Prototype Outcome Score with custom or default weights.
    """
    args = request.args if request.method == 'GET' else (request.get_json(silent=True) or request.form)
    
    emp = float(args.get('employment_rate', 78.0))
    ret = float(args.get('retention_rate', 71.4))
    rel = float(args.get('job_relevance', 82.0))
    sal = float(args.get('salary_growth_pct', 33.3))
    fee = float(args.get('employer_satisfaction', 84.0))

    score_result = OutcomeScoreCalculator.calculate_score(
        employment_rate=emp,
        retention_rate=ret,
        job_relevance=rel,
        avg_salary_growth_pct=sal,
        employer_satisfaction_pct=fee
    )
    return jsonify({'success': True, 'data': score_result})
