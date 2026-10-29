#!/usr/bin/env python3
"""Validate the frozen inputs and raw full-Lake target-verification result."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXECUTION_HEAD = "98fca453a13b0e4e1ae866a96d14c2760cfb2aeb"
TARGET = "CryptoResearch.Binstd.EncodedDivisors.archived_no_small_monic_divisors"
RAW = (
    "binstd-lake-root-complete-20261027.log",
    "binstd-lake-root-complete-20261027.exit",
    "binstd-formal-verify-20261027.json",
    "binstd-formal-verify-20261027.log",
    "binstd-formal-verify-20261027.exit",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check() -> dict:
    named_path = ROOT / "research/binstd_end_to_end_20261026/lake-named-20261027/lake-named-validation.json"
    prior_path = ROOT / "research/binstd_end_to_end_20261026/lake-workspace-20261027/workspace-build-receipt.json"
    root_path = ROOT / "research/binstd_end_to_end_20261026/lake-workspace-20261027/generated-root.lean"
    named = json.loads(named_path.read_text())
    prior = json.loads(prior_path.read_text())
    raw_receipt = json.loads((HERE / "binstd-formal-verify-20261027.json").read_text())
    result = raw_receipt["verification"]
    provenance = raw_receipt["provenance"]

    assert (HERE / "binstd-lake-root-complete-20261027.exit").read_text().strip() == "0"
    assert (HERE / "binstd-formal-verify-20261027.exit").read_text().strip() == "0"
    assert "Build completed successfully (8980 jobs)." in (
        HERE / "binstd-lake-root-complete-20261027.log").read_text()
    assert "machine_verified" in (HERE / "binstd-formal-verify-20261027.log").read_text()
    assert raw_receipt["schema"] == "crypto.autoresearch.formal_verification.v1"
    assert result["status"] == "machine_verified"
    assert result["build_passed"] is True and result["axiom_audit_passed"] is True
    assert result["forbidden_constructs"] == [] and result["blocking_reason"] is None
    assert result["theorem_name"] == TARGET
    assert raw_receipt["infrastructure_failure"] is None
    assert raw_receipt["semantic_review"] == {"required": True, "status": "pending"}
    assert "Build completed successfully (8980 jobs)." in raw_receipt["build_log"]
    assert "Build completed successfully (2 jobs)." in raw_receipt["build_log"]
    assert "axiom audit: 707 theorem(s), all standard axioms only" in raw_receipt["audit_log"]
    assert f"target axiom audit passed: {TARGET}" in raw_receipt["audit_log"]
    assert provenance["source_commit"] == EXECUTION_HEAD
    assert "version 4.35.0-rc1" in provenance["lean_version"]

    for receipt_key, source_path in (
        ("theorem_sha256", "formal/CryptoResearch/Binstd/EncodedDivisors.lean"),
        ("task_spec_sha256", "formal/targets/binstd-encoded-divisors.yaml"),
        ("lean_toolchain_sha256", "formal/lean-toolchain"),
        ("lake_manifest_sha256", "formal/lake-manifest.json"),
    ):
        value = sha((ROOT / source_path).read_bytes())
        assert value == provenance[receipt_key] == named["input_sha256"][source_path]
    assert provenance["workspace_inputs"]["CryptoResearch.lean"] == sha(root_path.read_bytes())
    assert prior["artifact_sha256"]["generated-root.lean"] == sha(root_path.read_bytes())
    assert named["frozen_inputs_unchanged_since_producer"] is True
    for relative, expected in provenance["workspace_inputs"].items():
        assert sha((ROOT / "formal" / relative).read_bytes()) == expected, relative
    for relative, expected in provenance["verifier_inputs"].items():
        assert sha((ROOT / relative).read_bytes()) == expected, relative

    return {
        "schema": "binstd.lake_full_target_validation.v1",
        "producer_revision": named["producer_revision"],
        "execution_head": EXECUTION_HEAD,
        "target": TARGET,
        "toolchain": named["toolchain"],
        "named_validation_sha256": sha(named_path.read_bytes()),
        "prior_bounded_attempts_sha256": sha(prior_path.read_bytes()),
        "source_spec_toolchain_manifest_unchanged": True,
        "workspace_input_count": len(provenance["workspace_inputs"]),
        "verifier_input_count": len(provenance["verifier_inputs"]),
        "root_lake_jobs": 8980,
        "named_lake_jobs": 2,
        "project_axiom_audit_theorems": 707,
        "target_axiom_audit": "passed",
        "formal_verifier_status": "machine_verified",
        "independent_semantic_review": "separate sealed J1/J2 finite-claim packet; not ingested by verifier",
        "polynomial_and_runner_bridge": "not_proved_by_this_target",
        "raw_artifact_sha256": {name: sha((HERE / name).read_bytes()) for name in RAW},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(check(), indent=2) + "\n"
    output = HERE / "full-gate-validation.json"
    if args.check:
        assert output.read_text() == content
        print("full BINSTD target receipt matches 707-theorem audit and frozen input hashes")
    else:
        assert not output.exists(), "receipt exists; use --check"
        output.write_text(content)
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
