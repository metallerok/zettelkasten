import abc
from typing import List
from src.message_bus import commands
from src.message_bus.types import Message


class CommandHandlerABC(abc.ABC):
    def __init__(self):
        self._emitted_messages = []

    @abc.abstractmethod
    def handle(self, cmd: commands.Command, context: dict, *args, **kwargs):
        pass

    def emmit_message(self, message: Message):
        self._emitted_messages.append(message)

    @property
    def emitted_messages(self) -> List[Message]:
        return self._emitted_messages
