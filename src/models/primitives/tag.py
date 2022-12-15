import sqlalchemy as sa
import re
from src.models.exc import AttributeValidationError
from copy import deepcopy


class TagTitle:
    MAX_LENGTH = 40
    MIN_LENGTH = 3
    PATTERN = r"^[a-zA-Z0-9а-яА-Я_]{3,40}$"

    def __init__(self, value: str):
        if value is None:
            raise AttributeValidationError("TagTitle cannot be None")

        if len(value) == 0:
            raise AttributeValidationError("TagTitle cannot be empty")

        if len(value) < self.MIN_LENGTH:
            raise AttributeValidationError("TagTitle is too short")

        if len(value) > self.MAX_LENGTH:
            raise AttributeValidationError("TagTitle is too long")

        regexp = re.compile(self.PATTERN)

        if not bool(regexp.match(value)):
            raise AttributeValidationError("TagTitle does not match expected pattern")

        self._value = value

    @property
    def value(self):
        return deepcopy(self._value)

    def __eq__(self, other: 'TagTitle'):
        other_value = other.value if type(other) == TagTitle else None
        return self._value == other_value

    def __str__(self):
        return self._value

    def __repr__(self):
        return f"<TagTitle value={self._value}>"


class SATagTitle(sa.TypeDecorator):
    @property
    def python_type(self):
        return TagTitle

    impl = sa.String

    cache_ok = True

    def process_bind_param(self, value: TagTitle, dialect):
        return value.value

    def process_result_value(self, value, dialect):
        return TagTitle(value)
