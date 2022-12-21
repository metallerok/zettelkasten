from src.message_bus import MessageBusABC


class MessageBusMiddleware:
    def __init__(self, message_bus: MessageBusABC):
        self._message_bus = message_bus

    def process_request(self, req, resp):
        req.context["message_bus"] = self._message_bus
