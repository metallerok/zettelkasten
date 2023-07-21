import logging
import os
import falcon
import redis
from typing import Type
from depot.manager import DepotManager
from sqlalchemy.orm import Session
from config import Config
from .middleware import (
    SADBSessionMiddleware,
    EncodeMiddleware,
    LoggingMiddleware,
    RedisMiddleware,
    MessageBusMiddleware,
    ConfigMiddleware,
)
from src.entrypoints.web.middleware.auth_middleware import AuthMiddleware
from .middleware.depot_middleware import DepotMiddleware
from src.entrypoints.web.lib.apicache import CacheMiddleware
from src.models.meta import session_factory
from src import models
from src.entrypoints.web import api
from .errors.base import (
    validation_error_handler,
    no_result_found_handler,
)

from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError
from src.message_bus import make_message_bus, MessageBusABC
import venusian


class AppLogFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = ''
        return True


def make_app(
        config: Type[Config] = Config,
        message_bus: MessageBusABC = None,
        depot: DepotManager = None,
) -> falcon.App:
    _init_environment(config)
    # cache = _init_cache(config)

    if not depot:
        depot = _init_file_storage(config)

    db_session = _make_db_session(config)
    redis_ = _make_redis_conn(config)

    if not message_bus:
        message_bus = make_message_bus(config)

    middlewares = [
        ConfigMiddleware(config),
        DepotMiddleware(depot),
        RedisMiddleware(redis_),
        CacheMiddleware(),
        AuthMiddleware(db_session, config),
        EncodeMiddleware(),
        LoggingMiddleware(config),
        SADBSessionMiddleware(db_session),
        MessageBusMiddleware(message_bus),
    ]

    if config.is_cors_enabled:
        middlewares.append(
            falcon.CORSMiddleware(allow_origins='*', allow_credentials='*')
        )

    app = falcon.App(
        middleware=middlewares,
    )

    app.add_error_handler(ValidationError, validation_error_handler)
    app.add_error_handler(NoResultFound, no_result_found_handler)

    venusian.Scanner().scan(models)
    venusian.Scanner(api=app).scan(api)

    os.environ['PYTHON_EGG_CACHE'] = os.path.dirname(os.path.abspath(__file__)) + '/.cache'

    return app


def _init_file_storage(config: Type[Config]):
    return DepotManager.configure(
        "default",
        {'depot.storage_path': config.file_storage}
    )


def _init_environment(config: Type[Config]):
    root_logger = logging.getLogger()
    root_logger.addFilter(AppLogFilter())
    logger = logging.getLogger(__name__)
    logger.format = logging.Formatter(config.logger_format)
    logger.setLevel(config.log_level)


def _make_db_session(config: Type[Config]) -> Session:
    session = session_factory(config)()

    return session


def _make_redis_conn(config: Type[Config]) -> redis.Redis:
    redis_conn_poll = redis.ConnectionPool(
        host=config.redis_host,
        port=config.redis_port,
        db=config.redis_db,
        password=config.redis_password,
        socket_connect_timeout=10,
    )
    redis_conn = redis.StrictRedis(connection_pool=redis_conn_poll)

    return redis_conn
