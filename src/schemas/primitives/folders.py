import typing
from marshmallow import fields, ValidationError
from src.models.primitives.folder import (
    FolderTitle,
    FolderColor,
)
from src.models.exc import (
    AttributeValidationError,
)


class FolderTitleField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return FolderTitle(value)
        except AttributeValidationError as e:
            raise ValidationError(e.message)
        except Exception:
            raise ValidationError("Invalid folder title")

    def _serialize(self, value: FolderTitle, attr: str, obj: typing.Any, **kwargs):
        if value:
            return value.value

        return None


class FolderColorField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return FolderColor(value)
        except AttributeValidationError as e:
            raise ValidationError(e.message)
        except Exception:
            raise ValidationError("Invalid folder color")

    def _serialize(self, value: FolderColor, attr: str, obj: typing.Any, **kwargs):
        if value:
            return value.value

        return None
