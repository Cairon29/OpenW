from src.extensions import db
from src.db.models.enums import OnboardingStepEnum
from datetime import datetime, timezone


class ConversationState(db.Model):
    __tablename__ = 'conversation_state'

    phone                = db.Column(db.String(20), primary_key=True)
    bot_active           = db.Column(db.Boolean, nullable=False, default=True)
    updated_at           = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    onboarding_step      = db.Column(
        db.Enum(OnboardingStepEnum, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=OnboardingStepEnum.BIENVENIDA,
    )
    email                = db.Column(db.String(120), nullable=True)
    verification_token   = db.Column(db.String(64), nullable=True, unique=True)
    verification_sent_at = db.Column(db.DateTime, nullable=True)

    # Datos de perfil (persisten entre novedades)
    fk_id_vicepresidencia = db.Column(db.Integer, db.ForeignKey('vicepresidencia.id'), nullable=True)
    fk_id_direccion       = db.Column(db.Integer, db.ForeignKey('direccion.id'), nullable=True)

    # Datos temporales de novedad (se limpian después de cada confirmación)
    pending_titulo        = db.Column(db.String(200), nullable=True)
    pending_descripcion   = db.Column(db.Text, nullable=True)
    pending_severidad     = db.Column(db.String(20), nullable=True)
    pending_categoria_id  = db.Column(db.Integer, db.ForeignKey('categoria_novedad.id'), nullable=True)
    pending_respuesta     = db.Column(db.Text, nullable=True)

    # Flag para sub-flujo de modificación en confirmación
    awaiting_modification = db.Column(db.Boolean, default=False)

    # Relationships
    vicepresidencia   = db.relationship("Vicepresidencia", foreign_keys=[fk_id_vicepresidencia])
    direccion         = db.relationship("Direccion", foreign_keys=[fk_id_direccion])
    pending_categoria = db.relationship("CategoriaNovedad", foreign_keys=[pending_categoria_id])
