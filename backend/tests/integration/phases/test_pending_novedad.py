"""
Characterization: PENDING_NOVEDAD phase.
Pins current behavior:
  - Runs classify_message(), copies result into pending_* fields, transitions to PENDING_CONFIRMACION.
  - Stores original user text as pending_descripcion.
  - Title falls back to first 50 chars if classifier omits it.
"""
import pytest

from src.modules.chat.utils.phases.pending_novedad import handle_pending_novedad
from src.db.models.enums import OnboardingStepEnum
from tests.factories import ConversationStateFactory, CategoriaNovedadFactory
from tests.helpers import reload_state


pytestmark = [pytest.mark.integration, pytest.mark.characterization]


def test_novedad_saves_classification_and_advances(mock_whatsapp, mock_classify):
    cat = CategoriaNovedadFactory(categoria="Phishing")
    mock_classify.return_value = {
        "titulo": "Phishing detectado",
        "severidad": "alta",
        "categoria_obj": cat,
        "respuesta_usuario": "Gracias, registramos el phishing.",
    }
    state = ConversationStateFactory(pending_novedad=True)
    phone = state.phone
    texto = "Me llegó un email raro pidiéndome la contraseña"

    handle_pending_novedad(state, phone, texto, False)

    fresh = reload_state(phone)
    assert fresh.onboarding_step == OnboardingStepEnum.PENDING_CONFIRMACION
    assert fresh.pending_titulo == "Phishing detectado"
    assert fresh.pending_severidad == "alta"
    assert fresh.pending_categoria_id == cat.id
    assert fresh.pending_descripcion == texto
    assert fresh.pending_respuesta == "Gracias, registramos el phishing."
    assert fresh.awaiting_modification is False


def test_novedad_sends_confirmation_summary(mock_whatsapp, mock_classify):
    state = ConversationStateFactory(pending_novedad=True)

    handle_pending_novedad(state, state.phone, "descripcion cualquiera", False)

    # mock_whatsapp.send is called with the summary text.
    assert mock_whatsapp.send.called
    summary_text = mock_whatsapp.send.last_call["args"][1]
    assert "Resumen" in summary_text or "resumen" in summary_text


def test_classify_without_title_key_uses_first_50_chars(mock_whatsapp, mock_classify):
    # Classifier omits the `titulo` key entirely → fallback to texto[:50].
    # Note: current code uses dict.get("titulo", texto[:50]); if classifier
    # returns {"titulo": None} explicitly, pending_titulo becomes None (bug-ish).
    mock_classify.return_value = {
        "severidad": "media",
        "categoria_obj": None,
        "respuesta_usuario": "Recibido.",
    }
    long_text = "a" * 100
    state = ConversationStateFactory(pending_novedad=True)

    handle_pending_novedad(state, state.phone, long_text, False)

    fresh = reload_state(state.phone)
    assert fresh.pending_titulo == long_text[:50]


def test_classify_with_no_category_leaves_id_null(mock_whatsapp, mock_classify):
    mock_classify.return_value = {
        "titulo": "Sin categoria",
        "severidad": "media",
        "categoria_obj": None,
        "respuesta_usuario": "Recibido.",
    }
    state = ConversationStateFactory(pending_novedad=True)

    handle_pending_novedad(state, state.phone, "mensaje sin match", False)

    assert reload_state(state.phone).pending_categoria_id is None
