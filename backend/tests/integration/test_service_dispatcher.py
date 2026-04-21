"""
Characterization: ChatService.procesar_mensaje_whatsapp (dispatcher).
Pins current behavior:
  - New phone → creates state in BIENVENIDA → handle_bienvenida runs → transitions to PENDING_EMAIL.
  - bot_active=False → persists user message + returns None without invoking handler.
  - profile_name propagates to ConversationState.wa_profile_name.
  - Typing indicator fires for active bot.
  - SSE publish receives bot_typing_start + bot_typing_stop events.
"""
import pytest

from src.modules.chat.service import ChatService
from src.db.models.enums import OnboardingStepEnum, RoleMensajeEnum
from src.db.models.conversation_state import ConversationState
from src.db.models.chat_message import ChatMessage
from tests.factories import ConversationStateFactory
from tests.helpers import reload_state, user_messages_for


pytestmark = [pytest.mark.integration, pytest.mark.characterization]


def test_new_phone_creates_state_and_runs_bienvenida(mock_whatsapp, mock_template):
    phone = "5491100099901"
    assert ConversationState.query.get(phone) is None

    ChatService.procesar_mensaje_whatsapp(phone, "hola", wa_message_id="wamid.1")

    fresh = ConversationState.query.get(phone)
    assert fresh is not None
    # handle_bienvenida transitioned to PENDING_EMAIL.
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_EMAIL
    assert mock_template.called


def test_bot_off_persists_user_message_and_returns_none(monkeypatch, mock_whatsapp):
    # Override the autouse bot-always-on fixture for this test.
    monkeypatch.setattr(
        "src.modules.chat.service._get_bot_state",
        lambda phone: False,
    )
    state = ConversationStateFactory(pending_email=True)

    result = ChatService.procesar_mensaje_whatsapp(state.phone, "user@test.local")

    assert result is None
    # Handler did NOT run: still in PENDING_EMAIL with no advance.
    fresh = reload_state(state.phone)
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_EMAIL
    # User message was stored.
    msgs = user_messages_for(state.phone)
    assert any("user@test.local" in m for m in msgs)


def test_profile_name_updates_state(mock_whatsapp, mock_template):
    phone = "5491100099902"
    ChatService.procesar_mensaje_whatsapp(
        phone, "hola", wa_message_id="wamid.2", profile_name="Juan Pérez",
    )

    fresh = ConversationState.query.get(phone)
    assert fresh.wa_profile_name == "Juan Pérez"


def test_typing_indicator_fires_when_bot_active(mock_whatsapp, mock_template, capture_events):
    state = ConversationStateFactory(pending_email=True)

    ChatService.procesar_mensaje_whatsapp(state.phone, "hola", wa_message_id="wamid.3")

    # Typing indicator: WhatsApp API called + SSE events published.
    assert mock_whatsapp.typing.called
    event_types = [c["args"][0].get("type") for c in capture_events.calls]
    assert "bot_typing_start" in event_types
    assert "bot_typing_stop" in event_types


def test_user_message_persisted_with_wa_message_id(mock_whatsapp, mock_template):
    state = ConversationStateFactory(pending_email=True)

    ChatService.procesar_mensaje_whatsapp(
        state.phone, "mi texto exacto", wa_message_id="wamid.unique.42",
    )

    msg = ChatMessage.query.filter_by(
        phone=state.phone, role=RoleMensajeEnum.USER, text="mi texto exacto",
    ).first()
    assert msg is not None
    assert msg.wa_message_id == "wamid.unique.42"
