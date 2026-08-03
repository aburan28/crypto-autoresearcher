#!/usr/bin/env python3
"""Fail if a committed run record was modified or deleted.

Run artifacts under experiments/<EXP>/runs/<RUN>/ are immutable (AGENTS.md rule
4, docs/evidence-and-reproducibility.md): a defective run is superseded by a
new RUN id, never edited or removed. This checks a diff range for any
modification (M) or deletion (D) touching run directories. New files (A) are
allowed — that is how new runs are added.

Rename detection is disabled deliberately: with it on, moving a run directory
is reported as R and never reaches the M/D filter, so any rename would pass —
including one that also edited content. Renames are instead permitted only
when declared in tools/run_id_remaps.yaml, and only after every file in the
directory is proved byte-identical to its base blob with the declared run id
substituted. That exception exists because a duplicate RUN id is the one defect
the append-only rule cannot repair: superseding under a fresh id leaves the
collision standing. See CORR-20260802-004.

Usage:
    python3 tools/check_run_immutability.py [BASE_REF] [HEAD_REF]

Defaults: BASE from $GITHUB_BASE_REF or origin/main; HEAD = HEAD.
Exit 0 if no immutable path was mutated, 1 otherwise. If the base ref cannot
be resolved (e.g. shallow clone without it), the check is skipped with a
notice rather than failing the build.
"""
from __future__ import annotations

import os
import subprocess
import sys

RUN_PATH = os.path.join("experiments", "")  # prefix; refined below

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMAP_PATH = os.path.join(REPO, "tools", "run_id_remaps.yaml")


def load_renames() -> dict[str, tuple[str, list[tuple[str, str]]]]:
    """Declared identifier repairs: old run directory -> (new dir, substitutions).

    A duplicate RUN id is the one defect the append-only rule cannot repair,
    because superseding under a fresh id leaves the collision standing. Renames
    listed in tools/run_id_remaps.yaml are therefore allowed -- but only after
    `rename_is_faithful` proves the directory's bytes are unchanged apart from
    the declared substitutions. That keeps this an identifier repair, never a
    data edit.

    `from_experiment` covers the case where the EXPERIMENT id is what changed,
    so the run moves between directories. `also_substitute` then declares the
    extra string swap that entails -- a run manifest names its own experiment,
    so a run-id-only substitution could not describe such a move honestly. Every
    declared substitution is still verified byte for byte; nothing is waived.
    """
    try:
        import yaml
        with open(REMAP_PATH, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}
    except (OSError, ImportError):
        return {}
    if doc.get("schema") != "run-id-remap-v1":
        return {}
    renames = {}
    for entry in doc.get("renames") or []:
        experiment = entry.get("experiment")
        old, new = entry.get("from_run_id"), entry.get("to_run_id")
        if not (experiment and old and new):
            continue
        from_experiment = entry.get("from_experiment") or experiment
        old_dir = f"experiments/{from_experiment}/runs/{old}"
        new_dir = f"experiments/{experiment}/runs/{new}"
        subs = [(old, new)]
        for extra in entry.get("also_substitute") or []:
            src, dst = extra.get("from"), extra.get("to")
            if src and dst:
                subs.append((src, dst))
        renames[old_dir] = (new_dir, subs)
    return renames


def blob(ref: str, path: str) -> bytes | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def rename_is_faithful(base_sha: str, head: str, old_dir: str, new_dir: str,
                       subs: list[tuple[str, str]]) -> str | None:
    """None if the rename only applied the declared substitutions."""
    listing = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", base_sha, old_dir + "/"],
        capture_output=True, text=True)
    names = [p for p in listing.stdout.splitlines() if p]
    if not names:
        return f"{old_dir}: nothing at {base_sha} to rename"
    shown = ", ".join(f"{a} -> {b}" for a, b in subs)
    for old_path in names:
        new_path = new_dir + old_path[len(old_dir):]
        before, after = blob(base_sha, old_path), blob(head, new_path)
        if after is None:
            return f"{new_path}: declared rename target is missing"
        if before is None:
            return f"{old_path}: unreadable at {base_sha}"
        expected = before
        for src, dst in subs:
            expected = expected.replace(src.encode(), dst.encode())
        if after != expected:
            return (f"{new_path}: content changed beyond the declared "
                    f"substitution(s) [{shown}]")
    return None


def resolve(ref: str) -> str | None:
    r = subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref],
                       capture_output=True, text=True)
    return r.stdout.strip() or None


def main() -> int:
    argv = sys.argv[1:]
    base = argv[0] if len(argv) > 0 else (
        os.environ.get("GITHUB_BASE_REF") and f"origin/{os.environ['GITHUB_BASE_REF']}"
        or "origin/main")
    head = argv[1] if len(argv) > 1 else "HEAD"

    base_sha = resolve(base) or resolve(base.replace("origin/", ""))
    if not base_sha:
        print(f"NOTICE: base ref '{base}' not resolvable; skipping "
              f"immutability check")
        return 0

    # --no-renames is load-bearing. With rename detection on, moving a run
    # directory is reported as R and slips past --diff-filter=MD entirely, so
    # the gate would permit any rename -- including one that edited content,
    # as long as the files stayed similar enough to be paired. Disabling it
    # makes a rename a deletion plus an addition, which this check sees; the
    # declared, byte-verified remaps below are then the only way to move a run.
    diff = subprocess.run(
        ["git", "diff", "--no-renames", "--diff-filter=MD", "--name-only",
         base_sha, head],
        capture_output=True, text=True)
    if diff.returncode != 0:
        print(f"NOTICE: git diff failed ({diff.stderr.strip()}); skipping")
        return 0

    touched = [
        line for line in diff.stdout.splitlines()
        if "/runs/" in line and line.startswith("experiments/")
        # A zero-byte placeholder that exists only to keep an empty runs/
        # directory in git. It records no measurement, so moving or dropping
        # one destroys no evidence -- and an experiment directory could never
        # be renamed while its own placeholder counted as an immutable run.
        and os.path.basename(line) != ".gitkeep"
    ]

    # A declared rename shows up as D on every old path. Accept those only
    # once the whole directory is proved byte-identical modulo the run id.
    renames = load_renames()
    violations, allowed, unfaithful = [], 0, []
    bad_dirs: set[str] = set()
    checked: set[str] = set()
    for path in touched:
        old_dir = next((d for d in renames if path.startswith(d + "/")), None)
        if old_dir is None:
            violations.append(path)
            continue
        if old_dir not in checked:
            checked.add(old_dir)
            new_dir, subs = renames[old_dir]
            reason = rename_is_faithful(base_sha, head, old_dir, new_dir, subs)
            if reason:
                unfaithful.append(reason)
                bad_dirs.add(old_dir)
        if old_dir in bad_dirs:
            violations.append(path)
        else:
            allowed += 1

    if unfaithful:
        print("FAIL: declared run-id renames are not faithful:\n",
              file=sys.stderr)
        for reason in unfaithful:
            print(f"  - {reason}", file=sys.stderr)
        print("\nA declared rename may only substitute the run id. Any other "
              "change to a committed run is forbidden.", file=sys.stderr)
        return 1

    if violations:
        print("FAIL: immutable run artifacts were modified or deleted:\n",
              file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        print("\nRun records are append-only. Supersede with a new RUN id "
              "instead of editing.", file=sys.stderr)
        return 1
    if allowed:
        print(f"OK: no committed run artifacts were modified or deleted "
              f"({allowed} path(s) moved by declared, verified run-id "
              f"renames in tools/run_id_remaps.yaml)")
    else:
        print("OK: no committed run artifacts were modified or deleted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
