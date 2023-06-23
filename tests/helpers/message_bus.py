from typing import List, Dict, Union, Callable, Type
from src.message_bus import MessageBusABC, events, commands
from src.message_bus.types import Message
from src.message_bus.event_handlers.base import EventHandlerABC
from src.message_bus.command_handlers.base import CommandHandlerABC


class DryRunMessageBus(MessageBusABC):
    def __init__(
        self,
        event_handlers: Dict[Type[events.Event], List[Union[Callable, EventHandlerABC]]] = None,
        command_handlers: Dict[Type[commands.Command], Union[Callable, CommandHandlerABC]] = None,
    ):
        self.messages = []

        if event_handlers:
            self._event_handlers = event_handlers
        else:
            self._event_handlers = dict()

        if command_handlers:
            self._command_handlers = command_handlers
        else:
            self._command_handlers = dict()

    def set_event_handlers(self, event: Type[events.Event], handlers: List[Union[Callable, EventHandlerABC]]):
        self._event_handlers[event] = handlers

    def set_command_handler(self, cmd: Type[commands.Command], handler: Union[Callable, CommandHandlerABC]):
        self._command_handlers[cmd] = handler

    def get_event_handlers(
            self,
            event: Type[events.Event],
    ) -> List[Union[Callable, EventHandlerABC]]:
        return self._event_handlers[event]

    def get_command_handler(
            self,
            command: Type[commands.Command],
    ) -> CommandHandlerABC:
        return self._command_handlers[commands]

    def handle(self, message: Message, *args, **kwargs):
        handlers = []
        message_desc = {}
        if isinstance(message, events.Event):
            message_desc = {
                "message": message,
                "args": args,
                "kwargs": kwargs,
            }

            for handler in self._event_handlers[type(message)]:
                handlers.append(handler)

        elif isinstance(message, commands.Command):
            message_desc = {
                "message": message,
                "args": args,
                "kwargs": kwargs,
            }

            for handler in self._command_handlers[type(message)]:
                handlers.append(handler)
        else:
            raise Exception(f"{message} was not an Event or Command type")

        message_desc["handlers"] = handlers
        self.messages.append(message_desc)
