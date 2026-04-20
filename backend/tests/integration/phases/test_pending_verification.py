"""
Characterization: PENDING_VERIFICATION phase.
Pins current behavior:
  - Within timeout: tell user email is still pending; stays in same step.
  - After timeout: reverts to PENDING_EMAIL, clears token.
"""
from datetime import datetime, timezone, timedelta

import pytest

from src.modules.chat.utils.phases.pending_verification import handle_pending_verification
from src.db.models.enums import OnboardingStepEnum
from tests.factories import ConversationStateFactory
from tests.helpers import reload_state, bot_messages_for


pytestmark = [pytest.mark.integration, pytest.mark.characterization]


def test_within_timeout_keeps_state_and_notifies(mock_whatsapp):
    state = ConversationStateFactory(
        pending_verification=True,
        verification_sent_at=datetime.now(timezone.utc) - timedelta(seconds=30),
    )

    handle_pending_verification(state, state.phone, "cualquier mensaje", False)

    fresh = reload_state(state.phone)
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_VERIFICATION
    assert fresh.verification_token == "token-fixture"
    texts = bot_messages_for(state.phone)
    assert any("verificaste" in t.lower() or "bandeja" in t.lower() for t in texts)


def test_after_timeout_reverts_to_pending_email(mock_whatsapp):
    state = ConversationStateFactory(
        pending_verification=True,
        verification_sent_at=datetime.now(timezone.utc) - timedelta(minutes=10),
    )

    handle_pending_verification(state, state.phone, "cualquier", False)

    fresh = reload_state(state.phone)
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_EMAIL
    assert fresh.verification_token is None
    texts = bot_messages_for(state.phone)
    assert any("venció" in t.lower() or "vencio" in t.lower() for t in texts)
