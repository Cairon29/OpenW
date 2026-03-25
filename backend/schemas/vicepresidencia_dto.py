from marshmallow import Schema, fields, validate

class VicepresidenciaSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(
        required=True, 
        validate=validate.Length(min=3, max=150),
        error_messages={"required": "El nombre de la vicepresidencia es obligatorio."}
    )
    direccion = fields.Str(validate=validate.Length(max=250), allow_none=True)
    created_at = fields.DateTime(dump_only=True)

vicepresidencia_schema = VicepresidenciaSchema()
vicepresidencias_schema = VicepresidenciaSchema(many=True)