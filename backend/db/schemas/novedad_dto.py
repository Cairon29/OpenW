from marshmallow import Schema, fields, validate
from backend.db.models import SeveridadEnum, EstadoEnum


class NovedadSchema(Schema):
    id = fields.Int(dump_only=True)
    fecha_registro = fields.DateTime(dump_only=True)
    titulo = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    descripcion = fields.Str(required=True)
    severidad = fields.Enum(SeveridadEnum, by_value=True)
    estado = fields.Enum(EstadoEnum, by_value=True)
    fk_id_categoria = fields.Int(allow_none=True)
    fk_id_usuario = fields.Int(allow_none=True)
    creador = fields.Nested("UserSchema", only=("id", "name"), dump_only=True)
    categoria = fields.Nested("CategoriaSchema", only=("id", "categoria"), dump_only=True)


novedad_schema = NovedadSchema()
novedades_schema = NovedadSchema(many=True)
