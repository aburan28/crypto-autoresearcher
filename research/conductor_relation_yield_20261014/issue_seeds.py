"""Issue private 256-bit study seeds after a committed source freeze.

The private directory must be outside the repository. This command prints no
seed values. Its public commitment file must be archived before collection.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SOURCE_NAMES = (
    "plan.json", "collector.rs", "count_verify.cpp", "verify_collector.py",
    "prepare_input.py", "exact_interval.py", "execute_prepared.py", "certify_panel.py",
    "issue_seeds.py", "reveal_seeds.py",
)


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-commit", required=True)
    parser.add_argument("--specification", type=Path, required=True)
    parser.add_argument("--private-dir", type=Path, required=True)
    parser.add_argument("--public-commitment", type=Path, required=True)
    args = parser.parse_args()
    head = git("rev-parse", "HEAD")
    if args.freeze_commit != head:
        parser.error("freeze commit must be the current HEAD")
    specification_path = args.specification.resolve()
    if REPO not in specification_path.parents:
        parser.error("approved specification must be in this repository")
    specification = yaml.safe_load(specification_path.read_text())["experiment"]
    if (specification.get("status") != "approved" or specification.get("approved_by") != "coordinator"
            or not specification.get("frozen") or not specification.get("approval_decision_id")):
        parser.error("seed issuance requires a frozen Coordinator-approved specification")
    git("ls-files", "--error-unmatch", str(specification_path.relative_to(REPO)))
    if git("status", "--porcelain", "--", str(specification_path.relative_to(REPO))):
        parser.error("approved specification must be clean at the freeze commit")
    relative = [str((HERE / name).relative_to(REPO)) for name in SOURCE_NAMES]
    if git("status", "--porcelain", "--", *relative):
        parser.error("study source files must be clean at the freeze commit")
    for name in relative:
        git("ls-files", "--error-unmatch", name)
    private_dir = args.private_dir.resolve()
    public_path = args.public_commitment.resolve()
    if private_dir == REPO or REPO in private_dir.parents:
        parser.error("private seed directory must be outside this repository")
    if REPO not in public_path.parents:
        parser.error("public commitment must be inside this repository")
    if not private_dir.parent.is_dir() or not public_path.parent.is_dir():
        parser.error("both output parent directories must already exist")
    if public_path.exists() or private_dir.exists():
        parser.error("seed output already exists; issue one immutable attempt per directory")
    target_seed = os.urandom(32)
    k_seed = os.urandom(32)
    while target_seed == k_seed:
        k_seed = os.urandom(32)
    public = {
        "schema": "arity3-seed-commitment/v1",
        "freeze_commit": head,
        "experiment_id": specification["id"],
        "specification_path": str(specification_path.relative_to(REPO)),
        "specification_sha256": sha256(specification_path),
        "issued_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "target_seed_sha256": hashlib.sha256(target_seed).hexdigest(),
        "k_seed_sha256": hashlib.sha256(k_seed).hexdigest(),
        "source_sha256": {name: sha256(HERE / name) for name in SOURCE_NAMES},
        "next_gate": "commit public commitment and prepared target-vector digests before collection; reveal seeds only after collector outputs are sealed",
    }
    private_dir.mkdir(mode=0o700, parents=False)
    for filename, seed in (("target.seed", target_seed), ("k.seed", k_seed)):
        descriptor = os.open(private_dir / filename, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(descriptor, "w") as stream:
            stream.write(seed.hex() + "\n")
    with public_path.open("x", encoding="utf-8") as stream:
        json.dump(public, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"status": "issued", "public_commitment": str(public_path),
                      "private_directory": str(private_dir),
                      "target_seed_sha256": public["target_seed_sha256"],
                      "k_seed_sha256": public["k_seed_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
