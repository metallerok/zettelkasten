from sqlalchemy.dialects.postgresql import UUID as sa_uuid_type
from sqlalchemy import types
import uuid
from src.models.exc import AttributeValidationError


class SAUUID(types.TypeDecorator):
    impl = sa_uuid_type
    cache_ok = True

    def __init__(self):
        types.TypeDecorator.__init__(self)

    def process_bind_param(self, value, dialect=None):
        if value and isinstance(value, uuid.UUID):
            return str(value)
        elif value and not isinstance(value, uuid.UUID):
            print(value, type(value))
            raise AttributeValidationError('Not a valid uuid.UUID')
        else:
            return None

    def process_result_value(self, value, dialect=None):
        if value:
            return uuid.UUID(value)
        else:
            return None
