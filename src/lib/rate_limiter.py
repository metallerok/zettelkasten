import abc
import time
import logging
from redis import Redis, ConnectionError

logger = logging.getLogger(__name__)


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

        try:
            if self._check_reset_interval(last_reset_key, interval):
                self._reset_counter(counter_key, last_reset_key, max_requests, interval)
            else:
                if self._check_counter_value(counter_key) is False:
                    return False

            self._decrement_counter(counter_key)

            return True
        except ConnectionError as e:
            logger.exception(e)
            return False

    def _check_reset_interval(self, last_reset_key: str, interval: int) -> bool:
        last_reset_time = self._get_last_reset_time(last_reset_key)
        now = int(time.time())

        return (now - last_reset_time) >= interval

    def _get_last_reset_time(self, key: str) -> int:
        last_reset_time = self._redis.get(key)

        return int(last_reset_time or 0)

    def _check_counter_value(self, counter_key: str) -> bool:
        counter_value = self._get_counter_value(counter_key)
        return counter_value > 0

    def _get_counter_value(self, counter_key: str) -> int:
        counter_value = self._redis.get(counter_key)
        return int(counter_value or 0)

    def _decrement_counter(self, counter_key: str):
        self._redis.decr(counter_key)

    def _reset_counter(self, counter_key: str, last_reset_key: str, max_requests: int, interval: int):
        self._redis.set(counter_key, max_requests, ex=interval)
        self._redis.set(last_reset_key, int(time.time()), ex=interval)
