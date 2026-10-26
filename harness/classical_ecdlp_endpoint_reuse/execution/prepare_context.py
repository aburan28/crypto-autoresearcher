#!/usr/bin/env python3
"""Materialize an allowlisted image context from a committed git tree."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess


ALLOWED = ("implementation/", "execution/", "verification/", "cohort/", "protocol/")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", required=True)
    p.add_argument("--package-path", required=True)
    p.add_argument("--source-revision", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    if not re.fullmatch(r"[a-f0-9]{40}", a.source_revision):
        p.error("source revision must be a full SHA")
    prefix = PurePosixPath(a.package_path)
    if prefix.is_absolute() or ".." in prefix.parts:
        p.error("package path must be a repository-relative directory")
    out = Path(a.output)
    if out.exists():
        p.error("fresh output directory required")
    names = subprocess.check_output(
        ["git", "ls-tree", "-r", "-z", "--name-only", a.source_revision, "--", str(prefix)],
        cwd=a.repo,
    ).split(b"\0")
    chosen = []
    for raw in names:
        if not raw:
            continue
        full = raw.decode("utf-8")
        rel = PurePosixPath(full).relative_to(prefix).as_posix()
        if any(x in PurePosixPath(rel).parts for x in ("private", "public", "__pycache__", "development", ".pytest_cache", "build", "target")):
            continue
        if not rel.startswith(ALLOWED) or rel.startswith("execution/evidence/"):
            continue
        if rel.startswith("protocol/") and not rel.endswith(".py"):
            continue
        chosen.append((full, rel))
    required = {"implementation/build.py", "execution/run_experiment.py", "execution/worker.py", "execution/image_build.py", "execution/Dockerfile", "cohort/public_inputs.py", "protocol/seed_rules.py"}
    if not required.issubset({x[1] for x in chosen}):
        p.error("the committed package lacks its concrete build/run plan or worker")
    out.mkdir(parents=True)
    manifest = []
    for full, rel in chosen:
        data = subprocess.check_output(["git", "show", f"{a.source_revision}:{full}"], cwd=a.repo)
        dest = out / "payload" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        manifest.append({"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    (out / "Dockerfile").write_bytes((out / "payload/execution/Dockerfile").read_bytes())
    (out / "context-manifest.json").write_text(json.dumps({"source_revision": a.source_revision, "files": manifest}, indent=2) + "\n")
    print(out)


if __name__ == "__main__":
    main()
