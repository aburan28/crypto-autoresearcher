#!/usr/bin/env python3
"""Triage for the autofix queue (.github/workflows/autofix-queue.yml).

Finds open same-repo pull requests that have merge conflicts or failing
checks, decides which model tier should try first, and emits a job matrix.

Tiers
  haiku   every problem is mechanical: only lockfile conflicts and/or only
          lint / format / syntax checks failing
  sonnet  anything else (real merge conflicts, test or build failures)

Escalation is tracked with PR labels so it survives across runs:
  autofix:haiku    Haiku has attempted this PR
  autofix:sonnet   Sonnet has attempted this PR
  autofix:running  a fix job is in flight (triage skips the PR)
  autofix:off      opt this PR out entirely
  needs-human      Sonnet already tried and the PR is still broken

When a PR comes back clean (no conflicts, every check green) its
autofix:haiku / autofix:sonnet labels are removed, so the next breakage starts
again at the bottom of the ladder.

Standard library only; talks to GitHub through `gh api` (REST).
"""
from __future__ import annotations

import argparse
import calendar
import json
import os
import re
import subprocess
import sys
import time

FAILED = {"failure", "timed_out", "startup_failure"}
L_HAIKU, L_SONNET = "autofix:haiku", "autofix:sonnet"
L_RUNNING, L_OFF, L_HUMAN = "autofix:running", "autofix:off", "needs-human"

DEFAULT_MECHANICAL_CHECKS = (
    r"(?i)(lint|fmt|format|clippy|rustfmt|ruff|black|isort|prettier|eslint|"
    r"typos|spell|yaml|parse|syntax|whitespace|markdown)"
)
DEFAULT_MECHANICAL_FILES = (
    r"(^|/)(Cargo\.lock|package-lock\.json|yarn\.lock|pnpm-lock\.yaml|"
    r"poetry\.lock|uv\.lock|Gemfile\.lock|go\.sum|requirements[^/]*\.lock)$"
)
# Check runs produced by the queue itself or by advisory reviewers.
DEFAULT_IGNORE_CHECKS = r"^(autofix|triage|review|claude)( |$|\()"


def env_regex(name: str, default: str) -> re.Pattern[str] | None:
    value = os.environ.get(name, default)
    return re.compile(value) if value else None


def gh(path: str, *args: str, paginate: bool = False, max_pages: int = 10) -> object:
    def call(p: str) -> object:
        res = subprocess.run(
            ["gh", "api", "-H", "Accept: application/vnd.github+json", p, *args],
            capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"gh api {p}: {res.stderr.strip()}")
        return json.loads(res.stdout) if res.stdout.strip() else None

    if not paginate:
        return call(path)
    # Explicit ?page=N rather than `gh --paginate`, which follows Link headers
    # that some proxies refuse; every caller passes per_page=100.
    items: list = []
    sep = "&" if "?" in path else "?"
    for page in range(1, max_pages + 1):
        data = call(f"{path}{sep}page={page}")
        batch = data if isinstance(data, list) else data.get("check_runs", [])
        items.extend(batch)
        if len(batch) < 100:
            break
    return items


def pr_detail(repo: str, number: int) -> dict:
    # `mergeable` is computed lazily; the first read can return null.
    for attempt in range(3):
        pr = gh(f"repos/{repo}/pulls/{number}")
        if pr.get("mergeable") is not None:
            return pr
        time.sleep(3 * (attempt + 1))
    return pr


def check_runs(repo: str, sha: str, ignore: re.Pattern[str] | None) -> list[dict]:
    runs = gh(f"repos/{repo}/commits/{sha}/check-runs?per_page=100&filter=latest",
              paginate=True)
    return [r for r in runs if not (ignore and ignore.search(r["name"]))]


def conflict_files(base: str, head: str) -> list[str] | None:
    """Files `git merge-tree` reports as conflicting, or None if unknown."""
    def git(*a: str, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *a], capture_output=True, text=True,
                              check=check)
    try:
        git("fetch", "--quiet", "--no-tags", "--filter=blob:none", "--depth=300",
            "origin", f"+refs/heads/{base}:refs/autofix/base",
            f"+refs/heads/{head}:refs/autofix/head")
        if git("merge-base", "refs/autofix/base", "refs/autofix/head",
               check=False).returncode != 0:
            return None  # merge base deeper than we fetched
        res = git("merge-tree", "--write-tree", "--name-only", "--no-messages",
                  "refs/autofix/base", "refs/autofix/head", check=False)
    except subprocess.CalledProcessError as exc:
        print(f"  conflict listing failed: {exc.stderr.strip()}", file=sys.stderr)
        return None
    if res.returncode not in (0, 1):
        return None
    lines = [l for l in res.stdout.splitlines() if l.strip()]
    return lines[1:]  # first line is the merged tree id


def set_labels(repo: str, number: int, add=(), remove=(), dry=False) -> None:
    for label in add:
        print(f"  + label {label}")
        if not dry:
            gh(f"repos/{repo}/issues/{number}/labels", "-X", "POST",
               "-f", f"labels[]={label}")
    for label in remove:
        print(f"  - label {label}")
        if not dry:
            subprocess.run(["gh", "api", "-X", "DELETE",
                            f"repos/{repo}/issues/{number}/labels/{label}"],
                           capture_output=True)


def comment(repo: str, number: int, body: str, dry=False) -> None:
    print(f"  comment: {body.splitlines()[0]}")
    if not dry:
        gh(f"repos/{repo}/issues/{number}/comments", "-X", "POST", "-f",
           f"body={body}")


def triage(args: argparse.Namespace) -> list[dict]:
    repo = args.repo
    mech_checks = env_regex("AUTOFIX_MECHANICAL_CHECKS", DEFAULT_MECHANICAL_CHECKS)
    mech_files = env_regex("AUTOFIX_MECHANICAL_FILES", DEFAULT_MECHANICAL_FILES)
    protected = env_regex("AUTOFIX_PROTECTED_PATHS", "")
    ignore = env_regex("AUTOFIX_IGNORE_CHECKS", DEFAULT_IGNORE_CHECKS)

    if args.pr:
        prs = [gh(f"repos/{repo}/pulls/{n}") for n in args.pr]
    else:
        prs = gh(f"repos/{repo}/pulls?state=open&per_page=100", paginate=True)

    queue: list[dict] = []
    for pr in prs:
        if len(queue) >= args.max:
            print(f"queue full ({args.max}); remaining PRs wait for the next sweep")
            break
        n = pr["number"]
        labels = {l["name"] for l in pr.get("labels", [])}
        print(f"#{n} {pr['title'][:70]!r}")
        if pr.get("state") != "open":
            print("  skip: not open"); continue
        if pr["head"]["repo"] is None or pr["head"]["repo"]["full_name"] != repo:
            print("  skip: fork PR (never run with write access)"); continue
        if pr.get("draft") and not args.include_drafts:
            print("  skip: draft"); continue
        if labels & {L_OFF, L_HUMAN, L_RUNNING}:
            print(f"  skip: labelled {sorted(labels & {L_OFF, L_HUMAN, L_RUNNING})}")
            continue

        detail = pr_detail(repo, n)
        conflict = detail.get("mergeable_state") == "dirty"
        if detail.get("mergeable") is None:
            print("  skip: GitHub has not computed mergeability yet"); continue

        if not args.pr and args.min_age > 0:
            # Leave branches alone while their author (often another agent)
            # is still pushing to them.
            when = gh(f"repos/{repo}/commits/{pr['head']['sha']}")["commit"][
                "committer"]["date"]
            age = (time.time() - calendar.timegm(
                time.strptime(when, "%Y-%m-%dT%H:%M:%SZ"))) / 60
            if age < args.min_age:
                print(f"  skip: head commit is {age:.0f} min old "
                      f"(< {args.min_age}); author may still be pushing")
                continue

        runs = check_runs(repo, pr["head"]["sha"], ignore)
        pending = [r["name"] for r in runs if r["status"] != "completed"]
        failing = [r for r in runs
                   if r["status"] == "completed" and r["conclusion"] in FAILED]

        if not conflict and not failing:
            if not pending and labels & {L_HAIKU, L_SONNET}:
                print("  clean: resetting escalation ladder")
                set_labels(repo, n, remove=sorted(labels & {L_HAIKU, L_SONNET}),
                           dry=args.dry_run)
            else:
                print(f"  ok ({len(pending)} pending)")
            continue
        if pending and not conflict:
            print(f"  wait: {len(failing)} failing but {len(pending)} still running")
            continue

        files: list[str] | None = []
        if conflict:
            files = conflict_files(pr["base"]["ref"], pr["head"]["ref"])
            print(f"  conflicts: {files if files is not None else 'unknown'}")
            if files and protected and any(protected.search(f) for f in files):
                hit = [f for f in files if protected.search(f)]
                set_labels(repo, n, add=[L_HUMAN], dry=args.dry_run)
                comment(repo, n,
                        "**autofix:** merge conflicts touch protected research-record "
                        f"paths ({', '.join(f'`{f}`' for f in hit)}). These need a "
                        "Coordinator, so the queue is handing this PR to a human.",
                        dry=args.dry_run)
                continue

        fail_names = [r["name"] for r in failing]
        if failing and protected:
            changed = [f["filename"] for f in
                       gh(f"repos/{repo}/pulls/{n}/files?per_page=100", paginate=True)]
            if any(protected.search(f) for f in changed):
                if not conflict:
                    print("  skip: PR changes protected record paths; its check "
                          "failures are for the record owner, not the queue")
                    continue
                print("  PR changes protected record paths: fixing the merge "
                      "conflict only, not the check failures")
                failing, fail_names = [], []
        checks_mech = all(mech_checks and mech_checks.search(x) for x in fail_names)
        files_mech = (not conflict) or (
            files is not None and len(files) > 0
            and all(mech_files and mech_files.search(f) for f in files))
        tier = "haiku" if (checks_mech and files_mech) else "sonnet"

        if L_SONNET in labels:
            set_labels(repo, n, add=[L_HUMAN], dry=args.dry_run)
            comment(repo, n,
                    "**autofix:** Sonnet already attempted this PR and it is still "
                    "broken"
                    + (" (merge conflicts)" if conflict else "")
                    + (f" (failing: {', '.join(fail_names)})" if fail_names else "")
                    + ". Handing it to a human. Remove `needs-human` and "
                    "`autofix:sonnet` to let the queue try again.",
                    dry=args.dry_run)
            continue
        if tier == "haiku" and L_HAIKU in labels:
            tier = "sonnet"
            print("  Haiku already tried: escalating")

        print(f"  -> queue as {tier}: conflict={conflict} failing={fail_names}")
        queue.append({
            "number": n,
            "head_ref": pr["head"]["ref"],
            "base_ref": pr["base"]["ref"],
            "tier": tier,
            "conflict": conflict,
            "conflict_files": files or [],
            "failing": [{"name": r["name"], "id": r["id"],
                         "url": r.get("html_url") or r.get("details_url"),
                         "actions_job": (r.get("app") or {}).get("slug")
                         == "github-actions"}
                        for r in failing],
        })
    return queue


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    p.add_argument("--pr", type=int, action="append",
                   help="only consider these PR numbers")
    p.add_argument("--max", type=int,
                   default=int(os.environ.get("AUTOFIX_MAX_PER_SWEEP") or 5))
    p.add_argument("--min-age", type=int,
                   default=int(os.environ.get("AUTOFIX_MIN_AGE_MINUTES") or 45),
                   help="minutes since the head commit before a sweep touches "
                        "a PR (ignored with --pr)")
    p.add_argument("--include-drafts", action="store_true")
    p.add_argument("--dry-run", action="store_true",
                   help="print decisions; change no labels, post no comments")
    args = p.parse_args()
    if not args.repo:
        p.error("--repo or GITHUB_REPOSITORY is required")

    queue = triage(args)
    payload = json.dumps(queue)
    print(f"\nqueued {len(queue)}: {payload}")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as fh:
            fh.write(f"matrix={payload}\n")
            fh.write(f"count={len(queue)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
