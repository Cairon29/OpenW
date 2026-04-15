"""
Utilidad para almacenamiento de mensajes de chat en la base de datos.
"""

from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from src.extensions import db
from src.db.models.chat_message import ChatMessage


def store_message(phone, role, text, wa_message_id=None):
    """Guarda un mensaje en la base de datos e intenta generar su embedding."""
    phone = str(phone)

    embedding = None
    try:
        from src.utils.embeddings import get_embedding
        embedding = get_embedding(text)
    except Exception as e:
        print(f"[Embeddings] No se pudo generar embedding: {e}")

    msg = ChatMessage(
        phone=phone,
        role=role,
        text=text,
        wa_message_id=wa_message_id,
        timestamp=datetime.now(timezone.utc),
        embedding=embedding,
    )
    try:
        db.session.add(msg)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        print(f"[Chat] Duplicate message ignored: {wa_message_id}")
        return

    from src.modules.chat.events import publish
    publish({
        "type": "new_message",
        "phone": phone,
        "role": role.value if hasattr(role, "value") else str(role),
        "text": text,
        "time": msg.timestamp.isoformat(),
    })
