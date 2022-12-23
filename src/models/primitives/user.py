import sqlalchemy as sa
import re
from src.models.exc import AttributeValidationError
from copy import deepcopy


class FirstName:
    MAX_LENGTH = 40
    MIN_LENGTH = 2
    PATTERN = r"^[a-zA-Z0-9а-яА-Я-_ ]{2,40}$"

    def __init__(self, value: str):
        if len(value) == 0:
            raise AttributeValidationError("FirstName cannot be empty")

        if len(value) < self.MIN_LENGTH:
            raise AttributeValidationError("FirstName is too short")

        if len(value) > self.MAX_LENGTH:
            raise AttributeValidationError("FirstName is too long")

        regexp = re.compile(self.PATTERN)

        if not bool(regexp.match(value)):
            raise AttributeValidationError("FirstName does not match expected pattern")

        self._value = value

    @property
    def value(self):
        return deepcopy(self._value)

    def __eq__(self, other: 'FirstName'):
        other_value = other.value if type(other) == FirstName else None
        return self._value == other_value

    def __str__(self):
        return self._value

    def __repr__(self):
        return f"<FirstName value={self._value}>"


class SAFirstName(sa.TypeDecorator):
    @property
    def python_type(self):
        return FirstName

    impl = sa.String

    cache_ok = True

    def process_bind_param(self, value: FirstName, dialect):
        if value:
            return value.value

        return None

    def process_result_value(self, value, dialect):
        if value:
            return FirstName(value)

        return None


class LastName:
    MAX_LENGTH = 40
    MIN_LENGTH = 2
    PATTERN = r"^[a-zA-Z0-9а-яА-Я-_ ]{2,40}$"

    def __init__(self, value: str):
        if len(value) == 0:
            raise AttributeValidationError("LastName cannot be empty")

        if len(value) < self.MIN_LENGTH:
            raise AttributeValidationError("LastName is too short")

        if len(value) > self.MAX_LENGTH:
            raise AttributeValidationError("LastName is too long")

        regexp = re.compile(self.PATTERN)

        if not bool(regexp.match(value)):
            raise AttributeValidationError("LastName does not match expected pattern")

        self._value = value

    @property
    def value(self):
        return deepcopy(self._value)

    def __eq__(self, other: 'LastName'):
        other_value = other.value if type(other) == LastName else None
        return self._value == other_value

    def __str__(self):
        return self._value

    def __repr__(self):
        return f"<LastName value={self._value}>"


class SALastName(sa.TypeDecorator):
    @property
    def python_type(self):
        return LastName

    impl = sa.String

    cache_ok = True

    def process_bind_param(self, value: LastName, dialect):
        if value:
            return value.value

        return None

    def process_result_value(self, value, dialect):
        if value:
            return LastName(value)

        return None


class MiddleName:
    MAX_LENGTH = 40
    MIN_LENGTH = 2
    PATTERN = r"^[a-zA-Z0-9а-яА-Я-_ ]{2,40}$"

    def __init__(self, value: str):
        if len(value) == 0:
            raise AttributeValidationError("MiddleName cannot be empty")

        if len(value) < self.MIN_LENGTH:
            raise AttributeValidationError("MiddleName is too short")

        if len(value) > self.MAX_LENGTH:
            raise AttributeValidationError("MiddleName is too long")

        regexp = re.compile(self.PATTERN)

        if not bool(regexp.match(value)):
            raise AttributeValidationError("MiddleName does not match expected pattern")

        self._value = value

    @property
    def value(self):
        return deepcopy(self._value)

    def __eq__(self, other: 'MiddleName'):
        other_value = other.value if type(other) == MiddleName else None
        return self._value == other_value

    def __str__(self):
        return self._value

    def __repr__(self):
        return f"<MiddleName value={self._value}>"


class SAMiddleName(sa.TypeDecorator):
    @property
    def python_type(self):
        return MiddleName

    impl = sa.String

    cache_ok = True

    def process_bind_param(self, value: MiddleName, dialect):
        if value:
            return value.value

        return None

    def process_result_value(self, value, dialect):
        if value:
            return MiddleName(value)

        return None
