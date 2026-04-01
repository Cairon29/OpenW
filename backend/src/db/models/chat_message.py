from src.extensions import db
from src.db.models.enums import RoleMensajeEnum
from datetime import datetime, timezone
from pgvector.sqlalchemy import Vector


class ChatMessage(db.Model):
    __tablename__ = 'chat_message'

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False, index=True)
    role = db.Column(db.Enum(RoleMensajeEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    wa_message_id = db.Column(db.String(100), nullable=True, unique=True)
    status = db.Column(db.String(20), nullable=True)  # sent/delivered/read (outgoing only)
    embedding = db.Column(Vector(384), nullable=True)  # all-MiniLM-L6-v2 dimension
