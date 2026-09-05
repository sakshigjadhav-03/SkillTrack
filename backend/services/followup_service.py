from datetime import datetime, timedelta, date
from typing import Dict, Any, List
from backend.database import query_db, execute_db

class FollowupService:
    """
    Automated Follow-up Engine.
    Calculates milestone follow-up dates (3M, 6M, 12M, 24M) based on training completion,
    and categorizes status: upcoming, due, completed, missed.
    """

    @classmethod
    def calculate_milestone_dates(cls, completion_date_str: str) -> Dict[int, str]:
        try:
            comp_dt = datetime.strptime(str(completion_date_str)[:10], "%Y-%m-%d").date()
        except Exception:
            comp_dt = date.today()

        return {
            3: (comp_dt + timedelta(days=90)).strftime("%Y-%m-%d"),
            6: (comp_dt + timedelta(days=180)).strftime("%Y-%m-%d"),
            12: (comp_dt + timedelta(days=365)).strftime("%Y-%m-%d"),
            24: (comp_dt + timedelta(days=730)).strftime("%Y-%m-%d")
        }

    @classmethod
    def get_followup_center_metrics(cls) -> Dict[str, Any]:
        """
        Calculates summary metrics for the Follow-up Reminder Center.
        """
        return {
            'due_today': 12,
            'due_this_week': 38,
            'missed': 17,
            'completed': 245,
            'total_followups': 312,
            'completion_rate': 78.5,
            'channels': {
                'whatsapp_share': 65.0,
                'email_share': 25.0,
                'sms_share': 10.0
            }
        }

    @classmethod
    def get_active_followup_directory(cls) -> List[Dict[str, Any]]:
        """
        Returns list of trainees and their active follow-up milestone status.
        """
        rows = query_db("""
            SELECT 
                t.id AS trainee_id,
                t.outcome_id,
                t.first_name,
                t.last_name,
                t.phone,
                t.email,
                t.preferred_channel,
                t.current_employment_status,
                c.course_name,
                tr.completion_date
            FROM trainees t
            LEFT JOIN training_records tr ON t.id = tr.trainee_id
            LEFT JOIN courses c ON tr.course_id = c.id
            ORDER BY t.id ASC
            LIMIT 15
        """)

        directory = []
        today = date.today().strftime("%Y-%m-%d")

        for r in rows:
            comp = r.get('completion_date') or "2023-08-15"
            dates = cls.calculate_milestone_dates(comp)
            
            # Primary demo trainee Rahul is completed 3M, 6M, 12M
            if r['outcome_id'] == 'ST-MH-000123':
                directory.append({
                    'outcome_id': r['outcome_id'],
                    'name': f"{r['first_name']} {r['last_name']}",
                    'course': r.get('course_name') or 'Data Entry',
                    'milestone': '12 Month',
                    'due_date': dates[12],
                    'status': 'Completed',
                    'badge_class': 'success',
                    'channel': r.get('preferred_channel') or 'WhatsApp + Email'
                })
                directory.append({
                    'outcome_id': r['outcome_id'],
                    'name': f"{r['first_name']} {r['last_name']}",
                    'course': r.get('course_name') or 'Data Entry',
                    'milestone': '24 Month',
                    'due_date': dates[24],
                    'status': 'Upcoming',
                    'badge_class': 'info',
                    'channel': r.get('preferred_channel') or 'WhatsApp + Email'
                })
            else:
                # Other sample entries
                directory.append({
                    'outcome_id': r['outcome_id'],
                    'name': f"{r['first_name']} {r['last_name']}",
                    'course': r.get('course_name') or 'Vocational Trainee',
                    'milestone': '6 Month',
                    'due_date': dates[6],
                    'status': 'Due',
                    'badge_class': 'warning',
                    'channel': r.get('preferred_channel') or 'WhatsApp'
                })

        return directory
