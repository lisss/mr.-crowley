import os
import redis
from typing import Set


class Storage:
    def __init__(self, redis_host=None, redis_port=None, redis_db=0, redis_password=None):
        self.redis_host = redis_host or os.getenv("REDIS_HOST", "localhost")
        self.redis_port = redis_port or int(os.getenv("REDIS_PORT", "6379"))
        self.redis_db = redis_db
        self.redis_password = redis_password or os.getenv("REDIS_PASSWORD")
        self.client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
            password=self.redis_password,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            socket_keepalive=True,
            socket_keepalive_options={},
        )
        self._visited_cache = set()
        self._queued_cache = set()
        self._cache_size_limit = 10000

    def add_to_set(self, key: str, value: str) -> bool:
        result = self.client.sadd(key, value) > 0
        if key == "crawley:visited" and len(self._visited_cache) < self._cache_size_limit:
            self._visited_cache.add(value)
        elif key == "crawley:queued" and len(self._queued_cache) < self._cache_size_limit:
            self._queued_cache.add(value)
        return result

    def is_in_set(self, key: str, value: str) -> bool:
        if key == "crawley:visited" and value in self._visited_cache:
            return True
        if key == "crawley:queued" and value in self._queued_cache:
            return True
        result = self.client.sismember(key, value)
        if (
            result
            and key == "crawley:visited"
            and len(self._visited_cache) < self._cache_size_limit
        ):
            self._visited_cache.add(value)
        elif (
            result and key == "crawley:queued" and len(self._queued_cache) < self._cache_size_limit
        ):
            self._queued_cache.add(value)
        return result

    def get_set_size(self, key: str) -> int:
        return self.client.scard(key)

    def add_to_list(self, key: str, value: str):
        self.client.rpush(key, value)

    def add_to_list_batch(self, key: str, values: list):
        if values:
            self.client.rpush(key, *values)

    def pop_from_list(self, key: str) -> str:
        return self.client.lpop(key)

    def get_list_length(self, key: str) -> int:
        return self.client.llen(key)

    def remove_from_set(self, key: str, value: str):
        self.client.srem(key, value)
        if key == "crawley:queued":
            self._queued_cache.discard(value)

    def get_all_from_set(self, key: str) -> Set[str]:
        return self.client.smembers(key)

    def pipeline(self):
        return self.client.pipeline()
