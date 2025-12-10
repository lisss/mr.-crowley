# System Overview

Flow:
```
Browser UI
   |
   v
Flask API (web.py / api/index.py)
   |
   | spawn subprocess
   v
Crawler (crawler.py) --> Redis (visited, queued)
             ^
             |
      Fetch visited URLs for UI
```

Notes:
- Web UI (React) calls Flask endpoints for crawl control, logs, visited URLs.
- Flask starts the crawler as a subprocess; crawler writes to Redis.
- When Redis is not configured, falls back to in-memory (testing only).

