import sys
from pathlib import Path

# Add project root directory to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import unittest
from backend.config import Config
from backend.app import create_app
from backend.database import query_db, execute_db
from backend.services.outcome_id_service import is_valid_outcome_id, lookup_by_outcome_id
from backend.services.skill_matcher import SkillMatcher
from backend.services.outcome_score import OutcomeScoreCalculator
from backend.services.recommendation_engine import RecommendationEngine


from backend.services.risk_radar import OutcomeRiskRadar
from backend.services.policy_simulator import PolicySimulator
from backend.services.cohort_comparison import CohortComparisonService


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

        # Verify longitudinal followups
        followups = query_db(
            "SELECT milestone_months, current_salary, salary_growth_pct FROM followups WHERE trainee_id = %s ORDER BY milestone_months ASC",
            (trainee['id'],)
        )
        self.assertGreaterEqual(len(followups), 3, "Trainee must have at least 3-month, 6-month, and 12-month followups.")
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

    def test_risk_radar_service(self):
        """Verify Outcome Risk Radar correctly flags Low vs High risk trainees."""
        # Low risk: Employed, retained, 33% growth
        low_res = OutcomeRiskRadar.evaluate_trainee_risk(
            employment_status='employed',
            salary_growth_pct=33.3,
            job_relevance_pct=78.0,
            retention_status='retained',
            employer_rating=4.5,
            missing_skills_text=''
        )
        self.assertEqual(low_res['risk_level'], 'LOW')

        # High risk: Unemployed, 0 salary growth, multiple skill gaps
        high_res = OutcomeRiskRadar.evaluate_trainee_risk(
            employment_status='unemployed',
            salary_growth_pct=0.0,
            job_relevance_pct=30.0,
            retention_status='at_risk',
            employer_rating=2.5,
            missing_skills_text='Advanced Excel, Data Analysis'
        )
        self.assertEqual(high_res['risk_level'], 'HIGH')
        self.assertGreater(len(high_res['risk_factors']), 0)
        self.assertIn('excel', high_res['recommended_intervention'].lower())

    def test_policy_simulator(self):
        """Verify What-If Policy Simulator predicts uplift accurately."""
        # Baseline (no levers)
        base = PolicySimulator.simulate([])
        self.assertEqual(base['projected']['employment_rate'], 68.0)

        # Apply Advanced Excel and Data Analytics levers
        uplift = PolicySimulator.simulate(['add_adv_excel', 'add_data_analytics'])
        self.assertGreater(uplift['projected']['employment_rate'], 68.0)
        self.assertGreater(uplift['projected']['retention_rate'], 63.0)
        self.assertEqual(uplift['active_levers_count'], 2)

    def test_cohort_comparison(self):
        """Verify Before vs After intervention cohort comparison and impact score."""
        comp = CohortComparisonService.get_comparison()
        self.assertIn('before', comp)
        self.assertIn('after', comp)
        self.assertIn('impact_score', comp)
        self.assertEqual(comp['before']['cohort_id'], 'COHORT-2023-A')
        self.assertEqual(comp['after']['cohort_id'], 'COHORT-2024-B')
        self.assertGreater(comp['impact_score']['score'], 0.0)

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

        # Test new Outcome Intelligence endpoints
        res_cohort = self.client.get('/api/cohorts/comparison')
        self.assertEqual(res_cohort.status_code, 200)
        self.assertTrue(res_cohort.json['success'])

        res_sim = self.client.post('/api/simulator/evaluate', json={'levers': ['add_adv_excel']})
        self.assertEqual(res_sim.status_code, 200)
        self.assertTrue(res_sim.json['success'])
        self.assertGreater(res_sim.json['simulation']['projected']['employment_rate'], 68.0)

        res_radar = self.client.get('/api/risk-radar/evaluate?outcome_id=ST-MH-000123')
        self.assertEqual(res_radar.status_code, 200)
        self.assertEqual(res_radar.json['risk_assessment']['risk_level'], 'LOW')

        # Test mobility endpoint
        res_mob = self.client.get('/api/mobility/metrics')
        self.assertEqual(res_mob.status_code, 200)
        self.assertTrue(res_mob.json['success'])
        self.assertEqual(res_mob.json['mobility']['distribution']['maharashtra_pct'], 62.0)
        # Test global world map endpoint
        res_world = self.client.get('/api/mobility/world')
        self.assertEqual(res_world.status_code, 200)
        self.assertTrue(res_world.json['success'])
        self.assertIn('data', res_world.json)
        # Ensure at least one record contains latitude and longitude
        self.assertTrue(any(item.get('lat') is not None and item.get('lon') is not None for item in res_world.json['data']))

        # Test follow-up engine simulation endpoint
        res_fu = self.client.post('/api/followup/run-engine')
        self.assertEqual(res_fu.status_code, 200)
        self.assertTrue(res_fu.json['success'])
        self.assertGreater(res_fu.json['summary']['total_queued'], 0)

        # Test employer registration page
        res_reg_emp = self.client.get('/register-employer')
        self.assertEqual(res_reg_emp.status_code, 200)

    def test_mock_verifications(self):
        """Verify DigiLocker & Identity Verification mock services."""
        from backend.services.document_verification_service import DocumentVerificationService
        from backend.services.identity_verification_service import IdentityVerificationService

        doc_res = DocumentVerificationService.verify_skill_certificate("CERT-MH-2023-000123")
        self.assertTrue(doc_res['is_verified'])
        self.assertEqual(doc_res['status'], 'Demo Verification Successful')

        id_res = IdentityVerificationService.verify_identity("ST-MH-000123")
        self.assertTrue(id_res['is_verified'])
        self.assertIn('DEMO-ID', id_res['verification_token'])

    def test_provider_outcome_intelligence_access(self):
        """Verify Training Provider has full access to the Outcome Intelligence suite."""
        # 1. Quick login as provider
        login_res = self.client.post('/login', data={'quick_role': 'provider'}, follow_redirects=False)
        self.assertEqual(login_res.status_code, 302)

        # 2. Access Outcome Dashboard
        dash_res = self.client.get('/government/dashboard')
        self.assertEqual(dash_res.status_code, 200)
        self.assertIn(b'Outcome Intelligence Dashboard', dash_res.data)

        # 3. Access Skill Gap Analysis
        skill_res = self.client.get('/government/skill-gaps')
        self.assertEqual(skill_res.status_code, 200)

        # 4. Access Recommendations & Action Engine
        rec_res = self.client.get('/government/recommendations')
        self.assertEqual(rec_res.status_code, 200)

        # 5. Access Interactive District Map
        map_res = self.client.get('/government/map')
        self.assertEqual(map_res.status_code, 200)

    def test_new_trainee_registration_and_enrollment(self):
        """Verify full multi-step registration, unique profile creation, and course enrollment."""
        test_email = 'rohit.deshmukh.test@example.com'
        test_username = 'rohit_deshmukh_test'

        # Ensure clean state for test trainee
        trainee_exists = query_db("SELECT id FROM trainees WHERE email = %s", (test_email,), one=True)
        if trainee_exists:
            tid = trainee_exists['id']
            execute_db("DELETE FROM training_records WHERE trainee_id = %s", (tid,))
            execute_db("DELETE FROM employment_records WHERE trainee_id = %s", (tid,))
            execute_db("DELETE FROM followups WHERE trainee_id = %s", (tid,))
            execute_db("DELETE FROM trainee_skills WHERE trainee_id = %s", (tid,))
            execute_db("DELETE FROM consents WHERE trainee_id = %s", (tid,))
            execute_db("DELETE FROM trainees WHERE id = %s", (tid,))
        execute_db("DELETE FROM users WHERE email = %s OR username = %s", (test_email, test_username))

        # 1. GET registration wizard
        res_get = self.client.get('/register')
        self.assertEqual(res_get.status_code, 200)
        self.assertIn(b'Create Trainee Profile', res_get.data)

        # 2. POST 5-step registration data
        reg_payload = {
            'first_name': 'Rohit',
            'last_name': 'Deshmukh',
            'email': test_email,
            'phone': '+91 9123456780',
            'dob': '2001-08-20',
            'gender': 'Male',
            'country': 'India',
            'state': 'Maharashtra',
            'city': 'Nashik',
            'district_id': 1,
            'highest_education': "Bachelor's Degree",
            'field_of_study': 'Mechanical Engineering',
            'institution': 'Nashik Engineering College',
            'graduation_year': 2023,
            'provider_id': 1,
            'course_id': 1,
            'training_start_date': '2023-01-01',
            'training_completion_date': '2023-05-30',
            'skills_learned': ['1', '4', '6'],
            'employment_status': 'employed',
            'employer_name': 'Nashik Auto Systems',
            'job_role': 'Quality Analyst',
            'employment_location': 'Nashik',
            'employment_start_date': '2023-06-15',
            'salary_monthly': 21000,
            'username': 'rohit_deshmukh_test',
            'password': 'rohitpassword123',
            'confirm_password': 'rohitpassword123'
        }

        res_post = self.client.post('/register', data=reg_payload, follow_redirects=True)
        self.assertEqual(res_post.status_code, 200)
        self.assertIn(b'Welcome to SkillTrack, Rohit!', res_post.data)
        self.assertIn(b'Rohit Deshmukh', res_post.data)

        # Verify unique trainee record in database
        trainee = query_db("SELECT * FROM trainees WHERE email = %s", (test_email,), one=True)
        self.assertIsNotNone(trainee)
        self.assertTrue(trainee['outcome_id'].startswith('ST-MH-'))
        self.assertNotEqual(trainee['outcome_id'], 'ST-MH-000123')
        self.assertEqual(trainee['city'], 'Nashik')

        # Test Course Enrollment
        res_enroll = self.client.post('/trainee/enroll', data={'course_id': 2, 'provider_id': 3}, follow_redirects=True)
        self.assertEqual(res_enroll.status_code, 200)
        self.assertIn(b'Successfully enrolled', res_enroll.data)


if __name__ == '__main__':
    unittest.main()


