"""
ChatService: orquestador de fases conversacionales.
Delega phase handlers a utils/phases.py y dashboard a utils/dashboard.py.
"""

from src.extensions import db
from src.db.models.conversation_state import ConversationState
from src.db.models.enums import OnboardingStepEnum, RoleMensajeEnum
from src.utils.messages import store_message
from src.modules.chat.utils.phases import (
    handle_bienvenida,
    handle_pending_email,
    handle_pending_verification,
    handle_pending_vicepresidencia,
    handle_pending_direccion,
    handle_pending_novedad,
    handle_pending_confirmacion,
    handle_completed,
    handle_expired,
)
from src.modules.chat.utils.dashboard import (
    toggle_bot as _toggle_bot,
    set_bot_state as _set_bot_state,
    enviar_mensaje_manual as _enviar_mensaje_manual,
    get_conversations as _get_conversations,
    update_message_status as _update_message_status,
    get_bot_metrics as _get_bot_metrics,
    _get_bot_state,
)


class ChatService:

    # ── Dispatcher ────────────────────────────────────────────────────────────

    _PHASE_HANDLERS = {
        OnboardingStepEnum.BIENVENIDA:              handle_bienvenida,
        OnboardingStepEnum.PENDING_EMAIL:           handle_pending_email,
        OnboardingStepEnum.PENDING_VERIFICATION:    handle_pending_verification,
        OnboardingStepEnum.PENDING_VICEPRESIDENCIA: handle_pending_vicepresidencia,
        OnboardingStepEnum.PENDING_DIRECCION:       handle_pending_direccion,
        OnboardingStepEnum.PENDING_NOVEDAD:         handle_pending_novedad,
        OnboardingStepEnum.PENDING_CONFIRMACION:    handle_pending_confirmacion,
        OnboardingStepEnum.COMPLETED:               handle_completed,
        OnboardingStepEnum.EXPIRED:                 handle_expired,
    }

    @staticmethod
    def enviar_indicador_escribiendo(phone, wa_message_id=None):
        """Mark last user message as read, show typing bubble on WA + CRM."""
        phone = str(phone)
        if not _get_bot_state(phone):
            return

        from src.modules.chat.events import publish
        publish({"type": "bot_typing_start", "phone": phone})

        if wa_message_id:
            from src.utils.whatsapp import enviar_indicador_typing
            enviar_indicador_typing(wa_message_id)


    @staticmethod
    def procesar_mensaje_whatsapp(phone, texto, wa_message_id=None, profile_name=None):
        """Procesa un mensaje entrante de WhatsApp usando el dispatcher de fases."""
        phone = str(phone)

        estado, es_nuevo = ChatService._get_or_create_state(phone)
        store_message(phone, RoleMensajeEnum.USER, texto, wa_message_id=wa_message_id)

        # Update WhatsApp profile data (dirties ORM, no commit)
        ChatService._update_profile(estado, profile_name)

        if not _get_bot_state(phone):
            db.session.commit()  # flush profile changes when bot is off
            return None

        # Typing indicator: WA (read + typing bubble) + CRM SSE
        ChatService.enviar_indicador_escribiendo(phone, wa_message_id)

        handler = ChatService._PHASE_HANDLERS.get(estado.onboarding_step)
        try:
            if handler:
                return handler(estado, phone, texto, es_nuevo)  # handler commits all
            db.session.commit()  # fallback commit if no handler matched
            return None
        finally:
            from src.modules.chat.events import publish
            publish({"type": "bot_typing_stop", "phone": phone})

    # ── State management ──────────────────────────────────────────────────────

    @staticmethod
    def _get_or_create_state(phone):
        """Retorna (ConversationState, es_nuevo)."""
        state = ConversationState.query.get(phone)
        if state is not None:
            return state, False
        state = ConversationState(phone=phone, onboarding_step=OnboardingStepEnum.BIENVENIDA)
        db.session.add(state)
        db.session.commit()
        return state, True

    # ── Profile management ─────────────────────────────────────────────────────

    @staticmethod
    def _update_profile(state, profile_name):
        """Update WhatsApp profile name if provided. No commit — handler flushes."""
        if profile_name and state.wa_profile_name != profile_name:
            state.wa_profile_name = profile_name

    # ── Dashboard (delegado a utils/dashboard.py) ─────────────────────────────

    toggle_bot = staticmethod(_toggle_bot)
    set_bot_state = staticmethod(_set_bot_state)
    enviar_mensaje_manual = staticmethod(_enviar_mensaje_manual)
    get_conversations = staticmethod(_get_conversations)
    update_message_status = staticmethod(_update_message_status)
    get_bot_metrics = staticmethod(_get_bot_metrics)
