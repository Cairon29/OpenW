import os
import json
import requests
from groq import Groq
from models.Novedad import Novedad, SeveridadEnum, EstadoEnum
from models.Categoria import Categoria
from extensions import db
from datetime import datetime, timezone

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")

# In-memory stores (se resetean al reiniciar el servidor)
_conversations = {}  # {phone: [{"role": "user"|"bot", "text": str, "time": str}]}
_bot_states = {}     # {phone: bool} True = bot activo (default: True)


class NovedadService:

    @staticmethod
    def procesar_mensaje_whatsapp(phone, texto):
        """Procesa un mensaje entrante de WhatsApp y responde si el bot está activo."""
        phone = str(phone)
        NovedadService._store_message(phone, "user", texto)

        # Si el bot está apagado para esta conversación, no responder
        if not _bot_states.get(phone, True):
            return None

        # 1. Buscar categoría por palabras clave
        categoria_detectada = NovedadService._match_categoria_por_palabras_clave(texto)

        # 2. Análisis con IA (pasa la categoría detectada como contexto)
        analisis = NovedadService._analizar_con_ia(texto, categoria_detectada)

        # 3. Determinar categoría final
        categoria = categoria_detectada
        if not categoria:
            nombre_ia = analisis.get("categoria")
            if nombre_ia:
                categoria = Categoria.query.filter_by(nombre=nombre_ia).first()

        categoria_id = categoria.id if categoria else None

        # 4. Crear registro en DB
        nueva_novedad = Novedad(
            titulo=analisis.get("titulo", texto[:50]),
            descripcion=texto,
            user_phone=None,  # No se vincula a usuario por FK para evitar errores de tipo
            categoria_id=categoria_id,
            severidad=analisis.get("severidad", SeveridadEnum.MEDIA),
            estado=EstadoEnum.ABIERTA,
            fecha_registro=datetime.now(timezone.utc)
        )

        try:
            db.session.add(nueva_novedad)
            db.session.commit()

            # 5. Enviar respuesta al usuario por WhatsApp
            respuesta = analisis.get("respuesta_usuario", "Recibimos tu mensaje. En breve te responderemos.")
            NovedadService._enviar_whatsapp(phone, respuesta)
            NovedadService._store_message(phone, "bot", respuesta)

            return nueva_novedad
        except Exception as e:
            db.session.rollback()
            print(f"Error guardando novedad: {e}")
            return None

    @staticmethod
    def _match_categoria_por_palabras_clave(texto):
        """Busca si el texto contiene la palabra clave de alguna categoría."""
        texto_lower = texto.lower()
        try:
            categorias = Categoria.query.all()
            for cat in categorias:
                if cat.palabra_clave and cat.palabra_clave.lower() in texto_lower:
                    return cat
        except Exception as e:
            print(f"Error buscando categorías: {e}")
        return None

    @staticmethod
    def _analizar_con_ia(texto, categoria_detectada=None):
        """Llama a Groq para clasificar el mensaje y generar una respuesta al usuario."""
        try:
            categorias = Categoria.query.all()
            nombres = [c.nombre for c in categorias] if categorias else ["General"]
            categorias_str = ", ".join(f"'{n}'" for n in nombres)

            system_prompt = (
                "Eres un asistente de atención al cliente. Analiza el mensaje y responde SOLO en JSON válido.\n"
                "Campos requeridos:\n"
                "1. 'titulo': resumen del mensaje en máximo 8 palabras.\n"
                "2. 'severidad': nivel de urgencia: 'critica', 'alta', 'media' o 'baja'.\n"
                f"3. 'categoria': clasifica en una de estas categorías: {categorias_str}.\n"
                "4. 'respuesta_usuario': mensaje amigable y breve para enviarle al usuario por WhatsApp. "
                "Confirma que recibiste su mensaje y oriéntalo según el tema."
            )

            if categoria_detectada:
                system_prompt += f"\nNota: el mensaje fue clasificado automáticamente como '{categoria_detectada.nombre}' por palabra clave."

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": texto}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"Error con Groq: {e}")
            return {
                "titulo": "Mensaje recibido",
                "severidad": "media",
                "categoria": None,
                "respuesta_usuario": "Recibimos tu mensaje. En breve te daremos más información."
            }

    @staticmethod
    def _enviar_whatsapp(phone, mensaje):
        """Envía un mensaje de texto via Meta WhatsApp Cloud API."""
        if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
            print(f"[WhatsApp] Credenciales no configuradas. Mensaje para {phone}: {mensaje}")
            return

        url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": str(phone),
            "type": "text",
            "text": {"body": mensaje}
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            print(f"[WhatsApp] Mensaje enviado a {phone}: {response.json()}")
        except Exception as e:
            print(f"[WhatsApp] Error enviando a {phone}: {e}")

    @staticmethod
    def toggle_bot(phone):
        """Activa o desactiva el bot para una conversación. Retorna el nuevo estado."""
        phone = str(phone)
        _bot_states[phone] = not _bot_states.get(phone, True)
        return _bot_states[phone]

    @staticmethod
    def set_bot_state(phone, active):
        """Establece el estado del bot para una conversación."""
        phone = str(phone)
        _bot_states[phone] = bool(active)
        return _bot_states[phone]

    @staticmethod
    def enviar_mensaje_manual(phone, mensaje):
        """Envía un mensaje manual desde el dashboard (ignora estado del bot)."""
        phone = str(phone)
        NovedadService._enviar_whatsapp(phone, mensaje)
        NovedadService._store_message(phone, "bot", mensaje)

    @staticmethod
    def get_conversations():
        """Retorna todas las conversaciones activas con sus mensajes."""
        result = []
        for phone, msgs in _conversations.items():
            last = msgs[-1] if msgs else {}
            result.append({
                "phone": phone,
                "bot_active": _bot_states.get(phone, True),
                "last_message": last.get("text", ""),
                "last_time": last.get("time", ""),
                "messages": msgs
            })
        # Ordenar por última actividad (más reciente primero)
        result.sort(key=lambda x: x["last_time"], reverse=True)
        return result

    @staticmethod
    def _store_message(phone, role, text):
        """Guarda un mensaje en el historial de conversación."""
        phone = str(phone)
        if phone not in _conversations:
            _conversations[phone] = []
        _conversations[phone].append({
            "role": role,
            "text": text,
            "time": datetime.now(timezone.utc).isoformat()
        })

    @staticmethod
    def get_all_novedades():
        return Novedad.query.order_by(Novedad.fecha_registro.desc()).all()

    @staticmethod
    def create_novedad(titulo, descripcion, severidad, estado=None, categoria_id=None, user_phone=None):
        """Crea una novedad manualmente desde el dashboard."""
        sev = SeveridadEnum(severidad) if severidad else SeveridadEnum.MEDIA
        est = EstadoEnum(estado) if estado else EstadoEnum.ABIERTA
        novedad = Novedad(
            titulo=titulo,
            descripcion=descripcion,
            severidad=sev,
            estado=est,
            categoria_id=categoria_id,
            user_phone=user_phone,
            fecha_registro=datetime.now(timezone.utc),
        )
        db.session.add(novedad)
        db.session.commit()
        return novedad

    @staticmethod
    def get_dashboard_metrics():
        """Calcula métricas reales del dashboard desde la tabla novedades."""
        from sqlalchemy import func, cast, Date
        from datetime import date, timedelta

        today = date.today()

        total = Novedad.query.count()
        open_cases = Novedad.query.filter_by(estado=EstadoEnum.ABIERTA).count()
        resolved_today = Novedad.query.filter(
            Novedad.estado == EstadoEnum.RESUELTA,
            cast(Novedad.fecha_registro, Date) == today,
        ).count()
        critical_open = Novedad.query.filter(
            Novedad.severidad == SeveridadEnum.CRITICA,
            Novedad.estado == EstadoEnum.ABIERTA,
        ).count()

        # Distribución por severidad
        by_severity = {}
        for sev in SeveridadEnum:
            by_severity[sev.value] = Novedad.query.filter_by(severidad=sev).count()

        # Distribución por estado
        by_status = {}
        for est in EstadoEnum:
            by_status[est.value] = Novedad.query.filter_by(estado=est).count()

        # Tendencia últimos 7 días
        recent_trend = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            count = Novedad.query.filter(
                cast(Novedad.fecha_registro, Date) == day
            ).count()
            recent_trend.append({"date": day.strftime("%b %d"), "count": count})

        return {
            "totalCases": total,
            "openCases": open_cases,
            "resolvedToday": resolved_today,
            "criticalOpen": critical_open,
            "bySeverity": by_severity,
            "byStatus": by_status,
            "recentTrend": recent_trend,
        }

    @staticmethod
    def get_bot_metrics():
        """Calcula métricas reales del bot desde conversaciones en memoria y la DB."""
        from sqlalchemy import cast, func
        from datetime import date, timedelta
        from collections import defaultdict

        total_conversations = len(_conversations)

        # Mensajes totales del bot
        bot_messages = sum(
            sum(1 for m in msgs if m["role"] == "bot")
            for msgs in _conversations.values()
        )

        # Tasa de respuesta: % de conversaciones donde el bot respondió al menos una vez
        responded = sum(
            1 for msgs in _conversations.values()
            if any(m["role"] == "bot" for m in msgs)
        )
        response_rate = round((responded / total_conversations * 100) if total_conversations else 0)

        # Uso por día (últimos 7 días)
        today = date.today()
        counts_by_day = defaultdict(int)
        for msgs in _conversations.values():
            for m in msgs:
                try:
                    msg_date = datetime.fromisoformat(m["time"]).date()
                    counts_by_day[msg_date] += 1
                except Exception:
                    pass

        usage_over_time = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            usage_over_time.append({"date": str(day), "count": counts_by_day.get(day, 0)})

        # Efectividad: novedades con categoría vs sin categoría
        con_categoria = Novedad.query.filter(Novedad.categoria_id.isnot(None)).count()
        sin_categoria = Novedad.query.filter(Novedad.categoria_id.is_(None)).count()

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
