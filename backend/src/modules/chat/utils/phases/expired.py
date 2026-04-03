"""Estado legacy: resetear a PENDING_EMAIL."""

from src.extensions import db
from src.db.models.enums import OnboardingStepEnum
from .helpers import send_and_store


def handle_expired(estado, phone, texto, es_nuevo):
    estado.onboarding_step = OnboardingStepEnum.PENDING_EMAIL
    db.session.commit()
    send_and_store(
        phone,
        "Para continuar, necesitamos tu email corporativo "
        "(*@fiduprevisora.com.co*)."
    )
