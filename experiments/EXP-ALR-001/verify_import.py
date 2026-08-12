#!/usr/bin/env python3
"""Verify the immutable AutoLab R182 import and its scoped claim boundary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
EXPECTED_SHA256 = {
    "frozen_m6_gcd_equivalent_target_subresultant.json": "29291879484cf68bc16b83e2341818a611bb0c529c53e135f33bc181f30d462e",
    "gcd_equivalent_target_subresultant_applicability_r182.json": "5f1700e9b00d6756daa58d38f36002e7f0dee704632f223de8f4bc55cfce620c",
    "m6_gcd_equivalent_target_subresultant_controls.json": "850099e9c6f538baea1f94b7d87dafbe8c2df7a83b3dcf9d47be9b233639b77f",
    "m6_gcd_equivalent_target_subresultant_cost_ledger.json": "0eb0f05465fc072c72b6cccc24105d420431eb53162a6d5042b135bdcb454121",
    "m6_gcd_equivalent_target_subresultant_replay.json": "bec170f0a0148e269b28c0499f7a8c65b20a3270a8f8dbfc41a0724d3e71e9ba",
    "p1436_autoresearch_focus_harness_v131_result.md": "47e7b2b328b93d4b2fcbb64773b654a930f2bbfd9c2a96de7a63963e89c3122c",
    "p1553_m6_gcd_equivalent_target_subresultant_probe_gate_r182.md": "960fbcdcae0867bc8b02786f81af9eb68ed337d2dfff9019e62c61248ca303fd",
    "p1553_m6_gcd_equivalent_target_subresultant_probe_parent_report_r182.yaml": "d83ffeed2d66b78ec40a7b14e3a89fd5a8940775d21f5c297c6105454032ba66",
    "p1553_m6_gcd_equivalent_target_subresultant_probe_r182.py": "0058a28e4c337df97cec7b2e87bb5cc16e18a5b47029ab72d12b852405875e15",
    "p1553_m6_gcd_equivalent_target_subresultant_probe_report_r182.json": "9a38150e9e7e0e41f455b000b4cda390aaff4f428c2828d5ffeed8a9781f7f5d",
    "test_p1553_m6_gcd_equivalent_target_subresultant_probe_r182.py": "37e7ced472a7eb2244e1539cb3248fd2e170bdec343a89a69b93ce9e05d39a7e",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    actual = {name: sha256_file(SOURCE / name) for name in EXPECTED_SHA256}
    mismatches = {
        name: {"expected": EXPECTED_SHA256[name], "actual": digest}
        for name, digest in actual.items()
        if digest != EXPECTED_SHA256[name]
    }
    if mismatches:
        raise AssertionError(f"R182 import hash mismatch: {mismatches}")

    report = json.loads(
        (SOURCE / "p1553_m6_gcd_equivalent_target_subresultant_probe_report_r182.json").read_text()
    )
    controls = report["controls"]
    admission = report["admission"]
    opposite = controls["opposite_point_two_chart_control"]
    assert admission["passed_obligation_count"] == 24
    assert admission["obligation_count"] == 35
    assert admission["target_subresultant_identity_admitted"] is True
    assert admission["represented_standard_routes_closed"] is True
    assert admission["slp_direct_output_sensitive_resultant_admitted"] is False
    assert controls["control_count"] == 12
    assert controls["held_out_control_count"] == 3
    assert controls["remainder_coefficient_slot_count"] == 2962
    assert controls["remainder_nonzero_coefficient_count"] == 2962
    assert controls["all_remainder_matrices_full_target_rank"] is True
    assert controls["all_norm_zero_iff_subresultant_gcd_nontrivial"] is True
    assert controls["all_unit_inverse_certificates_exact"] is True
    assert opposite["target_chart_count"] == 2
    assert opposite["candidate_roots_equal_gcd_roots"] is True
    assert report["pollard_rho_improvement"] is False
    assert report["shoup_bound_improvement"] is False
    assert report["breakthrough"] is False

    print(
        json.dumps(
            {
                "verified_artifact_count": len(actual),
                "control_count": controls["control_count"],
                "held_out_control_count": controls["held_out_control_count"],
                "opposite_point_target_chart_count": opposite["target_chart_count"],
                "passed_obligations": admission["passed_obligation_count"],
                "total_obligations": admission["obligation_count"],
                "breakthrough": report["breakthrough"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
