from marshmallow import Schema, fields, validate


class DireccionSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=150),
        error_messages={"required": "El nombre de la dirección es obligatorio."},
    )
    descripcion = fields.Str(validate=validate.Length(max=500), allow_none=True)
    fk_id_vicepresidencia = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)


direccion_schema = DireccionSchema()
direcciones_schema = DireccionSchema(many=True)
