"""
Utilidad para envio de mensajes de texto via Meta WhatsApp Cloud API.
"""

import requests
from src.config import config


WHATSAPP_ACCESS_TOKEN = config.WHATSAPP_ACCESS_TOKEN
WHATSAPP_PHONE_NUMBER_ID = config.WHATSAPP_PHONE_NUMBER_ID


def enviar_whatsapp(phone, mensaje):
    """Envia un mensaje de texto via Meta WhatsApp Cloud API. Returns wamid or None."""
    if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print(f"[WhatsApp] Credenciales no configuradas. Mensaje para {phone}: {mensaje}")
        return None

    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": str(phone),
        "type": "text",
        "text": {"body": mensaje},
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        wamid = data.get("messages", [{}])[0].get("id")
        print(f"[WhatsApp] Mensaje enviado a {phone}: {wamid}")
        return wamid
    except Exception as e:
        print(f"[WhatsApp] Error enviando a {phone}: {e}")
        return None
