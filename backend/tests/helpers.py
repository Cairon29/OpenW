"""
Reusable assertion helpers for characterization tests.
Kept tiny and explicit — prefer `assert` in tests when a helper would hide intent.
"""
from src.db.models.chat_message import ChatMessage
from src.db.models.conversation_state import ConversationState
from src.db.models.enums import RoleMensajeEnum


def reload_state(phone):
    """Return a fresh copy of ConversationState from DB."""
    return ConversationState.query.get(str(phone))


def bot_messages_for(phone):
    """List bot text messages sent to a phone in insertion order."""
    msgs = (
        ChatMessage.query
        .filter_by(phone=str(phone), role=RoleMensajeEnum.BOT)
        .order_by(ChatMessage.timestamp, ChatMessage.id)
        .all()
    )
    return [m.text for m in msgs]


def user_messages_for(phone):
    msgs = (
        ChatMessage.query
        .filter_by(phone=str(phone), role=RoleMensajeEnum.USER)
        .order_by(ChatMessage.timestamp, ChatMessage.id)
        .all()
    )
    return [m.text for m in msgs]


def assert_wa_sent_contains(mock_whatsapp, *fragments):
    """Asserta que algún mensaje enviado por WA contiene cada fragmento dado."""
    sent = [call["args"][1] for call in mock_whatsapp.send.calls]
    for fragment in fragments:
        assert any(fragment in text for text in sent), (
            f"Fragment {fragment!r} not found in sent messages: {sent!r}"
        )
