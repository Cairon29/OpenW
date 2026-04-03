"""Fase 6: Clasificar novedad con IA y guardar resultado temporal."""

from src.extensions import db
from src.db.models.enums import OnboardingStepEnum
from src.utils.classification import classify_message
from src.utils.menu_builders import build_confirmation_summary
from .helpers import send_and_store


def handle_pending_novedad(estado, phone, texto, es_nuevo):
    analisis = classify_message(phone, texto)

    categoria_obj = analisis.get("categoria_obj")
    estado.pending_titulo       = analisis.get("titulo", texto[:50])
    estado.pending_descripcion  = texto
    estado.pending_severidad    = analisis.get("severidad", "media")
    estado.pending_categoria_id = categoria_obj.id if categoria_obj else None
    estado.pending_respuesta    = analisis.get("respuesta_usuario")
    estado.awaiting_modification = False
    estado.onboarding_step      = OnboardingStepEnum.PENDING_CONFIRMACION
    db.session.commit()

    summary = build_confirmation_summary(estado)
    send_and_store(phone, summary)
