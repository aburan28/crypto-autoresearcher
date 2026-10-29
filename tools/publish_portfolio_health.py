#!/usr/bin/env python3
"""Publish a workflow-generated health cache on a review branch, never on main.

Only main-health.yml generates the real cache. This helper validates its source
binding and stages that one file. Push/API failures are fatal; the workflow
retains the generated artifact before invoking this helper. It never merges,
approves, rebases or force-pushes. Reconcile a partially published branch from
the printed receipt before retrying a failed publication.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

CACHE = "coordination/portfolio_health/latest.json"
SCHEMA = "crypto.autoresearch.portfolio_health_cache.v1"


def command(root: Path, *args: str) -> str:
    return subprocess.run(args, cwd=root, check=True, capture_output=True,
                          text=True).stdout.strip()


def git(root: Path, *args: str) -> str:
    return command(root, "git", *args)


def changed_paths(root: Path, *args: str) -> set[str]:
    result = subprocess.run(["git", "diff", "--name-only", "--no-renames", "-z", *args],
                            cwd=root, check=True, capture_output=True, text=True)
    return set(filter(None, result.stdout.split("\0")))


def cache_only_merge(root: Path) -> bool:
    """Only a nonempty, exact cache-only diff can suppress another sweep."""
    return changed_paths(root, "HEAD^1", "HEAD") == {CACHE}


def validate_cache(root: Path, source: str) -> tuple[bytes, dict]:
    if not re.fullmatch(r"[0-9a-f]{40}", source) or git(root, "rev-parse", "HEAD") != source:
        raise ValueError("source must be the full SHA of the checked-out commit")
    if git(root, "rev-parse", "--is-shallow-repository") != "false":
        raise ValueError("health publication requires full history")
    # The sweep's classification relies on files actually being present.
    sparse = subprocess.run(["git", "config", "--bool", "core.sparseCheckout"],
                            cwd=root, capture_output=True, text=True)
    if sparse.returncode not in (0, 1) or sparse.stdout.strip() == "true":
        raise ValueError("health publication requires a full checkout")
    if changed_paths(root, "--cached"):
        raise ValueError("refusing a nonempty staged index")
    if changed_paths(root) != {CACHE}:
        raise ValueError("only the generated cache may differ from the source tree")
    path = root / CACHE
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise ValueError("cache must be an ordinary file under ordinary directories")
    raw = path.read_bytes()
    cache = json.loads(raw)
    if (cache.get("schema") != SCHEMA or cache.get("commit") != source
            or cache.get("shallow_clone") is not False):
        raise ValueError("cache schema, commit or full-history binding is invalid")
    stamp = datetime.fromisoformat(cache["generated_at"])
    if stamp.tzinfo is None:
        raise ValueError("cache timestamp must include a timezone")
    goals = cache["goals"]
    if not isinstance(goals, list) or cache["active_goals"] != len(goals):
        raise ValueError("cache goal count does not match its rows")
    expected: dict[str, list[str]] = {}
    for goal in goals:
        expected.setdefault(goal["bucket"], []).append(goal["id"])
    actual = cache["buckets"]
    if not isinstance(actual, dict) or any(
        sorted(actual.get(bucket, [])) != sorted(expected.get(bucket, []))
        for bucket in set(actual) | set(expected)
    ):
        raise ValueError("cache bucket membership does not match its rows")
    return raw, cache


def publish(root: Path, *, source: str, repository: str, run_id: str,
            run_attempt: str) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("invalid repository name")
    if not re.fullmatch(r"[1-9][0-9]*", run_id) or not re.fullmatch(r"[1-9][0-9]*", run_attempt):
        raise ValueError("run identity must be positive integers")
    raw, cache = validate_cache(root, source)
    branch = f"health-cache/{source[:12]}-{run_id}-{run_attempt}"
    # A remote collision is a reconciliation condition, never permission to
    # replace an earlier receipt or create a second PR for the same attempt.
    if git(root, "ls-remote", "--heads", "origin", f"refs/heads/{branch}"):
        raise ValueError(f"publication branch already exists; reconcile {branch}")
    git(root, "switch", "-c", branch)
    git(root, "add", "--", CACHE)
    git(root, "-c", "user.name=main-health", "-c", "user.email=main-health@users.noreply.github.com",
        "commit", "-m", f"health: portfolio cache for {source}")
    commit = git(root, "rev-parse", "HEAD")
    if changed_paths(root, source, commit) != {CACHE}:
        raise ValueError("publication commit must change exactly the generated cache")
    receipt = {"source_commit": source, "cache_sha256": hashlib.sha256(raw).hexdigest(),
               "generated_at": cache["generated_at"], "branch": branch, "commit": commit,
               "run_url": f"https://github.com/{repository}/actions/runs/{run_id}"}
    print(json.dumps({**receipt, "state": "prepared"}), flush=True)
    git(root, "push", "origin", f"HEAD:refs/heads/{branch}")
    print(json.dumps({**receipt, "state": "branch_pushed"}), flush=True)
    body = (f"Generated by [main-health]({receipt['run_url']}) from source `{source}`.\n\n"
            f"Cache SHA-256: `{receipt['cache_sha256']}`. Generated at {cache['generated_at']}.\n\n"
            "This snapshot reports repository health; publication does not mean the absolute "
            "sweep passed. Inspect the linked run and the recorded repair/blocked buckets. "
            "Only the generated cache changes. Normal current-head CI and review gates apply; "
            "this workflow does not approve or merge the PR.\n\n"
            "GitHub may require a maintainer to approve workflows on a PR created by GITHUB_TOKEN. "
            "Pending checks must run successfully before merge.\n")
    with tempfile.TemporaryDirectory(prefix="health-pr-") as temp:
        body_path = Path(temp) / "body.md"
        body_path.write_text(body)
        url = command(root, "gh", "pr", "create", "--repo", repository,
                      "--base", "main", "--head", branch,
                      "--title", f"health: portfolio snapshot at {source[:12]}",
                      "--body-file", str(body_path))
    return {**receipt, "state": "pull_request_open", "url": url}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--cache-only-merge", action="store_true")
    parser.add_argument("--source")
    parser.add_argument("--repository")
    parser.add_argument("--run-id")
    parser.add_argument("--run-attempt")
    args = parser.parse_args()
    if args.cache_only_merge:
        print("true" if cache_only_merge(args.repo_root) else "false")
        return 0
    if not all((args.source, args.repository, args.run_id, args.run_attempt)):
        parser.error("publication requires source, repository, run-id and run-attempt")
    result = publish(args.repo_root, source=args.source, repository=args.repository,
                     run_id=args.run_id, run_attempt=args.run_attempt)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"health publication failed: {exc.cmd[0]} exited {exc.returncode}: "
              f"{(exc.stderr or '').strip()[:2000]}", file=sys.stderr)
        raise SystemExit(1)
    except (ValueError, KeyError, TypeError) as exc:
        print(f"health publication rejected: {exc}", file=sys.stderr)
        raise SystemExit(1)
