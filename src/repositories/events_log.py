import abc
from typing import TYPE_CHECKING
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio.session import AsyncSession

if TYPE_CHECKING:
    from src.models.event_log import EventLog


class EventsLogRepoABC(abc.ABC):
    @abc.abstractmethod
    def add(self, event_log: 'EventLog'):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def create(cls, *args, **kwargs):
        return cls()


class SAEventsLogRepo(EventsLogRepoABC):
    def __init__(self, db_session: Session):
        self._db_session = db_session

    @classmethod
    def create(cls, db_session: Session) -> 'SAEventsLogRepo':
        return cls(db_session)

    def add(self, event_log: 'EventLog'):
        self._db_session.add(event_log)


class AsyncSAEventsLogRepo(EventsLogRepoABC):

    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    @classmethod
    def create(cls, db_session: AsyncSession) -> 'AsyncSAEventsLogRepo':
        return cls(db_session)

    def add(self, event_log: 'EventLog'):
        self._db_session.add(event_log)
