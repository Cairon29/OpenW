"""Fase 4: Selección de vicepresidencia desde lista numerada."""

from src.extensions import db
from src.db.models.vicepresidencia import Vicepresidencia
from src.db.models.enums import OnboardingStepEnum
from src.utils.ai_validation import validate_input
from src.utils.menu_builders import build_vicepresidencia_menu, build_direccion_menu
from .helpers import send_and_store


def handle_pending_vicepresidencia(estado, phone, texto, es_nuevo):
    vps = Vicepresidencia.query.order_by(Vicepresidencia.id).all()
    if not vps:
        estado.onboarding_step = OnboardingStepEnum.PENDING_NOVEDAD
        db.session.commit()
        send_and_store(phone, "Describí tu novedad de ciberseguridad.")
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
                send_and_store(phone, ai["guidance_message"] or f"Opción no válida. {menu}")
                return
        else:
            menu = build_vicepresidencia_menu()
            send_and_store(phone, ai["guidance_message"] or f"Opción no válida. {menu}")
            return

    vp_elegida = vps[seleccion - 1]
    estado.fk_id_vicepresidencia = vp_elegida.id
    estado.fk_id_direccion = None
    estado.onboarding_step = OnboardingStepEnum.PENDING_DIRECCION
    db.session.commit()

    menu = build_direccion_menu(vp_elegida.id)
    if menu:
        send_and_store(phone, menu)
    else:
        estado.onboarding_step = OnboardingStepEnum.PENDING_NOVEDAD
        db.session.commit()
        send_and_store(
            phone,
            f"*{vp_elegida.nombre}* no tiene direcciones registradas.\n\n"
            "Describí tu novedad de ciberseguridad."
        )
