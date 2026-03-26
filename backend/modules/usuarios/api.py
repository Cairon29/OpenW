from flask import Blueprint
from .controller import UsuariosController

controller = UsuariosController()
usuarios_bp = Blueprint('api_usuarios', __name__)

usuarios_bp.add_url_rule('/', view_func=controller.register_user, methods=['POST'])
usuarios_bp.add_url_rule('/', view_func=controller.get_users, methods=['GET'])
usuarios_bp.add_url_rule('/login', view_func=controller.login, methods=['POST'])
