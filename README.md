# Crawley

![Crawley](./crowley.jpg)

A web crawler with a simple web interface. Start crawls, watch progress, and see what URLs were visited.

## Features

- Web UI to start and stop crawls
- Set starting URL, user agent, allowed domain, and crawl depth
- See pages crawled, warnings, queue size
- View visited URLs grouped by patterns
- Optional Redis storage
- Live logs

## Setup

```bash
pip install -r requirements.txt
npm install
npm run build
python web.py
```

Open `http://localhost:5002` in your browser.

## How to Use

Enter a URL to start crawling. You can set:
- User agent string
- Allowed domain (only crawl this domain)
- Crawl depth level (0 = just the start URL)
- Enable Redis storage if you want

Watch the metrics, logs, and visited URLs update as it crawls.
