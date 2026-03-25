from marshmallow import Schema, fields


class UserSchema(Schema):
    phone = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    is_admin = fields.Boolean()
    vicepresidencia_id = fields.Int()
    direccion_id = fields.Int()

    novedades = fields.List(fields.Pluck("NovedadSchema", "phone"))
