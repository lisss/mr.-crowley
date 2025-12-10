from deduplicator.normalize import normalize_url
from deduplicator.filter import filter_unique
from storage import Storage


class Deduplicator:
    def __init__(self, storage=None):
        self.storage = storage
        self.seen_key = "crawley:seen"
        if storage is None:
            self._in_memory_seen = set()
        else:
            self._in_memory_seen = None

    def normalize(self, url):
        return normalize_url(url)

    def is_seen(self, url):
        normalized = self.normalize(url)
        if self.storage:
            return self.storage.is_in_set(self.seen_key, normalized)
        return normalized in self._in_memory_seen

    def mark_seen(self, url):
        normalized = self.normalize(url)
        if self.storage:
            self.storage.add_to_set(self.seen_key, normalized)
        else:
            self._in_memory_seen.add(normalized)
        return normalized

    def filter_unique(self, urls):
        return filter_unique(self.storage, self.seen_key, urls, self._in_memory_seen)

    def get_seen_count(self):
        if self.storage:
            return self.storage.get_set_size(self.seen_key)
        return len(self._in_memory_seen)

