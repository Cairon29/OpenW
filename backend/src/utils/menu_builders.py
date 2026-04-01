"""
Funciones de construcción de menús para el flujo de conversación WhatsApp.
Extraídas como utilidades para evitar imports circulares entre AuthService y ChatService.
"""


def build_vicepresidencia_menu():
    """Construye lista numerada de vicepresidencias desde la DB."""
    from src.db.models.vicepresidencia import Vicepresidencia
    vps = Vicepresidencia.query.order_by(Vicepresidencia.id).all()
    if not vps:
        return None
    lines = [f"{i + 1}. {vp.nombre}" for i, vp in enumerate(vps)]
    return (
        "✅ *Tu email fue verificado con éxito.*\n\n"
        "Ahora seleccioná tu *Vicepresidencia*:\n\n"
        + "\n".join(lines)
        + "\n\nRespondé con el *número* de tu opción."
    )


def build_direccion_menu(vicepresidencia_id):
    """Construye lista numerada de direcciones filtradas por vicepresidencia."""
    from src.db.models.direccion import Direccion
    dirs = Direccion.query.filter_by(fk_id_vicepresidencia=vicepresidencia_id)\
        .order_by(Direccion.id).all()
    if not dirs:
        return None
    lines = [f"{i + 1}. {d.nombre}" for i, d in enumerate(dirs)]
    return (
        "Seleccioná tu *Dirección*:\n\n"
        + "\n".join(lines)
        + "\n\nRespondé con el *número* de tu opción."
    )


def build_confirmation_summary(estado):
    """Construye el resumen completo de datos recopilados para confirmación."""
    from src.db.models.vicepresidencia import Vicepresidencia
    from src.db.models.direccion import Direccion
    from src.db.models.categoria_novedad import CategoriaNovedad

    vp = Vicepresidencia.query.get(estado.fk_id_vicepresidencia) if estado.fk_id_vicepresidencia else None
    dir_ = Direccion.query.get(estado.fk_id_direccion) if estado.fk_id_direccion else None
    cat = CategoriaNovedad.query.get(estado.pending_categoria_id) if estado.pending_categoria_id else None

    return (
        "📋 *Resumen de tu reporte:*\n\n"
        f"📧 *Email:* {estado.email}\n"
        f"🏢 *Vicepresidencia:* {vp.nombre if vp else 'N/A'}\n"
        f"📁 *Dirección:* {dir_.nombre if dir_ else 'N/A'}\n"
        f"📝 *Título:* {estado.pending_titulo}\n"
        f"🏷️ *Categoría:* {cat.categoria if cat else 'General'}\n"
        f"⚠️ *Severidad:* {estado.pending_severidad}\n"
        f"💬 *Descripción:* {estado.pending_descripcion}\n\n"
        "¿Los datos son correctos?\n\n"
        "*1.* Sí, confirmar ✅\n"
        "*2.* Modificar ✏️"
    )


def build_modification_menu():
    """Construye el menú de opciones para modificar datos."""
    return (
        "¿Qué deseas modificar?\n\n"
        "*1.* Vicepresidencia\n"
        "*2.* Dirección\n"
        "*3.* Novedad (volver a describir el problema)\n\n"
        "Respondé con el *número*."
    )
