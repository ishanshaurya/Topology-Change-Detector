# Topology Change Detector

A real-time network topology monitor built for PES University (Assignment #21). Detects when devices go up or down on a local network, updates a live topology map, and logs every change with a timestamp.

Built with Python 3 and plain HTML/CSS/JS. No external libraries or pip installs required.

---

## Assignment Requirements

1. Monitor switch/link events — backend pings each node every 5 seconds and detects state transitions
2. Update topology map — frontend redraws node status live using canvas
3. Display changes — change counter increments on every up/down event
4. Log updates — event log records every change with a human-readable timestamp

---

## Architecture

Three files, each with a distinct role:

```
topology_detector.py       # Standalone Python CLI monitor (terminal output)
backend.py                 # HTTP server on port 8888, does real ICMP pings
topology_detector.html     # Browser dashboard, polls backend every 5 seconds
```

How they connect:

- `topology_detector.py` runs independently as a CLI tool. It pings nodes in a loop and prints change events to stdout. No browser needed.
- `backend.py` is an `http.server.HTTPServer` that exposes a single endpoint: `GET /ping?ip=x.x.x.x`. It runs a subprocess ping and returns `{"status": "up"}` or `{"status": "down"}`.
- `topology_detector.html` is a static file opened directly in the browser. It cannot ping IPs itself (browser security restriction), so it fetches `http://localhost:8888/ping?ip=...` for each node and renders the result.

The frontend and CLI tool are independent — you can use either one. The HTML frontend requires `backend.py` to be running.

---

## Network Topology Result

The dashboard renders a hub-and-spoke topology with the router as the center node. Each device gets a status card and a connecting line that turns red when the node goes down.

![Topology Map](screenshots/topology_map.png)
![Dashboard](screenshots/dashboard.png)

---

## How to Run

**Step 1 — Start the backend server**

```bash
sudo python3 /Users/ishaan/Documents/topology-detector/backend.py
```

`sudo` is required because ICMP ping on macOS needs root privileges.

**Step 2 — Open the dashboard**

```bash
open /Users/ishaan/Documents/topology-detector/topology_detector.html
```

Then click **START** in the browser. The dashboard will begin polling every 5 seconds.

**Optional — Run the CLI monitor instead**

```bash
sudo python3 /Users/ishaan/Documents/topology-detector/topology_detector.py
```

This prints change events directly to the terminal with no browser required.

---

## Adapting It to Your Own Network

Before running, update the IP list in both `topology_detector.py` and `topology_detector.html` to match your network.

**Finding your IPs:**

```bash
# Your own IP
ipconfig getifaddr en0

# All devices currently on your network
arp -a
```

`arp -a` lists every device your Mac has recently seen, in the format:

```
? (192.168.0.1) at a4:xx:xx:xx:xx:xx on en0
? (192.168.0.2) at b8:xx:xx:xx:xx:xx on en0
```

Take the IPs in parentheses. The `.1` address is almost always the router.

**Where to update them:**

In `topology_detector.py`, find the `NODES` list near the top:

```python
NODES = [
    {"ip": "192.168.0.1", "label": "Router"},
    {"ip": "192.168.0.2", "label": "Device-2"},
    # add or remove entries here
]
```

In `topology_detector.html`, find the equivalent `nodes` array in the `<script>` section and update it the same way.

---

## macOS-Specific Fixes

Two platform bugs were found and fixed during development:

**1. ping -W timeout units**

On Linux, `ping -W 1` means a 1-second timeout. On macOS, `-W` takes milliseconds, not seconds. Passing `1` caused every ping to time out almost instantly, making all nodes appear down permanently.

Fix applied in `topology_detector.py`:

```python
timeout_val = str(PING_TIMEOUT * 1000) if platform.system().lower() == "darwin" else str(PING_TIMEOUT)
```

**2. Port 5000 conflict with AirPlay**

macOS Monterey and later run a ControlCenter service (AirPlay receiver) that binds to port 5000. Running the backend on 5000 gave an `Address already in use` error immediately.

Fix: moved the backend to port **8888**, which is unused by default on macOS.

---

## Known Limitations

- **sudo required** — ICMP ping on macOS requires elevated privileges. The backend will fail silently or raise a permission error if run without `sudo`.
- **Browser CORS** — a page loaded from `file:///` cannot make fetch requests to arbitrary local IPs. All ping checks are routed through `backend.py` on localhost to work around this.
- **Single subnet** — the tool monitors a flat `/24` subnet. It does not handle VLANs or multi-hop topologies.
- **No persistence across restarts** — `topology_changes.log` stores the event log locally, but the in-browser state resets on page reload.
- **macOS only tested** — the ping timeout fix targets Darwin. Linux should work with minor changes; Windows is untested.

---

## Files

```
topology_detector.py       # CLI monitor
backend.py                 # Ping server (port 8888)
topology_detector.html     # Browser dashboard
screenshots/               # Result screenshots for reference
.gitignore
README.md
```
