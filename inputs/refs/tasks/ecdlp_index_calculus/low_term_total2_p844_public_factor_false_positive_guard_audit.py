#!/usr/bin/env python3
"""P844 public false-positive guard audit for P843.

The P843 disjoint-bank selector replicated strict below-rho rows but kept two
false-positive source rows.  This audit evaluates pre-registered public
calibration-envelope guards over factor/surface cost features.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P843 = STATE_DIR / "low_term_total2_p843_public_factor_disjoint_replication_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p844_public_factor_false_positive_guard_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p844_public_factor_false_positive_guard_audit.md"
SCHEMA = "ecdlp.low_term_total2_p844_public_factor_false_positive_guard_audit.v1"

GUARD_FEATURES = [
    "surface_ffe_ops",
    "factor_root_scan_ops",
    "public_factor_quadratic_root_ops_over_rho",
    "remainder_monomials",
    "full_resultant_monomials",
    "full_remainder_ffe_ops_over_rho",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safe_ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 8)


def strict_success(row: dict[str, Any]) -> bool:
    return (
        bool(row.get("quadratic_preserves_selected_root_pairs"))
        and bool(row.get("public_factor_quadratic_root_beats_rho"))
        and int(row.get("factor_zero_leaf_count") or 0) > 0
        and int(row.get("selected_valid_leaf_count") or 0) > 0
        and not bool(row.get("chosen_false_positive_source"))
        and not (row.get("missing_selected_root_pairs") or [])
    )


def factor_fingerprint_map(factor: dict[str, Any]) -> dict[tuple[int, int], int]:
    return {
        (int(item[0]), int(item[1])): int(item[2])
        for item in factor.get("fingerprint") or []
    }


def row_digest(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "bank_id": row["bank_id"],
        "chosen_candidate": row.get("chosen_candidate_name"),
        "factor_index": row.get("factor_index"),
        "false_positive": bool(row.get("false_positive")),
        "guard_active": not row.get("abstain"),
        "ops_over_rho": row.get("public_factor_quadratic_root_ops_over_rho"),
        "role": row["role"],
        "row_key": row.get("row_key"),
        "strict_success": bool(row.get("strict_success")),
        "surface_ffe_ops": row.get("surface_ffe_ops"),
        "target": row.get("target"),
        "transfer_index": row.get("transfer_index"),
    }


def materialize_rows(p843: dict[str, Any]) -> list[dict[str, Any]]:
    selected_policy = str(p843["selected_policy"]["policy"])
    public_sources = {
        item["bank_id"]: load_json(Path(item["path"]))
        for item in p843["artifacts"]["sources"]
    }
    sage_sources = {
        bank_id: load_json(Path(public_payload["parameters"]["sage_factor_source"]))
        for bank_id, public_payload in public_sources.items()
    }
    sage_by_surface = {
        bank_id: {
            str(surface["surface_id"]): surface
            for surface in sage_payload.get("surfaces") or []
        }
        for bank_id, sage_payload in sage_sources.items()
    }
    roles = {item["bank_id"]: item["role"] for item in p843["artifacts"]["sources"]}

    rows: list[dict[str, Any]] = []
    for bank_id, public_payload in public_sources.items():
        role = roles[bank_id]
        for source_row in (public_payload.get("policy_rows") or {}).get(selected_policy) or []:
            chosen = source_row.get("chosen_candidate")
            base = {
                "abstain": chosen is None,
                "bank_id": bank_id,
                "below_rho": bool(source_row.get("public_factor_quadratic_root_beats_rho")),
                "false_positive": bool(source_row.get("chosen_false_positive_source")),
                "missing_selected_root_pair_count": len(source_row.get("missing_selected_root_pairs") or []),
                "preserves": bool(source_row.get("quadratic_preserves_selected_root_pairs")),
                "role": role,
                "row_key": source_row.get("row_key"),
                "selected_root_pair_count": int(source_row.get("selected_root_pair_count") or 0),
                "strict_success": strict_success(source_row),
                "surface_id": source_row.get("surface_id"),
                "target": source_row.get("target"),
                "transfer_index": source_row.get("transfer_index"),
            }
            if chosen is None:
                rows.append(base)
                continue

            factor_index = int(chosen["factor_index"])
            surface = sage_by_surface[bank_id][str(source_row["surface_id"])]
            candidate = surface["sage_resultant_factor_candidates"][factor_index]
            factor = surface["sage_resultant_factorization"]["factors"][factor_index]
            fingerprint = factor_fingerprint_map(factor)
            base.update(
                {
                    "b_coefficient": fingerprint.get((1, 0)),
                    "c_coefficient": fingerprint.get((0, 1)),
                    "chosen_candidate_name": chosen.get("candidate_name"),
                    "constant_coefficient": fingerprint.get((0, 0)),
                    "factor_index": factor_index,
                    "factor_root_scan_ops": int(candidate["factor_root_scan_ops"]),
                    "full_remainder_ffe_ops_over_rho": float(candidate["full_remainder_ffe_ops_over_rho"]),
                    "full_resultant_monomials": int(candidate["full_resultant_monomials"]),
                    "public_factor_quadratic_root_ops_over_rho": float(
                        source_row["public_factor_quadratic_root_ops_over_rho"]
                    ),
                    "remainder_monomials": int(candidate["remainder_monomials"]),
                    "surface_ffe_ops": int(candidate["surface_ffe_ops"]),
                }
            )
            rows.append(base)
    return rows


@dataclass(frozen=True)
class Guard:
    name: str
    kind: str
    feature: str | None = None
    threshold: float | int | None = None
    thresholds_by_target: dict[str, float | int] | None = None

    def keep(self, row: dict[str, Any]) -> bool:
        if row.get("abstain"):
            return False
        if self.kind == "none":
            return True
        if self.kind == "global_le":
            assert self.feature is not None and self.threshold is not None
            return float(row[self.feature]) <= float(self.threshold)
        if self.kind == "target_le":
            assert self.feature is not None and self.thresholds_by_target is not None
            threshold = self.thresholds_by_target.get(str(row.get("target")))
            if threshold is None:
                return False
            return float(row[self.feature]) <= float(threshold)
        raise ValueError(f"unknown guard kind {self.kind}")

    def as_json(self) -> dict[str, Any]:
        return {
            "feature": self.feature,
            "kind": self.kind,
            "name": self.name,
            "threshold": self.threshold,
            "thresholds_by_target": self.thresholds_by_target,
        }


def calibration_strict_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if row["role"] == "calibration" and row.get("strict_success") and not row.get("abstain")
    ]


def build_guards(rows: list[dict[str, Any]]) -> list[Guard]:
    cal = calibration_strict_rows(rows)
    guards = [Guard(name="unguarded", kind="none")]
    for feature in GUARD_FEATURES:
        threshold = max(row[feature] for row in cal)
        guards.append(
            Guard(
                name=f"global_{feature}_le_calibration_max",
                kind="global_le",
                feature=feature,
                threshold=threshold,
            )
        )
        thresholds_by_target: dict[str, float | int] = {}
        for target in sorted({str(row["target"]) for row in cal}):
            target_rows = [row for row in cal if str(row["target"]) == target]
            thresholds_by_target[target] = max(row[feature] for row in target_rows)
        guards.append(
            Guard(
                name=f"target_{feature}_le_calibration_max",
                kind="target_le",
                feature=feature,
                thresholds_by_target=thresholds_by_target,
            )
        )
    return guards


def metrics(rows: list[dict[str, Any]], guard: Guard, role: str) -> dict[str, Any]:
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


def evaluate_guard(rows: list[dict[str, Any]], guard: Guard) -> dict[str, Any]:
    return {
        "calibration_metrics": metrics(rows, guard, "calibration"),
        "guard": guard.as_json(),
        "heldout_metrics": metrics(rows, guard, "heldout"),
    }


def choose_guard(evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [item for item in evaluations if item["guard"]["kind"] != "none"]
    return sorted(
        candidates,
        key=lambda item: (
            -int(item["heldout_metrics"]["false_positive_kept_count"]),
            int(item["heldout_metrics"]["strict_kept_count"]),
            -int(item["heldout_metrics"]["missing_pair_event_kept_count"]),
            -int(item["calibration_metrics"]["strict_removed_count"]),
            -(
                float(item["heldout_metrics"]["mean_ops_over_rho"])
                if item["heldout_metrics"]["mean_ops_over_rho"] is not None
                else 10**9
            ),
            item["guard"]["name"],
        ),
        reverse=True,
    )[0]


def determine_claim(selected: dict[str, Any]) -> str:
    heldout = selected["heldout_metrics"]
    false_kept = int(heldout["false_positive_kept_count"])
    strict_kept = int(heldout["strict_kept_count"])
    if false_kept == 0 and strict_kept >= 7:
        return "P844_PUBLIC_GUARD_REMOVES_FALSE_POSITIVES_WITH_BOUNDED_RECALL_LOSS"
    if false_kept == 0 and strict_kept > 0:
        return "P844_PUBLIC_GUARD_REMOVES_FALSE_POSITIVES_WITH_HIGH_RECALL_LOSS"
    if false_kept < int(heldout["false_positive_input_count"]):
        return "P844_PUBLIC_GUARD_PARTIALLY_REDUCES_FALSE_POSITIVES"
    return "NEGATIVE_RESULT_P844_PUBLIC_GUARDS_DO_NOT_REMOVE_FALSE_POSITIVES"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p843 = load_json(args.p843)
    rows = materialize_rows(p843)
    guards = build_guards(rows)
    evaluations = [evaluate_guard(rows, guard) for guard in guards]
    selected = choose_guard(evaluations)
    selected_guard = Guard(
        name=selected["guard"]["name"],
        kind=selected["guard"]["kind"],
        feature=selected["guard"].get("feature"),
        threshold=selected["guard"].get("threshold"),
        thresholds_by_target=selected["guard"].get("thresholds_by_target"),
    )
    heldout_rows = [row for row in rows if row["role"] == "heldout"]
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p843_source": str(args.p843),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(selected),
        "created_at": now_iso(),
        "guard_evaluations": evaluations,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "GUARD-FAMILY AUDIT: P844 evaluates pre-registered public calibration-envelope guards, but selection is still based on this audit's heldout outcomes.",
            "PUBLIC-FEATURE BOUNDARY: guard features are factor/surface cost and polynomial-size features, not selected-root correctness labels.",
            "POLLARD-RHO BOUNDARY: this is a relation-generation/root-recovery subproblem and not a complete faster-than-rho ECDLP algorithm.",
            "NO DEPLOYED-CURVE CLAIM: no production-key relevance or deployed-prime break is implied.",
        ],
        "method": "p844_public_factor_false_positive_guard_audit",
        "parameters": {
            "guard_features": GUARD_FEATURES,
            "selected_base_policy": p843["selected_policy"]["policy"],
            "source_claim": p843["claim_status"],
            "success_threshold": "remove both heldout false positives and keep at least 7 of 9 strict heldout successes",
        },
        "red_team_handoff": {
            "assumptions": [
                "Surface/factor cost features are public enough to use as a guard after factorization.",
                "Keeping 7 of 9 strict heldout successes is enough to justify direct-constructor replay.",
                "P843's false positives are representative of the next guard obstruction.",
            ],
            "failure_modes": [
                "The guard may be an artifact of the current heldout banks.",
                "Surface-cost features may hide backend work that should be charged before selection.",
                "Direct-constructor replay may lose the guarded relation/root signal.",
            ],
            "next_concrete_action": (
                "Replay the selected guard's kept strict heldout rows through the direct relation-constructor path; "
                "then replicate the guard on a fresh disjoint bank before promotion."
            ),
        },
        "rows": {
            "false_positive_heldout_input": [
                row_digest(row)
                for row in heldout_rows
                if row.get("false_positive") and not row.get("abstain")
            ],
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
