
from extensions import db
from datetime import datetime, timezone
import enum

class SeveridadEnum(str, enum.Enum):
    CRITICA  = "critica"
    ALTA     = "alta"
    MEDIA    = "media"
    BAJA     = "baja"
    INFO     = "informativa"

class EstadoEnum(str, enum.Enum):
    ABIERTA     = "abierta"
    EN_PROCESO  = "en_proceso"
    RESUELTA    = "resuelta"
    DESCARTADA  = "descartada"


class Novedad(db.Model):
    __tablename__ = "novedades"

    id             = db.Column(db.Integer, primary_key=True)
    titulo         = db.Column(db.String(200), nullable=False)
    descripcion    = db.Column(db.Text, nullable=False)
    fecha_registro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    severidad = db.Column(
        db.Enum(SeveridadEnum, name="severidad_enum"),
        nullable=False,
        default=SeveridadEnum.MEDIA,
    )
    estado = db.Column(
        db.Enum(EstadoEnum, name="estado_enum"),
        nullable=False,
        default=EstadoEnum.ABIERTA,
    )

    
    categoria_id = db.Column(
        db.Integer,
        db.ForeignKey("categorias.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    
    user_phone = db.Column(
        db.Integer,
        db.ForeignKey("users.phone", ondelete="SET NULL"),
        nullable=True,
    )

   
    categoria = db.relationship("Categoria", back_populates="novedades")

    creador   = db.relationship("User", back_populates="novedades")

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "titulo":          self.titulo,
            "descripcion":     self.descripcion,
            "severidad":       self.severidad.value if self.severidad else None,
            "estado":          self.estado.value if self.estado else None,
            "fecha_registro":  self.fecha_registro.isoformat() if self.fecha_registro else None,
            "categoria": {
                "id":     self.categoria.id,
                "nombre": self.categoria.nombre,
            } if self.categoria else None,
            "creador": {
                "phone":  self.creador.phone, 
                "name":   self.creador.name,
            } if self.creador else None,
        }

    def __repr__(self):
        return f"<Novedad '{self.titulo}' [{self.severidad}]>"