#!/usr/bin/env python3
"""Build the committed implementation; never execute a scientific workload."""
import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import subprocess


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--root", default="/opt/study")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-f0-9]{40}", args.source_revision):
        raise SystemExit("A full immutable source revision is required")
    root = Path(args.root).resolve()
    build = root / "implementation/build.py"
    orchestrator = root / "execution/run_experiment.py"
    if not build.is_file() or not orchestrator.is_file():
        raise SystemExit("Committed build.py and production orchestrator are required")
    if (root / "cohort/public").exists() or (root / "cohort/private").exists():
        raise SystemExit("The code-only image must not contain confirmation inputs or private labels")
    binary = Path("/usr/local/bin/endpoint_reuse")
    subprocess.run(["python3", str(build), "--output", str(binary)], cwd=root, check=True)
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise SystemExit("Production build did not produce the declared executable")
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "build-info.json":
            files[path.relative_to(root).as_posix()] = digest(path)
    info = {
        "schema": "classical.ecdlp.endpoint-reuse.image-build/v1",
        "source_revision": args.source_revision,
        "binary": str(binary),
        "binary_sha256": digest(binary),
        "confirmation_inputs_baked": False,
        "architecture": platform.machine(),
        "orchestrator": "execution/run_experiment.py",
        "orchestrator_sha256": digest(orchestrator),
        "source_and_public_input_sha256": files,
        "compiler": subprocess.check_output(["g++", "--version"], text=True).splitlines()[0],
        "python": subprocess.check_output(["python3", "--version"], text=True).strip(),
        "package_versions": subprocess.check_output(["dpkg-query", "-W", "gcc", "g++", "libc6", "python3", "python3-boto3"], text=True),
        "scientific_workload_executed": False,
    }
    (root / "build-info.json").write_text(json.dumps(info, indent=2) + "\n")


if __name__ == "__main__":
    main()
