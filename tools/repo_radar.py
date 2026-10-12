#!/usr/bin/env python3
"""Daily radar for cryptography repositories on GitHub.

Three sources feed one digest:

* **discover** -- GitHub repository search for the configured topics and
  keywords, limited to repos created or pushed since the last run. Each hit
  is scored for relevance (topic and term weights, minus cryptocurrency
  noise), and relevant hits are remembered so that a digest lists only what
  is new to the radar.
* **watch** -- new commits, releases and tags on the followed repositories.
* **archive** -- one day of GH Archive (https://www.gharchive.org), GitHub's
  public event stream saved hourly: stars, forks, releases and repos made
  public, for known repos and for repos whose names match a pattern. Matches
  the radar has not seen are looked up and scored like search hits.

Configuration is `orchestration/repo-radar.toml`. Seen repos, watch cursors,
per-day archive aggregates and digests live in a state directory, which the
`repo-radar` workflow keeps on the orphan branch `automation/repo-radar`.
Nothing here reads or writes research records. See docs/repo-radar.md.

    python3 tools/repo_radar.py run --state-dir radar-state
    python3 tools/repo_radar.py publish-issue --state-dir radar-state --repo OWNER/REPO
    python3 tools/repo_radar.py archive --day 2026-10-05 --days 3
    python3 tools/repo_radar.py score OWNER/REPO
    python3 tools/repo_radar.py opml > feeds.opml

The API token comes from GITHUB_TOKEN or GH_TOKEN; without one, search is
limited to 10 requests a minute.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
import gzip
import http.client
import json
import os
from pathlib import Path
import re
import sys
import time
import tomllib
from typing import Any, Callable, Iterable
import urllib.error
import urllib.parse
import urllib.request
from xml.sax.saxutils import quoteattr
import zlib

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "orchestration" / "repo-radar.toml"
API = "https://api.github.com"
ARCHIVE_URL = "https://data.gharchive.org/{day}-{hour}.json.gz"
USER_AGENT = "crypto-autoresearcher-repo-radar"
STATE_VERSION = 1
STATE_BRANCH = "automation/repo-radar"
ISSUE_LABEL = "repo-radar"
# GitHub rejects issue bodies over 65,536 characters.
ISSUE_BODY_LIMIT = 60_000
REPO_NAME = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
# Fields kept per remembered repo; the rest of an API record is not needed.
KEEP = ("full_name", "description", "topics", "language", "stars", "forks",
        "created_at", "pushed_at", "archived", "html_url")


# --------------------------------------------------------------------------
# GitHub REST client

Transport = Callable[[str, str, dict, "bytes | None"], "tuple[int, dict, bytes]"]


def urllib_transport(method: str, url: str, headers: dict,
                     body: bytes | None) -> tuple[int, dict, bytes]:
    request = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as resp:
            return resp.status, {k.lower(): v for k, v in resp.headers.items()}, resp.read()
    except urllib.error.HTTPError as err:
        headers = {k.lower(): v for k, v in (err.headers or {}).items()}
        return err.code, headers, err.read()


class GitHubError(RuntimeError):
    def __init__(self, status: int, url: str, detail: str = "", message: str | None = None):
        super().__init__(message or f"GitHub API {status} for {url}" + (f": {detail}" if detail else ""))
        self.status = status


class GitHub:
    """A small REST client: bearer token, search pacing, rate-limit waits, retries.

    Search allows 30 requests a minute with a token, so search calls are
    spaced `search_interval` seconds apart rather than spent in a burst and
    then waited out.
    """

    def __init__(self, token: str | None = None, transport: Transport = urllib_transport,
                 sleep: Callable[[float], None] = time.sleep,
                 clock: Callable[[], float] = time.time,
                 search_interval: float = 2.1, max_wait: float = 900.0):
        self.token = token
        self.transport = transport
        self.sleep = sleep
        self.clock = clock
        self.search_interval = search_interval if token else 6.1
        self.max_wait = max_wait
        self.calls: Counter = Counter()
        self._last_search = float("-inf")

    @classmethod
    def from_env(cls) -> "GitHub":
        return cls(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))

    def request(self, method: str, path: str, params: dict | None = None,
                body: Any = None, *, search: bool = False) -> Any:
        url = path if path.startswith("https://") else API + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        headers = {"Accept": "application/vnd.github+json",
                   "X-GitHub-Api-Version": "2022-11-28", "User-Agent": USER_AGENT}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        status = 0
        for attempt in range(6):
            if search:
                wait = self._last_search + self.search_interval - self.clock()
                if wait > 0:
                    self.sleep(wait)
                self._last_search = self.clock()
            try:
                status, resp_headers, raw = self.transport(method, url, headers, data)
            except (urllib.error.URLError, TimeoutError, ConnectionError,
                    http.client.HTTPException) as err:
                if attempt == 5:
                    raise GitHubError(0, url, str(err)) from err
                self.sleep(2 ** attempt)
                continue
            self.calls["search" if search else "core"] += 1
            if status in (403, 429) and _rate_limited(resp_headers, raw):
                wait = _reset_wait(resp_headers, self.clock())
                if wait > self.max_wait:
                    raise GitHubError(status, url, f"rate limited for another {wait:.0f}s")
                self.sleep(wait)
                continue
            if status >= 500 and attempt < 5:
                self.sleep(2 ** attempt)
                continue
            if status >= 400:
                raise GitHubError(status, url, _error_detail(raw))
            return json.loads(raw) if raw.strip() else None
        raise GitHubError(status, url, "retries exhausted")


def _rate_limited(headers: dict, raw: bytes) -> bool:
    return (headers.get("x-ratelimit-remaining") == "0" or "retry-after" in headers
            or b"rate limit" in raw.lower())


def _reset_wait(headers: dict, now: float) -> float:
    if "retry-after" in headers:
        return max(1.0, float(headers["retry-after"]))
    if "x-ratelimit-reset" in headers:
        return max(1.0, float(headers["x-ratelimit-reset"]) - now + 1)
    return 60.0


def _error_detail(raw: bytes) -> str:
    try:
        return str(json.loads(raw).get("message", ""))[:200]
    except (ValueError, AttributeError):
        return raw[:200].decode("utf-8", "replace")


def repo_record(item: dict) -> dict:
    """The fields the radar keeps from a repository API object."""
    name = item["full_name"]
    return {
        "full_name": name,
        "description": " ".join((item.get("description") or "").split())[:300],
        "topics": sorted(item.get("topics") or []),
        "language": item.get("language"),
        "stars": int(item.get("stargazers_count") or 0),
        "forks": int(item.get("forks_count") or 0),
        "created_at": item.get("created_at"),
        "pushed_at": item.get("pushed_at"),
        "archived": bool(item.get("archived")),
        "fork": bool(item.get("fork")),
        "html_url": item.get("html_url") or f"https://github.com/{name}",
    }


# --------------------------------------------------------------------------
# Configuration and relevance scoring

def load_config(path: Path) -> dict:
    with open(path, "rb") as fh:
        cfg = tomllib.load(fh)
    for section in ("search", "scoring", "archive", "watch", "digest"):
        cfg.setdefault(section, {})
    bad = [name for name in watchlist(cfg) if not REPO_NAME.match(name)]
    if bad:
        raise SystemExit(f"{path}: [watch] repos must be OWNER/REPO, got {bad}")
    return cfg


def watchlist(cfg: dict) -> list[str]:
    return list(dict.fromkeys(cfg.get("watch", {}).get("repos", [])))


@dataclass
class Scorer:
    """Adds topic and term weights; negative terms subtract.

    Terms are case-insensitive regular expressions over the repo name (not the
    owner) and description. Each pattern counts once. The labels returned
    with a score say which topics and terms fired, so a digest row explains
    itself and a weight can be tuned from it.
    """

    topics: dict[str, int]
    terms: list[tuple[re.Pattern[str], int]]
    min_score: int

    @classmethod
    def from_config(cls, cfg: dict) -> "Scorer":
        scoring = cfg["scoring"]
        patterns = {**scoring.get("terms", {}), **scoring.get("negative", {})}
        return cls(
            topics={k.lower(): int(v) for k, v in scoring.get("topics", {}).items()},
            terms=[(re.compile(p, re.I), int(w)) for p, w in patterns.items()],
            min_score=int(scoring.get("min_score", 3)),
        )

    def score(self, rec: dict) -> tuple[int, list[str]]:
        name = rec["full_name"].partition("/")[2]
        text = re.sub(r"[_.]+", " ", name) + " " + (rec.get("description") or "")
        total, why = 0, []
        for topic in rec.get("topics") or ():
            weight = self.topics.get(topic.lower())
            if weight:
                total += weight
                why.append(f"#{topic}")
        for pattern, weight in self.terms:
            match = pattern.search(text)
            if match:
                total += weight
                why.append(("-" if weight < 0 else "") + " ".join(match.group(0).lower().split()))
        return total, why


# --------------------------------------------------------------------------
# State

def load_state(state_dir: Path) -> dict:
    path = state_dir / "state.json"
    state = json.loads(path.read_text()) if path.exists() else {}
    state.setdefault("version", STATE_VERSION)
    for key in ("meta", "repos", "watch", "rejected"):
        state.setdefault(key, {})
    return state


def save_state(state_dir: Path, state: dict) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    path = state_dir / "state.json"
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    tmp.replace(path)


def remember(state: dict, rec: dict, score: int, why: list[str], today: date,
             source: str) -> dict:
    prev = state["repos"].get(rec["full_name"], {})
    entry = {**prev, **{k: rec[k] for k in KEEP if k in rec}}
    entry.update(score=score, why=why, last_seen=today.isoformat())
    entry.setdefault("first_seen", today.isoformat())
    entry["sources"] = sorted(set(prev.get("sources", [])) | {source})
    state["repos"][rec["full_name"]] = entry
    return entry


def prune(state: dict, today: date, cfg: dict) -> None:
    """Forget repos unseen for `retention_days`; retry rejected ones after 30 days."""
    keep_after = (today - timedelta(days=int(cfg["digest"].get("retention_days", 365)))).isoformat()
    watched = {n.lower() for n in watchlist(cfg)}
    for name, entry in list(state["repos"].items()):
        if entry.get("last_seen", "") < keep_after and name.lower() not in watched:
            del state["repos"][name]
    retry_after = (today - timedelta(days=30)).isoformat()
    for name, seen in list(state["rejected"].items()):
        if seen < retry_after:
            del state["rejected"][name]
    for name in list(state["watch"]):
        if name.lower() not in watched:
            del state["watch"][name]


# --------------------------------------------------------------------------
# Discovery: repository search

def window_start(state: dict, cfg: dict, today: date) -> date:
    search = cfg["search"]
    last = state["meta"].get("last_discovery")
    if last:
        start = date.fromisoformat(last) - timedelta(days=int(search.get("overlap_days", 1)))
    else:
        start = today - timedelta(days=int(search.get("first_run_days", 7)))
    return max(start, today - timedelta(days=int(search.get("max_window_days", 14))))


def build_queries(cfg: dict, since: date) -> list[dict]:
    """Each topic and keyword runs twice, for repos created and pushed since `since`.

    `created_only` names the ones too broad to search by push date daily.
    `extra_queries` are used as written, with `{since}` substituted.
    """
    search = cfg["search"]
    qualifiers = search.get("qualifiers", "").strip()
    created_only = {t.lower() for t in search.get("created_only", [])}
    queries = []

    def add(label: str, base: str, mode: str) -> None:
        q = f"{base} {mode}:>={since.isoformat()}" + (f" {qualifiers}" if qualifiers else "")
        queries.append({"label": label, "q": q, "mode": mode,
                        "sort": "updated" if mode == "created" else "stars"})

    for kind, terms in (("topic", search.get("topics", [])), ("keyword", search.get("keywords", []))):
        for term in terms:
            base = f"topic:{term}" if kind == "topic" else f"{term} in:name,description,readme"
            label = f"topic:{term}" if kind == "topic" else term
            for mode in ("created",) if term.lower() in created_only else ("created", "pushed"):
                add(label, base, mode)
    for extra in search.get("extra_queries", []):
        queries.append({"label": extra, "q": extra.format(since=since.isoformat()),
                        "mode": "custom", "sort": "updated"})
    return queries


def run_search(gh: GitHub, query: dict, max_pages: int) -> tuple[list[dict], dict]:
    items: list[dict] = []
    total, incomplete = 0, False
    for page in range(1, max_pages + 1):
        data = gh.request("GET", "/search/repositories",
                          {"q": query["q"], "sort": query["sort"], "order": "desc",
                           "per_page": 100, "page": page}, search=True)
        total = int(data.get("total_count") or 0)
        incomplete = incomplete or bool(data.get("incomplete_results"))
        batch = data.get("items") or []
        items.extend(batch)
        if len(batch) < 100 or len(items) >= min(total, 1000):
            break
    return items, {"label": query["label"], "mode": query["mode"], "q": query["q"],
                   "total": total, "fetched": len(items), "incomplete": incomplete}


def discover(gh: GitHub, cfg: dict, since: date) -> tuple[dict[str, dict], list[dict]]:
    """Run every query; return {full_name: record with `matched` labels} and coverage.

    A failing query is recorded and skipped; discovery fails only when every
    query does.
    """
    found: dict[str, dict] = {}
    coverage: list[dict] = []
    max_pages = int(cfg["search"].get("max_pages", 3))
    queries = build_queries(cfg, since)
    for query in queries:
        try:
            items, cov = run_search(gh, query, max_pages)
        except GitHubError as err:
            coverage.append({"label": query["label"], "mode": query["mode"],
                             "q": query["q"], "error": str(err)})
            continue
        coverage.append(cov)
        for item in items:
            rec = found.setdefault(item["full_name"], {**repo_record(item), "matched": []})
            if query["label"] not in rec["matched"]:
                rec["matched"].append(query["label"])
    if queries and all("error" in c for c in coverage):
        raise GitHubError(0, "/search/repositories",
                          message=f"all {len(queries)} queries failed; the first: {coverage[0]['error']}")
    return found, coverage


def merge_discovery(state: dict, found: dict[str, dict], scorer: Scorer, cfg: dict,
                    since: date, today: date) -> dict:
    """Fold relevant search hits into state.

    Returns the number of relevant hits and three lists of them: `new`
    (created in the window and not seen before), `spotted` (older, first seen
    now) and `rising` (seen before, with at least `rising_min_stars` more
    stars than last time). Forks and `ignore_owners` are skipped.
    """
    new, spotted, rising = [], [], []
    relevant = 0
    ignored = ignored_owner(cfg)
    for name, rec in found.items():
        if rec.get("fork") or ignored(name):
            continue
        score, why = scorer.score(rec)
        if score < scorer.min_score:
            continue
        relevant += 1
        prev = state["repos"].get(name)
        entry = {**remember(state, rec, score, why, today, "search"), "matched": rec["matched"]}
        if prev is None:
            created = (rec.get("created_at") or "")[:10]
            (new if created >= since.isoformat() else spotted).append(entry)
        else:
            gain = rec["stars"] - int(prev.get("stars") or 0)
            if gain >= int(cfg["digest"].get("rising_min_stars", 10)):
                rising.append({**entry, "gain": gain, "prev_seen": prev.get("last_seen")})
    by_score = lambda r: (-r["score"], -r["stars"], r["full_name"].lower())
    return {"relevant": relevant, "new": sorted(new, key=by_score), "spotted": sorted(spotted, key=by_score),
            "rising": sorted(rising, key=lambda r: (-r["gain"], r["full_name"].lower()))}


# --------------------------------------------------------------------------
# Watchlist: commits, releases and tags

def check_watchlist(gh: GitHub, names: list[str], state: dict, now: datetime,
                    max_commits: int) -> list[dict]:
    reports = []
    for name in names:
        try:
            reports.append(check_watched(gh, name, state["watch"], now, max_commits))
        except GitHubError as err:
            detail = "not found (renamed, deleted or private)" if err.status == 404 else str(err)
            reports.append({"repo": name, "error": detail})
    return reports


def check_watched(gh: GitHub, name: str, cursors: dict, now: datetime,
                  max_commits: int) -> dict:
    """What changed on one followed repo since its cursor.

    The first check only records a cursor. Commits are new down to the
    previous head of the default branch; a head missing from the latest 30
    means a busy day or rewritten history, reported as "30+".
    """
    info = gh.request("GET", f"/repos/{name}")
    rec = repo_record(info)
    cur = cursors.get(name)
    report: dict = {"repo": name, "record": rec, "first": cur is None, "commits": [],
                    "commit_count": 0, "more_commits": False, "releases": [], "tags": []}
    if rec["full_name"].lower() != name.lower():
        report["moved_to"] = rec["full_name"]
    if cur and cur.get("stars") is not None:
        report["stars_delta"] = rec["stars"] - int(cur["stars"])
    branch = info.get("default_branch") or "main"
    pushed = cur is None or rec["pushed_at"] != cur.get("pushed_at") or branch != cur.get("branch")
    new_cur = {"stars": rec["stars"], "pushed_at": rec["pushed_at"], "branch": branch,
               "head": (cur or {}).get("head"), "release_ids": (cur or {}).get("release_ids", []),
               "tags": (cur or {}).get("tags", []), "checked_at": now.isoformat()}

    if pushed:
        commits = gh.request("GET", f"/repos/{name}/commits", {"sha": branch, "per_page": 30}) or []
        if commits:
            new_cur["head"] = commits[0]["sha"]
            old_head = (cur or {}).get("head")
            if cur is not None and old_head and branch == cur.get("branch"):
                fresh = []
                for commit in commits:
                    if commit["sha"] == old_head:
                        break
                    fresh.append(commit)
                else:
                    report["more_commits"] = True
                report["commit_count"] = len(fresh)
                report["commits"] = [_commit_row(c) for c in fresh[:max_commits]]

    releases = [r for r in gh.request("GET", f"/repos/{name}/releases", {"per_page": 10}) or []
                if not r.get("draft")]
    seen_ids = set(new_cur["release_ids"])
    if cur is not None:
        report["releases"] = [_release_row(r) for r in releases if r["id"] not in seen_ids]
    current_ids = [r["id"] for r in releases]
    new_cur["release_ids"] = (current_ids + [i for i in new_cur["release_ids"] if i not in current_ids])[:50]

    if pushed:
        tags = [t["name"] for t in gh.request("GET", f"/repos/{name}/tags", {"per_page": 20}) or []]
        if cur is not None:
            known_tags = set(cur.get("tags", [])) | {r["tag_name"] for r in releases}
            report["tags"] = [t for t in tags if t not in known_tags]
        new_cur["tags"] = (tags + [t for t in new_cur["tags"] if t not in tags])[:60]

    cursors[name] = new_cur
    return report


def _commit_row(commit: dict) -> dict:
    meta = commit.get("commit") or {}
    author = (meta.get("author") or {}).get("name") or (commit.get("author") or {}).get("login") or ""
    lines = (meta.get("message") or "").strip().splitlines()
    return {"sha": commit["sha"][:7], "url": commit.get("html_url", ""),
            "message": lines[0][:120] if lines else "",
            "author": author, "date": ((meta.get("committer") or {}).get("date") or "")[:10]}


def _release_row(release: dict) -> dict:
    return {"tag": release.get("tag_name", ""), "name": release.get("name") or "",
            "url": release.get("html_url", ""), "prerelease": bool(release.get("prerelease")),
            "date": (release.get("published_at") or "")[:10]}


# --------------------------------------------------------------------------
# GH Archive

TYPE_RE = re.compile(rb'"type":"([A-Za-z]+)"')
REPO_RE = re.compile(rb'"repo":\{"id":\d+,"name":"([^"]+)"')
ACTIVITY = {"PullRequestEvent": "prs", "IssuesEvent": "issues", "IssueCommentEvent": "comments",
            "PullRequestReviewEvent": "comments", "PullRequestReviewCommentEvent": "comments"}


def archive_lines(day: date, hour: int) -> Iterable[bytes]:
    url = ARCHIVE_URL.format(day=day.isoformat(), hour=hour)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as resp, gzip.GzipFile(fileobj=resp) as fh:
        yield from fh


@dataclass
class HourScan:
    hour: int
    ok: bool = True
    events: int = 0
    types: Counter = field(default_factory=Counter)
    hits: list[dict] = field(default_factory=list)
    error: str | None = None


def event_hit(event: dict) -> dict:
    """The few fields of a matching event that the aggregates use."""
    payload = event.get("payload") or {}
    hit = {"repo": event["repo"]["name"], "type": event.get("type"),
           "actor": (event.get("actor") or {}).get("login")}
    if hit["type"] == "ReleaseEvent":
        release = payload.get("release") or {}
        hit["tag"] = release.get("tag_name")
        hit["url"] = release.get("html_url")
    elif hit["type"] == "CreateEvent":
        hit["ref_type"] = payload.get("ref_type")
        hit["ref"] = payload.get("ref")
    return hit


def scan_hour(day: date, hour: int, matches: Callable[[str], bool],
              lines_for: Callable[[date, int], Iterable[bytes]] | None = None,
              attempts: int = 3, sleep: Callable[[float], None] = time.sleep) -> HourScan:
    """Count every event; parse only the ones whose repo name `matches`.

    Type and repo name are read with byte regexes, so the JSON parser runs
    on a few hundred lines an hour rather than on all of them.
    """
    lines_for = lines_for or archive_lines
    error = ""
    for attempt in range(attempts):
        scan = HourScan(hour)
        try:
            for line in lines_for(day, hour):
                scan.events += 1
                kind = TYPE_RE.search(line, 0, 200)
                scan.types[kind.group(1).decode() if kind else "unknown"] += 1
                repo = REPO_RE.search(line)
                if repo and matches(repo.group(1).decode("utf-8", "replace")):
                    try:
                        scan.hits.append(event_hit(json.loads(line)))
                    except (ValueError, KeyError, TypeError):
                        scan.types["malformed"] += 1
            return scan
        except urllib.error.HTTPError as err:
            if err.code == 404:
                return HourScan(hour, ok=False, error="not published")
            error = f"HTTP {err.code}"
        except (urllib.error.URLError, OSError, EOFError, zlib.error,
                http.client.HTTPException) as err:
            error = f"{type(err).__name__}: {err}"
        if attempt + 1 < attempts:
            sleep(2 ** attempt)
    return HourScan(hour, ok=False, error=error)


def scan_day(day: date, matches: Callable[[str], bool], workers: int = 4,
             lines_for: Callable[[date, int], Iterable[bytes]] | None = None) -> dict:
    with ThreadPoolExecutor(max_workers=workers) as pool:
        hours = list(pool.map(lambda h: scan_hour(day, h, matches, lines_for), range(24)))
    types: Counter = Counter()
    for scan in hours:
        types.update(scan.types)
    return {"day": day.isoformat(),
            "hours_ok": sum(s.ok for s in hours),
            "hours_missing": {s.hour: s.error for s in hours if not s.ok},
            "events": sum(s.events for s in hours),
            "types": dict(types.most_common()),
            "repos": aggregate(hit for scan in hours for hit in scan.hits)}


def aggregate(hits: Iterable[dict]) -> dict[str, dict]:
    repos: dict[str, dict] = {}
    actors: dict[str, set] = {}
    for hit in hits:
        name = hit["repo"]
        agg = repos.setdefault(name, {"events": 0, "stars": 0, "forks": 0, "pushes": 0,
                                      "prs": 0, "issues": 0, "comments": 0, "releases": [],
                                      "tags": [], "made_public": False, "created": False})
        agg["events"] += 1
        actors.setdefault(name, set()).add(hit.get("actor"))
        kind = hit.get("type")
        if kind == "WatchEvent":
            agg["stars"] += 1
        elif kind == "ForkEvent":
            agg["forks"] += 1
        elif kind == "PushEvent":
            agg["pushes"] += 1
        elif kind == "PublicEvent":
            agg["made_public"] = True
        elif kind == "ReleaseEvent" and hit.get("tag"):
            if all(r["tag"] != hit["tag"] for r in agg["releases"]):
                agg["releases"].append({"tag": hit["tag"], "url": hit.get("url") or ""})
        elif kind == "CreateEvent":
            if hit.get("ref_type") == "repository":
                agg["created"] = True
            elif hit.get("ref_type") == "tag" and hit.get("ref") not in agg["tags"]:
                agg["tags"].append(hit["ref"])
        elif kind in ACTIVITY:
            agg[ACTIVITY[kind]] += 1
    for name, agg in repos.items():
        agg["actors"] = len(actors[name] - {None})
    return repos


def name_words(full_name: str) -> str:
    """The repo name (not the owner) as lowercase words: `ECDLPSolver_gpu` -> `ecdlp solver gpu`.

    Archive patterns match whole words of this, so `falcon` does not fire on
    `falconfix` and an owner called `...Lattice` does not make its repos leads.
    """
    name = full_name.partition("/")[2]
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name)
    return " ".join(w for w in re.split(r"[^A-Za-z0-9]+", name) if w).lower()


def ignored_owner(cfg: dict) -> Callable[[str], bool]:
    owners = {o.lower() for o in cfg["search"].get("ignore_owners", [])}
    return lambda full_name: full_name.partition("/")[0].lower() in owners


def archive_matcher(cfg: dict, known: Iterable[str]) -> Callable[[str], bool]:
    pattern = re.compile(cfg["archive"].get("name_pattern", r"\bcrypt"), re.I)
    known_lower = {name.lower() for name in known}
    ignored = ignored_owner(cfg)
    return lambda name: name.lower() in known_lower or (
        not ignored(name) and bool(pattern.search(name_words(name))))


def archive_days(state: dict, today: date, catch_up: int) -> list[date]:
    """Days not yet scanned, up to yesterday, at most `catch_up` of them."""
    yesterday = today - timedelta(days=1)
    last = state["meta"].get("last_archive_day")
    start = date.fromisoformat(last) + timedelta(days=1) if last else yesterday
    start = max(start, yesterday - timedelta(days=catch_up - 1))
    return [start + timedelta(days=i) for i in range((yesterday - start).days + 1)]


def enrich(gh: GitHub, day_result: dict, state: dict, scorer: Scorer, cfg: dict,
           today: date) -> list[dict]:
    """Look up archive-only repos and keep the relevant ones.

    Archive events carry no description or topics, so a name match is only a
    lead. Leads are ranked (made public or created, then releases, stars,
    events) and the top `enrich_limit` are fetched and scored like search
    hits. Irrelevant ones are not fetched again for 30 days.
    """
    arch = cfg["archive"]
    known = {n.lower() for n in state["repos"]} | {n.lower() for n in watchlist(cfg)}
    known |= {n.lower() for n in state["rejected"]}
    min_events = int(arch.get("min_events", 2))
    leads = [(name, agg) for name, agg in day_result["repos"].items()
             if name.lower() not in known
             and (agg["made_public"] or agg["created"] or agg["releases"] or agg["events"] >= min_events)]
    leads.sort(key=lambda item: (-(item[1]["made_public"] or item[1]["created"]),
                                 -len(item[1]["releases"]), -item[1]["stars"],
                                 -item[1]["events"], item[0].lower()))
    kept = []
    for name, agg in leads[: int(arch.get("enrich_limit", 40))]:
        try:
            info = gh.request("GET", f"/repos/{name}")
        except GitHubError as err:
            if err.status in (404, 403, 451):
                state["rejected"][name] = today.isoformat()
                continue
            raise
        rec = repo_record(info)
        score, why = scorer.score(rec)
        if rec["fork"] or score < scorer.min_score:
            state["rejected"][name] = today.isoformat()
            continue
        entry = remember(state, rec, score, why, today, "archive")
        kept.append({**entry, "archive": agg})
    return kept


def summarize_archive(result: dict, spotted: list[dict], state: dict, cfg: dict) -> dict:
    """The digest's view of one archive day: coverage plus the notable repos."""
    known = {n.lower(): n for n in state["repos"]}
    known.update({n.lower(): n for n in watchlist(cfg)})
    repos = result["repos"]
    tracked = {n: a for n, a in repos.items() if n.lower() in known}
    expected = ("PushEvent", "CreateEvent", "WatchEvent", "ReleaseEvent")
    spotted_names = {r["full_name"].lower() for r in spotted}
    return {
        "day": result["day"], "hours_ok": result["hours_ok"],
        "hours_missing": result["hours_missing"], "events": result["events"],
        "types": result["types"],
        "absent_types": [t for t in expected if not result["types"].get(t)],
        "matched": len(repos), "spotted": spotted,
        "made_public": sorted(n for n, a in tracked.items()
                              if (a["made_public"] or a["created"]) and n.lower() not in spotted_names),
        "tracked_activity": sorted(
            ({"repo": n, **a} for n, a in tracked.items() if n.lower() not in spotted_names),
            key=lambda r: (-r["stars"], -r["forks"], -r["events"], r["repo"].lower())),
    }


# --------------------------------------------------------------------------
# Digest

_MD_SPECIAL = re.compile(r"([\\`*_\[\]<>|~])")


def md_text(value: Any, limit: int = 140) -> str:
    """Render untrusted text inert: one line, markdown escaped, no mentions.

    Descriptions and commit messages come from strangers. A zero-width space
    after `@` and `#` keeps them from pinging users, cross-referencing other
    repos' issues, or waking the `@claude` workflow when posted in an issue.
    """
    text = " ".join(str(value or "").split())
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    text = _MD_SPECIAL.sub(r"\\\1", text)
    return text.replace("@", "@\u200b").replace("#", "#\u200b")


def code_text(value: Any, limit: int = 60) -> str:
    """Untrusted text as an inline code span, where markdown and mentions are inert."""
    text = " ".join(str(value or "").replace("`", "'").split())
    if len(text) > limit:
        text = text[: limit - 1] + "…"
    return f"`{text}`" if text else ""


def repo_link(name: str) -> str:
    if REPO_NAME.match(name):
        return f"[{name}](https://github.com/{name})"
    return md_text(name)


def _stars(n: int) -> str:
    return f"★ {n:,}"


def _repo_table(rows: list[dict], limit: int, extra: Callable[[dict], str] | None = None,
                extra_head: str = "") -> list[str]:
    head = "| Repository | Stars | Language | Score | Why | Description |"
    sep = "|---|---:|---|---:|---|---|"
    if extra:
        head = f"| Repository | Stars | {extra_head} | Language | Score | Why | Description |"
        sep = "|---|---:|---:|---|---:|---|---|"
    lines = [head, sep]
    for row in rows[:limit]:
        cells = [repo_link(row["full_name"]), f"{row['stars']:,}"]
        if extra:
            cells.append(extra(row))
        cells += [md_text(row.get("language") or "", 20), str(row["score"]),
                  md_text(", ".join(row.get("why", [])[:5]), 60), md_text(row.get("description"), 140)]
        lines.append("| " + " | ".join(cells) + " |")
    if len(rows) > limit:
        lines.append(f"\n…and {len(rows) - limit} more, recorded in `state.json`.")
    return lines


def count_items(digest: dict) -> int:
    """Things worth a notification: watch activity, new or rising repos, archive finds."""
    total = 0
    for report in digest.get("watch") or []:
        total += bool(report.get("commit_count") or report.get("releases") or report.get("tags")
                      or report.get("moved_to") or report.get("error"))
    disc = digest.get("discover") or {}
    total += len(disc.get("new", [])) + len(disc.get("spotted", [])) + len(disc.get("rising", []))
    for day in digest.get("archive") or []:
        total += len(day["spotted"]) + len(day["made_public"])
        total += sum(bool(r["releases"]) for r in day["tracked_activity"])
    return total


def render_digest(digest: dict, cfg: dict) -> str:
    limit = int(cfg["digest"].get("max_rows", 30))
    out = [f"# Crypto repo radar · {digest['date']}", ""]
    disc = digest.get("discover")
    parts = []
    if disc:
        parts.append(f"search since {disc['since']}: {disc['relevant']} relevant of {disc['seen']} hits")
    if digest.get("watch") is not None:
        parts.append(f"{len(digest['watch'])} followed repos")
    for day in digest.get("archive") or []:
        parts.append(f"GH Archive {day['day']}: {day['events']:,} events, {day['hours_ok']}/24 hours")
    out.append(" · ".join(parts) + ".")
    if digest.get("baseline"):
        out += ["", ("First run: everything found was recorded as a baseline. Later digests "
                     "list only repos new to the radar, star jumps, and activity on followed repos.")]
    if digest.get("problems"):
        out += ["", "> [!WARNING]"] + [f"> {md_text(p, 400)}" for p in digest["problems"]]

    watch = digest.get("watch")
    if watch is not None:
        out += ["", "## Followed repositories"]
        active = [r for r in watch if r.get("commit_count") or r.get("releases") or r.get("tags")
                  or r.get("moved_to") or r.get("error")]
        for report in active:
            out += [""] + _watch_lines(report, int(cfg["watch"].get("max_commits", 10)))
        quiet = [r["repo"] for r in watch if r not in active and not r.get("first")]
        started = [r["repo"] for r in watch if r.get("first") and not r.get("error")]
        if not active:
            out += ["", "No new commits, releases or tags."]
        if quiet:
            out += ["", "Quiet: " + ", ".join(repo_link(n) for n in quiet) + "."]
        if started:
            out += ["", ("Now following (activity is reported from the next run): "
                         + ", ".join(repo_link(n) for n in started) + ".")]

    if disc:
        out += ["", f"## New repositories (created since {disc['since']})", ""]
        out += _repo_table(disc["new"], limit) if disc["new"] else ["None."]
        heading = "Already active (baseline)" if digest.get("baseline") else "Newly spotted (older repos, first seen today)"
        out += ["", f"## {heading}", ""]
        out += _repo_table(disc["spotted"], limit) if disc["spotted"] else ["None."]
        if disc["rising"]:
            out += ["", "## Rising (star gains since last seen)", ""]
            out += _repo_table(disc["rising"], limit, lambda r: f"+{r['gain']:,}", "Gain")

    for day in digest.get("archive") or []:
        out += ["", f"## GH Archive · {day['day']}", ""]
        note = (f"{day['hours_ok']}/24 hours, {day['events']:,} public events, "
                f"{day['matched']:,} repos matching the name pattern or already tracked.")
        if day["absent_types"]:
            note += (f" The feed held no {', '.join(day['absent_types'])} this day, so pushes and "
                     "repo creation cannot be seen here; search still covers them.")
        out.append(note + " Stars and forks count the events in the feed, a sample of the true totals.")
        if day["spotted"]:
            out += ["", "**New to the radar** (name matched, then scored after an API lookup):", ""]
            out += _repo_table(day["spotted"], limit,
                               lambda r: f"{r['archive']['stars']}★ {r['archive']['forks']}⑂"
                               + (" public" if r["archive"]["made_public"] or r["archive"]["created"] else ""),
                               "That day")
        if day["made_public"]:
            out += ["", "**Made public or created:** " + ", ".join(repo_link(n) for n in day["made_public"]) + "."]
        releases = [r for r in day["tracked_activity"] if r["releases"]]
        if releases:
            out += ["", "**Releases on tracked repos:**"]
            out += [f"- {repo_link(r['repo'])}: " + ", ".join(
                f"[{md_text(rel['tag'], 40)}]({rel['url']})" if rel["url"].startswith("https://github.com/")
                else md_text(rel["tag"], 40) for rel in r["releases"]) for r in releases]
        busiest = [r for r in day["tracked_activity"] if r["stars"] or r["forks"] or r["pushes"] or r["prs"]]
        if busiest:
            out += ["", "**Most active tracked repos:**", "",
                    "| Repository | Stars | Forks | Pushes | PRs | Issues | People |",
                    "|---|---:|---:|---:|---:|---:|---:|"]
            out += [f"| {repo_link(r['repo'])} | {r['stars']} | {r['forks']} | {r['pushes']} | "
                    f"{r['prs']} | {r['issues']} | {r['actors']} |" for r in busiest[:15]]

    out += ["", "<details><summary>Coverage</summary>", ""]
    if disc:
        out += ["| Query | Mode | Total | Fetched | Note |", "|---|---|---:|---:|---|"]
        for cov in disc["coverage"]:
            note = cov.get("error", "")
            if not note and cov["total"] > cov["fetched"]:
                note = "truncated: raise max_pages or narrow the query"
            if cov.get("incomplete"):
                note = (note + "; " if note else "") + "GitHub returned incomplete results"
            out.append(f"| `{cov['q'].replace('|', '/')}` | {cov['mode']} | {cov.get('total', 0):,} | "
                       f"{cov.get('fetched', 0):,} | {md_text(note, 200)} |")
    for day in digest.get("archive") or []:
        types = ", ".join(f"{k} {v:,}" for k, v in day["types"].items())
        out += ["", f"GH Archive {day['day']} event types: {types or 'none'}."]
        if day["hours_missing"]:
            out.append("Missing hours: " + ", ".join(f"{h} ({md_text(e, 60)})" for h, e in day["hours_missing"].items()) + ".")
    calls = digest.get("api_calls") or {}
    out += ["", (f"API calls: {calls.get('search', 0)} search, {calls.get('core', 0)} core. "
                 f"Generated {digest['generated']} by `tools/repo_radar.py`."), "", "</details>", ""]
    return "\n".join(out)


def _watch_lines(report: dict, max_commits: int) -> list[str]:
    name = report["repo"]
    if report.get("error"):
        return [f"**{repo_link(name)}**: {md_text(report['error'], 200)}"]
    rec = report["record"]
    head = f"**{repo_link(rec['full_name'])}** {_stars(rec['stars'])}"
    if report.get("stars_delta"):
        head += f" ({report['stars_delta']:+,})"
    if report.get("moved_to"):
        head += f" · renamed from {code_text(name, 80)}; update the watchlist"
    count = report.get("commit_count") or 0
    if count:
        more = "+" if report.get("more_commits") else ""
        head += f" · {count}{more} new commit{'s' if count != 1 or more else ''}"
    lines = [head]
    for c in report.get("commits", [])[:max_commits]:
        sha = f"[`{c['sha']}`]({c['url']})" if c["url"].startswith("https://github.com/") else f"`{c['sha']}`"
        lines.append(f"- {sha} {md_text(c['message'], 100)} · {md_text(c['author'], 40)}, {c['date']}")
    if count > max_commits:
        lines.append(f"- …and {count - max_commits}{'+' if report.get('more_commits') else ''} more")
    for rel in report.get("releases", []):
        label = md_text(rel["name"] or rel["tag"], 80)
        link = f"[{label}]({rel['url']})" if rel["url"].startswith("https://github.com/") else label
        lines.append(f"- Release {link}{' (pre-release)' if rel['prerelease'] else ''}, {rel['date']}")
    if report.get("tags"):
        lines.append("- New tags: " + ", ".join(code_text(t, 40) for t in report["tags"][:10]))
    return lines


def opml(names: list[str], title: str = "Crypto repo radar") -> str:
    """Atom feeds (releases, commits, tags) for each followed repo, as OPML."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<opml version="2.0">',
             f"  <head><title>{title}</title></head>", "  <body>"]
    for name in names:
        lines.append(f"    <outline text={quoteattr(name)}>")
        for kind in ("releases", "commits", "tags"):
            url = f"https://github.com/{name}/{kind}.atom"
            lines.append(f"      <outline type=\"rss\" text={quoteattr(f'{name} {kind}')} "
                         f"xmlUrl={quoteattr(url)} htmlUrl={quoteattr(f'https://github.com/{name}')}/>")
        lines.append("    </outline>")
    lines += ["  </body>", "</opml>", ""]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Issue delivery

def fit_issue_body(body: str, full_url: str, limit: int = ISSUE_BODY_LIMIT) -> str:
    if len(body) <= limit:
        return body
    note = f"\n\n*Truncated; the full digest is [on the state branch]({full_url}).*\n"
    cut = body.rfind("\n## ", 0, limit - len(note))
    if cut <= 0:
        cut = body.rfind("\n", 0, limit - len(note))
    return body[:cut] + note


def publish_issue(gh: GitHub, repo: str, title: str, body: str, label: str = ISSUE_LABEL) -> str:
    """Open today's digest issue and close the previous ones.

    Opening an issue is what notifies the repository's watchers by email, so
    one issue a day is the delivery channel; the closed ones are the archive.
    """
    try:
        gh.request("GET", f"/repos/{repo}/labels/{urllib.parse.quote(label)}")
    except GitHubError as err:
        if err.status != 404:
            raise
        gh.request("POST", f"/repos/{repo}/labels",
                   body={"name": label, "color": "5319e7",
                         "description": "Daily digest from tools/repo_radar.py"})
    previous = gh.request("GET", f"/repos/{repo}/issues",
                          {"labels": label, "state": "open", "per_page": 30}) or []
    created = gh.request("POST", f"/repos/{repo}/issues",
                         body={"title": title, "body": body, "labels": [label]})
    for issue in previous:
        if "pull_request" not in issue and issue["number"] != created["number"]:
            gh.request("PATCH", f"/repos/{repo}/issues/{issue['number']}",
                       body={"state": "closed", "state_reason": "completed"})
    return created["html_url"]


# --------------------------------------------------------------------------
# Commands

STATE_README = """# Repo radar state

Written by `tools/repo_radar.py` from the `repo-radar` workflow on `main`; see
`docs/repo-radar.md` there. This orphan branch is never merged.

- `state.json`: repos the radar has judged relevant, watch cursors, run dates.
- `digests/DATE.md`: each day's digest, also posted as a `repo-radar` issue.
- `archive/DATE.json`: per-day GH Archive aggregates for matching and tracked repos.
- `feeds.opml`: Atom feeds of the followed repos, for an RSS reader.
"""


def cmd_run(args: argparse.Namespace) -> int:
    cfg = load_config(Path(args.config))
    state_dir = Path(args.state_dir)
    state = load_state(state_dir)
    gh = GitHub.from_env()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    today = now.date()
    scorer = Scorer.from_config(cfg)
    steps = set(args.only or ("discover", "watch", "archive"))
    digest: dict = {"date": today.isoformat(), "generated": now.isoformat(),
                    "baseline": "discover" in steps and not state["meta"].get("last_discovery"),
                    "problems": []}

    if "discover" in steps:
        since = window_start(state, cfg, today)
        try:
            found, coverage = discover(gh, cfg, since)
            changes = merge_discovery(state, found, scorer, cfg, since, today)
            digest["discover"] = {"since": since.isoformat(), "seen": len(found),
                                  "coverage": coverage, **changes}
            failed = [c for c in coverage if "error" in c]
            if failed:
                digest["problems"].append(f"{len(failed)} of {len(coverage)} search queries failed; see Coverage.")
            state["meta"]["last_discovery"] = today.isoformat()
        except GitHubError as err:
            digest["problems"].append(f"Search failed: {err}")

    if "watch" in steps:
        names = watchlist(cfg)
        digest["watch"] = check_watchlist(gh, names, state, now, int(cfg["watch"].get("max_commits", 10)))
        errors = [r for r in digest["watch"] if r.get("error")]
        if errors and len(errors) == len(names):
            digest["problems"].append("Every followed repo failed to load; check the token.")

    if "archive" in steps:
        days = [date.fromisoformat(args.archive_day)] if args.archive_day else \
            archive_days(state, today, int(cfg["archive"].get("catch_up_days", 3)))
        digest["archive"] = []
        for day in days:
            matches = archive_matcher(cfg, list(state["repos"]) + watchlist(cfg))
            result = scan_day(day, matches, workers=int(cfg["archive"].get("workers", 4)))
            if not result["hours_ok"]:
                digest["problems"].append(f"GH Archive {day}: no hours could be read; it will be retried.")
                break
            # GH Archive occasionally lacks an hour; the Coverage section lists
            # those. Only a large gap is a problem worth a red job.
            if len(result["hours_missing"]) > 4:
                digest["problems"].append(f"GH Archive {day}: {len(result['hours_missing'])} of 24 hours unreadable.")
            try:
                spotted = enrich(gh, result, state, scorer, cfg, today)
            except GitHubError as err:
                digest["problems"].append(f"GH Archive {day}: lookups failed: {err}")
                spotted = []
            archive_dir = state_dir / "archive"
            archive_dir.mkdir(parents=True, exist_ok=True)
            (archive_dir / f"{day}.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
            digest["archive"].append(summarize_archive(result, spotted, state, cfg))
            if not args.archive_day:
                state["meta"]["last_archive_day"] = day.isoformat()

    prune(state, today, cfg)
    state["meta"]["last_run"] = now.isoformat()
    digest["api_calls"] = dict(gh.calls)
    digest["items"] = count_items(digest)

    digest_dir = state_dir / "digests"
    digest_dir.mkdir(parents=True, exist_ok=True)
    text = render_digest(digest, cfg)
    (digest_dir / f"{today}.md").write_text(text)
    (digest_dir / f"{today}.json").write_text(json.dumps(
        {"date": today.isoformat(), "items": digest["items"], "problems": digest["problems"],
         "baseline": digest["baseline"]}, indent=1) + "\n")
    (state_dir / "feeds.opml").write_text(opml(watchlist(cfg)))
    if not (state_dir / "README.md").exists():
        (state_dir / "README.md").write_text(STATE_README)
    save_state(state_dir, state)
    print(f"{digest_dir / f'{today}.md'}: {digest['items']} items, {len(digest['problems'])} problems")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
            fh.write(f"date={today}\n")
    for problem in digest["problems"]:
        print(f"::warning::{problem}", file=sys.stderr)
    return 2 if digest["problems"] else 0


def cmd_publish_issue(args: argparse.Namespace) -> int:
    day = args.date or datetime.now(timezone.utc).date().isoformat()
    digest_dir = Path(args.state_dir) / "digests"
    meta = json.loads((digest_dir / f"{day}.json").read_text())
    if not args.always and not meta["items"] and not meta["problems"] and not meta["baseline"]:
        print(f"{day}: nothing new; no issue opened")
        return 0
    full_url = f"https://github.com/{args.repo}/blob/{STATE_BRANCH}/digests/{day}.md"
    body = fit_issue_body((digest_dir / f"{day}.md").read_text(), full_url)
    count = meta["items"]
    title = f"Repo radar {day}: {count} item{'s' if count != 1 else ''}"
    print(publish_issue(GitHub.from_env(), args.repo, title, body))
    return 0


def cmd_archive(args: argparse.Namespace) -> int:
    """Ad-hoc GH Archive analysis over a range of days; changes no state."""
    cfg = load_config(Path(args.config))
    known = watchlist(cfg)
    if args.state_dir:
        known += list(load_state(Path(args.state_dir))["repos"])
    matches = archive_matcher(cfg, known)
    start = date.fromisoformat(args.day)
    results = []
    for i in range(args.days):
        day = start + timedelta(days=i)
        result = scan_day(day, matches, workers=args.workers)
        print(f"{day}: {result['hours_ok']}/24 hours, {result['events']:,} events, "
              f"{len(result['repos']):,} matching repos", file=sys.stderr)
        results.append(result)
    combined: dict[str, dict] = {}
    for result in results:
        for name, agg in result["repos"].items():
            total = combined.setdefault(name, Counter())
            total.update({k: v for k, v in agg.items() if isinstance(v, int) and not isinstance(v, bool)})
            total["releases"] += len(agg["releases"])
            total["made_public"] += int(agg["made_public"] or agg["created"])
    if args.json:
        Path(args.json).write_text(json.dumps({"days": results}, indent=1, sort_keys=True) + "\n")
    ranked = sorted(combined.items(), key=lambda kv: (-kv[1][args.sort], -kv[1]["events"], kv[0].lower()))
    print("| Repository | Events | Stars | Forks | Pushes | Releases | Public |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for name, c in ranked[: args.top]:
        print(f"| {name} | {c['events']} | {c['stars']} | {c['forks']} | {c['pushes']} | "
              f"{c['releases']} | {'yes' if c['made_public'] else ''} |")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    cfg = load_config(Path(args.config))
    scorer = Scorer.from_config(cfg)
    gh = GitHub.from_env()
    for name in args.repos:
        rec = repo_record(gh.request("GET", f"/repos/{name}"))
        score, why = scorer.score(rec)
        verdict = "relevant" if score >= scorer.min_score else f"below min_score {scorer.min_score}"
        print(f"{rec['full_name']}: {score} ({verdict}) {', '.join(why) or 'no matches'}")
        print(f"  topics: {', '.join(rec['topics']) or '-'}; description: {rec['description'] or '-'}")
    return 0


def cmd_opml(args: argparse.Namespace) -> int:
    sys.stdout.write(opml(watchlist(load_config(Path(args.config)))))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--config", default=str(DEFAULT_CONFIG), help="radar TOML (default: %(default)s)")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", parents=[common], help="search, check followed repos, scan GH Archive, write the digest")
    run.add_argument("--state-dir", required=True)
    run.add_argument("--only", action="append", choices=("discover", "watch", "archive"),
                     help="run only these steps (repeatable)")
    run.add_argument("--archive-day", help="scan this UTC day instead of the days not yet scanned")
    run.set_defaults(func=cmd_run)

    issue = sub.add_parser("publish-issue", parents=[common], help="post a written digest as a GitHub issue")
    issue.add_argument("--state-dir", required=True)
    issue.add_argument("--repo", required=True, help="OWNER/REPO to open the issue in")
    issue.add_argument("--date", help="digest date (default: today, UTC)")
    issue.add_argument("--always", action="store_true", help="open an issue even on a quiet day")
    issue.set_defaults(func=cmd_publish_issue)

    arch = sub.add_parser("archive", parents=[common], help="ad-hoc GH Archive scan over a range of days")
    arch.add_argument("--day", required=True, help="first UTC day, YYYY-MM-DD")
    arch.add_argument("--days", type=int, default=1)
    arch.add_argument("--state-dir", help="also count repos remembered in this state")
    arch.add_argument("--sort", default="stars",
                      choices=("stars", "events", "forks", "pushes", "releases", "made_public"))
    arch.add_argument("--top", type=int, default=40)
    arch.add_argument("--workers", type=int, default=4)
    arch.add_argument("--json", help="write the per-day aggregates here")
    arch.set_defaults(func=cmd_archive)

    score = sub.add_parser("score", parents=[common], help="show how repos score against the config")
    score.add_argument("repos", nargs="+", metavar="OWNER/REPO")
    score.set_defaults(func=cmd_score)

    feeds = sub.add_parser("opml", parents=[common], help="print Atom feeds of the followed repos as OPML")
    feeds.set_defaults(func=cmd_opml)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
