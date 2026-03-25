from .app import db
from sqlalchemy.dialects.postgresql import JSONB

class Usuarios(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  
    fk_id_vicepresidencia = db.Column(db.Integer, db.ForeignKey('vicepresidencia.id'), nullable=True)
    fk_id_direccion = db.Column(db.Integer, db.ForeignKey('direccion.id'), nullable=True)

    # todo: metodos de autorizacion y autenticacion, relacion con logs, configuraciones, etc

class Vicepresidencia(db.Model):
    __tablename__ = 'vicepresidencia'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False, unique=True)
    descripcion = db.Column(db.Text, nullable=False)

class Direccion(db.Model):
    __tablename__ = 'direccion'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False, unique=True)
    descripcion = db.Column(db.Text, nullable=False)
    fk_id_vicepresidencia = db.Column(db.Integer, db.ForeignKey('vicepresidencia.id'), nullable=True)


class Novedad(db.Model):
    __tablename__ = 'novedad'
    id = db.Column(db.Integer, primary_key=True)
    fk_id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fk_id_direccion = db.Column(db.Integer, db.ForeignKey('direccion.id'), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    solucionada = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())
    fecha_solucion = db.Column(db.DateTime, nullable=True)
    fk_id_categoria = db.Column(db.String(150), db.ForeignKey('categoria_novedad.id'), nullable=False)


class CategoriaNovedad(db.Model): 
    __tablename__ = 'categoria_novedad'
    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(150), nullable=False, unique=True)
    descripcion = db.Column(db.Text, nullable=False, unique=True)
    contador = db.Column(db.Integer, default=0)
    ejemplo = db.Column(db.Text, nullable=False, unique=True)
    svg_icon = db.Column(db.Text, nullable=True) # Nueva columna para el SVG del icono

    def to_dict(self):
        return {
            "id": self.id,
            "categoria": self.categoria,
            "descripcion": self.descripcion,
            "contador": self.contador,
            "ejemplo": self.ejemplo,
            "svg_icon": self.svg_icon
        }

class IAModel(db.Model):
    __tablename__ = 'ia_model'
    id = db.Column(db.Integer, primary_key=True)
    familia_modelos = db.Column(db.String(150), nullable=False, unique=True)
    modelo = db.Column(db.String(150), nullable=False, unique=True)
    url = db.Column(db.String(255), nullable=False)
    key = db.Column(db.String(255), nullable=False)

class configuracion(db.Model):
    __tablename__ = 'configuracion'
    id = db.Column(db.Integer, primary_key=True)
    version_name = db.Column(db.String(150), nullable=False, unique=True)
    data = db.Column(JSONB, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)