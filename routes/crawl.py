import os
import subprocess
import threading
from datetime import datetime
from flask import request, jsonify

crawl_logs = []
crawl_lock = threading.Lock()
crawl_running = False
crawl_process = None


def start_crawl():
    global crawl_logs, crawl_lock, crawl_running, crawl_process

    if crawl_running:
        return jsonify({"error": "Crawl already in progress"}), 400

    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    with crawl_lock:
        crawl_logs = []
        crawl_logs.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting crawl...\n")

    def run_crawl():
        global crawl_logs, crawl_running, crawl_process
        crawl_running = True
        process = None
        try:
            cmd = ["python", "crawler.py", url]

            if data.get("user_agent"):
                cmd.extend(["--user-agent", data["user_agent"]])
            if data.get("allowed_domain"):
                cmd.extend(["--allowed-domain", data["allowed_domain"]])
            level_value = data.get("level")
            if level_value is not None and level_value != "":
                cmd.extend(["--level", str(level_value)])

            use_storage = data.get("use_storage", False)
            if (
                not use_storage
                and os.getenv("REDIS_HOST")
                and os.getenv("REDIS_HOST") != "localhost"
            ):
                use_storage = True
            if use_storage:
                cmd.append("--use-storage")
                if data.get("clear_storage", True):
                    cmd.append("--clear-storage")

            with crawl_lock:
                crawl_logs.append(f"Executing: {' '.join(cmd)}\n")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=os.getcwd(),
            )
            crawl_process = process

            with crawl_lock:
                crawl_logs.append("Running...\n")

            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    with crawl_lock:
                        crawl_logs.append(line)

            returncode = process.returncode

            with crawl_lock:
                if returncode == 0:
                    crawl_logs.append(
                        f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Crawl completed successfully\n"
                    )
                else:
                    crawl_logs.append(
                        f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Crawl completed with exit code {returncode}\n"
                    )
        except Exception as e:
            import traceback

            with crawl_lock:
                crawl_logs.append(
                    f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error: {str(e)}\n"
                )
                crawl_logs.append(f"Traceback: {traceback.format_exc()}\n")
        finally:
            if process:
                try:
                    process.stdout.close()
                except:
                    pass
            crawl_running = False
            crawl_process = None

    thread = threading.Thread(target=run_crawl, daemon=True)
    thread.start()

    return jsonify({"message": "Crawl started"})


def get_logs():
    global crawl_logs, crawl_lock, crawl_running

    with crawl_lock:
        logs = "".join(crawl_logs)

    status = "running" if crawl_running else "idle"
    if "Error:" in logs:
        status = "error"

    return jsonify({"logs": logs, "status": status})


def clear_logs():
    global crawl_logs, crawl_lock

    with crawl_lock:
        crawl_logs = []

    return jsonify({"message": "Logs cleared"})


def stop_crawl():
    global crawl_running, crawl_process, crawl_logs, crawl_lock

    if not crawl_running:
        return jsonify({"error": "No crawl in progress"}), 400

    with crawl_lock:
        if crawl_process:
            try:
                crawl_process.terminate()
                crawl_process.wait(timeout=5)
            except:
                try:
                    crawl_process.kill()
                except:
                    pass
            crawl_logs.append(
                f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Crawl stopped by user\n"
            )

    crawl_running = False
    crawl_process = None

    return jsonify({"message": "Crawl stopped"})
