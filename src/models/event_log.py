import sqlalchemy as sa
from typing import Type, TYPE_CHECKING
from src.models.primitives.base import SAUUID
from sqlalchemy import types
from .meta import Base
from uuid import uuid4, UUID

if TYPE_CHECKING:
    from src.message_bus import Event


class SAEventType(types.TypeDecorator):
    impl = types.String

    def process_bind_param(self, value, dialect):
        return str(value.__name__)

    def process_result_value(self, value, dialect):
        return value

    def process_literal_param(self, value, dialect):
        pass

    @property
    def python_type(self):
        return Event


class SAEvent(types.TypeDecorator):
    impl = types.String

    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value, dialect):
        return value

    def process_literal_param(self, value, dialect):
        pass

    @property
    def python_type(self):
        return Event


class EventLog(Base):
    __tablename__ = "events_log"

    id: UUID = sa.Column(SAUUID, primary_key=True, default=lambda: uuid4())
    user_id: UUID = sa.Column(SAUUID, nullable=True, index=True)
    object_id = sa.Column(sa.String, nullable=True, index=True)
    type: Type['Event'] = sa.Column(SAEventType, nullable=False, index=True)
    event: 'Event' = sa.Column(SAEvent, nullable=False)
    info = sa.Column(sa.String, nullable=True)
    datetime = sa.Column(sa.DateTime, default=sa.func.now())
