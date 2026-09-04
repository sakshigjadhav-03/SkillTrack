from typing import Dict, Any
from backend.config import Config

class OutcomeScoreCalculator:
    """
    Computes institutional and cohort Prototype Outcome Scores (0-100).
    Uses configurable weights defined in Config.
    IMPORTANT: Clearly designated as a prototype metric, not an official government formula.
    """

    LABEL = "Prototype Outcome Score (Experimental Indicator)"
    DISCLAIMER = "This is a prototype metric developed for SIH26135 evaluation, not an official government formula."

    @classmethod
    def calculate_score(
        cls,
        employment_rate: float = 0.0,
        retention_rate: float = 0.0,
        job_relevance: float = 0.0,
        avg_salary_growth_pct: float = 0.0,
        employer_satisfaction_pct: float = 0.0,
        custom_weights: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Calculates the weighted prototype outcome score.
        All input rates should be 0 - 100 percentages.
        """
        weights = {
            'employment': Config.WEIGHT_EMPLOYMENT,
            'retention': Config.WEIGHT_RETENTION,
            'relevance': Config.WEIGHT_RELEVANCE,
            'salary_growth': Config.WEIGHT_SALARY_GROWTH,
            'employer_feedback': Config.WEIGHT_EMPLOYER_FEEDBACK
        }
        if custom_weights:
            weights.update(custom_weights)

        # Normalize salary growth to a 0-100 scale (e.g. 50% salary growth = 100 points, 0% = 0 points)
        normalized_salary_growth = min(100.0, max(0.0, avg_salary_growth_pct * 2.0))

        # Ensure values are bounded between 0 and 100
        emp = min(100.0, max(0.0, float(employment_rate)))
        ret = min(100.0, max(0.0, float(retention_rate)))
        rel = min(100.0, max(0.0, float(job_relevance)))
        sal = min(100.0, max(0.0, normalized_salary_growth))
        fee = min(100.0, max(0.0, float(employer_satisfaction_pct)))

        total_weight = sum(weights.values()) or 100.0

        score = (
            (emp * weights['employment']) +
            (ret * weights['retention']) +
            (rel * weights['relevance']) +
            (sal * weights['salary_growth']) +
            (fee * weights['employer_feedback'])
        ) / total_weight

        rounded_score = round(score, 1)

        return {
            'outcome_score': rounded_score,
            'metric_label': cls.LABEL,
            'disclaimer': cls.DISCLAIMER,
            'weights_used': weights,
            'components': {
                'employment_rate': round(emp, 1),
                'retention_rate': round(ret, 1),
                'job_relevance': round(rel, 1),
                'salary_growth_pct': round(avg_salary_growth_pct, 1),
                'salary_growth_normalized': round(sal, 1),
                'employer_satisfaction_pct': round(fee, 1)
            },
            'weighted_contributions': {
                'employment': round((emp * weights['employment']) / total_weight, 1),
                'retention': round((ret * weights['retention']) / total_weight, 1),
                'relevance': round((rel * weights['relevance']) / total_weight, 1),
                'salary_growth': round((sal * weights['salary_growth']) / total_weight, 1),
                'employer_feedback': round((fee * weights['employer_feedback']) / total_weight, 1)
            }
        }
