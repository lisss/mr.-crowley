from flask import Flask, send_from_directory, jsonify
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(base_dir, "static")

if not os.path.exists(static_dir):
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")
if not os.path.exists(static_dir):
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(static_dir):
    static_dir = "static"

sys.path.insert(0, base_dir)
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, static_folder=static_dir)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "crawley"})


@app.route("/")
def index():
    try:
        if os.path.exists(os.path.join(static_dir, "index.html")):
            return send_from_directory(static_dir, "index.html")
        else:
            return jsonify({"error": "index.html not found", "static_dir": static_dir}), 404
    except Exception as e:
        return jsonify({"error": str(e), "static_dir": static_dir, "base_dir": base_dir}), 500


@app.route("/static/<path:path>")
def serve_static(path):
    try:
        return send_from_directory(static_dir, path)
    except Exception as e:
        return jsonify({"error": f"Static file not found: {path}", "static_dir": static_dir}), 404


try:
    from routes import crawl, redis, visited_urls

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

except ImportError:
    pass
