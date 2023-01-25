from marshmallow import Schema, fields
from src.schemas.user import (
    EmailFiled
)


class UserAuthSchema(Schema):
    email = EmailFiled(required=True)
    password = fields.String(required=True)

    device_id = fields.String(required=False)
    device_type = fields.String(required=False)
    device_name = fields.String(required=False, missing=None)
    device_os = fields.String(required=False, missing=None)


class AuthSessionSchema(Schema):
    uuid = fields.String(required=True)
    user_uuid = fields.String(required=True)
    device_id = fields.String(required=True)
    created = fields.DateTime(required=True)
    device_type = fields.String(required=False, allow_none=True)
    device_os = fields.String(required=False, allow_none=True)
    ip = fields.String(required=False, allow_none=True)
    user_agent = fields.String(required=False, allow_none=True)
    expires_in = fields.DateTime(required=False, allow_none=True)


class AuthSessionRefreshSchema(Schema):
    refresh_token = fields.String(required=False)
    device_id = fields.String(required=False)


class SignOutSessionSchema(Schema):
    refresh_token = fields.String(required=False)
