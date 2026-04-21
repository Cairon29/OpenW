"""
Helpers compartidos por todos los phase handlers.
"""

import requests
from src.db.models import Novedad, SeveridadEnum, EstadoEnum
from src.db.models.enums import OnboardingStepEnum, RoleMensajeEnum
from src.extensions import db
from src.utils.whatsapp import enviar_whatsapp
from src.utils.messages import store_message
from src.config import config
from datetime import datetime, timezone


WHATSAPP_ACCESS_TOKEN = config.WHATSAPP_ACCESS_TOKEN
WHATSAPP_PHONE_NUMBER_ID = config.WHATSAPP_PHONE_NUMBER_ID

SEVERIDAD_MAP = {
    "critica": SeveridadEnum.CRITICA,
    "alta": SeveridadEnum.ALTA,
    "media": SeveridadEnum.MEDIA,
    "baja": SeveridadEnum.BAJA,
    "informativa": SeveridadEnum.INFO,
}


def send_and_store(phone, respuesta):
    """Envía un mensaje por WhatsApp y lo almacena en la DB."""
    wamid = enviar_whatsapp(phone, respuesta)
    store_message(phone, RoleMensajeEnum.BOT, respuesta, wa_message_id=wamid)
    return wamid


def enviar_template_whatsapp(phone, template_name, lang_code="es_CO"):
    """Envia una plantilla de WhatsApp via Meta Cloud API."""
    if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print(f"[WhatsApp] Credenciales no configuradas. Template '{template_name}' para {phone}")
        return None

    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": str(phone),
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": lang_code},
        },
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        wamid = data.get("messages", [{}])[0].get("id")
        print(f"[WhatsApp] Template '{template_name}' enviado a {phone}: {wamid}")
        return wamid
    except Exception as e:
        print(f"[WhatsApp] Error enviando template a {phone}: {e}")
        return None


def create_novedad_from_state(estado, phone):
    """Crea la Novedad con los datos almacenados en ConversationState."""
    from src.db.models import Usuarios

    user_email = estado.email
    if user_email:
        user = Usuarios.query.filter_by(email=user_email).first()
        if not user:
            user = Usuarios(
                email=user_email,
                phone=str(phone) if phone else None,
                name=estado.wa_profile_name or f"Usuario_{phone}",
                fk_id_vicepresidencia=estado.fk_id_vicepresidencia,
                fk_id_direccion=estado.fk_id_direccion,
            )
            db.session.add(user)
            db.session.flush()
        else:
            phone_str = str(phone) if phone else None
            if estado.wa_profile_name and estado.wa_profile_name != user.name:
                user.name = estado.wa_profile_name
            if phone_str and phone_str != user.phone:
                user.phone = phone_str
            if estado.fk_id_vicepresidencia and estado.fk_id_vicepresidencia != user.fk_id_vicepresidencia:
                user.fk_id_vicepresidencia = estado.fk_id_vicepresidencia
            if estado.fk_id_direccion and estado.fk_id_direccion != user.fk_id_direccion:
                user.fk_id_direccion = estado.fk_id_direccion
            db.session.flush()

    nueva_novedad = Novedad(
        titulo=estado.pending_titulo,
        descripcion=estado.pending_descripcion,
        fk_email_usuario=user_email,
        fk_id_direccion=estado.fk_id_direccion,
        fk_id_categoria=estado.pending_categoria_id,
        severidad=SEVERIDAD_MAP.get(estado.pending_severidad, SeveridadEnum.MEDIA),
        estado=EstadoEnum.ABIERTA,
        fecha_registro=datetime.now(timezone.utc),
    )

    try:
        db.session.add(nueva_novedad)

        estado.pending_titulo = None
        estado.pending_descripcion = None
        estado.pending_severidad = None
        estado.pending_categoria_id = None
        estado.pending_respuesta = None
        estado.awaiting_modification = False
        estado.onboarding_step = OnboardingStepEnum.COMPLETED
        db.session.commit()

        respuesta = (
            "✅ *Tu novedad fue registrada exitosamente.*\n\n"
            "¿Querés reportar otra novedad?\n\n"
            "*Sí* — para reportar otra\n"
            "*No* — para finalizar"
        )
        send_and_store(phone, respuesta)
        return nueva_novedad
    except Exception as e:
        db.session.rollback()
        print(f"Error guardando novedad: {e}")
        send_and_store(
            phone,
            "Ocurrió un error al guardar tu reporte. Por favor, intentá de nuevo."
        )
        return None
