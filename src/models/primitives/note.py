import sqlalchemy as sa
import re
from src.models.exc import AttributeValidationError
from copy import deepcopy


class NoteTitle:
    MAX_LENGTH = 60
    MIN_LENGTH = 3
    PATTERN = r"^[a-zA-Z0-9а-яА-Я-_() ]{3,60}$"

    def __init__(self, value: str):
        if value is None:
            raise AttributeValidationError("NoteTitle cannot be None")

        if len(value) == 0:
            raise AttributeValidationError("NoteTitle cannot be empty")

        if len(value) < self.MIN_LENGTH:
            raise AttributeValidationError("NoteTitle is too short")

        if len(value) > self.MAX_LENGTH:
            raise AttributeValidationError("NoteTitle is too long")

        regexp = re.compile(self.PATTERN)

        if not bool(regexp.match(value)):
            raise AttributeValidationError("NoteTitle does not match expected pattern")

        self._value = value

    @property
    def value(self):
        return deepcopy(self._value)

    def __eq__(self, other: 'NoteTitle'):
        other_value = other.value if type(other) == NoteTitle else None
        return self._value == other_value

    def __str__(self):
        return self._value

    def __repr__(self):
        return f"<NoteTitle value={self._value}>"


class SANoteTitle(sa.TypeDecorator):
    @property
    def python_type(self):
        return NoteTitle

    impl = sa.String

    cache_ok = True

    def process_bind_param(self, value: NoteTitle, dialect):
        return value.value

    def process_result_value(self, value, dialect):
        return NoteTitle(value)


class NoteColor:
    MIN_LENGTH = 4
    MAX_LENGTH = 7
    PATTERN = r"^#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$"

    def __init__(self, value: str):
        if len(value) < self.MIN_LENGTH:
            raise AttributeValidationError("NoteColor is too short")

        if len(value) > self.MAX_LENGTH:
            raise AttributeValidationError("NoteColor is too long")

        regexp = re.compile(self.PATTERN)

        if not bool(regexp.match(value)):
            raise AttributeValidationError("NoteColor does not match expected pattern")

        self._value = value

    @property
    def value(self):
        return deepcopy(self._value)

    def __eq__(self, other: 'NoteColor'):
        other_value = other.value if type(other) == NoteColor else None
        return self._value == other_value

    def __str__(self):
        return self._value

    def __repr__(self):
        return f"<NoteColor value={self._value}>"


class SANoteColor(sa.TypeDecorator):
    @property
    def python_type(self):
        return NoteColor

    impl = sa.String

    cache_ok = True

    def process_bind_param(self, value: NoteColor, dialect):
        if value:
            return value.value

        return None

    def process_result_value(self, value, dialect):
        if value:
            return NoteColor(value)

        return None
