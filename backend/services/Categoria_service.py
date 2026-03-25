from models.Categoria import Categoria
from extensions import db

class CategoriaService:

    @staticmethod
    def crear_categoria(data):
        """Crea una categoría manualmente validando que el nombre sea único."""
        nombre = data.get("nombre")
        if Categoria.query.filter_by(nombre=nombre).first():
            return None, "La categoría ya existe."
        
        nueva_cat = Categoria(
            nombre=nombre,
            descripcion=data.get("descripcion"),
            palabra_clave=data.get("palabra_clave")
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
        """Permite modificar manualmente el nombre o la palabra clave."""
        categoria = Categoria.query.get(id)
        if not categoria:
            return None, "Categoría no encontrada."

        categoria.nombre = data.get("nombre", categoria.nombre)
        categoria.descripcion = data.get("descripcion", categoria.descripcion)
        categoria.palabra_clave = data.get("palabra_clave", categoria.palabra_clave)

        db.session.commit()
        return categoria, None

    @staticmethod
    def eliminar_categoria(id):
        categoria = Categoria.query.get(id)
        if not categoria:
            return False
        
        db.session.delete(categoria)
        db.session.commit()
        return True

    @staticmethod
    def obtener_todas():
        return Categoria.query.order_by(Categoria.nombre.asc()).all()