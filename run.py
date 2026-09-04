import sys
from pathlib import Path

# Add project root directory to Python path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from backend.config import Config
from backend.app import create_app
from database.init_db import init_database

def main():
    """Main launcher script for SkillTrack."""
    # Ensure database is initialized
    db_file = Path(Config.SQLITE_DB_PATH)
    if Config.USE_SQLITE and (not db_file.exists() or db_file.stat().st_size == 0):
        print("[SkillTrack Launcher] Database file not found. Auto-initializing with synthetic demo data...")
        init_database()

    app = create_app()
    print("=" * 65)
    print("  SkillTrack: From Training to Sustainable Employment (SIH26135)")
    print(f"  Starting local server at http://127.0.0.1:{Config.PORT}")
    print("  Synthetic Prototype Data -- Not Government Data")
    print("=" * 65)
    app.run(host='127.0.0.1', port=Config.PORT, debug=Config.DEBUG)

if __name__ == '__main__':
    main()
