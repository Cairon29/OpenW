"""
Validacion de input por fase usando Groq LLM como fallback.
Solo se llama cuando la validacion basica falla.
Retorna JSON unificado: {is_valid, extracted_value, guidance_message}.
"""

import json
import os
from src.utils.classification import get_groq_client
from src.db.models.chat_message import ChatMessage

VALIDATION_HISTORY = 2

_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'prompt_templates')

_TEMPLATE_FILES = {
    "email": "email_validation.txt",
    "menu_selection": "menu_selection.txt",
    "confirmation": "confirmation_validation.txt",
}

_SAFE_FALLBACK = {
    "is_valid": False,
    "extracted_value": None,
    "guidance_message": None,
}


def _load_template(phase):
    """Carga el prompt template para la fase indicada."""
    filename = _TEMPLATE_FILES.get(phase)
    if not filename:
        print(f"[AI Validation] Template desconocido para fase: {phase}")
        return None
    path = os.path.join(_TEMPLATES_DIR, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"[AI Validation] Template no encontrado: {path}")
        return None


def _inject_context(template, context):
    """Reemplaza placeholders en el template con valores del contexto."""
    if not context:
        return template
    result = template
    for key, value in context.items():
        placeholder = "{" + key.upper() + "}"
        result = result.replace(placeholder, str(value))
    return result


def _build_messages(system_prompt, phone, user_text):
    """Construye la lista de mensajes para Groq con historial minimo."""
    messages = [{"role": "system", "content": system_prompt}]

    historial = ChatMessage.query.filter_by(phone=phone)\
        .order_by(ChatMessage.timestamp.desc())\
        .limit(VALIDATION_HISTORY).all()
    historial = list(reversed(historial))

    for msg in historial:
        role = "assistant" if msg.role == "bot" else "user"
        messages.append({"role": role, "content": msg.text})

    messages.append({"role": "user", "content": user_text})
    return messages


def validate_input(phase, user_text, phone, context=None):
    """
    Valida el input del usuario usando IA como fallback.

    Args:
        phase: "email", "menu_selection", o "confirmation"
        user_text: mensaje raw del usuario
        phone: para historial de conversacion
        context: dict con valores para inyectar en el template
            - email: {"allowed_domain": "fiduprevisora.com.co"}
            - menu_selection: {"menu_options": "1. VP...", "menu_type": "Vicepresidencia"}
            - confirmation: {"valid_options": "...", "mode": "confirmacion|modificacion"}

    Returns:
        {"is_valid": bool, "extracted_value": str|None, "guidance_message": str|None}
    """
    try:
        client = get_groq_client()
        if client is None:
            return dict(_SAFE_FALLBACK)

        template = _load_template(phase)
        if template is None:
            return dict(_SAFE_FALLBACK)

        system_prompt = _inject_context(template, context)
        messages = _build_messages(system_prompt, phone, user_text)

        completion = client.chat.completions.create(
            messages=messages,
            model="qwen/qwen3-32b",
            response_format={"type": "json_object"},
            temperature=0.0,
        )

        result = json.loads(completion.choices[0].message.content)

        return {
            "is_valid": result.get("is_valid", False),
            "extracted_value": result.get("extracted_value"),
            "guidance_message": result.get("guidance_message"),
        }
    except Exception as e:
        print(f"[AI Validation] Error en fase '{phase}': {e}")
        return dict(_SAFE_FALLBACK)
