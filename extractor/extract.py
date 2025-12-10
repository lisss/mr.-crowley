import sys
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from deduplicator.deduplicator import Deduplicator


def extract_links(html, base_url, allowed_domain, deduplicator):
    links = set()
    try:
        soup = BeautifulSoup(html, "html.parser")
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            absolute_url = urljoin(base_url, href)
            normalized = deduplicator.normalize(absolute_url)
            from extractor.domain import is_allowed_domain
            if is_allowed_domain(normalized, allowed_domain):
                links.add(normalized)
    except Exception as e:
        print(f"  Error parsing HTML: {e}", file=sys.stderr)
    return sorted(links)

