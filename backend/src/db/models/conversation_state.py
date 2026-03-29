from src.extensions import db
from datetime import datetime, timezone


class ConversationState(db.Model):
    __tablename__ = 'conversation_state'

    phone = db.Column(db.String(20), primary_key=True)
    bot_active = db.Column(db.Boolean, nullable=False, default=True)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
