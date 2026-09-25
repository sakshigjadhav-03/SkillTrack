import unittest
from backend.app import create_app
from backend.database import query_db, execute_db

class TestVerificationWorkflow(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        # Clean up test accounts
        execute_db("DELETE FROM users WHERE email IN ('testprov@test.org', 'testemp@testcorp.com')")
        execute_db("DELETE FROM training_providers WHERE provider_code = 'PRV-TEST-999'")
        execute_db("DELETE FROM employers WHERE registration_id = 'GST-TEST-999'")

    def tearDown(self):
        execute_db("DELETE FROM users WHERE email IN ('testprov@test.org', 'testemp@testcorp.com')")
        execute_db("DELETE FROM training_providers WHERE provider_code = 'PRV-TEST-999'")
        execute_db("DELETE FROM employers WHERE registration_id = 'GST-TEST-999'")

    def test_homepage_portal_signin_links(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Create Trainee Account', res.data)
        self.assertIn(b'Create Provider Account', res.data)
        self.assertIn(b'Create Employer Account', res.data)
        self.assertIn(b'Login as Employer', res.data)

    def test_provider_registration_verification_and_login_flow(self):
        # 1. Register Provider
        reg_res = self.client.post('/register-provider', data={
            'provider_name': 'Test Apex Academy',
            'registration_id': 'PRV-TEST-999',
            'authorized_person': 'Dr. Test Patil',
            'email': 'testprov@test.org',
            'phone': '+91 9898989898',
            'address': 'Test Campus, MG Road',
            'district_id': 2,
            'state': 'Maharashtra',
            'password': 'providerpass',
            'confirm_password': 'providerpass'
        }, follow_redirects=True)
        self.assertEqual(reg_res.status_code, 200)
        self.assertIn(b'Registration successful. Your Training Provider account is pending Administrator verification.', reg_res.data)

        # 2. Check DB status is pending
        p_row = query_db("SELECT * FROM training_providers WHERE provider_code = 'PRV-TEST-999'", one=True)
        self.assertIsNotNone(p_row)
        self.assertEqual(p_row['verification_status'], 'pending')

        # 3. Attempt Login while pending -> blocked
        login_res = self.client.post('/login', data={
            'role': 'provider',
            'email': 'testprov@test.org',
            'password': 'providerpass'
        }, follow_redirects=True)
        self.assertIn(b'awaiting Administrator verification', login_res.data)

        # 4. Admin verifies provider
        with self.client.session_transaction() as sess:
            sess['user_id'] = 4
            sess['role'] = 'administrator'
            sess['username'] = 'admin_gov'

        # Check admin dashboard shows provider
        admin_page = self.client.get('/government/dashboard')
        self.assertIn(b'provider-records', admin_page.data)
        self.assertIn(b'PRV-TEST-999', admin_page.data)

        # Verify action
        v_res = self.client.post(f"/government/provider/{p_row['id']}/status", data={'status': 'verified'}, follow_redirects=True)
        self.assertEqual(v_res.status_code, 200)
        p_verified = query_db(f"SELECT verification_status FROM training_providers WHERE id = {p_row['id']}", one=True)
        self.assertEqual(p_verified['verification_status'], 'verified')

        # 5. Provider login now succeeds!
        self.client.get('/logout')
        p_ok = self.client.post('/login', data={
            'role': 'provider',
            'email': 'testprov@test.org',
            'password': 'providerpass'
        }, follow_redirects=False)
        self.assertEqual(p_ok.status_code, 302)
        self.assertIn('/provider/dashboard', p_ok.headers['Location'])

        # 6. Admin rejects provider
        with self.client.session_transaction() as sess:
            sess['user_id'] = 4
            sess['role'] = 'administrator'
            sess['username'] = 'admin_gov'
        self.client.post(f"/government/provider/{p_row['id']}/status", data={'status': 'rejected'})
        self.client.get('/logout')

        # Provider login now blocked with rejection message
        p_rej = self.client.post('/login', data={
            'role': 'provider',
            'email': 'testprov@test.org',
            'password': 'providerpass'
        }, follow_redirects=True)
        self.assertIn(b'account verification was rejected', p_rej.data)

    def test_employer_registration_verification_and_login_flow(self):
        # 1. Register Employer
        reg_res = self.client.post('/register-employer', data={
            'company_name': 'Apex Corp Solutions',
            'industry': 'IT & ITES',
            'contact_person': 'Sneha Rao',
            'phone': '+91 9797979797',
            'company_email': 'testemp@testcorp.com',
            'registration_id': 'GST-TEST-999',
            'address': 'Cyber City, Hinjawadi',
            'state': 'Maharashtra',
            'district_id': 2,
            'password': 'employerpass',
            'confirm_password': 'employerpass'
        }, follow_redirects=True)
        self.assertEqual(reg_res.status_code, 200)
        self.assertIn(b'Registration successful. Your Employer account is pending Administrator verification.', reg_res.data)

        # 2. Check DB status is pending
        e_row = query_db("SELECT * FROM employers WHERE registration_id = 'GST-TEST-999'", one=True)
        self.assertIsNotNone(e_row)
        self.assertEqual(e_row['verification_status'], 'pending')

        # 3. Attempt Login while pending -> blocked
        login_res = self.client.post('/login', data={
            'role': 'employer',
            'email': 'testemp@testcorp.com',
            'password': 'employerpass'
        }, follow_redirects=True)
        self.assertIn(b'awaiting Administrator verification', login_res.data)

        # 4. Admin verifies employer
        with self.client.session_transaction() as sess:
            sess['user_id'] = 4
            sess['role'] = 'administrator'
            sess['username'] = 'admin_gov'

        # Check admin dashboard shows employer
        admin_page = self.client.get('/government/dashboard')
        self.assertIn(b'employer-records', admin_page.data)
        self.assertIn(b'GST-TEST-999', admin_page.data)

        # Verify action
        v_res = self.client.post(f"/government/employer/{e_row['id']}/status", data={'status': 'verified'}, follow_redirects=True)
        self.assertEqual(v_res.status_code, 200)
        e_verified = query_db(f"SELECT verification_status FROM employers WHERE id = {e_row['id']}", one=True)
        self.assertEqual(e_verified['verification_status'], 'verified')

        # 5. Employer login now succeeds!
        self.client.get('/logout')
        e_ok = self.client.post('/login', data={
            'role': 'employer',
            'email': 'testemp@testcorp.com',
            'password': 'employerpass'
        }, follow_redirects=False)
        self.assertEqual(e_ok.status_code, 302)
        self.assertIn('/employer/dashboard', e_ok.headers['Location'])

        # 6. Admin rejects employer
        with self.client.session_transaction() as sess:
            sess['user_id'] = 4
            sess['role'] = 'administrator'
            sess['username'] = 'admin_gov'
        self.client.post(f"/government/employer/{e_row['id']}/status", data={'status': 'rejected'})
        self.client.get('/logout')

        # Employer login now blocked with rejection message
        e_rej = self.client.post('/login', data={
            'role': 'employer',
            'email': 'testemp@testcorp.com',
            'password': 'employerpass'
        }, follow_redirects=True)
        self.assertIn(b'account verification was rejected', e_rej.data)


if __name__ == '__main__':
    unittest.main()
