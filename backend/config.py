import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / '.env')

class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'skilltrack_dev_secret_key_sih26135')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 'yes')
    PORT = int(os.getenv('PORT', 5000))

    # Database settings
    USE_SQLITE = os.getenv('USE_SQLITE', 'true').lower() in ('true', '1', 'yes')
    SQLITE_DB_PATH = BASE_DIR / os.getenv('SQLITE_DB_PATH', 'database/skilltrack.db')

    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'skilltrack_db')

    # Configurable Outcome Score Weights (Total = 100)
    # Prototype formula: clearly labeled as a prototype metric
    WEIGHT_EMPLOYMENT = float(os.getenv('WEIGHT_EMPLOYMENT', 30))
    WEIGHT_RETENTION = float(os.getenv('WEIGHT_RETENTION', 25))
    WEIGHT_RELEVANCE = float(os.getenv('WEIGHT_RELEVANCE', 20))
    WEIGHT_SALARY_GROWTH = float(os.getenv('WEIGHT_SALARY_GROWTH', 15))
    WEIGHT_EMPLOYER_FEEDBACK = float(os.getenv('WEIGHT_EMPLOYER_FEEDBACK', 10))

    # Disclaimer constant
    DATA_DISCLAIMER = "Synthetic Prototype Data — Not Government Data. SkillTrack acts as an outcome-intelligence layer working with existing skilling systems."
