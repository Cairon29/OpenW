from src.extensions import db


class IAModel(db.Model):
    __tablename__ = 'ia_model'
    id = db.Column(db.Integer, primary_key=True)
    familia_modelos = db.Column(db.String(150), nullable=False, unique=True)
    modelo = db.Column(db.String(150), nullable=False, unique=True)
    url = db.Column(db.String(255), nullable=False)
    key = db.Column(db.String(255), nullable=False)
