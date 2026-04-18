from flask import Blueprint

from .usuarios.api import usuarios_bp
from .categorias.api import categorias_bp
from .novedades.api import novedades_bp
from .viceprecidencia.api import viceprecidencia_bp
from .chat.api import chat_bp
from .auth.api import auth_bp
from .configuracion.api import configuracion_bp

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

api_v1.register_blueprint(usuarios_bp, url_prefix='/usuarios')
api_v1.register_blueprint(categorias_bp, url_prefix='/categorias')
api_v1.register_blueprint(novedades_bp, url_prefix='/novedades')
api_v1.register_blueprint(viceprecidencia_bp, url_prefix='/vicepresidencias')
api_v1.register_blueprint(chat_bp, url_prefix='/chat')
api_v1.register_blueprint(auth_bp, url_prefix='/auth')
api_v1.register_blueprint(configuracion_bp, url_prefix='/configuracion')
