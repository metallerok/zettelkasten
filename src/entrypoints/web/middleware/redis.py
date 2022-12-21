from redis import Redis


class RedisMiddleware:
    def __init__(self, redis: Redis):
        self._redis = redis

    def process_request(self, req, resp):
        req.context["redis"] = self._redis
