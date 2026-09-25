import unittest
from backend.app import create_app
from backend.database import query_db, execute_db

class TestRoleSeparation(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_employer_login_opens_employer_dashboard_only(self):
        # Login as employer_tcs
        res = self.client.post('/login', data={
            'role': 'employer',
            'email': 'employer@tcs.in',
            'password': 'employer123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Employer Dashboard', res.data)
        self.assertIn(b'A. Employment Verification Requests', res.data)
        self.assertIn(b'B. Workplace Skill Feedback', res.data)
        self.assertIn(b'C. Employer Skill Requirements &amp; Deficiencies', res.data)
        self.assertIn(b'D. Verification History', res.data)
        # Verify employer does NOT see provider or admin content
        self.assertNotIn(b'Enrolled Trainee Cohort Directory', res.data)
        self.assertNotIn(b'Course Outcome Intelligence', res.data)
        self.assertNotIn(b'Curriculum Skill Gaps', res.data)
        self.assertNotIn(b'Outcome Risk Radar', res.data)
        self.assertNotIn(b'What-if Simulator', res.data)

    def test_provider_login_opens_provider_dashboard_only(self):
        # Login as provider_msdm
        res = self.client.post('/login', data={
            'role': 'provider',
            'email': 'provider@maharashtra-skills.org',
            'password': 'provider123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Training Provider Dashboard', res.data)
        self.assertIn(b'Enrolled Trainee Cohort Directory', res.data)
        self.assertIn(b'Employer Verification Requests Console', res.data)
        self.assertIn(b'Follow-up Reminder Center', res.data)
        self.assertIn(b'View Certificate', res.data)
        # Verify provider does NOT see admin or employer private dashboard
        self.assertNotIn(b'What-if Simulator', res.data)
        self.assertNotIn(b'A. Employment Verification Requests', res.data)

    def test_role_based_access_control_isolation(self):
        # 1. Employer cannot access Provider dashboard
        with self.client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['role'] = 'employer'
            sess['employer_id'] = 1
        prov_res = self.client.get('/provider/dashboard', follow_redirects=True)
        self.assertIn(b'You do not have permission to view this section', prov_res.data)

        # 2. Provider cannot access Employer dashboard
        with self.client.session_transaction() as sess:
            sess['user_id'] = 3
            sess['role'] = 'provider'
            sess['provider_id'] = 1
        emp_res = self.client.get('/employer/dashboard', follow_redirects=True)
        self.assertIn(b'You do not have permission to view this section', emp_res.data)

        # 3. Provider cannot access Administrator dashboard
        gov_res = self.client.get('/government/dashboard', follow_redirects=True)
        self.assertIn(b'You do not have permission to view this section', gov_res.data)

        # 4. Trainee cannot access Employer, Provider, or Administrator dashboard
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'trainee'
            sess['trainee_id'] = 1
        t_to_emp = self.client.get('/employer/dashboard', follow_redirects=True)
        self.assertIn(b'You do not have permission to view this section', t_to_emp.data)
        t_to_prov = self.client.get('/provider/dashboard', follow_redirects=True)
        self.assertIn(b'You do not have permission to view this section', t_to_prov.data)
        t_to_gov = self.client.get('/government/dashboard', follow_redirects=True)
        self.assertIn(b'You do not have permission to view this section', t_to_gov.data)

    def test_employer_verification_actions_and_skill_feedback(self):
        # As Employer
        with self.client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['role'] = 'employer'
            sess['employer_id'] = 1
            sess['company_name'] = 'TCS BPS Services'

        # Action 1: Confirm Verification
        confirm_res = self.client.post('/employer/verify', data={
            'outcome_id': 'ST-MH-000123',
            'action': 'confirm',
            'verified_role': 'Senior Data Operator',
            'verified_joining_date': '2023-09-01',
            'verified_salary_range': '₹18,000 - ₹22,000',
            'remarks': 'Role confirmed on active rolls'
        }, follow_redirects=True)
        self.assertEqual(confirm_res.status_code, 200)
        self.assertIn(b'Employment verified', confirm_res.data)

        # Action 2: Submit Workplace Skill Feedback
        fb_res = self.client.post('/employer/feedback/ST-MH-000123', data={
            'technical_skills_rating': 5,
            'communication_rating': 4,
            'problem_solving_rating': 4,
            'teamwork_rating': 5,
            'practical_skills_rating': 5,
            'digital_skills_rating': 4,
            'industry_readiness_rating': 5,
            'missing_skills_text': 'Advanced Excel, PowerBI Dashboarding',
            'general_feedback': 'Strong performer with consistent accuracy.'
        }, follow_redirects=True)
        self.assertEqual(fb_res.status_code, 200)
        self.assertIn(b'Workplace skill feedback and employer requirements recorded', fb_res.data)

        # Check DB updated
        fb_row = query_db("SELECT * FROM employer_feedback WHERE employer_id = 1 AND trainee_id = 1", one=True)
        self.assertIsNotNone(fb_row)
        self.assertEqual(fb_row['teamwork_rating'], 5)
        self.assertIn('PowerBI', fb_row['missing_skills_text'])

    def test_provider_initiate_verification_request_flow(self):
        # As Training Provider
        with self.client.session_transaction() as sess:
            sess['user_id'] = 3
            sess['role'] = 'provider'
            sess['provider_id'] = 1
            sess['provider_name'] = 'MSDM Center'

        # Dispatch verification request
        req_res = self.client.post('/provider/request-verification', data={
            'trainee_id': 1,
            'outcome_id': 'ST-MH-000123',
            'employer_id': 1,
            'job_role': 'Junior Data Operations Executive',
            'joining_date': '2023-09-01',
            'salary_range': '₹18,000 - ₹22,000',
            'notes': 'Candidate completed accredited training'
        }, follow_redirects=True)
        self.assertEqual(req_res.status_code, 200)
        self.assertIn(b'Employer verification request successfully dispatched', req_res.data)

        # Verify DB status is pending for this request
        ev = query_db("SELECT * FROM employer_verifications WHERE employer_id = 1 AND trainee_id = 1", one=True)
        self.assertEqual(ev['verification_status'], 'pending')
