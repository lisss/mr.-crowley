import argparse
import sys
from urllib.parse import urlparse

from crawler import Crawley


def main():
    parser = argparse.ArgumentParser(
        description="A simple web crawler that crawls pages on a single subdomain."
    )
    parser.add_argument(
        "url", nargs="?", help="Starting URL to crawl (e.g., https://crawlme.monzo.com/)"
    )
    parser.add_argument(
        "--user-agent",
        default="CrawleyBot/1.0",
        help="User agent string for HTTP requests (default: CrawleyBot/1.0)",
    )
    parser.add_argument(
        "--allowed-domain",
        default=None,
        help="Domain to allow crawling (default: same as starting URL domain)",
    )
    parser.add_argument(
        "--use-storage",
        action="store_true",
        help="Enable Redis storage (default: in-memory for speed)",
    )
    parser.add_argument(
        "--level",
        type=int,
        default=None,
        help="Maximum crawl depth level (0 = start URL only, 1 = start URL + direct links, etc.)",
    )
    parser.add_argument(
        "--clear-storage",
        action="store_true",
        help="Clear Redis storage before starting crawl",
    )

    args = parser.parse_args()

    if not args.url:
        parser.print_help()
        sys.exit(0)

    parsed = urlparse(args.url)
    if not parsed.scheme or not parsed.netloc:
        print(f"Error: Invalid URL: {args.url}", file=sys.stderr)
        sys.exit(1)

    crawler = Crawley(
        args.url,
        args.user_agent,
        args.allowed_domain,
        use_storage=args.use_storage,
        max_level=args.level,
        clear_storage=args.clear_storage,
    )
    crawler.crawl()


if __name__ == "__main__":
    main()
