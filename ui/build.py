"""Build the dashboard as a static site, for GitHub Pages.

    python3 -m ui.build --out site
    make ui-build

GitHub Pages serves files; it cannot run a query. So this writes out the
same data contract `ui/server.py` serves (`ui/payloads.py`), one file per
thing a reader can open, and the browser does every filter, sort and search
locally over `data/index.json`. The published site and the local server run
the SAME `app.js` against the SAME paths -- the only difference is whether
a file was written by this script or computed on request.

What a snapshot is, and what it is not
--------------------------------------
The published site is the corpus AT ONE COMMIT. `data/meta.json` carries
that commit and the build time, the page shows both, and every record links
to its source on GitHub at that exact sha. It is not live and does not
claim to be: a reader comparing it against a working tree needs to know
which commit they are looking at, and a static page that implied freshness
would mislead on exactly the point that matters.

Source text is deliberately NOT bundled. 116 MB of YAML would triple the
site for bytes that are one click away on GitHub, permalinked to the built
commit and syntax-highlighted there. The local server still inlines it,
because it costs nothing to read a file that is already on disk.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import payloads
from .index import ResearchIndex

STATIC_DIR = Path(__file__).resolve().parent / "static"


def _git(repo: Path, *args: str) -> str:
    try:
        out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                             text=True, timeout=30, check=False)
        return out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def resolve_commit(repo: Path) -> str:
    """The sha the site is built from.

    In Actions `GITHUB_SHA` is authoritative -- the checkout may be a
    detached merge commit whose `HEAD` is not the sha anyone can browse.
    """
    return os.environ.get("GITHUB_SHA") or _git(repo, "rev-parse", "HEAD")


def resolve_repo_url(repo: Path) -> str:
    """The https URL every source link is built from.

    `GITHUB_REPOSITORY` in Actions; otherwise the origin remote, normalised
    from either the ssh or https form. Empty if there is no remote, in which
    case the page simply shows no source links rather than broken ones.
    """
    slug = os.environ.get("GITHUB_REPOSITORY")
    if slug:
        server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
        return f"{server.rstrip('/')}/{slug}"
    remote = _git(repo, "remote", "get-url", "origin")
    if not remote:
        return ""
    if remote.startswith("git@"):
        remote = "https://" + remote.split("@", 1)[1].replace(":", "/", 1)
    return remote.removesuffix(".git")


def write_json(path: Path, payload: Any) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    path.write_text(blob, encoding="utf-8")
    return len(blob.encode("utf-8"))


def build(repo: Path, out: Path, clean: bool = True,
          verbose: bool = True) -> dict[str, Any]:
    started = time.time()

    def say(message: str) -> None:
        if verbose:
            print(message, flush=True)

    say(f"indexing {repo}")
    index = ResearchIndex(repo).build()
    # The dashboard must not publish an unmeasured integrity report. The
    # sweep runs in a thread behind the live server; here it is the whole
    # point of the page, so it is waited for.
    say("  exact parse sweep (this is the slow part)")
    while index.deep_scan_state == "running":
        time.sleep(0.5)
    say(f"  {len(index.records)} records, {len(index.goals)} goals, "
        f"{len(index.experiments)} experiments, {len(index.findings)} findings")

    if clean and out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    for asset in sorted(STATIC_DIR.iterdir()):
        if asset.is_file():
            shutil.copy2(asset, out / asset.name)
    # Without this, Pages runs the content through Jekyll, which drops any
    # path beginning with an underscore and slows every deploy.
    (out / ".nojekyll").write_text("")

    data = out / "data"
    total = 0

    meta = payloads.meta_payload(
        index, mode="static",
        commit=resolve_commit(repo),
        repo_url=resolve_repo_url(repo),
        built_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))
    total += write_json(data / "meta.json", meta)
    total += write_json(data / "index.json", payloads.index_rows(index))
    total += write_json(data / "overview.json", payloads.overview_payload(index))
    total += write_json(data / "goals.json", payloads.goals_payload(index))
    total += write_json(data / "experiments.json", payloads.experiments_payload(index))
    total += write_json(data / "findings.json", payloads.findings_payload(index))
    total += write_json(data / "integrity.json", index.integrity)

    say("  goals")
    for goal in index.goals:
        total += write_json(data / "goals" / f"{goal.record_id}.json",
                            payloads.goal_payload(index, goal, detail=True))

    say(f"  {len(index.records)} record pages")
    for n, record_id in enumerate(index.records, 1):
        payload = payloads.record_payload(index, record_id, include_raw=False)
        total += write_json(data / "records" / f"{record_id}.json", payload)
        if verbose and n % 2000 == 0:
            say(f"    {n}/{len(index.records)}")

    say("  search shards")
    for kind, shard in payloads.search_shards(index).items():
        total += write_json(data / "search" / f"{kind}.json", shard)

    files = sum(1 for _ in out.rglob("*") if _.is_file())
    report = {
        "out": str(out),
        "files": files,
        "bytes": total,
        "megabytes": round(total / 1e6, 1),
        "seconds": round(time.time() - started, 1),
        "commit": meta["commit"],
        "repo_url": meta["repo_url"],
        "records": len(index.records),
        "unparseable": len(index.integrity.get("unparseable", [])),
    }
    say(f"built {report['files']} files, {report['megabytes']} MB, "
        f"in {report['seconds']}s -> {out}")
    # GitHub Pages publishes at most 1 GB. Saying so at 40% is more useful
    # than failing a deploy at 100%.
    if total > 400e6:
        say(f"  WARNING: {report['megabytes']} MB is a large fraction of the "
            "1 GB GitHub Pages limit")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m ui.build",
        description="Build the read-only dashboard as a static site for GitHub Pages.")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out", type=Path, default=Path("site"),
                        help="output directory (default: ./site, gitignored)")
    parser.add_argument("--keep", action="store_true",
                        help="do not clear the output directory first")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--report", type=Path, help="also write the build report here")
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    if not (repo / "ledger").is_dir():
        parser.error(f"no ledger/ under {repo}: not a crypto-autoresearcher checkout")

    report = build(repo, args.out.resolve(), clean=not args.keep, verbose=not args.quiet)
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
