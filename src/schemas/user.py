from marshmallow import Schema, fields
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
