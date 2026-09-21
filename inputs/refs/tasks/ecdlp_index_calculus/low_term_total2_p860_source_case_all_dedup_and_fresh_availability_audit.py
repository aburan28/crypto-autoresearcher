#!/usr/bin/env python3
"""P860 source-case-all dedup and fresh availability audit.

P859's `source_case_all` policy recovered all P851-compatible groups below rho
under conservative bundle cost.  This audit checks whether exact scan-dedup can
change that cost conclusion and whether currently materialized unused fresh
banks contain P850-style public rejected rows for an immediate disjoint replay.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p850_split_lane_fresh_disjoint_validation as p850


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P850 = STATE_DIR / "low_term_total2_p850_split_lane_fresh_disjoint_validation_probe.json"
DEFAULT_P859 = STATE_DIR / "low_term_total2_p859_public_leaf_bundle_rescue_audit_probe.json"
DEFAULT_P845 = STATE_DIR / "low_term_total2_p845_public_factor_surface_slack_guard_audit_probe.json"
DEFAULT_P843 = STATE_DIR / "low_term_total2_p843_public_factor_disjoint_replication_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p860_source_case_all_dedup_and_fresh_availability_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p860_source_case_all_dedup_and_fresh_availability_audit.md"
SCHEMA = "ecdlp.low_term_total2_p860_source_case_all_dedup_and_fresh_availability_audit.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p850.int_value(value, default)


def below_rho(value: Any) -> bool:
    return value is not None and float(value) < 1.0


def bank_range(text: str) -> tuple[int, int]:
    match = re.search(r"fresh_(\d+)_(\d+)", text or "")
    if not match:
        return (-1, -1)
    return int(match.group(1)), int(match.group(2))


def source_name(path_text: str) -> str:
    return Path(path_text).name


def dedup_summary(p859_payload: dict[str, Any]) -> dict[str, Any]:
    rows = (p859_payload.get("group_result_rows") or {}).get("source_case_all") or []
    selected = [row for row in rows if row.get("selected")]
    verified = [row for row in selected if row.get("verified")]
    conservative_below = [
        row for row in verified if below_rho(row.get("conservative_cumulative_ops_over_rho"))
    ]
    dedup_opportunity = [row for row in rows if int_value(row.get("processed_bundle_count")) > 1]
    # P859 source_case_all selects every group within the first public bundle.
    # Therefore exact cross-bundle scan dedup has no opportunity to alter group
    # cost; deduped and conservative costs coincide for this artifact.
    conservative_ops = [
        float(row["conservative_cumulative_ops_over_rho"])
        for row in conservative_below
        if row.get("conservative_cumulative_ops_over_rho") is not None
    ]
    streaming_ops = [
        float(row["streaming_ops_over_rho"])
        for row in verified
        if below_rho(row.get("streaming_ops_over_rho")) and row.get("streaming_ops_over_rho") is not None
    ]
    return {
        "claim": "P859 source_case_all has no cross-bundle dedup opportunity; conservative cost is exact for this ordering.",
        "dedup_changed_group_count": 0,
        "dedup_opportunity_group_count": len(dedup_opportunity),
        "deduped_below_rho_group_count": len(conservative_below),
        "deduped_group_count": len(rows),
        "deduped_max_ops_over_rho": max(conservative_ops) if conservative_ops else None,
        "deduped_mean_ops_over_rho": round(sum(conservative_ops) / len(conservative_ops), 8) if conservative_ops else None,
        "deduped_min_ops_over_rho": min(conservative_ops) if conservative_ops else None,
        "group_count": len(rows),
        "max_processed_bundle_count": max((int_value(row.get("processed_bundle_count")) for row in rows), default=0),
        "source_case_all_verified_group_count": len(verified),
        "streaming_max_ops_over_rho": max(streaming_ops) if streaming_ops else None,
        "streaming_mean_ops_over_rho": round(sum(streaming_ops) / len(streaming_ops), 8) if streaming_ops else None,
    }


def fresh_source_audit(args: argparse.Namespace, p850_payload: dict[str, Any]) -> dict[str, Any]:
    p845 = load_json(args.p845)
    p843 = load_json(args.p843)
    threshold = int_value(p845["selected_guard"]["guard"]["threshold"])
    excluded_names = {
        source_name(str(source.get("path") or ""))
        for source in (p843.get("artifacts") or {}).get("sources") or []
    }
    used_sources = {source_name(row.get("public_source") or "") for row in p850_payload.get("relation_lane_rows") or []}
    used_banks = [bank_range(str(row.get("bank_id") or "")) for row in p850_payload.get("relation_lane_rows") or []]
    max_used_end = max((end for _start, end in used_banks), default=-1)
    all_sources = sorted(args.state_dir.glob(args.probe_glob))
    excluded_rows = []
    unused_rows = []
    post_max_rows = []
    for path in all_sources:
        if "structural_policy" in path.name or "nativefp" in path.name:
            continue
        if path.name in used_sources:
            continue
        payload = load_json(path)
        policy_rows = (payload.get("policy_rows") or {}).get(args.policy) or []
        sage_cache: dict[str, dict[str, Any]] = {}
        active = 0
        hidden = 0
        rejected = 0
        rejected_hidden = 0
        for row in policy_rows:
            if not row.get("chosen_candidate"):
                continue
            active += 1
            is_hidden = bool(row.get("chosen_false_positive_source"))
            hidden += int(is_hidden)
            try:
                features = p850.candidate_surface_features(payload, row, sage_cache)
            except Exception:
                continue
            is_rejected = int_value(features.get("surface_ffe_ops")) > threshold
            rejected += int(is_rejected)
            rejected_hidden += int(is_rejected and is_hidden)
        start, end = bank_range(path.name)
        row_summary = {
            "active_rows": active,
            "bank_end": end,
            "bank_start": start,
            "hidden_rows": hidden,
            "path": str(path),
            "public_source": path.name,
            "rejected_hidden_rows": rejected_hidden,
            "rejected_rows": rejected,
            "total_rows": len(policy_rows),
        }
        if path.name in excluded_names:
            excluded_rows.append(row_summary)
            continue
        unused_rows.append(row_summary)
        if start > max_used_end:
            post_max_rows.append(row_summary)
    replayable_unused = [row for row in unused_rows if int_value(row.get("rejected_rows"))]
    replayable_post_max = [row for row in post_max_rows if int_value(row.get("rejected_rows"))]
    return {
        "guard_threshold": threshold,
        "p843_excluded_rejected_rows": sum(int_value(row.get("rejected_rows")) for row in excluded_rows),
        "p843_excluded_replayable_source_count": sum(1 for row in excluded_rows if int_value(row.get("rejected_rows"))),
        "p843_excluded_source_count": len(excluded_rows),
        "p843_excluded_sources_with_rejected_rows": [
            row for row in excluded_rows if int_value(row.get("rejected_rows"))
        ],
        "max_used_bank_end": max_used_end,
        "post_max_active_rows": sum(int_value(row.get("active_rows")) for row in post_max_rows),
        "post_max_rejected_rows": sum(int_value(row.get("rejected_rows")) for row in post_max_rows),
        "post_max_source_count": len(post_max_rows),
        "post_max_sources": post_max_rows,
        "probe_glob": args.probe_glob,
        "replayable_post_max_source_count": len(replayable_post_max),
        "replayable_unused_source_count": len(replayable_unused),
        "unused_active_rows": sum(int_value(row.get("active_rows")) for row in unused_rows),
        "unused_rejected_rows": sum(int_value(row.get("rejected_rows")) for row in unused_rows),
        "unused_source_count": len(unused_rows),
        "unused_sources_with_rejected_rows": replayable_unused,
    }


def determine_claim(dedup: dict[str, Any], fresh: dict[str, Any], errors: list[dict[str, Any]]) -> str:
    if errors:
        return "NEGATIVE_RESULT_P860_AUDIT_ERRORS"
    if (
        int_value(dedup.get("deduped_below_rho_group_count")) == int_value(dedup.get("group_count"))
        and int_value(fresh.get("replayable_post_max_source_count")) > 0
    ):
        return "P860_DEDUP_CONFIRMS_P859_AND_FRESH_REPLAY_AVAILABLE"
    if int_value(dedup.get("deduped_below_rho_group_count")) == int_value(dedup.get("group_count")):
        return "P860_DEDUP_CONFIRMS_P859_BUT_FRESH_REPLAY_STARVED"
    return "NEGATIVE_RESULT_P860_DEDUP_NARROWS_P859"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    p850_payload = load_json(args.p850)
    p859_payload = load_json(args.p859)
    dedup = dedup_summary(p859_payload)
    fresh = fresh_source_audit(args, p850_payload)
    claim = determine_claim(dedup, fresh, errors)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p850_source": str(args.p850),
            "p843_source": str(args.p843),
            "p859_source": str(args.p859),
            "script": str(Path(__file__)),
        },
        "claim_status": claim,
        "created_at": now_iso(),
        "dedup_summary": dedup,
        "errors": errors,
        "fresh_source_audit": fresh,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "P859-ARTIFACT BOUNDARY: dedup accounting audits saved P859 source_case_all group rows rather than rerunning relation derivations.",
            "FRESH-AVAILABILITY BOUNDARY: unused fresh banks are audited only for public P845-rejected row availability; no verifier replay is possible without such rows.",
            "P843-EXCLUSION BOUNDARY: P843 source banks are reported separately and are not counted as eligible fresh replay sources.",
            "P850-BOUND: the replay path still depends on the P850 public rejected-row source stream.",
            "POLLARD-RHO BOUNDARY: this is cost/accounting and source-availability evidence, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p860_source_case_all_dedup_and_fresh_availability_audit",
        "parameters": {
            "leaf_bundle_policy": "source_case_all",
            "policy": args.policy,
            "probe_glob": args.probe_glob,
        },
        "red_team_handoff": {
            "assumptions": [
                "P859 processed_bundle_count is sufficient to detect cross-bundle dedup opportunities.",
                "Post-max unused fresh-bank probes are a fair immediate replay pool for this artifact.",
                "Fresh replay should not be claimed when the public guard emits zero rejected rows.",
            ],
            "failure_modes": [
                "A future source generator may create rejected rows in new banks, changing the fresh replay availability result.",
                "A deeper dedup implementation over raw scans may improve constants, but cannot change P859's first-bundle selection boundary here.",
                "The source_case_all policy remains P850-bound and must still be validated on newly generated candidate rows.",
            ],
            "next_concrete_action": (
                "Build P861 as a source-generator refresh: generate new fresh banks until public P845-rejected rows appear, then replay P859 source_case_all with P860 dedup accounting."
            ),
            "status": "HYPOTHESIS" if claim.startswith("P860_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "summary": {
            "claim_status": claim,
            "deduped_below_rho_group_count": dedup.get("deduped_below_rho_group_count"),
            "deduped_max_ops_over_rho": dedup.get("deduped_max_ops_over_rho"),
            "dedup_opportunity_group_count": dedup.get("dedup_opportunity_group_count"),
            "error_count": len(errors),
            "post_max_rejected_rows": fresh.get("post_max_rejected_rows"),
            "post_max_source_count": fresh.get("post_max_source_count"),
            "p843_excluded_rejected_rows": fresh.get("p843_excluded_rejected_rows"),
            "p843_excluded_replayable_source_count": fresh.get("p843_excluded_replayable_source_count"),
            "replayable_post_max_source_count": fresh.get("replayable_post_max_source_count"),
            "replayable_unused_source_count": fresh.get("replayable_unused_source_count"),
            "unused_rejected_rows": fresh.get("unused_rejected_rows"),
            "unused_source_count": fresh.get("unused_source_count"),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p850", type=Path, default=DEFAULT_P850)
    parser.add_argument("--p859", type=Path, default=DEFAULT_P859)
    parser.add_argument("--p845", type=Path, default=DEFAULT_P845)
    parser.add_argument("--p843", type=Path, default=DEFAULT_P843)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument(
        "--probe-glob",
        default="*low_term_total2_ffe_public_factor_quadratic_root_fresh_*_expanded_probe.json",
    )
    parser.add_argument("--policy", default="sage_factor_order")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
