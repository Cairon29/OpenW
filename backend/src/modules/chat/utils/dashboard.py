"""
Funciones de dashboard para el modulo chat.
Manejo de estado del bot, metricas, conversaciones y mensajes manuales.
"""

from datetime import datetime, timezone, date, timedelta
from sqlalchemy import func

from src.extensions import db
from src.db.models import Novedad
from src.db.models.chat_message import ChatMessage
from src.db.models.conversation_state import ConversationState
from src.db.models.enums import OnboardingStepEnum
from src.utils.whatsapp import enviar_whatsapp
from src.utils.messages import store_message


def _get_bot_state(phone):
    """Lee el estado del bot para este telefono desde la DB. Default: True (activo)."""
    state = ConversationState.query.get(phone)
    return state.bot_active if state else True


def toggle_bot(phone):
    """Activa o desactiva el bot para una conversacion. Retorna el nuevo estado."""
    phone = str(phone)
    state = ConversationState.query.get(phone)
    if state is None:
        state = ConversationState(phone=phone, bot_active=False)
        db.session.add(state)
    else:
        state.bot_active = not state.bot_active
        state.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return state.bot_active


def set_bot_state(phone, active):
    """Establece el estado del bot para una conversacion."""
    phone = str(phone)
    state = ConversationState.query.get(phone)
    if state is None:
        state = ConversationState(phone=phone, bot_active=bool(active))
        db.session.add(state)
    else:
        state.bot_active = bool(active)
        state.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return state.bot_active


def enviar_mensaje_manual(phone, mensaje):
    """Envia un mensaje manual desde el dashboard (ignora estado del bot)."""
    phone = str(phone)
    wamid = enviar_whatsapp(phone, mensaje)
    store_message(phone, "bot", mensaje, wa_message_id=wamid)


def get_conversations():
    """Retorna todas las conversaciones activas con sus mensajes desde la DB."""
    subq = db.session.query(
        ChatMessage.phone,
        func.max(ChatMessage.timestamp).label('last_time')
    ).group_by(ChatMessage.phone).subquery()

    phones = db.session.query(subq.c.phone, subq.c.last_time).order_by(
        subq.c.last_time.desc()
    ).all()

    result = []
    for phone, _ in phones:
        msgs = ChatMessage.query.filter_by(phone=phone).order_by(ChatMessage.timestamp).all()
        messages = [{"role": m.role, "text": m.text, "time": m.timestamp.isoformat()} for m in msgs]
        last = messages[-1] if messages else {}
        result.append({
            "phone": phone,
            "bot_active": _get_bot_state(phone),
            "last_message": last.get("text", ""),
            "last_time": last.get("time", ""),
            "messages": messages,
        })
    return result


def update_message_status(wa_message_id, status):
    """Actualiza el estado de entrega de un mensaje (sent/delivered/read)."""
    msg = ChatMessage.query.filter_by(wa_message_id=wa_message_id).first()
    if msg:
        msg.status = status
        db.session.commit()


def get_bot_metrics():
    """Calcula metricas reales del bot desde la DB."""
    total_conversations = db.session.query(
        func.count(func.distinct(ChatMessage.phone))
    ).scalar() or 0

    bot_messages = ChatMessage.query.filter_by(role="bot").count()

    responded = db.session.query(
        func.count(func.distinct(ChatMessage.phone))
    ).filter(ChatMessage.role == "bot").scalar() or 0

    response_rate = round((responded / total_conversations * 100) if total_conversations else 0)

    today = date.today()
    usage_over_time = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = ChatMessage.query.filter(
            func.date(ChatMessage.timestamp) == day
        ).count()
        usage_over_time.append({"date": str(day), "count": count})

    con_categoria = Novedad.query.filter(Novedad.fk_id_categoria.isnot(None)).count()
    sin_categoria = Novedad.query.filter(Novedad.fk_id_categoria.is_(None)).count()

    return {
        "totalConversations": total_conversations,
        "botMessages": bot_messages,
        "responseRate": response_rate,
        "usageOverTime": usage_over_time,
        "effectiveness": {
            "conContexto": con_categoria,
            "sinContexto": sin_categoria,
        },
    }
