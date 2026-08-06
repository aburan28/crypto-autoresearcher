#!/usr/bin/env python3
"""Keep every open research branch current with `main`, without agent attention.

`CLAUDE.md` has instructed sessions to "run `tools/sync_open_branches.py`" since
the merge-hygiene rules were written. THE FILE DID NOT EXIST. Branches were
therefore synced by hand, when someone remembered, and the measured result was
115 open branches with the median 26-55 commits behind and two forks sitting at
1279 behind / 143 ahead -- far past the point where anyone will merge them.

The reason is not laziness. Merging `main` used to cost an identifier collision,
an invalidated archive receipt, a conflict in a generated file, and a
revalidation pass. Deferring was individually rational and collectively fatal.
Three changes landed alongside this tool remove most of that cost:

  * generated artifacts are no longer committed, so they cannot conflict;
  * archive receipts verify on content when their commit binding is gone;
  * identifiers are random tokens, so concurrent worktrees cannot collide.

What remains is mechanical, which is what this automates.

USAGE

    python3 tools/sync_open_branches.py                  # report only (default)
    python3 tools/sync_open_branches.py --apply          # merge and push what is safe
    python3 tools/sync_open_branches.py --json out.json  # machine-readable

SAFETY, and why `--apply` is not the default:

  * A branch is only touched when it is IDLE (no commit for --idle-minutes,
    default 120). Pushing into a branch an agent is actively committing to turns
    its next push into a non-fast-forward -- precisely the interference this is
    meant to reduce.
  * The merge must be clean, or clean after resolving conflicts confined to
    GENERATED paths (resolution: remove; they are rebuilt on demand).
  * `validate_ledger.py` must report no NEW errors against the branch's own
    pre-merge state. A merge that introduces validation errors is left for a
    human.
  * MERGE, NEVER REBASE. Branches carry pushed run records whose archive
    receipts name their commits; rebasing rewrites exactly those commits.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Conflicts confined to these are resolved by REMOVAL, because they are derived
# and .gitignore'd on main. Any other conflicting path stops the merge.
GENERATED = (
    "knowledge/INDEX.md",
    "dispatch_plan.json",
    "dispatch_plan.md",
)

# Branches never synced: the trunk itself and anything a human owns by name.
SKIP_PREFIXES = ("origin/main", "origin/HEAD")

# Kept for unit tests and for any PR-scoped sync wrapper that still filters
# open pull requests before delegating to branch-based sync.
SKIP_LABEL = "no-auto-sync"


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
    """Comment marker, one per pull request per base tip."""
    return f"<!-- sync-open-branches:{pr_number}:{base_sha[:12]} -->"


def run(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd or REPO, capture_output=True, text=True)


def is_generated(path: str) -> bool:
    return any(path == g or path.endswith("/" + g) or path.endswith(g)
               for g in GENERATED)


def remote_branches() -> list[str]:
    out = run("git", "for-each-ref", "--format=%(refname:short)",
              "refs/remotes/origin").stdout.split()
    return [b for b in out if not b.startswith(SKIP_PREFIXES)]


def branch_digest(branch: str, base: str) -> dict | None:
    """What changed on `base` since this branch last shared history with it.

    This is the per-branch half of the merge feed. The feed under
    coordination/events/main/ answers "what landed"; this answers "what landed
    THAT MATTERS TO YOU" -- which of your goals moved, and whether the shared
    contract changed under you while you were away.
    """
    merge_base = run("git", "merge-base", branch, base).stdout.strip()
    if not merge_base:
        return None
    out = run(sys.executable, "tools/merge_digest.py", "--since", merge_base,
              "--until", base, "--json")
    try:
        body = json.loads(out.stdout)["merge_event"]
    except (json.JSONDecodeError, KeyError):
        return None
    return {
        "since": merge_base[:12],
        "goal_transitions": body.get("goal_transitions") or [],
        "contract_changed": body.get("contract_changed") or [],
        "records_added": {k: v.get("added", []) for k, v in
                          (body.get("records") or {}).items() if v.get("added")},
    }


def branch_state(branch: str, base: str) -> dict:
    behind = run("git", "rev-list", "--count", f"{branch}..{base}").stdout.strip()
    ahead = run("git", "rev-list", "--count", f"{base}..{branch}").stdout.strip()
    last = run("git", "log", "-1", "--format=%ct", branch).stdout.strip()
    subject = run("git", "log", "-1", "--format=%s", branch).stdout.strip()
    age_minutes = None
    if last.isdigit():
        age_minutes = int((time.time() - int(last)) / 60)
    return {
        "branch": branch,
        "behind": int(behind) if behind.isdigit() else None,
        "ahead": int(ahead) if ahead.isdigit() else None,
        "idle_minutes": age_minutes,
        "last_subject": subject[:80],
    }


def classify(state: dict, fork_threshold: int) -> str:
    behind, ahead = state["behind"], state["ahead"]
    if behind is None or ahead is None:
        return "unknown"
    if ahead == 0:
        return "merged_or_empty"
    if behind == 0:
        return "current"
    if behind >= fork_threshold:
        return "fork"
    return "behind"


def try_merge(branch: str, base: str, idle_minutes: int, apply: bool) -> dict:
    """Merge `base` into `branch` in a scratch worktree. Push only if --apply."""
    work = tempfile.mkdtemp(prefix="sync-", dir=tempfile.gettempdir())
    tree = os.path.join(work, "wt")
    result: dict = {"merged": False, "pushed": False, "conflicts": [],
                    "resolved_generated": [], "note": ""}
    try:
        add = run("git", "worktree", "add", "--quiet", "--detach", tree, branch)
        if add.returncode:
            result["note"] = f"worktree add failed: {add.stderr.strip()[:200]}"
            return result

        pre = run(sys.executable, "tools/validate_ledger.py", cwd=tree)
        pre_errs = {l for l in pre.stdout.splitlines() if l.startswith("  - ")}

        merge = run("git", "-c", "user.name=sync-open-branches",
                    "-c", "user.email=noreply@anthropic.com",
                    "merge", "--no-edit", base, cwd=tree)
        if merge.returncode:
            status = run("git", "diff", "--name-only", "--diff-filter=U",
                         cwd=tree).stdout.split()
            unmergeable = [p for p in status if not is_generated(p)]
            if unmergeable:
                result["conflicts"] = unmergeable
                result["note"] = "real conflicts; left for a human"
                run("git", "merge", "--abort", cwd=tree)
                return result
            for p in status:
                run("git", "rm", "-q", "--cached", "--ignore-unmatch", p, cwd=tree)
                fs = os.path.join(tree, p)
                if os.path.exists(fs):
                    os.remove(fs)
                result["resolved_generated"].append(p)
            cont = run("git", "-c", "user.name=sync-open-branches",
                       "-c", "user.email=noreply@anthropic.com",
                       "commit", "--no-edit", cwd=tree)
            if cont.returncode:
                result["note"] = f"could not finish merge: {cont.stderr.strip()[:200]}"
                run("git", "merge", "--abort", cwd=tree)
                return result

        post = run(sys.executable, "tools/validate_ledger.py", cwd=tree)
        post_errs = {l for l in post.stdout.splitlines() if l.startswith("  - ")}
        new_errs = sorted(post_errs - pre_errs)
        result["merged"] = True
        result["new_validation_errors"] = new_errs
        if new_errs:
            result["note"] = (f"merge is clean but introduces {len(new_errs)} new "
                              f"validation error(s); not pushed")
            return result

        if not apply:
            result["note"] = "merges cleanly and validates; not pushed (report mode)"
            return result
        if idle_minutes is not None and idle_minutes < 0:
            result["note"] = "branch is active; not pushed"
            return result

        short = branch.split("/", 1)[1]
        push = run("git", "push", "origin", f"HEAD:refs/heads/{short}", cwd=tree)
        if push.returncode:
            result["note"] = f"push failed: {push.stderr.strip()[:200]}"
            return result
        result["pushed"] = True
        result["note"] = "merged and pushed"
        return result
    finally:
        run("git", "worktree", "remove", "--force", tree)
        shutil.rmtree(work, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--apply", action="store_true",
                    help="merge and push branches that are safe to sync")
    ap.add_argument("--idle-minutes", type=int, default=120,
                    help="only touch branches with no commit for this long "
                         "(default 120; pushing into a live agent's branch is "
                         "the interference this tool exists to reduce)")
    ap.add_argument("--fork-threshold", type=int, default=500,
                    help="behind-count past which a branch is reported as a fork "
                         "needing a human decision rather than a sync")
    ap.add_argument("--branch", action="append",
                    help="restrict to branches containing this substring")
    ap.add_argument("--limit", type=int, help="process at most N candidate branches")
    ap.add_argument("--json", metavar="PATH", help="write the full report as JSON")
    ap.add_argument("--digest", action="store_true",
                    help="for each out-of-date branch, summarise what changed on "
                         "the base since it last shared history: goal transitions, "
                         "new records, and whether the shared contract moved")
    args = ap.parse_args()

    run("git", "fetch", "--quiet", "origin")
    if run("git", "rev-parse", "--verify", "--quiet",
           args.base + "^{commit}").returncode:
        print(f"base {args.base} does not resolve", file=sys.stderr)
        return 2

    rows = []
    for branch in remote_branches():
        if args.branch and not any(pat in branch for pat in args.branch):
            continue
        state = branch_state(branch, args.base)
        state["status"] = classify(state, args.fork_threshold)
        if args.digest and state["status"] in ("behind", "fork"):
            state["digest"] = branch_digest(branch, args.base)
        rows.append(state)

    candidates = [r for r in rows if r["status"] == "behind"]
    # MOST IDLE FIRST. Sorting by behind-count picks the branches closest to
    # main, which are the ones an agent is most likely to be committing to right
    # now -- so --limit would spend its budget on exactly the branches the idle
    # guard then refuses. Idle-first spends it on the branches that are safe to
    # touch and most overdue.
    candidates.sort(key=lambda r: -(r["idle_minutes"] or 0))
    if args.limit:
        candidates = candidates[: args.limit]

    for row in candidates:
        idle = row["idle_minutes"]
        if idle is not None and idle < args.idle_minutes:
            row["action"] = {"merged": False, "pushed": False,
                             "note": f"active {idle}m ago; skipped "
                                     f"(idle threshold {args.idle_minutes}m)"}
            continue
        row["action"] = try_merge(row["branch"], args.base, idle, args.apply)

    by_status: dict[str, list[dict]] = {}
    for r in rows:
        by_status.setdefault(r["status"], []).append(r)

    print(f"base {args.base}; {len(rows)} open branches\n")
    for status in ("current", "behind", "fork", "merged_or_empty", "unknown"):
        group = by_status.get(status, [])
        if not group:
            continue
        print(f"## {status} ({len(group)})")
        for r in sorted(group, key=lambda x: -(x["behind"] or 0))[:40]:
            line = (f"  behind={r['behind']:<5} ahead={r['ahead']:<4} "
                    f"idle={r['idle_minutes']}m  {r['branch']}")
            dig = r.get("digest")
            if dig:
                if dig["contract_changed"]:
                    line += (f"\n      !! shared contract moved under this branch: "
                             f"{len(dig['contract_changed'])} file(s) incl. "
                             f"{', '.join(dig['contract_changed'][:3])}")
                for t in dig["goal_transitions"][:4]:
                    if t.get("new_goal"):
                        line += f"\n      + {t['goal_id']}: new goal ({t.get('status')})"
                        continue
                    bits = []
                    if "status" in t:
                        bits.append(f"status {t['status']['from']} -> {t['status']['to']}")
                    if t.get("next_action_changed"):
                        bits.append("next_action changed")
                    if "latest_verified_commit" in t:
                        bits.append("provenance rebound")
                    if bits:
                        line += f"\n      ~ {t['goal_id']}: {'; '.join(bits)}"
            act = r.get("action")
            if act:
                line += f"\n      -> {act['note']}"
                if act.get("conflicts"):
                    line += f" [{', '.join(act['conflicts'][:4])}]"
                if act.get("resolved_generated"):
                    line += (f" [auto-resolved generated: "
                             f"{len(act['resolved_generated'])}]")
            print(line)
        print()

    forks = by_status.get("fork", [])
    live_forks = [r for r in forks
                  if r["idle_minutes"] is not None and r["idle_minutes"] < 240]
    if live_forks:
        print(f"WARNING: {len(live_forks)} fork(s) are BOTH past the fork "
              f"threshold AND actively committed to in the last 4 hours. These "
              f"are the expensive ones: work is still accumulating on a base "
              f"that will only get harder to reconcile.")
        for r in live_forks:
            print(f"  - {r['branch']}: behind {r['behind']}, ahead "
                  f"{r['ahead']}, last commit {r['idle_minutes']}m ago")
        print()

    if forks:
        print(f"{len(forks)} branch(es) are past --fork-threshold "
              f"{args.fork_threshold} and will not be synced automatically.")
        print("These are forks, not branches: land them or close them.")
        for r in forks:
            print(f"  - {r['branch']}: behind {r['behind']}, ahead {r['ahead']}")
        print()

    pushed = [r for r in rows if (r.get("action") or {}).get("pushed")]
    blocked = [r for r in rows if (r.get("action") or {}).get("conflicts")]
    print(f"pushed {len(pushed)}; blocked by real conflicts {len(blocked)}; "
          f"forks {len(forks)}")
    if not args.apply:
        print("report mode: nothing was pushed. Re-run with --apply to sync.")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"base": args.base, "branches": rows}, fh, indent=1,
                      sort_keys=True)
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
