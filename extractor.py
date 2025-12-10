import sys
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from deduplicator import Deduplicator


class Extractor:
    def __init__(self, allowed_domain=None, deduplicator=None):
        self.allowed_domain = allowed_domain
        self.deduplicator = deduplicator or Deduplicator()

    def _is_allowed_domain(self, url):
        if self.allowed_domain is None:
            return True
        parsed = urlparse(url)
        return parsed.netloc == self.allowed_domain

    def extract(self, html, base_url):
        links = set()
        try:
            soup = BeautifulSoup(html, "html.parser")
            for anchor in soup.find_all("a", href=True):
                href = anchor["href"]
                absolute_url = urljoin(base_url, href)
                normalized = self.deduplicator.normalize(absolute_url)
                if self._is_allowed_domain(normalized):
                    links.add(normalized)
        except Exception as e:
            print(f"  Error parsing HTML: {e}", file=sys.stderr)
        return sorted(links)

