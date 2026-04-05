"""Fase 1: Enviar template de bienvenida y solicitar email."""

import time
from src.extensions import db
from src.db.models.enums import OnboardingStepEnum
from .helpers import send_and_store, enviar_template_whatsapp

def handle_bienvenida(estado, phone, texto, es_nuevo):
    enviar_template_whatsapp(phone, "mensaje_bienvenida")
    # Meta acepta el request rápido pero entrega la template con demora en su pipeline.
    #
    estado.onboarding_step = OnboardingStepEnum.PENDING_EMAIL
    db.session.commit()

    send_and_store(
        phone,
        "Para continuar, necesitamos tu email corporativo "
        "(*@fiduprevisora.com.co*)."
    )
