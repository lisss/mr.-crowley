FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY package.json package-lock.json ./
COPY tsconfig.json ./
COPY scripts ./scripts
COPY static/src ./static/src
COPY static/css ./static/css
RUN npm install && npm run build

COPY *.py ./
COPY routes ./routes
COPY crawler ./crawler
COPY frontier ./frontier
COPY deduplicator ./deduplicator
COPY extractor ./extractor
COPY fetcher.py ./
COPY storage.py ./
COPY static/index.html ./static/index.html
COPY static/dist ./static/dist

EXPOSE 5000

ENTRYPOINT []
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --threads 2 --timeout 120 --access-logfile - --error-logfile - web:app"]

