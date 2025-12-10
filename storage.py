import os
import redis
from typing import Set


class Storage:
    def __init__(self, redis_host=None, redis_port=None, redis_db=0, redis_password=None):
        redis_url_env = os.getenv("REDIS_URL")
        redis_host_env = (os.getenv("REDIS_HOST", "localhost") or "").strip()
        allow_in_memory = bool(
            os.getenv("ALLOW_IN_MEMORY_REDIS")
            or os.getenv("PYTEST_CURRENT_TEST")
            or os.getenv("CI")
        )

        # In-memory stub for tests/CI when no Redis is configured
        class InMemoryRedis:
            def __init__(self):
                self.sets = {}
                self.lists = {}
                self.hashes = {}

            def sadd(self, key, value):
                s = self.sets.setdefault(key, set())
                before = len(s)
                s.add(value)
                return 1 if len(s) > before else 0

            def sismember(self, key, value):
                return value in self.sets.get(key, set())

            def scard(self, key):
                return len(self.sets.get(key, set()))

            def smembers(self, key):
                return set(self.sets.get(key, set()))

            def srem(self, key, value):
                return (
                    1
                    if value in self.sets.get(key, set()) and not self.sets[key].discard(value)
                    else 0
                )

            def rpush(self, key, *values):
                lst = self.lists.setdefault(key, [])
                lst.extend(values)

            def lpop(self, key):
                lst = self.lists.get(key, [])
                return lst.pop(0) if lst else None

            def llen(self, key):
                return len(self.lists.get(key, []))

            def hgetall(self, key):
                return self.hashes.get(key, {}).copy()

            def hset(self, key, field, value):
                self.hashes.setdefault(key, {})[field] = value

            def exists(self, key):
                return key in self.hashes

            def hlen(self, key):
                return len(self.hashes.get(key, {}))

            def ping(self):
                return True

        # Fallback to in-memory for tests if no real credentials
        if not redis_url_env and (redis_host_env in ("", "your-redis-host")) and allow_in_memory:
            self.client = InMemoryRedis()
            self.redis_host = "in-memory"
            self.redis_port = 0
            self.redis_db = 0
            self.redis_password = None
            self._visited_cache = set()
            self._queued_cache = set()
            self._cache_size_limit = 10000
            return

        if not redis_url_env and (redis_host_env in ("", "your-redis-host")):
            raise ValueError(
                "Redis credentials not configured! "
                "Set REDIS_HOST, REDIS_PASSWORD (or REDIS_URL) using: "
                "flyctl secrets set REDIS_HOST=your-host REDIS_PASSWORD=your-password"
            )

        if redis_url_env:
            use_ssl = os.getenv("REDIS_SSL", "false").lower() in ("true", "1", "yes")
            connection_kwargs = {
                "decode_responses": True,
                "socket_connect_timeout": 10,
                "socket_timeout": 10,
                "socket_keepalive": True,
                "retry_on_timeout": True,
                "health_check_interval": 30,
            }

            if use_ssl:
                import ssl

                ssl_context = ssl.SSLContext()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                connection_kwargs["ssl_cert_reqs"] = ssl.CERT_NONE

            self.client = redis.from_url(redis_url_env, **connection_kwargs)
            parsed = redis.from_url(
                redis_url_env, decode_responses=False
            ).connection_pool.connection_kwargs
            self.redis_host = parsed.get("host", "unknown")
            self.redis_port = parsed.get("port", 6379)
        else:
            self.redis_host = redis_host or os.getenv("REDIS_HOST", "localhost")
            self.redis_port = redis_port or int(os.getenv("REDIS_PORT", "6379"))
            self.redis_db = redis_db
            redis_password_env = redis_password or os.getenv("REDIS_PASSWORD")
            self.redis_password = redis_password_env if redis_password_env else None

            use_ssl = os.getenv("REDIS_SSL", "false").lower() in ("true", "1", "yes")

            connection_kwargs = {
                "host": self.redis_host,
                "port": self.redis_port,
                "db": self.redis_db,
                "decode_responses": True,
                "socket_connect_timeout": 10,
                "socket_timeout": 10,
                "socket_keepalive": True,
                "socket_keepalive_options": {},
                "retry_on_timeout": True,
                "health_check_interval": 30,
            }

            if self.redis_password:
                connection_kwargs["password"] = self.redis_password

            if use_ssl:
                import ssl

                ssl_context = ssl.SSLContext()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                connection_kwargs["ssl"] = True
                connection_kwargs["ssl_cert_reqs"] = ssl.CERT_NONE

            self.client = redis.Redis(**connection_kwargs)
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
