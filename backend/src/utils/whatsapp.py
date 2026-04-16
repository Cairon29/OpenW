"""
Utilidad para envio de mensajes de texto via Meta WhatsApp Cloud API.
"""

import os
import requests


def enviar_whatsapp(phone, mensaje):
    """Envia un mensaje de texto via Meta WhatsApp Cloud API. Returns wamid or None."""
    token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    if not token or not phone_id:
        print(f"[WhatsApp] Credenciales no configuradas. Mensaje para {phone}: {mensaje}")
        return None

    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
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


def enviar_indicador_typing(wa_message_id: str) -> None:
    """Mark a received message as read AND show typing bubble on user's WhatsApp.

    Uses the combined read-receipt + typing_indicator endpoint. The bubble
    auto-clears when the bot's next outbound message is delivered (or after
    ~25s, per Meta docs).
    """
    if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID or not wa_message_id:
        return
    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": wa_message_id,
        "typing_indicator": {"type": "text"},
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"[WhatsApp] typing indicator error: {e}")
