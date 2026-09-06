"""Serve the dashboard locally, from a live index.

Standard library only. This is deliberate and is why there is no build
step, no `npm`, no CDN and no new entry in `pyproject.toml`: the
repository's dependency set is kept small and slow-moving so a run record
is reproducible years from now, and a dashboard is not a good enough
reason to widen it.

This serves EXACTLY the paths `ui/build.py` writes for GitHub Pages, out
of `ui/payloads.py`, so the same `app.js` runs against both. The
differences are only the ones that cannot be otherwise:

  * `data/meta.json` says `mode: "live"` rather than `"static"`, so the
    page shows a refresh button and no snapshot banner;
  * a record payload inlines its source text, which the static build
    leaves to GitHub at the built commit;
  * `POST /api/refresh` re-reads the corpus.

Binds to loopback by default. There is no authentication because there is
nothing to authenticate: every handler reads.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import threading
import time
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from . import payloads
from .build import resolve_repo_url
from .index import ResearchIndex

STATIC_DIR = Path(__file__).resolve().parent / "static"

# Identifiers are drawn from `[A-Za-z0-9-]` plus `~`, which separates a goal
# checkpoint's goal from its batch. Anything else in a `data/...` path is not
# an identifier this index can hold, and is refused rather than joined onto a
# filesystem path.
SAFE_ID = re.compile(r"^[A-Za-z0-9._~-]{1,200}$")


class IndexHolder:
    """Owns the index and the thread that builds it.

    The server answers before the index exists: a first build takes about
    ten seconds on this corpus, and a dashboard that showed a blank page
    for ten seconds would read as broken. `data/meta.json` reports
    `state: "building"` until it is ready and the page renders that.
    """

    def __init__(self, repo: Path) -> None:
        self.repo = repo
        self.index: ResearchIndex | None = None
        self.error: str | None = None
        self.state = "idle"
        self.started_at = 0.0
        self.repo_url = resolve_repo_url(repo)
        self._lock = threading.Lock()

    def start(self) -> None:
        with self._lock:
            if self.state == "building":
                return
            self.state = "building"
            self.started_at = time.time()
        threading.Thread(target=self._build, daemon=True, name="ui-index-build").start()

    def _build(self) -> None:
        try:
            built = ResearchIndex(self.repo).build()
            with self._lock:
                self.index, self.error, self.state = built, None, "ready"
        except Exception as exc:                       # noqa: BLE001
            with self._lock:
                self.error, self.state = f"{type(exc).__name__}: {exc}", "error"

    def meta(self) -> dict[str, Any]:
        index = self.index
        base = {
            "mode": "live",
            "state": self.state,
            "error": self.error,
            "elapsed": round(time.time() - self.started_at, 1)
            if self.state == "building" else None,
            "repo": str(self.repo),
            "repo_url": self.repo_url,
            "commit": None,
            "built_at": None,
        }
        if index is None:
            return base
        return payloads.meta_payload(index, mode="live", repo_url=self.repo_url) | base | {
            "build_seconds": round(index.build_seconds, 1),
            "deep_scan": index.deep_scan_state,
            "deep_scan_seconds": round(index.deep_scan_seconds, 1),
        }


class Handler(BaseHTTPRequestHandler):
    server_version = "autoresearch-ui"
    protocol_version = "HTTP/1.1"
    holder: IndexHolder                                # injected by `serve`

    def log_message(self, fmt: str, *args) -> None:    # quieter than the default
        if getattr(self.server, "verbose", False):
            super().log_message(fmt, *args)

    # -- plumbing ---------------------------------------------------------
    def _send(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, payload: Any, status: int = 200) -> None:
        self._send(json.dumps(payload, ensure_ascii=False,
                              separators=(",", ":")).encode("utf-8"),
                   "application/json; charset=utf-8", status)

    # -- routing ----------------------------------------------------------
    def do_HEAD(self) -> None:
        self.do_GET()

    def do_POST(self) -> None:
        if urlparse(self.path).path.rstrip("/").endswith("/api/refresh"):
            self.holder.start()
            self._json(self.holder.meta())
            return
        self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        try:
            if path.startswith("/data/"):
                self._data(path[len("/data/"):])
            else:
                self._static(path)
        except BrokenPipeError:
            pass
        except Exception as exc:                       # noqa: BLE001
            self._json({"error": f"{type(exc).__name__}: {exc}"},
                       HTTPStatus.INTERNAL_SERVER_ERROR)

    def _data(self, rel: str) -> None:
        rel = unquote(rel)
        if rel == "meta.json":
            self._json(self.holder.meta())
            return

        index = self.holder.index
        if index is None:
            self._json({"error": "index not ready", "meta": self.holder.meta()},
                       HTTPStatus.SERVICE_UNAVAILABLE)
            return

        simple = {
            "index.json": lambda: payloads.index_rows(index),
            "overview.json": lambda: payloads.overview_payload(index),
            "goals.json": lambda: payloads.goals_payload(index),
            "experiments.json": lambda: payloads.experiments_payload(index),
            "findings.json": lambda: payloads.findings_payload(index),
            "integrity.json": lambda: index.integrity,
        }
        if rel in simple:
            self._json(simple[rel]())
            return

        for prefix, handler in (
            ("goals/", self._goal_detail),
            ("records/", self._record_detail),
            ("search/", self._search_shard),
        ):
            if rel.startswith(prefix):
                name = rel[len(prefix):]
                if not name.endswith(".json") or not SAFE_ID.match(name[:-5]):
                    self._json({"error": "bad identifier"}, HTTPStatus.BAD_REQUEST)
                    return
                handler(index, name[:-5])
                return

        self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    def _goal_detail(self, index: ResearchIndex, goal_id: str) -> None:
        goal = next((g for g in index.goals if g.record_id == goal_id), None)
        if goal is None:
            self._json({"error": "unknown goal"}, HTTPStatus.NOT_FOUND)
        else:
            self._json(payloads.goal_payload(index, goal, detail=True))

    def _record_detail(self, index: ResearchIndex, record_id: str) -> None:
        # `include_raw` is the one place the live server gives more than the
        # static site: the file is already on disk here.
        payload = payloads.record_payload(index, record_id, include_raw=True)
        if payload is None:
            self._json({"error": "unknown record"}, HTTPStatus.NOT_FOUND)
        else:
            self._json(payload)

    def _search_shard(self, index: ResearchIndex, kind: str) -> None:
        shard = payloads.search_shards(index).get(kind)
        if shard is None:
            self._json({"kind": kind, "ids": [], "text": []})
        else:
            self._json(shard)

    def _static(self, path: str) -> None:
        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        target = (STATIC_DIR / rel).resolve()
        if not str(target).startswith(str(STATIC_DIR)) or not target.is_file():
            target = STATIC_DIR / "index.html"         # hash routing: unknown = client route
        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype == "application/javascript":
            ctype += "; charset=utf-8"
        self._send(target.read_bytes(), ctype)


def serve(repo: Path, host: str, port: int, open_browser: bool, verbose: bool) -> int:
    holder = IndexHolder(repo)
    holder.start()

    httpd = ThreadingHTTPServer((host, port), type("BoundHandler", (Handler,),
                                                   {"holder": holder}))
    httpd.verbose = verbose
    url = f"http://{host if host != '0.0.0.0' else '127.0.0.1'}:{httpd.server_address[1]}/"

    print(f"autoresearch UI  {url}")
    print(f"  repository : {repo}")
    print("  read-only  : this server writes nothing to the repository")
    print("  building index in the background; the page fills in as it lands")
    print("  ctrl-c to stop")
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        httpd.server_close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m ui",
        description="Read-only web dashboard over the crypto-autoresearcher ledger. "
                    "`python3 -m ui.build` renders the same thing as a static site.")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1],
                        help="repository root (default: the repo this file lives in)")
    parser.add_argument("--host", default="127.0.0.1",
                        help="bind address (default: 127.0.0.1, loopback only)")
    parser.add_argument("--port", type=int, default=8787, help="bind port (default: 8787)")
    parser.add_argument("--open", action="store_true", help="open a browser once serving")
    parser.add_argument("--verbose", action="store_true", help="log every request")
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    if not (repo / "ledger").is_dir():
        parser.error(f"no ledger/ under {repo}: not a crypto-autoresearcher checkout")
    return serve(repo, args.host, args.port, args.open, args.verbose)
