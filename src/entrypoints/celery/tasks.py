from typing import List, Any
from sqlalchemy.orm import Session
from .decorators import db_session_dec
from .app import app
from config import Config
from logging import getLogger
import dataclasses_serialization
from src.message_bus.event_handlers.base import EventHandlerABC
from src.message_bus import MessageBusABC, MessageBus, events, commands
from src.message_bus.factory import default_events_handlers

logger = getLogger(__name__)


@app.task
@db_session_dec()
def process_message_bus_event(db_session: Session, event_name: str, serialized_data: dict, *args, **kwargs):
    try:
        event_type: events.Event = getattr(events, event_name)
    except AttributeError:
        logger.error(f"Wrong event type: {event_name}")
        return

    try:
        event = event_type.deserialize(serialized_data)
    except dataclasses_serialization.serializer_base.errors.DeserializationError as e:
        logger.exception(e)
        return

    message_bus = MessageBus(
        event_handlers=default_events_handlers(Config)
    )
    message_bus.context["db_session"] = db_session

    _handle_event(event, message_bus, *args, **kwargs)


def _handle_event(
        event: events.Event,
        message_bus: MessageBusABC,
        *args, **kwargs
) -> List[Any]:
    results = []

    for handler in message_bus.get_event_handlers(type(event)):
        logger.debug(f"Handling  event {event} with handler {handler}")

        try:
            if issubclass(type(handler), EventHandlerABC):
                handler.handle(event, context=message_bus.context, *args, **kwargs)

                for message in handler.emitted_messages:
                    if type(message) == events.Event:
                        process_message_bus_event.s(
                            event_name=type(message).__name__,
                            serialized_data=message.serialize(),
                        ).apply_async(queue="events")
                    if type(message) == commands.Command:
                        message_bus.handle(message)
            else:
                handler(event, context=message_bus.context, *args, **kwargs)

        except Exception as e:
            logger.exception(f"Error handling event {event}", exc_info=e)
            continue

    return results
