import pytest
from unittest.mock import Mock, patch

from deduplicator import Deduplicator
from extractor import Extractor
from frontier import Frontier


class TestArchitecture:
    def test_services_integrate_correctly(self):
        deduplicator = Deduplicator()
        frontier = Frontier("https://crawlme.monzo.com/", deduplicator=deduplicator)
        extractor = Extractor("crawlme.monzo.com", deduplicator)

        html = '<html><body><a href="/page1">Link 1</a><a href="/page2">Link 2</a></body></html>'
        links = extractor.extract(html, "https://crawlme.monzo.com/")
        assert len(links) == 2

        added = frontier.add_urls(links)
        assert len(added) == 2
        assert frontier.has_next()

    def test_fetcher_handles_successful_request(self):
        from fetcher import Fetcher

        fetcher = Fetcher()

        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.text = "<html>Test</html>"
            mock_response.status_code = 200
            mock_response.url = "https://crawlme.monzo.com/"
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            success, html, status, url = fetcher.fetch("https://crawlme.monzo.com/")
            assert success is True
            assert html == "<html>Test</html>"
            assert status == 200

    def test_fetcher_handles_failed_request(self):
        from fetcher import Fetcher
        import requests

        fetcher = Fetcher()

        with patch("requests.Session.get") as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Connection error")

            success, html, status, url = fetcher.fetch("https://crawlme.monzo.com/")
            assert success is False
            assert html is None
            assert status is None

    def test_extractor_filters_by_domain(self):
        deduplicator = Deduplicator()
        extractor = Extractor("crawlme.monzo.com", deduplicator)

        html = '<html><body><a href="https://crawlme.monzo.com/page1">Same</a><a href="https://other.com/page">Other</a></body></html>'
        links = extractor.extract(html, "https://crawlme.monzo.com/")

        assert len(links) == 1
        assert "https://crawlme.monzo.com/page1" in links
        assert "https://other.com/page" not in links
