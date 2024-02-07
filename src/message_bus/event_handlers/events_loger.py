from copy import deepcopy
from typing import Type
from .base import EventHandlerABC
from .. import events
from logging import getLogger
from src.repositories.events_log import EventsLogRepoABC
from src.models.event_log import EventLog

logger = getLogger(__name__)


class EventsLogger(EventHandlerABC):
    def __init__(
            self,
            logs_repo_class: Type[EventsLogRepoABC],
    ):
        super().__init__()
        self._logs_repo_class = logs_repo_class

    def _before_handle(self, context: dict):
        self._db_session = context["db_session"]

    def _handle(self, event: events.Event, context: dict, *args, **kwargs):
        event = deepcopy(event)

        if hasattr(event, "password"):
            event.password = "*******"

        if hasattr(event, "token"):
            event.token = "*******"

        event_log = EventLog(
            user_id=kwargs.get("user_id"),
            object_id=kwargs.get("object_id") or getattr(event, "id", None),
            type=type(event),
            event=event,
            info=kwargs.get("meta"),
        )

        log_repo = self._logs_repo_class.create(self._db_session)

        log_repo.add(event_log)

        self._db_session.commit()

    def _after_handle(self, context: dict):
        self._db_session.close()


class AsyncEventsLogger(EventHandlerABC):
    def __init__(
            self,
            logs_repo_class: Type[EventsLogRepoABC],
    ):
        super().__init__()
        self._logs_repo_class = logs_repo_class

    async def handle(self, event: events.Event, context: dict, *args, **kwargs):
        await self._before_handle(context)
        try:
            await self._handle(event, context=context, *args, **kwargs)
        finally:
            await self._after_handle(context)

    async def _before_handle(self, context: dict):
        self._db_sessionmaker = context["db_sessionmaker"]

    async def _after_handle(self, context: dict):
        pass

    async def _handle(self, event: events.Event, context: dict, *args, **kwargs):
        event = deepcopy(event)

        if hasattr(event, "password"):
            event.password = "*******"

        if hasattr(event, "token"):
            event.token = "*******"

        event_log = EventLog(
            user_id=kwargs.get("user_id"),
            object_id=kwargs.get("object_id") or getattr(event, "id", None),
            type=type(event),
            event=event,
            info=kwargs.get("meta"),
        )

        async with self._db_sessionmaker() as db_session:
            log_repo = self._logs_repo_class.create(db_session)
            log_repo.add(event_log)

            await db_session.commit()
