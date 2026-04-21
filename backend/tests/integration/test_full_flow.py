"""
Characterization: golden path E2E.
New phone → BIENVENIDA → PENDING_EMAIL → PENDING_VERIFICATION → verify token →
PENDING_VICEPRESIDENCIA → PENDING_DIRECCION → PENDING_NOVEDAD →
PENDING_CONFIRMACION → COMPLETED + Novedad persisted.

Pins the full state machine end-to-end as it currently behaves.
"""
import pytest

from src.modules.chat.service import ChatService
from src.modules.auth.service import AuthService
from src.db.models.enums import OnboardingStepEnum, EstadoEnum, SeveridadEnum
from src.db.models.conversation_state import ConversationState
from src.db.models.novedad import Novedad
from tests.factories import VicepresidenciaFactory, DireccionFactory, CategoriaNovedadFactory
from tests.helpers import reload_state


pytestmark = [pytest.mark.integration, pytest.mark.characterization]


def test_golden_path_creates_novedad(
    mock_whatsapp, mock_template, mock_classify, mock_ai_validate, mock_email,
):
    vp = VicepresidenciaFactory(nombre="VP Ciber")
    direccion = DireccionFactory(vicepresidencia=vp, nombre="Dirección IT")
    cat = CategoriaNovedadFactory(categoria="Phishing")

    mock_classify.return_value = {
        "titulo": "Phishing reportado",
        "severidad": "alta",
        "categoria_obj": cat,
        "respuesta_usuario": "Gracias por el reporte.",
    }

    phone = "5491100077777"

    # 1. BIENVENIDA → PENDING_EMAIL
    ChatService.procesar_mensaje_whatsapp(phone, "hola", wa_message_id="w.1")
    assert reload_state(phone).onboarding_step == OnboardingStepEnum.PENDING_EMAIL

    # 2. PENDING_EMAIL → PENDING_VERIFICATION (mock_email returns True)
    ChatService.procesar_mensaje_whatsapp(phone, "user@test.local", wa_message_id="w.2")
    state = reload_state(phone)
    assert state.onboarding_step == OnboardingStepEnum.PENDING_VERIFICATION
    token = state.verification_token
    assert token

    # 3. Verify email token → PENDING_VICEPRESIDENCIA
    AuthService.verify_email(token)
    assert reload_state(phone).onboarding_step == OnboardingStepEnum.PENDING_VICEPRESIDENCIA

    # 4. User sends any text → VP menu already displayed; pick "1"
    ChatService.procesar_mensaje_whatsapp(phone, "1", wa_message_id="w.3")
    state = reload_state(phone)
    assert state.onboarding_step == OnboardingStepEnum.PENDING_DIRECCION
    assert state.fk_id_vicepresidencia == vp.id

    # 5. PENDING_DIRECCION → PENDING_NOVEDAD
    ChatService.procesar_mensaje_whatsapp(phone, "1", wa_message_id="w.4")
    state = reload_state(phone)
    assert state.onboarding_step == OnboardingStepEnum.PENDING_NOVEDAD
    assert state.fk_id_direccion == direccion.id

    # 6. PENDING_NOVEDAD → PENDING_CONFIRMACION (classifier mocked)
    ChatService.procesar_mensaje_whatsapp(
        phone, "Me llegó un email raro pidiendo contraseña", wa_message_id="w.5",
    )
    state = reload_state(phone)
    assert state.onboarding_step == OnboardingStepEnum.PENDING_CONFIRMACION
    assert state.pending_titulo == "Phishing reportado"

    # 7. PENDING_CONFIRMACION "1" → COMPLETED + Novedad row
    ChatService.procesar_mensaje_whatsapp(phone, "1", wa_message_id="w.6")
    state = reload_state(phone)
    assert state.onboarding_step == OnboardingStepEnum.COMPLETED

    novedades = Novedad.query.filter_by(fk_id_direccion=direccion.id).all()
    assert len(novedades) == 1
    nov = novedades[0]
    assert nov.titulo == "Phishing reportado"
    assert nov.severidad == SeveridadEnum.ALTA
    assert nov.estado == EstadoEnum.ABIERTA
    assert nov.fk_id_categoria == cat.id

    # Pending_* cleared.
    assert state.pending_titulo is None
    assert state.pending_descripcion is None
    assert state.pending_categoria_id is None
