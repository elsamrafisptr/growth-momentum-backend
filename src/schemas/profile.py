from marshmallow import Schema, fields

class ProfileRegisterSchema(Schema):
    id = fields.Str()
    age = fields.Int(required=True)
    job_type = fields.Str()
    job_name = fields.Str()
    activity_level = fields.Str()
    gender = fields.Str()
    preferences = fields.Str(required=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

class ProfileUpdateSchema(Schema):
    id = fields.Str()
    job_type = fields.Str()
    job_name = fields.Str()
    activity_level = fields.Str()
    preferences = fields.Str()
    updated_at = fields.DateTime()