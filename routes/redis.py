import os
from flask import jsonify, redirect


def get_redis_ui_url():
    redis_ui_url = os.getenv("REDIS_UI_URL")
    return jsonify({"url": redis_ui_url} if redis_ui_url else {})


def redis_ui():
    redis_ui_url = os.getenv("REDIS_UI_URL")
    if redis_ui_url:
        return redirect(redis_ui_url)
    else:
        return jsonify({"message": "Redis UI not configured"}), 404


def redis_health():
    try:
        from storage import Storage

        storage = Storage()
        storage.client.ping()

        visited_count = storage.client.scard("crawley:visited")
        level_count = (
            storage.client.hlen("crawley:level") if storage.client.exists("crawley:level") else 0
        )

        return jsonify(
            {
                "status": "connected",
                "host": storage.redis_host,
                "port": storage.redis_port,
                "visited_count": visited_count,
                "level_count": level_count,
            }
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(e),
                    "host": os.getenv("REDIS_HOST", "not set"),
                    "port": os.getenv("REDIS_PORT", "not set"),
                }
            ),
            500,
        )

