from extensions import db
from datetime import datetime, timezone


class Vicepresidencia(db.Model):
    """
    Representa una vicepresidencia de la organización.
    Un usuario pertenece a UNA vicepresidencia (relación 1 a muchos).
    """

    __tablename__ = "vicepresidencias"

    id         = db.Column(db.Integer, primary_key=True)
    nombre     = db.Column(db.String(150), nullable=False, unique=True)
    direccion  = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    usuarios = db.relationship("User", back_populates="vicepresidencia", lazy="select")

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "nombre":     self.nombre,
            "direccion":  self.direccion,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Vicepresidencia {self.nombre}>"