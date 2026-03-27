from src.extensions import db
from datetime import datetime, timezone


class ChatMessage(db.Model):
    __tablename__ = 'chat_message'

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False, index=True)
    role = db.Column(db.String(10), nullable=False)  # "user" or "bot"
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    wa_message_id = db.Column(db.String(100), nullable=True, unique=True)
    status = db.Column(db.String(20), nullable=True)  # sent/delivered/read (outgoing only)
