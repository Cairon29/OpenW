import re
from datetime import datetime, timezone, timedelta
from src.extensions import db
from src.db.models.conversation_state import ConversationState
from src.db.models.enums import OnboardingStepEnum, RoleMensajeEnum
from src.utils.whatsapp import enviar_whatsapp
from src.utils.messages import store_message
from src.utils.menu_builders import build_vicepresidencia_menu


VERIFICATION_TIMEOUT = timedelta(minutes=3)
ALLOWED_DOMAIN = "fiduprevisora.com.co"


class AuthService:

    @staticmethod
    def is_valid_email(text: str) -> bool:
        """Valida si el texto tiene formato de email y dominio @fiduprevisora.com.co."""
        text = text.strip().lower()
        if not re.match(r'^[\w\.\-]+@[\w\.\-]+\.\w{2,}$', text):
            return False
        return text.endswith(f"@{ALLOWED_DOMAIN}")

    @staticmethod
    def email_validation_error(text: str) -> str | None:
        """Retorna mensaje de error específico o None si el email es válido."""
        text = text.strip().lower()
        if not re.match(r'^[\w\.\-]+@[\w\.\-]+\.\w{2,}$', text):
            return "El formato del email no es válido. Ejemplo: nombre@fiduprevisora.com.co"
        if not text.endswith(f"@{ALLOWED_DOMAIN}"):
            return f"Solo se permiten emails con dominio @{ALLOWED_DOMAIN}"
        return None

    @staticmethod
    def verify_email(token: str) -> bool:
        """
        Verifica el token de email. Si es válido y no expiró,
        transiciona a PENDING_VICEPRESIDENCIA y envía el menú de VPs.
        """
        state = ConversationState.query.filter_by(verification_token=token).first()

        if not state or state.onboarding_step != OnboardingStepEnum.PENDING_VERIFICATION:
            return False

        elapsed = datetime.now(timezone.utc) - state.verification_sent_at.replace(tzinfo=timezone.utc)
        if elapsed > VERIFICATION_TIMEOUT:
            state.onboarding_step    = OnboardingStepEnum.PENDING_EMAIL
            state.verification_token = None
            db.session.commit()
            return False

        state.onboarding_step    = OnboardingStepEnum.PENDING_VICEPRESIDENCIA
        state.verification_token = None
        db.session.commit()

        menu = build_vicepresidencia_menu()
        if menu:
            respuesta = menu
        else:
            # Sin vicepresidencias en DB, saltar directo a novedad
            state.onboarding_step = OnboardingStepEnum.PENDING_NOVEDAD
            db.session.commit()
            respuesta = (
                "✅ *Tu email fue verificado con éxito.*\n\n"
                "Describí tu novedad de ciberseguridad."
            )

        wamid = enviar_whatsapp(state.phone, respuesta)
        store_message(state.phone, RoleMensajeEnum.BOT, respuesta, wa_message_id=wamid)
        return True
