from flask import Blueprint
from .controller import ConfiguracionController

configuracion_bp = Blueprint('api_configuracion', __name__)

configuracion_bp.add_url_rule('',                          view_func=ConfiguracionController.listar,          methods=['GET'], strict_slashes=False)
configuracion_bp.add_url_rule('/<string:key>',             view_func=ConfiguracionController.obtener,         methods=['GET'], strict_slashes=False)
configuracion_bp.add_url_rule('/<string:key>',             view_func=ConfiguracionController.actualizar,      methods=['PUT'], strict_slashes=False)
configuracion_bp.add_url_rule('/bulk',                     view_func=ConfiguracionController.bulk_actualizar, methods=['POST'], strict_slashes=False)
configuracion_bp.add_url_rule('/test/<string:service>',    view_func=ConfiguracionController.test_conexion,   methods=['POST'], strict_slashes=False)
