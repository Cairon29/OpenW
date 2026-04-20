"""
Characterization: PENDING_EMAIL phase.
Pins current behavior:
  - Valid email → generates token, calls email sender, transitions to PENDING_VERIFICATION.
  - Invalid email format → IA fallback; if IA fails too, stays in PENDING_EMAIL.
  - Email send failure → reverts to PENDING_EMAIL.
"""
import pytest

from src.modules.chat.utils.phases.pending_email import handle_pending_email
from src.db.models.enums import OnboardingStepEnum
from tests.factories import ConversationStateFactory
from tests.helpers import reload_state, bot_messages_for


pytestmark = [pytest.mark.integration, pytest.mark.characterization]


def test_valid_email_advances_to_pending_verification(mock_whatsapp, mock_email):
    state = ConversationStateFactory(pending_email=True)
    phone = state.phone

    handle_pending_email(state, phone, "juan.perez@test.local", False)

    fresh = reload_state(phone)
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_VERIFICATION
    assert fresh.email == "juan.perez@test.local"
    assert fresh.verification_token is not None
    assert fresh.verification_sent_at is not None
    assert mock_email.called
    assert mock_email.last_call["args"][0] == "juan.perez@test.local"


def test_valid_email_sends_confirmation_to_user(mock_whatsapp, mock_email):
    state = ConversationStateFactory(pending_email=True)

    handle_pending_email(state, state.phone, "ana@test.local", False)

    texts = bot_messages_for(state.phone)
    assert any("ana@test.local" in t for t in texts)


def test_invalid_format_falls_back_to_ai_and_stays(mock_whatsapp, mock_ai_validate):
    state = ConversationStateFactory(pending_email=True)
    phone = state.phone

    handle_pending_email(state, phone, "not-an-email", False)

    assert mock_ai_validate.called
    assert reload_state(phone).onboarding_step == OnboardingStepEnum.PENDING_EMAIL


def test_invalid_domain_falls_back_to_ai_and_stays(mock_whatsapp, mock_ai_validate):
    state = ConversationStateFactory(pending_email=True)
    phone = state.phone

    handle_pending_email(state, phone, "user@wrongdomain.com", False)

    assert mock_ai_validate.called
    assert reload_state(phone).onboarding_step == OnboardingStepEnum.PENDING_EMAIL


def test_ai_rescued_email_transitions(mock_whatsapp, mock_email, mock_ai_validate):
    # IA extracts a valid domain email from messy input → treated as valid.
    mock_ai_validate.return_value = {
        "is_valid": True,
        "extracted_value": "laura@test.local",
        "guidance_message": None,
    }
    state = ConversationStateFactory(pending_email=True)

    handle_pending_email(state, state.phone, "mi mail es laura arroba test.local", False)

    fresh = reload_state(state.phone)
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_VERIFICATION
    assert fresh.email == "laura@test.local"


def test_email_send_failure_reverts_to_pending_email(mock_whatsapp, mock_email):
    mock_email.return_value = False  # SMTP failed
    state = ConversationStateFactory(pending_email=True)
    phone = state.phone

    handle_pending_email(state, phone, "pablo@test.local", False)

    fresh = reload_state(phone)
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_EMAIL
    assert fresh.verification_token is None
    assert fresh.verification_sent_at is None
