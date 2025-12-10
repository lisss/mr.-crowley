# Tests

- `test_basic.py` - service architecture and components integration
- `test_dedup.py` - URL deduplication logic
- `test_crawling_level.py` - checking the basic crawling logic of limiting crawling depth
- `test_storage.py` - storage (redis) integration

## Running Tests

### Prerequisites

- Docker and Docker Compose installed
- Redis service running (for integration tests)

### Running Tests in Docker

#### Option 1: Using Docker Compose Test Service (Recommended)

```bash
# Run all tests (starts Redis automatically)
docker-compose --profile test run --rm test

# Or start Redis first, then run tests
docker-compose up -d redis
docker-compose --profile test run --rm test

# Run specific test file
docker-compose --profile test run --rm test pytest tests/test_deduplication.py -v

# Run specific test
docker-compose --profile test run --rm test pytest tests/test_deduplication.py::TestDeduplication::test_deduplicator_filters_duplicates -v
```

#### Option 2: Using Docker Compose with Crawler Service

```bash
# Start Redis service
docker-compose up -d redis

# Run all tests
docker-compose run --rm crawler pytest tests/ -v

# Run specific test file
docker-compose run --rm crawler pytest tests/test_deduplication.py -v

# Run with coverage
docker-compose run --rm crawler pytest tests/ --cov=. --cov-report=html
```

#### Option 3: Using Docker Exec

```bash
# Start services
docker-compose up -d

# Run tests in the crawler container
docker exec -it crawley-crawler pytest tests/ -v

# Run specific test file
docker exec -it crawley-crawler pytest tests/test_redis_storage.py -v
```

#### Option 4: Build Test Image

```bash
# Build the image
docker build -t crawley-test .

# Run tests
docker run --rm --network crowley_default \
  -e REDIS_HOST=redis \
  -e REDIS_PORT=6379 \
  crawley-test pytest tests/ -v
```

### Running Tests Locally

```bash
# Activate virtual environment
source venv/bin/activate

# Install test dependencies
pip install -r requirements.txt

# Make sure Redis is running locally or set REDIS_HOST
export REDIS_HOST=localhost
export REDIS_PORT=6379

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_deduplication.py -v

# Run tests with coverage
pytest tests/ --cov=. --cov-report=html
```

## Test Categories

### Architecture Tests (`test_architecture.py`)

Tests that validate the service architecture:
- ✅ Fetcher service exists and has required methods
- ✅ Frontier service exists and has required methods
- ✅ Extractor service exists and has required methods
- ✅ Deduplicator service exists and has required methods
- ✅ Services work together correctly

### Deduplication Tests (`test_deduplication.py`)

Tests for URL deduplication:
- ✅ URL normalization works correctly
- ✅ Duplicate URLs are filtered out
- ✅ Seen URLs are tracked
- ✅ Frontier prevents duplicate visits
- ✅ URLs are deduplicated when adding to queue
- ✅ Deduplication works across multiple pages

### Redis Storage Tests (`test_redis_storage.py`)

Tests for Redis integration:
- ✅ Storage connects to Redis
- ✅ Set operations work correctly
- ✅ List operations work correctly
- ✅ Deduplicator works with Redis
- ✅ Frontier works with Redis storage
- ✅ Queue operations work in Redis
- ✅ Data persists across instances
- ✅ Deduplication persists in Redis

## Test Environment Variables

For Redis integration tests, set:
- `REDIS_HOST` - Redis host (default: localhost)
- `REDIS_PORT` - Redis port (default: 6379)

## Skipping Tests

Tests that require Redis will be automatically skipped if Redis is not available:
```bash
pytest tests/ -v -rs  # Show skipped tests
```

## Continuous Integration

To run tests in CI/CD:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    docker-compose up -d redis
    docker-compose run --rm crawler pytest tests/ -v
```

## Troubleshooting

### Redis Connection Errors

If you see Redis connection errors:
1. Make sure Redis is running: `docker-compose up -d redis`
2. Check Redis is healthy: `docker-compose ps`
3. Verify connection: `docker exec -it crawley-redis redis-cli ping`

### Import Errors

If you see import errors:
1. Make sure you're running from the project root
2. Check that all Python files are in the correct location
3. Verify `sys.path` includes the project root

### Test Failures

If tests fail:
1. Check Redis data is cleared between tests
2. Verify test isolation (each test should be independent)
3. Check for race conditions in concurrent tests

TODO:
- [ ] pre-generate a few pages to pass to the tests, so that we do not depend on the monzo site