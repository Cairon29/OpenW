from marshmallow import Schema, fields, validate


class IAModelSchema(Schema):
    id = fields.Int(dump_only=True)
    familia_modelos = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=150),
    )
    modelo = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=150),
    )
    url = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
    )
    key = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
    )


ia_model_schema = IAModelSchema()
ia_models_schema = IAModelSchema(many=True)
