"""
Characterization: PENDING_VICEPRESIDENCIA phase.
Pins current behavior:
  - Numeric selection 1..N → sets fk_id_vicepresidencia, transitions to PENDING_DIRECCION.
  - Invalid number → IA fallback; if IA fails, stays in same phase.
  - No VPs in DB → skips to PENDING_NOVEDAD.
  - Chosen VP with no directions → skips to PENDING_NOVEDAD.
"""
import pytest

from src.modules.chat.utils.phases.pending_vicepresidencia import handle_pending_vicepresidencia
from src.db.models.enums import OnboardingStepEnum
from tests.factories import (
    ConversationStateFactory, VicepresidenciaFactory, DireccionFactory,
)
from tests.helpers import reload_state


pytestmark = [pytest.mark.integration, pytest.mark.characterization]


def test_valid_selection_sets_vp_and_advances_to_direccion(mock_whatsapp, mock_ai_validate):
    vp1 = VicepresidenciaFactory()
    DireccionFactory(vicepresidencia=vp1)  # ensure direccion menu renders
    state = ConversationStateFactory(pending_vicepresidencia=True)

    handle_pending_vicepresidencia(state, state.phone, "1", False)

    fresh = reload_state(state.phone)
    assert fresh.fk_id_vicepresidencia == vp1.id
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_DIRECCION


def test_no_vps_skips_to_pending_novedad(mock_whatsapp, mock_ai_validate):
    state = ConversationStateFactory(pending_vicepresidencia=True)

    handle_pending_vicepresidencia(state, state.phone, "1", False)

    assert reload_state(state.phone).onboarding_step == OnboardingStepEnum.PENDING_NOVEDAD


def test_selected_vp_without_directions_skips_to_novedad(mock_whatsapp, mock_ai_validate):
    vp = VicepresidenciaFactory()  # no directions
    state = ConversationStateFactory(pending_vicepresidencia=True)

    handle_pending_vicepresidencia(state, state.phone, "1", False)

    fresh = reload_state(state.phone)
    assert fresh.fk_id_vicepresidencia == vp.id
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_NOVEDAD


def test_out_of_range_falls_back_to_ai_and_stays(mock_whatsapp, mock_ai_validate):
    VicepresidenciaFactory()  # id 1 only
    state = ConversationStateFactory(pending_vicepresidencia=True)

    handle_pending_vicepresidencia(state, state.phone, "99", False)

    assert mock_ai_validate.called
    assert reload_state(state.phone).onboarding_step == OnboardingStepEnum.PENDING_VICEPRESIDENCIA


def test_ai_rescued_selection_advances(mock_whatsapp, mock_ai_validate):
    vp1 = VicepresidenciaFactory()
    DireccionFactory(vicepresidencia=vp1)
    mock_ai_validate.return_value = {
        "is_valid": True,
        "extracted_value": "1",
        "guidance_message": None,
    }
    state = ConversationStateFactory(pending_vicepresidencia=True)

    handle_pending_vicepresidencia(state, state.phone, "la primera", False)

    fresh = reload_state(state.phone)
    assert fresh.fk_id_vicepresidencia == vp1.id
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_DIRECCION
