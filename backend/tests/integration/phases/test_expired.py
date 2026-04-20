"""
Characterization: EXPIRED phase (legacy/fallback state).
Pins current behavior:
  - Always resets to PENDING_EMAIL regardless of input.
  - Sends email prompt with corporate domain hint.
"""
import pytest

from src.modules.chat.utils.phases.expired import handle_expired
from src.db.models.enums import OnboardingStepEnum
from tests.factories import ConversationStateFactory
from tests.helpers import reload_state, bot_messages_for


pytestmark = [pytest.mark.integration, pytest.mark.characterization]


def test_expired_resets_to_pending_email(mock_whatsapp):
    state = ConversationStateFactory(
        onboarding_step=OnboardingStepEnum.EXPIRED,
    )

    handle_expired(state, state.phone, "cualquier cosa", False)

    fresh = reload_state(state.phone)
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_EMAIL
    texts = bot_messages_for(state.phone)
    assert any("email" in t.lower() for t in texts)
