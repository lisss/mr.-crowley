from urllib.parse import urlparse

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
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        if normalized.endswith("/") and len(parsed.path) > 1:
            normalized = normalized[:-1]
        return normalized

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
        seen_in_list = set()
        unique = []
        if self.storage:
            normalized_urls = []
            for url in urls:
                normalized = self.normalize(url)
                if normalized not in seen_in_list:
                    seen_in_list.add(normalized)
                    normalized_urls.append(normalized)

            if normalized_urls:
                pipe = self.storage.pipeline()
                for normalized in normalized_urls:
                    pipe.sismember(self.seen_key, normalized)
                results = pipe.execute()

                pipe = self.storage.pipeline()
                for i, normalized in enumerate(normalized_urls):
                    if not results[i]:
                        unique.append(normalized)
                        pipe.sadd(self.seen_key, normalized)
                if unique:
                    pipe.execute()
        else:
            for url in urls:
                normalized = self.normalize(url)
                if not self.is_seen(normalized) and normalized not in seen_in_list:
                    seen_in_list.add(normalized)
                    unique.append(normalized)
                    self.mark_seen(normalized)
        return unique

    def get_seen_count(self):
        if self.storage:
            return self.storage.get_set_size(self.seen_key)
        return len(self._in_memory_seen)
