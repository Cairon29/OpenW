from src.extensions import db
from sqlalchemy.dialects.postgresql import JSONB


class configuracion(db.Model):
    __tablename__ = 'configuracion'
    id = db.Column(db.Integer, primary_key=True)
    version_name = db.Column(db.String(150), nullable=False, unique=True)
    data = db.Column(JSONB, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
