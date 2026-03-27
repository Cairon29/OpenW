from flask import Blueprint
from .controller import VicepresidenciaController

controller = VicepresidenciaController()
viceprecidencia_bp = Blueprint('api_viceprecidencia', __name__)

viceprecidencia_bp.add_url_rule('/', view_func=controller.crear_vp, methods=['POST'])
viceprecidencia_bp.add_url_rule('/', view_func=controller.listar_vps, methods=['GET'])
