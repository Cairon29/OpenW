"""
Characterization: PENDING_DIRECCION phase.
Pins current behavior:
  - Numeric selection 1..N (filtered by fk_id_vicepresidencia) → sets fk_id_direccion, advances to PENDING_NOVEDAD.
  - No directions under chosen VP → skips to PENDING_NOVEDAD without touching fk_id_direccion.
  - Invalid number → IA fallback; if IA fails, stays in same phase.
  - IA rescues numeric string → advances.
"""
import pytest

from src.modules.chat.utils.phases.pending_direccion import handle_pending_direccion
from src.db.models.enums import OnboardingStepEnum
from tests.factories import (
    ConversationStateFactory, VicepresidenciaFactory, DireccionFactory,
)
from tests.helpers import reload_state


pytestmark = [pytest.mark.integration, pytest.mark.characterization]


def test_valid_selection_sets_direccion_and_advances(mock_whatsapp, mock_ai_validate):
    vp = VicepresidenciaFactory()
    d1 = DireccionFactory(vicepresidencia=vp)
    DireccionFactory(vicepresidencia=vp)
    state = ConversationStateFactory(
        pending_direccion=True, fk_id_vicepresidencia=vp.id,
    )

    handle_pending_direccion(state, state.phone, "1", False)

    fresh = reload_state(state.phone)
    assert fresh.fk_id_direccion == d1.id
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_NOVEDAD


def test_no_directions_skips_to_pending_novedad(mock_whatsapp, mock_ai_validate):
    vp = VicepresidenciaFactory()  # VP without directions
    state = ConversationStateFactory(
        pending_direccion=True, fk_id_vicepresidencia=vp.id,
    )

    handle_pending_direccion(state, state.phone, "1", False)

    fresh = reload_state(state.phone)
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_NOVEDAD
    assert fresh.fk_id_direccion is None


def test_out_of_range_falls_back_to_ai_and_stays(mock_whatsapp, mock_ai_validate):
    vp = VicepresidenciaFactory()
    DireccionFactory(vicepresidencia=vp)  # only id=1 exists
    state = ConversationStateFactory(
        pending_direccion=True, fk_id_vicepresidencia=vp.id,
    )

    handle_pending_direccion(state, state.phone, "99", False)

    assert mock_ai_validate.called
    assert reload_state(state.phone).onboarding_step == OnboardingStepEnum.PENDING_DIRECCION


def test_ai_rescued_selection_advances(mock_whatsapp, mock_ai_validate):
    vp = VicepresidenciaFactory()
    d1 = DireccionFactory(vicepresidencia=vp)
    mock_ai_validate.return_value = {
        "is_valid": True,
        "extracted_value": "1",
        "guidance_message": None,
    }
    state = ConversationStateFactory(
        pending_direccion=True, fk_id_vicepresidencia=vp.id,
    )

    handle_pending_direccion(state, state.phone, "la primera", False)

    fresh = reload_state(state.phone)
    assert fresh.fk_id_direccion == d1.id
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_NOVEDAD
