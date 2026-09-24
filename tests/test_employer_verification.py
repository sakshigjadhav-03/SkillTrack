import unittest
from backend.app import create_app
from backend.database import query_db, execute_db

class EmployerVerificationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    def test_public_employer_verification_flow(self):
        # 1. Access verification page with pre-seeded demo token
        res = self.client.get('/verify-employment/EV-DEMO-000123')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Employment Verification', res.data)
        self.assertIn(b'Rahul Sharma', res.data)
        self.assertIn(b'Workplace Skill Validation', res.data)

        # 2. Submit employer verification confirmation
        post_data = {
            'decision': 'confirm',
            'skill_communication': 'Demonstrated',
            'skill_technical': 'Demonstrated',
            'skill_problem_solving': 'Partially Demonstrated',
            'skill_teamwork': 'Demonstrated',
            'missing_skills_text': 'Advanced Analytics, Cloud ERP',
            'general_feedback': 'Strong performer with consistent attendance.'
        }
        res_post = self.client.post('/verify-employment/EV-DEMO-000123', data=post_data)
        self.assertEqual(res_post.status_code, 200)
        self.assertIn(b'Employment Verified', res_post.data)

        # 3. Check database record
        ev = query_db("SELECT * FROM employer_verifications WHERE token = %s", ('EV-DEMO-000123',), one=True)
        self.assertIsNotNone(ev)
        self.assertEqual(ev['verification_status'], 'verified')

        # Check employer feedback was recorded
        fb = query_db("SELECT * FROM employer_feedback WHERE trainee_id = %s", (ev['trainee_id'],), one=True)
        self.assertIsNotNone(fb)
        self.assertEqual(fb['communication_rating'], 5)
        self.assertIn('Advanced Analytics', fb['missing_skills_text'])

    def test_provider_verification_generation(self):
        # Login as provider
        self.client.post('/login', data={'email': 'provider@maharashtra-skills.org', 'password': 'provider123'})
        res_api = self.client.post('/provider/api/request-verification', json={'trainee_id': 2})
        self.assertEqual(res_api.status_code, 200)
        data = res_api.get_json()
        self.assertTrue(data['success'])
        self.assertIn('token', data)
        self.assertTrue(data['token'].startswith('EV-'))

        # Verify generated link can be loaded by an external user (no auth required)
        fresh_client = self.app.test_client()
        res_link = fresh_client.get(f"/verify-employment/{data['token']}")
        self.assertEqual(res_link.status_code, 200)
        self.assertIn(b'Employment Verification', res_link.data)

    def test_invalid_token_returns_404(self):
        res = self.client.get('/verify-employment/INVALID-NONEXISTENT-TOKEN')
        self.assertEqual(res.status_code, 404)
        self.assertIn(b'Invalid or Expired Link', res.data)

if __name__ == '__main__':
    unittest.main()
