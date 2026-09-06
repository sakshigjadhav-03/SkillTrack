import sys
import os
import subprocess
from pathlib import Path

# Base directory
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

# Import project dependencies
from backend.config import Config
from backend.app import create_app
from database.init_db import init_database, run_schema_migrations

def ensure_database():
    """Ensures database is initialized with tables and synthetic demo data on container start."""
    try:
        db_file = Path(Config.SQLITE_DB_PATH)
        if Config.USE_SQLITE and (not db_file.exists() or db_file.stat().st_size == 0):
            print("[SkillTrack] SQLite database not found or empty. Auto-initializing with synthetic demo data...")
            init_database()
        else:
            run_schema_migrations()
    except Exception as e:
        print(f"[SkillTrack DB Startup Warning] {e}")

# Initialize DB if necessary and create WSGI application instance
ensure_database()
app = create_app()

if __name__ == '__main__':
    # Auto-detect and switch to .venv only for direct local Windows python execution
    if os.name == 'nt':
        venv_python = ROOT_DIR / '.venv' / 'Scripts' / 'python.exe'
        if venv_python.exists() and Path(sys.executable).resolve() != venv_python.resolve():
            print(f"[SkillTrack] Activating local virtual environment: {venv_python}")
            sys.exit(subprocess.call([str(venv_python)] + sys.argv))

    port = int(os.environ.get('PORT', Config.PORT))
    host = os.environ.get('HOST', '0.0.0.0')
    print("=" * 65)
    print("  SkillTrack: From Training to Sustainable Employment (SIH26135)")
    print(f"  Starting web server at http://{host}:{port}")
    print("  Synthetic Prototype Data -- Not Government Data")
    print("=" * 65)
    app.run(host=host, port=port, debug=Config.DEBUG)
