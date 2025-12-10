from flask import jsonify
import traceback


def get_visited_urls():
    try:
        from storage import Storage

        try:
            storage = Storage()
        except ValueError as config_error:
            return (
                jsonify(
                    {
                        "error": str(config_error),
                        "visited": [],
                        "total": 0,
                        "level_distribution": {},
                    }
                ),
                500,
            )

        try:
            storage.client.ping()
        except Exception as conn_error:
            error_msg = str(conn_error)
            if "localhost" in error_msg or "Connection refused" in error_msg:
                error_msg = "Redis not configured! Set credentials using: flyctl secrets set REDIS_HOST=your-host REDIS_PASSWORD=your-password"
            return (
                jsonify(
                    {
                        "error": f"Redis connection failed: {error_msg}",
                        "visited": [],
                        "total": 0,
                        "level_distribution": {},
                    }
                ),
                500,
            )

        visited = storage.client.smembers("crawley:visited")
        visited_list = []
        level_data = {}

        if storage.client.exists("crawley:level"):
            all_levels = storage.client.hgetall("crawley:level")
            for url, level_str in all_levels.items():
                try:
                    level = int(level_str) if isinstance(level_str, str) else int(level_str)
                    level_data[url] = level
                except (ValueError, TypeError):
                    continue

        for url in visited:
            level = level_data.get(url, 0)
            visited_list.append({"url": url, "level": level})

        visited_list.sort(key=lambda x: (x["level"], x["url"]))

        level_distribution = {}
        for item in visited_list:
            level = item["level"]
            level_distribution[level] = level_distribution.get(level, 0) + 1

        return jsonify(
            {
                "visited": visited_list,
                "total": len(visited_list),
                "level_distribution": level_distribution,
            }
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "visited": [],
                    "total": 0,
                    "level_distribution": {},
                }
            ),
            500,
        )

