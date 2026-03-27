from src.extensions import db
from datetime import datetime, timezone
from .enums import SeveridadEnum, EstadoEnum


class Novedad(db.Model):
    __tablename__ = 'novedad'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    solucionada = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())
    fecha_solucion = db.Column(db.DateTime, nullable=True)
    fecha_registro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    severidad = db.Column(
        db.Enum(SeveridadEnum, name="severidad_enum"),
        nullable=True,
        default=SeveridadEnum.MEDIA,
    )
    estado = db.Column(
        db.Enum(EstadoEnum, name="estado_enum"),
        nullable=True,
        default=EstadoEnum.ABIERTA,
    )

    fk_id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    fk_id_direccion = db.Column(db.Integer, db.ForeignKey('direccion.id'), nullable=True)
    fk_id_categoria = db.Column(db.Integer, db.ForeignKey('categoria_novedad.id'), nullable=True)

    categoria = db.relationship("CategoriaNovedad", back_populates="novedades")
    creador = db.relationship("Usuarios", back_populates="novedades")

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "severidad": self.severidad.value if self.severidad else None,
            "estado": self.estado.value if self.estado else None,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
            "categoria": {
                "id": self.categoria.id,
                "categoria": self.categoria.categoria,
            } if self.categoria else None,
            "creador": {
                "id": self.creador.id,
                "name": self.creador.name,
            } if self.creador else None,
        }
