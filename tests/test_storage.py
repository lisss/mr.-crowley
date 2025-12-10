import pytest
import redis

from storage import Storage
from deduplicator import Deduplicator
from frontier import Frontier


@pytest.fixture
def redis_storage():
    try:
        storage = Storage()
        storage.client.ping()
        storage.client.flushdb()
        yield storage
        storage.client.flushdb()
    except (redis.ConnectionError, redis.TimeoutError):
        pytest.skip("Redis not available")


class TestRedisStorage:
    def test_visited_urls_stored_in_redis(self, redis_storage):
        deduplicator = Deduplicator(redis_storage)
        frontier = Frontier("https://crawlme.monzo.com/", deduplicator=deduplicator, storage=redis_storage)

        url = "https://crawlme.monzo.com/page1"
        frontier.mark_visited(url)

        assert redis_storage.is_in_set("crawley:visited", url)
        assert frontier.is_visited(url)

    def test_queue_operations_in_redis(self, redis_storage):
        deduplicator = Deduplicator(redis_storage)
        frontier = Frontier("https://crawlme.monzo.com/", deduplicator=deduplicator, storage=redis_storage)

        urls = ["https://crawlme.monzo.com/page1", "https://crawlme.monzo.com/page2"]
        frontier.add_urls(urls)

        assert redis_storage.get_list_length("crawley:queue") >= 1
        assert redis_storage.is_in_set("crawley:queued", "https://crawlme.monzo.com/page1")

    def test_redis_persistence_across_instances(self, redis_storage):
        deduplicator1 = Deduplicator(redis_storage)
        frontier1 = Frontier("https://crawlme.monzo.com/", deduplicator=deduplicator1, storage=redis_storage)

        url = "https://crawlme.monzo.com/test-page"
        frontier1.mark_visited(url)

        deduplicator2 = Deduplicator(redis_storage)
        frontier2 = Frontier("https://crawlme.monzo.com/", deduplicator=deduplicator2, storage=redis_storage)

        assert frontier2.is_visited(url)
        assert redis_storage.is_in_set("crawley:visited", url)

    def test_deduplication_persists_in_redis(self, redis_storage):
        deduplicator = Deduplicator(redis_storage)
        frontier = Frontier("https://crawlme.monzo.com/", deduplicator=deduplicator, storage=redis_storage)

        urls = ["https://crawlme.monzo.com/page1", "https://crawlme.monzo.com/page1/", "https://crawlme.monzo.com/page2"]
        added = frontier.add_urls(urls)

        assert len(added) == 2
        assert redis_storage.get_set_size("crawley:seen") >= 2

        added_again = frontier.add_urls(urls)
        assert len(added_again) == 0
