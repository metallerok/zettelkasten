import os
import falcon
import falcon.asgi
import venusian
import logging

from typing import Type

from config import Config
from src.message_bus import make_message_bus, MessageBusABC

from src.entrypoints.web.async_middleware.database import DatabaseMiddleware
from src.entrypoints.web.async_middleware.config_middleware import ConfigMiddleware
from src.entrypoints.web.async_middleware.encode import EncodeMiddleware
from src.entrypoints.web.async_middleware.auth_middleware import AuthMiddleware
from src.entrypoints.web.async_middleware.message_bus import MessageBudsMiddleware
from .middleware.cors_middleware import CORSMiddleware

from src.models.meta import async_session_factory, Base

from src.entrypoints.web.errors.base import (
    async_no_result_found_handler,
    async_validation_error_handler,
    async_base_exception,
)

from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from src import models
from src import schemas
from src.entrypoints.web import api


class AppLogFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = ''
        return True


def make_app(
        config: Type[Config] = Config,
        message_bus: MessageBusABC = None,
) -> falcon.asgi.App:
    _init_environment(config)

    if not message_bus:
        message_bus = make_message_bus(config)

    db_sessionmaker, db_engine = async_session_factory(config)
    Base.metadata.bind = db_engine

    middlewares = [
        ConfigMiddleware(config),
        DatabaseMiddleware(config, db_engine, db_sessionmaker),
        MessageBudsMiddleware(message_bus),
        AuthMiddleware(config),
        EncodeMiddleware(),
    ]

    if config.is_cors_enable:
        middlewares.append(
            CORSMiddleware(allow_origins=config.allow_origins, allow_credentials=config.allow_credentials)
        )

    app = falcon.asgi.App(
        middleware=middlewares,
    )

    app.add_error_handler(ValidationError, async_validation_error_handler)
    app.add_error_handler(NoResultFound, async_no_result_found_handler)
    app.add_error_handler(Exception, async_base_exception)

    venusian.Scanner().scan(schemas)
    venusian.Scanner(api=app).scan(api)

    os.environ['PYTHON_EGG_CACHE'] = os.path.dirname(os.path.abspath(__file__)) + '/.cache'

    return app


def _init_environment(config: Type[Config]):
    root_logger = logging.getLogger()
    root_logger.addFilter(AppLogFilter())
    logger = logging.getLogger(__name__)
    logger.format = logging.Formatter(config.logger_format)
    logger.setLevel(config.log_level)

    venusian.Scanner().scan(models)
