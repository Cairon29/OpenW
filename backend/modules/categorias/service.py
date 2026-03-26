from backend.extensions import db
from backend.schemas import CategoriaNovedad


class CategoriasService:

    @staticmethod
    def crear_categoria(data):
        nombre = data.get("nombre") or data.get("categoria")
        if CategoriaNovedad.query.filter_by(categoria=nombre).first():
            return None, "La categoría ya existe."

        nueva_cat = CategoriaNovedad(
            categoria=nombre,
            descripcion=data.get("descripcion"),
            palabra_clave=data.get("palabra_clave"),
        )

        try:
            db.session.add(nueva_cat)
            db.session.commit()
            return nueva_cat, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def actualizar_categoria(id, data):
        categoria = CategoriaNovedad.query.get(id)
        if not categoria:
            return None, "Categoría no encontrada."

        categoria.categoria = data.get("nombre", categoria.categoria)
        categoria.descripcion = data.get("descripcion", categoria.descripcion)
        categoria.palabra_clave = data.get("palabra_clave", categoria.palabra_clave)

        db.session.commit()
        return categoria, None

    @staticmethod
    def eliminar_categoria(id):
        categoria = CategoriaNovedad.query.get(id)
        if not categoria:
            return False

        db.session.delete(categoria)
        db.session.commit()
        return True

    @staticmethod
    def obtener_todas():
        return CategoriaNovedad.query.order_by(CategoriaNovedad.categoria.asc()).all()
