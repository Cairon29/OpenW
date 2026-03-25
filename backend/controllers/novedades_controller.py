import os
from flask import Blueprint, request, jsonify
from services.novedad_service import NovedadService
from schemas.novedad_dto import NovedadSchema

novedades_bp = Blueprint('novedades', __name__)
novedad_schema = NovedadSchema()
novedades_schema = NovedadSchema(many=True)

VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "openw_webhook_secret_2024")


# ── Webhook de WhatsApp (Meta Cloud API) ──────────────────────────────────────

@novedades_bp.route('/webhook/whatsapp', methods=['GET'])
def verificar_webhook():
    """
    Meta verifica el webhook enviando un GET con estos parámetros.
    Debemos responder con hub.challenge si el token es correcto.
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print(f"[Webhook] Verificación exitosa")
        return challenge, 200

    print(f"[Webhook] Verificación fallida. Token recibido: {token}")
    return jsonify({"error": "Token de verificación inválido"}), 403


@novedades_bp.route('/webhook/whatsapp', methods=['POST'])
def recibir_mensaje():
    """
    Recibe mensajes entrantes de WhatsApp desde Meta Cloud API.
    Meta envía un JSON con la estructura: entry > changes > value > messages
    """
    data = request.get_json(silent=True)

    if not data or data.get("object") != "whatsapp_business_account":
        return jsonify({"status": "ignored"}), 200

    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])

                for message in messages:
                    msg_type = message.get("type")
                    phone = message.get("from")

                    if not phone:
                        continue

                    if msg_type == "text":
                        texto = message.get("text", {}).get("body", "").strip()
                        if texto:
                            print(f"[Webhook] Mensaje de {phone}: {texto}")
                            NovedadService.procesar_mensaje_whatsapp(phone, texto)

                    # Ignorar otros tipos (imagen, audio, etc.) por ahora
    except Exception as e:
        print(f"[Webhook] Error procesando mensaje: {e}")

    # Meta requiere siempre un 200 para confirmar recepción
    return jsonify({"status": "ok"}), 200


# ── Novedades (casos) ─────────────────────────────────────────────────────────

@novedades_bp.route('/novedades', methods=['GET'])
def listar_novedades():
    """Retorna el historial de novedades registradas."""
    try:
        novedades = NovedadService.get_all_novedades()
        return jsonify(novedades_schema.dump(novedades)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@novedades_bp.route('/novedades/<int:id>', methods=['GET'])
def obtener_novedad(id):
    """Detalle de una novedad por ID."""
    from models.Novedad import Novedad
    novedad = Novedad.query.get_or_404(id)
    return jsonify(novedad_schema.dump(novedad)), 200


# ── Bot: conversaciones y control ─────────────────────────────────────────────

@novedades_bp.route('/bot/conversations', methods=['GET'])
def get_conversations():
    """
    Retorna todas las conversaciones activas con sus mensajes.
    Usado por el dashboard para mostrar la vista del bot.
    """
    return jsonify(NovedadService.get_conversations()), 200


@novedades_bp.route('/bot/toggle', methods=['POST'])
def toggle_bot():
    """
    Activa o desactiva el bot para una conversación específica.
    Body: {"phone": "573001234567"}
    """
    data = request.get_json(silent=True)
    if not data or not data.get("phone"):
        return jsonify({"error": "phone requerido"}), 400

    phone = str(data["phone"])
    bot_active = NovedadService.toggle_bot(phone)
    return jsonify({"phone": phone, "bot_active": bot_active}), 200


@novedades_bp.route('/bot/send', methods=['POST'])
def send_manual():
    """
    Envía un mensaje manual desde el dashboard (sin pasar por la IA).
    Body: {"phone": "573001234567", "message": "Hola, te ayudamos en breve"}
    """
    data = request.get_json(silent=True)
    if not data or not data.get("phone") or not data.get("message"):
        return jsonify({"error": "phone y message requeridos"}), 400

    phone = str(data["phone"])
    mensaje = data["message"].strip()

    if not mensaje:
        return jsonify({"error": "El mensaje no puede estar vacío"}), 400

    NovedadService.enviar_mensaje_manual(phone, mensaje)
    return jsonify({"status": "sent", "phone": phone}), 200
