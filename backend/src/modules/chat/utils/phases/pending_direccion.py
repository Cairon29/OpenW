"""Fase 5: Selección de dirección filtrada por vicepresidencia."""

from src.extensions import db
from src.db.models.direccion import Direccion
from src.db.models.enums import OnboardingStepEnum
from src.utils.ai_validation import validate_input
from src.utils.menu_builders import build_direccion_menu
from .helpers import send_and_store


def handle_pending_direccion(estado, phone, texto, es_nuevo):
    dirs = Direccion.query.filter_by(
        fk_id_vicepresidencia=estado.fk_id_vicepresidencia
    ).order_by(Direccion.id).all()

    if not dirs:
        estado.onboarding_step = OnboardingStepEnum.PENDING_NOVEDAD
        db.session.commit()
        send_and_store(phone, "Describí tu novedad de ciberseguridad.")
        return

    try:
        seleccion = int(texto.strip())
        if seleccion < 1 or seleccion > len(dirs):
            raise ValueError
    except ValueError:
        ai = validate_input("menu_selection", texto, phone, {
            "menu_options": "\n".join(f"{i+1}. {d.nombre}" for i, d in enumerate(dirs)),
            "menu_type": "Dirección",
        })
        if ai["is_valid"] and ai["extracted_value"]:
            try:
                seleccion = int(ai["extracted_value"])
                if seleccion < 1 or seleccion > len(dirs):
                    raise ValueError
            except ValueError:
                menu = build_direccion_menu(estado.fk_id_vicepresidencia)
                send_and_store(phone, ai["guidance_message"] or f"Opción no válida. {menu}")
                return
        else:
            menu = build_direccion_menu(estado.fk_id_vicepresidencia)
            send_and_store(phone, ai["guidance_message"] or f"Opción no válida. {menu}")
            return

    dir_elegida = dirs[seleccion - 1]
    estado.fk_id_direccion = dir_elegida.id
    estado.onboarding_step = OnboardingStepEnum.PENDING_NOVEDAD
    db.session.commit()

    send_and_store(
        phone,
        "Ahora describí tu novedad de ciberseguridad. "
        "Contanos qué pasó con el mayor detalle posible."
    )
