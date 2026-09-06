from datetime import datetime
from typing import Dict, Any, List
from backend.database import query_db, execute_db

class NotificationService:
    """
    Simulated Automated Notification & Communication Service.
    Handles queuing and dispatch simulation for WhatsApp, Email, and SMS.
    
    IMPORTANT: Prototype simulation. No real external messages are dispatched.
    Clearly designated as: 'Demo Notification - Simulated for Prototype'.
    """

    DISCLAIMER = "Demo Notification - No real WhatsApp/SMS message sent (Simulated for Prototype)"

    @classmethod
    def run_followup_engine(cls) -> Dict[str, Any]:
        """
        Simulates execution of automated follow-up engine:
        1. Scans due follow-ups
        2. Queues simulated WhatsApp, Email, and SMS reminders
        3. Updates notification logs
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Synthetic engine run results
        identified_count = 12
        whatsapp_queued = 8
        email_queued = 10
        sms_queued = 4

        # Log simulated dispatch for demo trainee Rahul
        sample_msg = "Hello Rahul, your SkillTrack 12-month employment follow-up is due. Please update your current employment status."
        execute_db("""
            INSERT INTO notification_logs (trainee_id, outcome_id, channel, recipient, message_body, status, is_simulated, sent_at)
            VALUES (1, 'ST-MH-000123', 'WhatsApp', '+91 9823012345', %s, 'queued', 1, %s)
        """, (sample_msg, now_str))

        execute_db("""
            INSERT INTO notification_logs (trainee_id, outcome_id, channel, recipient, message_body, status, is_simulated, sent_at)
            VALUES (1, 'ST-MH-000123', 'Email', 'trainee@skilltrack.in', %s, 'queued', 1, %s)
        """, (sample_msg, now_str))

        return {
            'success': True,
            'disclaimer': cls.DISCLAIMER,
            'timestamp': now_str,
            'summary': {
                'identified_count': identified_count,
                'whatsapp_queued': whatsapp_queued,
                'email_queued': email_queued,
                'sms_queued': sms_queued,
                'total_queued': whatsapp_queued + email_queued + sms_queued
            },
            'sample_message': sample_msg,
            'message': 'Follow-Up Engine Execution Completed Successfully (Simulation Mode)'
        }

    @classmethod
    def get_recent_logs(cls, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            logs = query_db("""
                SELECT * FROM notification_logs ORDER BY sent_at DESC LIMIT %s
            """, (limit,))
            if logs:
                return logs
        except Exception:
            pass
        return [
            {
                'outcome_id': 'ST-MH-000123',
                'channel': 'WhatsApp',
                'recipient': '+91 9823012345',
                'message_body': 'Hello Rahul, your SkillTrack 12-month employment follow-up is due. Please update your current status.',
                'status': 'queued',
                'is_simulated': 1,
                'sent_at': '2024-09-02 10:30:00'
            },
            {
                'outcome_id': 'ST-MH-000123',
                'channel': 'Email',
                'recipient': 'trainee@skilltrack.in',
                'message_body': 'SkillTrack Follow-up reminder: Please complete your 12-month employment milestone.',
                'status': 'queued',
                'is_simulated': 1,
                'sent_at': '2024-09-02 10:30:00'
            }
        ]
