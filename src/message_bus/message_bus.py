import abc
import logging
from typing import Union, List, Type, Dict, Callable, Any, Tuple
import asyncio
from . import events
from . import commands
from .event_handlers.base import EventHandlerABC
from .command_handlers.base import CommandHandlerABC
from .types import Message

logger = logging.getLogger(__name__)


class MessageBusABC(abc.ABC):
    context = {}

    @abc.abstractmethod
    def set_event_handlers(
            self,
            event: Type[events.Event],
            handlers: List[Union[Callable, EventHandlerABC]],
    ):
        pass

    @abc.abstractmethod
    def get_event_handlers(
            self,
            event: Type[events.Event],
    ) -> List[Union[Callable, EventHandlerABC]]:
        pass

    @abc.abstractmethod
    def set_command_handler(
            self,
            cmd: Type[commands.Command],
            handler: Union[Callable, CommandHandlerABC],
    ):
        pass

    @abc.abstractmethod
    def get_command_handler(
            self,
            command: Type[commands.Command],
    ) -> CommandHandlerABC:
        pass

    @abc.abstractmethod
    def handle(self, message: Message, *args, **kwargs):
        pass

    def batch_handle(self, messages: List[Message], *args, **kwargs):
        for message in messages:
            self.handle(message, *args, **kwargs)


class MessageBus(MessageBusABC):
    def __init__(
            self,
            event_handlers: Dict[Type[events.Event], List[Union[Callable, EventHandlerABC]]] = None,
            command_handlers: Dict[Type[commands.Command], Union[Callable, CommandHandlerABC]] = None,
    ):
        if event_handlers:
            self._event_handlers = event_handlers
        else:
            self._event_handlers = dict()

        if command_handlers:
            self._command_handlers = command_handlers
        else:
            self._command_handlers = dict()

        self.context = {}

    def set_event_handlers(
            self,
            event: Type[events.Event],
            handlers: List[Union[Callable, EventHandlerABC]]
    ):
        self._event_handlers[event] = handlers

    def get_event_handlers(
            self,
            event: Type[events.Event],
    ) -> List[Union[Callable, EventHandlerABC]]:
        return self._event_handlers[event]

    def get_command_handler(
            self,
            command: Type[commands.Command],
    ) -> CommandHandlerABC:
        return self._command_handlers[command]

    def set_command_handler(
            self,
            cmd: Type[commands.Command],
            handler: Union[Callable, CommandHandlerABC],
    ):
        self._command_handlers[cmd] = handler

    def handle(self, message: Message, *args, **kwargs) -> List:
        results = []
        queue = [message]

        while queue:
            message = queue.pop(0)

            if isinstance(message, events.Event):
                events_results = self._handle_event(message, queue, *args, **kwargs)
                results.extend(events_results)
            elif isinstance(message, commands.Command):
                result = self._handle_command(message, queue, *args, **kwargs)
                results.append(result)
            else:
                raise Exception(f"{message} was not an Event or Command type")

        return results

    def _handle_event(
            self,
            event: events.Event,
            queue: List[Message],
            *args, **kwargs
    ) -> List[Any]:
        results = []

        try:
            handlers = self._event_handlers[type(event)]
        except KeyError:
            logger.error(f"Event handlers for {type(event)} does not exist")
            return results

        for handler in handlers:
            logger.debug(f"Handling  event {event} with handler {handler}")

            try:
                if issubclass(type(handler), EventHandlerABC):
                    result = handler.handle(event, context=self.context, *args, **kwargs)
                    queue.extend(handler.emitted_messages)
                else:
                    result = handler(event, context=self.context, *args, **kwargs)

                results.append({
                    "event": event,
                    "result": result
                })
            except Exception as e:
                logger.exception(f"Error handling event {event}", exc_info=e)
                continue

        return results

    def _handle_command(
            self,
            cmd: commands.Command,
            queue: List[Message],
            *args, **kwargs
    ) -> Any:
        logger.debug(f"Handling command {cmd}")

        try:
            handler = self._command_handlers[type(cmd)]

            if issubclass(type(handler), CommandHandlerABC):
                result = handler.handle(cmd, context=self.context, *args, **kwargs)
                queue.extend(handler.emitted_messages)
            else:
                result = handler(cmd, context=self.context, *args, **kwargs)
        except Exception as e:
            logger.exception(f"Error handling command {cmd}", exc_info=e)
            raise

        return {
            "command": cmd,
            "result": result,
        }


class AsyncMessageBus(MessageBusABC):
    def __init__(
            self,
            event_handlers: Dict[Type[events.Event], List[Union[Callable, EventHandlerABC]]] = None,
            command_handlers: Dict[Type[commands.Command], Union[Callable, CommandHandlerABC]] = None,
    ):
        if event_handlers:
            self._event_handlers = event_handlers
        else:
            self._event_handlers = dict()

        if command_handlers:
            self._command_handlers = command_handlers
        else:
            self._command_handlers = dict()

        self.context = {}

    def set_event_handlers(
            self,
            event: Type[events.Event],
            handlers: List[Union[Callable, EventHandlerABC]]
    ):
        self._event_handlers[event] = handlers

    def set_command_handler(
            self,
            cmd: Type[commands.Command],
            handler: Union[Callable, CommandHandlerABC],
    ):
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
        return self._command_handlers[command]

    async def batch_handle(self, messages: List[Message], *args, **kwargs):
        for message in messages:
            await self.handle(message, *kwargs, **kwargs)

    async def handle(self, message: Message, *args, **kwargs) -> List:
        results = []
        queue = [message]

        while queue:
            message = queue.pop(0)

            if isinstance(message, events.Event):
                events_results = await self._handle_event(message, queue, *args, **kwargs)
                results.extend(events_results)
            elif isinstance(message, commands.Command):
                result = self._handle_command(message, queue, *args, **kwargs)
                results.append(result)
            else:
                raise Exception(f"{message} was not an Event or Command type")

        return results

    async def _handle_event(
            self,
            event: events.Event,
            queue: List[Message],
            *args, **kwargs
    ) -> Tuple[Any]:
        coroutines = []

        try:
            handlers = self._event_handlers[type(event)]
        except KeyError:
            logger.error(f"Event handlers for {type(event)} does not exist")
            return tuple()

        for handler in handlers:
            logger.debug(f"Handling event {event} with handler {handler}")

            try:
                if issubclass(type(handler), EventHandlerABC):
                    coroutine = handler.handle(event, context=self.context, *args, **kwargs)
                    coroutines.append(coroutine)
                    queue.extend(handler.emitted_messages)
                else:
                    coroutine = handler(event, context=self.context, *args, **kwargs)
                    coroutines.append(coroutine)

            except Exception as e:
                logger.exception(f"Error handling event {event}", exc_info=e)
                continue

        results = await asyncio.gather(*coroutines)

        if "db_session" in self.context:
            self.context["db_session"].close()

        return results

    def _handle_command(
            self,
            cmd: commands.Command,
            queue: List[Message],
            *args, **kwargs
    ) -> Any:
        logger.debug(f"Handling command {cmd}")

        try:
            handler = self._command_handlers[type(cmd)]

            if issubclass(type(handler), CommandHandlerABC):
                result = handler.handle(cmd, context=self.context, *args, **kwargs)
                queue.extend(handler.emitted_messages)
            else:
                result = handler(cmd, context=self.context, *args, **kwargs)
        except Exception as e:
            logger.exception(f"Error handling command {cmd}", exc_info=e)
            raise

        return result
