#!/usr/bin/env python3
"""Add an artifact-store pull step to every workflow that names moved data.

After `artifacts.py push` moves files out of Git, a workflow that reads them
(a replay of `research/x/`, a check over `experiments/y/results/`) would find
pointers only. This finds, per workflow file, the repository paths it names
that hold moved files, and inserts after each `actions/checkout` step:

    - name: Pull store data this workflow reads (tools/artifacts)
      env: {AWS_ACCESS_KEY_ID: ..., AWS_SECRET_ACCESS_KEY: ..., AWS_REGION: ...}
      run: |
        if ! command -v aws ...; then (install the AWS CLI into $RUNNER_TEMP); fi
        python3 tools/artifacts/artifacts.py pull research/x experiments/y/results

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
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artifacts  # noqa: E402

STEP_NAME = "Pull store data this workflow reads (tools/artifacts)"
NO_PULL_ANNOTATION = "# artifact-store: no-pull"
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
    # Documentation comments do not make a job consume the referenced path.
    active_text = "\n".join(line for line in text.splitlines()
                            if not line.lstrip().startswith("#"))
    for m in PATH_RE.finditer(active_text):
        p = m.group(1).split("*", 1)[0].rstrip("/.")
        if p in moved or p in dirs:
            found.add(p)
    return sorted(p for p in found if not any(p.startswith(q + "/") for q in found))


def explicitly_pulled_and_verified(text: str, paths: list[str]) -> bool:
    """Accept a scoped pull only in each job that names the moved path.

    The automatic writer inserts a pull after every checkout in a workflow.
    Some workflows have a single consuming job and other jobs with deliberately
    narrow sparse checkouts. A pull in the consumer, followed by verification,
    is sufficient there; requiring it in unrelated jobs would break those
    checkouts. Do not let a pull in one job cover a different consuming job.
    """
    jobs = re.search(r"(?m)^jobs:\s*$", text)
    if jobs is None:
        return False
    tail = text[jobs.end():]
    starts = list(re.finditer(r"(?m)^  [A-Za-z_][A-Za-z0-9_-]*:\s*(?:#.*)?$", tail))
    if not starts:
        return False
    blocks = [tail[m.end():starts[i + 1].start() if i + 1 < len(starts) else len(tail)]
              for i, m in enumerate(starts)]
    seen: set[str] = set()
    for block in blocks:
        named = [path for path in paths if path in block]
        if not named:
            continue
        seen.update(named)
        commands: dict[str, list[list[str]]] = {"pull": [], "verify": []}
        for line in block.splitlines():
            match = re.match(r"\s*python3?\s+tools/artifacts/artifacts\.py\s+(pull|verify)\s+(.+)$", line)
            if match is None:
                continue
            try:
                commands[match.group(1)].append(shlex.split(match.group(2)))
            except ValueError:
                return False
        for path in named:
            if not all(any(path == arg or path.startswith(arg.rstrip("/") + "/")
                           for args in commands[verb] for arg in args
                           if arg and not arg.startswith("-"))
                       for verb in ("pull", "verify")):
                return False
    return seen == set(paths)


def metadata_only(text: str) -> bool:
    """Whether the workflow documents that it never reads stored file bytes."""
    return any(line.strip().startswith(NO_PULL_ANNOTATION) for line in text.splitlines())


def step_lines(indent: str, paths: list[str]) -> list[str]:
    i2 = indent + "  "
    return [
        f"{indent}- name: {STEP_NAME}",
        f"{i2}shell: bash",
        f"{i2}working-directory: ${{{{ github.workspace }}}}",
        f"{i2}env:",
        f"{i2}  AWS_ACCESS_KEY_ID: ${{{{ secrets.ARTIFACTS_AWS_ACCESS_KEY_ID }}}}",
        f"{i2}  AWS_SECRET_ACCESS_KEY: ${{{{ secrets.ARTIFACTS_AWS_SECRET_ACCESS_KEY }}}}",
        f"{i2}  AWS_REGION: ${{{{ vars.ARTIFACTS_AWS_REGION || 'us-west-2' }}}}",
        f"{i2}run: |",
        # A pinned, isolated CLI works on Linux, macOS and Windows without sudo.
        f"{i2}  if ! command -v aws >/dev/null; then",
        f'{i2}    python3 -m venv "$RUNNER_TEMP/artifacts-awscli"',
        f'{i2}    artifacts_cli_python="$RUNNER_TEMP/artifacts-awscli/bin/python"',
        f'{i2}    artifacts_cli_aws="$RUNNER_TEMP/artifacts-awscli/bin/aws"',
        f'{i2}    if [ -d "$RUNNER_TEMP/artifacts-awscli/Scripts" ]; then',
        f'{i2}      artifacts_cli_python="$RUNNER_TEMP/artifacts-awscli/Scripts/python.exe"',
        f'{i2}      artifacts_cli_aws="$RUNNER_TEMP/artifacts-awscli/Scripts/aws.exe"',
        f'{i2}    fi',
        f'{i2}    "$artifacts_cli_python" -m pip install --disable-pip-version-check awscli==1.46.2',
        f'{i2}    export ARTIFACTS_AWS="$artifacts_cli_aws"',
        f"{i2}  fi",
        f"{i2}  python3 tools/artifacts/artifacts.py pull --jobs 16 {' '.join(paths)}",
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
        # CI scope detection checks out only .github/scripts and never reads
        # moved data. A hydration step there cannot even access artifacts.py.
        if any(b.strip() == "sparse-checkout: .github/scripts" for b in block):
            out.extend(block)
            i = j
            continue
        block = add_sparse_pattern(block, indent)
        out.extend(block)
        k = next((k for k in range(j, len(lines)) if lines[k].strip()), len(lines))
        if k < len(lines) and STEP_NAME in lines[k]:
            # A step inserted earlier: replace it, so a changed template or
            # path list regenerates (and --check flags the stale copy).
            out.extend(lines[j:k])
            j = k + 1
            while j < len(lines) and (not lines[j].strip() or len(lines[j]) - len(lines[j].lstrip()) > len(indent)):
                j += 1
            while j > k + 1 and not lines[j - 1].strip():
                j -= 1
        step = step_lines(indent, paths)
        cond = next((re.sub(rf"^{indent}(?:- |  )", "", b) for b in block
                     if re.match(rf"^{indent}(?:- |  )if: ", b)), None)
        if cond:  # skipped with its checkout, so it never runs against an empty workspace
            step.insert(1, f"{indent}  {cond}")
        out.extend(step)
        i = j
    return "\n".join(out), notes


def add_sparse_pattern(block: list[str], indent: str) -> list[str]:
    """Make a sparse checkout also fetch tools/artifacts and .artifacts (the
    store config the pull step reads; without it the remote is empty)."""
    cone = not any("sparse-checkout-cone-mode: false" in x for x in block)
    want = [("tools/artifacts", "/tools/artifacts/", ("tools", "/tools/")),
            (".artifacts", "/.artifacts/", ())]
    for k, b in enumerate(block):
        scalar = re.match(rf"^({indent}    sparse-checkout: )(?!\|)(\S.*)$", b)
        if scalar and "${{" in scalar.group(2):
            # A conditional empty value means a full checkout. Appending literal
            # patterns would silently narrow it to the artifact bootstrap only.
            return block
        if scalar:  # one literal pattern on the key line: rewrite as a block list
            pad = indent + "      "
            block = block[:k] + [f"{scalar.group(1)}|", pad + scalar.group(2)] + block[k + 1:]
            b = block[k]
        if re.match(rf"^{indent}    sparse-checkout: \|", b):
            items = []
            n = k + 1
            while n < len(block) and len(block[n]) - len(block[n].lstrip()) > len(indent) + 4:
                items.append(block[n])
                n += 1
            if any(x.strip() == "/*" for x in items):
                return block
            pad = (items[0][: len(items[0]) - len(items[0].lstrip())]) if items else indent + "      "
            extra = [pad + (c if cone else nc) for c, nc, covers in want
                     if not any(c in x or x.strip() in covers for x in items)]
            return block[:n] + extra + block[n:]
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
        # Keep metadata-only checks usable on fork PRs without private S3
        # credentials. Content consumers still require a pull and verify.
        if metadata_only(text):
            continue
        paths = needed(text, moved, dirs)
        if not paths:
            continue
        if explicitly_pulled_and_verified(text, paths):
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
