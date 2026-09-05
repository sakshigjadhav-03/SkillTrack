from typing import Dict, Any

class CohortComparisonService:
    """
    Cohort Comparison Service (Before vs. After Intervention).
    Measures empirical outcome improvements across historical vs. modernized cohorts.
    
    IMPORTANT: Prototype comparison using synthetic cohort data.
    Clearly designated as: 'Synthetic Prototype Comparison — Not Government Data'.
    """

    DISCLAIMER = "Synthetic Prototype Comparison — Not Official Government Data"

    @classmethod
    def get_comparison(cls, course_name: str = "Data Entry & Office Automation") -> Dict[str, Any]:
        """
        Returns comparative benchmarks for historical cohort vs post-intervention cohort.
        """
        # Primary SIH Hackathon Demo: Data Entry & Office Automation
        before_cohort = {
            'cohort_id': 'COHORT-2023-A',
            'period': 'Jan 2023 - Jun 2023',
            'curriculum': 'Traditional Data Entry (Basic MS Office, Typing)',
            'total_trained': 120,
            'employment_rate': 64.0,
            'retention_rate': 58.0,
            'relevance_score': 62.0,
            'avg_salary': 14500
        }

        after_cohort = {
            'cohort_id': 'COHORT-2024-B',
            'period': 'Jan 2024 - Jun 2024',
            'curriculum': 'Modernized Data Operations (Advanced Excel + Basic Analytics Added)',
            'total_trained': 135,
            'employment_rate': 76.0,
            'retention_rate': 71.0,
            'relevance_score': 81.0,
            'avg_salary': 17200
        }

        # Calculate Deltas (Improvements)
        emp_delta = round(after_cohort['employment_rate'] - before_cohort['employment_rate'], 1)
        ret_delta = round(after_cohort['retention_rate'] - before_cohort['retention_rate'], 1)
        rel_delta = round(after_cohort['relevance_score'] - before_cohort['relevance_score'], 1)
        salary_delta = after_cohort['avg_salary'] - before_cohort['avg_salary']

        # Feature 6: Prototype Intervention Impact Score
        # Formula: (Emp Delta * 0.35) + (Ret Delta * 0.35) + (Rel Delta * 0.30)
        impact_score = round((emp_delta * 0.35) + (ret_delta * 0.35) + (rel_delta * 0.30), 1)
        overall_impact = "POSITIVE (HIGH EFFICACY)" if impact_score >= 10.0 else ("MODERATE" if impact_score > 0 else "NEUTRAL")

        return {
            'course_name': course_name,
            'intervention_applied': "30 Hours of Advanced Excel (VLOOKUP, Pivot, INDEX-MATCH) + 15 Hours Introductory Data Analytics & Dashboard Reporting",
            'disclaimer': cls.DISCLAIMER,
            'before': before_cohort,
            'after': after_cohort,
            'improvements': {
                'employment_delta_pp': emp_delta,
                'retention_delta_pp': ret_delta,
                'relevance_delta_pp': rel_delta,
                'salary_delta_inr': salary_delta
            },
            'impact_score': {
                'score': impact_score,
                'overall_assessment': overall_impact,
                'metric_label': "Prototype Impact Metric — Illustrative",
                'formula_explanation': "Impact Score = (35% x ΔEmployment) + (35% x ΔRetention) + (30% x ΔRelevance)"
            }
        }
