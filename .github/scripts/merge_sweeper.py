#!/usr/bin/env python3
"""Merge sweeper (.github/workflows/merge-sweeper.yml).

AGENTS.md ("Default workflow") lets the session that opened a PR merge it
once every applicable check on its head is green. Sessions end, though, and
their PRs stay open long after CI finished: on 2026-10-22 there were 187 open
PRs in this repository and about 1,000 queued workflow runs. The sweeper
applies the merge gate to every open PR on a schedule, and keeps CI demand
inside the runner capacity (docs/ci-tiers.md).

A PR is merged only when all of these hold on its current head:

  * not a draft, from this repository (no forks), based on the default branch
  * none of the hold labels (`do-not-merge`, `hold`, `needs-human`, `wip`,
    `autofix:running`, `merge-sweeper:off`, `ci:over-budget`)
  * GitHub reports it mergeable with `mergeable_state` `clean`
  * no reviewer's latest review is CHANGES_REQUESTED
  * at least one check run exists, every check run has completed, and each
    concluded success, neutral or skipped (cancelled, timed out, failed,
    action_required and stale are not a pass)
  * every legacy commit status is success
  * the full tier ran: the `full-tier` check (ci-tier.yml) succeeded on the
    head. A draft's gated jobs report `skipped`, so without this marker a
    draft-era head would look green. Heads whose checks all started before
    ci-tier.yml reached the default branch predate the tiers and ran in full.
  * at most --max-checks (default 30) checks ran on the head

The merge uses a merge commit and the head SHA the checks ran on, so a push
that lands between the read and the merge makes GitHub refuse it.

With --apply it also manages capacity labels, after merging. It never changes
whether a pull request is a draft or ready for review:

  * park: red, conflicted, over-budget or `needs-human` PRs get `ci:parked`
  * cap: PRs beyond --max-ready get `ci:waiting` for prioritization; they stay
    open and ready, and the label is cleared when they return within the cap

Standard library only; talks to the GitHub REST and GraphQL APIs with
$GH_TOKEN or $GITHUB_TOKEN (a token is optional for a public repository's
read-only report).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request

API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
PASS = {"success", "neutral", "skipped"}
FULL_TIER = "full-tier"
TIER_WORKFLOW = ".github/workflows/ci-tier.yml"
L_PARKED, L_WAITING, L_BUDGET = "ci:parked", "ci:waiting", "ci:over-budget"
HOLD_LABELS = {"do-not-merge", "hold", "needs-human", "wip",
               "autofix:running", "merge-sweeper:off", L_BUDGET}
# The sweeper's own check run does not gate a merge or count against a budget.
IGNORE_CHECKS = {"sweep", "merge-sweeper"}
PARK_BUCKETS = {"fail", "conflict", "over-budget"}


def api(method: str, path: str, body: dict | None = None) -> object:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    url = path if path.startswith("http") else f"{API}/{path}"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    cafile = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    ctx = ssl.create_default_context(cafile=cafile) if cafile else None
    with urllib.request.urlopen(req, context=ctx, timeout=60) as res:
        raw = res.read()
    return json.loads(raw) if raw.strip() else None


def paged(path: str, key: str | None = None, max_pages: int = 20) -> list:
    items: list = []
    sep = "&" if "?" in path else "?"
    for page in range(1, max_pages + 1):
        data = api("GET", f"{path}{sep}per_page=100&page={page}")
        batch = data[key] if key else data
        items.extend(batch)
        if len(batch) < 100:
            break
    return items


def parse_time(value: str | None) -> dt.datetime | None:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def pr_detail(repo: str, number: int) -> dict:
    # `mergeable` is computed lazily; the first read can return null.
    for attempt in range(3):
        pr = api("GET", f"repos/{repo}/pulls/{number}")
        if pr.get("mergeable") is not None:
            return pr
        time.sleep(3 * (attempt + 1))
    return pr


def tiers_since(repo: str, branch: str) -> dt.datetime | None:
    """When ci-tier.yml first reached the default branch (None: not yet)."""
    commits = paged(f"repos/{repo}/commits?sha={branch}&path={TIER_WORKFLOW}", max_pages=5)
    if not commits:
        return None
    return parse_time(commits[-1]["commit"]["committer"]["date"])


def blocking_reviews(reviews: list[dict]) -> list[str]:
    """Reviewers whose latest decisive review requests changes."""
    latest: dict[str, str] = {}
    for r in reviews:
        state = r.get("state")
        if state in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
            latest[(r.get("user") or {}).get("login", "?")] = state
    return sorted(u for u, s in latest.items() if s == "CHANGES_REQUESTED")


def check_verdict(runs: list[dict], statuses: list[dict]) -> tuple[str, list[str]]:
    """('pass' | 'pending' | 'fail' | 'none', names that keep it from passing).

    `runs` are the latest check runs of the head SHA, `statuses` the legacy
    commit statuses (newest first, as GitHub returns them).
    """
    runs = [r for r in runs if r.get("name") not in IGNORE_CHECKS]
    seen: set[str] = set()
    current = []
    for s in statuses:
        if s.get("context") not in seen:
            seen.add(s.get("context"))
            current.append(s)
    if not runs and not current:
        return "none", []
    pending = [r["name"] for r in runs if r.get("status") != "completed"]
    pending += [s["context"] for s in current if s.get("state") == "pending"]
    failed = [f"{r['name']} ({r.get('conclusion')})" for r in runs
              if r.get("status") == "completed" and r.get("conclusion") not in PASS]
    failed += [f"{s['context']} ({s.get('state')})" for s in current
               if s.get("state") in {"failure", "error"}]
    if failed:
        return "fail", sorted(failed)
    if pending:
        return "pending", sorted(pending)
    return "pass", []


def checks_ran(runs: list[dict]) -> int:
    """Checks that took a runner: everything but skipped and neutral ones."""
    return sum(1 for r in runs if r.get("name") not in IGNORE_CHECKS
               and r.get("conclusion") not in {"skipped", "neutral"})


def full_tier_missing(runs: list[dict], since: dt.datetime | None) -> bool:
    if since is None:
        return False
    if any(r.get("name") == FULL_TIER and r.get("conclusion") == "success" for r in runs):
        return False
    started = [parse_time(r.get("started_at")) for r in runs]
    return any(t is not None and t >= since for t in started)


def assess(repo: str, pr: dict, default_branch: str, *, max_checks: int = 30,
           since: dt.datetime | None = None) -> tuple[str, str]:
    """(bucket, reason). Bucket 'ready' means the merge gate is satisfied."""
    labels = {l["name"] for l in pr.get("labels", [])}
    if pr.get("draft"):
        return "draft", "draft"
    if (pr["head"].get("repo") or {}).get("full_name") != repo:
        return "held", "fork"
    if pr["base"]["ref"] != default_branch:
        return "held", f"based on {pr['base']['ref']}"
    if "needs-human" in labels:
        return "needs-human", "label needs-human"
    if held := sorted(labels & (HOLD_LABELS - {L_BUDGET})):
        return "held", "label " + ", ".join(held)

    sha = pr["head"]["sha"]
    runs = paged(f"repos/{repo}/commits/{sha}/check-runs?filter=latest", "check_runs")
    if (n := checks_ran(runs)) > max_checks:
        return "over-budget", f"{n} checks ran on the head (budget {max_checks})"
    if L_BUDGET in labels:
        return "held", f"label {L_BUDGET}"
    statuses = paged(f"repos/{repo}/commits/{sha}/statuses")
    verdict, names = check_verdict(runs, statuses)
    if verdict == "none":
        return "pending", "no checks reported on the head"
    if verdict != "pass":
        shown = ", ".join(names[:6]) + (" …" if len(names) > 6 else "")
        return verdict, shown
    if full_tier_missing(runs, since):
        return "pending", f"no successful {FULL_TIER} check on the head (mark it ready to run the full tier)"

    detail = pr_detail(repo, pr["number"])
    if detail["head"]["sha"] != sha:
        return "pending", "head moved during the sweep"
    if detail.get("mergeable") is False or detail.get("mergeable_state") == "dirty":
        return "conflict", "merge conflict with the base branch"
    if detail.get("mergeable_state") != "clean":
        return "pending", f"mergeable_state {detail.get('mergeable_state')}"
    if blockers := blocking_reviews(paged(f"repos/{repo}/pulls/{pr['number']}/reviews")):
        return "held", "changes requested by " + ", ".join(blockers)
    return "ready", ""


def merge(repo: str, pr: dict) -> str:
    try:
        api("PUT", f"repos/{repo}/pulls/{pr['number']}/merge",
            {"merge_method": "merge", "sha": pr["head"]["sha"]})
    except urllib.error.HTTPError as exc:
        return f"refused ({exc.code}): {exc.read().decode(errors='replace')[:200]}"
    return "merged"


PARK_NOTE = (
    "The merge sweeper marked this PR `ci:parked` ({why}). It remains open and "
    "ready for review; the label records the blocker. The sweeper may merge it "
    "after the blocker is resolved and all merge gates pass. "
    "Rule: `docs/ci-tiers.md`."
)
WAIT_NOTE = (
    "The merge sweeper marked this PR `ci:waiting`: {n} ready PRs exceed the "
    "prioritization cap ({cap}). It remains open and ready for review. The label "
    "will be cleared when it returns within the cap. "
    "Rule: `docs/ci-tiers.md`."
)


def add_label(repo: str, number: int, label: str) -> None:
    api("POST", f"repos/{repo}/issues/{number}/labels", {"labels": [label]})


def remove_label(repo: str, number: int, label: str) -> None:
    try:
        api("DELETE", f"repos/{repo}/issues/{number}/labels/{label}")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise


def comment(repo: str, number: int, body: str) -> None:
    api("POST", f"repos/{repo}/issues/{number}/comments",
        {"body": body + "\n\n---\n_Posted by `merge-sweeper.yml`._"})


def plan_capacity(prs: list[dict], buckets: dict[int, str], *,
                  max_ready: int) -> list[tuple[str, dict, str]]:
    """Plan capacity labels without changing draft/ready state.

    `prs` are the open PRs left after merging, `buckets` their assess() bucket.
    """
    actions: list[tuple[str, dict, str]] = []
    ready = []
    for pr in prs:
        if pr.get("draft"):
            continue
        labels = {label["name"] for label in pr.get("labels", [])}
        b = buckets.get(pr["number"])
        if b in PARK_BUCKETS or b == "needs-human":
            if L_WAITING in labels:
                actions.append(("resume", pr, "no longer in the waiting lane"))
            if L_PARKED not in labels:
                actions.append(("park", pr, {"fail": "failing checks", "conflict": "merge conflict",
                                             "over-budget": "too many CI checks",
                                             "needs-human": "labelled needs-human"}[b]))
        elif b != "held":
            if L_PARKED in labels:
                actions.append(("unpark", pr, "merge blocker cleared"))
            ready.append((pr, labels))
    ready.sort(key=lambda item: item[0]["created_at"])
    prioritized = ready[:max_ready]
    waiting = ready[max_ready:]
    for pr, labels in waiting:
        if L_WAITING not in labels:
            actions.append(("wait", pr, f"{len(ready)} ready"))
    for pr, labels in prioritized:
        if L_WAITING in labels:
            actions.append(("resume", pr, "within the prioritization cap"))
    return actions


def apply_action(repo: str, kind: str, pr: dict, why: str, *, max_ready: int) -> str:
    n = pr["number"]
    try:
        if kind == "park":
            add_label(repo, n, L_PARKED)
            comment(repo, n, PARK_NOTE.format(why=why))
        elif kind == "wait":
            add_label(repo, n, L_WAITING)
            comment(repo, n, WAIT_NOTE.format(n=why.split()[0], cap=max_ready))
        elif kind == "resume":
            remove_label(repo, n, L_WAITING)
        elif kind == "unpark":
            remove_label(repo, n, L_PARKED)
    except (urllib.error.HTTPError, RuntimeError) as exc:
        return f"failed: {exc}"
    return "done"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    ap.add_argument("--apply", action="store_true", help="merge and manage capacity")
    ap.add_argument("--max-merges", type=int, default=10,
                    help="merge at most N PRs per sweep (default 10)")
    ap.add_argument("--max-checks", type=int, default=30,
                    help="hold PRs whose head ran more checks than this (default 30)")
    ap.add_argument("--max-ready", type=int, default=40,
                    help="keep at most N PRs ready for review (default 40)")
    ap.add_argument("--pr", type=int, action="append", default=[],
                    help="only consider these PR numbers")
    args = ap.parse_args()
    if not args.repo:
        ap.error("--repo or GITHUB_REPOSITORY is required")

    default_branch = api("GET", f"repos/{args.repo}")["default_branch"]
    since = tiers_since(args.repo, default_branch)
    prs = paged(f"repos/{args.repo}/pulls?state=open&sort=created&direction=asc")
    if args.pr:
        prs = [p for p in prs if p["number"] in set(args.pr)]

    lines: dict[str, list[str]] = {}
    bucket_of: dict[int, str] = {}
    left: list[dict] = []
    merged = 0
    for pr in prs:
        try:
            bucket, reason = assess(args.repo, pr, default_branch,
                                    max_checks=args.max_checks, since=since)
        except urllib.error.HTTPError as exc:
            bucket, reason = "error", f"HTTP {exc.code} reading the PR"
        line = f"#{pr['number']} {pr['title'][:80]}" + (f" — {reason}" if reason else "")
        if bucket == "ready" and args.apply:
            if merged >= args.max_merges:
                line += " — over this sweep's merge cap"
            else:
                outcome = merge(args.repo, pr)
                merged += outcome == "merged"
                bucket = "merged" if outcome == "merged" else "error"
                line += f" — {outcome}"
        if bucket != "merged":
            left.append(pr)
        bucket_of[pr["number"]] = bucket
        lines.setdefault(bucket, []).append(line)
        print(f"[{bucket}] {line}", flush=True)

    actions = plan_capacity(left, bucket_of, max_ready=args.max_ready)
    acted: dict[str, list[str]] = {}
    for kind, pr, why in actions:
        outcome = apply_action(args.repo, kind, pr, why, max_ready=args.max_ready) \
            if args.apply else "planned"
        acted.setdefault(kind, []).append(f"#{pr['number']} {pr['title'][:80]} — {why} — {outcome}")
        print(f"[{kind}] #{pr['number']} {why} — {outcome}", flush=True)

    order = ["merged", "ready", "pending", "fail", "over-budget", "conflict",
             "needs-human", "held", "draft", "error"]
    mode = "apply" if args.apply else "report only"
    tiers = since.isoformat() if since else "not on the default branch yet"
    out = [f"## Merge sweeper ({mode}): {len(prs)} open PRs", "",
           f"Check budget {args.max_checks}, ready cap {args.max_ready}, tiers since {tiers}.", "",
           "| bucket | PRs |", "| --- | --- |"]
    out += [f"| {b} | {len(lines.get(b, []))} |" for b in order]
    out += [f"| → {k} | {len(acted.get(k, []))} |"
            for k in ("park", "wait", "resume", "unpark")]
    for title, group in [(b, lines.get(b)) for b in order] + [(f"→ {k}", acted.get(k)) for k in acted]:
        if group:
            out += ["", f"<details><summary>{title} ({len(group)})</summary>", ""]
            out += [f"- {l}" for l in group] + ["", "</details>"]
    summary = "\n".join(out) + "\n"
    if path := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(summary)
    else:
        print("\n" + summary)
    failed = any(l.endswith("failed") or " — failed:" in l for g in acted.values() for l in g)
    return 1 if lines.get("error") or failed else 0


if __name__ == "__main__":
    sys.exit(main())
