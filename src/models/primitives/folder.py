import sqlalchemy as sa
import re
from src.models.exc import AttributeValidationError
from copy import deepcopy


class FolderTitle:
    MAX_LENGTH = 60
    MIN_LENGTH = 3
    PATTERN = r"^[a-zA-Z0-9а-яА-Я-_() ]{3,60}$"

    def __init__(self, value: str):
        if value is None:
            raise AttributeValidationError("FolderTitle cannot be None")

        if len(value) == 0:
            raise AttributeValidationError("FolderTitle cannot be empty")

        if len(value) < self.MIN_LENGTH:
            raise AttributeValidationError("FolderTitle is too short")

        if len(value) > self.MAX_LENGTH:
            raise AttributeValidationError("FolderTitle is too long")

        regexp = re.compile(self.PATTERN)

        if not bool(regexp.match(value)):
            raise AttributeValidationError("FolderTitle does not match expected pattern")

        self._value = value

    @property
    def value(self):
        return deepcopy(self._value)

    def __eq__(self, other: 'FolderTitle'):
        other_value = other.value if type(other) == FolderTitle else None
        return self._value == other_value

    def __str__(self):
        return self._value

    def __repr__(self):
        return f"<FolderTitle value={self._value}>"


class SAFolderTitle(sa.TypeDecorator):
    @property
    def python_type(self):
        return FolderTitle

    impl = sa.String

    cache_ok = True

    def process_bind_param(self, value: FolderTitle, dialect):
        return value.value

    def process_result_value(self, value, dialect):
        return FolderTitle(value)


class FolderColor:
    MIN_LENGTH = 4
    MAX_LENGTH = 7
    PATTERN = r"^#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$"

    def __init__(self, value: str):
        if len(value) < self.MIN_LENGTH:
            raise AttributeValidationError("FolderColor is too short")

        if len(value) > self.MAX_LENGTH:
            raise AttributeValidationError("FolderColor is too long")

        regexp = re.compile(self.PATTERN)

        if not bool(regexp.match(value)):
            raise AttributeValidationError("FolderColor does not match expected pattern")

        self._value = value

    @property
    def value(self):
        return deepcopy(self._value)

    def __eq__(self, other: 'FolderColor'):
        other_value = other.value if type(other) == FolderColor else None
        return self._value == other_value

    def __str__(self):
        return self._value

    def __repr__(self):
        return f"<FolderColor value={self._value}>"


class SAFolderColor(sa.TypeDecorator):
    @property
    def python_type(self):
        return FolderColor

    impl = sa.String

    cache_ok = True

    def process_bind_param(self, value: FolderColor, dialect):
        if value:
            return value.value

        return None

    def process_result_value(self, value, dialect):
        if value:
            return FolderColor(value)

        return None
