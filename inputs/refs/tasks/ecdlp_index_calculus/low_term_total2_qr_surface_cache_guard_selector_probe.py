#!/usr/bin/env python3
"""Select a public cache-reuse guard for live QR-surface kernels.

This probe follows P205's red-team next action.  It consumes live cache-kernel
artifacts, extracts only public/cache-ledger-visible group features, selects a
guard on prior windows, and reports the unchanged guard on a later held-out
window.  The selected guard is a route selector, not a solved ECDLP algorithm.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_KERNEL_SOURCES = [
    DEFAULT_STATE_DIR / "low_term_total2_qr_surface_live_cache_kernel_1024_1031_global_fingerprint_hash_accept_extra_probe.json",
    DEFAULT_STATE_DIR / "low_term_total2_qr_surface_live_cache_kernel_1032_1039_high_coeff_sum_accept_extra_probe.json",
    DEFAULT_STATE_DIR / "low_term_total2_qr_surface_live_cache_kernel_1040_1047_high_coeff_sum_accept_extra_probe.json",
]
DEFAULT_TEST_KERNEL_SOURCES = [
    DEFAULT_STATE_DIR / "low_term_total2_qr_surface_live_cache_kernel_1048_1055_high_coeff_sum_accept_extra_probe.json",
]
DEFAULT_OUT = DEFAULT_STATE_DIR / "low_term_total2_qr_surface_cache_guard_selector_1024_1047_train_to_1048_1055_probe.json"

GuardFn = Callable[[dict[str, Any]], bool]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def window_label(path: Path) -> str:
    match = re.search(r"(\d{4}_\d{4})", path.name)
    return match.group(1) if match else path.stem


def norm_pairs(value: Any) -> tuple[tuple[int, int], ...]:
    pairs = []
    for pair in value or []:
        if isinstance(pair, (list, tuple)) and len(pair) == 2:
            pairs.append((int_value(pair[0]), int_value(pair[1])))
    return tuple(sorted(pairs))


def group_key(group: dict[str, Any]) -> str:
    return f"{group.get('target')}@{group.get('transfer_index')}"


def public_duplicate_counts(group: dict[str, Any]) -> tuple[Counter[tuple[str, tuple[tuple[int, int], ...]]], Counter[tuple[tuple[int, int], ...]]]:
    hash_root: Counter[tuple[str, tuple[tuple[int, int], ...]]] = Counter()
    root_only: Counter[tuple[tuple[int, int], ...]] = Counter()
    for row in group.get("public_rows") or []:
        if not isinstance(row, dict) or not row.get("public_zero_recovered"):
            continue
        roots = norm_pairs(row.get("expected_root_pairs"))
        if not roots:
            continue
        selected_hash = str(row.get("selected_factor_hash") or "")
        root_only[roots] += 1
        if selected_hash:
            hash_root[(selected_hash, roots)] += 1
    return hash_root, root_only


def compact_group(path: Path, payload: dict[str, Any], group: dict[str, Any]) -> dict[str, Any]:
    hash_root_counts, root_counts = public_duplicate_counts(group)
    max_hash_root = max(hash_root_counts.values()) if hash_root_counts else 0
    max_root = max(root_counts.values()) if root_counts else 0
    duplicate_hash_roots = [
        {
            "selected_factor_hash": selected_hash,
            "expected_root_pairs": [[leaf, root] for leaf, root in roots],
            "count": count,
        }
        for (selected_hash, roots), count in sorted(hash_root_counts.items())
        if count >= 2
    ]
    return {
        "source": str(path),
        "window": window_label(path),
        "policy": payload.get("parameters", {}).get("policy"),
        "target": group.get("target"),
        "transfer_index": int_value(group.get("transfer_index")),
        "group_key": group_key(group),
        "rho": int_value(group.get("rho")),
        "scanner_union_verified": bool(group.get("scanner_union_public_key_verified")),
        "scanner_union_rank": int_value((group.get("scanner_union") or {}).get("union_rank")),
        "scanner_relation_count": int_value(group.get("scanner_relation_count")),
        "scanner_row_count": int_value(group.get("scanner_row_count")),
        "public_policy_row_count": int_value(group.get("public_policy_row_count")),
        "public_rejected_row_count": int_value(group.get("public_rejected_row_count")),
        "public_unique_root_count": int_value(group.get("public_unique_root_count")),
        "accepted_preserving_extra_root_row_count": int_value(
            group.get("accepted_preserving_extra_root_row_count")
        ),
        "public_cache_ops_over_rho": group.get("public_cache_ops_over_rho"),
        "public_strict_ops_over_rho": group.get("public_strict_ops_over_rho"),
        "cache_integrated_combined_ops_over_rho": group.get("cache_integrated_combined_ops_over_rho"),
        "strict_combined_ops_over_rho": group.get("strict_combined_ops_over_rho"),
        "cache_integrated_below_rho": bool(
            group.get("scanner_union_public_key_verified")
            and group.get("cache_integrated_combined_below_rho")
        ),
        "strict_combined_below_rho": bool(
            group.get("scanner_union_public_key_verified") and group.get("strict_combined_below_rho")
        ),
        "max_duplicate_hash_root_count": max_hash_root,
        "max_duplicate_root_count": max_root,
        "has_duplicate_hash_root": max_hash_root >= 2,
        "has_duplicate_root": max_root >= 2,
        "has_public_reject": int_value(group.get("public_rejected_row_count")) > 0,
        "has_accepted_preserving_extra_root": int_value(
            group.get("accepted_preserving_extra_root_row_count")
        )
        > 0,
        "duplicate_hash_roots": duplicate_hash_roots,
        "accepted_preserving_extra_root_row_keys": group.get("accepted_preserving_extra_root_row_keys") or [],
        "public_row_keys": [
            row.get("row_key") for row in group.get("public_rows") or [] if isinstance(row, dict)
        ],
        "scanner_row_keys": [
            row.get("row_key") for row in group.get("scanner_rows") or [] if isinstance(row, dict)
        ],
    }


def load_groups(paths: list[Path]) -> list[dict[str, Any]]:
    groups = []
    for path in paths:
        payload = load_json(path)
        for group in payload.get("groups") or []:
            if isinstance(group, dict):
                groups.append(compact_group(path, payload, group))
    return groups


def load_test_groups(paths: list[Path], allow_missing: bool) -> tuple[list[dict[str, Any]], list[str]]:
    groups = []
    missing_sources = []
    for path in paths:
        if not path.exists():
            if allow_missing:
                missing_sources.append(str(path))
                continue
            raise FileNotFoundError(path)
        payload = load_json(path)
        for group in payload.get("groups") or []:
            if isinstance(group, dict):
                groups.append(compact_group(path, payload, group))
    return groups, missing_sources


def guard_no_guard(group: dict[str, Any]) -> bool:
    return True


def guard_duplicate_hash_root(group: dict[str, Any]) -> bool:
    return bool(group.get("has_duplicate_hash_root"))


def guard_duplicate_hash_root_no_reject(group: dict[str, Any]) -> bool:
    return bool(group.get("has_duplicate_hash_root") and not group.get("has_public_reject"))


def guard_duplicate_hash_root_no_reject_public_strict_lt_rho(group: dict[str, Any]) -> bool:
    return bool(
        guard_duplicate_hash_root_no_reject(group)
        and number(group.get("public_strict_ops_over_rho"), 999.0) < 1.0
    )


def guard_duplicate_hash_root_no_reject_public_cache_lt_rho(group: dict[str, Any]) -> bool:
    return bool(
        guard_duplicate_hash_root_no_reject(group)
        and number(group.get("public_cache_ops_over_rho"), 999.0) < 1.0
    )


def guard_duplicate_hash_root_no_reject_public_cache_lt_rho_no_accepted_extra(
    group: dict[str, Any],
) -> bool:
    return bool(
        guard_duplicate_hash_root_no_reject_public_cache_lt_rho(group)
        and not group.get("has_accepted_preserving_extra_root")
    )


def guard_duplicate_hash_root_no_reject_public_cache_lt_rho_unique_root(
    group: dict[str, Any],
) -> bool:
    return bool(
        guard_duplicate_hash_root_no_reject_public_cache_lt_rho(group)
        and int_value(group.get("public_unique_root_count")) == 1
    )


def guard_accepted_extra(group: dict[str, Any]) -> bool:
    return bool(group.get("has_accepted_preserving_extra_root"))


def guard_accepted_extra_duplicate_hash_root(group: dict[str, Any]) -> bool:
    return bool(group.get("has_accepted_preserving_extra_root") and group.get("has_duplicate_hash_root"))


def guard_accepted_extra_duplicate_hash_root_no_reject(group: dict[str, Any]) -> bool:
    return bool(
        group.get("has_accepted_preserving_extra_root")
        and group.get("has_duplicate_hash_root")
        and not group.get("has_public_reject")
    )


def guard_accepted_extra_duplicate_hash_root_no_reject_public_cache_lt_rho(group: dict[str, Any]) -> bool:
    return bool(
        guard_accepted_extra_duplicate_hash_root_no_reject(group)
        and number(group.get("public_cache_ops_over_rho"), 999.0) < 1.0
    )


def guard_accepted_extra_or_duplicate_hash_root_no_reject_public_strict_lt_rho(
    group: dict[str, Any],
) -> bool:
    return bool(
        guard_accepted_extra_duplicate_hash_root_no_reject(group)
        or guard_duplicate_hash_root_no_reject_public_strict_lt_rho(group)
    )


GUARDS: dict[str, GuardFn] = {
    "no_guard_all_groups": guard_no_guard,
    "duplicate_hash_root": guard_duplicate_hash_root,
    "duplicate_hash_root_no_public_reject": guard_duplicate_hash_root_no_reject,
    "duplicate_hash_root_no_public_reject_public_strict_lt_rho": (
        guard_duplicate_hash_root_no_reject_public_strict_lt_rho
    ),
    "duplicate_hash_root_no_public_reject_public_cache_lt_rho": (
        guard_duplicate_hash_root_no_reject_public_cache_lt_rho
    ),
    "duplicate_hash_root_no_public_reject_public_cache_lt_rho_no_accepted_extra": (
        guard_duplicate_hash_root_no_reject_public_cache_lt_rho_no_accepted_extra
    ),
    "duplicate_hash_root_no_public_reject_public_cache_lt_rho_unique_root": (
        guard_duplicate_hash_root_no_reject_public_cache_lt_rho_unique_root
    ),
    "accepted_extra": guard_accepted_extra,
    "accepted_extra_duplicate_hash_root": guard_accepted_extra_duplicate_hash_root,
    "accepted_extra_duplicate_hash_root_no_public_reject": guard_accepted_extra_duplicate_hash_root_no_reject,
    "accepted_extra_duplicate_hash_root_no_public_reject_public_cache_lt_rho": (
        guard_accepted_extra_duplicate_hash_root_no_reject_public_cache_lt_rho
    ),
    "accepted_extra_or_duplicate_hash_root_no_public_reject_public_strict_lt_rho": (
        guard_accepted_extra_or_duplicate_hash_root_no_reject_public_strict_lt_rho
    ),
}

GUARD_SPECIFICITY = {
    "no_guard_all_groups": 0,
    "duplicate_hash_root": 1,
    "accepted_extra": 1,
    "duplicate_hash_root_no_public_reject": 2,
    "duplicate_hash_root_no_public_reject_public_strict_lt_rho": 3,
    "duplicate_hash_root_no_public_reject_public_cache_lt_rho": 3,
    "accepted_extra_duplicate_hash_root": 3,
    # This is the P205 mechanism-specific guard.  The public-cache threshold
    # variant is kept as a candidate but ranked lower to avoid promoting a
    # numeric cutoff on the small calibration bank unless it earns a real edge.
    "accepted_extra_duplicate_hash_root_no_public_reject_public_cache_lt_rho": 3,
    "duplicate_hash_root_no_public_reject_public_cache_lt_rho_unique_root": 4,
    "accepted_extra_duplicate_hash_root_no_public_reject": 4,
    "duplicate_hash_root_no_public_reject_public_cache_lt_rho_no_accepted_extra": 5,
    "accepted_extra_or_duplicate_hash_root_no_public_reject_public_strict_lt_rho": 5,
}


def evaluate_guard(name: str, groups: list[dict[str, Any]]) -> dict[str, Any]:
    guard = GUARDS[name]
    selected = [group for group in groups if guard(group)]
    positives = [group for group in groups if group.get("cache_integrated_below_rho")]
    true_pos = [group for group in selected if group.get("cache_integrated_below_rho")]
    false_pos = [group for group in selected if not group.get("cache_integrated_below_rho")]
    false_neg = [group for group in positives if not guard(group)]
    verified_selected = [group for group in selected if group.get("scanner_union_verified")]
    min_cache = (
        min(number(group.get("cache_integrated_combined_ops_over_rho"), 999.0) for group in selected)
        if selected
        else None
    )
    return {
        "guard": name,
        "group_count": len(groups),
        "selected_count": len(selected),
        "selected_verified_count": len(verified_selected),
        "cache_below_rho_count": len(positives),
        "true_positive_count": len(true_pos),
        "false_positive_count": len(false_pos),
        "false_negative_count": len(false_neg),
        "precision": ratio(len(true_pos), len(selected)),
        "recall": ratio(len(true_pos), len(positives)),
        "min_selected_cache_integrated_ops_over_rho": min_cache,
        "selected_groups": selected,
        "false_positive_groups": false_pos,
        "false_negative_groups": false_neg,
    }


def score_row(row: dict[str, Any]) -> list[Any]:
    no_support = row["true_positive_count"] == 0
    return [
        row["false_positive_count"],
        1 if no_support else 0,
        -row["true_positive_count"],
        row["false_negative_count"],
        row["selected_count"],
        -GUARD_SPECIFICITY.get(str(row["guard"]), 0),
        row["guard"],
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-kernel-sources", nargs="+", type=Path, default=DEFAULT_TRAIN_KERNEL_SOURCES)
    parser.add_argument("--test-kernel-sources", nargs="+", type=Path, default=DEFAULT_TEST_KERNEL_SOURCES)
    parser.add_argument(
        "--force-selected-guard",
        choices=sorted(GUARDS),
        default="",
        help="Freeze this guard after external/prior evidence instead of selecting the top training score.",
    )
    parser.add_argument(
        "--allow-missing-test-sources",
        action="store_true",
        help="Permit absent test artifacts so the selected guard can be pre-registered before a future window exists.",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    train_groups = load_groups(args.train_kernel_sources)
    test_groups, missing_test_sources = load_test_groups(
        args.test_kernel_sources,
        args.allow_missing_test_sources,
    )
    train_scores = [evaluate_guard(name, train_groups) for name in GUARDS]
    for row in train_scores:
        row["score_tuple"] = score_row(row)
    train_scores.sort(key=lambda row: row["score_tuple"])
    selected_guard = args.force_selected_guard or (train_scores[0]["guard"] if train_scores else None)
    selected_training_score = next(
        (row for row in train_scores if row.get("guard") == selected_guard),
        None,
    )
    test_score = evaluate_guard(selected_guard, test_groups) if selected_guard else None
    test_scores = [evaluate_guard(name, test_groups) for name in GUARDS] if test_groups else []
    payload = {
        "schema": "low_term_total2_qr_surface_cache_guard_selector_v1",
        "created_at": now_iso(),
        "method": "prior_window_public_cache_reuse_guard_selection",
        "parameters": {
            "train_kernel_sources": [str(path) for path in args.train_kernel_sources],
            "test_kernel_sources": [str(path) for path in args.test_kernel_sources],
            "allow_missing_test_sources": bool(args.allow_missing_test_sources),
            "missing_test_sources": missing_test_sources,
            "force_selected_guard": args.force_selected_guard,
            "candidate_guards": list(GUARDS),
            "score_order": [
                "min_false_positive_count",
                "require_training_true_positive_support",
                "max_training_true_positive_count",
                "min_false_negative_count",
                "min_selected_count",
                "guard_name_tiebreak",
            ],
        },
        "selection_mode": "forced" if args.force_selected_guard else "training_score",
        "selected_guard": selected_guard,
        "selected_training_score": selected_training_score,
        "top_training_score": train_scores[0] if train_scores else None,
        "training_scores": train_scores,
        "heldout_score": test_score,
        "heldout_scores": test_scores,
        "honesty_boundary": [
            "The guard uses live cache-kernel artifacts and is therefore a route-selection audit, not an integrated generator.",
            "Selection uses prior windows only; the held-out score is reported after the guard is frozen.",
            "Cache-integrated below-rho is model-bound and must still be compared with fused, strict, all-policy, and rejected-row controls.",
        ],
    }
    write_json(args.out, payload)
    print(json.dumps({"selected_guard": selected_guard, "heldout_score": test_score}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
