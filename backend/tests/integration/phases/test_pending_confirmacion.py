"""
Characterization: PENDING_CONFIRMACION phase.
This handler has the highest complexity:
  - Main flow: "1/sí" → create Novedad → COMPLETED. "2/no" → awaiting_modification.
  - Modification sub-flow: "1" → re-pick VP, "2" → re-pick Direccion, "3" → re-describe.
  - Unknown input → IA fallback with recursion.

These tests PIN the recursive behavior intentionally — State pattern refactor
will remove the recursion but MUST preserve the observable outcomes.
"""
import pytest

from src.modules.chat.utils.phases.pending_confirmacion import handle_pending_confirmacion
from src.db.models.enums import OnboardingStepEnum, SeveridadEnum, EstadoEnum
from src.db.models.novedad import Novedad
from tests.factories import (
    ConversationStateFactory, VicepresidenciaFactory, DireccionFactory,
    CategoriaNovedadFactory,
)
from tests.helpers import reload_state


pytestmark = [pytest.mark.integration, pytest.mark.characterization]


# ── Main flow: confirm ────────────────────────────────────────────────────

@pytest.mark.parametrize("user_input", ["1", "si", "sí", "confirmar", "si, confirmar"])
def test_confirm_creates_novedad_and_advances_to_completed(
    mock_whatsapp, mock_ai_validate, user_input,
):
    vp = VicepresidenciaFactory()
    direccion = DireccionFactory(vicepresidencia=vp)
    cat = CategoriaNovedadFactory()
    state = ConversationStateFactory(
        pending_confirmacion=True,
        fk_id_vicepresidencia=vp.id,
        fk_id_direccion=direccion.id,
        pending_categoria_id=cat.id,
    )

    handle_pending_confirmacion(state, state.phone, user_input, False)

    fresh = reload_state(state.phone)
    assert fresh.onboarding_step == OnboardingStepEnum.COMPLETED
    # pending_* fields cleared after creation
    assert fresh.pending_titulo is None
    assert fresh.pending_descripcion is None
    assert fresh.pending_severidad is None
    assert fresh.pending_categoria_id is None
    # Novedad row created with expected linkage
    novedades = Novedad.query.filter_by(fk_id_direccion=direccion.id).all()
    assert len(novedades) == 1
    nov = novedades[0]
    assert nov.titulo == "Phishing recibido"
    assert nov.severidad == SeveridadEnum.ALTA
    assert nov.estado == EstadoEnum.ABIERTA
    assert nov.fk_id_categoria == cat.id


# ── Main flow: modify ─────────────────────────────────────────────────────

@pytest.mark.parametrize("user_input", ["2", "modificar", "no"])
def test_modify_enters_awaiting_modification(mock_whatsapp, mock_ai_validate, user_input):
    state = ConversationStateFactory(pending_confirmacion=True)

    handle_pending_confirmacion(state, state.phone, user_input, False)

    fresh = reload_state(state.phone)
    assert fresh.awaiting_modification is True
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_CONFIRMACION


# ── Modification sub-flow ────────────────────────────────────────────────

def test_modification_option_1_goes_back_to_vicepresidencia(mock_whatsapp, mock_ai_validate):
    VicepresidenciaFactory()
    state = ConversationStateFactory(
        pending_confirmacion=True, awaiting_modification=True,
    )

    handle_pending_confirmacion(state, state.phone, "1", False)

    fresh = reload_state(state.phone)
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_VICEPRESIDENCIA
    assert fresh.fk_id_vicepresidencia is None
    assert fresh.fk_id_direccion is None
    assert fresh.awaiting_modification is False


def test_modification_option_2_goes_back_to_direccion(mock_whatsapp, mock_ai_validate):
    vp = VicepresidenciaFactory()
    DireccionFactory(vicepresidencia=vp)
    state = ConversationStateFactory(
        pending_confirmacion=True, awaiting_modification=True,
        fk_id_vicepresidencia=vp.id,
    )

    handle_pending_confirmacion(state, state.phone, "2", False)

    fresh = reload_state(state.phone)
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_DIRECCION
    assert fresh.fk_id_direccion is None
    assert fresh.fk_id_vicepresidencia == vp.id  # preserved


def test_modification_option_3_goes_back_to_novedad(mock_whatsapp, mock_ai_validate):
    state = ConversationStateFactory(
        pending_confirmacion=True, awaiting_modification=True,
    )

    handle_pending_confirmacion(state, state.phone, "3", False)

    fresh = reload_state(state.phone)
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_NOVEDAD
    assert fresh.pending_titulo is None
    assert fresh.pending_descripcion is None
    assert fresh.awaiting_modification is False


def test_ai_rescued_input_triggers_recursion_into_same_handler(
    mock_whatsapp, mock_ai_validate,
):
    # Characterization pins the recursive fallback path currently in prod.
    VicepresidenciaFactory()
    mock_ai_validate.return_value = {
        "is_valid": True,
        "extracted_value": "1",
        "guidance_message": None,
    }
    state = ConversationStateFactory(
        pending_confirmacion=True, awaiting_modification=True,
    )

    handle_pending_confirmacion(state, state.phone, "la primera", False)

    fresh = reload_state(state.phone)
    # Recursion delegated to "1" branch → go back to VICEPRESIDENCIA
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_VICEPRESIDENCIA
