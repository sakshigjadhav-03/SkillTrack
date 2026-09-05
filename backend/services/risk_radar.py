from typing import Dict, Any, List

class OutcomeRiskRadar:
    """
    Outcome Risk Radar.
    Evaluates individual trainee outcome trajectories to identify candidates at risk of:
    - Early job attrition
    - Long-term unemployment
    - Wage stagnation / poor career progression
    - Workplace skill mismatch
    
    IMPORTANT: Prototype rule-based heuristic for SIH demonstration.
    Clearly designated as 'Prototype Risk Assessment — Illustrative'.
    """

    DISCLAIMER = "Prototype Risk Assessment — Illustrative Rule-Based Metric (Not an official government predictive score)"

    @classmethod
    def evaluate_trainee_risk(
        cls,
        employment_status: str,
        salary_growth_pct: float = 0.0,
        job_relevance_pct: float = 75.0,
        retention_status: str = 'retained',
        employer_rating: float = 4.0,
        missing_skills_text: str = ""
    ) -> Dict[str, Any]:
        """
        Calculates trainee risk level (LOW, MEDIUM, HIGH) with explainable risk factors
        and targeted recommended interventions.
        """
        risk_score = 0
        risk_factors: List[str] = []
        intervention = "Continue periodic milestone tracking."

        # Factor 1: Current Employment Status
        status = (employment_status or '').lower().strip()
        if status in ('unemployed', 'dropped'):
            risk_score += 45
            risk_factors.append("Candidate is currently unplaced / seeking livelihood")
        elif status == 'apprentice':
            risk_score += 15
            risk_factors.append("In temporary apprenticeship role (conversion tracking needed)")

        # Factor 2: Job Retention State
        ret_st = (retention_status or '').lower().strip()
        if ret_st in ('at_risk', 'left_job'):
            risk_score += 35
            risk_factors.append("Employment retention flagged as unstable or job exited")

        # Factor 3: Salary Progression Trajectory
        if status in ('employed', 'self_employed'):
            if salary_growth_pct <= 0:
                risk_score += 25
                risk_factors.append("Wage stagnation: 0% salary growth recorded over follow-up interval")
            elif salary_growth_pct < 12.0:
                risk_score += 10
                risk_factors.append("Low salary progression (<12% annual rate)")

        # Factor 4: Training -> Job Relevance
        if job_relevance_pct < 65.0:
            risk_score += 25
            risk_factors.append(f"Severe skill mismatch: Training relevance is low ({job_relevance_pct}%)")
        elif job_relevance_pct < 75.0:
            risk_score += 10
            risk_factors.append(f"Moderate curriculum gap: Training relevance is {job_relevance_pct}%")

        # Factor 5: Employer Feedback
        if employer_rating and employer_rating < 3.0:
            risk_score += 20
            risk_factors.append(f"Below-average employer satisfaction score ({employer_rating}/5.0)")

        # Targeted Recommended Intervention
        missing_clean = (missing_skills_text or '').lower()
        if 'excel' in missing_clean or 'data' in missing_clean:
            intervention = "Targeted upskilling in Advanced Excel & Basic Data Analytics modules."
        elif 'communication' in missing_clean or 'english' in missing_clean:
            intervention = "Enroll in 20-hour Workplace Communication & Client Pitching bootcamp."
        elif 'transport' in risk_factors or 'location' in missing_clean:
            intervention = "Provide localized district transport stipend allowance."
        elif status == 'unemployed':
            intervention = "Priority referral to empanelled placement partners with 45-day retention support."
        elif risk_score >= 50:
            intervention = "Proactive retention counseling and employer wage review engagement."

        # Determine Classification
        if risk_score >= 55:
            risk_level = "HIGH"
            badge_class = "danger"
        elif risk_score >= 30:
            risk_level = "MEDIUM"
            badge_class = "warning"
        else:
            risk_level = "LOW"
            badge_class = "success"

        return {
            'risk_level': risk_level,
            'risk_score': min(100, risk_score),
            'risk_factors': risk_factors if risk_factors else ["Stable employment trajectory", "Positive employer validation"],
            'recommended_intervention': intervention,
            'badge_class': badge_class,
            'disclaimer': cls.DISCLAIMER
        }
