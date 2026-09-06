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

    # Friendly Error Handlers (No raw tracebacks to judges)
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app
