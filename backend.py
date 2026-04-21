"""
Topology Detector - Ping Backend
Runs a local HTTP server on port 5000.
The HTML frontend calls this to check if IPs are reachable.
Requires: python3 (no pip installs needed)
Run with: sudo python3 backend.py
"""

import subprocess
import platform
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PING_TIMEOUT = 1

def ping(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_flag = "-w" if platform.system().lower() == "windows" else "-W"
    timeout_val = str(PING_TIMEOUT * 1000) if platform.system().lower() == "darwin" else str(PING_TIMEOUT)
    cmd = ["ping", param, "1", timeout_flag, timeout_val, host]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=PING_TIMEOUT + 2,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        ip = params.get("ip", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        if parsed.path != "/ping" or not ip:
            self.wfile.write(json.dumps({"error": "bad request"}).encode())
            return

        result = ping(ip)
        response = json.dumps({"ip": ip, "status": "up" if result else "down"})
        self.wfile.write(response.encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.end_headers()

    def log_message(self, format, *args):
        print(f"  [{self.address_string()}] {format % args}")

if __name__ == "__main__":
    port = 8888
    print(f"Topology ping backend running on http://localhost:{port}")
    print("Keep this running, then open topology_detector.html in your browser.")
    print("Press Ctrl+C to stop.\n")
    server = HTTPServer(("localhost", port), Handler)
    server.serve_forever()
