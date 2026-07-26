#!/usr/bin/env python3
"""Merge the base branch into every open pull-request branch that is behind it.

Run periodically (see .github/workflows/sync-main.yml) so a long-lived research
branch does not silently diverge from main while a campaign is in flight.

Three properties matter more here than in an ordinary repository:

1. **Merge, never rebase.** AGENTS.md forbids rewriting history over pushed run
   records, and a rebase rewrites every commit on the branch. This tool only
   ever merges main *into* the branch.
2. **A conflict is never auto-resolved.** Records are immutable and corrections
   supersede rather than overwrite (AGENTS.md rule 4), so no machine may pick a
   side in a conflicted ledger record, run artifact, or knowledge entry. The
   merge is aborted and the pull request is told why.
3. **The merged tree is validated before it is pushed.** Two branches can each
   add a record that git merges cleanly but that `validate_ledger.py` rejects
   together -- a duplicate id, a cross-reference to a record that moved. A sync
   that leaves the ledger invalid is worse than no sync, so the merge is thrown
   away and reported instead.

A conflict or a failed validation is a normal outcome and exits 0: the pull
request carries the report, and a red schedule every six hours would train the
reader to ignore it. Only an infrastructure failure exits non-zero.

Usage:
    python3 tools/sync_open_branches.py [--base main] [--dry-run] [--limit N]

Requires `gh` authenticated via GH_TOKEN and a full-history checkout. Fork pull
requests are skipped: GITHUB_TOKEN cannot push to them. Label a pull request
`no-auto-sync` to exclude it.

This tool switches branches and hard-resets between them, so it refuses to run
against a dirty working tree, and returns to the ref it started on. `--dry-run`
is not exempt: it still needs to check branches out to attempt the merges it
reports on.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

SKIP_LABEL = "no-auto-sync"

# Run against the merged tree before pushing. Each is already part of CI
# (.github/workflows/validate.yml); these are the subset that can fail purely
# because two independently valid branches were combined.
POST_MERGE_CHECKS: list[list[str]] = [
    ["python3", "tools/validate_ledger.py"],
    ["python3", "tools/build_knowledge_index.py", "--check"],
]

BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"


class InfrastructureError(RuntimeError):
    """The tool could not do its job; distinct from a branch that won't merge."""


def _exec(cmd: list[str]) -> subprocess.CompletedProcess:
    """Run a command, turning a missing binary into an InfrastructureError.

    A bare FileNotFoundError traceback in a scheduled job reads like a bug in
    this tool rather than a runner that is missing `git` or `gh`.
    """
    try:
        return subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise InfrastructureError(f"{cmd[0]} is not installed on this runner") from exc


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    proc = _exec(["git", *args])
    if check and proc.returncode != 0:
        raise InfrastructureError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc


def gh(*args: str) -> subprocess.CompletedProcess:
    proc = _exec(["gh", *args])
    if proc.returncode != 0:
        raise InfrastructureError(f"gh {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc


def gh_json(*args: str):
    return json.loads(gh(*args).stdout or "[]")


def skip_reason(pr: dict, base: str) -> str | None:
    """Why this pull request must not be synced, or None to proceed.

    Pure decision logic, kept free of git and network calls so it is testable.
    """
    if pr.get("isCrossRepository"):
        return "fork pull request; GITHUB_TOKEN cannot push to it"
    if any(label.get("name") == SKIP_LABEL for label in pr.get("labels") or []):
        return f"labelled {SKIP_LABEL}"
    if pr.get("baseRefName") != base:
        return f"targets {pr.get('baseRefName')!r}, not {base!r}"
    if pr.get("isDraft") and pr.get("mergeable") == "CONFLICTING":
        return "draft with known conflicts; leave it to its author"
    return None


def marker(pr_number: int, base_sha: str) -> str:
    """Comment marker, one per pull request per base tip.

    Keyed on the base sha so a branch that stays conflicted is reported once per
    move of main, not once every six hours.
    """
    return f"<!-- sync-open-branches:{pr_number}:{base_sha[:12]} -->"


def already_reported(repo: str, pr_number: int, text: str) -> bool:
    comments = gh_json(
        "api", f"repos/{repo}/issues/{pr_number}/comments",
        "--paginate", "--jq", "[.[].body]")
    return any(text in (body or "") for body in comments)


def comment(repo: str, pr_number: int, base_sha: str, body: str, dry_run: bool) -> None:
    tagged = f"{body}\n\n{marker(pr_number, base_sha)}"
    if dry_run:
        print(f"    would comment on #{pr_number}:\n{body}")
        return
    if already_reported(repo, pr_number, marker(pr_number, base_sha)):
        print("    already reported for this base tip; not repeating")
        return
    gh("api", f"repos/{repo}/issues/{pr_number}/comments", "-f", f"body={tagged}")


def run_post_merge_checks() -> str | None:
    """Return the first failing check's report, or None if the tree is clean."""
    for cmd in POST_MERGE_CHECKS:
        proc = _exec(cmd)
        if proc.returncode != 0:
            output = (proc.stdout + proc.stderr).strip()
            return f"`{' '.join(cmd)}` failed:\n\n```\n{output[-3000:]}\n```"
    return None


def sync_one(repo: str, pr: dict, base: str, base_sha: str, dry_run: bool) -> str:
    """Sync a single pull request. Returns a one-word outcome for the summary."""
    number, head = pr["number"], pr["headRefName"]

    reason = skip_reason(pr, base)
    if reason:
        print(f"  #{number} ({head}): skipped -- {reason}")
        return "skipped"

    git("fetch", "origin", head)
    if git("merge-base", "--is-ancestor", f"origin/{base}", f"origin/{head}",
           check=False).returncode == 0:
        print(f"  #{number} ({head}): already current")
        return "current"

    git("checkout", "-B", head, f"origin/{head}")
    merge = git("merge", "--no-edit", f"origin/{base}", check=False)
    if merge.returncode != 0:
        conflicts = git("diff", "--name-only", "--diff-filter=U",
                        check=False).stdout.strip() or "(none reported)"
        git("merge", "--abort", check=False)
        print(f"  #{number} ({head}): CONFLICT")
        comment(repo, number, base_sha,
                f"This branch conflicts with `{base}` and was not synced "
                f"automatically.\n\nConflicting paths:\n\n```\n{conflicts}\n```\n\n"
                f"Resolve it locally with `git merge origin/{base}` -- do not "
                f"rebase, which would rewrite history over pushed run records. "
                f"A conflict inside an immutable record is resolved by "
                f"superseding it with a new id, never by editing it in place.",
                dry_run)
        return "conflict"

    failure = run_post_merge_checks()
    if failure:
        git("reset", "--hard", f"origin/{head}", check=False)
        print(f"  #{number} ({head}): merged cleanly but validation failed")
        comment(repo, number, base_sha,
                f"`{base}` merges into this branch without conflict, but the "
                f"merged tree does not validate, so nothing was pushed.\n\n"
                f"{failure}\n\nThis usually means this branch and `{base}` each "
                f"added a record that is valid alone and invalid together.",
                dry_run)
        return "invalid"

    if dry_run:
        print(f"  #{number} ({head}): would push merge of {base}")
        git("reset", "--hard", f"origin/{head}", check=False)
        return "would-sync"

    git("push", "origin", f"{head}:{head}")
    print(f"  #{number} ({head}): synced")
    return "synced"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="main", help="base branch (default: main)")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would happen; push and comment nothing")
    parser.add_argument("--limit", type=int, default=50,
                        help="maximum open pull requests to consider")
    args = parser.parse_args()

    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        print("GITHUB_REPOSITORY is not set", file=sys.stderr)
        return 1

    # This tool checks out other people's branches and hard-resets between
    # them. On a runner that is free; in a working repository it would discard
    # whatever the author had in progress. Refuse rather than destroy.
    if git("status", "--porcelain").stdout.strip():
        print("FAIL: working tree is not clean. This tool switches branches "
              "and resets between them; commit or stash first.", file=sys.stderr)
        return 1
    original = git("symbolic-ref", "--quiet", "--short", "HEAD",
                   check=False).stdout.strip() or git("rev-parse", "HEAD").stdout.strip()

    try:
        git("config", "user.name", BOT_NAME)
        git("config", "user.email", BOT_EMAIL)
        git("fetch", "origin", args.base)
        base_sha = git("rev-parse", f"origin/{args.base}").stdout.strip()

        pulls = gh_json(
            "pr", "list", "--repo", repo, "--state", "open",
            "--base", args.base, "--limit", str(args.limit),
            "--json", "number,headRefName,baseRefName,isCrossRepository,"
                      "isDraft,mergeable,labels,title")
        print(f"{len(pulls)} open pull request(s) against {args.base} "
              f"@ {base_sha[:12]}")

        outcomes: dict[str, int] = {}
        for pr in pulls:
            outcome = sync_one(repo, pr, args.base, base_sha, args.dry_run)
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
    except InfrastructureError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        # Return to wherever we started, never to a pull-request branch. The
        # tree was clean on entry and each branch is left clean, so this needs
        # no --force -- and must not have one, since a --force here discards
        # anything the checks above did not anticipate.
        git("checkout", original, check=False)

    print("summary: " + (", ".join(f"{k}={v}" for k, v in sorted(outcomes.items()))
                         or "nothing to do"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
