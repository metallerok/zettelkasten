import msgpack
import io
import falcon
import datetime as dt
from redis import Redis
from src.models.user import User


class Cache:
    invalidate_methods = ["POST", "PATCH", "PUT", "DELETE", "PROPPATCH"]
    cache_methods = ["GET", "PROPFIND", "REPORT"]
    CACHE_HEADER = 'X-WSGILook-Cache'

    @staticmethod
    def make_cache_key(req: falcon.Request):
        current_user: User = req.context["current_user"]
        user_id = current_user.id if current_user else None
        return f"API_CACHE:{req.host}:USER:{user_id}:{req.relative_uri}:{req.params}"

    @staticmethod
    def _serialize_response(resp: falcon.Response):
        stream = None
        if resp.stream:
            stream = resp.stream.read()
            resp.stream = io.BytesIO(stream)

        value = msgpack.packb(
            [resp.status, resp.content_type, resp.text, stream],
            use_bin_type=True
        )

        return value

    @staticmethod
    def _deserialize_response(resp: falcon.Response, data):
        resp.status, resp.content_type, resp.text, stream = msgpack.unpackb(data, raw=False)
        resp.stream = io.BytesIO(stream) if stream else None
        resp.complete = True

    @staticmethod
    def cached(timeout: int):
        def decorator(func, *args):
            def wrapper(cls, req, resp, *args, **kwargs):
                redis: Redis = req.context["redis"]
                key = Cache.make_cache_key(req)

                if req.method in Cache.invalidate_methods:
                    redis.delete(key)

                if req.method in Cache.cache_methods:
                    data = redis.get(key)

                    if data:
                        Cache._deserialize_response(resp, data)
                        resp.set_header(Cache.CACHE_HEADER, 'Hit')
                        return
                    else:
                        resp.set_header(Cache.CACHE_HEADER, 'Miss')

                func(cls, req, resp, *args, **kwargs)

                if req.method in Cache.cache_methods:
                    value = Cache._serialize_response(resp)
                    redis.set(key, value, ex=dt.timedelta(seconds=timeout))

            return wrapper

        return decorator


class CacheMiddleware:
    @classmethod
    def process_response(cls, req, resp, resource, req_succeeded):
        if not req_succeeded:
            return

        redis: Redis = req.context["redis"]
        key = Cache.make_cache_key(req)

        if req.method in Cache.invalidate_methods:
            redis.delete(key)
