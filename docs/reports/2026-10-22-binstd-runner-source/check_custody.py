"""Bind archived BINSTD Stage-1 source digests to recorded snapshot commits."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

BASE = "13eb217678653267553dcbfa9601f2564f63706b"
PANELS = (
    ("ell89", "8efed7dea288e827a4889aec8b768180b6b55e02", "RUN-BINSTD-43abd4"),
    ("ell89r1", "c39a3d5e4cc750a837d6339d2ff28f3209c67619", "RUN-BINSTD-a2a24c"),
)
SOURCE_FILES = ("run.py", "gf2.py", "check.py")
PREFIX = "experiments/EXP-BINSTD-8bdf86/implementation/"


def committed_bytes(repo: Path, commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=repo)


def main(repo: Path) -> dict:
    original = committed_bytes(repo, BASE, PREFIX + "run.py")
    assert hashlib.sha256(original).hexdigest() == "6d0e90f863c46eca1615bda68098a6beb7c9cc752581ee8fe4ec28d32b4eb0be"
    assert b'"--artifact-tag"' not in original and b'"--ells"' not in original
    panels = []
    for tag, commit, run_id in PANELS:
        environment = json.loads(
            (repo / "experiments/EXP-BINSTD-8bdf86/runs" / run_id / "environment.json").read_text()
        )
        hashes = {}
        for name in SOURCE_FILES:
            rel = PREFIX + name
            digest = hashlib.sha256(committed_bytes(repo, commit, rel)).hexdigest()
            assert digest == environment["source_sha256"][rel]
            hashes[name] = digest
        source = committed_bytes(repo, commit, PREFIX + "run.py")
        assert b'"--artifact-tag"' in source and b'"--ells"' in source
        if tag == "ell89r1":
            assert b'"--seed"' in source
            assert hashlib.sha256((repo / PREFIX / "run.py").read_bytes()).hexdigest() == hashes["run.py"]
        panels.append({"panel": tag, "snapshot_commit": commit, "stage1_run": run_id, "source_sha256": hashes})
    return {
        "schema": "binstd-source-custody-v1",
        "main_base_commit": BASE,
        "main_base_runner_sha256": hashlib.sha256(original).hexdigest(),
        "main_base_missing_amendment_cli": True,
        "snapshot_panels": panels,
        "restored_runner_equals_ell89r1_snapshot": True,
    }


if __name__ == "__main__":
    print(json.dumps(main(Path(sys.argv[1]).resolve()), indent=2, sort_keys=True))
