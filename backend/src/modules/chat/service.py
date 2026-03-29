import json
import requests
from groq import Groq
from sqlalchemy.exc import IntegrityError
from src.extensions import db
from src.db.models import Novedad, CategoriaNovedad, SeveridadEnum, EstadoEnum
from src.db.models.chat_message import ChatMessage
from src.db.models.conversation_state import ConversationState
from datetime import datetime, timezone
from collections import defaultdict
from src.config import config


_groq_client = None

HISTORY_WINDOW = 10   # mensajes anteriores que se pasan a Groq como contexto
SIMILAR_WINDOW = 3    # mensajes similares recuperados via pgVector


def _get_groq_client():
    global _groq_client
    if _groq_client is None:
        api_key = config.GROQ_API_KEY
        if not api_key:
            print("[WARNING] GROQ_API_KEY not set. AI features will be disabled.")
            return None
        _groq_client = Groq(api_key=api_key)
    return _groq_client


# WhatsApp credentials from config
WHATSAPP_ACCESS_TOKEN = config.WHATSAPP_ACCESS_TOKEN
WHATSAPP_PHONE_NUMBER_ID = config.WHATSAPP_PHONE_NUMBER_ID


class ChatService:

    @staticmethod
    def procesar_mensaje_whatsapp(phone, texto, wa_message_id=None):
        """Procesa un mensaje entrante de WhatsApp y responde si el bot esta activo."""
        phone = str(phone)
        ChatService._store_message(phone, "user", texto, wa_message_id=wa_message_id)

        # Lee estado del bot desde DB (no memoria volatil)
        if not ChatService._get_bot_state(phone):
            return None

        categoria_detectada = ChatService._match_categoria_por_palabras_clave(texto)
        analisis = ChatService._analizar_con_ia(phone, texto, categoria_detectada)

        categoria = categoria_detectada
        if not categoria:
            nombre_ia = analisis.get("categoria")
            if nombre_ia:
                categoria = CategoriaNovedad.query.filter_by(categoria=nombre_ia).first()

        categoria_id = categoria.id if categoria else None

        nueva_novedad = Novedad(
            titulo=analisis.get("titulo", texto[:50]),
            descripcion=texto,
            fk_id_usuario=None,
            fk_id_categoria=categoria_id,
            severidad=analisis.get("severidad", SeveridadEnum.MEDIA),
            estado=EstadoEnum.ABIERTA,
            fecha_registro=datetime.now(timezone.utc),
        )

        try:
            db.session.add(nueva_novedad)
            db.session.commit()

            respuesta = analisis.get("respuesta_usuario", "Recibimos tu mensaje. En breve te responderemos.")
            wamid = ChatService._enviar_whatsapp(phone, respuesta)
            ChatService._store_message(phone, "bot", respuesta, wa_message_id=wamid)

            return nueva_novedad
        except Exception as e:
            db.session.rollback()
            print(f"Error guardando novedad: {e}")
            return None

    @staticmethod
    def _match_categoria_por_palabras_clave(texto):
        """Busca si el texto contiene la palabra clave de alguna categoria."""
        texto_lower = texto.lower()
        try:
            categorias = CategoriaNovedad.query.all()
            for cat in categorias:
                if cat.palabra_clave and cat.palabra_clave.lower() in texto_lower:
                    return cat
        except Exception as e:
            print(f"Error buscando categorias: {e}")
        return None

    @staticmethod
    def _analizar_con_ia(phone, texto, categoria_detectada=None):
        """
        Llama a Groq para clasificar el mensaje y generar una respuesta.
        Incluye historial de conversacion y contexto semantico similar via pgVector.
        """
        try:
            groq_client = _get_groq_client()
            if groq_client is None:
                raise Exception("Groq client not available (GROQ_API_KEY not set)")

            categorias = CategoriaNovedad.query.all()
            nombres = [c.categoria for c in categorias] if categorias else ["General"]
            categorias_str = ", ".join(f"'{n}'" for n in nombres)

            # Contexto semantico: mensajes similares de otras conversaciones
            contexto_similar = ChatService._buscar_mensajes_similares(texto, phone)
            contexto_txt = ""
            if contexto_similar:
                ejemplos = "\n".join(f"- {m.text}" for m in contexto_similar)
                contexto_txt = f"\nMensajes similares previos de otros usuarios:\n{ejemplos}\n"

            system_prompt = (
                "Eres un asistente de atencion al cliente. Analiza el mensaje y responde SOLO en JSON valido.\n"
                "Campos requeridos:\n"
                "1. 'titulo': resumen del mensaje en maximo 8 palabras.\n"
                "2. 'severidad': nivel de urgencia: 'critica', 'alta', 'media' o 'baja'.\n"
                f"3. 'categoria': clasifica en una de estas categorias: {categorias_str}.\n"
                "4. 'respuesta_usuario': mensaje amigable y breve para enviarle al usuario por WhatsApp. "
                "Confirma que recibiste su mensaje y orientalo segun el tema."
                f"{contexto_txt}"
            )

            if categoria_detectada:
                system_prompt += f"\nNota: el mensaje fue clasificado automaticamente como '{categoria_detectada.categoria}' por palabra clave."

            # Historial de la conversacion actual (ultimos N mensajes)
            historial = ChatMessage.query.filter_by(phone=phone)\
                .order_by(ChatMessage.timestamp.desc())\
                .limit(HISTORY_WINDOW).all()
            historial = list(reversed(historial))

            messages = [{"role": "system", "content": system_prompt}]
            for msg in historial:
                role = "assistant" if msg.role == "bot" else "user"
                messages.append({"role": role, "content": msg.text})
            # El mensaje actual va al final
            messages.append({"role": "user", "content": texto})

            chat_completion = groq_client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"Error con Groq: {e}")
            return {
                "titulo": "Mensaje recibido",
                "severidad": "media",
                "categoria": None,
                "respuesta_usuario": "Recibimos tu mensaje. En breve te daremos mas informacion.",
            }

    @staticmethod
    def _buscar_mensajes_similares(texto, phone_excluir, limit=SIMILAR_WINDOW):
        """
        Busca mensajes semanticamente similares en otras conversaciones usando pgVector.
        Retorna una lista de ChatMessage o lista vacia si embeddings no estan disponibles.
        """
        try:
            from src.utils.embeddings import get_embedding
            embedding = get_embedding(texto)
            similares = ChatMessage.query\
                .filter(ChatMessage.phone != phone_excluir)\
                .filter(ChatMessage.embedding.isnot(None))\
                .filter(ChatMessage.role == "user")\
                .order_by(ChatMessage.embedding.cosine_distance(embedding))\
                .limit(limit)\
                .all()
            return similares
        except Exception as e:
            print(f"[Embeddings] Busqueda semantica no disponible: {e}")
            return []

    @staticmethod
    def _enviar_whatsapp(phone, mensaje):
        """Envia un mensaje de texto via Meta WhatsApp Cloud API. Returns wamid or None."""
        if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
            print(f"[WhatsApp] Credenciales no configuradas. Mensaje para {phone}: {mensaje}")
            return None

        url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": str(phone),
            "type": "text",
            "text": {"body": mensaje},
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            wamid = data.get("messages", [{}])[0].get("id")
            print(f"[WhatsApp] Mensaje enviado a {phone}: {wamid}")
            return wamid
        except Exception as e:
            print(f"[WhatsApp] Error enviando a {phone}: {e}")
            return None

    @staticmethod
    def _store_message(phone, role, text, wa_message_id=None):
        """Guarda un mensaje en la base de datos e intenta generar su embedding."""
        phone = str(phone)

        # Genera embedding de forma no bloqueante (falla silenciosamente)
        embedding = None
        try:
            from src.utils.embeddings import get_embedding
            embedding = get_embedding(text)
        except Exception as e:
            print(f"[Embeddings] No se pudo generar embedding: {e}")

        msg = ChatMessage(
            phone=phone,
            role=role,
            text=text,
            wa_message_id=wa_message_id,
            timestamp=datetime.now(timezone.utc),
            embedding=embedding,
        )
        try:
            db.session.add(msg)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print(f"[Chat] Duplicate message ignored: {wa_message_id}")

    # ── Bot state (persistido en DB) ─────────────────────────────────────────

    @staticmethod
    def _get_bot_state(phone: str) -> bool:
        """Lee el estado del bot para este telefono desde la DB. Default: True (activo)."""
        state = ConversationState.query.get(phone)
        return state.bot_active if state else True

    @staticmethod
    def toggle_bot(phone):
        """Activa o desactiva el bot para una conversacion. Retorna el nuevo estado."""
        phone = str(phone)
        state = ConversationState.query.get(phone)
        if state is None:
            state = ConversationState(phone=phone, bot_active=False)
            db.session.add(state)
        else:
            state.bot_active = not state.bot_active
            state.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return state.bot_active

    @staticmethod
    def set_bot_state(phone, active):
        """Establece el estado del bot para una conversacion."""
        phone = str(phone)
        state = ConversationState.query.get(phone)
        if state is None:
            state = ConversationState(phone=phone, bot_active=bool(active))
            db.session.add(state)
        else:
            state.bot_active = bool(active)
            state.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return state.bot_active

    @staticmethod
    def enviar_mensaje_manual(phone, mensaje):
        """Envia un mensaje manual desde el dashboard (ignora estado del bot)."""
        phone = str(phone)
        wamid = ChatService._enviar_whatsapp(phone, mensaje)
        ChatService._store_message(phone, "bot", mensaje, wa_message_id=wamid)

    @staticmethod
    def get_conversations():
        """Retorna todas las conversaciones activas con sus mensajes desde la DB."""
        from sqlalchemy import func

        subq = db.session.query(
            ChatMessage.phone,
            func.max(ChatMessage.timestamp).label('last_time')
        ).group_by(ChatMessage.phone).subquery()

        phones = db.session.query(subq.c.phone, subq.c.last_time).order_by(
            subq.c.last_time.desc()
        ).all()

        result = []
        for phone, _ in phones:
            msgs = ChatMessage.query.filter_by(phone=phone).order_by(ChatMessage.timestamp).all()
            messages = [{"role": m.role, "text": m.text, "time": m.timestamp.isoformat()} for m in msgs]
            last = messages[-1] if messages else {}
            result.append({
                "phone": phone,
                "bot_active": ChatService._get_bot_state(phone),
                "last_message": last.get("text", ""),
                "last_time": last.get("time", ""),
                "messages": messages,
            })
        return result

    @staticmethod
    def update_message_status(wa_message_id, status):
        """Actualiza el estado de entrega de un mensaje (sent/delivered/read)."""
        msg = ChatMessage.query.filter_by(wa_message_id=wa_message_id).first()
        if msg:
            msg.status = status
            db.session.commit()

    @staticmethod
    def get_bot_metrics():
        """Calcula metricas reales del bot desde la DB."""
        from sqlalchemy import func
        from datetime import date, timedelta

        total_conversations = db.session.query(
            func.count(func.distinct(ChatMessage.phone))
        ).scalar() or 0

        bot_messages = ChatMessage.query.filter_by(role="bot").count()

        responded = db.session.query(
            func.count(func.distinct(ChatMessage.phone))
        ).filter(ChatMessage.role == "bot").scalar() or 0

        response_rate = round((responded / total_conversations * 100) if total_conversations else 0)

        today = date.today()
        usage_over_time = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            count = ChatMessage.query.filter(
                func.date(ChatMessage.timestamp) == day
            ).count()
            usage_over_time.append({"date": str(day), "count": count})

        con_categoria = Novedad.query.filter(Novedad.fk_id_categoria.isnot(None)).count()
        sin_categoria = Novedad.query.filter(Novedad.fk_id_categoria.is_(None)).count()

        return {
            "totalConversations": total_conversations,
            "botMessages": bot_messages,
            "responseRate": response_rate,
            "usageOverTime": usage_over_time,
            "effectiveness": {
                "conContexto": con_categoria,
                "sinContexto": sin_categoria,
            },
        }
