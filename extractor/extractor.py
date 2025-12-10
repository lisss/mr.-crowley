from extractor.extract import extract_links
from extractor.domain import is_allowed_domain
from deduplicator.deduplicator import Deduplicator


class Extractor:
    def __init__(self, allowed_domain=None, deduplicator=None):
        self.allowed_domain = allowed_domain
        self.deduplicator = deduplicator or Deduplicator()

    def _is_allowed_domain(self, url):
        return is_allowed_domain(url, self.allowed_domain)

    def extract(self, html, base_url):
        return extract_links(html, base_url, self.allowed_domain, self.deduplicator)

