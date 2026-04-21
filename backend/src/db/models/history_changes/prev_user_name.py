from src.extensions import db
from datetime import datetime, timezone


class PrevUserName(db.Model):
    __tablename__ = 'prev_user_name'
    id = db.Column(db.Integer, primary_key=True)
    fk_email_usuario = db.Column(db.String(120), db.ForeignKey('usuarios.email'), nullable=True)
    nombre_anterior = db.Column(db.String(120), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))