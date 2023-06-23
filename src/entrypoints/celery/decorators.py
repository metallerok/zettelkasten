import functools
import logging
import redis

from config import Config
from src.models.meta import session_factory

logger = logging.getLogger(__name__)


def db_session_dec():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            db_session = session_factory(Config)(expire_on_commit=False)

            try:
                value = func(db_session=db_session, *args, **kwargs)

                return value
            except Exception as e:
                logger.debug("db rollback")
                db_session.rollback()
                logger.exception(e)
            finally:
                logger.debug("db_session closed")
                db_session.close()

        return wrapper
    return decorator


def redis_conn_dec():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            r_conn = redis.Redis(
                host=Config.redis_host, port=Config.redis_port,
                db=Config.redis_db, password=Config.redis_password,
            )

            try:
                value = func(redis_conn=r_conn, *args, **kwargs)

                return value
            finally:
                r_conn.close()

        return wrapper
    return decorator
