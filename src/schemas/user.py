from marshmallow import Schema, fields

class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    time_created = fields.Str(dump_only=True)

class UserUpdateSchema(Schema):
    username = fields.Str(allow_none=True, required=True)
    password = fields.Str(allow_none=True, required=True)
    roles = fields.List(cls_or_instance=fields.Int, required=True)

class UserSchema(PlainUserSchema):
    roles = fields.List(fields.Nested(PlainUserSchema), dump_only=True)

class CheckUserExistsSchema(Schema):
    email = fields.Str(required=True)

class UserLoginSchema(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()
    user = fields.Nested(UserSchema)