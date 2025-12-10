from crawler.init import init_crawler
from crawler.crawl import run_crawl


class Crawley:
    def __init__(
        self,
        start_url,
        user_agent="CrawleyBot/1.0",
        allowed_domain=None,
        use_storage=False,
        max_level=None,
        clear_storage=False,
    ):
        self.components = init_crawler(
            start_url, user_agent, allowed_domain, use_storage, max_level, clear_storage
        )
        self.start_url = start_url
        self.max_level = max_level

    def crawl(self):
        run_crawl(self.components)

