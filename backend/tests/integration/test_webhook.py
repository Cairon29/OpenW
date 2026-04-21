"""
Characterization: HTTP webhook entry point.
Pins current behavior:
  - GET /webhook/whatsapp — verify challenge returns challenge text when token matches.
  - POST /webhook/whatsapp — HMAC SHA256 signature required when APP_SECRET set.
  - Invalid signature → 401.
  - Valid payload → 200 + dispatches to ChatService.procesar_mensaje_whatsapp.
  - Non-whatsapp_business_account payloads → 200 "ignored".
  - Status updates → delegate to ChatService.update_message_status.
"""
import hmac
import hashlib
import json

import pytest

from src.config import config as _config
from tests.conftest import CallRecorder


pytestmark = [pytest.mark.integration, pytest.mark.characterization]


APP_SECRET = _config.WHATSAPP_APP_SECRET
VERIFY_TOKEN = _config.WHATSAPP_VERIFY_TOKEN


def _sign(body: bytes) -> str:
    return "sha256=" + hmac.new(APP_SECRET.encode(), body, hashlib.sha256).hexdigest()


def _wa_text_payload(phone="5491100099999", text="hola", wamid="wamid.webhook.1",
                     profile="TestUser"):
    return {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "contacts": [{"profile": {"name": profile}, "wa_id": phone}],
                    "messages": [{
                        "from": phone,
                        "id": wamid,
                        "type": "text",
                        "text": {"body": text},
                    }],
                },
            }],
        }],
    }


def test_verify_challenge_returns_challenge_on_valid_token(client):
    resp = client.get(
        "/api/v1/chat/webhook/whatsapp",
        query_string={
            "hub.mode": "subscribe",
            "hub.verify_token": VERIFY_TOKEN,
            "hub.challenge": "12345",
        },
    )
    assert resp.status_code == 200
    assert resp.data.decode() == "12345"


def test_verify_challenge_rejects_invalid_token(client):
    resp = client.get(
        "/api/v1/chat/webhook/whatsapp",
        query_string={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong-token",
            "hub.challenge": "12345",
        },
    )
    assert resp.status_code == 403


def test_post_missing_signature_returns_401(client):
    body = json.dumps(_wa_text_payload()).encode()
    resp = client.post(
        "/api/v1/chat/webhook/whatsapp",
        data=body,
        content_type="application/json",
    )
    assert resp.status_code == 401


def test_post_invalid_signature_returns_401(client):
    body = json.dumps(_wa_text_payload()).encode()
    resp = client.post(
        "/api/v1/chat/webhook/whatsapp",
        data=body,
        content_type="application/json",
        headers={"X-Hub-Signature-256": "sha256=deadbeef"},
    )
    assert resp.status_code == 401


def test_post_valid_payload_dispatches_to_service(client, monkeypatch):
    recorder = CallRecorder(return_value=None)
    monkeypatch.setattr(
        "src.modules.chat.controller.ChatService.procesar_mensaje_whatsapp",
        recorder,
    )
    body = json.dumps(_wa_text_payload(
        phone="5491100088888", text="hola mundo", wamid="wamid.W.1", profile="Ana",
    )).encode()

    resp = client.post(
        "/api/v1/chat/webhook/whatsapp",
        data=body,
        content_type="application/json",
        headers={"X-Hub-Signature-256": _sign(body)},
    )

    assert resp.status_code == 200
    assert recorder.called
    call = recorder.last_call
    # procesar_mensaje_whatsapp(phone, texto, wa_message_id=, profile_name=)
    assert call["args"][0] == "5491100088888"
    assert call["args"][1] == "hola mundo"
    assert call["kwargs"]["wa_message_id"] == "wamid.W.1"
    assert call["kwargs"]["profile_name"] == "Ana"


def test_non_whatsapp_object_returns_ignored(client):
    body = json.dumps({"object": "unrelated"}).encode()
    resp = client.post(
        "/api/v1/chat/webhook/whatsapp",
        data=body,
        content_type="application/json",
        headers={"X-Hub-Signature-256": _sign(body)},
    )
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ignored"}


def test_status_update_dispatches_to_update_message_status(client, monkeypatch):
    recorder = CallRecorder(return_value=None)
    monkeypatch.setattr(
        "src.modules.chat.controller.ChatService.update_message_status",
        recorder,
    )
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "statuses": [{"id": "wamid.status.1", "status": "delivered"}],
                },
            }],
        }],
    }
    body = json.dumps(payload).encode()

    resp = client.post(
        "/api/v1/chat/webhook/whatsapp",
        data=body,
        content_type="application/json",
        headers={"X-Hub-Signature-256": _sign(body)},
    )

    assert resp.status_code == 200
    assert recorder.called
    assert recorder.last_call["args"] == ("wamid.status.1", "delivered")
