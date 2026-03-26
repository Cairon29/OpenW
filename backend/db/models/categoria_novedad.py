from backend.extensions import db
from datetime import datetime, timezone


class CategoriaNovedad(db.Model):
    __tablename__ = 'categoria_novedad'
    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(150), nullable=False, unique=True)
    descripcion = db.Column(db.Text, nullable=False)
    contador = db.Column(db.Integer, default=0)
    ejemplo = db.Column(db.Text, nullable=False)
    svg_icon = db.Column(db.Text, nullable=True)
    palabra_clave = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    novedades = db.relationship("Novedad", back_populates="categoria", lazy="select")

    def to_dict(self):
        return {
            "id": self.id,
            "categoria": self.categoria,
            "descripcion": self.descripcion,
            "contador": self.contador,
            "ejemplo": self.ejemplo,
            "svg_icon": self.svg_icon,
        }
