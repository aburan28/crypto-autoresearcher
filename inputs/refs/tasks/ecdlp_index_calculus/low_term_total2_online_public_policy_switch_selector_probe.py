#!/usr/bin/env python3
"""Select an online QR policy from public QR summaries.

The live fused selector intentionally freezes a single policy from prior scalar
outcomes.  The P225 drift suggests a different public rule: after public QR
factor scoring for the current window, choose the clean low-charge policy from a
fixed candidate set, then run the online Sage-recomputed QR stop gate for that
policy.  This probe records that rule and, when online artifacts are supplied,
evaluates whether the public choice reaches scalar materialization below rho.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CANDIDATES = (
    "high_coeff_sum",
    "minsum_low_degree_low_high_constant",
    "low_constant",
)
DEFAULT_OUT = (
    DEFAULT_STATE_DIR
    / "low_term_total2_online_public_policy_switch_selector_probe.json"
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def parse_paths(raw: str | None) -> list[Path]:
    if not raw:
        return []
    return [Path(part.strip()) for part in raw.split(",") if part.strip()]


def parse_list(raw: str | None, default: tuple[str, ...]) -> list[str]:
    if not raw:
        return list(default)
    return [part.strip() for part in raw.split(",") if part.strip()]


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 10**12) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def window_label(path: Path) -> str:
    match = re.search(r"(\d+_\d+)", path.name)
    return match.group(1) if match else path.stem


def public_summary(path: Path) -> dict[str, Any]:
    data = load_json(path)
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else data
    return summary if isinstance(summary, dict) else {}


def policy_summary(summary: dict[str, Any], policy: str) -> dict[str, Any]:
    summaries = summary.get("policy_summaries")
    if isinstance(summaries, dict) and isinstance(summaries.get(policy), dict):
        return summaries[policy]
    return {}


def public_score(row: dict[str, Any], policy: str) -> tuple[Any, ...]:
    false_pos = int_value(row.get("quadratic_false_positive_surface_count"))
    mismatch = int_value(row.get("quadratic_mismatch_surface_count"))
    preserving = int_value(row.get("quadratic_preserving_surface_count"))
    recovered = int_value(row.get("recovered_surface_count"))
    charged_below = int_value(row.get("charged_below_rho_count"))
    source_preserving = int_value(row.get("source_preserving_surface_count"))
    eligible = bool(
        row
        and source_preserving > 0
        and recovered > 0
        and false_pos == 0
        and mismatch == 0
    )
    return (
        0 if eligible else 1,
        false_pos,
        mismatch,
        -preserving,
        -charged_below,
        float_value(row.get("max_charged_ops_over_rho")),
        float_value(row.get("mean_charged_ops_over_rho")),
        float_value(row.get("mean_selector_eval_ops")),
        policy,
    )


def choose_policy(summary: dict[str, Any], candidates: list[str]) -> dict[str, Any]:
    rows = []
    for policy in candidates:
        ps = policy_summary(summary, policy)
        rows.append(
            {
                "policy": policy,
                "public_summary": ps,
                "score": list(public_score(ps, policy)),
            }
        )
    rows.sort(key=lambda row: tuple(row["score"]))
    selected = rows[0] if rows else None
    abstain_reason = None
    selected_policy = selected.get("policy") if selected else None
    selected_public_summary = selected.get("public_summary") if selected else None
    if not selected:
        abstain_reason = "ABSTAIN_NO_PUBLIC_QR_POLICY"
        selected_policy = None
        selected_public_summary = None
    elif selected["score"][0] != 0:
        abstain_reason = "ABSTAIN_NO_CLEAN_PUBLIC_QR_POLICY"
        selected_policy = None
        selected_public_summary = None
    return {
        "selected_policy": selected_policy,
        "abstain_reason": abstain_reason,
        "best_ranked_policy": selected.get("policy") if selected else None,
        "ranked_policies": rows,
        "selected_public_summary": selected_public_summary,
    }


def ratio_from_stop(row: dict[str, Any] | None) -> float:
    if not isinstance(row, dict):
        return 10**12
    return float_value(row.get("charged_source_attempt_ops_over_rho"))


def online_summary_for(data: dict[str, Any], policy: str) -> dict[str, Any]:
    replays = data.get("replays")
    if not isinstance(replays, dict):
        return {}
    candidates: list[dict[str, Any]] = []
    for key, replay in replays.items():
        summary = replay.get("summary") if isinstance(replay, dict) else None
        if not isinstance(summary, dict) or summary.get("policy") != policy:
            continue
        best_below = (summary.get("best_below_rho_stops") or [None])[0]
        best_scalar = (summary.get("best_scalar_stops") or [None])[0]
        candidates.append(
            {
                "key": key,
                "summary": summary,
                "best_below": best_below,
                "best_scalar": best_scalar,
                "score": [
                    -int_value(summary.get("below_rho_scalar_stop_count")),
                    -int_value(summary.get("scalar_stop_count")),
                    ratio_from_stop(best_below),
                    ratio_from_stop(best_scalar),
                    str(summary.get("order") or ""),
                ],
            }
        )
    candidates.sort(key=lambda row: tuple(row["score"]))
    selected = candidates[0] if candidates else None
    return {
        "policy": policy,
        "selected_replay_key": selected.get("key") if selected else None,
        "selected_replay_summary": selected.get("summary") if selected else None,
        "best_below": selected.get("best_below") if selected else None,
        "best_scalar": selected.get("best_scalar") if selected else None,
        "ranked_replays": candidates,
    }


def evaluate_pair(public_path: Path, online_path: Path | None, candidates: list[str]) -> dict[str, Any]:
    summary = public_summary(public_path)
    choice = choose_policy(summary, candidates)
    selected_policy = choice.get("selected_policy")
    result = {
        "window": window_label(public_path),
        "public_source": str(public_path),
        "online_source": str(online_path) if online_path else None,
        "public_best_policy": summary.get("best_policy"),
        **choice,
    }
    if online_path and selected_policy:
        result["online_evaluation"] = online_summary_for(load_json(online_path), selected_policy)
    if online_path and choice.get("best_ranked_policy"):
        result["best_ranked_online_evaluation"] = online_summary_for(
            load_json(online_path), choice["best_ranked_policy"]
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-public-sources", default="")
    parser.add_argument("--train-online-sources", default="")
    parser.add_argument("--test-public-source", type=Path)
    parser.add_argument("--test-online-source", type=Path)
    parser.add_argument("--candidate-policies", default=",".join(DEFAULT_CANDIDATES))
    parser.add_argument("--test-window", default="")
    parser.add_argument("--allow-missing-test-sources", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    candidates = parse_list(args.candidate_policies, DEFAULT_CANDIDATES)
    train_public = parse_paths(args.train_public_sources)
    train_online = parse_paths(args.train_online_sources)
    if train_online and len(train_online) != len(train_public):
        raise ValueError("--train-online-sources must match train public source count")

    train_results = [
        evaluate_pair(public_path, train_online[index] if train_online else None, candidates)
        for index, public_path in enumerate(train_public)
    ]

    test_result = None
    if args.test_public_source:
        if not args.test_public_source.exists() and not args.allow_missing_test_sources:
            raise FileNotFoundError(args.test_public_source)
        if args.test_public_source.exists():
            test_online = args.test_online_source if args.test_online_source and args.test_online_source.exists() else None
            if args.test_online_source and not args.test_online_source.exists() and not args.allow_missing_test_sources:
                raise FileNotFoundError(args.test_online_source)
            test_result = evaluate_pair(args.test_public_source, test_online, candidates)
    elif args.test_window:
        test_result = {
            "window": args.test_window,
            "status": "PREREGISTERED_RULE_AWAITING_PUBLIC_QR_SOURCE",
            "selected_rule": "choose_clean_public_qr_policy_by_recovery_then_charge",
        }

    output = {
        "schema": "ecdlp.low_term_total2_online_public_policy_switch_selector.v3",
        "candidate_policies": candidates,
        "selected_rule": "choose_clean_public_qr_policy_by_recovery_then_charge_else_abstain",
        "rule_sort_order": [
            "eligible clean recovered policies first",
            "fewest false positives",
            "fewest mismatches",
            "most preserving surfaces",
            "most charged-below-rho surfaces",
            "lowest max charged ops/rho",
            "lowest mean charged ops/rho",
            "lowest mean selector eval ops",
            "policy name tie-break",
        ],
        "train_results": train_results,
        "test_result": test_result,
        "summary": {
            "train_window_count": len(train_results),
            "train_selected_policy_counts": {
                policy: sum(1 for row in train_results if row.get("selected_policy") == policy)
                for policy in candidates
            },
            "train_abstain_count": sum(1 for row in train_results if row.get("abstain_reason")),
            "test_window": (test_result or {}).get("window"),
            "test_selected_policy": (test_result or {}).get("selected_policy"),
            "test_best_ranked_policy": (test_result or {}).get("best_ranked_policy"),
            "test_abstain_reason": (test_result or {}).get("abstain_reason"),
            "test_online_below_rho": bool(
                (((test_result or {}).get("online_evaluation") or {}).get("best_below"))
            ),
            "test_best_ranked_online_below_rho": bool(
                (((test_result or {}).get("best_ranked_online_evaluation") or {}).get("best_below"))
            ),
            "honesty_boundary": [
                "The policy choice uses public QR aggregate summaries, not scalar labels.",
                "When an online source is supplied, scalar success is evaluation-only.",
                "If every candidate has public QR false-positive or mismatch risk, the selector abstains.",
                "The selector still depends on public QR materialization; a later generator must charge this rule in one online artifact.",
            ],
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
