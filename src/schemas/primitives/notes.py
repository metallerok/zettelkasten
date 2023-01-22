import typing
from marshmallow import fields, ValidationError
from src.models.primitives.note import (
    NoteTitle,
    NoteColor,
)
from src.models.exc import (
    AttributeValidationError,
)


class NoteTitleField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return NoteTitle(value)
        except AttributeValidationError as e:
            raise ValidationError(e.message)
        except Exception:
            raise ValidationError("Invalid note title")

    def _serialize(self, value: NoteTitle, attr: str, obj: typing.Any, **kwargs):
        if value:
            return value.value

        return None


class NoteColorField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return NoteColor(value)
        except AttributeValidationError as e:
            raise ValidationError(e.message)
        except Exception:
            raise ValidationError("Invalid note color")

    def _serialize(self, value: NoteColor, attr: str, obj: typing.Any, **kwargs):
        if value:
            return value.value

        return None
