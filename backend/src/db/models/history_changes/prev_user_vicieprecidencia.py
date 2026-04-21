from src.extensions import db
from datetime import datetime, timezone


class PrevUserViceprecidencia(db.Model):
    __tablename__ = 'prev_user_viceprecidencia'
    id = db.Column(db.Integer, primary_key=True)
    fk_email_usuario = db.Column(db.String(120), db.ForeignKey('usuarios.email'), nullable=True)
    fk_id_viceprecidencia = db.Column(db.Integer, db.ForeignKey('vicepresidencia.id'), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))