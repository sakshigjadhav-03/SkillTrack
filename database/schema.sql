-- SkillTrack Normalized Database Schema
-- Compatible with MySQL 8+ and SQLite 3

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('trainee', 'employer', 'provider', 'government', 'admin')),
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS districts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    state VARCHAR(50) DEFAULT 'Maharashtra',
    division VARCHAR(100),
    lat REAL NOT NULL,
    lng REAL NOT NULL,
    total_training_centers INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS training_providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    provider_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    district_id INTEGER NOT NULL,
    contact_email VARCHAR(150),
    phone VARCHAR(20),
    rating REAL DEFAULT 4.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (district_id) REFERENCES districts(id)
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code VARCHAR(50) NOT NULL UNIQUE,
    course_name VARCHAR(200) NOT NULL,
    sector VARCHAR(100) NOT NULL,
    duration_hours INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) DEFAULT 'Technical' CHECK (category IN ('Technical', 'Digital', 'Soft', 'Domain', 'Practical'))
);

CREATE TABLE IF NOT EXISTS course_skills (
    course_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    PRIMARY KEY (course_id, skill_id),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trainees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    outcome_id VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    gender VARCHAR(20) CHECK (gender IN ('Male', 'Female', 'Other')),
    dob DATE,
    phone VARCHAR(20),
    email VARCHAR(150),
    district_id INTEGER NOT NULL,
    linkedin_url VARCHAR(255) DEFAULT NULL,
    preferred_channel VARCHAR(50) DEFAULT 'WhatsApp',
    consent_status VARCHAR(20) DEFAULT 'pending' CHECK (consent_status IN ('pending', 'agreed', 'declined')),
    consent_date TIMESTAMP,
    consent_version VARCHAR(20),
    current_employment_status VARCHAR(50) DEFAULT 'unemployed' 
        CHECK (current_employment_status IN ('employed', 'self_employed', 'apprentice', 'unemployed', 'further_education')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (district_id) REFERENCES districts(id)
);

CREATE TABLE IF NOT EXISTS consents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainee_id INTEGER NOT NULL,
    consent_version VARCHAR(20) NOT NULL,
    consent_given INTEGER NOT NULL,
    ip_address VARCHAR(50),
    agreed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainee_id) REFERENCES trainees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS training_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainee_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    provider_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    completion_date DATE NOT NULL,
    certification_status VARCHAR(50) DEFAULT 'certified' CHECK (certification_status IN ('certified', 'completed', 'dropped')),
    certificate_number VARCHAR(100),
    grade VARCHAR(20) DEFAULT 'A',
    FOREIGN KEY (trainee_id) REFERENCES trainees(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id),
    FOREIGN KEY (provider_id) REFERENCES training_providers(id)
);

CREATE TABLE IF NOT EXISTS trainee_skills (
    trainee_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    proficiency_level VARCHAR(50) DEFAULT 'Intermediate',
    PRIMARY KEY (trainee_id, skill_id),
    FOREIGN KEY (trainee_id) REFERENCES trainees(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS employers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    company_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100) NOT NULL,
    district_id INTEGER NOT NULL,
    contact_person VARCHAR(100),
    contact_email VARCHAR(150),
    phone VARCHAR(20),
    is_verified INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (district_id) REFERENCES districts(id)
);

CREATE TABLE IF NOT EXISTS employment_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainee_id INTEGER NOT NULL,
    employer_id INTEGER,
    employer_name VARCHAR(200) NOT NULL,
    job_role VARCHAR(150) NOT NULL,
    employment_type VARCHAR(50) DEFAULT 'Full-time' CHECK (employment_type IN ('Full-time', 'Part-time', 'Contract')),
    joining_date DATE NOT NULL,
    salary_monthly REAL NOT NULL,
    latitude REAL DEFAULT NULL,
    longitude REAL DEFAULT NULL,
    location_district_id INTEGER,
    skills_used_text TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainee_id) REFERENCES trainees(id) ON DELETE CASCADE,
    FOREIGN KEY (employer_id) REFERENCES employers(id) ON DELETE SET NULL,
    FOREIGN KEY (location_district_id) REFERENCES districts(id)
);

CREATE TABLE IF NOT EXISTS followups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainee_id INTEGER NOT NULL,
    milestone_months INTEGER NOT NULL CHECK (milestone_months IN (3, 6, 12, 24)),
    status VARCHAR(50) DEFAULT 'completed' CHECK (status IN ('upcoming', 'completed', 'missed')),
    due_date DATE,
    completed_date DATE,
    employment_status VARCHAR(50) NOT NULL CHECK (employment_status IN ('employed', 'self_employed', 'apprentice', 'unemployed', 'further_education')),
    current_salary REAL,
    salary_growth_pct REAL DEFAULT 0.0,
    retention_status VARCHAR(50) DEFAULT 'retained' CHECK (retention_status IN ('retained', 'at_risk', 'left_job', 'not_applicable')),
    non_placement_reason VARCHAR(255),
    attrition_reason VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainee_id) REFERENCES trainees(id) ON DELETE CASCADE
);



CREATE TABLE IF NOT EXISTS employer_verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employer_id INTEGER NOT NULL,
    trainee_id INTEGER NOT NULL,
    outcome_id VARCHAR(50) NOT NULL,
    verification_status VARCHAR(50) DEFAULT 'verified' CHECK (verification_status IN ('verified', 'rejected', 'pending')),
    verified_role VARCHAR(150),
    verified_joining_date DATE,
    verified_salary_range VARCHAR(100),
    remarks TEXT,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employer_id) REFERENCES employers(id),
    FOREIGN KEY (trainee_id) REFERENCES trainees(id)
);

CREATE TABLE IF NOT EXISTS employer_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employer_id INTEGER NOT NULL,
    trainee_id INTEGER NOT NULL,
    technical_skills_rating INTEGER DEFAULT 4 CHECK (technical_skills_rating BETWEEN 1 AND 5),
    communication_rating INTEGER DEFAULT 4 CHECK (communication_rating BETWEEN 1 AND 5),
    practical_skills_rating INTEGER DEFAULT 4 CHECK (practical_skills_rating BETWEEN 1 AND 5),
    problem_solving_rating INTEGER DEFAULT 3 CHECK (problem_solving_rating BETWEEN 1 AND 5),
    digital_skills_rating INTEGER DEFAULT 3 CHECK (digital_skills_rating BETWEEN 1 AND 5),
    industry_readiness_rating INTEGER DEFAULT 4 CHECK (industry_readiness_rating BETWEEN 1 AND 5),
    missing_skills_text TEXT,
    general_feedback TEXT,
    feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employer_id) REFERENCES employers(id),
    FOREIGN KEY (trainee_id) REFERENCES trainees(id)
);

CREATE TABLE IF NOT EXISTS self_employment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainee_id INTEGER NOT NULL,
    business_name VARCHAR(200) NOT NULL,
    business_type VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    monthly_revenue REAL NOT NULL,
    workers_employed INTEGER DEFAULT 0,
    is_sustained INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainee_id) REFERENCES trainees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS apprenticeships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainee_id INTEGER NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    trade VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    stipend_monthly REAL,
    is_completed INTEGER DEFAULT 1,
    converted_to_regular_job INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainee_id) REFERENCES trainees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS skill_gaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    job_role VARCHAR(150),
    detected_missing_skill VARCHAR(150) NOT NULL,
    frequency_count INTEGER DEFAULT 1,
    relevance_score REAL DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS recommendations (
    id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_name VARCHAR(200) NOT NULL,
    problem_detected TEXT NOT NULL,
    evidence_data TEXT NOT NULL,
    recommendation_text TEXT NOT NULL,
    suggested_action TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'Medium' CHECK (priority IN ('Critical', 'High', 'Medium', 'Low')),
    impact_potential VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    target_entity VARCHAR(100),
    target_id VARCHAR(100),
    details TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS notification_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainee_id INTEGER,
    outcome_id VARCHAR(50),
    channel VARCHAR(50),
    recipient VARCHAR(150),
    message_body TEXT,
    status VARCHAR(50) DEFAULT 'queued',
    is_simulated INTEGER DEFAULT 1,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainee_id) REFERENCES trainees(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS document_verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainee_id INTEGER,
    document_type VARCHAR(100) DEFAULT 'Skill Certificate',
    certificate_number VARCHAR(100),
    issuer VARCHAR(150) DEFAULT 'Maharashtra State Skill Authority',
    verification_status VARCHAR(50) DEFAULT 'verified',
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (trainee_id) REFERENCES trainees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS identity_verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainee_id INTEGER,
    method VARCHAR(100) DEFAULT 'Aadhaar-based verification (Prototype)',
    verification_token VARCHAR(100) DEFAULT 'DEMO-ID-000123',
    is_verified INTEGER DEFAULT 1,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainee_id) REFERENCES trainees(id) ON DELETE CASCADE
);

-- Optimization indexes for high-frequency queries
CREATE INDEX IF NOT EXISTS idx_trainees_outcome_id ON trainees(outcome_id);
CREATE INDEX IF NOT EXISTS idx_trainees_status ON trainees(current_employment_status);
CREATE INDEX IF NOT EXISTS idx_followups_trainee ON followups(trainee_id, milestone_months);
CREATE INDEX IF NOT EXISTS idx_employment_trainee ON employment_records(trainee_id);
CREATE INDEX IF NOT EXISTS idx_verifications_outcome ON employer_verifications(outcome_id);
