import abc
from typing import List
from src.message_bus import events
from src.message_bus.types import Message


class EventHandlerABC(abc.ABC):
    def __init__(self):
        self._emitted_messages = []

    @abc.abstractmethod
    def _handle(self, event: events.Event, context: dict, *args, **kwargs):
        pass

    def handle(self, event: events.Event, context: dict, *args, **kwargs):
        self._before_handle(context)
        try:
            self._handle(event, context=context, *args, **kwargs)
        finally:
            self._after_handle(context)

    def _before_handle(self, context: dict):
        pass

    def _after_handle(self, context: dict):
        pass

    def emmit_message(self, message: Message):
        self._emitted_messages.append(message)

    @property
    def emitted_messages(self) -> List[Message]:
        return self._emitted_messages
