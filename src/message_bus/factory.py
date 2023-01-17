from typing import Type
from config import Config
from src.models.meta import session_factory

from .message_bus import MessageBus
from . import events
from src.repositories.events_log import SAEventsLogRepo
from src.message_bus.event_handlers.events_loger import EventsLogger


def default_events_handlers(config: Type[Config]):
    return {
        events.TestEvent: [EventsLogger(SAEventsLogRepo)],
        events.AuthSessionClosed: [EventsLogger(SAEventsLogRepo)],

        events.FolderCreated: [EventsLogger(SAEventsLogRepo)],
        events.FolderUpdated: [EventsLogger(SAEventsLogRepo)],
        events.FolderRemoved: [EventsLogger(SAEventsLogRepo)],
    }


def make_message_bus(config: Type[Config]) -> MessageBus:
    message_bus = MessageBus(
        event_handlers=default_events_handlers(config)
    )

    message_bus.context["db_session"] = session_factory(config)()

    return message_bus
