from backend.extensions import db
from backend.schemas import Vicepresidencia


class VicepresidenciaService:

    @staticmethod
    def crear(data):
        nombre = data.get("nombre")
        if Vicepresidencia.query.filter_by(nombre=nombre).first():
            return None, "Esta vicepresidencia ya está registrada."

        nueva_vp = Vicepresidencia(
            nombre=nombre,
            descripcion=data.get("descripcion"),
        )

        try:
            db.session.add(nueva_vp)
            db.session.commit()
            return nueva_vp, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def obtener_todas():
        return Vicepresidencia.query.order_by(Vicepresidencia.nombre.asc()).all()

    @staticmethod
    def obtener_por_id(vp_id):
        return Vicepresidencia.query.get(vp_id)
