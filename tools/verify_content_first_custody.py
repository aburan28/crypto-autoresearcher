#!/usr/bin/env python3
"""Verify the additive GFPN R2-r5 custody receipt against immutable Git blobs.

The receipt commit owns only the receipt. The five producer commits own the
run files and report; this verifier checks both bindings without rewriting them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PREFIX = "experiments/EXP-GFPN-05ff43"
RECEIPT = "coordination/goals/GOAL-GFPN-380702/archives/TASK-20261010-0fda2f/content-first-receipt.json"
SOURCES = (
    ("G1", f"{PREFIX}/runs/RUN-GFPN-4d1ac0", "7d7ca64dfb6eadccc234bdbf3e3aeff0435d5898", 337),
    ("G2", f"{PREFIX}/runs/RUN-GFPN-d98707", "fbd12d5b9284dd849ed1806b3d4d811809e089e0", 319),
    ("G3", f"{PREFIX}/runs/RUN-GFPN-347fde", "61004685f4750553a59bc4ee7a776cb5e69754f2", 13),
    ("G4", f"{PREFIX}/runs/RUN-GFPN-0037fb", "fdf9aa1c942050d77ead194dbe3878cde054d17f", 101),
    ("report", f"{PREFIX}/execution-report-v2-r5.yaml", "bc3abe8e463b2b23c9a20725ad955b29f7c2b3ac", 1),
)
REQUIRED_CHECKS = (
    "phase_a_hashes", "earlier_run_hashes", "reserved_id_accounting",
    "r5_checker_outputs", "reg1_comparator", "solver_events",
    "forbidden_id_sweep", "gate_and_rb4", "ssf_counts", "callgrind_counts",
    "g3_infrastructure", "g4_sequencing_deviation",
)


def git(*args: str, binary: bool = False) -> str | bytes:
    output = subprocess.check_output(["git", *args], cwd=REPO)
    return output if binary else output.decode().strip()


def tree_paths(rev: str, scope: str) -> dict[str, str]:
    out = git("ls-tree", "-r", rev, "--", scope)
    result = {}
    for line in out.splitlines():
        left, path = line.split("\t", 1)
        mode, kind, blob = left.split(" ")
        assert mode == "100644" and kind == "blob", (rev, path, mode, kind)
        result[path] = blob
    return result


def changed_paths(rev: str) -> list[str]:
    return git("diff-tree", "--no-commit-id", "--name-only", "-r", rev).splitlines()


def verify(receipt_path: Path, head: str) -> dict:
    rel_receipt = receipt_path.resolve().relative_to(REPO).as_posix()
    assert rel_receipt == RECEIPT
    data = json.loads(receipt_path.read_text())
    item = data["custody_receipt"]
    assert item["schema"] == "gfpn_r5_content_first_custody_v1"
    assert item["task_id"] == "TASK-20261010-0fda2f"
    assert item["correction_id"] == "CORR-20261010-db44b4"
    assert item["decision_id"] == "DEC-20261010-fb6792"
    assert item["original_phase_b_state"] == "incomplete"
    assert item["scientific_claim_change"] is False
    assert item["r2b_or_review_dispatched"] is False
    assert item["verifier_sha256"] == hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

    head_sha = git("rev-parse", head)
    assert head_sha == git("rev-parse", "HEAD")
    assert git("rev-parse", f"{head_sha}^") == item["parent_sha"]
    base = item["base_commit_checked"]
    assert len(base) == 40 and git("rev-parse", base) == base
    assert git("merge-base", "--is-ancestor", base, head_sha) == ""
    assert isinstance(item["merge_outcome"], str) and item["merge_outcome"].strip()
    assert changed_paths(head_sha) == [RECEIPT]
    assert git("show", f"{head_sha}:{RECEIPT}", binary=True) == receipt_path.read_bytes()
    message = git("show", "-s", "--format=%B", head_sha)
    for required in (item["task_id"], item["correction_id"], item["decision_id"],
                     "TASK-20260925-480d02", *(f"RUN-GFPN-{suffix}" for suffix in
                       ("4d1ac0", "d98707", "347fde", "0037fb"))):
        assert required in message, required

    sources = item["sources"]
    paths = item["paths"]
    assert isinstance(paths, dict) and len(paths) == 771
    found = set()
    counts = {}
    for label, scope, commit, expected_count in SOURCES:
        source = sources[label]
        assert source == {"scope": scope, "commit": commit, "path_count": expected_count}
        assert git("merge-base", "--is-ancestor", commit, head_sha) == ""
        assert git("merge-base", "--is-ancestor", commit, base) == ""
        changed = changed_paths(commit)
        added = git("diff-tree", "--no-commit-id", "--name-only", "--diff-filter=A", "-r", commit).splitlines()
        assert sorted(added) == sorted(changed)
        assert len(changed) == expected_count
        assert all(path == scope or path.startswith(scope + "/") for path in changed)
        old_tree = tree_paths(commit, scope)
        head_tree = tree_paths(head_sha, scope)
        assert set(changed) == set(old_tree) == set(head_tree)
        for path in changed:
            assert path not in found
            found.add(path)
            assert old_tree[path] == head_tree[path]
            content = (REPO / path).read_bytes()
            assert git("show", f"{commit}:{path}", binary=True) == content
            assert paths[path] == {
                "sha256": hashlib.sha256(content).hexdigest(),
                "size_bytes": len(content),
                "source_commit": commit,
                "blob_id": old_tree[path],
            }
        counts[label] = len(changed)
    assert set(paths) == found
    assert not git("status", "--porcelain", "--untracked-files=all", "--",
                   *(scope for _, scope, _, _ in SOURCES))

    checks = item["checks"]
    for key in REQUIRED_CHECKS:
        assert key in checks and checks[key] not in (None, "", [], {}), key
    assert checks["g3_infrastructure"]["classification"] == "infrastructure_error"
    assert checks["g4_sequencing_deviation"]["occurred"] is True
    assert checks["g4_sequencing_deviation"]["admissible_post_gate"] is False
    assert item["inventory_count"] == 771
    assert item["custody_commit_role"] == "receipt_only"
    return {"valid": True, "head": head_sha, "receipt": RECEIPT,
            "source_counts": counts, "inventory_count": len(found),
            "original_phase_b_state": "incomplete"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = verify(Path(args.receipt), args.head)
    except (AssertionError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        result = {"valid": False, "reason": f"{type(exc).__name__}: {exc}"}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS" if result["valid"] else "FAIL", result)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
