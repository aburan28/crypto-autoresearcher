#!/usr/bin/env python3
"""RUN-HZM-001-d: aggregate metrics and apply the specification's outcome
classification (specification.yaml planned_runs[3]).

Because CTRL-HZM-MANUSCRIPT-ALIGNMENT failed in RUN-HZM-001-a and the
pre-registered stopping rule fired (stopping_rules[0]: "a toy run is never
opened on unaligned formulas"), RUN-HZM-001-b and RUN-HZM-001-c were never
opened. There are therefore no enumeration/control metrics to aggregate.
This run's job reduces to reading RUN-HZM-001-a's raw-result.json, applying
the specification's own decision rule for this branch, and recording the
final experiment-level classification and metric completeness table.
"""
from __future__ import annotations

import json
from pathlib import Path

EXP_DIR = Path(__file__).resolve().parents[2]
RUN_A = EXP_DIR / "runs" / "RUN-HZM-001-a" / "raw-result.json"
RUN_DIR = Path(__file__).resolve().parent


def main() -> int:
    run_a = json.loads(RUN_A.read_text())

    primary_metrics_status = {
        "candidate_completion_count_ratio": "not_measured (RUN-HZM-001-b never opened)",
        "signature_enumeration_count_ratio": "not_measured (RUN-HZM-001-b never opened)",
        "charged_expected_work_vs_rho_bound": "not_measured (RUN-HZM-001-c never opened)",
        "zero_minor_certificate_reverification_failures": "not_applicable (no certificate was ever generated; certificate.kind: none for every run in this experiment)",
        "brute_force_control_zero_minor_discrepancies": "not_measured (RUN-HZM-001-c never opened)",
    }
    secondary_metrics_status = {
        "measured_zero_minor_hit_rate_vs_occupancy_law": "not_measured",
        "per_stage_charged_operations": "not_measured",
        "failed_outer_trials": "not_measured",
        "peak_live_field_elements": "not_measured",
        "manuscript_alignment_anchors": "RECORDED — see manuscript_alignment.md and RUN-HZM-001-a/raw-result.json.anchors",
        "worked_example_source": "control_unavailable — see manuscript_alignment.md",
    }

    controls_status = {
        "CTRL-HZM-MANUSCRIPT-ALIGNMENT": "FAIL — " + run_a["ctrl_hzm_manuscript_alignment"]["reason"][:200] + "...",
        "CTRL-HZM-WORKED-EXAMPLE": "control_unavailable (no fully parameterized worked example in the pinned manuscript)",
        "CTRL-HZM-BRUTE-FORCE": "not_evaluated (Stage 1 stopped the experiment before Stage 2/3 could open)",
        "CTRL-HZM-CERTIFICATE": "not_applicable (no certificate was ever generated under this experiment; claim_tier toy, no solve/relation claimed)",
    }

    decision_rule_applied = {
        "success_criterion_evaluatable": False,
        "falsification_criterion_branch": "(a) manuscript-alignment premise fails -> "
                                          "recorded inconclusive_misalignment per "
                                          "RT-20260723-303, NOT branch (b) (charged "
                                          "cost meets/exceeds rho bound), because no "
                                          "cost was ever charged.",
        "final_classification": "inconclusive_misalignment",
        "note": "Both the success_criterion and falsification_criterion(b) require "
                "measured counts/costs that this experiment never produced, because "
                "the pre-registered Stage-1 stop fired first. This is neither a "
                "positive (gate survival) nor a scoped-negative (falsification-b, "
                "non-sub-rho) result; it is the pre-registered third branch, "
                "explicitly anticipated by RT-20260723-303 and "
                "specification.yaml falsification_criterion(a).",
    }

    result = {
        "run_id": "RUN-HZM-001-d",
        "experiment_id": "EXP-HZM-001",
        "purpose": "Aggregate metrics, apply outcome classification, write analysis and execution report.",
        "input_run": "RUN-HZM-001-a",
        "runs_opened": ["RUN-HZM-001-a", "RUN-HZM-001-d"],
        "runs_never_opened": {
            "RUN-HZM-001-b": run_a["stopping_rule_applied"],
            "RUN-HZM-001-c": run_a["stopping_rule_applied"],
        },
        "primary_metrics_status": primary_metrics_status,
        "secondary_metrics_status": secondary_metrics_status,
        "controls_status": controls_status,
        "decision_rule_applied": decision_rule_applied,
        "experiment_level_classification": "inconclusive_misalignment",
    }

    (RUN_DIR / "raw-result.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
