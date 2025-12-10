import sys
import time


def run_crawl(components):
    f = sys.stdout
    frontier = components['frontier']
    deduplicator = components['deduplicator']
    fetcher = components['fetcher']
    extractor = components['extractor']
    start_url = components['start_url']
    max_level = components['max_level']

    start_time = time.time()
    f.write(f"Starting crawl from: {start_url}\n")
    f.write(f"Domain: {frontier.base_netloc}\n")
    if max_level is not None:
        f.write(f"Max depth: {max_level}\n")
    f.write("\n")

    while frontier.has_next():
        url, level = frontier.get_next()

        if url is None:
            continue

        if max_level is not None and level > max_level:
            continue

        if frontier.is_visited(url):
            continue

        normalized_url = deduplicator.normalize(url)

        if not frontier.is_allowed(normalized_url):
            f.write(f"Skipping (robots.txt): {normalized_url}\n")
            frontier.mark_visited(normalized_url)
            continue

        normalized_url = frontier.mark_visited(normalized_url)
        f.write(f"Visited (level {level}): {normalized_url}\n")

        success, html, status_code, final_url = fetcher.fetch(normalized_url)

        if not success:
            f.write(f"Failed to fetch: {normalized_url}\n")
            if status_code:
                f.write(f"  Status code: {status_code}\n")
            frontier.mark_visited(normalized_url)
            continue

        if final_url != normalized_url:
            final_normalized = deduplicator.normalize(final_url)
            if frontier.is_visited(final_normalized):
                continue
            normalized_url = frontier.mark_visited(final_normalized)
            f.write(f"Visited (level {level}): {normalized_url}\n")

        links = extractor.extract(html, normalized_url)
        frontier.add_urls(links, level)

    elapsed_time = time.time() - start_time
    f.write(
        f"\nCrawl complete. Visited {frontier.get_visited_count()} pages in {elapsed_time:.2f} seconds.\n"
    )

