from typing import Dict, Any, List

class PolicySimulator:
    """
    Government 'What-If' Policy & Intervention Simulator.
    Allows administrators to test hypothetical policy levers and view simulated prototype improvements.
    
    IMPORTANT: Prototype simulation using synthetic heuristic models.
    Clearly designated as: 'Prototype Simulation using Synthetic Data — Not an Official Forecast'.
    """

    DISCLAIMER = "Prototype Simulation using Synthetic Data — Not an Official Forecast"

    # Predefined synthetic policy levers and their estimated outcome deltas
    LEVERS = {
        'add_adv_excel': {
            'label': 'Add Advanced Excel Module (30h practical)',
            'emp_delta': 5.5,
            'ret_delta': 4.5,
            'rel_delta': 8.5,
            'wage_delta': 1200,
            'description': 'Closes the #1 detected skill gap across back-office and ITES recruitment drives.'
        },
        'add_data_analytics': {
            'label': 'Add Introductory Data Analytics & Reporting',
            'emp_delta': 4.0,
            'ret_delta': 3.5,
            'rel_delta': 6.0,
            'wage_delta': 900,
            'description': 'Prepares candidates for analytical dashboard reporting and ERP entry.'
        },
        'increase_practical_training': {
            'label': 'Increase Hands-On Practical Lab Hours by 25%',
            'emp_delta': 4.5,
            'ret_delta': 4.0,
            'rel_delta': 5.0,
            'wage_delta': 700,
            'description': 'Elevates practical competency scores and speeds up workplace onboarding.'
        },
        'mandate_wage_benchmarks': {
            'label': 'Enforce Placement Living Wage Benchmark (>= ₹16,500)',
            'emp_delta': 2.0,
            'ret_delta': 8.0,
            'rel_delta': 2.0,
            'wage_delta': 1800,
            'description': 'Directly targets the #1 reason for 6-month attrition (low starting pay).'
        },
        'transport_subsidy': {
            'label': 'Provide 90-Day District Commute & Transport Stipends',
            'emp_delta': 4.8,
            'ret_delta': 3.2,
            'rel_delta': 1.0,
            'wage_delta': 300,
            'description': 'Removes geographic accessibility barriers for female and rural candidates.'
        }
    }

    @classmethod
    def simulate(
        cls,
        selected_levers: List[str],
        baseline_employment: float = 68.0,
        baseline_retention: float = 63.0,
        baseline_relevance: float = 71.0,
        baseline_salary: float = 16000.0
    ) -> Dict[str, Any]:
        """
        Calculates projected prototype outcomes based on activated policy levers.
        """
        emp_gain = 0.0
        ret_gain = 0.0
        rel_gain = 0.0
        wage_gain = 0.0
        applied_details = []

        for lever_key in selected_levers:
            if lever_key in cls.LEVERS:
                lever = cls.LEVERS[lever_key]
                emp_gain += lever['emp_delta']
                ret_gain += lever['ret_delta']
                rel_gain += lever['rel_delta']
                wage_gain += lever['wage_delta']
                applied_details.append({
                    'key': lever_key,
                    'label': lever['label'],
                    'description': lever['description']
                })

        # Cap gains to realistic bounds
        proj_emp = min(96.0, round(baseline_employment + emp_gain, 1))
        proj_ret = min(94.0, round(baseline_retention + ret_gain, 1))
        proj_rel = min(98.0, round(baseline_relevance + rel_gain, 1))
        proj_sal = round(baseline_salary + wage_gain, 0)

        # Compute Prototype Outcome Score for both baseline and projected
        # 30% Emp + 25% Ret + 20% Rel + 15% Sal + 10% Feed
        base_score = round((baseline_employment * 0.3) + (baseline_retention * 0.25) + (baseline_relevance * 0.2) + (50 * 0.15) + (80 * 0.1), 1)
        proj_score = round((proj_emp * 0.3) + (proj_ret * 0.25) + (proj_rel * 0.2) + (65 * 0.15) + (88 * 0.1), 1)

        return {
            'disclaimer': cls.DISCLAIMER,
            'active_levers_count': len(applied_details),
            'applied_levers': applied_details,
            'baseline': {
                'employment_rate': baseline_employment,
                'retention_rate': baseline_retention,
                'relevance_score': baseline_relevance,
                'avg_salary': baseline_salary,
                'outcome_score': base_score
            },
            'projected': {
                'employment_rate': proj_emp,
                'retention_rate': proj_ret,
                'relevance_score': proj_rel,
                'avg_salary': proj_sal,
                'outcome_score': proj_score
            },
            'improvements': {
                'employment_delta': round(proj_emp - baseline_employment, 1),
                'retention_delta': round(proj_ret - baseline_retention, 1),
                'relevance_delta': round(proj_rel - baseline_relevance, 1),
                'salary_delta': round(proj_sal - baseline_salary, 0),
                'score_delta': round(proj_score - base_score, 1)
            }
        }
