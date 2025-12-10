import pytest
from unittest.mock import Mock, patch

from crawler import Crawley
from frontier import Frontier


class TestLevel:
    def test_level_0_only_processes_start_url(self):
        frontier = Frontier("https://crawlme.monzo.com/", max_level=0)
        
        url, level = frontier.get_next()
        assert url == "https://crawlme.monzo.com/"
        assert level == 0
        
        assert not frontier.has_next()

    def test_level_1_adds_direct_links(self):
        frontier = Frontier("https://crawlme.monzo.com/", max_level=1)
        
        url, level = frontier.get_next()
        assert level == 0
        
        links = [
            "https://crawlme.monzo.com/page1",
            "https://crawlme.monzo.com/page2",
        ]
        added = frontier.add_urls(links, current_level=0)
        assert len(added) == 2
        
        url1, level1 = frontier.get_next()
        assert level1 == 1
        
        url2, level2 = frontier.get_next()
        assert level2 == 1

    def test_level_prevents_adding_urls_beyond_max_level(self):
        frontier = Frontier("https://crawlme.monzo.com/", max_level=1)
        
        links = ["https://crawlme.monzo.com/page1"]
        added = frontier.add_urls(links, current_level=0)
        assert len(added) == 1
        
        added_beyond = frontier.add_urls(links, current_level=1)
        assert len(added_beyond) == 0

    def test_level_0_crawls_only_start_url(self):
        with patch("crawley.Fetcher") as mock_fetcher_class, patch("crawley.Extractor") as mock_extractor_class:
            mock_fetcher = Mock()
            mock_fetcher.fetch.return_value = (True, "<html><body><a href='/page1'>Link</a></body></html>", 200, "https://crawlme.monzo.com/")
            mock_fetcher_class.return_value = mock_fetcher
            
            mock_extractor = Mock()
            mock_extractor.extract.return_value = ["https://crawlme.monzo.com/page1"]
            mock_extractor_class.return_value = mock_extractor
            
            crawley = Crawley("https://crawlme.monzo.com/", max_level=0)
            
            from io import StringIO
            import sys
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            try:
                crawley.crawl()
                output = sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout
            
            assert "Visited (level 0)" in output
            assert output.count("Visited (level 0)") == 1
            assert "Visited (level 1)" not in output

