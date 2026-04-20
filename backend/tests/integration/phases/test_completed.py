"""
Characterization: COMPLETED phase.
Pins current behavior:
  - "sí/otra" → reset to PENDING_NOVEDAD, sends prompt.
  - "no/gracias" → farewell message, stays in COMPLETED.
  - Anything else → treat as new novedad: moves to PENDING_NOVEDAD and delegates to handle_pending_novedad.
"""
import pytest

from src.modules.chat.utils.phases.completed import handle_completed
from src.db.models.enums import OnboardingStepEnum
from tests.factories import ConversationStateFactory
from tests.helpers import reload_state, bot_messages_for


pytestmark = [pytest.mark.integration, pytest.mark.characterization]


@pytest.mark.parametrize("user_input", ["si", "sí", "otra", "si, otra"])
def test_affirmative_resets_to_pending_novedad(mock_whatsapp, user_input):
    state = ConversationStateFactory(completed=True)

    handle_completed(state, state.phone, user_input, False)

    fresh = reload_state(state.phone)
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_NOVEDAD
    texts = bot_messages_for(state.phone)
    assert any("describí" in t.lower() or "describi" in t.lower() for t in texts)


@pytest.mark.parametrize("user_input", ["no", "no, gracias", "chau", "gracias"])
def test_negative_stays_completed_with_farewell(mock_whatsapp, user_input):
    state = ConversationStateFactory(completed=True)

    handle_completed(state, state.phone, user_input, False)

    fresh = reload_state(state.phone)
    assert fresh.onboarding_step == OnboardingStepEnum.COMPLETED
    texts = bot_messages_for(state.phone)
    assert any("gracias" in t.lower() for t in texts)


def test_unknown_input_treated_as_new_novedad(mock_whatsapp, mock_classify):
    # Falls through to handle_pending_novedad → classifier runs + transitions to PENDING_CONFIRMACION.
    mock_classify.return_value = {
        "titulo": "Incidente",
        "severidad": "media",
        "categoria_obj": None,
        "respuesta_usuario": "Recibido.",
    }
    state = ConversationStateFactory(completed=True)

    handle_completed(state, state.phone, "me llegó otro phishing", False)

    fresh = reload_state(state.phone)
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_CONFIRMACION
    assert fresh.pending_titulo == "Incidente"
