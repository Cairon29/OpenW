from flask import Blueprint
from .controller import ChatController

controller = ChatController()
chat_bp = Blueprint('api_chat', __name__)

# Webhook WhatsApp
chat_bp.add_url_rule('/webhook/whatsapp', view_func=controller.verificar_webhook, methods=['GET'])
chat_bp.add_url_rule('/webhook/whatsapp', view_func=controller.recibir_mensaje, methods=['POST'])

# Bot management
chat_bp.add_url_rule('/bot/metrics', view_func=controller.bot_metrics, methods=['GET'])
chat_bp.add_url_rule('/bot/conversations', view_func=controller.get_conversations, methods=['GET'])
chat_bp.add_url_rule('/bot/stream', view_func=controller.stream_conversations, methods=['GET'])
chat_bp.add_url_rule('/bot/toggle', view_func=controller.toggle_bot, methods=['POST'])
chat_bp.add_url_rule('/bot/send', view_func=controller.send_manual, methods=['POST'])
