from marshmallow import Schema, fields

class UserSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True)

class UserRegisterSchema(Schema):
    id = fields.Str()
    user = fields.Nested(UserSchema)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)

class UserLoginSchema(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()
    user = fields.Nested(UserSchema)