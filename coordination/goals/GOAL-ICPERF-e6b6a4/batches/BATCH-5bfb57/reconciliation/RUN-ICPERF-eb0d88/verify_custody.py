#!/usr/bin/env python3
"""Replay the prepared RUN-ICPERF-eb0d88 byte inventory without a solver."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tarfile
from pathlib import Path


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], stderr=subprocess.DEVNULL)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify(manifest_path: Path) -> None:
    root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
    document = json.loads(manifest_path.read_text())
    require(document["schema"] == "crypto.autoresearch.icperf_failed_run_custody.v1", "schema")
    require(document["record_status"] == "prepared_unarchived", "status")
    require(document["scientific_effect"] == "none", "scientific boundary")
    commit = document["source_commit"]
    bundle = root / document["copy_bundle"]["path"]
    data = bundle.read_bytes()
    require(digest(data) == document["copy_bundle"]["sha256"], "bundle digest")
    require(len(data) == document["copy_bundle"]["size_bytes"], "bundle size")
    copies = document["copies"]
    require(len(copies) == 26, "copy count")
    expected = {item["copy_member"] for item in copies}
    require(len(expected) == len(copies), "duplicate manifest member")
    with tarfile.open(bundle, "r:gz") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        require(len(names) == len(set(names)), "duplicate tar member")
        require(all(member.isfile() for member in members), "nonfile tar member")
        require(set(names) == expected, "bundle member set")
        by_name = {member.name: member for member in members}
        for item in copies:
            source = item["source_path"]
            require(not Path(source).is_absolute() and ".." not in Path(source).parts, "unsafe source path")
            member = by_name[item["copy_member"]]
            copied = archive.extractfile(member).read()
            require(len(copied) == item["size_bytes"], f"copy size: {source}")
            require(digest(copied) == item["sha256"], f"copy digest: {source}")
            require(copied == (root / source).read_bytes(), f"working source: {source}")
            require(copied == git_blob(commit, source), f"Git source: {source}")
            blob = subprocess.check_output(["git", "rev-parse", f"{commit}:{source}"], text=True).strip()
            require(blob == item["source_git_blob"], f"Git blob ID: {source}")
    for item in document["historical_anchors"]:
        source = item["path"]
        current = (root / source).read_bytes()
        require(len(current) == item["size_bytes"] and digest(current) == item["sha256"], f"anchor: {source}")
        require(current == git_blob(commit, source), f"Git anchor: {source}")
    for source in document["required_absent"]:
        require(not (root / source).exists(), f"required output appeared: {source}")
        result = subprocess.run(["git", "cat-file", "-e", f"{commit}:{source}"], capture_output=True)
        require(result.returncode != 0, f"required output present in Git: {source}")
    run_root = root / "experiments/EXP-ICPERF-515ae3/runs/RUN-ICPERF-eb0d88"
    raw_receipt = json.loads((run_root / "diagnostic/receipt.json").read_text())
    raw_expected = {(item["path"], item["sha256"], item["bytes"]) for item in raw_receipt["raw_files"]}
    raw_recorded = {(item["path"], item["sha256"], item["size_bytes"]) for item in document["raw_diagnostic_members"]}
    require(raw_expected == raw_recorded and len(raw_recorded) == 15, "raw member receipt parity")
    with tarfile.open(run_root / "diagnostic/raw.tar.gz", "r:gz") as archive:
        raw_actual = {(member.name, digest(archive.extractfile(member).read()), member.size)
                      for member in archive.getmembers() if member.isfile()}
    require(raw_actual == raw_recorded, "raw tar member parity")
    supervisor = json.loads((run_root / "execution-receipt.json").read_text())
    checker = json.loads((run_root / "check.stdout.log").read_text())
    require(supervisor["status"] == document["historical_supervisor_status"] == "invalid_output", "supervisor status")
    require(checker["status"] == document["raw_checker_status"] == "integrity_pass", "checker status")
    print(f"custody replay passed: {len(copies)} exact copies, {len(raw_actual)} raw members, "
          f"{len(document['historical_anchors'])} anchors, {len(document['required_absent'])} absent outputs")


if __name__ == "__main__":
    try:
        verify(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("custody.json"))
    except (OSError, KeyError, ValueError, tarfile.TarError, subprocess.CalledProcessError) as error:
        print(f"custody replay failed: {error}", file=sys.stderr)
        raise SystemExit(1)
