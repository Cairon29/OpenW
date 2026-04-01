import secrets
import time
import requests
from src.extensions import db
from src.db.models import Novedad, SeveridadEnum, EstadoEnum
from src.db.models.vicepresidencia import Vicepresidencia
from src.db.models.direccion import Direccion
from src.db.models.chat_message import ChatMessage
from src.db.models.conversation_state import ConversationState
from src.db.models.enums import OnboardingStepEnum, RoleMensajeEnum
from src.utils.email import send_verification_email
from src.utils.whatsapp import enviar_whatsapp
from src.utils.messages import store_message
from src.utils.classification import classify_message
from src.utils.ai_validation import validate_input
from src.utils.menu_builders import (
    build_vicepresidencia_menu,
    build_direccion_menu,
    build_confirmation_summary,
    build_modification_menu,
)
from src.modules.auth.service import AuthService, VERIFICATION_TIMEOUT
from datetime import datetime, timezone
from src.config import config


# WhatsApp credentials from config
WHATSAPP_ACCESS_TOKEN = config.WHATSAPP_ACCESS_TOKEN
WHATSAPP_PHONE_NUMBER_ID = config.WHATSAPP_PHONE_NUMBER_ID

SEVERIDAD_MAP = {
    "critica": SeveridadEnum.CRITICA,
    "alta": SeveridadEnum.ALTA,
    "media": SeveridadEnum.MEDIA,
    "baja": SeveridadEnum.BAJA,
    "informativa": SeveridadEnum.INFO,
}


def _send_and_store(phone, respuesta):
    """Helper: envía un mensaje por WhatsApp y lo almacena en la DB."""
    wamid = enviar_whatsapp(phone, respuesta)
    store_message(phone, RoleMensajeEnum.BOT, respuesta, wa_message_id=wamid)
    return wamid


class ChatService:

    # ── Dispatcher ────────────────────────────────────────────────────────────

    _PHASE_HANDLERS = {
        OnboardingStepEnum.BIENVENIDA:             '_handle_bienvenida',
        OnboardingStepEnum.PENDING_EMAIL:           '_handle_pending_email',
        OnboardingStepEnum.PENDING_VERIFICATION:    '_handle_pending_verification',
        OnboardingStepEnum.PENDING_VICEPRESIDENCIA: '_handle_pending_vicepresidencia',
        OnboardingStepEnum.PENDING_DIRECCION:       '_handle_pending_direccion',
        OnboardingStepEnum.PENDING_NOVEDAD:         '_handle_pending_novedad',
        OnboardingStepEnum.PENDING_CONFIRMACION:    '_handle_pending_confirmacion',
        OnboardingStepEnum.COMPLETED:               '_handle_completed',
        OnboardingStepEnum.EXPIRED:                 '_handle_expired',
    }

    @staticmethod
    def procesar_mensaje_whatsapp(phone, texto, wa_message_id=None):
        """Procesa un mensaje entrante de WhatsApp usando el dispatcher de fases."""
        phone = str(phone)

        estado, es_nuevo = ChatService._get_or_create_state(phone)
        store_message(phone, RoleMensajeEnum.USER, texto, wa_message_id=wa_message_id)

        if not ChatService._get_bot_state(phone):
            return None

        handler_name = ChatService._PHASE_HANDLERS.get(estado.onboarding_step)
        if handler_name:
            handler = getattr(ChatService, handler_name)
            return handler(estado, phone, texto, es_nuevo)
        return None

    # ── Phase handlers ────────────────────────────────────────────────────────

    @staticmethod
    def _handle_bienvenida(estado, phone, texto, es_nuevo):
        """Fase 1: Enviar template de bienvenida y solicitar email."""
        ChatService._enviar_template_whatsapp(phone, "mensaje_bienvenida")
        # Meta acepta el request rápido pero entrega la template con demora en su pipeline.
        # Se espera 5s para garantizar que el mensaje de bienvenida llegue antes del siguiente.
        time.sleep(5)
        estado.onboarding_step = OnboardingStepEnum.PENDING_EMAIL
        db.session.commit()

        respuesta = (
            "Para continuar, necesitamos tu email corporativo "
            "(*@fiduprevisora.com.co*)."
        )
        _send_and_store(phone, respuesta)

    @staticmethod
    def _handle_pending_email(estado, phone, texto, es_nuevo):
        """Fase 2: Validar email con dominio @fiduprevisora.com.co."""
        error = AuthService.email_validation_error(texto)
        if error:
            ai = validate_input("email", texto, phone, {"allowed_domain": "fiduprevisora.com.co"})
            if ai["is_valid"] and ai["extracted_value"]:
                extracted = ai["extracted_value"]
                if not AuthService.email_validation_error(extracted):
                    texto = extracted
                else:
                    _send_and_store(phone, ai["guidance_message"] or error)
                    return
            else:
                _send_and_store(phone, ai["guidance_message"] or error)
                return

        token = secrets.token_urlsafe(32)
        estado.email                = texto.strip().lower()
        estado.verification_token   = token
        estado.verification_sent_at = datetime.now(timezone.utc)
        estado.onboarding_step      = OnboardingStepEnum.PENDING_VERIFICATION
        db.session.commit()

        send_verification_email(estado.email, token)
        respuesta = (
            f"Te enviamos un email a *{estado.email}*.\n"
            "Tenés *3 minutos* para verificarlo antes de que el link expire."
        )
        _send_and_store(phone, respuesta)

    @staticmethod
    def _handle_pending_verification(estado, phone, texto, es_nuevo):
        """Fase 3: Esperando verificación de email."""
        elapsed = datetime.now(timezone.utc) - estado.verification_sent_at.replace(tzinfo=timezone.utc)
        if elapsed > VERIFICATION_TIMEOUT:
            estado.onboarding_step    = OnboardingStepEnum.PENDING_EMAIL
            estado.verification_token = None
            db.session.commit()
            respuesta = (
                "El tiempo de verificación venció. "
                "Escribí tu email nuevamente para recibir un nuevo link."
            )
        else:
            respuesta = (
                "Todavía no verificaste tu email. "
                "Revisá tu bandeja de entrada y hacé click en el botón de confirmación."
            )
        _send_and_store(phone, respuesta)

    @staticmethod
    def _handle_pending_vicepresidencia(estado, phone, texto, es_nuevo):
        """Fase 4: Selección de vicepresidencia desde lista numerada."""
        vps = Vicepresidencia.query.order_by(Vicepresidencia.id).all()
        if not vps:
            # Sin VPs en DB, saltar a novedad
            estado.onboarding_step = OnboardingStepEnum.PENDING_NOVEDAD
            db.session.commit()
            _send_and_store(phone, "Describí tu novedad de ciberseguridad.")
            return

        try:
            seleccion = int(texto.strip())
            if seleccion < 1 or seleccion > len(vps):
                raise ValueError
        except ValueError:
            ai = validate_input("menu_selection", texto, phone, {
                "menu_options": "\n".join(f"{i+1}. {vp.nombre}" for i, vp in enumerate(vps)),
                "menu_type": "Vicepresidencia",
            })
            if ai["is_valid"] and ai["extracted_value"]:
                try:
                    seleccion = int(ai["extracted_value"])
                    if seleccion < 1 or seleccion > len(vps):
                        raise ValueError
                except ValueError:
                    menu = build_vicepresidencia_menu()
                    _send_and_store(phone, ai["guidance_message"] or f"Opción no válida. {menu}")
                    return
            else:
                menu = build_vicepresidencia_menu()
                _send_and_store(phone, ai["guidance_message"] or f"Opción no válida. {menu}")
                return

        vp_elegida = vps[seleccion - 1]
        estado.fk_id_vicepresidencia = vp_elegida.id
        estado.fk_id_direccion = None  # Reset por si cambia de VP
        estado.onboarding_step = OnboardingStepEnum.PENDING_DIRECCION
        db.session.commit()

        menu = build_direccion_menu(vp_elegida.id)
        if menu:
            _send_and_store(phone, menu)
        else:
            # VP sin direcciones, saltar a novedad
            estado.onboarding_step = OnboardingStepEnum.PENDING_NOVEDAD
            db.session.commit()
            _send_and_store(
                phone,
                f"*{vp_elegida.nombre}* no tiene direcciones registradas.\n\n"
                "Describí tu novedad de ciberseguridad."
            )

    @staticmethod
    def _handle_pending_direccion(estado, phone, texto, es_nuevo):
        """Fase 5: Selección de dirección filtrada por vicepresidencia."""
        dirs = Direccion.query.filter_by(
            fk_id_vicepresidencia=estado.fk_id_vicepresidencia
        ).order_by(Direccion.id).all()

        if not dirs:
            estado.onboarding_step = OnboardingStepEnum.PENDING_NOVEDAD
            db.session.commit()
            _send_and_store(phone, "Describí tu novedad de ciberseguridad.")
            return

        try:
            seleccion = int(texto.strip())
            if seleccion < 1 or seleccion > len(dirs):
                raise ValueError
        except ValueError:
            ai = validate_input("menu_selection", texto, phone, {
                "menu_options": "\n".join(f"{i+1}. {d.nombre}" for i, d in enumerate(dirs)),
                "menu_type": "Dirección",
            })
            if ai["is_valid"] and ai["extracted_value"]:
                try:
                    seleccion = int(ai["extracted_value"])
                    if seleccion < 1 or seleccion > len(dirs):
                        raise ValueError
                except ValueError:
                    menu = build_direccion_menu(estado.fk_id_vicepresidencia)
                    _send_and_store(phone, ai["guidance_message"] or f"Opción no válida. {menu}")
                    return
            else:
                menu = build_direccion_menu(estado.fk_id_vicepresidencia)
                _send_and_store(phone, ai["guidance_message"] or f"Opción no válida. {menu}")
                return

        dir_elegida = dirs[seleccion - 1]
        estado.fk_id_direccion = dir_elegida.id
        estado.onboarding_step = OnboardingStepEnum.PENDING_NOVEDAD
        db.session.commit()

        _send_and_store(
            phone,
            "Ahora describí tu novedad de ciberseguridad. "
            "Contanos qué pasó con el mayor detalle posible."
        )

    @staticmethod
    def _handle_pending_novedad(estado, phone, texto, es_nuevo):
        """Fase 6: Clasificar novedad con IA y guardar resultado temporal."""
        analisis = classify_message(phone, texto)

        categoria_obj = analisis.get("categoria_obj")
        estado.pending_titulo       = analisis.get("titulo", texto[:50])
        estado.pending_descripcion  = texto
        estado.pending_severidad    = analisis.get("severidad", "media")
        estado.pending_categoria_id = categoria_obj.id if categoria_obj else None
        estado.pending_respuesta    = analisis.get("respuesta_usuario")
        estado.awaiting_modification = False
        estado.onboarding_step      = OnboardingStepEnum.PENDING_CONFIRMACION
        db.session.commit()

        summary = build_confirmation_summary(estado)
        _send_and_store(phone, summary)

    @staticmethod
    def _handle_pending_confirmacion(estado, phone, texto, es_nuevo):
        """Fase 7: Confirmación de datos o modificación."""
        txt = texto.strip().lower()

        # ── Sub-flujo de modificación ─────────────────────────────────────
        if estado.awaiting_modification:
            if txt == "1":
                # Cambiar VP → también invalida dirección
                estado.fk_id_vicepresidencia = None
                estado.fk_id_direccion = None
                estado.awaiting_modification = False
                estado.onboarding_step = OnboardingStepEnum.PENDING_VICEPRESIDENCIA
                db.session.commit()
                menu = build_vicepresidencia_menu()
                _send_and_store(phone, menu or "No hay vicepresidencias registradas.")
            elif txt == "2":
                # Cambiar dirección (mantiene VP actual)
                estado.fk_id_direccion = None
                estado.awaiting_modification = False
                estado.onboarding_step = OnboardingStepEnum.PENDING_DIRECCION
                db.session.commit()
                menu = build_direccion_menu(estado.fk_id_vicepresidencia)
                _send_and_store(phone, menu or "No hay direcciones registradas.")
            elif txt == "3":
                # Cambiar novedad
                estado.pending_titulo = None
                estado.pending_descripcion = None
                estado.pending_severidad = None
                estado.pending_categoria_id = None
                estado.pending_respuesta = None
                estado.awaiting_modification = False
                estado.onboarding_step = OnboardingStepEnum.PENDING_NOVEDAD
                db.session.commit()
                _send_and_store(phone, "Describí nuevamente tu novedad de ciberseguridad.")
            else:
                ai = validate_input("confirmation", texto, phone, {
                    "valid_options": "1. Vicepresidencia\n2. Dirección\n3. Novedad",
                    "mode": "modificacion",
                })
                if ai["is_valid"] and ai["extracted_value"] in ("1", "2", "3"):
                    return ChatService._handle_pending_confirmacion(
                        estado, phone, ai["extracted_value"], es_nuevo
                    )
                _send_and_store(phone, ai.get("guidance_message") or build_modification_menu())
            return

        # ── Flujo principal de confirmación ───────────────────────────────
        if txt in ("1", "si", "sí", "confirmar", "si, confirmar"):
            return ChatService._create_novedad_from_state(estado, phone)

        if txt in ("2", "modificar", "no"):
            estado.awaiting_modification = True
            db.session.commit()
            _send_and_store(phone, build_modification_menu())
            return

        # Input no reconocido → fallback IA
        ai = validate_input("confirmation", texto, phone, {
            "valid_options": "1. Confirmar\n2. Modificar",
            "mode": "confirmacion",
        })
        if ai["is_valid"] and ai["extracted_value"] == "confirmar":
            return ChatService._create_novedad_from_state(estado, phone)
        if ai["is_valid"] and ai["extracted_value"] == "modificar":
            estado.awaiting_modification = True
            db.session.commit()
            _send_and_store(phone, build_modification_menu())
            return

        summary = build_confirmation_summary(estado)
        _send_and_store(phone, ai.get("guidance_message") or summary)

    @staticmethod
    def _handle_completed(estado, phone, texto, es_nuevo):
        """Fase 8: Post-novedad. Permite reportar otra o despedirse."""
        txt = texto.strip().lower()

        if txt in ("si", "sí", "otra", "si, otra"):
            estado.onboarding_step = OnboardingStepEnum.PENDING_NOVEDAD
            db.session.commit()
            _send_and_store(phone, "Describí tu nueva novedad de ciberseguridad.")
            return

        if txt in ("no", "no, gracias", "chau", "gracias"):
            _send_and_store(
                phone,
                "¡Gracias por tu reporte! Si necesitás reportar otra novedad, "
                "escribinos en cualquier momento."
            )
            return

        # Cualquier otro texto → tratar como nueva novedad directamente
        estado.onboarding_step = OnboardingStepEnum.PENDING_NOVEDAD
        db.session.commit()
        return ChatService._handle_pending_novedad(estado, phone, texto, es_nuevo)

    @staticmethod
    def _handle_expired(estado, phone, texto, es_nuevo):
        """Estado legacy: resetear a PENDING_EMAIL."""
        estado.onboarding_step = OnboardingStepEnum.PENDING_EMAIL
        db.session.commit()
        _send_and_store(
            phone,
            "Para continuar, necesitamos tu email corporativo "
            "(*@fiduprevisora.com.co*)."
        )

    # ── Novedad creation ──────────────────────────────────────────────────────

    @staticmethod
    def _create_novedad_from_state(estado, phone):
        """Crea la Novedad con los datos almacenados en ConversationState."""
        nueva_novedad = Novedad(
            titulo=estado.pending_titulo,
            descripcion=estado.pending_descripcion,
            fk_id_usuario=None,
            fk_id_direccion=estado.fk_id_direccion,
            fk_id_categoria=estado.pending_categoria_id,
            severidad=SEVERIDAD_MAP.get(estado.pending_severidad, SeveridadEnum.MEDIA),
            estado=EstadoEnum.ABIERTA,
            fecha_registro=datetime.now(timezone.utc),
        )

        try:
            db.session.add(nueva_novedad)

            # Limpiar campos pending (pero mantener perfil: email, VP, dirección)
            estado.pending_titulo = None
            estado.pending_descripcion = None
            estado.pending_severidad = None
            estado.pending_categoria_id = None
            estado.pending_respuesta = None
            estado.awaiting_modification = False
            estado.onboarding_step = OnboardingStepEnum.COMPLETED
            db.session.commit()

            respuesta = (
                "✅ *Tu novedad fue registrada exitosamente.*\n\n"
                "¿Querés reportar otra novedad?\n\n"
                "*Sí* — para reportar otra\n"
                "*No* — para finalizar"
            )
            _send_and_store(phone, respuesta)
            return nueva_novedad
        except Exception as e:
            db.session.rollback()
            print(f"Error guardando novedad: {e}")
            _send_and_store(
                phone,
                "Ocurrió un error al guardar tu reporte. Por favor, intentá de nuevo."
            )
            return None

    # ── State management ──────────────────────────────────────────────────────
        # TODO: refactorizar esta clase para separar lógica de conversación (handlers) de utilidades de 
        # estado y envío de mensajes. Quizás crear un ConversationManager para manejar estado y mensajes, 
        # y dejar ChatService solo como orquestador de fases. 
    @staticmethod
    def _get_or_create_state(phone: str):
        """Retorna (ConversationState, es_nuevo)."""
        state = ConversationState.query.get(phone)
        if state is not None:
            return state, False
        state = ConversationState(phone=phone, onboarding_step=OnboardingStepEnum.BIENVENIDA)
        db.session.add(state)
        db.session.commit()
        return state, True

    @staticmethod
    def _enviar_template_whatsapp(phone: str, template_name: str, lang_code: str = "es_CO"):
        """Envia una plantilla de WhatsApp via Meta Cloud API."""
        if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
            print(f"[WhatsApp] Credenciales no configuradas. Template '{template_name}' para {phone}")
            return None

        url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": str(phone),
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": lang_code},
            },
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            wamid = data.get("messages", [{}])[0].get("id")
            print(f"[WhatsApp] Template '{template_name}' enviado a {phone}: {wamid}")
            return wamid
        except Exception as e:
            print(f"[WhatsApp] Error enviando template a {phone}: {e}")
            return None

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
        wamid = enviar_whatsapp(phone, mensaje)
        store_message(phone, "bot", mensaje, wa_message_id=wamid)

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
