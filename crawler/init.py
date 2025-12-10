import os
import sys
from urllib.parse import urlparse

from deduplicator.deduplicator import Deduplicator
from extractor.extractor import Extractor
from fetcher import Fetcher
from frontier.frontier import Frontier
from storage import Storage


def init_crawler(start_url, user_agent, allowed_domain, use_storage, max_level, clear_storage):
    parsed = urlparse(start_url)
    if allowed_domain is None:
        allowed_domain = parsed.netloc

    storage = None
    if use_storage:
        try:
            storage = Storage()
            storage.client.ping()
            if clear_storage:
                keys = [
                    "crawley:visited",
                    "crawley:queued",
                    "crawley:queue",
                    "crawley:level",
                    "crawley:seen",
                ]
                for key in keys:
                    storage.client.delete(key)
                print("Cleared Redis storage.", file=sys.stdout)
        except Exception as e:
            print(
                f"Warning: Could not connect to Redis: {e}. Using in-memory storage.",
                file=sys.stderr,
            )
            storage = None

    deduplicator = Deduplicator(storage)
    fetcher = Fetcher(user_agent)
    frontier = Frontier(start_url, user_agent, deduplicator, storage, max_level)
    extractor = Extractor(allowed_domain, deduplicator)

    return {
        'storage': storage,
        'deduplicator': deduplicator,
        'fetcher': fetcher,
        'frontier': frontier,
        'extractor': extractor,
        'user_agent': user_agent,
        'start_url': start_url,
        'max_level': max_level,
    }

