from marshmallow import Schema, fields, validate
from models.Novedad import SeveridadEnum, EstadoEnum

class NovedadSchema(Schema):

    id = fields.Int(dump_only=True)
    fecha_registro = fields.DateTime(dump_only=True)
    titulo = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    descripcion = fields.Str(required=True)
    severidad = fields.Enum(SeveridadEnum, by_value=True)
    estado = fields.Enum(EstadoEnum, by_value=True)
    categoria_id = fields.Int(allow_none=True)
    user_phone = fields.Int(required=True) 
    creador = fields.Nested("UserSchema", only=("phone", "name"), dump_only=True)
    categoria = fields.Nested("CategoriaSchema", only=("id", "nombre"), dump_only=True)

novedad_schema = NovedadSchema()
novedades_schema = NovedadSchema(many=True)