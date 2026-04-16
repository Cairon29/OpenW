import os
import hmac
import hashlib
import json
import traceback
from flask import request, jsonify, Response, stream_with_context
from gevent.queue import Empty
from .service import ChatService
from .events import subscribe, unsubscribe, get_current_seq
from src.config import config

WHATSAPP_VERIFY_TOKEN = config.WHATSAPP_VERIFY_TOKEN or "openw_webhook_secret_2024"
WHATSAPP_APP_SECRET = config.WHATSAPP_APP_SECRET


class ChatController:
    # -- Webhook endpoints --

    @staticmethod
    def verificar_webhook():
        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'openw_webhook_secret_2024')
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == verify_token:
            print("[Webhook] Verificacion exitosa")
            return challenge, 200

        print(f"[Webhook] Verificacion fallida. Token recibido: {token}")
        return jsonify({"error": "Token de verificacion invalido"}), 403

    @staticmethod
    def recibir_mensaje():
        # Signature verification (skip if APP_SECRET not configured)
        app_secret = os.getenv('WHATSAPP_APP_SECRET')
        if app_secret:
            signature = request.headers.get("X-Hub-Signature-256", "")
            if not signature:
                return jsonify({"error": "Missing signature"}), 401
            expected = "sha256=" + hmac.HMAC(
                app_secret.encode(),
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

                    # Extract profile name from contacts array (sent by Meta on every message)
                    contacts = value.get("contacts", [])
                    profile_name = None
                    if contacts:
                        profile_name = contacts[0].get("profile", {}).get("name")

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
                                ChatService.procesar_mensaje_whatsapp(
                                    phone, texto,
                                    wa_message_id=wa_message_id,
                                    profile_name=profile_name,
                                )

                    # Handle message status updates (sent/delivered/read)
                    for status_update in value.get("statuses", []):
                        wamid = status_update.get("id")
                        status = status_update.get("status")
                        if wamid and status:
                            ChatService.update_message_status(wamid, status)

        except Exception as e:
            print(f"[Webhook] Error procesando mensaje:\n{traceback.format_exc()}")

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
    def stream_conversations():
        def generate():
            q = subscribe()
            try:
                # Read seq BEFORE the DB query to close the race window:
                # any message committed during the snapshot query will have
                # seq > snapshot_seq, making it detectable as a duplicate on
                # the client side.
                snapshot_seq = get_current_seq()
                convs = ChatService.get_conversations()
                snapshot = {
                    "seq": snapshot_seq,
                    "type": "snapshot",
                    "conversations": convs,
                }
                yield f"retry: 5000\nevent: snapshot\ndata: {json.dumps(snapshot)}\n\n"

                while True:
                    try:
                        event = q.get(timeout=15)
                        yield f"event: {event['type']}\ndata: {json.dumps(event)}\n\n"
                    except Empty:
                        yield ": ping\n\n"
            except GeneratorExit:
                pass
            finally:
                unsubscribe(q)

        response = Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
        )
        response.headers["Cache-Control"] = "no-cache"
        response.headers["X-Accel-Buffering"] = "no"
        response.headers["Connection"] = "keep-alive"
        return response

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

