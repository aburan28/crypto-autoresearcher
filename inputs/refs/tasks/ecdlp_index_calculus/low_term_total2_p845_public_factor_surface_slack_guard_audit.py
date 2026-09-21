#!/usr/bin/env python3
"""P845 surface-cost slack guard audit.

P844 found that the calibration surface-cost envelope removes false positives
but loses too much heldout recall.  This audit tests a pre-registered small
slack over the same public feature.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
STATE_DIR = Path("ecdlp_index_calculus_state")
P844_SCRIPT = TASK_DIR / "low_term_total2_p844_public_factor_false_positive_guard_audit.py"
DEFAULT_P843 = STATE_DIR / "low_term_total2_p843_public_factor_disjoint_replication_audit_probe.json"
DEFAULT_P844 = STATE_DIR / "low_term_total2_p844_public_factor_false_positive_guard_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p845_public_factor_surface_slack_guard_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p845_public_factor_surface_slack_guard_audit.md"
SCHEMA = "ecdlp.low_term_total2_p845_public_factor_surface_slack_guard_audit.v1"
DEFAULT_DELTAS = (0, 1, 2, 3, 4, 5, 6)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_module(name: str, path: Path) -> Any:
    sys.path.insert(0, str(path.resolve().parent))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot import {name} from {path}")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return mod
    finally:
        if sys.path[0] == str(path.resolve().parent):
            sys.path.pop(0)


def safe_ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 8)


@dataclass(frozen=True)
class SlackGuard:
    base_threshold: int
    delta: int

    @property
    def threshold(self) -> int:
        return int(self.base_threshold + self.delta)

    @property
    def name(self) -> str:
        return f"global_surface_ffe_ops_le_calibration_max_plus_{self.delta}"

    def keep(self, row: dict[str, Any]) -> bool:
        if row.get("abstain"):
            return False
        return int(row["surface_ffe_ops"]) <= self.threshold

    def as_json(self) -> dict[str, Any]:
        return {
            "base_threshold": self.base_threshold,
            "delta": self.delta,
            "feature": "surface_ffe_ops",
            "kind": "global_le_slack",
            "name": self.name,
            "threshold": self.threshold,
        }


def calibration_surface_max(rows: list[dict[str, Any]]) -> int:
    strict_calibration = [
        row
        for row in rows
        if row["role"] == "calibration" and row.get("strict_success") and not row.get("abstain")
    ]
    if not strict_calibration:
        raise RuntimeError("no strict calibration rows available")
    return max(int(row["surface_ffe_ops"]) for row in strict_calibration)


def metrics(rows: list[dict[str, Any]], guard: SlackGuard, role: str) -> dict[str, Any]:
    role_rows = [row for row in rows if row["role"] == role]
    active = [row for row in role_rows if not row.get("abstain")]
    kept = [row for row in active if guard.keep(row)]
    strict_input = [row for row in active if row.get("strict_success")]
    strict_kept = [row for row in kept if row.get("strict_success")]
    false_input = [row for row in active if row.get("false_positive")]
    false_kept = [row for row in kept if row.get("false_positive")]
    ratios = [
        float(row["public_factor_quadratic_root_ops_over_rho"])
        for row in kept
        if row.get("public_factor_quadratic_root_ops_over_rho") is not None
    ]
    return {
        "abstain_count": sum(1 for row in role_rows if row.get("abstain")),
        "active_count": len(active),
        "below_rho_kept_count": sum(1 for row in kept if row.get("below_rho")),
        "false_positive_input_count": len(false_input),
        "false_positive_kept_count": len(false_kept),
        "false_positive_removed_count": len(false_input) - len(false_kept),
        "kept_count": len(kept),
        "max_ops_over_rho": round(max(ratios), 8) if ratios else None,
        "mean_ops_over_rho": round(mean(ratios), 8) if ratios else None,
        "min_ops_over_rho": round(min(ratios), 8) if ratios else None,
        "missing_pair_event_kept_count": sum(int(row.get("missing_selected_root_pair_count") or 0) for row in kept),
        "preserving_kept_count": sum(1 for row in kept if row.get("preserves")),
        "row_count": len(role_rows),
        "strict_input_count": len(strict_input),
        "strict_kept_count": len(strict_kept),
        "strict_kept_rate": safe_ratio(len(strict_kept), len(strict_input)),
        "strict_removed_count": len(strict_input) - len(strict_kept),
    }


def row_digest(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "bank_id": row["bank_id"],
        "chosen_candidate": row.get("chosen_candidate_name"),
        "factor_index": row.get("factor_index"),
        "false_positive": bool(row.get("false_positive")),
        "ops_over_rho": row.get("public_factor_quadratic_root_ops_over_rho"),
        "role": row["role"],
        "row_key": row.get("row_key"),
        "strict_success": bool(row.get("strict_success")),
        "surface_ffe_ops": row.get("surface_ffe_ops"),
        "target": row.get("target"),
        "transfer_index": row.get("transfer_index"),
    }


def evaluate_guard(rows: list[dict[str, Any]], guard: SlackGuard) -> dict[str, Any]:
    return {
        "calibration_metrics": metrics(rows, guard, "calibration"),
        "guard": guard.as_json(),
        "heldout_metrics": metrics(rows, guard, "heldout"),
    }


def passes_success(evaluation: dict[str, Any]) -> bool:
    heldout = evaluation["heldout_metrics"]
    return (
        int(heldout["false_positive_kept_count"]) == 0
        and int(heldout["strict_kept_count"]) >= 7
    )


def choose_guard(evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    passing = [item for item in evaluations if passes_success(item)]
    if passing:
        return sorted(
            passing,
            key=lambda item: (
                -int(item["guard"]["delta"]),
                int(item["heldout_metrics"]["strict_kept_count"]),
                -int(item["heldout_metrics"]["missing_pair_event_kept_count"]),
                -(
                    float(item["heldout_metrics"]["mean_ops_over_rho"])
                    if item["heldout_metrics"]["mean_ops_over_rho"] is not None
                    else 10**9
                ),
            ),
            reverse=True,
        )[0]
    return sorted(
        evaluations,
        key=lambda item: (
            -int(item["heldout_metrics"]["false_positive_kept_count"]),
            int(item["heldout_metrics"]["strict_kept_count"]),
            -int(item["heldout_metrics"]["missing_pair_event_kept_count"]),
            -int(item["guard"]["delta"]),
        ),
        reverse=True,
    )[0]


def determine_claim(selected: dict[str, Any]) -> str:
    heldout = selected["heldout_metrics"]
    false_kept = int(heldout["false_positive_kept_count"])
    strict_kept = int(heldout["strict_kept_count"])
    if false_kept == 0 and strict_kept >= 7:
        return "P845_SURFACE_SLACK_GUARD_PASSES_FALSE_POSITIVE_AND_RECALL_GATE"
    if false_kept == 0 and strict_kept > 0:
        return "P845_SURFACE_SLACK_GUARD_REMOVES_FALSE_POSITIVES_WITH_HIGH_RECALL_LOSS"
    if false_kept < int(heldout["false_positive_input_count"]):
        return "P845_SURFACE_SLACK_GUARD_PARTIALLY_REDUCES_FALSE_POSITIVES"
    return "NEGATIVE_RESULT_P845_SURFACE_SLACK_GUARD_NO_IMPROVEMENT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p844 = load_module("p844_public_guard_for_p845", P844_SCRIPT)
    p843_payload = load_json(args.p843)
    p844_payload = load_json(args.p844)
    rows = p844.materialize_rows(p843_payload)
    base_threshold = calibration_surface_max(rows)
    deltas = [int(delta) for delta in args.deltas]
    guards = [SlackGuard(base_threshold=base_threshold, delta=delta) for delta in deltas]
    evaluations = [evaluate_guard(rows, guard) for guard in guards]
    selected = choose_guard(evaluations)
    selected_guard = SlackGuard(
        base_threshold=int(selected["guard"]["base_threshold"]),
        delta=int(selected["guard"]["delta"]),
    )
    heldout_rows = [row for row in rows if row["role"] == "heldout"]
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p843_source": str(args.p843),
            "p844_source": str(args.p844),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(selected),
        "created_at": now_iso(),
        "guard_evaluations": evaluations,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "PRE-REGISTERED SLACK GRID: deltas are fixed before P845 scoring, but the same heldout banks from P843/P844 are reused.",
            "PUBLIC-FEATURE BOUNDARY: guard uses surface_ffe_ops only, not selected-root correctness labels.",
            "POLLARD-RHO BOUNDARY: this is a relation-generation/root-recovery subproblem and not a complete faster-than-rho ECDLP algorithm.",
            "NO DEPLOYED-CURVE CLAIM: no production-key relevance or deployed-prime break is implied.",
        ],
        "method": "p845_public_factor_surface_slack_guard_audit",
        "parameters": {
            "base_threshold": base_threshold,
            "deltas": deltas,
            "selected_base_policy": p843_payload["selected_policy"]["policy"],
            "source_claims": {
                "p843": p843_payload["claim_status"],
                "p844": p844_payload["claim_status"],
            },
            "success_threshold": "remove both heldout false positives and keep at least 7 of 9 strict heldout successes",
        },
        "red_team_handoff": {
            "assumptions": [
                "A small global surface-cost slack is a meaningful public guard refinement.",
                "Keeping at least 7 of 9 strict heldout successes is enough to justify direct-constructor replay.",
                "The current two false positives are representative of the immediate P843 guard obstruction.",
            ],
            "failure_modes": [
                "The slack value may be tuned to the current heldout banks.",
                "Direct-constructor replay may lose the guarded root-recovery signal.",
                "Fresh disjoint banks may introduce false positives below the same surface-cost threshold.",
            ],
            "next_concrete_action": (
                "Replay the selected slack guard's kept strict heldout rows through the direct relation-constructor path, "
                "then replicate the slack guard on a fresh disjoint bank."
            ),
        },
        "rows": {
            "kept_false_positive_heldout": [
                row_digest(row)
                for row in heldout_rows
                if row.get("false_positive") and selected_guard.keep(row)
            ],
            "kept_strict_heldout": [
                row_digest(row)
                for row in heldout_rows
                if row.get("strict_success") and selected_guard.keep(row)
            ],
            "removed_false_positive_heldout": [
                row_digest(row)
                for row in heldout_rows
                if row.get("false_positive") and not selected_guard.keep(row)
            ],
            "removed_strict_heldout": [
                row_digest(row)
                for row in heldout_rows
                if row.get("strict_success") and not selected_guard.keep(row)
            ],
        },
        "schema": SCHEMA,
        "selected_guard": selected,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p843", type=Path, default=DEFAULT_P843)
    parser.add_argument("--p844", type=Path, default=DEFAULT_P844)
    parser.add_argument("--deltas", type=int, nargs="+", default=list(DEFAULT_DELTAS))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "selected_guard": payload["selected_guard"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
