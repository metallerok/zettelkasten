from typing import Type
from config import Config


class ConfigMiddleware:
    def __init__(self, config: Type[Config]):
        self._config = config

    def process_request(self, req, resp):
        req.context["config"] = self._config
