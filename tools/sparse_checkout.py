#!/usr/bin/env python3
"""Sparse checkouts: run the harness without materializing 9 GB of archive.

A full checkout is about 9.3 GB and 7 GB of it is immutable archive that an
execution session never reads: experiment run directories
(`experiments/*/runs/`, 5 GB), reference bundles under `inputs/` (1.5 GB) and
cold index-calculus research outputs. The `harness` profile is everything
else (about 2.4 GB), plus the run directories of every experiment with a
trial plan -- `newest_experiments.py` and `experiment_execution.py` hash
those receipts to decide what is still planned -- plus whatever
`--experiment`, `--goal` or `--path` names. docs/sparse-checkout.md.

    python3 tools/sparse_checkout.py status [--json]
    python3 tools/sparse_checkout.py apply harness [--experiment EXP-ID] [--goal GOAL-ID] [--path P]
    python3 tools/sparse_checkout.py add --experiment EXP-ID     # widen the current profile
    python3 tools/sparse_checkout.py patterns harness             # print the rules, change nothing
    python3 tools/sparse_checkout.py disable                      # back to a full checkout
    python3 tools/sparse_checkout.py clone URL DIR [--branch B]   # blobless clone + harness profile
    python3 tools/sparse_checkout.py deepen                       # unshallow: commits and trees, no blobs

Excluding a path hides it from the filesystem, not from git: it stays in HEAD
and in the index with the skip-worktree bit. Absence on disk is therefore not
absence from the repository. `tracked_absent()` answers what the filesystem
cannot, and the selector, the runner and the id allocator use it. Whole-ledger
sweeps (validate_ledger, goal_portfolio_health, portfolio_kpis) need a full
checkout and refuse a sparse one (`refuse_if_sparse`).

Standard library only, so `clone` runs from a copy of this file before any
checkout exists.
"""
from __future__ import annotations

import argparse
import bisect
import fnmatch
import functools
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# State lives in the sparse-checkout file itself, as comment lines git keeps
# and ignores, so it is per-worktree exactly like the rules it describes.
STATE = "# sparse_checkout.py"

PROFILES: dict[str, dict] = {
    "harness": {
        "summary": "everything except run archives, reference bundles and cold research outputs",
        # Each entry is excluded wholesale; a named experiment or path re-includes
        # its part (later rules win, and git matches full paths, so re-including a
        # file under an excluded directory works).
        "exclude": (
            "/experiments/*/runs/",                     # 5.1 GB, 42k files
            "/experiments/*/implementation/runs/",      # 1.4 GB of LFS stage caches
            "/inputs/refs/",                            # 1.1 GB, includes committed Rust build trees
            "/inputs/archive_from_autolab/",            # 0.17 GB
            "/inputs/pqshield-signature-zoo-20260928/",  # 0.15 GB
            "/research/cold_*/",                        # 0.34 GB of IC run outputs
        ),
    },
}

# Repository-relative paths an experiment's own records may name as inputs.
_REF_ROOTS = ("inputs", "research", "experiments", "coordination", "knowledge",
              "ledger", "harness", "analysis", "focus", "notes", "outputs")
PATH_REF = re.compile(
    r"(?<![\w./-])((?:%s)/[\w.@+=,-]+(?:/[\w.@+=,-]+)*)" % "|".join(_REF_ROOTS))
GOAL_ID = re.compile(r"^\s*goal_id:\s*['\"]?(GOAL-[A-Za-z0-9-]+)", re.M)
EXP_ID = re.compile(r"EXP-[A-Za-z0-9]+-(?:[0-9a-fA-F]{6}|\d{3})\Z")
# Records an experiment directory keeps beside its specification that may name inputs.
_REF_SOURCES = ("specification.yaml", "trial-plan.json", "dependencies.json")


class SparseError(RuntimeError):
    """A checkout state this tool will not change silently."""


def git(repo: Path, *args: str, stdin: str | None = None, check: bool = True) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], input=stdin,
                          capture_output=True, text=True, check=False)
    if check and proc.returncode:
        raise SparseError(f"git {' '.join(args[:2])} failed: {proc.stderr.strip()}")
    return proc.stdout


def _toplevel(repo: Path) -> Path | None:
    try:
        proc = subprocess.run(["git", "-C", str(repo), "rev-parse", "--show-toplevel"],
                              capture_output=True, text=True, check=False)
    except OSError:
        return None
    if proc.returncode:
        return None
    return Path(proc.stdout.strip()).resolve()


# --- queries other tools use -------------------------------------------------

@functools.lru_cache(maxsize=None)
def _is_sparse(repo: str) -> bool:
    root = Path(repo)
    if _toplevel(root) != root:  # a fixture directory inside some other checkout
        return False
    return git(root, "config", "--bool", "core.sparseCheckout", check=False).strip() == "true"


def is_sparse(repo: Path = REPO) -> bool:
    """Whether `repo` is the root of a worktree with sparse checkout enabled."""
    return _is_sparse(str(Path(repo).resolve()))


@functools.lru_cache(maxsize=None)
def _skipped(repo: str) -> tuple[str, ...]:
    if not _is_sparse(repo):
        return ()
    out = git(Path(repo), "ls-files", "-t", "-z", check=False)
    return tuple(sorted(entry[2:] for entry in out.split("\0") if entry.startswith("S ")))


def tracked_absent(repo: Path, prefix: str) -> list[str]:
    """Tracked paths under `prefix` that this sparse checkout leaves off disk.

    Empty in a full checkout. `prefix` is repository-relative; give a trailing
    slash for a directory so `runs/` does not also match `runs-old/`.
    """
    entries = _skipped(str(Path(repo).resolve()))
    if not entries:
        return []
    start = bisect.bisect_left(entries, prefix)
    out = []
    for entry in entries[start:]:
        if not entry.startswith(prefix):
            break
        out.append(entry)
    return out


def outside_definition(repo: Path, paths: list[str]) -> list[str]:
    """Paths (tracked or not yet created) the sparse rules would leave off disk.

    `git add` refuses such paths, so a run directory created outside the
    definition could be executed but never published.
    """
    if not paths or not is_sparse(repo):
        return []
    inside = set(git(Path(repo), "sparse-checkout", "check-rules",
                     stdin="".join(f"{p}\n" for p in paths), check=False).splitlines())
    return [p for p in paths if p not in inside]


def refuse_if_sparse(tool: str, repo: Path = REPO) -> bool:
    """Whole-repository sweeps refuse a sparse checkout; True means refused.

    Off-disk records read as missing to them: validate_ledger reports ~2,000
    false errors and portfolio_kpis counts run contracts as unrun, which moves
    approval capacity. A refusal is cheaper than a session repairing records
    that are fine. CRYPTO_AR_ALLOW_SPARSE=1 runs anyway, over what is on disk.
    """
    if not is_sparse(repo):
        return False
    count = len(_skipped(str(Path(repo).resolve())))
    if os.environ.get("CRYPTO_AR_ALLOW_SPARSE") == "1":
        print(f"{tool}: sparse checkout, {count} tracked files off disk; results cover "
              "materialized paths only (CRYPTO_AR_ALLOW_SPARSE=1)", file=sys.stderr)
        return False
    print(f"{tool}: refused in a sparse checkout: {count} tracked files are off disk and "
          "would read as missing records. Run it in a full checkout or after `python3 "
          "tools/sparse_checkout.py disable`; CRYPTO_AR_ALLOW_SPARSE=1 runs it over what "
          "is on disk (docs/sparse-checkout.md)", file=sys.stderr)
    return True


def materialize_hint(experiment_id: str) -> str:
    return f"python3 tools/sparse_checkout.py add --experiment {experiment_id}"


# --- profile state ------------------------------------------------------------

def _rules_file(repo: Path) -> Path:
    path = Path(git(repo, "rev-parse", "--git-path", "info/sparse-checkout").strip())
    return path if path.is_absolute() else repo / path


def read_state(repo: Path) -> dict | None:
    """The profile this tool last applied, or None (full, or rules set by hand)."""
    if not is_sparse(repo):
        return None
    try:
        lines = _rules_file(repo).read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    state: dict = {"profile": None, "experiments": [], "paths": []}
    for line in lines:
        if not line.startswith(STATE + " "):
            continue
        key, _, value = line[len(STATE) + 1:].partition("=")
        if key == "profile":
            state["profile"] = value
        elif key == "experiment":
            state["experiments"].append(value)
        elif key == "path":
            state["paths"].append(value)
    return state if state["profile"] else None


@functools.lru_cache(maxsize=None)
def _tracked(repo: str) -> tuple[str, ...]:
    out = git(Path(repo), "ls-files", "-z", check=False)
    if not out:  # a --no-checkout clone has an empty index; its trees are local
        out = git(Path(repo), "ls-tree", "-r", "--name-only", "-z", "HEAD", check=False)
    return tuple(sorted(p for p in out.split("\0") if p))


def _tracked_prefix(entries: tuple[str, ...], prefix: str) -> bool:
    i = bisect.bisect_left(entries, prefix)
    return i < len(entries) and entries[i].startswith(prefix)


def plan_experiments(repo: Path) -> list[str]:
    """Experiments with a committed trial plan: their runs/ decide coverage."""
    out = []
    for path in _tracked(str(repo)):
        parts = path.split("/")
        if len(parts) == 3 and parts[0] == "experiments" and parts[2] == "trial-plan.json":
            out.append(parts[1])
    return sorted(set(out))


def _read(repo: Path, relative: str) -> str:
    file = repo / relative
    if file.is_file():
        return file.read_text(encoding="utf-8", errors="replace")
    # Not on disk: one blob from HEAD (fetched on demand in a blobless clone).
    return git(repo, "show", f"HEAD:{relative}", check=False)


def goal_experiments(repo: Path, goal_id: str) -> list[str]:
    """Experiments whose specification names `goal_id` (no scan of runs or ledger)."""
    found = []
    for path in _tracked(str(repo)):
        parts = path.split("/")
        if len(parts) == 3 and parts[0] == "experiments" and parts[2] == "specification.yaml":
            if goal_id in GOAL_ID.findall(_read(repo, path)):
                found.append(parts[1])
    return sorted(found)


def experiment_references(repo: Path, experiment_id: str) -> list[str]:
    """Tracked repository paths an experiment's specification or plan names.

    Returns rule-ready entries: `dir/` for a directory, the path for a file.
    Only paths git actually tracks are returned, so prose that happens to look
    like a path adds nothing.
    """
    entries = _tracked(str(repo))
    refs: set[str] = set()
    for name in _REF_SOURCES:
        text = _read(repo, f"experiments/{experiment_id}/{name}")
        for raw in PATH_REF.findall(text):
            candidate = raw.rstrip(".,:;")
            i = bisect.bisect_left(entries, candidate)
            if i < len(entries) and entries[i] == candidate:
                refs.add(candidate)
            elif _tracked_prefix(entries, candidate.rstrip("/") + "/"):
                refs.add(candidate.rstrip("/") + "/")
    return sorted(refs)


def render(repo: Path, profile: str, experiments: list[str] = (),
           paths: list[str] = ()) -> list[str]:
    """The full sparse-checkout rule file for a profile and its additions."""
    if profile not in PROFILES:
        raise SparseError(f"unknown profile {profile!r}; known: {', '.join(PROFILES)}")
    for exp in experiments:
        if not EXP_ID.match(exp):
            raise SparseError(f"not an experiment id: {exp!r}")
    lines = [f"{STATE} profile={profile}"]
    lines += [f"{STATE} experiment={e}" for e in experiments]
    lines += [f"{STATE} path={p}" for p in paths]
    lines += ["/*", *(f"!{rule}" for rule in PROFILES[profile]["exclude"])]
    lines.append("# trial-plan coverage hashes these receipts")
    lines += [f"/experiments/{e}/runs/" for e in plan_experiments(repo)]
    if experiments:
        lines.append("# named experiments, whole, and the inputs their records name")
    for exp in experiments:
        lines += _include(profile, f"experiments/{exp}/")
        for ref in experiment_references(repo, exp):
            lines += _include(profile, ref)
    if paths:
        lines.append("# named paths")
    for path in paths:
        lines += _include(profile, path.strip("/") + ("/" if path.endswith("/") else ""))
    return lines


def _include(profile: str, path: str) -> list[str]:
    """Rules that put `path` on disk, including excluded subtrees beneath it.

    A directory rule does not override a more specific exclusion under it
    (`/experiments/X/` leaves `experiments/X/runs/` excluded), so each
    exclusion the path contains is re-included explicitly.
    """
    rules = [f"/{path}"]
    if not path.endswith("/"):
        return rules
    mine = path.strip("/").split("/")
    for rule in PROFILES[profile]["exclude"]:
        theirs = rule.strip("/").split("/")
        if len(theirs) > len(mine) and all(
                fnmatch.fnmatchcase(m, t) for m, t in zip(mine, theirs)):
            rules.append("/" + "/".join(mine + theirs[len(mine):]) + "/")
    return rules


def _clear_caches() -> None:
    for cached in (_is_sparse, _skipped, _tracked):
        cached.cache_clear()


def apply(repo: Path, profile: str, experiments: list[str] = (),
          paths: list[str] = ()) -> dict:
    """Set the rules and update the working tree. Untracked files are never removed."""
    repo = repo.resolve()
    if _toplevel(repo) != repo:
        raise SparseError(f"{repo} is not the root of a git worktree")
    experiments = sorted(set(experiments))
    paths = sorted(set(paths))
    rules = render(repo, profile, experiments, paths)
    git(repo, "sparse-checkout", "set", "--no-cone", "--stdin", stdin="\n".join(rules) + "\n")
    _clear_caches()
    return summary(repo)


def summary(repo: Path) -> dict:
    repo = repo.resolve()
    state = read_state(repo)
    skipped = len(_skipped(str(repo)))
    tracked = len(_tracked(str(repo)))
    return {
        "sparse": is_sparse(repo),
        "profile": state["profile"] if state else None,
        "experiments": state["experiments"] if state else [],
        "paths": state["paths"] if state else [],
        "tracked_files": tracked,
        "materialized_files": tracked - skipped,
        "skipped_files": skipped,
        "partial_clone_filter": git(repo, "config", "remote.origin.partialclonefilter",
                                    check=False).strip() or None,
        "shallow": git(repo, "rev-parse", "--is-shallow-repository", check=False).strip() == "true",
    }


def deepen(repo: Path) -> tuple[bool, str]:
    """Unshallow without historical blobs: archive checks need commits, not contents.

    `--filter=blob:none` turns the clone into a partial clone: history arrives
    as commits and trees, and an old file version is fetched only if something
    reads it. The plain unshallow it replaces downloaded every blob of every
    branch. Falls back to it when the remote refuses filters.
    """
    if git(repo, "rev-parse", "--is-shallow-repository", check=False).strip() != "true":
        return True, "not shallow"
    attempts = (["fetch", "--unshallow", "--filter=blob:none", "origin"],
                ["fetch", "--unshallow", "origin"])
    detail = ""
    for args in attempts:
        proc = subprocess.run(["git", "-C", str(repo), *args],
                              capture_output=True, text=True, check=False)
        if proc.returncode == 0 and git(repo, "rev-parse", "--is-shallow-repository",
                                        check=False).strip() != "true":
            return True, f"deepened via `git {' '.join(args)}`"
        lines = (proc.stderr or proc.stdout).strip().splitlines()
        detail = lines[-1] if lines else f"git exited {proc.returncode}"
    return False, detail


def clone(url: str, directory: Path, *, branch: str | None, profile: str,
          experiments: list[str], paths: list[str]) -> dict:
    """Blobless clone, then the profile: only materialized files are downloaded."""
    cmd = ["git", "clone", "--filter=blob:none", "--no-checkout"]
    if branch:
        cmd += ["--branch", branch]
    subprocess.run([*cmd, url, str(directory)], check=True)
    repo = directory.resolve()
    git(repo, "sparse-checkout", "set", "--no-cone", "--stdin",
        stdin="\n".join(render(repo, profile)) + "\n")
    git(repo, "checkout", "-f", "HEAD")
    _clear_caches()
    if experiments or paths:
        return apply(repo, profile, experiments, paths)
    return summary(repo)


# --- command line ---------------------------------------------------------------

def _print_summary(info: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(info, indent=2))
        return
    if not info["sparse"]:
        print(f"full checkout: {info['tracked_files']} tracked files on disk")
    else:
        what = f"profile {info['profile']}" if info["profile"] else "rules not set by this tool"
        print(f"sparse checkout ({what}): {info['materialized_files']} of "
              f"{info['tracked_files']} tracked files on disk, {info['skipped_files']} skipped")
        for exp in info["experiments"]:
            print(f"  + experiment {exp}")
        for path in info["paths"]:
            print(f"  + path {path}")
    print(f"history: {'shallow' if info['shallow'] else 'complete'}; "
          f"partial clone filter: {info['partial_clone_filter'] or 'none'}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", type=Path, default=None,
                        help="worktree root (default: the checkout holding this file, else cwd)")
    sub = parser.add_subparsers(dest="command", required=True)

    def additions(p: argparse.ArgumentParser) -> None:
        p.add_argument("--experiment", action="append", default=[], metavar="EXP-ID",
                       help="materialize this experiment whole, with the inputs it names")
        p.add_argument("--goal", action="append", default=[], metavar="GOAL-ID",
                       help="every experiment whose specification names this goal")
        p.add_argument("--path", action="append", default=[], metavar="PATH",
                       help="materialize a repository path (end a directory with /)")

    p_status = sub.add_parser("status", help="what is on disk and what is not")
    p_status.add_argument("--json", action="store_true")
    for name, help_text in (("apply", "set a profile (replaces earlier additions)"),
                            ("patterns", "print the rules a profile would set")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("profile", nargs="?", default="harness", choices=sorted(PROFILES))
        additions(p)
        if name == "apply":
            p.add_argument("--json", action="store_true")
    p_add = sub.add_parser("add", help="widen the current profile")
    additions(p_add)
    p_add.add_argument("--json", action="store_true")
    sub.add_parser("disable", help="materialize everything (downloads it in a blobless clone)")
    p_clone = sub.add_parser("clone", help="blobless clone with a profile applied")
    p_clone.add_argument("url")
    p_clone.add_argument("directory", type=Path)
    p_clone.add_argument("--branch")
    p_clone.add_argument("--profile", default="harness", choices=sorted(PROFILES))
    additions(p_clone)
    sub.add_parser("deepen", help="unshallow with commits and trees only")
    args = parser.parse_args(argv)

    if args.command == "clone":
        try:
            if args.goal:
                raise SparseError("--goal needs the specifications; clone first, then `add --goal`")
            info = clone(args.url, args.directory, branch=args.branch, profile=args.profile,
                         experiments=args.experiment, paths=args.path)
        except (SparseError, subprocess.CalledProcessError) as error:
            print(f"sparse_checkout: {error}", file=sys.stderr)
            return 2
        _print_summary(info, False)
        return 0

    repo = (args.repo or (REPO if _toplevel(REPO) == REPO else Path.cwd())).resolve()
    top = _toplevel(repo)
    if top is None:
        print(f"sparse_checkout: {repo} is not inside a git worktree", file=sys.stderr)
        return 2
    repo = top
    try:
        if args.command == "status":
            _print_summary(summary(repo), args.json)
            return 0
        if args.command == "deepen":
            ok, detail = deepen(repo)
            print(detail)
            return 0 if ok else 1
        if args.command == "disable":
            git(repo, "sparse-checkout", "disable")
            _clear_caches()
            _print_summary(summary(repo), False)
            return 0
        experiments = list(args.experiment)
        for goal in args.goal:
            found = goal_experiments(repo, goal)
            if not found:
                print(f"sparse_checkout: no specification names {goal}", file=sys.stderr)
            experiments += found
        if args.command == "patterns":
            print("\n".join(render(repo, args.profile, sorted(set(experiments)),
                                   sorted(set(args.path)))))
            return 0
        if args.command == "add":
            state = read_state(repo)
            if state is None:
                raise SparseError("no profile applied here; use `apply harness` first")
            info = apply(repo, state["profile"], state["experiments"] + experiments,
                         state["paths"] + args.path)
        else:
            info = apply(repo, args.profile, experiments, args.path)
        _print_summary(info, args.json)
        return 0
    except SparseError as error:
        print(f"sparse_checkout: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
