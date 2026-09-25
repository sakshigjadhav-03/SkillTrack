import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.services.mobility_service import MobilityService

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class GeographicService:
    """
    Hierarchical Geographic Intelligence Service for SkillTrack.
    Supports navigation hierarchy:
    World -> Country -> India -> State / UT -> District -> Outcome Details
    
    Also supports Workforce Mobility:
    Intrastate, Interstate, and International migration corridors.
    """

    DISCLAIMER = "Synthetic Prototype Data — Not Government Data"

    @classmethod
    def get_world_data(cls) -> Dict[str, Any]:
        """Returns country-level outcome metrics, international destinations, and global mobility corridors."""
        countries_with_data = {
            "India": {
                "name": "India",
                "code": "IND",
                "has_data": True,
                "trainees_tracked": 4350,
                "employment_rate": 78.4,
                "retention_rate": 71.4,
                "avg_salary": 18400,
                "outcome_score": 81.2,
                "top_sectors": ["IT & ITES", "Retail", "Renewable Energy", "Healthcare", "Manufacturing"],
                "top_skills": ["Advanced Excel", "Data Analysis", "Solar PV Diagnostics", "Industrial Electrical"],
                "center": [22.5937, 78.9629],
                "zoom": 4.5,
                "is_domestic_hub": True
            },
            "United Arab Emirates": {
                "name": "United Arab Emirates",
                "code": "ARE",
                "has_data": True,
                "trainees_tracked": 34,
                "employment_rate": 88.2,
                "retention_rate": 82.4,
                "avg_salary": 52000,
                "outcome_score": 87.5,
                "primary_city": "Dubai / Abu Dhabi",
                "top_sectors": ["Retail", "Logistics", "Facility Operations"],
                "top_skills": ["Supply Chain Management", "Inventory Systems", "English Communication"],
                "center": [24.4539, 54.3773],
                "zoom": 6
            },
            "Germany": {
                "name": "Germany",
                "code": "DEU",
                "has_data": True,
                "trainees_tracked": 16,
                "employment_rate": 93.8,
                "retention_rate": 87.5,
                "avg_salary": 85000,
                "outcome_score": 92.0,
                "primary_city": "Berlin / Frankfurt",
                "top_sectors": ["Solar & Renewable Energy", "Electrical Engineering"],
                "top_skills": ["Solar PV Diagnostics", "Industrial Automation", "Workplace Safety"],
                "center": [51.1657, 10.4515],
                "zoom": 6
            },
            "Canada": {
                "name": "Canada",
                "code": "CAN",
                "has_data": True,
                "trainees_tracked": 12,
                "employment_rate": 91.7,
                "retention_rate": 83.3,
                "avg_salary": 78000,
                "outcome_score": 88.5,
                "primary_city": "Toronto",
                "top_sectors": ["Healthcare", "Assistant Care"],
                "top_skills": ["Patient Care", "Emergency First Aid", "Medical Documentation"],
                "center": [56.1304, -106.3468],
                "zoom": 4
            },
            "United Kingdom": {
                "name": "United Kingdom",
                "code": "GBR",
                "has_data": True,
                "trainees_tracked": 8,
                "employment_rate": 87.5,
                "retention_rate": 87.5,
                "avg_salary": 92000,
                "outcome_score": 89.0,
                "primary_city": "London / Manchester",
                "top_sectors": ["IT & Software", "Data Processing"],
                "top_skills": ["Full-Stack Development", "Python", "Database Management"],
                "center": [55.3781, -3.4360],
                "zoom": 6
            },
            "United States of America": {
                "name": "United States of America",
                "code": "USA",
                "has_data": True,
                "trainees_tracked": 6,
                "employment_rate": 83.3,
                "retention_rate": 83.3,
                "avg_salary": 95000,
                "outcome_score": 86.0,
                "primary_city": "New York",
                "top_sectors": ["Tech & Operations", "Logistics"],
                "top_skills": ["Cloud Infrastructure", "Client Operations"],
                "center": [37.0902, -95.7129],
                "zoom": 4
            }
        }

        # International Corridors (India -> Abroad)
        international_corridors = [
            {
                "origin": "India (Maharashtra)",
                "origin_coords": [19.7515, 75.7139],
                "destination": "United Arab Emirates (Dubai)",
                "destination_coords": [25.2048, 55.2708],
                "trainees_count": 14,
                "avg_salary": 52000,
                "primary_sector": "Retail, Logistics & Facility Ops",
                "type": "International"
            },
            {
                "origin": "India (Maharashtra)",
                "origin_coords": [19.7515, 75.7139],
                "destination": "Germany (Berlin)",
                "destination_coords": [52.5200, 13.4050],
                "trainees_count": 8,
                "avg_salary": 85000,
                "primary_sector": "Solar and Electrical Engineering",
                "type": "International"
            },
            {
                "origin": "India (Maharashtra)",
                "origin_coords": [19.7515, 75.7139],
                "destination": "Canada (Toronto)",
                "destination_coords": [43.6532, -79.3832],
                "trainees_count": 6,
                "avg_salary": 78000,
                "primary_sector": "Healthcare and Assistant Care",
                "type": "International"
            },
            {
                "origin": "India (Maharashtra)",
                "origin_coords": [19.7515, 75.7139],
                "destination": "United Kingdom (London)",
                "destination_coords": [51.5074, -0.1278],
                "trainees_count": 4,
                "avg_salary": 92000,
                "primary_sector": "Software & Data Processing",
                "type": "International"
            }
        ]

        return {
            "disclaimer": cls.DISCLAIMER,
            "countries_with_data": countries_with_data,
            "international_corridors": international_corridors,
            "total_international_placed": 70
        }

    @classmethod
    def get_india_data(cls) -> Dict[str, Any]:
        """Returns India state-level outcome metrics, interstate destinations, and corridors."""
        states_with_data = {
            "Maharashtra": {
                "name": "Maharashtra",
                "code": "MH",
                "type": "State",
                "has_data": True,
                "trainees_tracked": 3850,
                "employment_rate": 78.5,
                "retention_rate": 72.0,
                "avg_salary": 18200,
                "outcome_score": 81.5,
                "capital": "Mumbai",
                "districts_count": 36,
                "top_sectors": ["IT & ITES", "Manufacturing", "Renewable Energy", "Retail", "Healthcare"],
                "top_skills": ["Advanced Excel", "Data Analysis", "Industrial Automation", "Solar Diagnostics"],
                "center": [19.7515, 75.7139],
                "zoom": 6.8,
                "is_primary": True
            },
            "Karnataka": {
                "name": "Karnataka",
                "code": "KA",
                "type": "State",
                "has_data": True,
                "trainees_tracked": 48,
                "employment_rate": 81.5,
                "retention_rate": 79.2,
                "avg_salary": 26000,
                "outcome_score": 83.8,
                "capital": "Bengaluru",
                "primary_hub": "Bengaluru Urban",
                "top_sectors": ["IT & Tech Operations", "Electronics"],
                "top_skills": ["Python", "Cloud Ops", "Data Analytics"],
                "center": [15.3173, 75.7139],
                "zoom": 7
            },
            "Gujarat": {
                "name": "Gujarat",
                "code": "GJ",
                "type": "State",
                "has_data": True,
                "trainees_tracked": 32,
                "employment_rate": 77.2,
                "retention_rate": 75.0,
                "avg_salary": 21000,
                "outcome_score": 78.4,
                "capital": "Gandhinagar",
                "primary_hub": "Surat / Ahmedabad",
                "top_sectors": ["Renewable Energy", "Manufacturing", "Textiles"],
                "top_skills": ["Industrial Automation", "Solar PV Installation", "Supply Chain"],
                "center": [22.2587, 71.1924],
                "zoom": 7
            },
            "Telangana": {
                "name": "Telangana",
                "code": "TG",
                "type": "State",
                "has_data": True,
                "trainees_tracked": 24,
                "employment_rate": 79.0,
                "retention_rate": 76.5,
                "avg_salary": 24500,
                "outcome_score": 80.2,
                "capital": "Hyderabad",
                "primary_hub": "Hyderabad",
                "top_sectors": ["ITES", "FinTech", "Bio-Pharma Logistics"],
                "top_skills": ["FinTech Operations", "Client Communication", "SQL"],
                "center": [17.8496, 79.1152],
                "zoom": 7
            },
            "Delhi": {
                "name": "Delhi",
                "code": "DL",
                "type": "Union Territory",
                "has_data": True,
                "trainees_tracked": 16,
                "employment_rate": 75.0,
                "retention_rate": 72.0,
                "avg_salary": 23500,
                "outcome_score": 77.0,
                "capital": "New Delhi",
                "primary_hub": "National Capital Region",
                "top_sectors": ["Retail", "Healthcare Tech", "e-Commerce"],
                "top_skills": ["CRM Software", "Medical Records", "English Communication"],
                "center": [28.7041, 77.1025],
                "zoom": 9
            },
            "Tamil Nadu": {
                "name": "Tamil Nadu",
                "code": "TN",
                "type": "State",
                "has_data": True,
                "trainees_tracked": 18,
                "employment_rate": 76.5,
                "retention_rate": 73.0,
                "avg_salary": 22000,
                "outcome_score": 77.8,
                "capital": "Chennai",
                "primary_hub": "Chennai / Coimbatore",
                "top_sectors": ["Automotive", "Electronics Assembly"],
                "top_skills": ["Automotive Fitting", "Quality Testing", "Team Collaboration"],
                "center": [11.1271, 78.6569],
                "zoom": 7
            }
        }

        # Interstate Corridors
        interstate_corridors = [
            {
                "origin": "Nashik, Maharashtra",
                "origin_coords": [19.9975, 73.7898],
                "destination": "Bengaluru, Karnataka",
                "destination_coords": [12.9716, 77.5946],
                "trainees_count": 22,
                "avg_salary": 26000,
                "primary_sector": "IT & Tech Operations",
                "type": "Interstate"
            },
            {
                "origin": "Nagpur, Maharashtra",
                "origin_coords": [21.1458, 79.0882],
                "destination": "Hyderabad, Telangana",
                "destination_coords": [17.3850, 78.4867],
                "trainees_count": 18,
                "avg_salary": 24500,
                "primary_sector": "ITES and Financial Services",
                "type": "Interstate"
            },
            {
                "origin": "Chhatrapati Sambhajinagar, Maharashtra",
                "origin_coords": [19.8762, 75.3433],
                "destination": "Surat, Gujarat",
                "destination_coords": [21.1702, 72.8311],
                "trainees_count": 15,
                "avg_salary": 21000,
                "primary_sector": "Renewable Energy and Manufacturing",
                "type": "Interstate"
            },
            {
                "origin": "Pune, Maharashtra",
                "origin_coords": [18.5204, 73.8567],
                "destination": "Delhi NCR (Gurugram)",
                "destination_coords": [28.4595, 77.0266],
                "trainees_count": 12,
                "avg_salary": 23500,
                "primary_sector": "Retail and Healthcare Tech",
                "type": "Interstate"
            },
            {
                "origin": "Pune, Maharashtra",
                "origin_coords": [18.5204, 73.8567],
                "destination": "Chennai, Tamil Nadu",
                "destination_coords": [13.0827, 80.2707],
                "trainees_count": 10,
                "avg_salary": 22000,
                "primary_sector": "Automotive Fitting & Quality Testing",
                "type": "Interstate"
            }
        ]

        return {
            "disclaimer": cls.DISCLAIMER,
            "states_with_data": states_with_data,
            "interstate_corridors": interstate_corridors
        }

    @classmethod
    def get_state_districts(cls, state_name: str) -> Dict[str, Any]:
        """Returns district-level outcome records and intrastate mobility corridors for a given state."""
        state_key = state_name.strip().title()

        if state_key == "Maharashtra":
            districts_file = BASE_DIR / "data" / "maharashtra_districts.json"
            districts = []
            if districts_file.exists():
                with open(districts_file, "r", encoding="utf-8") as f:
                    districts = json.load(f)

            intrastate_corridors = [
                {"origin": "Nashik", "origin_coords": [19.9975, 73.7898], "destination": "Pune", "destination_coords": [18.5204, 73.8567], "trainees_count": 42, "avg_salary": 18500, "sector": "Auto & Engineering", "type": "Intrastate"},
                {"origin": "Ratnagiri", "origin_coords": [16.9902, 73.3120], "destination": "Mumbai", "destination_coords": [19.0760, 72.8777], "trainees_count": 35, "avg_salary": 22000, "sector": "Logistics & Maritime", "type": "Intrastate"},
                {"origin": "Solapur", "origin_coords": [17.6599, 75.9064], "destination": "Pune", "destination_coords": [18.5204, 73.8567], "trainees_count": 28, "avg_salary": 19000, "sector": "Manufacturing & Operations", "type": "Intrastate"},
                {"origin": "Kolhapur", "origin_coords": [16.7050, 74.2433], "destination": "Pune", "destination_coords": [18.5204, 73.8567], "trainees_count": 25, "avg_salary": 18800, "sector": "Industrial Machining", "type": "Intrastate"},
                {"origin": "Chhatrapati Sambhajinagar", "origin_coords": [19.8762, 75.3433], "destination": "Pune", "destination_coords": [18.5204, 73.8567], "trainees_count": 20, "avg_salary": 19200, "sector": "Auto-CAD & Diagnostics", "type": "Intrastate"},
                {"origin": "Amravati", "origin_coords": [20.9374, 77.7796], "destination": "Nagpur", "destination_coords": [21.1458, 79.0882], "trainees_count": 24, "avg_salary": 16500, "sector": "Healthcare & Clerical", "type": "Intrastate"}
            ]

            return {
                "state": "Maharashtra",
                "has_data": True,
                "districts": districts,
                "corridors": intrastate_corridors,
                "center": [19.7515, 75.7139],
                "zoom": 7
            }

        elif state_key == "Karnataka":
            districts = [
                {
                    "id": 101,
                    "name": "Bengaluru Urban",
                    "division": "Bengaluru",
                    "lat": 12.9716,
                    "lng": 77.5946,
                    "total_trained": 48,
                    "employment_rate": 81.5,
                    "retention_rate": 79.2,
                    "avg_salary": 26000,
                    "top_skill_gaps": ["Cloud Infrastructure", "DevOps Pipelines", "Python"],
                    "has_data": True
                },
                {
                    "id": 102,
                    "name": "Mysuru",
                    "division": "Mysuru",
                    "lat": 12.2958,
                    "lng": 76.6394,
                    "total_trained": 15,
                    "employment_rate": 74.0,
                    "retention_rate": 71.0,
                    "avg_salary": 21000,
                    "top_skill_gaps": ["IoT Operations", "Testing Automation"],
                    "has_data": True
                }
            ]
            return {
                "state": "Karnataka",
                "has_data": True,
                "districts": districts,
                "corridors": [
                    {"origin": "Mysuru", "origin_coords": [12.2958, 76.6394], "destination": "Bengaluru Urban", "destination_coords": [12.9716, 77.5946], "trainees_count": 12, "avg_salary": 25000, "sector": "Tech Operations", "type": "Intrastate"}
                ],
                "center": [15.3173, 75.7139],
                "zoom": 7
            }

        elif state_key == "Gujarat":
            districts = [
                {
                    "id": 201,
                    "name": "Surat",
                    "division": "South Gujarat",
                    "lat": 21.1702,
                    "lng": 72.8311,
                    "total_trained": 32,
                    "employment_rate": 77.2,
                    "retention_rate": 75.0,
                    "avg_salary": 21000,
                    "top_skill_gaps": ["Solar Panel Maintenance", "Industrial Automation", "Supply Chain"],
                    "has_data": True
                },
                {
                    "id": 202,
                    "name": "Ahmedabad",
                    "division": "Central Gujarat",
                    "lat": 23.0225,
                    "lng": 72.5714,
                    "total_trained": 20,
                    "employment_rate": 78.5,
                    "retention_rate": 74.2,
                    "avg_salary": 22500,
                    "top_skill_gaps": ["Quality Assurance", "ERP Systems"],
                    "has_data": True
                }
            ]
            return {
                "state": "Gujarat",
                "has_data": True,
                "districts": districts,
                "corridors": [
                    {"origin": "Surat", "origin_coords": [21.1702, 72.8311], "destination": "Ahmedabad", "destination_coords": [23.0225, 72.5714], "trainees_count": 14, "avg_salary": 22000, "sector": "Manufacturing", "type": "Intrastate"}
                ],
                "center": [22.2587, 71.1924],
                "zoom": 7
            }

        elif state_key == "Telangana":
            districts = [
                {
                    "id": 301,
                    "name": "Hyderabad",
                    "division": "Hyderabad",
                    "lat": 17.3850,
                    "lng": 78.4867,
                    "total_trained": 24,
                    "employment_rate": 79.0,
                    "retention_rate": 76.5,
                    "avg_salary": 24500,
                    "top_skill_gaps": ["FinTech APIs", "Data Warehousing", "Client Relations"],
                    "has_data": True
                }
            ]
            return {
                "state": "Telangana",
                "has_data": True,
                "districts": districts,
                "corridors": [],
                "center": [17.8496, 79.1152],
                "zoom": 7
            }

        elif state_key == "Delhi":
            districts = [
                {
                    "id": 401,
                    "name": "New Delhi (NCR)",
                    "division": "Delhi NCR",
                    "lat": 28.6139,
                    "lng": 77.2090,
                    "total_trained": 16,
                    "employment_rate": 75.0,
                    "retention_rate": 72.0,
                    "avg_salary": 23500,
                    "top_skill_gaps": ["Retail Tech", "Healthcare Billing", "Communication"],
                    "has_data": True
                }
            ]
            return {
                "state": "Delhi",
                "has_data": True,
                "districts": districts,
                "corridors": [],
                "center": [28.7041, 77.1025],
                "zoom": 9
            }

        elif state_key == "Tamil Nadu":
            districts = [
                {
                    "id": 501,
                    "name": "Chennai",
                    "division": "Chennai",
                    "lat": 13.0827,
                    "lng": 80.2707,
                    "total_trained": 18,
                    "employment_rate": 76.5,
                    "retention_rate": 73.0,
                    "avg_salary": 22000,
                    "top_skill_gaps": ["Embedded Systems", "Automotive CAD", "Team Leadership"],
                    "has_data": True
                }
            ]
            return {
                "state": "Tamil Nadu",
                "has_data": True,
                "districts": districts,
                "corridors": [],
                "center": [11.1271, 78.6569],
                "zoom": 7
            }

        else:
            # Region with no data
            return {
                "state": state_name,
                "has_data": False,
                "message": "No outcome data available for this state.",
                "districts": [],
                "corridors": []
            }

    @classmethod
    def search_locations(cls, query: str) -> List[Dict[str, Any]]:
        """Searches across countries, Indian states, UTs, and districts."""
        q = query.strip().lower()
        if not q:
            return []

        results = []

        # 1. Countries
        world = cls.get_world_data()
        for cname, cdata in world["countries_with_data"].items():
            if q in cname.lower() or (cdata.get("code") and q in cdata["code"].lower()) or (cname == "United Arab Emirates" and q in ["uae", "dubai"]):
                results.append({
                    "title": cname,
                    "type": "Country",
                    "level": "country",
                    "country": cname,
                    "has_data": cdata["has_data"],
                    "center": cdata["center"],
                    "zoom": cdata["zoom"],
                    "badge": f"{cdata['trainees_tracked']} Trainees" if cdata.get("trainees_tracked") else "No data"
                })

        # Add India if searched
        if q in "india":
            results.append({
                "title": "India",
                "type": "Country",
                "level": "india",
                "country": "India",
                "has_data": True,
                "center": [22.5937, 78.9629],
                "zoom": 5,
                "badge": "4,350 Trainees"
            })

        # 2. Indian States and UTs
        india = cls.get_india_data()
        # All 36 states and UTs
        all_states = [
            ("Maharashtra", "State", [19.7515, 75.7139]),
            ("Karnataka", "State", [15.3173, 75.7139]),
            ("Gujarat", "State", [22.2587, 71.1924]),
            ("Telangana", "State", [17.8496, 79.1152]),
            ("Delhi", "Union Territory", [28.7041, 77.1025]),
            ("Tamil Nadu", "State", [11.1271, 78.6569]),
            ("Andhra Pradesh", "State", [15.9129, 79.7400]),
            ("Kerala", "State", [10.8505, 76.2711]),
            ("Madhya Pradesh", "State", [22.9734, 78.6569]),
            ("Rajasthan", "State", [27.0238, 74.2179]),
            ("Uttar Pradesh", "State", [26.8467, 80.9462]),
            ("West Bengal", "State", [22.9868, 87.8550]),
            ("Bihar", "State", [25.0961, 85.3131]),
            ("Odisha", "State", [20.9517, 85.0985]),
            ("Punjab", "State", [31.1471, 75.3412]),
            ("Haryana", "State", [29.0588, 76.0856]),
            ("Jharkhand", "State", [23.6102, 85.2799]),
            ("Chhattisgarh", "State", [21.2787, 81.8661]),
            ("Assam", "State", [26.2006, 92.9376]),
            ("Jammu and Kashmir", "Union Territory", [33.7782, 76.5762]),
            ("Ladakh", "Union Territory", [34.1526, 77.5771]),
            ("Himachal Pradesh", "State", [31.1048, 77.1734]),
            ("Uttarakhand", "State", [30.0668, 79.0193]),
            ("Goa", "State", [15.2993, 74.1240]),
            ("Sikkim", "State", [27.5330, 88.5122]),
            ("Arunachal Pradesh", "State", [28.2180, 94.7278]),
            ("Meghalaya", "State", [25.4670, 91.3662]),
            ("Manipur", "State", [24.6637, 93.9063]),
            ("Nagaland", "State", [26.1584, 94.5624]),
            ("Mizoram", "State", [23.1645, 92.9376]),
            ("Tripura", "State", [23.9408, 91.9882]),
            ("Chandigarh", "Union Territory", [30.7333, 76.7794]),
            ("Puducherry", "Union Territory", [11.9416, 79.8083]),
            ("Dadra and Nagar Haveli and Daman and Diu", "Union Territory", [20.4283, 72.8397]),
            ("Andaman and Nicobar Islands", "Union Territory", [11.7401, 92.6586]),
            ("Lakshadweep", "Union Territory", [10.5667, 72.6417])
        ]

        for sname, stype, scenter in all_states:
            if q in sname.lower():
                sdata = india["states_with_data"].get(sname)
                results.append({
                    "title": sname,
                    "type": stype,
                    "level": "state",
                    "country": "India",
                    "state": sname,
                    "has_data": bool(sdata),
                    "center": scenter,
                    "zoom": 7 if stype == "State" else 9,
                    "badge": f"{sdata['trainees_tracked']} Trainees" if sdata else "No outcome data"
                })

        # 3. Districts in Maharashtra and destinations
        mh_data = cls.get_state_districts("Maharashtra")
        for d in mh_data["districts"]:
            if q in d["name"].lower():
                results.append({
                    "title": f"{d['name']}, Maharashtra",
                    "type": "District",
                    "level": "district",
                    "country": "India",
                    "state": "Maharashtra",
                    "district": d["name"],
                    "has_data": True,
                    "center": [d["lat"], d["lng"]],
                    "zoom": 10,
                    "badge": f"{d['total_trained']} Trained &bull; {d['employment_rate']}% Emp"
                })

        for other_state in ["Karnataka", "Gujarat", "Telangana", "Delhi", "Tamil Nadu"]:
            ost_data = cls.get_state_districts(other_state)
            for d in ost_data.get("districts", []):
                if q in d["name"].lower():
                    results.append({
                        "title": f"{d['name']}, {other_state}",
                        "type": "District",
                        "level": "district",
                        "country": "India",
                        "state": other_state,
                        "district": d["name"],
                        "has_data": True,
                        "center": [d["lat"], d["lng"]],
                        "zoom": 10,
                        "badge": f"{d['total_trained']} Trained &bull; {d['employment_rate']}% Emp"
                    })

        return results[:10]
