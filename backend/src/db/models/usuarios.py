from src.extensions import db
from datetime import datetime, timezone


class Usuarios(db.Model):
    __tablename__ = 'usuarios'
    phone = db.Column(db.String(20), nullable=True, unique=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), primary_key=True)
    password = db.Column(db.String(120), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    fk_id_vicepresidencia = db.Column(db.Integer, db.ForeignKey('vicepresidencia.id'), nullable=True)
    fk_id_direccion = db.Column(db.Integer, db.ForeignKey('direccion.id'), nullable=True)

    vicepresidencia = db.relationship("Vicepresidencia", back_populates="usuarios")
    novedades = db.relationship("Novedad", back_populates="creador", lazy="select")
