import os
import sys
import json
from pathlib import Path
from datetime import datetime, date

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from werkzeug.security import generate_password_hash
from backend.database import get_db_connection, execute_script, execute_db, query_db
from backend.config import Config
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def init_database():
    """Initializes the database schema and seeds realistic synthetic prototype data."""
    print("=" * 65)
    print("  SkillTrack -- Initializing Database & Seeding Synthetic Data  ")
    print("=" * 65)

    schema_file = BASE_DIR / "database" / "schema.sql"
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    print("[1/4] Executing schema.sql...")
    execute_script(schema_sql)
    print("      [OK] Tables created successfully.")

    # Check if data is already seeded
    existing_users = query_db("SELECT COUNT(*) AS count FROM users", one=True)
    if existing_users and existing_users['count'] > 0:
        print("[Notice] Database already contains seed data. Refreshing demo records...")
        # Clear existing tables in reverse dependency order for clean re-seed
        tables_to_clear = [
            'audit_logs', 'recommendations', 'skill_gaps', 'apprenticeships',
            'self_employment', 'employer_feedback', 'employer_verifications',
            'followups', 'employment_records', 'trainee_skills', 'training_records',
            'consents', 'trainees', 'employers', 'course_skills', 'skills',
            'training_providers', 'courses', 'districts', 'users'
        ]
        for t in tables_to_clear:
            execute_db(f"DELETE FROM {t}")

    print("[2/4] Seeding core users and districts...")

    # Seed Default Users (Passwords hashed using Werkzeug)
    users_data = [
        ('trainee_rahul', 'trainee@skilltrack.in', generate_password_hash('trainee123'), 'trainee'),
        ('employer_tcs', 'employer@tcs.in', generate_password_hash('employer123'), 'employer'),
        ('provider_msdm', 'provider@maharashtra-skills.org', generate_password_hash('provider123'), 'provider'),
        ('admin_gov', 'admin@skilltrack.gov.in', generate_password_hash('admin123'), 'government'),
        ('officer_pune', 'officer.pune@skilltrack.gov.in', generate_password_hash('admin123'), 'government'),
    ]
    for u, e, p, r in users_data:
        execute_db("INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)", (u, e, p, r))

    user_map = {row['username']: row['id'] for row in query_db("SELECT id, username FROM users")}

    # Seed Districts from JSON file
    districts_file = BASE_DIR / "data" / "maharashtra_districts.json"
    if districts_file.exists():
        with open(districts_file, "r", encoding="utf-8") as f:
            districts_list = json.load(f)
            for d in districts_list:
                execute_db(
                    "INSERT INTO districts (id, name, division, lat, lng, total_training_centers) VALUES (%s, %s, %s, %s, %s, %s)",
                    (d['id'], d['name'], d['division'], d['lat'], d['lng'], d.get('total_trained', 200) // 20)
                )
    print("      ✓ Seeded Maharashtra districts.")

    # Seed Courses
    courses = [
        (1, 'CRS-IT-01', 'Data Entry & Office Automation', 'IT & ITES', 240, 'Foundational computer operations, MS Office, documentation, typing and clerical data processing.'),
        (2, 'CRS-RET-02', 'Retail Sales Associate', 'Retail', 180, 'Customer relationship building, POS cash handling, visual merchandising and product pitching.'),
        (3, 'CRS-ELE-03', 'Electrician & Solar Technician', 'Renewable Energy', 300, 'Domestic wiring, solar PV installation, inverter diagnostics, and electrical safety standards.'),
        (4, 'CRS-HLT-04', 'General Duty Healthcare Assistant', 'Healthcare', 360, 'Patient handling, vital signs monitoring, bedside assistance, hygiene, and emergency first aid.'),
        (5, 'CRS-DEV-05', 'Full-Stack Web Development', 'IT & Software', 400, 'HTML, CSS, JavaScript, Python backend development, database management and web deployment.')
    ]
    for cid, ccode, cname, sec, dur, desc in courses:
        execute_db(
            "INSERT INTO courses (id, course_code, course_name, sector, duration_hours, description) VALUES (%s, %s, %s, %s, %s, %s)",
            (cid, ccode, cname, sec, dur, desc)
        )
    print("      ✓ Seeded course curricula.")

    # Seed Master Skills
    skills_data = [
        ('Basic Excel', 'Digital'),
        ('Advanced Excel', 'Digital'),
        ('Data Analysis', 'Technical'),
        ('Data Entry', 'Technical'),
        ('English Typing', 'Practical'),
        ('Communication', 'Soft'),
        ('Problem Solving', 'Soft'),
        ('Customer Service', 'Soft'),
        ('POS Billing', 'Technical'),
        ('Inventory Control', 'Domain'),
        ('Electrical Wiring', 'Technical'),
        ('Solar Panel Installation', 'Technical'),
        ('Inverter Maintenance', 'Technical'),
        ('Patient Care', 'Domain'),
        ('First Aid', 'Practical'),
        ('Vital Signs Monitoring', 'Technical'),
        ('Python', 'Technical'),
        ('JavaScript', 'Technical'),
        ('SQL', 'Technical')
    ]
    for sname, scat in skills_data:
        execute_db("INSERT INTO skills (skill_name, category) VALUES (%s, %s)", (sname, scat))

    skill_map = {row['skill_name']: row['id'] for row in query_db("SELECT id, skill_name FROM skills")}

    # Map Course to Curriculum Skills
    course_skills_map = [
        (1, ['Basic Excel', 'Data Entry', 'English Typing', 'Communication']),
        (2, ['Customer Service', 'POS Billing', 'Inventory Control', 'Communication']),
        (3, ['Electrical Wiring', 'Solar Panel Installation', 'Inverter Maintenance']),
        (4, ['Patient Care', 'First Aid', 'Vital Signs Monitoring', 'Communication']),
        (5, ['Python', 'JavaScript', 'SQL', 'Problem Solving'])
    ]
    for cid, sk_list in course_skills_map:
        for sk in sk_list:
            if sk in skill_map:
                execute_db("INSERT INTO course_skills (course_id, skill_id) VALUES (%s, %s)", (cid, skill_map[sk]))

    # Seed Training Providers
    providers = [
        (1, user_map.get('provider_msdm'), 'PRV-MH-001', 'Maharashtra Skill Development Mission Center', 2, 'contact@pune-msdm.org', '+91 20 25510101', 4.6),
        (2, None, 'PRV-MH-002', 'Vidarbha Vocational & Technical Institute', 3, 'info@vidarbha-tech.org', '+91 712 2567890', 4.2),
        (3, None, 'PRV-MH-003', 'Konkan Coastal Skilling Academy', 6, 'contact@konkan-skill.edu', '+91 22 25334411', 4.5),
        (4, None, 'PRV-MH-004', 'Marathwada Skill Hub', 5, 'admin@marathwada-hub.in', '+91 240 2341234', 4.1)
    ]
    for pid, uid, pcode, pname, did, pemail, pphone, prating in providers:
        execute_db(
            "INSERT INTO training_providers (id, user_id, provider_code, name, district_id, contact_email, phone, rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (pid, uid, pcode, pname, did, pemail, pphone, prating)
        )

    # Seed Employers
    employers = [
        (1, user_map.get('employer_tcs'), 'TCS BPS Services', 'IT & ITES', 2, 'Sunil Deshmukh', 'employer@tcs.in', '+91 20 66011111'),
        (2, None, 'Tech Mahindra Solutions', 'IT & Software', 2, 'Neha Kulkarni', 'hr@techmahindra.com', '+91 20 66022222'),
        (3, None, 'Reliance Retail Hub', 'Retail', 1, 'Prakash Patil', 'careers@relianceretail.com', '+91 22 44778899'),
        (4, None, 'Tata Power Solar Systems', 'Renewable Energy', 4, 'Anand Joshi', 'jobs@tatapower.com', '+91 253 2345678'),
        (5, None, 'Apollo HomeCare Services', 'Healthcare', 6, 'Dr. Rekha Nair', 'hr@apollohomecare.org', '+91 22 28991122')
    ]
    for eid, uid, cname, ind, did, cp, ce, cph in employers:
        execute_db(
            "INSERT INTO employers (id, user_id, company_name, industry, district_id, contact_person, contact_email, phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (eid, uid, cname, ind, did, cp, ce, cph)
        )

    print("[3/4] Seeding demo trainee ST-MH-000123 & longitudinal follow-ups...")

    # Primary SIH Hackathon Demo Trainee: ST-MH-000123
    execute_db(
        """
        INSERT INTO trainees (
            id, user_id, outcome_id, first_name, last_name, gender, dob, phone, email, district_id,
            consent_status, consent_date, consent_version, current_employment_status
        ) VALUES (
            1, %s, 'ST-MH-000123', 'Rahul', 'Sharma', 'Male', '2001-04-12', '+91 9823012345',
            'trainee@skilltrack.in', 2, 'agreed', '2023-08-01 10:30:00', 'v1.0', 'employed'
        )
        """,
        (user_map.get('trainee_rahul'),)
    )

    # Consent audit record
    execute_db(
        "INSERT INTO consents (trainee_id, consent_version, consent_given, ip_address, agreed_at) VALUES (1, 'v1.0', 1, '192.168.1.45', '2023-08-01 10:30:00')"
    )

    # Training record for ST-MH-000123
    execute_db(
        """
        INSERT INTO training_records (
            trainee_id, course_id, provider_id, start_date, completion_date, certification_status, certificate_number, grade
        ) VALUES (
            1, 1, 1, '2023-05-01', '2023-08-15', 'certified', 'CERT-MH-2023-000123', 'A'
        )
        """
    )

    # Skills acquired during training
    for sk in ['Basic Excel', 'Data Entry', 'Communication']:
        if sk in skill_map:
            execute_db("INSERT INTO trainee_skills (trainee_id, skill_id, proficiency_level) VALUES (1, %s, 'Proficient')", (skill_map[sk],))

    # Employment record for ST-MH-000123
    execute_db(
        """
        INSERT INTO employment_records (
            trainee_id, employer_id, employer_name, job_role, employment_type, joining_date, salary_monthly, location_district_id, skills_used_text
        ) VALUES (
            1, 1, 'TCS BPS Services', 'Junior Data Operations Executive', 'Full-time', '2023-09-01', 20000.0, 2, 'MS Excel, ERP data entry, verification, email drafting'
        )
        """
    )

    # Longitudinal Milestones (3, 6, 12 months) showing 33.3% salary progression
    followup_timeline = [
        (1, 3, 'completed', '2023-12-01', '2023-12-05', 'employed', 15000.0, 0.0, 'retained', None, None, 'Completed probation smoothly. Assigned to banking operations team.'),
        (1, 6, 'completed', '2024-03-01', '2024-03-03', 'employed', 17000.0, 13.3, 'retained', None, None, 'Received merit salary adjustment for low error rate in processing.'),
        (1, 12, 'completed', '2024-09-01', '2024-09-02', 'employed', 20000.0, 33.3, 'retained', None, None, 'Promoted to Senior Operations Associate. Sustained 12-month employment!')
    ]
    for tid, m_months, st, ddate, cdate, estatus, sal, sal_growth, ret_st, npr, ar, notes in followup_timeline:
        execute_db(
            """
            INSERT INTO followups (
                trainee_id, milestone_months, status, due_date, completed_date, employment_status,
                current_salary, salary_growth_pct, retention_status, non_placement_reason, attrition_reason, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (tid, m_months, st, ddate, cdate, estatus, sal, sal_growth, ret_st, npr, ar, notes)
        )

    # Employer Verification for ST-MH-000123
    execute_db(
        """
        INSERT INTO employer_verifications (
            employer_id, trainee_id, outcome_id, verification_status, verified_role, verified_joining_date, verified_salary_range, remarks
        ) VALUES (
            1, 1, 'ST-MH-000123', 'verified', 'Junior Data Operations Executive', '2023-09-01', '₹18,000 - ₹22,000', 'Employment and role verified. Candidate is confirmed on rolls.'
        )
        """
    )

    # Employer Feedback identifying workplace skill gaps
    execute_db(
        """
        INSERT INTO employer_feedback (
            employer_id, trainee_id, technical_skills_rating, communication_rating, practical_skills_rating,
            problem_solving_rating, digital_skills_rating, industry_readiness_rating, missing_skills_text, general_feedback
        ) VALUES (
            1, 1, 4, 4, 4, 3, 3, 4, 'Advanced Excel, Data Analysis',
            'Rahul has strong typing speed and dependable basic spreadsheet entry. To advance to senior analytics workflows, candidate needs Advanced Excel (VLOOKUP, Pivot tables, INDEX-MATCH) and introductory data analysis.'
        )
        """
    )

    print("[4/4] Seeding synthetic cohort trainees across Maharashtra districts...")

    # Seed 35 additional realistic trainees to generate rich dashboard charts & distributions
    sample_first_names = ['Sneha', 'Amit', 'Pooja', 'Sachin', 'Priyanka', 'Ganesh', 'Kavita', 'Rohan', 'Dipali', 'Vikram', 'Anjali', 'Mahesh', 'Sunita', 'Swapnil', 'Pallavi', 'Nilesh', 'Sheetal', 'Kiran', 'Meera', 'Akshay', 'Tanvi', 'Sandip', 'Jyoti', 'Chetan', 'Varsha', 'Amol', 'Shweta', 'Pradeep', 'Sarika', 'Dattatray', 'Smita', 'Mangesh', 'Tejaswini', 'Vinod', 'Archana']
    sample_last_names = ['Jadhav', 'Kadam', 'Patil', 'Shinde', 'Gaikwad', 'More', 'Chavan', 'Pawar', 'Bhosale', 'Deshmukh', 'Wagh', 'Sawant', 'Kale', 'Ghadge', 'Thorat', 'Babar', 'Suryavanshi', 'Kamble', 'Kharat', 'Sonawane', 'Dhumal', 'Gholap', 'Nikam', 'Mane', 'Shelar', 'Tambe', 'Lokhande', 'Raut', 'Munde', 'Koli', 'Kute', 'Pingle', 'Borse', 'Shirke', 'Zende']

    unemp_reasons = ['Lack of required skills', 'Low salary offered', 'No suitable jobs in local area', 'Transportation problem', 'Personal/family reasons', 'No interview opportunities']
    attrition_reasons = ['Low salary', 'Better opportunity elsewhere', 'Relocation to hometown', 'Work environment & long hours', 'Skill mismatch', 'Contract ended']

    for i in range(2, 37):
        out_id = f"ST-MH-{100120 + i:06d}"
        fname = sample_first_names[(i - 2) % len(sample_first_names)]
        lname = sample_last_names[(i - 2) % len(sample_last_names)]
        gender = 'Female' if i % 2 == 0 else 'Male'
        did = ((i - 2) % 10) + 1
        cid = ((i - 2) % 5) + 1
        pid = ((i - 2) % 4) + 1
        phone = f"+91 982{i:07d}"
        email = f"{fname.lower()}.{lname.lower()}{i}@example.com"

        # Employment distribution: ~65% employed, ~12% self-employed, ~8% apprentice, ~15% unemployed
        if i % 7 == 0:
            emp_status = 'unemployed'
        elif i % 11 == 0:
            emp_status = 'self_employed'
        elif i % 13 == 0:
            emp_status = 'apprentice'
        else:
            emp_status = 'employed'

        execute_db(
            """
            INSERT INTO trainees (
                id, outcome_id, first_name, last_name, gender, dob, phone, email, district_id,
                consent_status, consent_date, consent_version, current_employment_status
            ) VALUES (
                %s, %s, %s, %s, %s, '2000-01-15', %s, %s, %s, 'agreed', '2023-08-05', 'v1.0', %s
            )
            """,
            (i, out_id, fname, lname, gender, phone, email, did, emp_status)
        )

        execute_db(
            """
            INSERT INTO training_records (
                trainee_id, course_id, provider_id, start_date, completion_date, certification_status, certificate_number
            ) VALUES (%s, %s, %s, '2023-05-01', '2023-08-20', 'certified', %s)
            """,
            (i, cid, pid, f"CERT-MH-2023-{100120+i}")
        )

        # Baseline salaries based on course & experience
        base_sal = 14000.0 + (cid * 1200) + ((i % 5) * 600)

        if emp_status == 'employed':
            eid = ((i - 2) % 5) + 1
            execute_db(
                """
                INSERT INTO employment_records (
                    trainee_id, employer_id, employer_name, job_role, employment_type, joining_date, salary_monthly, location_district_id
                ) VALUES (%s, %s, 'Partner Employer Pvt Ltd', 'Associate Operations Executive', 'Full-time', '2023-09-15', %s, %s)
                """,
                (i, eid, base_sal + 3000, did)
            )
            # Add follow-ups
            execute_db(
                "INSERT INTO followups (trainee_id, milestone_months, status, due_date, completed_date, employment_status, current_salary, salary_growth_pct, retention_status) VALUES (%s, 3, 'completed', '2023-12-15', '2023-12-18', 'employed', %s, 0.0, 'retained')",
                (i, base_sal)
            )
            execute_db(
                "INSERT INTO followups (trainee_id, milestone_months, status, due_date, completed_date, employment_status, current_salary, salary_growth_pct, retention_status) VALUES (%s, 6, 'completed', '2024-03-15', '2024-03-20', 'employed', %s, %s, 'retained')",
                (i, base_sal + 1500, round((1500 / base_sal) * 100, 1))
            )
            execute_db(
                "INSERT INTO followups (trainee_id, milestone_months, status, due_date, completed_date, employment_status, current_salary, salary_growth_pct, retention_status) VALUES (%s, 12, 'completed', '2024-09-15', '2024-09-18', 'employed', %s, %s, 'retained')",
                (i, base_sal + 3500, round((3500 / base_sal) * 100, 1))
            )
            # Employer feedback
            execute_db(
                """
                INSERT INTO employer_feedback (
                    employer_id, trainee_id, technical_skills_rating, communication_rating, practical_skills_rating,
                    problem_solving_rating, digital_skills_rating, industry_readiness_rating, missing_skills_text
                ) VALUES (%s, %s, 4, 3, 4, 3, 3, 4, %s)
                """,
                (eid, i, 'Advanced Excel, Client Communication' if cid == 1 else 'Field Problem Solving, Safety Protocols')
            )
        elif emp_status == 'self_employed':
            execute_db(
                """
                INSERT INTO self_employment (trainee_id, business_name, business_type, start_date, monthly_revenue, workers_employed, is_sustained)
                VALUES (%s, %s, 'Service & Repair Enterprise', '2023-10-01', 24000.0, 2, 1)
                """,
                (i, f"{fname}'s Tech Solutions")
            )
            execute_db(
                "INSERT INTO followups (trainee_id, milestone_months, status, due_date, completed_date, employment_status, current_salary, salary_growth_pct, retention_status) VALUES (%s, 3, 'completed', '2023-12-15', '2023-12-18', 'self_employed', 18000.0, 0.0, 'retained')",
                (i,)
            )
            execute_db(
                "INSERT INTO followups (trainee_id, milestone_months, status, due_date, completed_date, employment_status, current_salary, salary_growth_pct, retention_status) VALUES (%s, 6, 'completed', '2024-03-15', '2024-03-20', 'self_employed', 22000.0, 22.2, 'retained')",
                (i,)
            )
        elif emp_status == 'apprentice':
            execute_db(
                """
                INSERT INTO apprenticeships (trainee_id, company_name, trade, start_date, end_date, stipend_monthly, is_completed, converted_to_regular_job)
                VALUES (%s, 'Maharashtra State Electricity Board', 'Solar Apprentice', '2023-09-01', '2024-03-01', 11500.0, 1, 1)
                """,
                (i,)
            )
            execute_db(
                "INSERT INTO followups (trainee_id, milestone_months, status, due_date, completed_date, employment_status, current_salary, salary_growth_pct, retention_status) VALUES (%s, 3, 'completed', '2023-12-15', '2023-12-18', 'apprentice', 11500.0, 0.0, 'retained')",
                (i,)
            )
        else:
            # Unemployed with non-placement reasons
            reason = unemp_reasons[i % len(unemp_reasons)]
            execute_db(
                """
                INSERT INTO followups (
                    trainee_id, milestone_months, status, due_date, completed_date, employment_status,
                    current_salary, salary_growth_pct, retention_status, non_placement_reason, notes
                ) VALUES (%s, 3, 'completed', '2023-12-15', '2023-12-18', 'unemployed', 0.0, 0.0, 'not_applicable', %s, 'Actively seeking work with closer commute.')
                """,
                (i, reason)
            )

    # Seed Data-Driven Action Recommendations
    recs = [
        ('REC-01', 'Curriculum Modernization', 'Course', 'Data Entry & Office Automation',
         'Workplace skill deficit in modern spreadsheet operations.',
         '68% of employer verifications reported missing skills in Advanced Excel (Pivot tables, formulas) and Data Analysis.',
         'Update course syllabus to include 30 hours of Advanced Excel and automated report generation.',
         'Issue curriculum amendment directive to affiliated training providers across Maharashtra.',
         'High', 'Projected +18% wage employment conversion'),

        ('REC-02', 'Wage Progression & Retention', 'Ecosystem', 'Tier-2 & Tier-3 District Hubs',
         'Early job attrition (6-month mark) driven by entry salaries below regional living wage expectations.',
         '41% of job exit reasons cite low compensation without scheduled wage reviews.',
         'Prioritize empanelling employers offering verifiable retention wage progression bands.',
         'Establish employer outcome score index favoring corporate partners with >75% 1-year retention.',
         'Critical', 'Estimated 24% reduction in early-career turnover'),

        ('REC-03', 'Geographic Access & Transport', 'District Cluster', 'Nashik, Solapur, Amravati',
         'Non-placement due to transportation constraints and lack of local industrial proximity.',
         'Candidate follow-ups cite commute distance and shift timings as the #1 rejection cause.',
         'Introduce 90-day transport allowance stipends and foster localized SME cluster drives.',
         'Partner with Maharashtra State Road Transport for subsidized trainee monthly bus passes.',
         'Medium', 'Estimated +12% female candidate placement uptake')
    ]
    for rid, cat, etype, ename, prob, evid, rec, act, prio, imp in recs:
        execute_db(
            """
            INSERT INTO recommendations (
                id, category, entity_type, entity_name, problem_detected, evidence_data, recommendation_text, suggested_action, priority, impact_potential
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (rid, cat, etype, ename, prob, evid, rec, act, prio, imp)
        )

    print("=" * 65)
    print("  ✓ Database Initialization and Synthetic Seeding Complete!   ")
    print("  Default Demo Accounts:")
    print("    - Trainee:    trainee@skilltrack.in            (trainee123)")
    print("    - Employer:   employer@tcs.in                 (employer123)")
    print("    - Provider:   provider@maharashtra-skills.org (provider123)")
    print("    - Government: admin@skilltrack.gov.in         (admin123)")
    print("=" * 65)

if __name__ == "__main__":
    init_database()
