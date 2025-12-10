from urllib.parse import urlparse
from frontier.queue import init_queue, has_next, get_next, add_urls
from frontier.robots import load_robots_txt, is_allowed
from frontier.visited import is_visited, mark_visited, get_visited_count
from deduplicator.deduplicator import Deduplicator
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

        self._in_memory_to_visit, self._in_memory_queued, self._in_memory_visited, self._url_levels = init_queue(
            self.storage, self.deduplicator, normalized_start, self.max_level
        )

        parsed = urlparse(start_url)
        self.base_scheme = parsed.scheme
        self.base_netloc = parsed.netloc
        self.user_agent = user_agent
        self.robots_parser = load_robots_txt(self.base_scheme, self.base_netloc, self.user_agent)

    def has_next(self):
        return has_next(self.storage, self._in_memory_to_visit)

    def get_next(self):
        return get_next(self.storage, self._in_memory_to_visit, self._in_memory_queued, self.max_level)

    def is_visited(self, url):
        return is_visited(self.storage, self.deduplicator, url, self.visited_key, self._in_memory_visited)

    def mark_visited(self, url):
        return mark_visited(self.storage, self.deduplicator, url, self.visited_key, self._in_memory_visited)

    def is_allowed(self, url):
        return is_allowed(self.robots_parser, self.user_agent, url)

    def add_urls(self, urls, current_level=0):
        return add_urls(
            self.storage, self.deduplicator, urls, current_level, self.max_level,
            self.visited_key, self.queued_key, self.queue_key, self.level_key,
            self._in_memory_to_visit, self._in_memory_queued, self._in_memory_visited
        )

    def get_visited_count(self):
        return get_visited_count(self.storage, self.visited_key, self._in_memory_visited)

