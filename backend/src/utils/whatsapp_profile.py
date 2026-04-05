"""
Fetch WhatsApp user profile photo via Meta Cloud API.
Requires whatsapp_business_management permission.
"""

import requests
from src.config import config

WHATSAPP_ACCESS_TOKEN = config.WHATSAPP_ACCESS_TOKEN
WHATSAPP_PHONE_NUMBER_ID = config.WHATSAPP_PHONE_NUMBER_ID

# Re-fetch photo if older than 23 hours
PHOTO_TTL_SECONDS = 23 * 60 * 60


def fetch_profile_photo_url(wa_id: str) -> str | None:
    """Fetch profile photo URL for a WhatsApp user. Returns URL string or None."""
    if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        return None

    url = (
        f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}"
        f"/contacts/{wa_id}/profile_photo"
    )
    headers = {"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        print(f"[WhatsApp Profile] Fetched photo URL for {wa_id}: {data}")
        return data.get("data", {}).get("url") or data.get("url")
    except Exception as e:
        print(f"[WhatsApp Profile] Error fetching photo for {wa_id}: {e}")
        return None
