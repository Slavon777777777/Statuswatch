from flask import Flask, jsonify, render_template_string
import requests
import time
import threading

app = Flask(__name__)

TARGETS = {
    "weather-app": "https://weather-app-6xq9.onrender.com",
    "example-site": "https://example.com",
}

status_data = {}

def check_targets():
    while True:
        for name, url in TARGETS.items():
            try:
                start = time.time()
                response = requests.get(url, timeout=5)
                duration = round((time.time() - start) * 1000)
                status_data[name] = {
                    "url": url,
                    "status_code": response.status_code,
                    "response_time_ms": duration,
                    "up": response.status_code == 200,
                }
            except requests.RequestException:
                status_data[name] = {
                    "url": url,
                    "status_code": None,
                    "response_time_ms": None,
                    "up": False,
                }
        time.sleep(30)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>StatusWatch</title>
    <meta http-equiv="refresh" content="15">
    <style>
        body { font-family: Arial, sans-serif; background: #1b3a5c; color: white; padding: 40px; }
        h1 { color: #ffffff; }
        table { width: 100%; border-collapse: collapse; background: white; color: #1b3a5c; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ccc; }
        th { background: #0f2540; color: white; }
        .up { color: green; font-weight: bold; }
        .down { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <h1>StatusWatch — Uptime Monitor</h1>
    <table>
        <tr>
            <th>Service</th>
            <th>URL</th>
            <th>Status</th>
            <th>Response Time</th>
        </tr>
        {% for name, data in status_data.items() %}
        <tr>
            <td>{{ name }}</td>
            <td>{{ data.url }}</td>
            <td class="{{ 'up' if data.up else 'down' }}">{{ 'UP' if data.up else 'DOWN' }}</td>
            <td>{{ data.response_time_ms }} ms</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE, status_data=status_data)

@app.route("/status")
def status():
    return jsonify(status_data)

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    checker_thread = threading.Thread(target=check_targets, daemon=True)
    checker_thread.start()
    app.run(host="0.0.0.0", port=5000)
