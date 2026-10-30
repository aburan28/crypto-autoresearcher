#!/usr/bin/env python3
"""Bind the local Lean gate pass to the unchanged sealed independent review."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REVIEW = HERE.parent
FULL = ROOT / "research/binstd_end_to_end_20261026/lake-verified-20261027/full-gate-validation.json"
SEAL = REVIEW / "archive/receipt.json"
VERDICTS = REVIEW / "archive/claim-verdicts.json"
ASSETS = (
    "REPORT.md", "report.tex", "report.pdf", "diagram.py", "diagram.svg",
    "diagram.pdf", "visual-inspection.json",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    seal, old = json.loads(SEAL.read_text()), json.loads(VERDICTS.read_text())
    full = json.loads(FULL.read_text())
    assert seal["content_at_commit"] is True
    assert seal["producer_revision"] == old["producer_revision"] == full["producer_revision"]
    assert seal["reviewer_tasks"] == old["reviewer_tasks"]
    for rel, expected in seal["content_paths_sha256"].items():
        assert digest(ROOT / rel) == expected, rel
    claims = {entry["id"]: entry for entry in old["claims"]}
    assert claims["C1"]["review_outcome"] == "validated_scoped"
    assert claims["C2"]["review_outcome"] == "inconclusive"
    assert claims["C3"]["review_outcome"] == "validated_scoped"
    assert claims["C4"]["machine_status"] == "not_verified"
    assert claims["C5"]["review_outcome"] == "inconclusive"
    assert full["formal_verifier_status"] == "machine_verified"
    assert full["root_lake_jobs"] == 8980
    assert full["project_axiom_audit_theorems"] == 707
    assert full["target_axiom_audit"] == "passed"
    assert full["source_spec_toolchain_manifest_unchanged"] is True
    inspect = json.loads((HERE / "visual-inspection.json").read_text())
    assert inspect["pages"] == 1 and inspect["pdf_sha256"] == digest(HERE / "report.pdf")
    assert "8,980" in (HERE / "REPORT.md").read_text()
    assert "707" in (HERE / "REPORT.md").read_text()
    return {
        "schema": "binstd.lean_review_gate_addendum.v1",
        "producer_revision": seal["producer_revision"],
        "execution_head": full["execution_head"],
        "original_review_content_commit": seal["content_commit"],
        "sealed_review_receipt_sha256": digest(SEAL),
        "full_gate_validation_sha256": digest(FULL),
        "reviewer_tasks": seal["reviewer_tasks"],
        "original_sealed_paths_unchanged": True,
        "claim_updates": {
            "C1": "unchanged: independently validated finite encoded masks and counts",
            "C2": "full exact-target Lean gate passed for same reviewed theorem bytes; encoded scope only",
            "C3": "unchanged: direct-check receipt consistency validated",
            "C4": "local full workspace and exact target machine verified; hosted checks still blocked",
            "C5": "unchanged: polynomial, concrete runner and Frobenius bridge not proved by this target",
        },
        "formal_verifier_semantic_review_field": "pending; J1/J2 review is separate evidence",
        "official_scientific_status_changed": False,
        "hosted_required_checks": "failed before runner assignment at observed current head",
        "canonical_run_graphs": "checked and left unchanged; no new run measurement",
        "addendum_asset_sha256": {name: digest(HERE / name) for name in ASSETS},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build(), indent=2) + "\n"
    output = HERE / "claim-addendum.json"
    if args.check:
        assert output.read_text() == content, "addendum differs from bound evidence"
        print("addendum matches sealed independent review, local full gate and inspected PDF")
    else:
        assert not output.exists(), "addendum exists; use --check"
        output.write_text(content)
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
