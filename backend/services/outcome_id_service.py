import re
from backend.database import query_db, execute_db

OUTCOME_ID_REGEX = re.compile(r'^ST-MH-\d{6}$')

def generate_outcome_id() -> str:
    """
    Generates a unique permanent SkillTrack Outcome ID for Maharashtra:
    Format: ST-MH-000123
    """
    # Fetch highest existing ID suffix from trainees table
    last_record = query_db(
        "SELECT outcome_id FROM trainees WHERE outcome_id LIKE 'ST-MH-%' ORDER BY id DESC LIMIT 1",
        one=True
    )
    if last_record and last_record['outcome_id']:
        match = re.search(r'ST-MH-(\d+)', last_record['outcome_id'])
        if match:
            next_num = int(match.group(1)) + 1
            return f"ST-MH-{next_num:06d}"

    return "ST-MH-000101"


def is_valid_outcome_id(outcome_id: str) -> bool:
    """Validates if an Outcome ID matches the ST-MH-XXXXXX format."""
    if not outcome_id or not isinstance(outcome_id, str):
        return False
    return bool(OUTCOME_ID_REGEX.match(outcome_id.strip().upper()))


def lookup_by_outcome_id(outcome_id: str):
    """
    Retrieves the trainee record for an Outcome ID,
    sanitizing sensitive PII to protect trainee privacy.
    """
    if not is_valid_outcome_id(outcome_id):
        return None

    clean_id = outcome_id.strip().upper()
    trainee = query_db(
        """
        SELECT 
            t.id AS trainee_id,
            t.outcome_id,
            t.first_name,
            t.last_name,
            t.gender,
            t.consent_status,
            t.current_employment_status,
            d.name AS district_name,
            c.course_name,
            c.sector,
            tp.name AS provider_name,
            tr.completion_date,
            tr.certification_status
        FROM trainees t
        LEFT JOIN districts d ON t.district_id = d.id
        LEFT JOIN training_records tr ON t.id = tr.trainee_id
        LEFT JOIN courses c ON tr.course_id = c.id
        LEFT JOIN training_providers tp ON tr.provider_id = tp.id
        WHERE t.outcome_id = %s
        """,
        (clean_id,),
        one=True
    )
    return trainee
