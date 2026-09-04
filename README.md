# SkillTrack — From Training to Sustainable Employment

> **SIH Problem Statement SIH26135**: Difficulties in tracking employment outcomes, skill gaps, and the impact of skilling initiatives.

---

## 🏛️ Positioning & Core Philosophy

> **"SkillTrack is NOT another job portal. SkillTrack is NOT another training portal.**  
> **SkillTrack acts as an outcome-intelligence layer that works with existing skilling ecosystems (e.g., Mahaswayam / NSDC), focusing on integrated, longitudinal tracking of employment outcomes, job retention, employer validation, skill gaps, and actionable recommendations."**

The fundamental question SkillTrack answers is:  
> **"What happened to the trainee after training, and did the training actually lead to a relevant and sustainable livelihood?"**

---

## 🚀 Live Demo Story (Jury Walkthrough Flow)

SkillTrack includes pre-seeded, realistic synthetic Maharashtra data supporting the end-to-end hackathon narrative:

1. **The Trainee Journey (`ST-MH-000123`)**:
   - Trainee **Rahul Sharma** completes *Data Entry & Office Automation* at Maharashtra Skill Development Mission Center (Pune).
   - Trainee signs the **Informed Consent** form (Version v1.0).
   - Receives permanent, tamper-proof **Unique Outcome ID**: `ST-MH-000123`.
   - Longitudinal Milestone Progress:
     - **3 Months**: Wage Employed at TCS BPS &bull; Salary: **₹15,000/mo**
     - **6 Months**: Wage Employed at TCS BPS &bull; Salary: **₹17,000/mo** (+13.3%)
     - **12 Months**: Promoted Senior Associate &bull; Salary: **₹20,000/mo** &bull; **Salary Growth = 33.3%**
2. **Employer Verification & 6-Pillar Feedback**:
   - Employer logs in, enters `ST-MH-000123`, and validates employment status on rolls: **Employment Verified ✓**.
   - Rates 6 pillars: Technical, Communication, Practical, Problem Solving, Digital, and Readiness.
   - Identifies workplace missing skills: **Advanced Excel, Data Analysis**.
3. **TF-IDF & Cosine Similarity Relevance Engine**:
   - Compares taught skills (*Basic Excel, Data Entry, English Typing, Communication*) with workplace requirements.
   - Computes **Training → Job Relevance**: **78.0%**.
   - Flags skill gaps: ⚠ *Advanced Excel* and ⚠ *Data Analysis*.
4. **Statewide Analytics & Government Action Engine**:
   - **Employment Rate**: 78.0% | **12-Month Retention Rate**: 71.4%
   - **Interactive Leaflet Map**: Visualizes Maharashtra district performance (Mumbai, Pune, Nagpur, Nashik, etc.).
   - **"Why Analysis"**: Diagnoses root causes for non-placement and early job attrition.
   - **Action Engine**: Generates data-driven policy recommendations:
     > *"Update the Data Entry curriculum to include 30 hours of Advanced Excel and basic data analytics to close the 68% employer gap."*

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
|---|---|
| **Frontend** | HTML5, CSS3, Modern Responsive Bootstrap 5.3, Bootstrap Icons |
| **Backend** | Python 3.11, Flask (Modular Blueprints), Werkzeug (Security & Password Hashing) |
| **Database** | Normalized 20-Table Relational Schema, MySQL 8+ support with seamless zero-friction SQLite fallback |
| **Skill Relevance (NLP)** | Scikit-Learn `TfidfVectorizer`, Cosine Similarity & token-level explainability |
| **Analytics & Data** | Pandas, NumPy |
| **Visualizations** | Chart.js 4.4 |
| **Geographic Mapping** | Leaflet.js + OpenStreetMap |

---

## 🔑 Quick Demo Credentials (1-Click Login Enabled)

For instant evaluation, the login page features **1-Click Evaluator Buttons**:

| Role | Email | Password | Primary Demo Feature |
|---|---|---|---|
| **Trainee** | `trainee@skilltrack.in` | `trainee123` | Permanent Outcome ID `ST-MH-000123`, Consent & Timeline |
| **Employer** | `employer@tcs.in` | `employer123` | Look up `ST-MH-000123`, Verify Badge & 6-Pillar Feedback |
| **Training Provider** | `provider@maharashtra-skills.org` | `provider123` | Cohort conversion, 6M retention & curriculum alerts |
| **Government Admin** | `admin@skilltrack.gov.in` | `admin123` | Statewide Command Center, Leaflet Map & Action Engine |

---

## ⚡ Quickstart Guide

### 1. Environment Activation
```powershell
# Using the pre-configured virtual environment
& "d:\SkillTrack\.venv\Scripts\python.exe" run.py
```

### 2. Access the Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

### 3. Running Automated Tests
```powershell
& "d:\SkillTrack\.venv\Scripts\python.exe" -m unittest tests/test_skilltrack.py
```

---

## ⚖️ Disclaimer
> **Synthetic Prototype Data — Not Government Data.**  
> SkillTrack is an academic hackathon prototype created for Smart India Hackathon (SIH26135). All trainee names, companies, and metric distributions are synthetically generated for demonstration purposes. Formula weights for the Prototype Outcome Score are illustrative.
