from marshmallow import Schema, fields, validate


class ConfiguracionSchema(Schema):
    id = fields.Int(dump_only=True)
    version_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=150),
    )
    data = fields.Dict(required=True)
    is_active = fields.Boolean()


configuracion_schema = ConfiguracionSchema()
configuraciones_schema = ConfiguracionSchema(many=True)
