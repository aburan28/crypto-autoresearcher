#!/usr/bin/env python3
"""Reclassify the 617 pinned ecbench receipts by declared session status.

An integrity verifier can return ``ok`` for the records that an interrupted
session retained. That verdict does not turn the run into a completed run.
The original receipts remain immutable; the nested-evidence P40 correction
supersedes only that session's first, incomplete input preparation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PINNED_CRYPTO_HEAD = "172f84c7b0143ff5b4a26d6d21ffed3bf0f0cf3b"
P40 = "research/ic_frontier_campaign_20261015/select/sessions/P40"
P40_CORRECTION = HERE / "ecbench-earlier-v2/nested-rechecks/9638deb99c0eeb49b657"
OUTPUT = HERE / "ecbench-status-correction.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(data: object) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n").encode()


def receipt(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    return json.loads(raw), digest(raw)


def build() -> dict:
    rows = []
    seen = set()
    for batch in ("ecbench-earlier-v2", "ecbench-later-v2"):
        for path in sorted((HERE / batch).glob("*.json")):
            if path.name.endswith(".ecbench.json"):
                continue
            source, source_hash = receipt(path)
            if source.get("schema") != "ecbench.session.integrity.recheck/v1":
                continue
            session = source.get("session_dir")
            if not session:
                continue
            assert source["head"] == PINNED_CRYPTO_HEAD, path
            assert session not in seen, session
            seen.add(session)
            result_name = source.get("result_file")
            result_hash = None
            original_result_hash = None
            if result_name is None:
                assert source["exit_code"] == 2, path
                status = "complete_missing_inputs"
            else:
                result, result_hash = receipt(path.with_name(result_name))
                assert result_hash == source["result_sha256"], path
                original_result_hash = result_hash
                if session == P40:
                    correction, _ = receipt(P40_CORRECTION.with_suffix(".json"))
                    assert correction["head"] == PINNED_CRYPTO_HEAD
                    assert correction["session_dir"] == session
                    assert correction["source_session_sha256"] == source["session_json_sha256"]
                    result, result_hash = receipt(P40_CORRECTION.with_suffix(".ecbench.json"))
                    assert result_hash == correction["audit_sha256"]
                if result["ok"] and result["records_bound"] and not result["problems"]:
                    status = {
                        "complete": "complete_status_integrity_pass",
                        "interrupted": "interrupted_status_bound_integrity_pass",
                    }[result["session_status"]]
                else:
                    assert result["session_status"] == "interrupted"
                    assert not result["records_bound"]
                    status = "interrupted_status_unbound"
            rows.append(
                {
                    "batch": batch,
                    "session_dir": session,
                    "source_session_sha256": source["session_json_sha256"],
                    "receipt_sha256": source_hash,
                    "original_result_sha256": original_result_hash,
                    "effective_result_sha256": result_hash,
                    "status": status,
                }
            )
    rows.sort(key=lambda row: row["session_dir"])
    counts = dict(sorted(Counter(row["status"] for row in rows).items()))
    expected = {
        "complete_missing_inputs": 4,
        "complete_status_integrity_pass": 590,
        "interrupted_status_bound_integrity_pass": 13,
        "interrupted_status_unbound": 10,
    }
    assert len(rows) == len(seen) == 617
    assert counts == expected, counts
    by_batch = {
        batch: dict(sorted(Counter(row["status"] for row in rows if row["batch"] == batch).items()))
        for batch in ("ecbench-earlier-v2", "ecbench-later-v2")
    }
    return {
        "schema": "sheriff.ecbench.declared-status-correction/v1",
        "pinned_crypto_head": PINNED_CRYPTO_HEAD,
        "scope": "617 source-bound ecbench audit receipts; integrity and declared status, not timing reproduction",
        "session_count": len(rows),
        "counts": counts,
        "by_batch": by_batch,
        "all_rows_sha256": digest(canonical(rows)),
        "p40_original_failed_audit_sha256": next(row["original_result_sha256"] for row in rows if row["session_dir"] == P40),
        "p40_corrected_audit_sha256": next(row["effective_result_sha256"] for row in rows if row["session_dir"] == P40),
        "noncomplete_rows": [row for row in rows if row["status"] != "complete_status_integrity_pass"],
        "interpretation": "A bound integrity pass for an interrupted session verifies retained records only; it is not evidence that the planned run completed.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare with committed output")
    args = parser.parse_args()
    result = build()
    if args.check:
        assert json.loads(OUTPUT.read_text()) == result
        print("ecbench declared-status correction matches all 617 receipts")
    else:
        OUTPUT.write_bytes(json.dumps(result, indent=2, sort_keys=True).encode() + b"\n")
        print(OUTPUT)


if __name__ == "__main__":
    main()
