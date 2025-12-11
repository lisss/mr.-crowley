import os
import sys
from flask import Flask, send_from_directory, jsonify

app = Flask(__name__, static_folder="static", static_url_path="/static")

try:
    from routes import crawl, redis, visited_urls
except ImportError as e:
    print(f"Warning: Could not import routes: {e}", file=sys.stderr)
    crawl = redis = visited_urls = None


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/static/<path:path>")
def serve_static(path):
    try:
        return send_from_directory("static", path)
    except Exception as e:
        print(f"Error serving static file {path}: {e}", file=sys.stderr)
        return jsonify({"error": f"File not found: {path}"}), 404


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


if crawl:

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


if redis:

    @app.route("/api/redis-ui-url")
    def get_redis_ui_url():
        return redis.get_redis_ui_url()

    @app.route("/redis-ui")
    def redis_ui():
        return redis.redis_ui()

    @app.route("/api/redis-health")
    def redis_health():
        return redis.redis_health()


if visited_urls:

    @app.route("/api/visited-urls")
    def get_visited_urls():
        return visited_urls.get_visited_urls()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
