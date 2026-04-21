from src.extensions import db
from datetime import datetime, timezone


class PrevUserDireccion(db.Model):
    __tablename__ = 'prev_user_direccion'
    id = db.Column(db.Integer, primary_key=True)
    fk_email_usuario = db.Column(db.String(120), db.ForeignKey('usuarios.email'), nullable=True)
    fk_id_direccion = db.Column(db.Integer, db.ForeignKey('direccion.id'), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
