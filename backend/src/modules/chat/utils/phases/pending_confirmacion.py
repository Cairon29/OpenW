"""Fase 7: Confirmación de datos o modificación."""

from src.extensions import db
from src.db.models.enums import OnboardingStepEnum
from src.utils.ai_validation import validate_input
from src.utils.menu_builders import (
    build_vicepresidencia_menu,
    build_direccion_menu,
    build_confirmation_summary,
    build_modification_menu,
)
from .helpers import send_and_store, create_novedad_from_state


def handle_pending_confirmacion(estado, phone, texto, es_nuevo):
    txt = texto.strip().lower()

    # ── Sub-flujo de modificación ─────────────────────────────────────
    if estado.awaiting_modification:
        if txt == "1":
            estado.fk_id_vicepresidencia = None
            estado.fk_id_direccion = None
            estado.awaiting_modification = False
            estado.onboarding_step = OnboardingStepEnum.PENDING_VICEPRESIDENCIA
            db.session.commit()
            menu = build_vicepresidencia_menu()
            send_and_store(phone, menu or "No hay vicepresidencias registradas.")
        elif txt == "2":
            estado.fk_id_direccion = None
            estado.awaiting_modification = False
            estado.onboarding_step = OnboardingStepEnum.PENDING_DIRECCION
            db.session.commit()
            menu = build_direccion_menu(estado.fk_id_vicepresidencia)
            send_and_store(phone, menu or "No hay direcciones registradas.")
        elif txt == "3":
            estado.pending_titulo = None
            estado.pending_descripcion = None
            estado.pending_severidad = None
            estado.pending_categoria_id = None
            estado.pending_respuesta = None
            estado.awaiting_modification = False
            estado.onboarding_step = OnboardingStepEnum.PENDING_NOVEDAD
            db.session.commit()
            send_and_store(phone, "Describí nuevamente tu novedad de ciberseguridad.")
        else:
            ai = validate_input("confirmation", texto, phone, {
                "valid_options": "1. Vicepresidencia\n2. Dirección\n3. Novedad",
                "mode": "modificacion",
            })
            if ai["is_valid"] and ai["extracted_value"] in ("1", "2", "3"):
                return handle_pending_confirmacion(
                    estado, phone, ai["extracted_value"], es_nuevo
                )
            send_and_store(phone, ai.get("guidance_message") or build_modification_menu())
        return

    # ── Flujo principal de confirmación ───────────────────────────────
    if txt in ("1", "si", "sí", "confirmar", "si, confirmar"):
        return create_novedad_from_state(estado, phone)

    if txt in ("2", "modificar", "no"):
        estado.awaiting_modification = True
        db.session.commit()
        send_and_store(phone, build_modification_menu())
        return

    # Input no reconocido → fallback IA
    ai = validate_input("confirmation", texto, phone, {
        "valid_options": "1. Confirmar\n2. Modificar",
        "mode": "confirmacion",
    })
    if ai["is_valid"] and ai["extracted_value"] == "confirmar":
        return create_novedad_from_state(estado, phone)
    if ai["is_valid"] and ai["extracted_value"] == "modificar":
        estado.awaiting_modification = True
        db.session.commit()
        send_and_store(phone, build_modification_menu())
        return

    summary = build_confirmation_summary(estado)
    send_and_store(phone, ai.get("guidance_message") or summary)
