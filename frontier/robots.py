from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import requests


def load_robots_txt(base_scheme, base_netloc, user_agent):
    try:
        robots_url = f"{base_scheme}://{base_netloc}/robots.txt"
        session = requests.Session()
        session.headers.update({"User-Agent": user_agent})
        response = session.get(robots_url, timeout=5)
        if response.status_code == 200 and not response.text.strip().startswith("<?xml"):
            parser = RobotFileParser()
            parser.set_url(robots_url)
            parser.read()
            return parser
        return None
    except Exception:
        return None


def is_allowed(robots_parser, user_agent, url):
    if robots_parser is None:
        return True
    return robots_parser.can_fetch(user_agent, url)

