"""A read-only HTTP dashboard over the research corpus.

Standard library only. This is deliberate and is the reason there is no
build step, no `npm`, no CDN and no new entry in `pyproject.toml`: the
repository's dependency set is kept small and slow-moving so that a run
record is reproducible years from now, and a dashboard is not a good enough
reason to widen it. It also means the UI works in an offline container,
which is where most of this program's sessions actually run.

Binds to loopback by default. There is no authentication because there is
nothing to authenticate: every handler reads, none writes.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import threading
import time
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from .index import KIND_LABELS, KIND_ORDER, TERMINAL_GOAL_STATUSES, ResearchIndex

STATIC_DIR = Path(__file__).resolve().parent / "static"


class IndexHolder:
    """Owns the index and the thread that builds it.

    The server starts answering before the index exists: a first build takes
    about ten seconds on the reference corpus, and a dashboard that showed a
    blank terminal for ten seconds would read as broken. `/api/status`
    reports `building` until it is ready and the page renders that state.
    """

    def __init__(self, repo: Path) -> None:
        self.repo = repo
        self.index: ResearchIndex | None = None
        self.error: str | None = None
        self.state = "idle"
        self.started_at = 0.0
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

    def status(self) -> dict[str, Any]:
        index = self.index
        payload = {
            "state": self.state,
            "error": self.error,
            "elapsed": round(time.time() - self.started_at, 1) if self.state == "building" else None,
            "repo": str(self.repo),
        }
        if index is not None:
            payload |= {
                "records": len(index.records),
                "goals": len(index.goals),
                "experiments": len(index.experiments),
                "built_at": index.built_at,
                "build_seconds": round(index.build_seconds, 1),
                "deep_scan": index.deep_scan_state,
                "deep_scan_seconds": round(index.deep_scan_seconds, 1),
                "ecc_areas": sorted(index.ecc_areas),
                "ecc_policy_error": index.ecc_error,
            }
        return payload


# ---------------------------------------------------------------------------
# Payload builders.
# ---------------------------------------------------------------------------

def _goal_payload(index: ResearchIndex, goal, detail: bool = False) -> dict[str, Any]:
    payload = {
        "id": goal.record_id,
        "title": goal.title,
        "status": goal.status,
        "area": goal.area,
        "ecc": goal.ecc,
        "owner": goal.owner,
        "path": goal.path,
        "sharded": goal.sharded,
        "current_batch_id": goal.current_batch_id,
        "updated_at": goal.updated_at,
        "created_at": goal.created_at,
        "question_ids": goal.question_ids,
        "active_hypothesis_ids": goal.active_hypothesis_ids,
        "budget": goal.budget,
        "batches": len(goal.checkpoints),
        "impediment_count": len(goal.impediments),
        "flags": goal.flags,
        "terminal": goal.status in TERMINAL_GOAL_STATUSES,
        "next_action_preview": goal.next_action[:260],
    }
    if detail:
        payload |= {
            "objective": goal.objective,
            "next_action": goal.next_action,
            "completion_criteria": goal.completion_criteria,
            "impediments": goal.impediments,
            "checkpoints": goal.checkpoints,
            "questions": [index.records[q].summary(index)
                          for q in goal.question_ids if q in index.records],
            "hypotheses": [index.records[h].summary(index)
                           for h in goal.active_hypothesis_ids if h in index.records],
            "mentions": sorted(index.backlinks.get(goal.record_id, ()))[:400],
        }
    return payload


def _overview(index: ResearchIndex) -> dict[str, Any]:
    goals = index.goals
    active = [g for g in goals if g.status == "active"]
    by_status: dict[str, int] = {}
    for goal in goals:
        by_status[goal.status or "(unstated)"] = by_status.get(goal.status or "(unstated)", 0) + 1

    hypothesis_status: dict[str, int] = {}
    for record in index.by_kind.get("H", []):
        hypothesis_status[record.status or "(unstated)"] = \
            hypothesis_status.get(record.status or "(unstated)", 0) + 1

    run_status: dict[str, int] = {}
    for experiment in index.experiments:
        for run in experiment.runs:
            run_status[run["status"]] = run_status.get(run["status"], 0) + 1

    recent = sorted(
        (r for r in index.records.values() if r.date and r.kind in ("DEC", "EV", "TASK", "CORR")),
        key=lambda r: r.date, reverse=True)[:40]

    return {
        "counts": [
            {"key": k, "label": KIND_LABELS[k], "count": len(index.by_kind.get(k, []))}
            for k in KIND_ORDER],
        "goals": {
            "total": len(goals),
            "active": len(active),
            "ecc_active": len([g for g in active if g.ecc]),
            "terminal": len([g for g in goals if g.status in TERMINAL_GOAL_STATUSES]),
            "by_status": by_status,
        },
        "hypothesis_status": hypothesis_status,
        "run_status": run_status,
        "experiments": {
            "total": len(index.experiments),
            "with_runs": len([e for e in index.experiments if e.runs]),
            "runs": sum(len(e.runs) for e in index.experiments),
        },
        "ecc_first": [_goal_payload(index, g) for g in active if g.ecc][:12],
        "attention": [_goal_payload(index, g) for g in goals if g.flags or g.impediments][:12],
        "recent": [r.summary(index) for r in recent],
        "integrity_totals": {
            "unparseable": len(index.integrity.get("unparseable", [])),
            "unparseable_state": index.integrity.get("unparseable_state"),
            "duplicate_ids": len(index.integrity.get("duplicate_ids", [])),
            "id_path_mismatch": len(index.integrity.get("id_path_mismatch", [])),
            "dangling_refs": index.integrity.get("dangling_refs_total", 0),
            "goal_flags": len(index.integrity.get("goal_flags", [])),
        },
    }


def _record_payload(index: ResearchIndex, record_id: str) -> dict[str, Any] | None:
    record = index.records.get(record_id)
    if record is None:
        return None
    parsed, error = index.full_record(record_id)
    body = parsed
    if isinstance(parsed, dict) and len(parsed) == 1:
        body = next(iter(parsed.values()))
    return {
        "summary": record.summary(index),
        "root_key": record.root_key,
        # `verified` is the tier-2 flag from ui/scan.py: true means this
        # payload's `body` came from a real YAML parse, not the header scan.
        "verified": error is None and parsed is not None,
        "parse_error": error,
        "body": _jsonable(body),
        "raw": index.raw_text(record_id),
        "links": index.neighbourhood(record_id),
    }


def _jsonable(value: Any, depth: int = 0) -> Any:
    """Coerce a parsed record to JSON.

    YAML dates, tuples and non-string keys all appear in this corpus. Rather
    than dropping them, they are stringified -- a reader looking at a detail
    view should see every field the record has.
    """
    if depth > 24:
        return "…"
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {str(k): _jsonable(v, depth + 1) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(v, depth + 1) for v in value]
    return str(value)


class Handler(BaseHTTPRequestHandler):
    server_version = "autoresearch-ui"
    protocol_version = "HTTP/1.1"
    holder: IndexHolder                                # injected by `serve`

    def log_message(self, fmt: str, *args) -> None:    # quieter than the default
        if not getattr(self.server, "verbose", False):
            return
        super().log_message(fmt, *args)

    # -- plumbing ---------------------------------------------------------
    def _send(self, body: bytes, content_type: str, status: int = 200,
              cache: str = "no-store") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", cache)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, payload: Any, status: int = 200) -> None:
        self._send(json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8", status)

    def _require_index(self) -> ResearchIndex | None:
        index = self.holder.index
        if index is None:
            self._json({"error": "index not ready", "status": self.holder.status()},
                       HTTPStatus.SERVICE_UNAVAILABLE)
            return None
        return index

    # -- routing ----------------------------------------------------------
    def do_HEAD(self) -> None:
        self.do_GET()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/refresh":
            self.holder.start()
            self._json(self.holder.status())
            return
        self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path, query = parsed.path, parse_qs(parsed.query)
        try:
            if path.startswith("/api/"):
                self._api(path, query)
            else:
                self._static(path)
        except BrokenPipeError:
            pass
        except Exception as exc:                       # noqa: BLE001
            self._json({"error": f"{type(exc).__name__}: {exc}"},
                       HTTPStatus.INTERNAL_SERVER_ERROR)

    def _api(self, path: str, query: dict[str, list[str]]) -> None:
        if path == "/api/status":
            self._json(self.holder.status())
            return

        index = self._require_index()
        if index is None:
            return

        if path == "/api/overview":
            self._json(_overview(index))
        elif path == "/api/facets":
            self._json(index.facets())
        elif path == "/api/ids":
            # Every identifier the index holds, in one response. The client
            # links identifiers found in free text, and it must only link the
            # ones that resolve -- an identifier that leads nowhere has to
            # stay plain text, because that is how a reader sees a dangling
            # reference while reading rather than by running a report.
            self._json({"ids": sorted(index.records)})
        elif path == "/api/goals":
            self._json({"goals": [_goal_payload(index, g) for g in index.goals]})
        elif path.startswith("/api/goals/"):
            wanted = unquote(path[len("/api/goals/"):])
            goal = next((g for g in index.goals if g.record_id == wanted), None)
            if goal is None:
                self._json({"error": "unknown goal"}, HTTPStatus.NOT_FOUND)
            else:
                self._json(_goal_payload(index, goal, detail=True))
        elif path == "/api/records":
            self._records(index, query)
        elif path.startswith("/api/records/"):
            payload = _record_payload(index, unquote(path[len("/api/records/"):]))
            if payload is None:
                self._json({"error": "unknown record"}, HTTPStatus.NOT_FOUND)
            else:
                self._json(payload)
        elif path == "/api/experiments":
            self._json({"experiments": [
                {
                    "id": e.record_id, "title": e.title, "status": e.status,
                    "area": e.area, "path": e.path, "hypothesis_id": e.hypothesis_id,
                    "question_id": e.question_id, "frozen": e.frozen,
                    "execution_authorized": e.execution_authorized,
                    "runs": e.runs, "run_count": len(e.runs),
                    "ecc": e.area in index.ecc_areas if e.area else False,
                }
                for e in index.experiments]})
        elif path == "/api/integrity":
            self._json(index.integrity)
        else:
            self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    def _records(self, index: ResearchIndex, query: dict[str, list[str]]) -> None:
        def multi(name: str) -> set[str] | None:
            values = {v for raw in query.get(name, []) for v in raw.split(",") if v}
            return values or None

        limit = max(1, min(int(query.get("limit", ["100"])[0] or 100), 500))
        offset = max(0, int(query.get("offset", ["0"])[0] or 0))
        hits, total = index.search(
            query.get("q", [""])[0], kinds=multi("kind"), areas=multi("area"),
            statuses=multi("status"), limit=limit, offset=offset)
        self._json({
            "total": total, "limit": limit, "offset": offset,
            "records": [r.summary(index) for r in hits],
        })

    def _static(self, path: str) -> None:
        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        target = (STATIC_DIR / rel).resolve()
        if not str(target).startswith(str(STATIC_DIR)) or not target.is_file():
            # Hash routing means every unknown path is a client route.
            target = STATIC_DIR / "index.html"
        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript",):
            ctype += "; charset=utf-8"
        self._send(target.read_bytes(), ctype)


def serve(repo: Path, host: str, port: int, open_browser: bool, verbose: bool) -> int:
    holder = IndexHolder(repo)
    holder.start()

    handler = type("BoundHandler", (Handler,), {"holder": holder})
    httpd = ThreadingHTTPServer((host, port), handler)
    httpd.verbose = verbose
    url = f"http://{host if host != '0.0.0.0' else '127.0.0.1'}:{httpd.server_address[1]}/"

    print(f"autoresearch UI  {url}")
    print(f"  repository : {repo}")
    print("  read-only  : this server writes nothing to the repository")
    print("  building index in the background; the page will fill in as it lands")
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
        description="Read-only web dashboard over the crypto-autoresearcher ledger.")
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
