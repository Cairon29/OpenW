"""Fase 3: Esperando verificación de email."""

from datetime import datetime, timezone

from src.extensions import db
from src.db.models.enums import OnboardingStepEnum
from src.modules.auth.service import VERIFICATION_TIMEOUT
from .helpers import send_and_store


def handle_pending_verification(estado, phone, texto, es_nuevo):
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
    send_and_store(phone, respuesta)
