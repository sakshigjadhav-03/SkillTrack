# SkillTrack — From Training to Sustainable Employment

> **Smart India Hackathon (SIH) — Problem Statement SIH26135**  
> *Longitudinal Outcome Intelligence & Impact Measurement Platform for Vocational Skilling Ecosystems.*

---

## 🏛️ Executive Summary & Platform Positioning

> **"SkillTrack is NOT another job portal. SkillTrack is NOT another training LMS.**  
> **SkillTrack acts as an outcome-intelligence layer that works alongside existing skilling systems (such as NSDC / State Skill Development Missions), focusing on integrated, longitudinal tracking of employment outcomes, job retention, employer validation, skill gaps, and actionable policy recommendations."**

The central question SkillTrack answers is:  
> **"What happened to the trainee after training, and did the training actually lead to a relevant and sustainable livelihood?"**

---

## 🚀 Key Features

1. **Unique Longitudinal Outcome ID (`ST-MH-XXXXXX`)**:
   - Consent-backed, tamper-proof lifetime outcome identifier issued after training completion.
   - Preserves privacy through data minimization while linking training to employment records.
2. **Multi-Milestone Follow-up Tracking (3, 6, 12 & 24 Months)**:
   - Automated scheduling and simulation across WhatsApp, Email, and SMS notification channels.
   - Captures wage progression, employment continuity, and reason for job attrition or non-placement.
3. **Multi-Employer Verification & Feedback**:
   - Empanelled corporate employers (TCS, Infosys, Tech Mahindra, Reliance, Tata Motors, etc.) can verify trainee employment and rate technical, communication, digital, and workplace skills.
4. **Scikit-Learn TF-IDF Skill Relevance & Gap Engine**:
   - Analyzes course syllabus text against real employer feedback using TF-IDF vectorization and Cosine Similarity.
   - Pinpoints exact missing workplace skills (e.g., *Advanced Excel*, *Data Analysis*).
5. **Early Outcome Risk Radar**:
   - Rule-based risk classification (**HIGH**, **MEDIUM**, **LOW**) evaluating employment status, salary growth, job relevance, and retention signals to recommend proactive interventions before dropouts occur.
6. **Workforce Mobility Intelligence**:
   - Distinguishes intra-state (Maharashtra), interstate (e.g., Karnataka, Delhi, Telangana), and international/cross-border destinations (e.g., UAE, Germany, USA).
   - Interactive district-level and global employment maps powered by Leaflet.js.
7. **What-If Policy Simulator & Cohort Impact**:
   - Interactive policy sandbox forecasting placement and retention uplifts based on curriculum upgrades and stipend levers.
   - Before-and-After cohort comparisons measuring real intervention impact.
8. **Digital Credential & Identity Verification Concepts (Prototype / Mock)**:
   - Simulated DigiLocker certificate verification and Aadhaar-based identity verification tokens (`DEMO-ID-XXXXXX`) with explicit prototype disclosures.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons, Leaflet.js (OpenStreetMap), Chart.js |
| **Backend** | Python 3.11+, Flask (Modular Blueprints), Werkzeug (Security & Password Hashing), Gunicorn WSGI |
| **AI / NLP** | Scikit-Learn (`TfidfVectorizer`, Cosine Similarity), NumPy, Pandas |
| **Database** | Relational schema with zero-friction SQLite fallback (or MySQL / PostgreSQL) |
| **Deployment** | Docker / Render / Railway ready, WSGI-compliant, Cloud Environment-driven |

---

## 🔑 Demo Accounts (1-Click Login Enabled)

For hackathon presentation and evaluation, SkillTrack includes pre-seeded synthetic accounts accessible directly via **Quick 1-Click Role Login** on the home page:

| Role | Demo Email | Password | Primary Demo Features |
|---|---|---|---|
| **Trainee** | `trainee@skilltrack.in` | `trainee123` | Consent, Outcome ID (`ST-MH-000123`), 33.3% Salary Growth Timeline, DigiLocker Verification |
| **Employer** | `employer@tcs.in` | `employer123` | Search Outcome ID, Verify Rolls, Rate 6 Skill Dimensions, Submit Missing Skills |
| **Training Provider** | `provider@maharashtra-skills.org` | `provider123` | Course Cohorts, Syllabus Matching, Placement Performance |
| **Government Admin** | `admin@skilltrack.gov.in` | `admin123` | Command Center, Risk Radar, WHY Engine, District Map, World Map, Recommendations |

---

## 💻 Local Setup & Development

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/SkillTrack.git
cd SkillTrack
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Linux / macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database & Seed Synthetic Data
```bash
python database/init_db.py
```

### 5. Run the Application
```bash
python run.py
```
Open your web browser at: **`http://127.0.0.1:5000`**

### 6. Run Automated Test Suite
```bash
python -m unittest tests/test_skilltrack.py
```

---

## ☁️ Deploying SkillTrack to Cloud (Render / Railway)

SkillTrack is built to run as a **public HTTPS web application** so SIH judges can evaluate it directly without any local installation.

### Option A: 1-Click Deploy on Render via GitHub

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "SkillTrack SIH26135 deployment ready"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/SkillTrack.git
   git push -u origin main
   ```

2. **Create a Web Service on [Render](https://render.com)**:
   - Log in to your Render dashboard.
   - Click **New +** → **Web Service**.
   - Connect your GitHub repository `SkillTrack`.

3. **Configure Service Settings**:
   - **Name**: `skilltrack` (or your preferred name)
   - **Region**: Choose the closest region (e.g., Singapore / Frankfurt)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python database/init_db.py
     ```
   - **Start Command**:
     ```bash
     gunicorn run:app
     ```
   - **Instance Type**: Free

4. **Environment Variables**:
   Under **Advanced** → **Environment Variables**, add:
   | Key | Value |
   |---|---|
   | `FLASK_ENV` | `production` |
   | `FLASK_DEBUG` | `False` |
   | `USE_SQLITE` | `true` |
   | `SECRET_KEY` | *(Generate a random string or click Generate)* |

5. **Deploy & Access**:
   - Click **Create Web Service**.
   - Render will run the build, seed the database, and launch Gunicorn.
   - Once deployed, Render provides your public HTTPS URL (e.g., `https://skilltrack-xxxx.onrender.com`).
   - Open this URL in any browser (Chrome, Edge, Safari) to view the live platform!

---

## 🔍 Health Check & System Monitoring

- **Endpoint**: `/health`
- **Response**:
  ```json
  {
    "status": "ok",
    "app": "SkillTrack",
    "service": "Longitudinal Skilling Outcomes Engine",
    "sih_code": "SIH26135"
  }
  ```

---

## ⚠️ Academic Prototype & Synthetic Data Disclaimer

> **Synthetic Prototype Data — Not Government Data**  
> SkillTrack is an academic hackathon prototype created for Smart India Hackathon (SIH26135). All trainee profiles, employer records, salaries, coordinates, and survey responses are realistically modeled synthetic demo data designed to demonstrate longitudinal tracking capabilities. External integrations (DigiLocker, Aadhaar, WhatsApp) are simulated prototype implementations and do not connect to live government servers or collect real citizen credentials.
