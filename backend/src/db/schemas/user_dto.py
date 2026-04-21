from marshmallow import Schema, fields


class UserSchema(Schema):
    phone = fields.Str()
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    is_admin = fields.Boolean()
    fk_id_vicepresidencia = fields.Int()
    fk_id_direccion = fields.Int()


user_schema = UserSchema()
users_schema = UserSchema(many=True)
