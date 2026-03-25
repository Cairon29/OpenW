from flask import Flask
from extensions import db, cors
from flask import Flask, request, jsonify, make_response
from sqlalchemy import create_engine


db = SQLAlchemy(app)
def create_app():
    app = Flask(__name__)
    engine = create_engine('sqlite:///example.db')
    Base = declarative_base()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    import os
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")

    # Inicializar extensiones
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # --- REGISTRO DE BLUEPRINTS ---
    from controllers.user_controller import user_bp
    from controllers.novedades_controller import novedades_bp
    from controllers.categoria_cotroller import categorias_bp
    from controllers.vicepresidencia_controller import vp_bp

    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(novedades_bp, url_prefix="/api/novedades")
    app.register_blueprint(categorias_bp, url_prefix="/api/categorias")
    app.register_blueprint(vp_bp, url_prefix="/api/vicepresidencias")

    # Crear tablas
    with app.app_context():
        import models  # Importante para que SQLAlchemy detecte las tablas
        db.create_all()

    @app.route("/health")
    def health():
        return {"status": "ok", "service": "openw-backend"}, 200

    return app