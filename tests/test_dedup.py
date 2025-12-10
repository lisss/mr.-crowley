import pytest

from deduplicator import Deduplicator
from frontier import Frontier


class TestDeduplication:
    def test_url_normalization_removes_trailing_slash(self):
        deduplicator = Deduplicator()
        assert deduplicator.normalize("https://crawlme.monzo.com/page/") == deduplicator.normalize(
            "https://crawlme.monzo.com/page"
        )

    def test_filter_unique_removes_duplicates(self):
        deduplicator = Deduplicator()
        urls = [
            "https://crawlme.monzo.com/page1",
            "https://crawlme.monzo.com/page1/",
            "https://crawlme.monzo.com/page2",
            "https://crawlme.monzo.com/page1",
        ]

        unique = deduplicator.filter_unique(urls)
        assert len(unique) == 2

    def test_frontier_deduplicates_and_prevents_re_adding(self):
        frontier = Frontier("https://crawlme.monzo.com/")
        urls = [
            "https://crawlme.monzo.com/page1",
            "https://crawlme.monzo.com/page1/",
            "https://crawlme.monzo.com/page2",
        ]

        added = frontier.add_urls(urls)
        assert len(added) == 2

        frontier.mark_visited("https://crawlme.monzo.com/page1")
        added_again = frontier.add_urls(urls)
        assert len(added_again) == 0


# LISS >>> keeping as test for now, but ideally, we need to create a monitoring on that
class TestDeduplicationRate:
    def test_duplicate_rate_increases_with_overlapping_links(self):
        deduplicator = Deduplicator()
        frontier = Frontier("https://crawlme.monzo.com/", deduplicator=deduplicator)

        common_links = [
            "https://crawlme.monzo.com/about.html",
            "https://crawlme.monzo.com/contact.html",
            "https://crawlme.monzo.com/products.html",
        ]

        page1_links = common_links + ["https://crawlme.monzo.com/page1.html"]
        page2_links = common_links + ["https://crawlme.monzo.com/page2.html"]
        page3_links = common_links + ["https://crawlme.monzo.com/page3.html"]

        added1 = frontier.add_urls(page1_links, current_level=0)
        assert len(added1) == 4

        added2 = frontier.add_urls(page2_links, current_level=0)
        assert len(added2) == 1

        added3 = frontier.add_urls(page3_links, current_level=0)
        assert len(added3) == 1

        duplicate_rate_page2 = (len(page2_links) - len(added2)) / len(page2_links)
        duplicate_rate_page3 = (len(page3_links) - len(added3)) / len(page3_links)

        assert duplicate_rate_page2 > 0.5
        assert duplicate_rate_page3 > 0.5
        assert duplicate_rate_page3 >= duplicate_rate_page2

    def test_deduplication_rate_remains_sensible_with_high_overlap(self):
        deduplicator = Deduplicator()
        frontier = Frontier("https://crawlme.monzo.com/", deduplicator=deduplicator)

        base_links = [f"https://crawlme.monzo.com/link{i}" for i in range(10)]

        total_extracted = 0
        total_added = 0

        for i in range(10):
            page_links = base_links + [f"https://crawlme.monzo.com/new{i}"]
            total_extracted += len(page_links)
            added = frontier.add_urls(page_links, current_level=0)
            total_added += len(added)

        duplicate_rate = (total_extracted - total_added) / total_extracted

        assert duplicate_rate > 0.7
        assert duplicate_rate < 0.95
