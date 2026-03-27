from flask import Blueprint
from .controller import NovedadesController

controller = NovedadesController()
novedades_bp = Blueprint('api_novedades', __name__)

# CRUD Novedades
novedades_bp.add_url_rule('/novedades', view_func=controller.listar_novedades, methods=['GET'])
novedades_bp.add_url_rule('/novedades', view_func=controller.crear_novedad, methods=['POST'])
novedades_bp.add_url_rule('/novedades/<int:id>', view_func=controller.obtener_novedad, methods=['GET'])

# Dashboard
novedades_bp.add_url_rule('/dashboard/metrics', view_func=controller.dashboard_metrics, methods=['GET'])
