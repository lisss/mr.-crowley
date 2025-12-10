import os
from flask import Flask, send_from_directory
from routes import crawl, redis, visited_urls

app = Flask(__name__, static_folder="static")


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)


@app.route("/api/redis-ui-url")
def get_redis_ui_url():
    return redis.get_redis_ui_url()


@app.route("/api/crawl", methods=["POST"])
def start_crawl():
    return crawl.start_crawl()


@app.route("/api/logs")
def get_logs():
    return crawl.get_logs()


@app.route("/api/clear-logs", methods=["POST"])
def clear_logs():
    return crawl.clear_logs()


@app.route("/api/stop-crawl", methods=["POST"])
def stop_crawl():
    return crawl.stop_crawl()


@app.route("/redis-ui")
def redis_ui():
    return redis.redis_ui()


@app.route("/api/redis-health")
def redis_health():
    return redis.redis_health()


@app.route("/api/visited-urls")
def get_visited_urls():
    return visited_urls.get_visited_urls()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
