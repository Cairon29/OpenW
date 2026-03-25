from extensions import db
from datetime import datetime  

class User(db.Model): 
    __tablename__ = 'users' 
    phone = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    vicepresidencia_id = db.Column(
        db.Integer,
        db.ForeignKey("vicepresidencias.id", ondelete="SET NULL"),
        nullable=True, 
    )
    
  
    direccion_id = db.Column(db.Integer, nullable=True) 

    vicepresidencia = db.relationship("Vicepresidencia", back_populates="usuarios")
    novedades = db.relationship("Novedad", back_populates="creador", lazy="select")

    def to_dict(self) -> dict: 
        return {
            "phone": self.phone,
            "name": self.name,
            "email": self.email,
            "is_admin": self.is_admin,
            "vicepresidencia_id": self.vicepresidencia_id,
            "direccion_id": self.direccion_id, 
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<User {self.name} ({self.email})>"