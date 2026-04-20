"""
Smoke test: validates the test harness itself.
If this passes, conftest + factories + mocks work end-to-end.
"""
import pytest

from src.modules.chat.service import ChatService
from src.db.models.enums import OnboardingStepEnum
from tests.helpers import reload_state, bot_messages_for


pytestmark = [pytest.mark.integration, pytest.mark.characterization]


def test_new_phone_triggers_bienvenida(mock_whatsapp, mock_template, mock_email):
    phone = "5491123456789"

    ChatService.procesar_mensaje_whatsapp(phone, "hola")

    state = reload_state(phone)
    assert state is not None
    assert state.onboarding_step == OnboardingStepEnum.PENDING_EMAIL
    assert mock_template.called, "Expected bienvenida template to be sent"
    # At least one text message (email prompt) should have been sent
    assert mock_whatsapp.send.called
    bot_texts = bot_messages_for(phone)
    assert any("email" in t.lower() for t in bot_texts)
