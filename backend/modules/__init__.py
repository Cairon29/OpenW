from flask import Blueprint

from .usuarios.api import usuarios_bp
from .categorias.api import categorias_bp
from .novedades.api import novedades_bp
from .viceprecidencia.api import viceprecidencia_bp

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

api_v1.register_blueprint(usuarios_bp, url_prefix='/usuarios')
api_v1.register_blueprint(categorias_bp, url_prefix='/categorias')
api_v1.register_blueprint(novedades_bp, url_prefix='/novedades')
api_v1.register_blueprint(viceprecidencia_bp, url_prefix='/vicepresidencias')
