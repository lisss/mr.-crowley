from urllib.parse import urlparse


def is_allowed_domain(url, allowed_domain):
    if allowed_domain is None:
        return True
    parsed = urlparse(url)
    return parsed.netloc == allowed_domain

