#!/usr/bin/env python3
"""Recheck the hosted LastFall target receipt against its exact PR head."""

import hashlib
import json
import subprocess
from pathlib import Path

HEAD = "5c405f05539649cffb7f796ac586db65cdde1661"
RUN = 41191503149
TARGET = "CryptoResearch.FallDegree.lastFallDegree_eq_max_degreeFall"
HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "lastfall-hosted-receipt.json"


def git_sha256(path: str) -> str:
    data = subprocess.check_output(["git", "show", f"{HEAD}:{path}"])
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    run = json.loads(subprocess.check_output([
        "gh", "run", "view", str(RUN), "-R",
        "isogeny-labs/crypto-autoresearcher", "--json",
        "headSha,event,status,conclusion",
    ]))
    assert run == {
        "headSha": HEAD, "event": "pull_request", "status": "completed",
        "conclusion": "success",
    }, run
    d = json.loads(RECEIPT.read_text())
    v = d["verification"]
    p = d["provenance"]
    source_hash = git_sha256("formal/CryptoResearch/FallDegree/LastFall.lean")
    target_hash = git_sha256("formal/targets/lastfall-is-max-degree-fall.yaml")
    assert v["theorem_name"] == TARGET
    assert d["task"]["theorem_name"] == TARGET
    assert v["status"] == "machine_verified" and v["build_passed"] is True
    assert v["axiom_audit_passed"] is True and v["forbidden_constructs"] == []
    assert d["infrastructure_failure"] is None
    assert p["workspace_inputs"]["CryptoResearch/FallDegree/LastFall.lean"] == source_hash
    assert p["theorem_sha256"] == source_hash
    assert p["task_spec_sha256"] == target_hash
    assert f"target axiom audit passed: {TARGET}" in d["audit_log"]
    assert f"'{TARGET}' depends on axioms: [propext, Classical.choice, Quot.sound]" in d["audit_log"]
    result = {
        "schema": "lastfall.hosted_machine_readback/v1",
        "run": RUN,
        "run_head": HEAD,
        "run_status": run,
        "artifact_id": 13039453747,
        "artifact_name": "formal-verification-receipts",
        "receipt_sha256": hashlib.sha256(RECEIPT.read_bytes()).hexdigest(),
        "target": TARGET,
        "target_status": v["status"],
        "build_passed": v["build_passed"],
        "axiom_audit_passed": v["axiom_audit_passed"],
        "source_sha256": source_hash,
        "target_spec_sha256": target_hash,
        "workspace_input_count": len(p["workspace_inputs"]),
        "verifier_input_count": len(p["verifier_inputs"]),
        "semantic_review_status_in_receipt": d["semantic_review"],
        "note": "Hosted tool receipt and matching source bytes; independent claim fidelity is reviewed separately.",
    }
    (HERE / "machine-readback.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print("PASS: exact-head hosted target, source bytes and named axiom audit")


if __name__ == "__main__":
    main()
