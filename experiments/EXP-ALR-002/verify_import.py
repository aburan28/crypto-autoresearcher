#!/usr/bin/env python3
"""Verify the immutable AutoLab R183 import and its scoped claim boundary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
EXPECTED_SHA256 = {
    "frozen_m6_sparse_projector_prony_locator.json": "8d020353811cf7cf47e7950fe14f7da1df74eafb7c904f7e0abcfd875ef48c4b",
    "m6_sparse_projector_prony_locator_controls.json": "9575764c7e662210b9f41ffe2783be3f6b95926f7b3d534e361401704b63366f",
    "m6_sparse_projector_prony_locator_cost_ledger.json": "c91e54b65c5068a3cada5b3f2237ec1f1228989d2115f22cfc2fd183cec27a6b",
    "m6_sparse_projector_prony_locator_replay.json": "2473d0295858506f0ec687c03831c5b345f726323e59486ef98f17b070ba168e",
    "p1436_autoresearch_focus_harness_v132_result.md": "bcc9f9a3429a5632734e8b79c848547a06d528ed92c02835cd0b0b299d1a4a03",
    "p1553_m6_sparse_projector_prony_locator_probe_gate_r183.md": "4544744eccc2050390b69bc377d6188e6e66b28c226c2840d0f607bc9330e67d",
    "p1553_m6_sparse_projector_prony_locator_probe_parent_report_r183.yaml": "28f0bf2f9f380944bf92ad2349eabd7fe230cf0e9d18574f3b09a84ac88a983c",
    "p1553_m6_sparse_projector_prony_locator_probe_r183.py": "202a28eade6a3d532c4f9f8cf6ae3e02c9a74da9bccc436069917204e511b53f",
    "p1553_m6_sparse_projector_prony_locator_probe_report_r183.json": "a2e746fa5159a3684d3f6913888ad9c6a1fd7983fcb9abbacc17e6d4ee5baae5",
    "sparse_projector_prony_locator_applicability_r183.json": "652e2a17148613d57d729200a3297948e9cebc898ce07992482a5bf3927e3be8",
    "test_p1553_m6_sparse_projector_prony_locator_probe_r183.py": "c44e54238b0599e30211a4035ed19858104272c11bfb866d2528e63343fac60e",
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
        raise AssertionError(f"R183 import hash mismatch: {mismatches}")

    report = json.loads(
        (
            SOURCE
            / "p1553_m6_sparse_projector_prony_locator_probe_report_r183.json"
        ).read_text()
    )
    controls = report["controls"]
    admission = report["admission"]
    collision = controls["source_blind_trace_collision"]
    assert len(report["source_bindings"]) == 16
    assert admission["passed_obligation_count"] == 19
    assert admission["obligation_count"] == 28
    assert admission["nested_projector_identity_admitted"] is True
    assert admission["weighted_prony_output_stage_admitted"] is True
    assert admission["slp_direct_nested_moment_constructor_admitted"] is False
    assert admission["lane_admitted"] is False
    assert controls["control_count"] == 13
    assert controls["r182_replay_control_count"] == 12
    assert controls["new_divisor_family_control_count"] == 1
    assert controls["candidate_degree_sum"] == 256
    assert controls["noncandidate_degree_sum"] == 155
    assert controls["weighted_moment_count_sum"] == 512
    assert controls["all_fermat_projector_traces_equal_gcd_degrees"] is True
    assert controls["all_prony_locators_equal_candidate_factors"] is True
    assert collision["all_source_blind_power_sums_equal"] is True
    assert collision["candidate_locators_differ"] is True
    assert report["finite_controls_receive_asymptotic_credit"] is False
    assert report["pollard_rho_improvement"] is False
    assert report["shoup_bound_improvement"] is False
    assert report["breakthrough"] is False

    print(
        json.dumps(
            {
                "verified_artifact_count": len(actual),
                "control_count": controls["control_count"],
                "r182_replay_control_count": controls["r182_replay_control_count"],
                "new_divisor_family_control_count": controls[
                    "new_divisor_family_control_count"
                ],
                "weighted_moment_count": controls["weighted_moment_count_sum"],
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
