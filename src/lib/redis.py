import datetime as dt
from redis import Redis
from typing import Optional, Dict, Set, Union
from redis.client import Pipeline


class RedisHelper:
    def __init__(self, connection: Redis):
        self._redis = connection

    @staticmethod
    def tag_prefix(tag: str, prefix: str = "tag") -> str:
        separator = ""
        if prefix:
            separator = ":"
        return "{prefix}{separator}{tag}".format(
            prefix=prefix,
            tag=tag,
            separator=separator
        )

    @staticmethod
    def get_keys_ttl(
            keys: list,
            pipe: Optional[Pipeline]
    ) -> Dict[str, int]:
        try:
            pipe.multi()
            for key in keys:
                pipe.ttl(key)
            res = pipe.execute()
            keys_ttl = {}
            for index, key_ttl in enumerate(res):
                keys_ttl[keys[index]] = key_ttl

            return keys_ttl
        except Exception as e:
            raise e
        finally:
            pipe.reset()

    def set_with_tags(
            self,
            key: str,
            value: Union[str, bytes],
            tags: list,
            ex: Optional[dt.timedelta] = None,
            tag_prefix: str = "tag",
    ) -> None:
        with self._redis.pipeline() as pipe:
            tags = [self.tag_prefix(tag, tag_prefix) for tag in tags]
            tags_ttl = self.get_keys_ttl(tags, pipe)

            pipe.multi()
            pipe.set(key, value, ex)
            for tag in tags:
                pipe.sadd(tag, key)
                if ex is not None and ex.total_seconds() > tags_ttl[tag]:
                    pipe.expire(tag, ex)
            pipe.execute()

    def get_by_tag(self, tag: str, tag_prefix: str = "tag") -> Set[Union[str, bytes]]:
        tag = self.tag_prefix(tag, tag_prefix)
        return self._redis.smembers(tag)

    def delete_by_tag(self, tag: str, tag_prefix: str = "tag") -> Set[str]:
        tag = self.tag_prefix(tag, tag_prefix)
        with self._redis.pipeline() as pipe:
            pipe.multi()
            members = self.get_by_tag(tag, tag_prefix="")
            if len(members) > 0:
                self._redis.delete(*members)
            self._redis.delete(tag)
            pipe.execute()

        return members

    def delete_namespace(self, pattern: str) -> None:
        chunk_size = 5000
        cursor = '0'
        while cursor != 0:
            cursor, keys = self._redis.scan(cursor=cursor, match=pattern, count=chunk_size)
            if keys:
                self._redis.delete(*keys)

    def hset_multiply(
            self,
            name: str,
            dict_: Dict[str, str],
            ex: Optional[dt.timedelta] = None
    ) -> None:
        with self._redis.pipeline() as pipe:
            pipe.multi()
            for key, value in dict_.items():
                pipe.hset(name, key, value)
            if ex is not None:
                pipe.expire(name, ex)
            pipe.execute()
