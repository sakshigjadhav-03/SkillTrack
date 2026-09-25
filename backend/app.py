from pathlib import Path
from flask import Flask, render_template, session
from backend.config import Config
from backend.utils.decorators import get_current_user

# Define path to frontend
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / 'frontend'

def create_app(config_class=Config):
    """Application factory for SkillTrack."""
    app = Flask(
        __name__,
        template_folder=str(FRONTEND_DIR / 'templates'),
        static_folder=str(FRONTEND_DIR / 'static'),
        static_url_path='/static'
    )
    app.config.from_object(config_class)

    # Register Blueprints
    from backend.routes.auth_routes import auth_bp
    from backend.routes.trainee_routes import trainee_bp
    from backend.routes.employer_routes import employer_bp
    from backend.routes.provider_routes import provider_bp
    from backend.routes.government_routes import gov_bp
    from backend.routes.api_routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(trainee_bp)
    app.register_blueprint(employer_bp)
    app.register_blueprint(provider_bp)
    app.register_blueprint(gov_bp)
    app.register_blueprint(api_bp)

    # Global Context Processor
    @app.context_processor
    def inject_globals():
        return {
            'DATA_DISCLAIMER': Config.DATA_DISCLAIMER,
            'current_user': get_current_user(),
            'system_tagline': "From Training to Sustainable Employment",
            'sih_problem_code': "SIH26135"
        }

    # Public Landing Page
    @app.route('/')
    def index():
        return render_template('index.html')

    # Health Check Endpoint for Cloud Monitoring
    @app.route('/health')
    def health_check():
        return {
            "status": "ok",
            "app": "SkillTrack",
            "service": "Longitudinal Skilling Outcomes Engine",
            "sih_code": "SIH26135"
        }, 200

    # Cloud Self-Diagnosis & Repair Endpoint
    @app.route('/api/diagnostic')
    def cloud_diagnostic():
        import sqlite3
        diag = {
            "status": "ok",
            "db_type": "sqlite" if Config.USE_SQLITE else "mysql",
            "tables": [],
            "users_count": 0,
            "trainees_count": 0,
            "columns": {},
            "errors": []
        }
        try:
            from backend.database import query_db, get_db_connection
            conn, db_type = get_db_connection()
            if db_type == 'sqlite':
                tables = query_db("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                diag["tables"] = [t['name'] for t in tables] if tables else []
                # Check trainee columns
                if 'trainees' in diag["tables"]:
                    cols = query_db("PRAGMA table_info(trainees)")
                    diag["columns"]["trainees"] = [c['name'] for c in cols] if cols else []
            else:
                tables = query_db("SHOW TABLES")
                diag["tables"] = [list(t.values())[0] for t in tables] if tables else []
            
            u = query_db("SELECT COUNT(*) AS c FROM users", one=True)
            diag["users_count"] = u['c'] if u else 0
            t = query_db("SELECT COUNT(*) AS c FROM trainees", one=True)
            diag["trainees_count"] = t['c'] if t else 0
        except Exception as e:
            diag["errors"].append(str(e))
            diag["status"] = "error"
        return diag, 200

    # Friendly Error Handlers with Server Logs
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        import traceback
        tb = traceback.format_exc()
        app.logger.error(f"500 Internal Server Error: {e}\n{tb}")
        return render_template('errors/500.html', error_details=str(e), traceback_str=tb), 500

    return app
