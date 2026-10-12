#!/usr/bin/env python3
"""Select CI work from a complete local Git diff; never use GitHub's 300-file filter.

Required workflows always start. Only positively identified documentation and
corpus-only changes skip software jobs. Unknown paths, dependencies and CI
changes run every software gate. Errors resolving a diff fail the caller.
Renames are examined as delete + add, so moving code into docs cannot hide it.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys

GATES = ("ledger", "static", "tests", "runtime", "progress", "full_checkout",
         "knowledge_index", "source_index", "frontier", "autolab")
CORPUS_ROOTS = {"ledger", "experiments", "knowledge", "coordination", "ideas", "inputs", "research"}
DOC_SUFFIXES = {".md", ".txt", ".pdf", ".png", ".jpg", ".jpeg", ".svg", ".tex", ".bib"}
CODE_SUFFIXES = {".py", ".sage", ".sh", ".c", ".h", ".cpp", ".cu", ".rs", ".js", ".cjs", ".mjs", ".ts", ".tsx", ".lean"}
ROOT_DOCS = {"README.md", "ROADMAP.md", "PUBLICATION-CANDIDATES.md", "plan.md", "research_ledger.md"}


def classify(paths: list[str], *, force: bool = False) -> dict[str, bool]:
    gates = dict.fromkeys(GATES, force)
    for path in paths:
        p = PurePosixPath(path)
        root = p.parts[0] if p.parts else ""
        if path in ROOT_DOCS or (root in {"docs", "papers"} and p.suffix.lower() in DOC_SUFFIXES):
            continue
        if root in CORPUS_ROOTS and p.suffix.lower() not in CODE_SUFFIXES:
            for gate in ("ledger", "static", "full_checkout"):
                gates[gate] = True
            if root == "knowledge":
                gates["knowledge_index"] = True
            if root == "inputs" or path.startswith("knowledge/literature/") or path in {"knowledge/SOURCES.md", "knowledge/sources.json"}:
                gates["source_index"] = True
            # The frontier map resolves internal record IDs across corpus roots.
            gates["frontier"] = True
            if root in {"experiments", "inputs"}:
                gates["autolab"] = True
            continue
        if root == "claims" and p.suffix.lower() not in CODE_SUFFIXES:
            gates["progress"] = True
            continue
        # There is no permissive default. New file families must first acquire
        # an explicit classification and regression tests before they can skip.
        gates = dict.fromkeys(GATES, True)
    return gates


# Source families whose relationship to the proof harness is known. A new
# top-level family is conservative; add it here only after checking imports.
NON_FORMAL_ROOTS = CORPUS_ROOTS | {
    "claims", "ui", "src", "harness", "scripts", "plugins", "kb", "groebner_compare",
    "tasks", "templates", "analysis", "outputs", "examples", "notes", "third_party",
    "cairn", "cli", "config", "focus", "xcrun_db", "research_digest",
}
FORMAL_DEPENDENCIES = {"pyproject.toml", "Makefile", ".python-version", "conftest.py", "setup.py", "setup.cfg", "uv.lock"}
FORMAL_TOOLS = {"tools/verify_formal_targets.py", "tools/rebuild_formal_root.py"}
FORMAL_TESTS = {
    "tests/test_lean_live.py", "tests/test_mathcode_formalizer.py",
    "tests/test_verify_formal_targets.py", "tests/conftest.py",
}


def formal_scope(paths: list[str], *, force: bool = False) -> tuple[bool, bool]:
    kernel = workspace = force
    for path in paths:
        p = PurePosixPath(path)
        root = p.parts[0] if p.parts else ""
        if path in ROOT_DOCS or (root in {"docs", "papers"} and p.suffix.lower() in DOC_SUFFIXES):
            continue
        if root == "formal":
            if p.suffix == ".md":
                continue
            kernel = True
            if not path.startswith("formal/smoke/"):
                workspace = True
            continue
        if path in FORMAL_TESTS or path.startswith("tests/test_formal") or path.startswith("tests/fixtures/"):
            kernel = True
            continue
        if root == "orchestration" or root == ".github" or path in FORMAL_DEPENDENCIES or path.startswith("requirements") or path in FORMAL_TOOLS:
            kernel = workspace = True
            continue
        # Kernel target tests assert that their source documents exist. Corpus
        # changes can remove those sources without changing any proof input.
        if root == "research" or root == "tools":
            kernel = True
            continue
        if root in NON_FORMAL_ROOTS or root == "tests":
            continue
        kernel = workspace = True
    return kernel, workspace


def formal_workspace_needed(paths: list[str], *, force: bool = False) -> bool:
    return formal_scope(paths, force=force)[1]


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True,
                          text=True).stdout.strip()


def resolve_base(event: dict, event_name: str) -> tuple[str | None, bool]:
    if event_name == "pull_request":
        # checkout's test merge uses the CURRENT base, unlike the event's
        # potentially stale pull_request.base.sha. Compare exactly that merge.
        parents = git("rev-list", "--parents", "-n", "1", "HEAD").split()
        base = parents[1] if len(parents) > 2 else event["pull_request"]["base"]["sha"]
    elif event_name == "merge_group":
        base = event["merge_group"]["base_sha"]
    elif event_name == "push":
        base = event["before"]
        if not base or set(base) == {"0"}:
            return None, True
    else:
        return None, True
    git("rev-parse", "--verify", f"{base}^{{commit}}")
    return base, False


def changed_paths(base: str) -> list[str]:
    # --no-renames includes the source AND destination; -z preserves spaces,
    # newlines and non-ASCII names. No diff-filter: deletions matter too.
    result = subprocess.run(["git", "diff", "--name-only", "--no-renames", "-z",
                             base, "HEAD", "--"], check=True, capture_output=True)
    return sorted(set(os.fsdecode(p) for p in result.stdout.split(b"\0") if p))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", type=Path, default=os.environ.get("GITHUB_EVENT_PATH"))
    parser.add_argument("--event-name", default=os.environ.get("GITHUB_EVENT_NAME"))
    parser.add_argument("--output", type=Path, default=os.environ.get("GITHUB_OUTPUT"))
    args = parser.parse_args()
    if not args.event or not args.event_name:
        parser.error("--event and --event-name are required")
    event = json.loads(args.event.read_text())
    base, force = resolve_base(event, args.event_name)
    paths = changed_paths(base) if base else []
    gates = classify(paths, force=force)
    gates["formal_kernel"], gates["formal_workspace"] = formal_scope(paths, force=force)
    print(json.dumps({"base": base, "changed_files": len(paths), "gates": gates}, indent=2))
    if args.output:
        with args.output.open("a") as stream:
            stream.write(f"base={base or ''}\n")
            for gate, enabled in gates.items():
                stream.write(f"{gate}={str(enabled).lower()}\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"CI scope failed; no gate may treat this as an empty diff: {exc}", file=sys.stderr)
        raise SystemExit(1)
