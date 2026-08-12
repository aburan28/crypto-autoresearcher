#!/usr/bin/env python3
"""P846 guarded public-factor direct replay readiness audit.

P845 found a narrow public surface-cost guard for the P843 factor policy.  This
audit replays that guard from source artifacts, exports direct-constructor input
packets for the heldout rows it selects, and reports verifier outcomes
separately.  It does not claim relation-equation certificates.
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
DEFAULT_P845 = STATE_DIR / "low_term_total2_p845_public_factor_surface_slack_guard_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p846_public_factor_direct_replay_readiness_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p846_public_factor_direct_replay_readiness_audit.md"
SCHEMA = "ecdlp.low_term_total2_p846_public_factor_direct_replay_readiness_audit.v1"


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
        if sys.path and sys.path[0] == str(path.resolve().parent):
            sys.path.pop(0)


def int_field(row: dict[str, Any], key: str) -> int | None:
    value = row.get(key)
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def bool_field(row: dict[str, Any], key: str) -> bool:
    return bool(row.get(key))


def numeric_summary(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {
        "count": len(values),
        "max": round(max(values), 8),
        "mean": round(mean(values), 8),
        "min": round(min(values), 8),
    }


def key_tuple(row: dict[str, Any]) -> tuple[str, str, int, int | None]:
    return (
        str(row["bank_id"]),
        str(row["row_key"]),
        int(row["transfer_index"]),
        row.get("factor_index"),
    )


def factor_terms(factor: dict[str, Any]) -> list[list[int]]:
    terms = factor.get("fingerprint") or []
    return sorted([[int(a), int(b), int(c)] for a, b, c in terms])


def public_zero(row: dict[str, Any]) -> bool:
    return bool(row.get("public_zero_recovered")) and row.get("public_factor_quadratic_root_ops") is not None


def profile_flags(source_row: dict[str, Any]) -> dict[str, bool]:
    chosen = source_row.get("chosen_candidate") if isinstance(source_row.get("chosen_candidate"), dict) else {}
    selected_leaf_count = int_field(source_row, "selected_leaf_count")
    factor_zero_leaf_count = int_field(source_row, "factor_zero_leaf_count")
    total_degree = int_field(chosen, "factor_total_degree")
    monomials = int_field(chosen, "factor_monomials")
    return {
        "public_zero_any": public_zero(source_row),
        "factor_zero_equals_selected": (
            public_zero(source_row)
            and factor_zero_leaf_count is not None
            and factor_zero_leaf_count == selected_leaf_count
        ),
        "selected_leaf_eq1_factor_zero_eq1": (
            public_zero(source_row)
            and selected_leaf_count == 1
            and factor_zero_leaf_count == 1
        ),
        "single_linear_factor_zero": (
            public_zero(source_row)
            and selected_leaf_count == 1
            and factor_zero_leaf_count == 1
            and total_degree == 1
        ),
        "single_trinomial_linear_factor_zero": (
            public_zero(source_row)
            and selected_leaf_count == 1
            and factor_zero_leaf_count == 1
            and total_degree == 1
            and (monomials if monomials is not None else 10**9) <= 3
        ),
    }


@dataclass(frozen=True)
class FrozenGuard:
    base_threshold: int
    delta: int
    feature: str
    kind: str
    name: str
    threshold: float

    @classmethod
    def from_p845(cls, payload: dict[str, Any]) -> "FrozenGuard":
        guard = payload["selected_guard"]["guard"]
        return cls(
            base_threshold=int(guard["base_threshold"]),
            delta=int(guard["delta"]),
            feature=str(guard["feature"]),
            kind=str(guard["kind"]),
            name=str(guard["name"]),
            threshold=float(guard["threshold"]),
        )

    def keep(self, row: dict[str, Any]) -> bool:
        if row.get("chosen_candidate") is None:
            return False
        features = row.get("public_candidate_features") or {}
        if self.kind != "global_le_slack":
            raise ValueError(f"unsupported guard kind {self.kind}")
        return float(features[self.feature]) <= self.threshold

    def as_json(self) -> dict[str, Any]:
        return {
            "base_threshold": self.base_threshold,
            "delta": self.delta,
            "feature": self.feature,
            "kind": self.kind,
            "name": self.name,
            "threshold": int(self.threshold) if self.threshold.is_integer() else self.threshold,
        }


def materialize_replay_rows(p843: dict[str, Any], p844: Any) -> list[dict[str, Any]]:
    selected_policy = str(p843["selected_policy"]["policy"])
    rows: list[dict[str, Any]] = []
    for source in p843["artifacts"]["sources"]:
        bank_id = str(source["bank_id"])
        role = str(source["role"])
        public_path = Path(source["path"])
        public_payload = load_json(public_path)
        params = public_payload.get("parameters") or {}
        sage_path = Path(params["sage_factor_source"])
        sage_payload = load_json(sage_path)
        surfaces_by_id = {
            str(surface["surface_id"]): surface
            for surface in sage_payload.get("surfaces") or []
        }

        for source_row in (public_payload.get("policy_rows") or {}).get(selected_policy) or []:
            chosen = source_row.get("chosen_candidate")
            chosen_dict = chosen if isinstance(chosen, dict) else None
            row: dict[str, Any] = {
                "bank_id": bank_id,
                "challenge_seed": source_row.get("challenge_seed"),
                "chosen_candidate": chosen_dict,
                "direct_source": params.get("direct_source"),
                "policy": selected_policy,
                "public_source": str(public_path),
                "role": role,
                "row_key": source_row.get("row_key"),
                "sage_factor_source": str(sage_path),
                "surface_id": source_row.get("surface_id"),
                "target": source_row.get("target"),
                "transfer_index": source_row.get("transfer_index"),
                "verifier_outcome": {
                    "below_rho": bool_field(source_row, "public_factor_quadratic_root_beats_rho"),
                    "false_positive": bool_field(source_row, "chosen_false_positive_source"),
                    "missing_selected_root_pair_count": len(source_row.get("missing_selected_root_pairs") or []),
                    "preserves_selected_root_pairs": bool_field(
                        source_row,
                        "quadratic_preserves_selected_root_pairs",
                    ),
                    "strict_success": bool(p844.strict_success(source_row)) if chosen_dict else False,
                },
            }

            if chosen_dict is not None:
                factor_index = int(chosen_dict["factor_index"])
                surface = surfaces_by_id.get(str(source_row["surface_id"]))
                if surface is None:
                    raise RuntimeError(f"missing surface {source_row['surface_id']} in {sage_path}")
                candidate = surface["sage_resultant_factor_candidates"][factor_index]
                factor = surface["sage_resultant_factorization"]["factors"][factor_index]
                row.update(
                    {
                        "factor_index": factor_index,
                        "factor_terms": factor_terms(factor),
                        "public_candidate_features": {
                            "factor_root_scan_ops": int(candidate["factor_root_scan_ops"]),
                            "full_remainder_ffe_ops_over_rho": float(
                                candidate["full_remainder_ffe_ops_over_rho"]
                            ),
                            "full_resultant_monomials": int(candidate["full_resultant_monomials"]),
                            "public_factor_quadratic_root_ops_over_rho": float(
                                source_row["public_factor_quadratic_root_ops_over_rho"]
                            ),
                            "remainder_monomials": int(candidate["remainder_monomials"]),
                            "surface_ffe_ops": int(candidate["surface_ffe_ops"]),
                        },
                        "public_replay_observables": {
                            "candidate_count": int_field(source_row, "candidate_count"),
                            "evaluated_factor_count": int_field(source_row, "evaluated_factor_count"),
                            "factor_fingerprint_term_count": int_field(
                                source_row,
                                "factor_fingerprint_term_count",
                            ),
                            "factor_monomials": int_field(chosen_dict, "factor_monomials"),
                            "factor_total_degree": int_field(chosen_dict, "factor_total_degree"),
                            "generic_rho_steps": int_field(source_row, "generic_rho_steps"),
                            "public_factor_quadratic_root_ops": int_field(
                                source_row,
                                "public_factor_quadratic_root_ops",
                            ),
                            "public_zero_recovered": bool_field(source_row, "public_zero_recovered"),
                            "recovered_root_count": int_field(source_row, "recovered_root_count"),
                            "selector_eval_ops": int_field(source_row, "selector_eval_ops"),
                            "source_factor_root_scan_ops": int_field(
                                source_row,
                                "source_factor_root_scan_ops",
                            ),
                            "surface_record_present": bool_field(source_row, "surface_record_present"),
                        },
                        "profile_flags": profile_flags(source_row),
                    }
                )
            else:
                row.update(
                    {
                        "factor_index": None,
                        "factor_terms": [],
                        "profile_flags": profile_flags(source_row),
                        "public_candidate_features": {},
                        "public_replay_observables": {
                            "candidate_count": int_field(source_row, "candidate_count"),
                            "evaluated_factor_count": int_field(source_row, "evaluated_factor_count"),
                            "public_zero_recovered": bool_field(source_row, "public_zero_recovered"),
                            "selector_eval_ops": int_field(source_row, "selector_eval_ops"),
                            "surface_record_present": bool_field(source_row, "surface_record_present"),
                        },
                    }
                )
            rows.append(row)
    return rows


def direct_packet_ready(row: dict[str, Any]) -> bool:
    observables = row.get("public_replay_observables") or {}
    return (
        row.get("chosen_candidate") is not None
        and bool(observables.get("surface_record_present"))
        and bool(observables.get("public_zero_recovered"))
        and int(observables.get("recovered_root_count") or 0) > 0
        and bool((row.get("profile_flags") or {}).get("single_trinomial_linear_factor_zero"))
    )


def materialized_linear_trinomial_public_zero_packet(row: dict[str, Any]) -> bool:
    observables = row.get("public_replay_observables") or {}
    return (
        row.get("chosen_candidate") is not None
        and bool(observables.get("surface_record_present"))
        and bool(observables.get("public_zero_recovered"))
        and int(observables.get("recovered_root_count") or 0) > 0
        and int(observables.get("factor_total_degree") or -1) == 1
        and int(observables.get("factor_monomials") or 10**9) <= 3
    )


def replay_packet(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "bank_id": row["bank_id"],
        "challenge_seed": row.get("challenge_seed"),
        "chosen_candidate_name": (row.get("chosen_candidate") or {}).get("candidate_name"),
        "direct_packet_ready": direct_packet_ready(row),
        "direct_source": row.get("direct_source"),
        "factor_index": row.get("factor_index"),
        "factor_terms": row.get("factor_terms") or [],
        "policy": row.get("policy"),
        "profile_flags": row.get("profile_flags") or {},
        "public_candidate_features": row.get("public_candidate_features") or {},
        "materialized_linear_trinomial_public_zero_packet": materialized_linear_trinomial_public_zero_packet(row),
        "public_replay_observables": row.get("public_replay_observables") or {},
        "public_source": row.get("public_source"),
        "role": row.get("role"),
        "row_key": row.get("row_key"),
        "sage_factor_source": row.get("sage_factor_source"),
        "surface_id": row.get("surface_id"),
        "target": row.get("target"),
        "transfer_index": row.get("transfer_index"),
        "verifier_outcome": row.get("verifier_outcome") or {},
    }


def summarize_split(rows: list[dict[str, Any]], guard: FrozenGuard, role: str) -> dict[str, Any]:
    role_rows = [row for row in rows if row["role"] == role]
    active = [row for row in role_rows if row.get("chosen_candidate") is not None]
    selected = [row for row in active if guard.keep(row)]
    ratios = [
        float((row.get("public_candidate_features") or {})["public_factor_quadratic_root_ops_over_rho"])
        for row in selected
    ]
    return {
        "active_count": len(active),
        "abstain_count": len(role_rows) - len(active),
        "below_rho_selected_count": sum(1 for row in selected if row["verifier_outcome"]["below_rho"]),
        "direct_packet_ready_count": sum(1 for row in selected if direct_packet_ready(row)),
        "false_positive_selected_count": sum(
            1 for row in selected if row["verifier_outcome"]["false_positive"]
        ),
        "materialized_linear_trinomial_public_zero_packet_count": sum(
            1 for row in selected if materialized_linear_trinomial_public_zero_packet(row)
        ),
        "missing_pair_event_selected_count": sum(
            int(row["verifier_outcome"]["missing_selected_root_pair_count"]) for row in selected
        ),
        "ops_over_rho": numeric_summary(ratios),
        "preserving_selected_count": sum(
            1 for row in selected if row["verifier_outcome"]["preserves_selected_root_pairs"]
        ),
        "role": role,
        "row_count": len(role_rows),
        "selected_by_public_guard_count": len(selected),
        "single_trinomial_linear_factor_zero_count": sum(
            1 for row in selected if (row.get("profile_flags") or {}).get("single_trinomial_linear_factor_zero")
        ),
        "strict_success_selected_count": sum(
            1 for row in selected if row["verifier_outcome"]["strict_success"]
        ),
    }


def p845_kept_keys(p845: dict[str, Any]) -> set[tuple[str, str, int, int | None]]:
    rows = (p845.get("rows") or {}).get("kept_strict_heldout") or []
    return {
        (str(row["bank_id"]), str(row["row_key"]), int(row["transfer_index"]), int(row["factor_index"]))
        for row in rows
    }


def determine_claim(heldout_summary: dict[str, Any], matches_p845: bool) -> str:
    selected = int(heldout_summary["selected_by_public_guard_count"])
    direct_ready = int(heldout_summary["direct_packet_ready_count"])
    materialized = int(heldout_summary["materialized_linear_trinomial_public_zero_packet_count"])
    strict = int(heldout_summary["strict_success_selected_count"])
    false_positive = int(heldout_summary["false_positive_selected_count"])
    below_rho = int(heldout_summary["below_rho_selected_count"])
    missing = int(heldout_summary["missing_pair_event_selected_count"])
    if (
        matches_p845
        and selected == 7
        and direct_ready == 7
        and strict == 7
        and below_rho == 7
        and false_positive == 0
        and missing == 0
    ):
        return "P846_PUBLIC_GUARDED_FACTOR_DIRECT_REPLAY_PACKETS_READY"
    if (
        matches_p845
        and selected == 7
        and materialized == 7
        and strict == 7
        and below_rho == 7
        and false_positive == 0
        and missing == 0
    ):
        return "P846_PUBLIC_GUARDED_FACTOR_REPLAY_HAS_ONE_MULTIROOT_PACKET"
    if selected and false_positive == 0 and strict == selected:
        return "P846_PUBLIC_GUARDED_FACTOR_REPLAY_PARTIAL_PACKET_READINESS"
    return "NEGATIVE_RESULT_P846_PUBLIC_GUARDED_FACTOR_REPLAY_NOT_READY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p844 = load_module("p844_public_guard_for_p846", P844_SCRIPT)
    p843 = load_json(args.p843)
    p845 = load_json(args.p845)
    guard = FrozenGuard.from_p845(p845)
    rows = materialize_replay_rows(p843, p844)
    selected_heldout = [
        row
        for row in rows
        if row["role"] == "heldout" and row.get("chosen_candidate") is not None and guard.keep(row)
    ]
    selected_keys = {key_tuple(row) for row in selected_heldout}
    p845_keys = p845_kept_keys(p845)
    matches_p845 = selected_keys == p845_keys
    calibration_summary = summarize_split(rows, guard, "calibration")
    heldout_summary = summarize_split(rows, guard, "heldout")
    claim = determine_claim(heldout_summary, matches_p845)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p843_source": str(args.p843),
            "p845_source": str(args.p845),
            "script": str(Path(__file__)),
        },
        "calibration_summary": calibration_summary,
        "claim_status": claim,
        "created_at": now_iso(),
        "guard": guard.as_json(),
        "heldout_summary": heldout_summary,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "PUBLIC-DECISION BOUNDARY: replay selection uses only the P843 public chosen candidate and the frozen P845 surface_ffe_ops guard.",
            "VERIFIER LABELS SEPARATED: preservation, false-positive, missing-pair, strict-success, and below-rho fields are reported as outcomes, not as selection inputs.",
            "DIRECT-REPLAY READINESS ONLY: packets identify direct-constructor inputs but do not certify relation equations or target descent.",
            "POLLARD-RHO BOUNDARY: this is relation-generation/root-recovery evidence, not a complete faster-than-rho ECDLP algorithm.",
            "NO DEPLOYED-CURVE CLAIM: no production-key relevance or deployed-prime break is implied.",
        ],
        "method": "p846_public_factor_direct_replay_readiness_audit",
        "parameters": {
            "forbidden_selection_fields": [
                "quadratic_preserves_selected_root_pairs",
                "public_factor_quadratic_root_beats_rho",
                "public_factor_quadratic_root_ops_over_rho",
                "chosen_false_positive_source",
                "missing_selected_root_pairs",
                "selected_valid_leaf_count",
                "factor_zero_leaf_count",
            ],
            "p843_claim": p843.get("claim_status"),
            "p845_claim": p845.get("claim_status"),
            "public_decision_fields": [
                "chosen_candidate exists under P843 policy",
                f"{guard.feature} <= {guard.threshold:g}",
            ],
            "selected_base_policy": p843["selected_policy"]["policy"],
            "success_threshold": (
                "replay exactly the seven P845 heldout packets, all direct-packet-ready, strict, "
                "below rho, false-positive-free, and missing-pair-free"
            ),
        },
        "p845_kept_key_match": {
            "matches": matches_p845,
            "p845_key_count": len(p845_keys),
            "replayed_key_count": len(selected_keys),
            "missing_from_replay": sorted([list(item) for item in p845_keys - selected_keys]),
            "unexpected_replay_keys": sorted([list(item) for item in selected_keys - p845_keys]),
        },
        "red_team_handoff": {
            "assumptions": [
                "The P843 policy's chosen candidate remains a valid public preselection primitive.",
                "A single linear/trinomial public factor-zero packet is an appropriate readiness condition for the next direct-constructor bridge.",
                "The tight P845 surface threshold is not just tuned to the current heldout banks.",
            ],
            "failure_modes": [
                "The packet may fail to produce independent relation equations in the direct constructor.",
                "Fresh disjoint banks may admit new false positives below surface_ffe_ops <= 64.",
                "Linear algebra rank or individual-log descent may erase the relation-generation gain.",
            ],
            "next_concrete_action": (
                "Build P847 to consume these seven replay packets in the direct relation-equation constructor "
                "and report certificate/rank outcomes; in parallel replicate the frozen guard on a fresh disjoint bank."
            ),
            "status": "HYPOTHESIS",
        },
        "replay_packets": [replay_packet(row) for row in selected_heldout],
        "schema": SCHEMA,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p843", type=Path, default=DEFAULT_P843)
    parser.add_argument("--p845", type=Path, default=DEFAULT_P845)
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
                "guard": payload["guard"],
                "heldout_summary": payload["heldout_summary"],
                "p845_kept_key_match": payload["p845_kept_key_match"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
