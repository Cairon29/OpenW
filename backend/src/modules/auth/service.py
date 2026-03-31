import re
from datetime import datetime, timezone, timedelta
from src.extensions import db
from src.db.models.conversation_state import ConversationState
from src.db.models.enums import OnboardingStepEnum, RoleMensajeEnum
from src.utils.whatsapp import enviar_whatsapp
from src.utils.messages import store_message


VERIFICATION_TIMEOUT = timedelta(minutes=3)


class AuthService:

    @staticmethod
    def is_valid_email(text: str) -> bool:
        """Valida si el texto tiene formato de email."""
        return bool(re.match(r'^[\w\.\-]+@[\w\.\-]+\.\w{2,}$', text.strip()))

    @staticmethod
    def verify_email(token: str) -> bool:
        """
        Verifica el token de email. Marca la conversacion como VERIFIED si es valido y no expiró.
        Retorna True si la verificacion fue exitosa.
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

        state.onboarding_step    = OnboardingStepEnum.VERIFIED
        state.verification_token = None
        db.session.commit()

        respuesta = "¡Tu email fue verificado con éxito! Ya podés enviarnos tus consultas."
        wamid = enviar_whatsapp(state.phone, respuesta)
        store_message(state.phone, RoleMensajeEnum.BOT, respuesta, wa_message_id=wamid)
        return True
