from typing import Dict, Any, List

class MobilityService:
    """
    Workforce Mobility and Geographic Destination Service.
    Analyzes geographic distribution of trained candidates:
    - Intra-state (Within Maharashtra)
    - Interstate (Other Indian States)
    - International (Abroad)
    
    IMPORTANT: Prototype analytics using synthetic demonstration data.
    Clearly designated as: 'Synthetic Prototype Data - Not Government Data'.
    """

    DISCLAIMER = "Synthetic Prototype Data - Not Government Data"

    @classmethod
    def get_mobility_metrics(cls) -> Dict[str, Any]:
        distribution = {
            'maharashtra_pct': 62.0,
            'interstate_pct': 24.0,
            'abroad_pct': 14.0,
            'maharashtra_count': 310,
            'interstate_count': 120,
            'abroad_count': 70,
            'total_placed': 500
        }

        top_interstate = [
            {'state': 'Karnataka', 'city': 'Bengaluru', 'count': 48, 'share_pct': 40.0, 'primary_sector': 'IT and Tech Operations'},
            {'state': 'Gujarat', 'city': 'Surat / Ahmedabad', 'count': 32, 'share_pct': 26.7, 'primary_sector': 'Renewable Energy and Manufacturing'},
            {'state': 'Telangana', 'city': 'Hyderabad', 'count': 24, 'share_pct': 20.0, 'primary_sector': 'ITES and Financial Services'},
            {'state': 'Delhi NCR', 'city': 'Gurugram / Noida', 'count': 16, 'share_pct': 13.3, 'primary_sector': 'Retail and Healthcare Tech'}
        ]

        top_international = [
            {'country': 'United Arab Emirates', 'city': 'Dubai / Abu Dhabi', 'count': 34, 'share_pct': 48.6, 'primary_sector': 'Retail, Logistics and Facility Ops'},
            {'country': 'Germany', 'city': 'Berlin / Frankfurt', 'count': 16, 'share_pct': 22.9, 'primary_sector': 'Solar and Electrical Engineering'},
            {'country': 'Canada', 'city': 'Toronto', 'count': 12, 'share_pct': 17.1, 'primary_sector': 'Healthcare and Assistant Care'},
            {'country': 'United Kingdom', 'city': 'London / Manchester', 'count': 8, 'share_pct': 11.4, 'primary_sector': 'Software and Data Processing'}
        ]

        corridors = [
            {'origin': 'Nashik', 'destination': 'Pune, Maharashtra', 'type': 'Intrastate', 'trainees_count': 42, 'avg_salary': 18500},
            {'origin': 'Nashik', 'destination': 'Bengaluru, Karnataka', 'type': 'Interstate', 'trainees_count': 22, 'avg_salary': 26000},
            {'origin': 'Nashik', 'destination': 'Dubai, UAE', 'type': 'International', 'trainees_count': 14, 'avg_salary': 52000},
            {'origin': 'Nagpur', 'destination': 'Hyderabad, Telangana', 'type': 'Interstate', 'trainees_count': 18, 'avg_salary': 24500},
            {'origin': 'Chhatrapati Sambhajinagar', 'destination': 'Surat, Gujarat', 'type': 'Interstate', 'trainees_count': 15, 'avg_salary': 21000},
            {'origin': 'Ratnagiri', 'destination': 'Mumbai, Maharashtra', 'type': 'Intrastate', 'trainees_count': 35, 'avg_salary': 22000},
            {'origin': 'Pune', 'destination': 'Berlin, Germany', 'type': 'International', 'trainees_count': 8, 'avg_salary': 85000}
        ]

        return {
            'disclaimer': cls.DISCLAIMER,
            'distribution': distribution,
            'top_interstate': top_interstate,
            'top_international': top_international,
            'corridors': corridors
        }
