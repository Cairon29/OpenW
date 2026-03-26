import os
from flask import request, jsonify
from .service import NovedadService
from backend.schemas.novedad_dto import novedad_schema, novedades_schema

VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "openw_webhook_secret_2024")


class NovedadesController:

    # ── Webhook de WhatsApp ──────────────────────────────────────────────────

    @staticmethod
    def verificar_webhook():
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("[Webhook] Verificación exitosa")
            return challenge, 200

        print(f"[Webhook] Verificación fallida. Token recibido: {token}")
        return jsonify({"error": "Token de verificación inválido"}), 403

    @staticmethod
    def recibir_mensaje():
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
        except Exception as e:
            print(f"[Webhook] Error procesando mensaje: {e}")

        return jsonify({"status": "ok"}), 200

    # ── Novedades (casos) ────────────────────────────────────────────────────

    @staticmethod
    def listar_novedades():
        try:
            novedades = NovedadService.get_all_novedades()
            return jsonify(novedades_schema.dump(novedades)), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def crear_novedad():
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Body requerido"}), 400

        titulo = (data.get("titulo") or "").strip()
        descripcion = (data.get("descripcion") or "").strip()
        if not titulo or not descripcion:
            return jsonify({"error": "titulo y descripcion son requeridos"}), 400

        try:
            novedad = NovedadService.create_novedad(
                titulo=titulo,
                descripcion=descripcion,
                severidad=data.get("severidad"),
                estado=data.get("estado"),
                categoria_id=data.get("categoria_id"),
                user_id=data.get("user_id"),
            )
            return jsonify(novedad_schema.dump(novedad)), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def obtener_novedad(id):
        from backend.schemas import Novedad
        novedad = Novedad.query.get_or_404(id)
        return jsonify(novedad_schema.dump(novedad)), 200

    # ── Dashboard y Bot ──────────────────────────────────────────────────────

    @staticmethod
    def dashboard_metrics():
        try:
            return jsonify(NovedadService.get_dashboard_metrics()), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def bot_metrics():
        try:
            return jsonify(NovedadService.get_bot_metrics()), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def get_conversations():
        return jsonify(NovedadService.get_conversations()), 200

    @staticmethod
    def toggle_bot():
        data = request.get_json(silent=True)
        if not data or not data.get("phone"):
            return jsonify({"error": "phone requerido"}), 400

        phone = str(data["phone"])
        bot_active = NovedadService.toggle_bot(phone)
        return jsonify({"phone": phone, "bot_active": bot_active}), 200

    @staticmethod
    def send_manual():
        data = request.get_json(silent=True)
        if not data or not data.get("phone") or not data.get("message"):
            return jsonify({"error": "phone y message requeridos"}), 400

        phone = str(data["phone"])
        mensaje = data["message"].strip()

        if not mensaje:
            return jsonify({"error": "El mensaje no puede estar vacío"}), 400

        NovedadService.enviar_mensaje_manual(phone, mensaje)
        return jsonify({"status": "sent", "phone": phone}), 200
