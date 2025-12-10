from collections import deque
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

from deduplicator import Deduplicator
from storage import Storage


class Frontier:
    def __init__(
        self,
        start_url,
        user_agent="CrawleyBot/1.0",
        deduplicator=None,
        storage=None,
        max_level=None,
    ):
        self.storage = storage
        self.max_level = max_level
        self.visited_key = "crawley:visited"
        self.queued_key = "crawley:queued"
        self.queue_key = "crawley:queue"
        self.level_key = "crawley:level"

        self.deduplicator = deduplicator or Deduplicator(storage)
        normalized_start = self.deduplicator.normalize(start_url)
        self.deduplicator.mark_seen(normalized_start)

        if self.storage:
            queue_length = self.storage.get_list_length(self.queue_key)
            if queue_length == 0:
                if not self.storage.is_in_set(self.visited_key, normalized_start):
                    if not self.storage.is_in_set(self.queued_key, normalized_start):
                        self.storage.add_to_list(self.queue_key, normalized_start)
                        self.storage.add_to_set(self.queued_key, normalized_start)
                        self.storage.client.hset(self.level_key, normalized_start, 0)
            self._in_memory_to_visit = None
            self._in_memory_queued = None
            self._in_memory_visited = None
            self._url_levels = None
        else:
            self._in_memory_to_visit = deque([(normalized_start, 0)])
            self._in_memory_queued = {normalized_start}
            self._in_memory_visited = set()
            self._url_levels = {normalized_start: 0}

        self.robots_parser = None
        self.user_agent = user_agent
        parsed = urlparse(start_url)
        self.base_scheme = parsed.scheme
        self.base_netloc = parsed.netloc
        self._load_robots_txt()

    def _load_robots_txt(self):
        try:
            robots_url = f"{self.base_scheme}://{self.base_netloc}/robots.txt"
            session = requests.Session()
            session.headers.update({"User-Agent": self.user_agent})
            response = session.get(robots_url, timeout=5)
            if response.status_code == 200 and not response.text.strip().startswith("<?xml"):
                self.robots_parser = RobotFileParser()
                self.robots_parser.set_url(robots_url)
                self.robots_parser.read()
            else:
                self.robots_parser = None
        except Exception:
            self.robots_parser = None

    def has_next(self):
        if self.storage:
            return self.storage.get_list_length(self.queue_key) > 0
        return len(self._in_memory_to_visit) > 0

    def get_next(self):
        if not self.has_next():
            return None, None
        if self.storage:
            url = self.storage.pop_from_list(self.queue_key)
            if url:
                self.storage.remove_from_set(self.queued_key, url)
                level_str = self.storage.client.hget(self.level_key, url)
                if level_str:
                    level = int(level_str.decode() if isinstance(level_str, bytes) else level_str)
                else:
                    if self.max_level is not None:
                        level = self.max_level + 1
                    else:
                        level = 0
                return url, level
            return None, None
        url, level = self._in_memory_to_visit.popleft()
        self._in_memory_queued.discard(url)
        return url, level

    def is_visited(self, url):
        normalized = self.deduplicator.normalize(url)
        if self.storage:
            return self.storage.is_in_set(self.visited_key, normalized)
        return normalized in self._in_memory_visited

    def mark_visited(self, url):
        normalized = self.deduplicator.normalize(url)
        if self.storage:
            self.storage.add_to_set(self.visited_key, normalized)
        else:
            self._in_memory_visited.add(normalized)
        self.deduplicator.mark_seen(normalized)
        return normalized

    def is_allowed(self, url):
        if self.robots_parser is None:
            return True
        return self.robots_parser.can_fetch(self.user_agent, url)

    def add_urls(self, urls, current_level=0):
        if self.max_level is not None and current_level >= self.max_level:
            return []

        unique_urls = self.deduplicator.filter_unique(urls)
        added = []
        next_level = current_level + 1

        if self.max_level is not None and next_level > self.max_level:
            return []

        if self.storage:
            if not unique_urls:
                return added

            pipe = self.storage.pipeline()
            for url in unique_urls:
                pipe.sismember(self.visited_key, url)
                pipe.sismember(self.queued_key, url)
            results = pipe.execute()

            to_add = []
            pipe = self.storage.pipeline()
            for i, url in enumerate(unique_urls):
                visited = results[i * 2]
                queued = results[i * 2 + 1]
                if not visited and not queued:
                    to_add.append(url)
                    pipe.rpush(self.queue_key, url)
                    pipe.sadd(self.queued_key, url)
                    pipe.hset(self.level_key, url, next_level)

            if to_add:
                pipe.execute()
                added = to_add
                for url in to_add:
                    if len(self.storage._queued_cache) < self.storage._cache_size_limit:
                        self.storage._queued_cache.add(url)
        else:
            for url in unique_urls:
                if not self.is_visited(url) and not self._is_queued(url):
                    self._in_memory_to_visit.append((url, next_level))
                    self._in_memory_queued.add(url)
                    self._url_levels[url] = next_level
                    added.append(url)
        return added

    def _is_queued(self, url):
        if self.storage:
            return self.storage.is_in_set(self.queued_key, url)
        return url in self._in_memory_queued

    def get_visited_count(self):
        if self.storage:
            return self.storage.get_set_size(self.visited_key)
        return len(self._in_memory_visited)
