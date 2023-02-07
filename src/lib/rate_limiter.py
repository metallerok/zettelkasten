import abc
import time
from redis import Redis


class TokenBucketRateLimiterABC(abc.ABC):
    @abc.abstractmethod
    def rate_limit(self, token: str, interval: int, max_requests: int) -> bool:
        raise NotImplementedError


class RedisTokenBucketRateLimiter(TokenBucketRateLimiterABC):
    def __init__(self, redis: Redis):
        self._redis = redis

    def rate_limit(self, token: str, interval: int, max_requests: int) -> bool:
        counter_key = f"rate_limit:{token}_counter"
        last_reset_key = f"rate_limit:{token}_last_reset"

        last_reset_time = self._get_last_reset_time(last_reset_key)

        now = int(time.time())

        if (now - last_reset_time) >= interval:
            self._reset_counter(counter_key, last_reset_key, max_requests, interval)
        else:
            counter = self._redis.get(counter_key)

            if counter is None:
                self._reset_counter(counter_key, last_reset_key, max_requests, interval)
                counter = max_requests

            if int(counter) <= 0:
                return False

        self._redis.decr(counter_key)

        return True

    def _get_last_reset_time(self, key: str) -> int:
        last_reset_time = self._redis.get(key)

        if last_reset_time is None:
            last_reset_time = 0

        return int(last_reset_time)

    def _reset_counter(self, counter_key: str, last_reset_key: str, max_requests: int, interval: int):
        self._redis.set(counter_key, max_requests, ex=interval)
        self._redis.set(last_reset_key, int(time.time()), ex=interval)
