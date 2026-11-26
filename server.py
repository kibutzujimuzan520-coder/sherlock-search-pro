#!/usr/bin/env python3
"""Sherlock Search Pro: limited public-profile URL checker. No scraping or login bypass."""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
import json, urllib.request, urllib.error, re, os

PLATFORMS = [
    ("Instagram", "Social", "https://www.instagram.com/{u}/"),
    ("TikTok", "Social", "https://www.tiktok.com/@{u}"),
    ("X", "Social", "https://x.com/{u}"),
    ("Reddit", "Social", "https://www.reddit.com/user/{u}/"),
    ("Pinterest", "Social", "https://www.pinterest.com/{u}/"),
    ("Twitch", "Social", "https://www.twitch.tv/{u}"),
    ("YouTube", "Social", "https://www.youtube.com/@{u}"),
    ("GitHub", "Developer", "https://github.com/{u}"),
    ("GitLab", "Developer", "https://gitlab.com/{u}"),
    ("Codeberg", "Developer", "https://codeberg.org/{u}"),
    ("Medium", "Other", "https://medium.com/@{u}"),
    ("SoundCloud", "Other", "https://soundcloud.com/{u}"),
    ("Steam", "Other", "https://steamcommunity.com/id/{u}"),
    ("Flickr", "Other", "https://www.flickr.com/people/{u}/"),
]
VALID = re.compile(r"^[A-Za-z0-9_.-]{1,30}$")


def check_profile(name, category, template, username):
    url = template.format(u=quote(username, safe="._-"))
    req = urllib.request.Request(url, headers={
        "User-Agent": "SherlockSearchPro/1.0 (public-profile URL checker)",
        "Range": "bytes=0-2048",
    })
    try:
        with urllib.request.urlopen(req, timeout=7) as resp:
            status = resp.status
            if status in (200, 206):
                state, note = "possible", "Page responded; open to verify. Some platforms return generic pages for unavailable profiles."
            else:
                state, note = "unknown", f"HTTP {status}; response is inconclusive."
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            state, note = "not_found", "The site returned a not-found response. This may still be inaccurate."
        elif e.code in (401, 403, 429, 503):
            state, note = "unknown", "Blocked or rate-limited. Open the link in your browser to verify."
        else:
            state, note = "unknown", f"HTTP {e.code}; cannot reliably determine."
    except Exception:
        state, note = "unknown", "Network/site restrictions prevented verification."
    return {"platform": name, "category": category, "url": url, "status": state, "note": note}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[Sherlock Pro] " + fmt % args)

    def send_file(self, filename, content_type):
        try:
            with open(filename, "rb") as f: data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_error(404, "File not found")

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self.send_file("index.html", "text/html; charset=utf-8")
        if self.path == "/manifest.json":
            return self.send_file("manifest.json", "application/manifest+json")
        if self.path == "/sw.js":
            return self.send_file("sw.js", "application/javascript; charset=utf-8")
        if self.path == "/icon.svg":
            return self.send_file("icon.svg", "image/svg+xml")
        if self.path == "/api/platforms":
            payload = json.dumps([{"name": p[0], "category": p[1]} for p in PLATFORMS]).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload); return
        self.send_error(404)

    def do_POST(self):
        if self.path != "/api/search": return self.send_error(404)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 5000: return self.send_error(413, "Request too large")
            body = json.loads(self.rfile.read(length) or b"{}")
            username = (body.get("username") or "").strip()
            cats = body.get("categories", ["Social", "Developer", "Other"])
            if not VALID.fullmatch(username):
                payload = json.dumps({"error": "Use 1–30 characters: letters, numbers, dots, underscores, or hyphens."}).encode()
                self.send_response(400); self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload); return
            selected = [p for p in PLATFORMS if p[1] in cats]
            results = []
            with ThreadPoolExecutor(max_workers=5) as pool:
                jobs = [pool.submit(check_profile, *p, username) for p in selected]
                for job in as_completed(jobs): results.append(job.result())
            order = {p[0]: i for i, p in enumerate(selected)}
            results.sort(key=lambda r: order[r["platform"]])
            payload = json.dumps({"username": username, "results": results, "checked": len(results)}, ensure_ascii=False).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload)
        except Exception:
            self.send_error(400, "Bad request")

if __name__ == "__main__":
    print("Sherlock Search Pro server started.")
    print("Open http://127.0.0.1:8765 locally, or use the deployed HTTPS URL.")
    print("For phones on the same Wi-Fi, open this computer's LAN IP at port 8765.")
    # LAN access enables a phone browser to reach the host computer. Use only on a trusted network.
    port = int(os.environ.get("PORT", "8765"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
