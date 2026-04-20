"""
factory-boy factories for all models touched by the chat flow.
Each factory uses `db.session` directly (not SQLAlchemyModelFactory's session param)
because we want to share the Flask-SQLAlchemy scoped session from conftest.
"""
from datetime import datetime, timezone, timedelta

import factory
from factory.alchemy import SQLAlchemyModelFactory

from src.extensions import db
from src.db.models.usuarios import Usuarios
from src.db.models.vicepresidencia import Vicepresidencia
from src.db.models.direccion import Direccion
from src.db.models.categoria_novedad import CategoriaNovedad
from src.db.models.novedad import Novedad
from src.db.models.chat_message import ChatMessage
from src.db.models.conversation_state import ConversationState
from src.db.models.enums import (
    OnboardingStepEnum, RoleMensajeEnum, SeveridadEnum, EstadoEnum,
)


class _Base(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"


class VicepresidenciaFactory(_Base):
    class Meta:
        model = Vicepresidencia

    nombre = factory.Sequence(lambda n: f"VP {n}")
    descripcion = "Vicepresidencia de prueba"


class DireccionFactory(_Base):
    class Meta:
        model = Direccion
        # Exclude pseudo-field used to auto-link to a parent VP factory.
        exclude = ("vicepresidencia",)

    nombre = factory.Sequence(lambda n: f"Dirección {n}")
    descripcion = "Dirección de prueba"
    # Helper: pass `vicepresidencia=vp` and we derive fk_id automatically.
    vicepresidencia = None
    fk_id_vicepresidencia = factory.LazyAttribute(
        lambda o: o.vicepresidencia.id if o.vicepresidencia else None
    )


class CategoriaNovedadFactory(_Base):
    class Meta:
        model = CategoriaNovedad

    categoria = factory.Sequence(lambda n: f"Categoria{n}")
    descripcion = "Descripción de categoría"
    contador = 0
    ejemplo = "Ejemplo de mensaje"


class UsuariosFactory(_Base):
    class Meta:
        model = Usuarios

    name = factory.Sequence(lambda n: f"Usuario {n}")
    email = factory.Sequence(lambda n: f"user{n}@test.local")
    password = "fake-hash"
    is_admin = False


class NovedadFactory(_Base):
    class Meta:
        model = Novedad

    titulo = "Novedad de prueba"
    descripcion = "Descripción extendida"
    severidad = SeveridadEnum.MEDIA
    estado = EstadoEnum.ABIERTA


class ChatMessageFactory(_Base):
    class Meta:
        model = ChatMessage

    phone = "5491100000000"
    role = RoleMensajeEnum.USER
    text = "mensaje de prueba"
    timestamp = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class ConversationStateFactory(_Base):
    class Meta:
        model = ConversationState

    phone = factory.Sequence(lambda n: f"54911000000{n:02d}")
    bot_active = True
    onboarding_step = OnboardingStepEnum.BIENVENIDA

    class Params:
        # Traits: enable with ConversationStateFactory(pending_email=True), etc.
        pending_email = factory.Trait(
            onboarding_step=OnboardingStepEnum.PENDING_EMAIL,
        )
        pending_verification = factory.Trait(
            onboarding_step=OnboardingStepEnum.PENDING_VERIFICATION,
            email="user@test.local",
            verification_token="token-fixture",
            verification_sent_at=factory.LazyFunction(
                lambda: datetime.now(timezone.utc) - timedelta(seconds=30)
            ),
        )
        pending_vicepresidencia = factory.Trait(
            onboarding_step=OnboardingStepEnum.PENDING_VICEPRESIDENCIA,
            email="user@test.local",
        )
        pending_direccion = factory.Trait(
            onboarding_step=OnboardingStepEnum.PENDING_DIRECCION,
            email="user@test.local",
        )
        pending_novedad = factory.Trait(
            onboarding_step=OnboardingStepEnum.PENDING_NOVEDAD,
            email="user@test.local",
        )
        pending_confirmacion = factory.Trait(
            onboarding_step=OnboardingStepEnum.PENDING_CONFIRMACION,
            email="user@test.local",
            pending_titulo="Phishing recibido",
            pending_descripcion="Me llegó un email raro pidiendo password",
            pending_severidad="alta",
        )
        completed = factory.Trait(
            onboarding_step=OnboardingStepEnum.COMPLETED,
            email="user@test.local",
        )
