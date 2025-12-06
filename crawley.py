import os
import sys
import time
from urllib.parse import urlparse

from deduplicator import Deduplicator
from extractor import Extractor
from fetcher import Fetcher
from frontier import Frontier
from storage import Storage


class Crawley:
    def __init__(
        self,
        start_url,
        user_agent="CrawleyBot/1.0",
        allowed_domain=None,
        use_storage=False,
        max_level=None,
    ):
        parsed = urlparse(start_url)
        if allowed_domain is None:
            allowed_domain = parsed.netloc

        self.storage = None
        if use_storage:
            try:
                self.storage = Storage()
                self.storage.client.ping()
            except Exception as e:
                print(
                    f"Warning: Could not connect to Redis: {e}. Using in-memory storage.",
                    file=sys.stderr,
                )
                self.storage = None

        self.deduplicator = Deduplicator(self.storage)
        self.fetcher = Fetcher(user_agent)
        self.frontier = Frontier(start_url, user_agent, self.deduplicator, self.storage, max_level)
        self.extractor = Extractor(allowed_domain, self.deduplicator)
        self.user_agent = user_agent
        self.start_url = start_url
        self.max_level = max_level

    def crawl(self):
        f = sys.stdout

        start_time = time.time()
        f.write(f"Starting crawl from: {self.start_url}\n")
        f.write(f"Domain: {self.frontier.base_netloc}\n")
        if self.max_level is not None:
            f.write(f"Max depth: {self.max_level}\n")
        f.write("\n")

        while self.frontier.has_next():
            url, level = self.frontier.get_next()

            if url is None:
                continue

            if self.max_level is not None and level > self.max_level:
                continue

            if self.frontier.is_visited(url):
                continue

            normalized_url = self.deduplicator.normalize(url)

            if not self.frontier.is_allowed(normalized_url):
                f.write(f"Skipping (robots.txt): {normalized_url}\n")
                self.frontier.mark_visited(normalized_url)
                continue

            normalized_url = self.frontier.mark_visited(normalized_url)
            f.write(f"Visited (level {level}): {normalized_url}\n")

            success, html, status_code, final_url = self.fetcher.fetch(normalized_url)

            if not success:
                f.write(f"Failed to fetch: {normalized_url}\n")
                if status_code:
                    f.write(f"  Status code: {status_code}\n")
                self.frontier.mark_visited(normalized_url)
                continue

            if final_url != normalized_url:
                final_normalized = self.deduplicator.normalize(final_url)
                if self.frontier.is_visited(final_normalized):
                    continue
                normalized_url = self.frontier.mark_visited(final_normalized)
                f.write(f"Visited (level {level}): {normalized_url}\n")

            links = self.extractor.extract(html, normalized_url)
            added = self.frontier.add_urls(links, level)

        elapsed_time = time.time() - start_time
        f.write(
            f"\nCrawl complete. Visited {self.frontier.get_visited_count()} pages in {elapsed_time:.2f} seconds.\n"
        )
