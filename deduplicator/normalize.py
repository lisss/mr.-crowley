from urllib.parse import urlparse


def normalize_url(url):
    parsed = urlparse(url)
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    if normalized.endswith("/") and len(parsed.path) > 1:
        normalized = normalized[:-1]
    return normalized

