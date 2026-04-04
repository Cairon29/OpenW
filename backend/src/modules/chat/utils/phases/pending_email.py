"""Fase 2: Validar email con dominio @fiduprevisora.com.co."""

import secrets
from datetime import datetime, timezone

from src.extensions import db
from src.db.models.enums import OnboardingStepEnum
from src.utils.email import send_verification_email
from src.utils.ai_validation import validate_input
from src.modules.auth.service import AuthService, ALLOWED_DOMAIN
from .helpers import send_and_store


def handle_pending_email(estado, phone, texto, es_nuevo):
    error = AuthService.email_validation_error(texto)
    if error:
        ai = validate_input("email", texto, phone, {"allowed_domain": ALLOWED_DOMAIN})
        if ai["is_valid"] and ai["extracted_value"]:
            extracted = ai["extracted_value"]
            if not AuthService.email_validation_error(extracted):
                texto = extracted
            else:
                send_and_store(phone, ai["guidance_message"] or error)
                return
        else:
            send_and_store(phone, ai["guidance_message"] or error)
            return

    token = secrets.token_urlsafe(32)
    estado.email                = texto.strip().lower()
    estado.verification_token   = token
    estado.verification_sent_at = datetime.now(timezone.utc)
    estado.onboarding_step      = OnboardingStepEnum.PENDING_VERIFICATION
    db.session.commit()

    send_verification_email(estado.email, token)
    send_and_store(
        phone,
        f"Te enviamos un email a *{estado.email}*.\n"
        "Tenés *3 minutos* para verificarlo antes de que el link expire."
    )
