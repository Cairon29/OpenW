import hmac
import hashlib
from flask import request, jsonify
from .service import ChatService
from src.config import config

WHATSAPP_VERIFY_TOKEN = config.WHATSAPP_VERIFY_TOKEN or "openw_webhook_secret_2024"
WHATSAPP_APP_SECRET = config.WHATSAPP_APP_SECRET


class ChatController:
    # -- Webhook endpoints --

    @staticmethod
    def verificar_webhook():
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == WHATSAPP_VERIFY_TOKEN:
            print("[Webhook] Verificacion exitosa")
            return challenge, 200

        print(f"[Webhook] Verificacion fallida. Token recibido: {token}")
        return jsonify({"error": "Token de verificacion invalido"}), 403

    @staticmethod
    def recibir_mensaje():
        # Signature verification (skip if APP_SECRET not configured)
        if WHATSAPP_APP_SECRET:
            signature = request.headers.get("X-Hub-Signature-256", "")
            if not signature:
                return jsonify({"error": "Missing signature"}), 401
            expected = "sha256=" + hmac.new(
                WHATSAPP_APP_SECRET.encode(),
                request.get_data(),
                hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(signature, expected):
                print("[Webhook] Signature verification failed")
                return jsonify({"error": "Invalid signature"}), 401

        data = request.get_json(silent=True)

        if not data or data.get("object") != "whatsapp_business_account":
            return jsonify({"status": "ignored"}), 200

        try:
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})

                    # Handle incoming messages
                    for message in value.get("messages", []):
                        msg_type = message.get("type")
                        phone = message.get("from")

                        if not phone:
                            continue

                        if msg_type == "text":
                            texto = message.get("text", {}).get("body", "").strip()
                            if texto:
                                wa_message_id = message.get("id")
                                print(f"[Webhook] Mensaje de {phone}: {texto}")
                                ChatService.procesar_mensaje_whatsapp(phone, texto, wa_message_id=wa_message_id)

                    # Handle message status updates (sent/delivered/read)
                    for status_update in value.get("statuses", []):
                        wamid = status_update.get("id")
                        status = status_update.get("status")
                        if wamid and status:
                            ChatService.update_message_status(wamid, status)

        except Exception as e:
            print(f"[Webhook] Error procesando mensaje: {e}")

        return jsonify({"status": "ok"}), 200

    # -- Bot management endpoints --

    @staticmethod
    def bot_metrics():
        try:
            return jsonify(ChatService.get_bot_metrics()), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def get_conversations():
        return jsonify(ChatService.get_conversations()), 200

    @staticmethod
    def toggle_bot():
        data = request.get_json(silent=True)
        if not data or not data.get("phone"):
            return jsonify({"error": "phone requerido"}), 400

        phone = str(data["phone"])
        bot_active = ChatService.toggle_bot(phone)
        return jsonify({"phone": phone, "bot_active": bot_active}), 200

    @staticmethod
    def send_manual():
        data = request.get_json(silent=True)
        if not data or not data.get("phone") or not data.get("message"):
            return jsonify({"error": "phone y message requeridos"}), 400

        phone = str(data["phone"])
        mensaje = data["message"].strip()

        if not mensaje:
            return jsonify({"error": "El mensaje no puede estar vacio"}), 400

        ChatService.enviar_mensaje_manual(phone, mensaje)
        return jsonify({"status": "sent", "phone": phone}), 200
