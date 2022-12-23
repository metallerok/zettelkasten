import typing
from marshmallow import fields, ValidationError
from src.models.primitives.user import (
    FirstName,
    LastName,
    MiddleName,
)
from src.models.exc import (
    AttributeValidationError,
)


class FirstNameField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return FirstName(value)
        except AttributeValidationError as e:
            raise ValidationError(e.message)
        except Exception:
            raise ValidationError("Invalid first name")

    def _serialize(self, value: FirstName, attr: str, obj: typing.Any, **kwargs):
        if value:
            return value.value

        return None


class LastNameField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return LastName(value)
        except AttributeValidationError as e:
            raise ValidationError(e.message)
        except Exception:
            raise ValidationError("Invalid last name")

    def _serialize(self, value: LastName, attr: str, obj: typing.Any, **kwargs):
        if value:
            return value.value

        return None


class MiddleNameField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return MiddleName(value)
        except AttributeValidationError as e:
            raise ValidationError(e.message)
        except Exception:
            raise ValidationError("Invalid middle name")

    def _serialize(self, value: MiddleName, attr: str, obj: typing.Any, **kwargs):
        if value:
            return value.value

        return None
