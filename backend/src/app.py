from flask import Flask
from flask_cors import CORS
from src.extensions import db, login_manager, cors, migrate
from src.config import DevelopmentConfig, ProductionConfig, TestingConfig
import os

login_manager.login_view = 'api_v1.auth.serve_login'

def create_app(config_override=None):
    # Initialize Flask app
    app = Flask(__name__)

    if config_override is not None:
        app.config.from_object(config_override)
    else:
        env = os.getenv('FLASK_MODE', 'development')
        if env == 'production':
            app.config.from_object(ProductionConfig)
        elif env == 'testing':
            app.config.from_object(TestingConfig)
        else:
            app.config.from_object(DevelopmentConfig)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    cors.init_app(app, resources={r"/api/v1/*": {"origins": "*"}})
    migrate.init_app(app, db, directory="src/db/migrations")

    # Register blueprints
    from src.modules import api_v1
    app.register_blueprint(api_v1)

    # Create all database tables
    with app.app_context():
        import src.db.models  # ensure all models are registered
        with db.engine.connect() as conn:
            conn.execute(db.text('CREATE EXTENSION IF NOT EXISTS vector'))
            conn.commit()
        db.create_all()
        if not app.config.get('TESTING'):
            # Seed default system configurations (idempotent — skips existing keys)
            from src.modules.configuracion.service import ConfiguracionService
            ConfiguracionService.seed_defaults()
        db.engine.dispose()  # close connections so forked workers get fresh ones

    # Health check endpoint
    @app.route("/health")
    def health():
        return {"status": "ok", "service": "openw-backend"}, 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=2222)
