"""Fase 8: Post-novedad. Permite reportar otra o despedirse."""

from src.extensions import db
from src.db.models.enums import OnboardingStepEnum
from .helpers import send_and_store
from .pending_novedad import handle_pending_novedad


def handle_completed(estado, phone, texto, es_nuevo):
    txt = texto.strip().lower()

    if txt in ("si", "sí", "otra", "si, otra"):
        estado.onboarding_step = OnboardingStepEnum.PENDING_NOVEDAD
        db.session.commit()
        send_and_store(phone, "Describí tu nueva novedad de ciberseguridad.")
        return

    if txt in ("no", "no, gracias", "chau", "gracias"):
        send_and_store(
            phone,
            "¡Gracias por tu reporte! Si necesitás reportar otra novedad, "
            "escribinos en cualquier momento."
        )
        return

    # Cualquier otro texto → tratar como nueva novedad directamente
    estado.onboarding_step = OnboardingStepEnum.PENDING_NOVEDAD
    db.session.commit()
    return handle_pending_novedad(estado, phone, texto, es_nuevo)
