#!/usr/bin/env python3
"""Deterministic half of an autofix job (.github/workflows/autofix-queue.yml).

The model only edits files in the working tree. Everything with side effects
(starting the merge, committing, pushing, re-running jobs, labels) happens
here, so a cheap model cannot force-push, commit to the wrong branch, or
silently skip a step.

Subcommands
  prepare   reset to the PR head, start the merge with the base branch if the
            PR conflicts, download failing-job log tails, write .autofix/task.md
  verify    accept or reject the model's attempt (writes ok=, status=, reason=
            to $GITHUB_OUTPUT)
  commit    commit the accepted attempt and push it to the PR branch
  rerun     re-run the failed jobs (the model judged them flaky)

Environment: PR, HEAD_REF, BASE_REF, TIER, CONFLICT, FAILING (JSON),
MODEL, GITHUB_REPOSITORY, GH_TOKEN, PUSH_TOKEN, AUTOFIX_PROTECTED_PATHS,
AUTOFIX_REPO_NOTES.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

WORK = Path(".autofix")
START = WORK / "start_sha"
CONFLICTS = WORK / "conflicts.txt"
RESULT = WORK / "result.json"
TASK = WORK / "task.md"
MARKER = re.compile(r"^(<<<<<<<|>>>>>>>)( |$)", re.M)


def sh(*cmd: str, check: bool = True, quiet: bool = False) -> str:
    if not quiet:
        print("+", " ".join(cmd), flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if check and res.returncode != 0:
        sys.stderr.write(res.stdout + res.stderr)
        raise SystemExit(f"command failed ({res.returncode}): {' '.join(cmd)}")
    return res.stdout


def output(**kv: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    for k, v in kv.items():
        print(f"{k}={v}")
        if path:
            with open(path, "a") as fh:
                fh.write(f"{k}={v}\n")


def oneline(text: str) -> str:
    """Single line, so model-written text cannot add $GITHUB_OUTPUT keys."""
    return " ".join(str(text).split())[:500]


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def failing() -> list[dict]:
    return json.loads(env("FAILING") or "[]")


# --------------------------------------------------------------------------
def prepare() -> None:
    repo, head, base = env("GITHUB_REPOSITORY"), env("HEAD_REF"), env("BASE_REF")
    conflict = env("CONFLICT") == "true"

    WORK.mkdir(exist_ok=True)
    exclude = Path(".git/info/exclude")
    exclude.parent.mkdir(parents=True, exist_ok=True)
    if not exclude.exists() or ".autofix/" not in exclude.read_text():
        with exclude.open("a") as fh:
            fh.write("\n.autofix/\n")

    # Start from the PR head every time, so a rejected Haiku attempt leaves
    # nothing behind for Sonnet.
    if START.exists():
        start = START.read_text().strip()
        sh("git", "merge", "--abort", check=False)
        sh("git", "reset", "--hard", start)
        sh("git", "clean", "-fdq", "-e", ".autofix/")
    else:
        start = sh("git", "rev-parse", "HEAD", quiet=True).strip()
        START.write_text(start + "\n")
    RESULT.unlink(missing_ok=True)

    conflicted: list[str] = []
    if conflict:
        # The checkout keeps no credentials, so pass the token for this fetch
        # only (private repositories need it).
        url = f"https://x-access-token:{env('GH_TOKEN')}@github.com/{repo}.git"
        res = subprocess.run(["git", "fetch", "--no-tags", url,
                              f"+refs/heads/{base}:refs/remotes/origin/{base}"],
                             capture_output=True, text=True)
        if res.returncode != 0:
            raise SystemExit("fetching the base branch failed: "
                             + res.stderr.replace(env("GH_TOKEN") or "\0", "***"))
        sh("git", "merge", "--no-ff", "--no-commit", f"origin/{base}", check=False)
        conflicted = [l for l in sh("git", "diff", "--name-only", "--diff-filter=U",
                                    quiet=True).splitlines() if l]
    CONFLICTS.write_text("".join(f"{f}\n" for f in conflicted))

    logs = WORK / "logs"
    logs.mkdir(exist_ok=True)
    fails = failing()
    for f in fails:
        if not f.get("actions_job"):
            continue
        res = subprocess.run(["gh", "api", f"repos/{repo}/actions/jobs/{f['id']}/logs"],
                             capture_output=True, text=True)
        lines = (res.stdout or res.stderr).splitlines()
        # Strip the timestamp prefix GitHub puts on every line.
        lines = [re.sub(r"^\d{4}-\d\d-\d\dT[\d:.]+Z ", "", l) for l in lines]
        (logs / f"{f['id']}.log").write_text("\n".join(lines[-300:]) + "\n")

    TASK.write_text(task_text(head, base, conflict, conflicted, fails))
    print(TASK.read_text())


def task_text(head: str, base: str, conflict: bool, conflicted: list[str],
              fails: list[dict]) -> str:
    protected = env("AUTOFIX_PROTECTED_PATHS")
    notes = env("AUTOFIX_REPO_NOTES").strip()
    problems = []
    if conflict:
        if conflicted:
            problems.append(
                f"- **Merge conflicts with `origin/{base}`.** The merge is already "
                "in progress. Resolve the conflict markers in:\n"
                + "".join(f"  - `{f}`\n" for f in conflicted))
        else:
            problems.append(f"- The merge with `origin/{base}` applied cleanly; "
                            "nothing to resolve unless a check also fails.")
    for f in fails:
        log = (f"`.autofix/logs/{f['id']}.log` (last 300 lines)"
               if f.get("actions_job") else "no log available")
        problems.append(f"- **Failing check `{f['name']}`**: {log}. Run: {f.get('url')}")

    rules = [
        "Edit files in the working tree only. Do not run `git add`, `commit`, "
        "`push`, `merge`, `reset`, `checkout`, `stash` or `rebase`: the workflow "
        "commits and pushes after you, and it rejects attempts that change git "
        "state or the remote branch.",
        "Make the smallest correct change. Do not refactor, rename, reformat "
        "untouched code, or fix unrelated problems you happen to notice.",
        "Conflicts: remove every `<<<<<<<` / `=======` / `>>>>>>>` marker and "
        "keep the intent of both sides. For generated files (lockfiles, files a "
        "script produces), run the generator rather than hand-merging. Delete a "
        "file only when one side deleted it.",
        "Failing checks: read the log tail, find the root cause, and fix it. If "
        "the check is a staleness `--check` for generated output, run the "
        "generator. Re-run the failing check locally when it is cheap (a "
        "linter, formatter, `--check` script, or one focused test). Do not run "
        "long benchmarks or whole test suites.",
        "Never make a check pass by weakening it: no deleted or skipped tests, "
        "relaxed thresholds, edited CI workflows, or new lint suppressions. "
        "Escalate instead.",
        "Never fabricate a command, output, timing, statistic, or result.",
    ]
    if protected:
        rules.append(f"Do not create, edit or delete any path matching "
                     f"`{protected}`. Those records belong to a human owner; "
                     "if the fix needs one, escalate.")
    rules.append(
        "Escalate rather than guess when the two sides of a conflict are "
        "incompatible and choosing needs a design decision, the fix needs "
        "changes well outside this PR's scope, or you are not confident. If "
        "the failure is in code this PR did not touch and looks like a flaky "
        "test or CI infrastructure problem, report `rerun` instead.")
    numbered = "".join(f"{i}. {r}\n" for i, r in enumerate(rules, 1))
    notes_block = f"\n## Repository notes\n\n{notes}\n" if notes else ""
    problem_block = "\n".join(problems)
    return f"""# Autofix task: PR #{env('PR')} ({env('GITHUB_REPOSITORY')})

You are an unattended CI janitor running in GitHub Actions on branch
`{head}`. Make this pull request mergeable and green with the smallest
correct change, and nothing else.
{notes_block}
## Problems

{problem_block}

## Rules

{numbered}
## Finish

Write `.autofix/result.json` as your last action:

```json
{{"status": "fixed", "summary": "one or two sentences on what you changed and why", "commit_title": "short imperative title"}}
```

`status` is one of `fixed`, `rerun` (no change needed; failures look flaky or
infrastructural), or `escalate` (you could not fix it safely; say why in
`summary`). An attempt without this file counts as a failure.
"""


# --------------------------------------------------------------------------
def touched_files() -> list[str]:
    changed = sh("git", "diff", "--name-only", quiet=True).splitlines()
    untracked = sh("git", "ls-files", "--others", "--exclude-standard",
                   quiet=True).splitlines()
    return sorted({f for f in changed + untracked if f})


def verify() -> None:
    def reject(reason: str, status: str = "failed") -> None:
        output(ok="false", status=status, reason=oneline(reason))
        sys.exit(0)

    repo, head = env("GITHUB_REPOSITORY"), env("HEAD_REF")
    start = START.read_text().strip()

    remote = sh("gh", "api", f"repos/{repo}/git/ref/heads/{head}", "--jq",
                ".object.sha", quiet=True).strip()
    if remote != start:
        reject(f"remote branch moved during the attempt ({start[:8]} -> "
               f"{remote[:8]}); someone else pushed, so this attempt is discarded",
               status="stale")
    if sh("git", "rev-parse", "HEAD", quiet=True).strip() != start:
        reject("the model changed HEAD (committed or reset); attempts may only "
               "edit files")

    try:
        result = json.loads(RESULT.read_text())
    except (OSError, ValueError):
        reject("no valid .autofix/result.json (the run probably hit its turn "
               "limit or crashed)")
    status = result.get("status")
    summary = str(result.get("summary", "")).strip()
    if status not in {"fixed", "rerun", "escalate"}:
        reject(f"unknown status {status!r}")
    if status == "escalate":
        reject(summary or "model escalated without a reason", status="escalate")

    conflicted = [l for l in CONFLICTS.read_text().splitlines() if l]
    merging = Path(".git/MERGE_HEAD").exists()
    for f in conflicted:
        p = Path(f)
        if p.is_file() and MARKER.search(p.read_text(errors="replace")):
            reject(f"conflict markers remain in {f}")

    touched = touched_files()
    pattern = env("AUTOFIX_PROTECTED_PATHS")
    if pattern:
        bad = [f for f in touched if re.search(pattern, f)]
        if bad:
            reject("touched protected paths: " + ", ".join(bad))
    if any(f.startswith(".github/workflows/") for f in touched):
        reject("edited CI workflows, which autofix may not do")

    if status == "rerun":
        if touched or merging:
            reject("reported `rerun` but also changed files or has a merge to commit")
        if not failing():
            reject("reported `rerun` but there are no failed checks to re-run")
    elif not touched and not merging:
        reject("reported `fixed` but changed nothing")

    title = str(result.get("commit_title", "")).strip()[:72] or "fix failing checks"
    WORK.joinpath("summary.txt").write_text(summary + "\n")
    output(ok="true", status=status, reason=oneline(summary),
           title=oneline(title))


def commit() -> None:
    repo, head, base = env("GITHUB_REPOSITORY"), env("HEAD_REF"), env("BASE_REF")
    model = env("MODEL")
    title = env("TITLE") or "fix failing checks"
    summary = WORK.joinpath("summary.txt").read_text().strip() \
        if WORK.joinpath("summary.txt").exists() else ""
    merging = Path(".git/MERGE_HEAD").exists()

    sh("git", "add", "-A")
    subject = (f"Merge origin/{base} into {head}" if merging
               else f"autofix: {title}")
    body = summary + ("\n\n" if summary else "") + \
        f"Autofix-Model: {model}\nAutofix-Tier: {env('TIER_USED')}"
    sh("git", "commit", "-m", subject, "-m", body)
    sha = sh("git", "rev-parse", "HEAD", quiet=True).strip()
    url = f"https://x-access-token:{env('PUSH_TOKEN')}@github.com/{repo}.git"
    # Plain push, never --force: if the branch moved, this fails and the
    # work is discarded rather than overwriting someone else's commit.
    res = subprocess.run(["git", "push", url, f"HEAD:refs/heads/{head}"],
                         capture_output=True, text=True)
    if res.returncode != 0:
        sys.stderr.write(res.stderr.replace(env("PUSH_TOKEN") or "\0", "***"))
        raise SystemExit("push rejected; the branch probably moved")
    output(sha=sha)


def rerun() -> None:
    repo = env("GITHUB_REPOSITORY")
    runs = set()
    for f in failing():
        if f.get("actions_job"):
            runs.add(sh("gh", "api", f"repos/{repo}/actions/jobs/{f['id']}",
                        "--jq", ".run_id", quiet=True).strip())
    for run in sorted(runs):
        sh("gh", "run", "rerun", run, "--failed", "-R", repo, check=False)
    output(reruns=str(len(runs)))


if __name__ == "__main__":
    cmds = {"prepare": prepare, "verify": verify, "commit": commit, "rerun": rerun}
    if len(sys.argv) != 2 or sys.argv[1] not in cmds:
        raise SystemExit(f"usage: {sys.argv[0]} {{{','.join(cmds)}}}")
    cmds[sys.argv[1]]()
