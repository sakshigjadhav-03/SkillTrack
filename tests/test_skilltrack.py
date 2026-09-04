import sys
from pathlib import Path

# Add project root directory to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import unittest
from backend.config import Config
from backend.app import create_app
from backend.database import query_db
from backend.services.outcome_id_service import is_valid_outcome_id, lookup_by_outcome_id
from backend.services.skill_matcher import SkillMatcher
from backend.services.outcome_score import OutcomeScoreCalculator
from backend.services.recommendation_engine import RecommendationEngine


class SkillTrackTestCase(unittest.TestCase):
    """Automated test suite verifying core SkillTrack prototype components."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    def test_database_and_demo_trainee(self):
        """Verify that demo trainee ST-MH-000123 exists with 33.3% salary growth."""
        trainee = query_db("SELECT * FROM trainees WHERE outcome_id = 'ST-MH-000123'", one=True)
        self.assertIsNotNone(trainee, "Demo trainee ST-MH-000123 must exist in database.")
        self.assertEqual(trainee['first_name'], 'Rahul')
        self.assertEqual(trainee['consent_status'], 'agreed')

        # Verify longitudinal followups (3m, 6m, 12m)
        followups = query_db(
            "SELECT milestone_months, current_salary, salary_growth_pct FROM followups WHERE trainee_id = %s ORDER BY milestone_months ASC",
            (trainee['id'],)
        )
        self.assertEqual(len(followups), 3, "Trainee must have 3-month, 6-month, and 12-month followups.")
        self.assertEqual(followups[0]['current_salary'], 15000.0)
        self.assertEqual(followups[1]['current_salary'], 17000.0)
        self.assertEqual(followups[2]['current_salary'], 20000.0)
        self.assertEqual(followups[2]['salary_growth_pct'], 33.3, "12-month salary growth must equal 33.3%.")

    def test_outcome_id_validation(self):
        """Verify Outcome ID format validation and lookup."""
        self.assertTrue(is_valid_outcome_id("ST-MH-000123"))
        self.assertTrue(is_valid_outcome_id("ST-MH-100125"))
        self.assertFalse(is_valid_outcome_id("INVALID-ID"))
        self.assertFalse(is_valid_outcome_id("ST-DL-000123"))

        lookup = lookup_by_outcome_id("ST-MH-000123")
        self.assertIsNotNone(lookup)
        self.assertEqual(lookup['outcome_id'], 'ST-MH-000123')

    def test_skill_matcher_tfidf(self):
        """Verify TF-IDF & Cosine Similarity skill relevance calculation."""
        curriculum = "Basic Excel, Communication, Data Entry, English Typing"
        workplace = "Advanced Excel, Data Analysis, Communication"

        res = SkillMatcher.calculate_relevance(curriculum, workplace)
        self.assertIn('relevance_percentage', res)
        self.assertGreater(res['relevance_percentage'], 0.0)
        self.assertLessEqual(res['relevance_percentage'], 100.0)
        self.assertIn('communication', res['matched_skills'])
        self.assertIn('advanced excel', res['missing_skills'])
        self.assertIn('data analysis', res['missing_skills'])

    def test_outcome_score_calculation(self):
        """Verify composite Prototype Outcome Score weights (30-25-20-15-10)."""
        score_res = OutcomeScoreCalculator.calculate_score(
            employment_rate=78.0,
            retention_rate=71.0,
            job_relevance=82.0,
            avg_salary_growth_pct=33.3,
            employer_satisfaction_pct=84.0
        )
        self.assertIn('outcome_score', score_res)
        score = score_res['outcome_score']
        self.assertGreater(score, 60.0)
        self.assertLessEqual(score, 100.0)
        self.assertEqual(score_res['weights_used']['employment'], 30.0)
        self.assertEqual(score_res['weights_used']['retention'], 25.0)

    def test_recommendation_engine(self):
        """Verify explainable policy recommendations generation."""
        recs = RecommendationEngine.generate_recommendations()
        self.assertIsInstance(recs, list)
        self.assertGreater(len(recs), 0)
        first_rec = recs[0]
        self.assertIn('problem', first_rec)
        self.assertIn('evidence', first_rec)
        self.assertIn('recommendation', first_rec)
        self.assertIn('suggested_action', first_rec)

    def test_http_routes(self):
        """Verify core HTTP endpoints return HTTP 200 OK."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)

        res_login = self.client.get('/login')
        self.assertEqual(res_login.status_code, 200)

        res_dist = self.client.get('/api/districts')
        self.assertEqual(res_dist.status_code, 200)
        self.assertTrue(res_dist.json['success'])

        res_trends = self.client.get('/api/charts/trends')
        self.assertEqual(res_trends.status_code, 200)

        res_rel = self.client.get('/api/relevance/calculate')
        self.assertEqual(res_rel.status_code, 200)


if __name__ == '__main__':
    unittest.main()
