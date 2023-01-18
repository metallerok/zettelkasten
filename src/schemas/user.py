from marshmallow import Schema, fields, validate
from src.schemas.primitives.users import (
    FirstNameField,
    MiddleNameField,
    LastNameField,
)


class UserDumpSchema(Schema):
    id = fields.String(dump_only=True, required=True)
    email = fields.Email(required=True)

    first_name = FirstNameField()
    last_name = LastNameField()
    middle_name = MiddleNameField()

    created = fields.DateTime(dump_only=True)
    updated = fields.DateTime(dump_only=True)


class CurrentUserDumpSchema(UserDumpSchema):
    is_admin = fields.Boolean(dump_only=True)


class PasswordChangeRequestByEmailSchema(Schema):
    email = fields.Email(required=True)


class PasswordChangeBodySchema(Schema):
    password = fields.String(required=True, validate=validate.Length(min=8, max=32))


class PasswordChangeParamsSchema(Schema):
    token = fields.String(required=True)


class CurrentUserChangePasswordSchema(Schema):
    current_password = fields.String(required=True, validate=validate.Length(min=8, max=32))
    new_password = fields.String(required=True, validate=validate.Length(min=8, max=32))
