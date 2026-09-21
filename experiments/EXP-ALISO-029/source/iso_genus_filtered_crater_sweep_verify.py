#!/usr/bin/env python3
"""Structural verifier for the multi-discriminant genus-filter sweep."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


INPUT = Path(
    "experiments/ecdlp_isogeny/"
    "iso_genus_filtered_crater_sweep_result.json"
)
OUTPUT = Path(
    "experiments/ecdlp_isogeny/"
    "iso_genus_filtered_crater_sweep_verify.json"
)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    source = json.loads(INPUT.read_text())
    row_checks = []
    for row in source["rows"]:
        manifest = row["pre_verifier_manifest"]
        manifest_hash = sha256(
            json.dumps(
                manifest, sort_keys=True, separators=(",", ":")
            ).encode()
        )
        counts = [entry["count"] for entry in row["class_counts"]]
        candidate_count = len(manifest["candidate_j_invariants"])
        checks = {
            "row_success": bool(row["success"]),
            "frobenius_identity": (
                row["parameters"]["t"] ** 2
                - 4 * row["parameters"]["p"]
                == row["parameters"]["f"] ** 2 * row["parameters"]["D"]
            ),
            "manifest_hash": (
                manifest_hash == row["pre_verifier_manifest_sha256"]
            ),
            "genus_class_count": (
                len(row["class_counts"]) == row["genus_number"]
            ),
            "equal_class_sizes": (
                set(counts) == {row["expected_genus_size"]}
            ),
            "candidate_count": (
                candidate_count == row["expected_genus_size"]
            ),
            "reduction_accounting": (
                row["reduction"]["before"] == row["class_number"]
                and row["reduction"]["after"] == candidate_count
                and row["reduction"]["factor"] == row["genus_number"]
            ),
            "ancestor_retained": bool(
                row["withheld_verification"]["ancestor_retained"]
            ),
            "ancestor_in_frozen_manifest": (
                row["withheld_verification"]["ancestor_j"]
                in manifest["candidate_j_invariants"]
            ),
            "unique_withheld_ascent": (
                row["withheld_verification"]["crater_ascent_count"] == 1
            ),
            "extension_degrees_match_primes": (
                row["extension_degrees"]
                == row["parameters"]["pairing_primes"]
            ),
        }
        row_checks.append(
            {
                "D": row["parameters"]["D"],
                "checks": checks,
                "passed": all(checks.values()),
            }
        )
    assertions = {
        "schema": source["schema"] == "iso-genus-filtered-crater-sweep-v1",
        "fixture_count_four": source["fixture_count"] == 4,
        "all_rows_present": len(source["rows"]) == 4,
        "all_source_success": bool(source["all_success"]),
        "all_row_checks": all(row["passed"] for row in row_checks),
        "multiple_conductors": len(
            {row["parameters"]["f"] for row in source["rows"]}
        )
        >= 2,
        "multiple_class_numbers": len(
            {row["class_number"] for row in source["rows"]}
        )
        >= 2,
    }
    status = "PASS" if all(assertions.values()) else "FAIL"
    result = {
        "schema": "iso-genus-filtered-crater-sweep-verify-v1",
        "status": status,
        "assertions": assertions,
        "assertions_passed": sum(assertions.values()),
        "assertions_total": len(assertions),
        "row_checks": row_checks,
        "input_sha256": sha256(INPUT.read_bytes()),
        "producer_scientific_payload_sha256": source[
            "scientific_payload_sha256"
        ],
    }
    result["scientific_payload_sha256"] = sha256(
        json.dumps(
            {
                "assertions": assertions,
                "row_checks": row_checks,
                "producer_scientific_payload_sha256": result[
                    "producer_scientific_payload_sha256"
                ],
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    )
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
