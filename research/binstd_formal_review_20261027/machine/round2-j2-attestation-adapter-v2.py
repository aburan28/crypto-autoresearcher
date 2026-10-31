#!/usr/bin/env python3
"""Deterministically expose a sealed J2 attestation to the stock checker.

The reviewer recorded source reads as objects with path, role and hash. The
stock checker expects a list of strings. This adapter projects each exact path
into that interface and retains the full original objects beside it. Every
other reviewer field is unchanged. The original sealed YAML is never edited.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
MACHINE = Path(__file__).resolve().parent
SOURCE = ROOT / ("research/binstd_formal_review_round2_20261027/reports/"
                 "TASK-20261027-b17d02/review_attestation.yaml")
EXPECTED_SHA256 = "1f8a9a2b2deb1b5ea065020c1d352fc039aba42460ed9e95255d7d9e08571ec9"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    assert digest(source_bytes) == EXPECTED_SHA256
    original = yaml.safe_load(source_bytes)
    assert isinstance(original, dict)
    reads = original["sources_read"]
    assert isinstance(reads, list) and reads
    assert all(isinstance(item, dict) and isinstance(item.get("path"), str)
               and item["path"] for item in reads)
    paths = [item["path"] for item in reads]
    assert len(paths) == len(set(paths))

    projected = dict(original)
    projected["sources_read"] = paths
    projected["sources_read_with_hashes"] = reads
    wrapped = {"review_attestation": projected}
    out = MACHINE / "round2-j2-checker-attestation-v2.yaml"
    out_bytes = yaml.safe_dump(wrapped, sort_keys=False, allow_unicode=True).encode()
    if out.exists():
        assert out.read_bytes() == out_bytes
    else:
        out.write_bytes(out_bytes)

    reloaded = yaml.safe_load(out_bytes)["review_attestation"]
    assert reloaded["sources_read"] == paths
    assert reloaded["sources_read_with_hashes"] == reads
    assert {k: v for k, v in reloaded.items()
            if k not in ("sources_read", "sources_read_with_hashes")} == {
                k: v for k, v in original.items() if k != "sources_read"
            }

    receipt = {
        "schema": "binstd.checker_attestation_adapter.v2",
        "source_path": str(SOURCE.relative_to(ROOT)),
        "source_sha256": digest(source_bytes),
        "adapter_path": str(out.relative_to(ROOT)),
        "adapter_sha256": digest(out_bytes),
        "source_read_count": len(paths),
        "all_read_objects_retained": True,
        "other_fields_identical": True,
        "transformation": "Wrap under review_attestation and project each source-read path string, retaining each full original read object",
    }
    receipt_path = MACHINE / "round2-j2-attestation-adapter-v2.json"
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    if receipt_path.exists():
        assert receipt_path.read_bytes() == receipt_bytes
    else:
        receipt_path.write_bytes(receipt_bytes)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
