"""
Clasificacion de mensajes de usuario usando Groq LLM.
Carga el prompt template desde archivo, inyecta categorias de DB,
y retorna clasificacion estructurada en JSON.
"""

import json
import os
from groq import Groq
from src.extensions import db
from src.db.models import CategoriaNovedad
from src.db.models.chat_message import ChatMessage
from src.config import config


_groq_client = None

HISTORY_WINDOW = 10
SIMILAR_WINDOW = 3

_TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'prompt_templates', 'category_classification.txt'
)


def get_groq_client():
    global _groq_client
    if _groq_client is None:
        api_key = config.GROQ_API_KEY
        if not api_key:
            print("[WARNING] GROQ_API_KEY not set. AI features will be disabled.")
            return None
        _groq_client = Groq(api_key=api_key)
    return _groq_client


def _load_template():
    """Carga el prompt template desde archivo."""
    try:
        with open(_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"[Classification] Template not found: {_TEMPLATE_PATH}")
        return (
            "Eres un asistente de atencion al cliente. Analiza el mensaje y responde en JSON.\n"
            "Campos: titulo, severidad, categoria, respuesta_usuario.\n"
            "Categorias: {CATEGORIAS}\n{EJEMPLOS}\n{CONTEXTO_SIMILAR}"
        )


def _build_categorias_text(categorias):
    """Construye el texto de categorias con descripcion para el prompt."""
    return "\n".join(
        f"- {c.categoria}: {c.descripcion}" for c in categorias
    )


def _build_ejemplos_text(categorias):
    """Construye ejemplos de clasificacion a partir de las categorias que tienen ejemplo."""
    ejemplos = [
        f'Usuario: "{c.ejemplo}" → {c.categoria}'
        for c in categorias if c.ejemplo
    ]
    return "\n".join(ejemplos) if ejemplos else "No hay ejemplos disponibles."


def _buscar_mensajes_similares(texto, phone_excluir, limit=SIMILAR_WINDOW):
    """
    Busca mensajes semanticamente similares en otras conversaciones usando pgVector.
    Retorna una lista de ChatMessage o lista vacia si embeddings no estan disponibles.
    """
    try:
        from src.utils.embeddings import get_embedding
        embedding = get_embedding(texto)
        similares = ChatMessage.query\
            .filter(ChatMessage.phone != phone_excluir)\
            .filter(ChatMessage.embedding.isnot(None))\
            .filter(ChatMessage.role == "user")\
            .order_by(ChatMessage.embedding.cosine_distance(embedding))\
            .limit(limit)\
            .all()
        return similares
    except Exception as e:
        print(f"[Embeddings] Busqueda semantica no disponible: {e}")
        return []


def _build_system_prompt(categorias, texto, phone):
    """Construye el system prompt completo inyectando categorias, ejemplos y contexto similar."""
    template = _load_template()

    categorias_txt = _build_categorias_text(categorias)
    ejemplos_txt = _build_ejemplos_text(categorias)

    contexto_similar = _buscar_mensajes_similares(texto, phone)
    contexto_txt = ""
    if contexto_similar:
        ejemplos_sim = "\n".join(f"- {m.text}" for m in contexto_similar)
        contexto_txt = f"### Mensajes similares previos de otros usuarios\n{ejemplos_sim}"

    return template\
        .replace("{CATEGORIAS}", categorias_txt)\
        .replace("{EJEMPLOS}", ejemplos_txt)\
        .replace("{CONTEXTO_SIMILAR}", contexto_txt)


def _match_categoria(nombre_ia, categorias):
    """
    Busca la categoria en DB usando ilike para tolerancia a mayusculas/acentos.
    Si no matchea, busca 'General' como fallback.
    """
    if not nombre_ia:
        return None

    categoria = CategoriaNovedad.query.filter(
        CategoriaNovedad.categoria.ilike(nombre_ia)
    ).first()

    if categoria:
        categoria.contador += 1
        db.session.commit()
        return categoria

    # Fallback: buscar "General" o "Otro"
    for fallback_name in ("General", "Otro"):
        fallback = CategoriaNovedad.query.filter(
            CategoriaNovedad.categoria.ilike(fallback_name)
        ).first()
        if fallback:
            fallback.contador += 1
            db.session.commit()
            return fallback

    return None


def classify_message(phone, texto):
    """
    Clasifica un mensaje de usuario usando Groq LLM.

    Retorna dict con:
      - titulo: str
      - severidad: str
      - categoria_obj: CategoriaNovedad | None
      - respuesta_usuario: str
    """
    try:
        groq_client = get_groq_client()
        if groq_client is None:
            raise Exception("Groq client not available (GROQ_API_KEY not set)")

        categorias = CategoriaNovedad.query.all()
        if not categorias:
            raise Exception("No categories found in database")

        system_prompt = _build_system_prompt(categorias, texto, phone)

        # Historial de la conversacion actual (ultimos N mensajes)
        historial = ChatMessage.query.filter_by(phone=phone)\
            .order_by(ChatMessage.timestamp.desc())\
            .limit(HISTORY_WINDOW).all()
        historial = list(reversed(historial))

        messages = [{"role": "system", "content": system_prompt}]
        for msg in historial:
            role = "assistant" if msg.role == "bot" else "user"
            messages.append({"role": role, "content": msg.text})
        messages.append({"role": "user", "content": texto})

        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model="qwen/qwen3-32b",
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        result = json.loads(chat_completion.choices[0].message.content)

        # Match categoria contra DB con ilike
        categoria_obj = _match_categoria(result.get("categoria"), categorias)

        return {
            "titulo": result.get("titulo", texto[:50]),
            "severidad": result.get("severidad", "media"),
            "categoria_obj": categoria_obj,
            "respuesta_usuario": result.get(
                "respuesta_usuario",
                "Recibimos tu mensaje. En breve te daremos mas informacion."
            ),
        }
    except Exception as e:
        print(f"[Classification] Error: {e}")
        return {
            "titulo": "Mensaje recibido",
            "severidad": "media",
            "categoria_obj": None,
            "respuesta_usuario": "Recibimos tu mensaje. En breve te daremos mas informacion.",
        }
