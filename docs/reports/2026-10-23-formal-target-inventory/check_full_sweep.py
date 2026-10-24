#!/usr/bin/env python3
"""Check the 84 archived verifier receipts against their exact source commit.

Run from any directory with ``--repo`` pointing to a full checkout at the
recorded sweep commit.  This checks machine evidence and source identity; it
does not judge whether a theorem faithfully models its research claim.
"""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import yaml


SWEEP_HEAD = "1c572eb4be33e1cb7fbcd5d50d3982a6eccc6696"
MAIN_HEAD = "bed002e64873c01a10082e1ad464bf0f9159fdce"
EVIDENCE = Path(__file__).resolve().parent / "evidence/full-target-sweep"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def tree_blobs(repo: Path, commit: str, paths: list[str]) -> dict[str, str]:
    raw = subprocess.check_output(
        ["git", "ls-tree", "-rz", commit, "--", *paths], cwd=repo
    )
    blobs = {}
    for row in raw.split(b"\0"):
        if row:
            mode_type_oid, path = row.split(b"\t", 1)
            blobs[path.decode()] = mode_type_oid.split()[2].decode()
    return blobs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    errors = []
    head = git(repo, "rev-parse", "HEAD")
    if head != SWEEP_HEAD:
        errors.append(f"checkout HEAD {head} != {SWEEP_HEAD}")

    specs = sorted((repo / "formal/targets").glob("*.yaml"))
    saved = json.loads((EVIDENCE / "receipt-audit.json").read_text())
    equivalence = json.loads((EVIDENCE / "main-source-equivalence.json").read_text())
    receipts = EVIDENCE / "receipts"
    names = {p.stem for p in specs}
    receipt_names = {p.stem for p in receipts.glob("*.json")}
    if names != receipt_names or len(names) != 84:
        errors.append("target and receipt names do not form the recorded 84-target set")

    verified = []
    hashes = {}
    sources = set()
    for spec_path in specs:
        spec = yaml.safe_load(spec_path.read_text())
        sources.add(spec["source"])
        receipt_path = receipts / f"{spec_path.stem}.json"
        if not receipt_path.is_file():
            continue
        receipt = json.loads(receipt_path.read_text())
        task = receipt.get("task") or {}
        result = receipt.get("verification") or {}
        provenance = receipt.get("provenance") or {}
        checks = {
            "schema": receipt.get("schema") == "crypto.autoresearch.formal_verification.v1",
            "task": task.get("task_id") == spec["task_id"] == result.get("task_id"),
            "claim": task.get("claim_id") == spec["claim_id"],
            "theorem": task.get("theorem_name") == spec["theorem_name"] == result.get("theorem_name"),
            "file": task.get("theorem_file") == spec["theorem_file"] == result.get("theorem_file"),
            "workspace": task.get("workspace") == spec["workspace"],
            "source_commit": provenance.get("source_commit") == SWEEP_HEAD,
            "spec_hash": provenance.get("task_spec_sha256") == sha(spec_path),
            "theorem_hash": provenance.get("theorem_sha256") == sha(repo / spec["workspace"] / spec["theorem_file"]),
            "toolchain_hash": provenance.get("lean_toolchain_sha256") == sha(repo / spec["workspace"] / "lean-toolchain"),
            "manifest_hash": provenance.get("lake_manifest_sha256") == sha(repo / spec["workspace"] / "lake-manifest.json"),
            "machine_verified": result.get("status") == "machine_verified",
            "build": result.get("build_passed") is True,
            "axioms": result.get("axiom_audit_passed") is True,
            "forbidden": result.get("forbidden_constructs") == [],
            "blocking_reason": result.get("blocking_reason") is None,
            "semantic_scope": receipt.get("semantic_review") == {"required": True, "status": "pending"},
        }
        failed = [key for key, passed in checks.items() if not passed]
        if failed:
            errors.append(f"{spec_path.stem}: {failed}")
        else:
            verified.append(spec_path.stem)
        hashes[spec_path.stem] = sha(receipt_path)

    formal_tree = git(repo, "rev-parse", "HEAD:formal")
    if (
        saved.get("checkout_head") != SWEEP_HEAD
        or saved.get("formal_tree") != formal_tree
        or saved.get("expected_targets") != 84
        or saved.get("verified") != 84
        or saved.get("pending") != 0
        or saved.get("errors") != []
        or saved.get("verified_targets") != verified
        or saved.get("receipt_sha256") != hashes
    ):
        errors.append("saved receipt audit differs from independently recomputed values")

    source_paths = sorted(sources)
    source_oids = {row["path"]: row["git_blob_oid"] for row in equivalence["sources"]}
    at_sweep = tree_blobs(repo, SWEEP_HEAD, source_paths)
    at_main = tree_blobs(repo, MAIN_HEAD, source_paths)
    main_formal = git(repo, "rev-parse", f"{MAIN_HEAD}:formal")
    if (
        equivalence.get("result") != "pass"
        or equivalence.get("sweep_checkout") != SWEEP_HEAD
        or equivalence.get("main_commit") != MAIN_HEAD
        or equivalence.get("target_count") != 84
        or equivalence.get("source_count") != 29
        or equivalence.get("mismatches") != []
        or equivalence.get("formal_tree_checkout") != formal_tree
        or equivalence.get("formal_tree_main") != main_formal
        or formal_tree != main_formal
        or set(source_oids) != set(source_paths)
        or at_sweep != source_oids
        or at_main != source_oids
    ):
        errors.append("source equivalence to the named main commit failed")

    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    print(
        f"PASS: {len(verified)} exact machine-verified target receipts; "
        f"{len(source_paths)} source blobs and formal tree match named main. "
        "Independent semantic review remains pending."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
