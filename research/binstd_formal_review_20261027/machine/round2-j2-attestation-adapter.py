#!/usr/bin/env python3
"""Wrap a sealed top-level J2 attestation for the stock independence checker.

This changes only YAML nesting. It does not edit the reviewer artifact or add
review claims. The expected source hash binds this adapter to the sealed file.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
MACHINE = Path(__file__).resolve().parent
SOURCE = (
    ROOT
    / "research/binstd_formal_review_round2_20261027/reports/"
    "TASK-20261027-b17d02/review_attestation.yaml"
)
EXPECTED_SOURCE_SHA256 = (
    "1f8a9a2b2deb1b5ea065020c1d352fc039aba42460ed9e95255d7d9e08571ec9"
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    assert digest(source_bytes) == EXPECTED_SOURCE_SHA256
    original = yaml.safe_load(source_bytes)
    assert isinstance(original, dict)
    assert original["task_id"] == "TASK-20261027-b17d02"
    assert original["read_sibling_reports"] is False
    assert original["blind_from_respected"] is True

    wrapped = {"review_attestation": original}
    out = MACHINE / "round2-j2-checker-attestation.yaml"
    out_bytes = yaml.safe_dump(wrapped, sort_keys=False, allow_unicode=True).encode()
    if out.exists():
        assert out.read_bytes() == out_bytes
    else:
        out.write_bytes(out_bytes)
    assert yaml.safe_load(out_bytes)["review_attestation"] == original

    receipt = {
        "schema": "binstd.checker_attestation_adapter.v1",
        "source_path": str(SOURCE.relative_to(ROOT)),
        "source_sha256": digest(source_bytes),
        "adapter_path": str(out.relative_to(ROOT)),
        "adapter_sha256": digest(out_bytes),
        "data_preserved": True,
        "transformation": "Nest the complete sealed YAML mapping under review_attestation; no value edits",
    }
    receipt_path = MACHINE / "round2-j2-attestation-adapter.json"
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    if receipt_path.exists():
        assert receipt_path.read_bytes() == receipt_bytes
    else:
        receipt_path.write_bytes(receipt_bytes)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
