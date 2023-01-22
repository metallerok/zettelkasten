from typing import Type
from config import Config
from src.models.meta import session_factory

from .message_bus import MessageBus
from . import events
from src.repositories.events_log import SAEventsLogRepo
from src.message_bus.event_handlers.events_loger import EventsLogger
from src.message_bus.event_handlers.notificators import (
    PasswordChangeRequestEmailNotificator,
    UserPasswordChangedEmailNotificator,
)


def default_events_handlers(config: Type[Config]):
    return {
        events.UserCreated: [EventsLogger(SAEventsLogRepo)],
        events.AuthSessionClosed: [EventsLogger(SAEventsLogRepo)],

        events.PasswordChangeRequestCreated: [
            EventsLogger(SAEventsLogRepo),
            PasswordChangeRequestEmailNotificator(config),
        ],
        events.UserPasswordChanged: [
            EventsLogger(SAEventsLogRepo),
            UserPasswordChangedEmailNotificator(config),
        ],

        events.FolderCreated: [EventsLogger(SAEventsLogRepo)],
        events.FolderUpdated: [EventsLogger(SAEventsLogRepo)],
        events.FolderRemoved: [EventsLogger(SAEventsLogRepo)],

        events.NoteCreated: [EventsLogger(SAEventsLogRepo)],
        events.NoteUpdated: [EventsLogger(SAEventsLogRepo)],
        events.NoteRemoved: [EventsLogger(SAEventsLogRepo)],
    }


def make_message_bus(config: Type[Config]) -> MessageBus:
    message_bus = MessageBus(
        event_handlers=default_events_handlers(config)
    )

    message_bus.context["db_session"] = session_factory(config)()

    return message_bus
