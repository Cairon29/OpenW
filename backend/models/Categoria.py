from extensions import db
from datetime import datetime, timezone


class Categoria(db.Model):
    __tablename__ = "categorias"

    id           = db.Column(db.Integer, primary_key=True)
    nombre       = db.Column(db.String(100), nullable=False, unique=True)
    descripcion  = db.Column(db.String(500), nullable=True)
    palabra_clave = db.Column(db.String(80), nullable=True)
    created_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    novedades = db.relationship("Novedad", back_populates="categoria", lazy="select")

    def __repr__(self):
        return f"<Categoria {self.nombre}>"
