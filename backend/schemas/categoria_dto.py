from marshmallow import Schema, fields, validate

class CategoriaSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(
        required=True, 
        validate=validate.Length(min=3, max=100),
        error_messages={"required": "El nombre de la categoría es obligatorio."}
    )
    descripcion = fields.Str(validate=validate.Length(max=500))
    palabra_clave = fields.Str(
        validate=validate.Length(max=80),
        allow_none=True
    )
    created_at = fields.DateTime(dump_only=True)


categoria_schema = CategoriaSchema()
categorias_schema = CategoriaSchema(many=True)