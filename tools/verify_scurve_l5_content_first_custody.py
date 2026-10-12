#!/usr/bin/env python3
"""Verify SCURVE L5's existing producer files and later custody receipt.

This checks Git and byte custody. It makes no finding about the certificate,
its controls, an implementation weakness, or a scientific claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "6a707e069f0a10b6e90b29c1c31b5243a207b5c6"
OLD = "TASK-20261001-762c5f"
PRODUCER = "TASK-20261011-e1f957"
ARCHIVE = "TASK-20261011-071e47"
BASE_DIR = f"coordination/goals/GOAL-SCURVE-48e06c/batches/BATCH-aa389e"
OLD_DIR = f"{BASE_DIR}/tasks/{OLD}"
REPORT = f"{BASE_DIR}/tasks/{PRODUCER}/verification-report.json"
RECEIPT = f"{BASE_DIR}/archives/{ARCHIVE}/snapshot-receipt.json"
HANDOFF = f"ledger/handoffs/{PRODUCER}.yaml"
SOURCE_BINDING = f"{OLD_DIR}/source-binding.yaml"
HTML_NAMES = {
    "safecurves-base.html", "safecurves-equation.html",
    "safecurves-field.html", "safecurves-transfer.html",
}
DECLARED_NAMES = {
    "source-binding.yaml", "transfer-lane-L5.yaml", "l5_certificate.py",
    "l5_certificate.stdout.txt", "task-report.yaml",
}


def git(*args: str, binary: bool = False) -> str | bytes:
    value = subprocess.check_output(["git", *args], cwd=ROOT)
    return value if binary else value.decode().strip()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def assert_ancestor(ancestor: str, descendant: str) -> None:
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT, check=True, capture_output=True,
    )


def assert_original_unreleased() -> None:
    output = subprocess.check_output(
        [sys.executable, str(ROOT / "tools/goal_lanes.py"), "claims",
         f"{BASE_DIR}/dispatch_queue.json", "--json"], cwd=ROOT,
    )
    entry = json.loads(output).get(OLD)
    assert not entry or not (
        entry.get("status") == "released" and entry.get("outcome") == "completed"
    ), entry


def changed(commit: str) -> list[tuple[str, str]]:
    return [tuple(line.split("\t", 1)) for line in
            git("diff-tree", "--no-commit-id", "--name-status", "-r", commit).splitlines()]


def old_source_inventory(head: str) -> tuple[dict[str, dict], str]:
    assert_original_unreleased()
    assert_ancestor(SOURCE, head)
    assert_ancestor(SOURCE, git("rev-parse", "origin/main"))
    source_parent = git("rev-parse", f"{SOURCE}^")
    changes = changed(SOURCE)
    expected = yaml.safe_load((ROOT / HANDOFF).read_text())["handoff"]["expected_inventory"]
    assert len(changes) == len(expected) == 10, (len(changes), len(expected))
    assert all(status == "A" for status, _ in changes), changes
    assert {path for _, path in changes} == set(expected)
    assert all(path.startswith(OLD_DIR + "/") for _, path in changes)
    names = {Path(path).name for _, path in changes}
    assert names == DECLARED_NAMES | HTML_NAMES | {"task.yaml"}, names
    binding = yaml.safe_load((ROOT / SOURCE_BINDING).read_text())
    html = {item["file"]: item for item in binding["route_1_attempts"]}
    assert set(html) == HTML_NAMES
    inventory = {}
    for _, path in changes:
        source_bytes = git("show", f"{SOURCE}:{path}", binary=True)
        head_bytes = git("show", f"{head}:{path}", binary=True)
        work_bytes = (ROOT / path).read_bytes()
        blob = git("rev-parse", f"{SOURCE}:{path}")
        assert source_bytes == head_bytes == work_bytes, path
        assert sha(source_bytes) == expected[path], path
        if Path(path).name in HTML_NAMES:
            row = html[Path(path).name]
            assert row["sha256"] == sha(source_bytes), path
            assert row["bytes"] == len(source_bytes), path
        inventory[path] = {
            "blob_id": blob,
            "sha256": sha(source_bytes),
            "size_bytes": len(source_bytes),
            "source_head_worktree_equal": True,
            "classification": (
                "declared_artifact" if Path(path).name in DECLARED_NAMES else
                "fetched_html" if Path(path).name in HTML_NAMES else
                "undeclared_task_yaml"
            ),
        }
    return inventory, source_parent


def verify_report(report: dict, head: str) -> dict:
    inventory, parent = old_source_inventory(head)
    assert report["schema"] == "scurve_l5_existing_output_verification_v1"
    assert report["task_id"] == PRODUCER
    assert report["goal_id"] == "GOAL-SCURVE-48e06c"
    assert report["batch_id"] == "BATCH-aa389e"
    assert report["source_task_id"] == OLD
    assert report["source_commit"] == SOURCE
    assert report["source_parent"] == parent
    assert report["paths"] == inventory
    binding = yaml.safe_load((ROOT / SOURCE_BINDING).read_text())
    expected_html = {
        item["file"]: {
            "source_binding_sha256": item["sha256"],
            "actual_sha256": inventory[f"{OLD_DIR}/{item['file']}"]["sha256"],
            "matches": True,
        }
        for item in binding["route_1_attempts"]
    }
    assert report["html_checks"] == expected_html
    claims = report["old_queue_claims"]
    assert claims["exit_code"] == 0
    assert claims["command"][-2:] == [
        f"{BASE_DIR}/dispatch_queue.json", "--json"
    ]
    assert OLD not in json.loads(claims["stdout"])
    assert report["checked_head"] == git("rev-parse", report["checked_head"])
    assert_ancestor(report["checked_head"], head)
    assert report["producer_release_state"] == "absent"
    assert report["old_snapshot_state"] == "incomplete"
    assert report["undeclared_extra"] == f"{OLD_DIR}/task.yaml"
    assert report["scientific_claim_change"] is False
    assert report["valid"] is True and report["failures"] == []
    return {"source_paths": len(inventory), "source_commit": SOURCE}


def verify_receipt(path: Path, head: str) -> dict:
    assert path.resolve() == (ROOT / RECEIPT).resolve()
    assert changed(head) == [("A", RECEIPT)]
    assert git("show", f"{head}:{RECEIPT}", binary=True) == path.read_bytes()
    receipt = json.loads(path.read_text())
    assert receipt["schema"] == "scurve_l5_content_first_snapshot_v1"
    assert receipt["task_id"] == ARCHIVE
    assert receipt["producer_task_id"] == PRODUCER
    assert receipt["source_commit"] == SOURCE
    assert receipt["report_path"] == REPORT
    assert receipt["old_producer_release_state"] == "absent"
    assert receipt["old_snapshot_state"] == "incomplete"
    assert receipt["scientific_claim_change"] is False
    assert receipt["independent_validation_dispatched"] is False
    assert receipt["verifier_sha256"] == sha(Path(__file__).read_bytes())
    assert receipt["receipt_parent"] == git("rev-parse", f"{head}^")
    base = receipt["base_commit_checked"]
    assert_ancestor(base, head)
    landing = receipt["producer_landing_commit"]
    assert_ancestor(landing, head)
    assert receipt["producer_landing_parent"] == git("rev-parse", f"{landing}^")
    assert changed(landing) == [("A", REPORT)]
    report_bytes = git("show", f"{landing}:{REPORT}", binary=True)
    assert report_bytes == git("show", f"{head}:{REPORT}", binary=True)
    assert sha(report_bytes) == receipt["report_sha256"]
    assert receipt["source_paths"] == old_source_inventory(head)[0]
    release_path = ROOT / receipt["producer_release_path"]
    release_bytes = release_path.read_bytes()
    assert sha(release_bytes) == receipt["producer_release_sha256"]
    release = json.loads(release_bytes)
    assert release["task_id"] == PRODUCER and release["outcome"] == "completed"
    assert release["artifact_sha256"] == {REPORT: sha(report_bytes)}
    assert receipt["source_parent"] == git("rev-parse", f"{SOURCE}^")
    result = verify_report(json.loads(report_bytes), head)
    return {"valid": True, "receipt_commit": head, "report_sha256": sha(report_bytes), **result}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        head = git("rev-parse", args.head)
        result = (verify_receipt(args.receipt, head) if args.receipt else
                  {"valid": True, "source_paths": len(old_source_inventory(head)[0]),
                   "source_commit": SOURCE, "head": head})
    except (AssertionError, KeyError, OSError, ValueError, subprocess.CalledProcessError) as exc:
        result = {"valid": False, "reason": f"{type(exc).__name__}: {exc}"}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS" if result["valid"] else "FAIL", result)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
