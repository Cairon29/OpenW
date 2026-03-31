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
        db.Enum(OnboardingStepEnum),
        nullable=False,
        default=OnboardingStepEnum.PENDING_EMAIL,
    )
    email                = db.Column(db.String(120), nullable=True)
    verification_token   = db.Column(db.String(64), nullable=True, unique=True)
    verification_sent_at = db.Column(db.DateTime, nullable=True)
