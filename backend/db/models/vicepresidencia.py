from backend.extensions import db
from datetime import datetime, timezone


class Vicepresidencia(db.Model):
    __tablename__ = 'vicepresidencia'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False, unique=True)
    descripcion = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    usuarios = db.relationship("Usuarios", back_populates="vicepresidencia", lazy="select")

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
