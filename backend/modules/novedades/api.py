from flask import Blueprint
from .controller import NovedadesController

controller = NovedadesController()
novedades_bp = Blueprint('api_novedades', __name__)

# Webhook WhatsApp
novedades_bp.add_url_rule('/webhook/whatsapp', view_func=controller.verificar_webhook, methods=['GET'])
novedades_bp.add_url_rule('/webhook/whatsapp', view_func=controller.recibir_mensaje, methods=['POST'])

# CRUD Novedades
novedades_bp.add_url_rule('/novedades', view_func=controller.listar_novedades, methods=['GET'])
novedades_bp.add_url_rule('/novedades', view_func=controller.crear_novedad, methods=['POST'])
novedades_bp.add_url_rule('/novedades/<int:id>', view_func=controller.obtener_novedad, methods=['GET'])

# Dashboard y Bot
novedades_bp.add_url_rule('/dashboard/metrics', view_func=controller.dashboard_metrics, methods=['GET'])
novedades_bp.add_url_rule('/bot/metrics', view_func=controller.bot_metrics, methods=['GET'])
novedades_bp.add_url_rule('/bot/conversations', view_func=controller.get_conversations, methods=['GET'])
novedades_bp.add_url_rule('/bot/toggle', view_func=controller.toggle_bot, methods=['POST'])
novedades_bp.add_url_rule('/bot/send', view_func=controller.send_manual, methods=['POST'])
