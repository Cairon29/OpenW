from flask import Blueprint
from .controller import AuthController

controller = AuthController()
auth_bp = Blueprint('api_auth', __name__)

auth_bp.add_url_rule('/verify-email', view_func=controller.verify_email, methods=['GET', 'POST'])
