# Crawley

![Crawley](crowley.jpg)

A simple web crawler that crawls all pages on a given subdomain.

## Features

- Crawls all pages on a single subdomain (e.g., `crawlme.monzo.com`)
- Does not follow external links to other domains or subdomains
- Prints each visited URL and the links found on that page
- Respects robots.txt
- Handles redirects and normalizes URLs
- Avoids infinite loops by tracking visited URLs
- Persistent storage using Redis (with in-memory fallback)
- Dockerized services for easy deployment

## Installation

Set up a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python crawler.py <starting_url>
```

### Example

```bash
python crawler.py https://crawlme.monzo.com/
```

The crawler will:
1. Start from the given URL
2. Visit each page on the same subdomain
3. Print each URL visited along with the links found on that page
4. Continue until all pages on the subdomain have been visited

### Quick Testing with Depth Limit

To test the crawler quickly without running a full crawl, use the `--level` option:

```bash
# Only crawl the start URL
python crawler.py https://crawlme.monzo.com/ --level 0

# Crawl start URL + links un to level N
python crawler.py https://crawlme.monzo.com/ --level N
```

### Options

- `--user-agent`: Specify a custom user agent string (default: `CrawleyBot/1.0`)
- `--allowed-domain`: Specify a domain to allow crawling (default: same as starting URL domain)
- `--use-storage`: Enable Redis storage (default: in-memory for speed)
- `--level`: Maximum crawl depth level (0 = start URL only, 1 = start URL + direct links, etc.). Useful for quick testing without running a full crawl.

## Docker Usage

The project includes Docker support with separate services for Redis and the crawler.

### Prerequisites

- Docker and Docker Compose installed

### Running with Docker Compose

```bash
# Build/rebuild the Docker image (required after code changes)
docker-compose build

# Start all services (Redis, crawler, and Redis UI)
docker-compose up -d

# Access Redis Web UI at http://localhost:8081
# Browse all crawl data in your browser!

# Run the crawler manually
docker exec -it crawley-crawler python crawler.py https://crawlme.monzo.com/ --use-storage

# Or with custom options (e.g., limit crawl depth to 2 levels for quick testing)
docker exec -it crawley-crawler python crawler.py https://crawlme.monzo.com/ --use-storage --level 2

# Or with multiple custom options
docker exec -it crawley-crawler python crawler.py https://crawlme.monzo.com/ --use-storage --user-agent "MyBot/1.0" --level 3
```

### Running Individual Services

```bash
# Build the crawler image
docker build -t crawley .

# Run Redis container
docker run -d --name crawley-redis -p 6379:6379 -v redis-data:/data redis:7-alpine redis-server --appendonly yes

# Run crawler container (keeps running, waiting for commands)
docker run -d --name crawley-crawler --link crawley-redis:redis -e REDIS_HOST=redis -e REDIS_PORT=6379 crawley

# Execute crawler command
docker exec -it crawley-crawler python crawler.py https://crawlme.monzo.com/ --use-storage

# Or with depth limit for quick testing
docker exec -it crawley-crawler python crawler.py https://crawlme.monzo.com/ --use-storage --level 2
```

## Storage

The crawler uses Redis for persistent storage by default:
- **Visited URLs**: Stored in Redis set `crawley:visited`
- **Queued URLs**: Stored in Redis set `crawley:queued`
- **URL Queue**: Stored in Redis list `crawley:queue`
- **Seen URLs**: Stored in Redis set `crawley:seen`

If Redis is unavailable, the crawler automatically falls back to in-memory storage.

### Redis Configuration

Set environment variables to configure Redis connection:
- `REDIS_HOST`: Redis host (default: `localhost`)
- `REDIS_PORT`: Redis port (default: `6379`)
- `REDIS_PASSWORD`: Redis password (optional, required for most hosted Redis services)

### Accessing Redis Data

#### Web UI (Recommended)

A Redis web UI is available at http://localhost:8081 when using Docker Compose:

```bash
# Start all services including Redis UI
docker-compose up -d

# Access the web UI in your browser
# Open http://localhost:8081
```

The web UI allows you to:
- Browse all Redis keys
- View sets, lists, and hashes
- Search and filter data
- Monitor Redis operations

#### Redis CLI

To inspect data via command line:

```bash
# Access Redis CLI
docker exec -it crawley-redis redis-cli

# Check existing keys
KEYS "*"

# View visited URLs count
SCARD crawley:visited

# View queued URLs count
SCARD crawley:queued

# View queue length
LLEN crawley:queue

# View seen URLs count
SCARD crawley:seen

# Get sample visited URLs
SMEMBERS crawley:visited | head -10

# Get sample queued URLs
LRANGE crawley:queue 0 9
```

## CI/CD

This project uses GitHub Actions for continuous integration. The CI workflow:

- Runs on push and pull requests to `main`, `master`, and `develop` branches
- Tests against Python 3.11
- Sets up Redis service for integration tests
- Runs all tests with pytest
- Checks for Python syntax errors

See `.github/workflows/ci.yml` for details.

## Implementation Details

- Uses `requests` for HTTP requests
- Uses `beautifulsoup4` for HTML parsing
- Uses Python's standard library `urllib.parse` for URL handling
- Implements its own crawling logic (no frameworks like scrapy)
