from marshmallow import Schema, fields
from src.schemas.primitives.users import (
    FirstNameField,
    LastNameField,
    MiddleNameField,
    EmailFiled,
)


class RegistrationSchema(Schema):
    last_name = FirstNameField(required=False, missing=None)
    first_name = LastNameField(required=False, missing=None)
    middle_name = MiddleNameField(required=False, missing=None)

    email = EmailFiled(required=True)
    password = fields.String(required=True)
