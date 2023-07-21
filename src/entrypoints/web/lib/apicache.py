import msgpack
import io
import falcon
import datetime as dt
import logging
from typing import List
from redis import Redis
from src.lib.redis import RedisHelper

logger = logging.getLogger(__name__)


class APICache:
    enabled = True

    invalidate_methods = ["POST", "PATCH", "PUT", "DELETE", "PROPPATCH"]
    cache_methods = ["GET", "PROPFIND", "REPORT"]
    CACHE_HEADER = 'X-WSGILook-Cache'

    API_CACHE_HIT_COUNTER_KEY = "API_CACHE:HIT_COUNTER"
    API_CACHE_MISS_COUNTER_KEY = "API_CACHE:MISS_COUNTER"

    @staticmethod
    def make_cache_key(req: falcon.Request):
        user_id = req.context.get("current_user_id")
        return f"API_CACHE:{req.host}:ORIGIN:{req.get_header('origin')}:USER:{user_id}:{req.relative_uri}:{req.params}"

    @staticmethod
    def _serialize_response(resp: falcon.Response):
        stream = None
        if resp.stream:
            stream = resp.stream.read()
            resp.stream = io.BytesIO(stream)

        value = msgpack.packb(
            [resp.status, resp.content_type, resp.text, stream, resp.headers],
            use_bin_type=True
        )

        return value

    @staticmethod
    def _deserialize_response(resp: falcon.Response, data):
        resp.status, resp.content_type, resp.text, stream, headers = msgpack.unpackb(data, raw=False)
        resp.stream = io.BytesIO(stream) if stream else None
        resp.set_headers(headers)
        resp.complete = True

    @staticmethod
    def cached(
            timeout: int,
            tags_templates: List[str] = None,
            stream_length_restriction: int = 512,
    ):
        if tags_templates is None:
            tags_templates = []

        def decorator(func, *args):
            def wrapper(cls, req, resp, *args, **kwargs):
                if not APICache.enabled:
                    func(cls, req, resp, *args, **kwargs)
                    return

                redis: Redis = req.context["redis"]
                redis_helper: RedisHelper = RedisHelper(redis)
                key = APICache.make_cache_key(req)

                logger.debug(f"APICache used for key: {key}")

                if req.method in APICache.invalidate_methods:
                    redis.delete(key)

                if req.method in APICache.cache_methods:
                    data = redis.get(key)

                    if data:
                        APICache._deserialize_response(resp, data)
                        resp.set_header(APICache.CACHE_HEADER, 'Hit')
                        APICache._increase_hit_counter(redis, key)
                        return
                    else:
                        resp.set_header(APICache.CACHE_HEADER, 'Miss')
                        APICache._increase_miss_counter(redis, key)

                func(cls, req, resp, *args, **kwargs)

                if req.method in APICache.cache_methods:
                    if resp.stream and round(resp.stream.content_length / 1024) > stream_length_restriction:
                        return

                    try:
                        value = APICache._serialize_response(resp)

                        tags = []
                        format_keys = {
                            **req.context,
                            **req.params
                        }

                        for tag in tags_templates:
                            tags.append(tag.format(**format_keys))

                        redis_helper.set_with_tags(key, value, ex=dt.timedelta(seconds=timeout), tags=tags)
                    except Exception as e:
                        logger.error(e)

            return wrapper

        return decorator

    @staticmethod
    def _increase_hit_counter(redis: Redis, key: str):
        try:
            if not redis.exists(APICache.API_CACHE_HIT_COUNTER_KEY):
                redis.set(APICache.API_CACHE_HIT_COUNTER_KEY, 0, ex=dt.timedelta(days=1))

            if not redis.exists(f"{key}:HIT"):
                redis.set(f"{key}:HIT", 0, ex=dt.timedelta(days=1))

            redis.incr(f"{key}:HIT")
            redis.incr(APICache.API_CACHE_HIT_COUNTER_KEY)
        except Exception as e:
            logger.error(e)

    @staticmethod
    def _increase_miss_counter(redis: Redis, key: str):
        try:
            if not redis.exists(APICache.API_CACHE_MISS_COUNTER_KEY):
                redis.set(APICache.API_CACHE_MISS_COUNTER_KEY, 0, ex=dt.timedelta(days=1))

            if not redis.exists(f"{key}:MISS"):
                redis.set(f"{key}:MISS", 0, ex=dt.timedelta(days=1))

            redis.incr(f"{key}:MISS")
            redis.incr(APICache.API_CACHE_MISS_COUNTER_KEY)
        except Exception as e:
            logger.error(e)


class CacheMiddleware:
    @classmethod
    def process_response(cls, req, resp, resource, req_succeeded):
        if not req_succeeded:
            return

        redis: Redis = req.context["redis"]
        key = APICache.make_cache_key(req)

        if req.method in APICache.invalidate_methods:
            redis.delete(key)
