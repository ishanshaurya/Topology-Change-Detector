"""
Topology Change Detector
========================
Monitors switch/link events, updates topology map,
displays changes, and logs updates.

Requirements: Python 3.6+ — zero external dependencies.

Usage:
    python topology_detector.py

Edit TOPOLOGY below to define your nodes.
"""

import subprocess
import platform
import time
import logging
import json
import os
from datetime import datetime

# ─── CONFIG ──────────────────────────────────────────────────────────────────

TOPOLOGY = {
    "Router":   "192.168.0.1",
    "Device-2": "192.168.0.2",
    "Device-4": "192.168.0.4",
    "Device-5": "192.168.0.5",
    "My-Mac":   "192.168.0.7",
}

POLL_INTERVAL = 5    # seconds between checks
LOG_FILE      = "topology_changes.log"
PING_TIMEOUT  = 1    # seconds per ping

# ─── LOGGING SETUP ───────────────────────────────────────────────────────────

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def log(msg):
    logging.info(msg)
    print(f"  [{datetime.now().strftime('%H:%M:%S')}] {msg}")

# ─── PING ────────────────────────────────────────────────────────────────────

def ping(host):
    """Return True if host responds to ping."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_flag = "-w" if platform.system().lower() == "windows" else "-W"
    timeout_val = str(PING_TIMEOUT * 1000) if platform.system().lower() == "darwin" else str(PING_TIMEOUT)
    cmd = ["ping", param, "1", timeout_flag, timeout_val, host]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=PING_TIMEOUT + 1,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

# ─── TOPOLOGY MAP ────────────────────────────────────────────────────────────

def build_snapshot():
    """Ping all nodes and return {name: 'UP'/'DOWN'}."""
    return {name: ("UP" if ping(ip) else "DOWN") for name, ip in TOPOLOGY.items()}

# ─── DISPLAY ─────────────────────────────────────────────────────────────────

def clear():
    os.system("cls" if platform.system().lower() == "windows" else "clear")

def display_map(snapshot, changes):
    clear()
    print("=" * 48)
    print("   TOPOLOGY CHANGE DETECTOR")
    print(f"   Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 48)
    print(f"  {'NODE':<14} {'IP':<18} {'STATUS'}")
    print("  " + "-" * 44)
    for name, ip in TOPOLOGY.items():
        status = snapshot.get(name, "UNKNOWN")
        icon   = "✓" if status == "UP" else "✗"
        print(f"  {name:<14} {ip:<18} {icon} {status}")
    print()
    if changes:
        print("  Recent changes:")
        for c in changes[-5:]:   # show last 5
            print(f"    → {c}")
    else:
        print("  No changes detected yet.")
    print()
    print(f"  Polling every {POLL_INTERVAL}s  |  Log: {LOG_FILE}")
    print("  Press Ctrl+C to stop.\n")

# ─── MAIN LOOP ────────────────────────────────────────────────────────────────

def main():
    print("Starting topology monitor…")
    log("=== Topology monitor started ===")
    log("Initial topology: " + json.dumps(TOPOLOGY))

    previous  = {}
    changes   = []

    while True:
        current = build_snapshot()

        # Detect changes vs previous snapshot
        for name, status in current.items():
            if name in previous and previous[name] != status:
                msg = f"{name} changed {previous[name]} → {status}"
                changes.append(msg)
                log(f"CHANGE: {msg}")

        # First run — log initial state
        if not previous:
            for name, status in current.items():
                log(f"INIT:   {name} ({TOPOLOGY[name]}) is {status}")

        display_map(current, changes)
        previous = current.copy()
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nMonitor stopped.")
        log("=== Topology monitor stopped ===")
