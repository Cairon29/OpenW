from flask import Blueprint
from .controller import CategoriasController

controller = CategoriasController()
categorias_bp = Blueprint('api_categorias', __name__)

categorias_bp.add_url_rule('/categorias', view_func=controller.crear, methods=['POST'])
categorias_bp.add_url_rule('/categorias', view_func=controller.listar, methods=['GET'])
