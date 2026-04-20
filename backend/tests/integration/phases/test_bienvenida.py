"""
Characterization: BIENVENIDA phase.
Pins current behavior: sends welcome template + email prompt, transitions to PENDING_EMAIL.
"""
import pytest

from src.modules.chat.utils.phases.bienvenida import handle_bienvenida
from src.db.models.enums import OnboardingStepEnum
from tests.factories import ConversationStateFactory
from tests.helpers import reload_state, bot_messages_for


pytestmark = [pytest.mark.integration, pytest.mark.characterization]


def test_bienvenida_transitions_to_pending_email(mock_whatsapp, mock_template):
    state = ConversationStateFactory(onboarding_step=OnboardingStepEnum.BIENVENIDA)
    phone = state.phone

    handle_bienvenida(state, phone, "hola", True)

    assert reload_state(phone).onboarding_step == OnboardingStepEnum.PENDING_EMAIL


def test_bienvenida_sends_welcome_template(mock_whatsapp, mock_template):
    state = ConversationStateFactory(onboarding_step=OnboardingStepEnum.BIENVENIDA)

    handle_bienvenida(state, state.phone, "hola", True)

    assert mock_template.call_count == 1
    assert mock_template.last_call["args"][1] == "mensaje_bienvenida"


def test_bienvenida_sends_email_prompt_and_persists_bot_message(mock_whatsapp, mock_template):
    state = ConversationStateFactory(onboarding_step=OnboardingStepEnum.BIENVENIDA)
    phone = state.phone

    handle_bienvenida(state, phone, "hola", True)

    bot_texts = bot_messages_for(phone)
    assert len(bot_texts) == 1
    assert "email" in bot_texts[0].lower()
    assert mock_whatsapp.send.call_count == 1
