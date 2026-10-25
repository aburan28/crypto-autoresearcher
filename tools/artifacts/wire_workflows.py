#!/usr/bin/env python3
"""Add an artifact-store pull step to every workflow that names moved data.

After `artifacts.py push` moves files out of Git, a workflow that reads them
(a replay of `research/x/`, a check over `experiments/y/results/`) would find
pointers only. This finds, per workflow file, the repository paths it names
that hold moved files, and inserts after each `actions/checkout` step:

    - name: Pull store data this workflow reads (tools/artifacts)
      env: {AWS_ACCESS_KEY_ID: ..., AWS_SECRET_ACCESS_KEY: ..., AWS_REGION: ...}
      run: python3 tools/artifacts/artifacts.py pull research/x experiments/y/results

A sparse checkout also gets `tools/artifacts` added to its patterns. The edit
is textual (comments and layout survive) and idempotent; checkouts into a
`path:` other than the workspace are reported, not edited.

    python3 tools/artifacts/wire_workflows.py [--check] [WORKFLOW ...]

`--check` edits nothing and exits 1 if any workflow lacks the step it needs,
which is how CI keeps new workflows honest.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artifacts  # noqa: E402

STEP_NAME = "Pull store data this workflow reads (tools/artifacts)"
PATH_RE = re.compile(r"(?<![A-Za-z0-9_./-])((?:[A-Za-z0-9_+-][A-Za-z0-9_.+-]*/)+[A-Za-z0-9_.+*-]*)")


def moved_paths(root: Path) -> set[str]:
    out = set()
    for d, name, _ in artifacts.selected(root, []):
        drel = artifacts.rel(root, d)
        out.add(f"{drel}/{name}" if drel else name)
    return out


def needed(text: str, moved: set[str], dirs: set[str]) -> list[str]:
    """Paths the workflow names that are, or contain, moved files; minimal cover."""
    found = set()
    for m in PATH_RE.finditer(text):
        p = m.group(1).split("*", 1)[0].rstrip("/.")
        while p and p not in moved and p not in dirs:
            p = p.rsplit("/", 1)[0] if "/" in p else ""
        if p:
            found.add(p)
    return sorted(p for p in found if not any(p.startswith(q + "/") for q in found))


def step_lines(indent: str, paths: list[str]) -> list[str]:
    i2 = indent + "  "
    return [
        f"{indent}- name: {STEP_NAME}",
        f"{i2}env:",
        f"{i2}  AWS_ACCESS_KEY_ID: ${{{{ secrets.ARTIFACTS_AWS_ACCESS_KEY_ID }}}}",
        f"{i2}  AWS_SECRET_ACCESS_KEY: ${{{{ secrets.ARTIFACTS_AWS_SECRET_ACCESS_KEY }}}}",
        f"{i2}  AWS_REGION: ${{{{ vars.ARTIFACTS_AWS_REGION || 'us-west-2' }}}}",
        f"{i2}run: python3 tools/artifacts/artifacts.py pull --jobs 16 {' '.join(paths)}",
    ]


def wire(text: str, paths: list[str]) -> tuple[str, list[str]]:
    """Insert the pull step after each workspace checkout; returns (text, notes)."""
    lines = text.split("\n")
    notes: list[str] = []
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(\s*)- [A-Za-z_-]+:", line)
        if not m:
            out.append(line)
            i += 1
            continue
        indent = m.group(1)
        j = i + 1
        while j < len(lines) and (not lines[j].strip() or len(lines[j]) - len(lines[j].lstrip()) > len(indent)):
            j += 1
        block = lines[i:j]
        while block and not block[-1].strip():  # keep trailing blank lines after the inserted step
            block.pop()
            j -= 1
        is_checkout = any(re.match(rf"^{indent}(?:- |  )uses: actions/checkout@", b) for b in block)
        if not is_checkout:
            out.append(line)
            i += 1
            continue
        if any(re.match(rf"^{indent}    path: ", b) for b in block):
            notes.append("checkout into a `path:` left unwired")
            out.extend(block)
            i = j
            continue
        block = add_sparse_pattern(block, indent)
        out.extend(block)
        nxt = next((lines[k] for k in range(j, len(lines)) if lines[k].strip()), "")
        if STEP_NAME not in nxt:
            step = step_lines(indent, paths)
            cond = next((re.sub(rf"^{indent}(?:- |  )", "", b) for b in block
                         if re.match(rf"^{indent}(?:- |  )if: ", b)), None)
            if cond:  # skipped with its checkout, so it never runs against an empty workspace
                step.insert(1, f"{indent}  {cond}")
            out.extend(step)
        i = j
    return "\n".join(out), notes


def add_sparse_pattern(block: list[str], indent: str) -> list[str]:
    """Make a sparse checkout also fetch tools/artifacts."""
    for k, b in enumerate(block):
        if re.match(rf"^{indent}    sparse-checkout: \|", b):
            cone = not any("sparse-checkout-cone-mode: false" in x for x in block)
            items = []
            n = k + 1
            while n < len(block) and len(block[n]) - len(block[n].lstrip()) > len(indent) + 4:
                items.append(block[n])
                n += 1
            if any("tools/artifacts" in x or x.strip() in ("/*", "tools", "/tools/") for x in items):
                return block
            pad = (items[0][: len(items[0]) - len(items[0].lstrip())]) if items else indent + "      "
            return block[:n] + [pad + ("tools/artifacts" if cone else "/tools/artifacts/")] + block[n:]
    return block


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("workflows", nargs="*")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    root = artifacts.repo_root()
    moved = moved_paths(root)
    dirs = {p.rsplit("/", n)[0] for p in moved for n in range(1, p.count("/") + 1)}
    files = [Path(w) for w in args.workflows] or sorted((root / ".github/workflows").glob("*.y*ml"))
    missing = 0
    for f in files:
        text = f.read_text()
        paths = needed(text, moved, dirs)
        if not paths:
            continue
        new, notes = wire(text, paths)
        for n in notes:
            print(f"{f.name}: {n}", file=sys.stderr)
        if new != text:
            missing += 1
            if args.check:
                print(f"{f.name}: needs `{STEP_NAME}` for {' '.join(paths)}")
            else:
                f.write_text(new)
                print(f"{f.name}: pull {' '.join(paths)}")
    if args.check and missing:
        print(f"\n{missing} workflow(s) read store data without pulling it; run "
              f"python3 tools/artifacts/wire_workflows.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
