import requests


class Fetcher:
    def __init__(self, user_agent="CrawleyBot/1.0"):
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def fetch(self, url):
        try:
            response = self.session.get(url, timeout=10, allow_redirects=True)
            response.raise_for_status()
            final_url = response.url
            return True, response.text, response.status_code, final_url
        except requests.exceptions.RequestException:
            return False, None, None, url

