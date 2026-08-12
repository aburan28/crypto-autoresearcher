#!/usr/bin/env python3
"""P807 richer public-feature classifier for requested support-pair derivation."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P806_SCRIPT = TASK_DIR / "low_term_total2_p806_public_feature_classifier.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p807_richer_public_feature_classifier_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p807_richer_public_feature_classifier.md"
SCHEMA = "ecdlp.low_term_total2_p807_richer_public_feature_classifier.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def slug(value: str) -> str:
    text = "".join(ch if ch.isalnum() else "_" for ch in str(value))
    return "_".join(part for part in text.split("_") if part)


def bounded_bin(value: int, modulus: int, bins: int) -> int:
    if modulus <= 0:
        return 0
    return max(0, min(int(bins) - 1, int(value) * int(bins) // int(modulus)))


def index_bin(value: int, size: int, bins: int) -> int:
    return bounded_bin(int(value), max(1, int(size)), int(bins))


def point_x(point: Any, p: int) -> int:
    if point is None:
        return int(p)
    return int(point[0]) % int(p)


def point_y(point: Any, p: int) -> int:
    if point is None:
        return int(p)
    return int(point[1]) % int(p)


def inv_mod(value: int, p: int) -> int | None:
    value %= int(p)
    if value == 0:
        return None
    return pow(value, -1, int(p))


def line_features(left_point: Any, right_point: Any, ainvs: list[int], p: int, bins: int) -> tuple[str, ...]:
    if left_point is None or right_point is None:
        return ("line_infinity=1",)
    a1, a2, a3, a4, _a6 = [int(value) % int(p) for value in ainvs]
    x1, y1 = int(left_point[0]) % int(p), int(left_point[1]) % int(p)
    x2, y2 = int(right_point[0]) % int(p), int(right_point[1]) % int(p)
    if x1 == x2 and (y1 + y2 + a1 * x2 + a3) % int(p) == 0:
        return ("line_vertical=1", f"line_x_bin={bounded_bin(x1, p, bins)}")
    if x1 == x2 and y1 == y2:
        den = (2 * y1 + a1 * x1 + a3) % int(p)
        inv_den = inv_mod(den, p)
        if inv_den is None:
            return ("line_tangent_singular=1", f"line_x_bin={bounded_bin(x1, p, bins)}")
        slope = ((3 * x1 * x1 + 2 * a2 * x1 + a4 - a1 * y1) * inv_den) % int(p)
        kind = "tangent"
    else:
        den = (x2 - x1) % int(p)
        inv_den = inv_mod(den, p)
        if inv_den is None:
            return ("line_vertical_den=1", f"line_x_bin={bounded_bin(x1, p, bins)}")
        slope = ((y2 - y1) * inv_den) % int(p)
        kind = "chord"
    intercept = (y1 - slope * x1) % int(p)
    return (
        f"line_kind={kind}",
        f"line_slope_bin={bounded_bin(slope, p, bins)}",
        f"line_intercept_bin={bounded_bin(intercept, p, bins)}",
        f"line_slope_mod8={slope % 8}",
        f"line_intercept_mod8={intercept % 8}",
    )


def richer_features_for_support(
    p806: Any,
    p801: Any,
    support: tuple[int, int],
    factor_base: list[Any],
    ainvs: list[int],
    p: int,
    bins: int,
    pair_points: dict[tuple[int, int], Any],
    pair_x_counts: Counter,
    pair_y_counts: Counter,
    pair_point_counts: Counter,
    factor_x_counts: Counter,
    factor_y_counts: Counter,
) -> tuple[str, ...]:
    left, right = p806.canonical_support(support)
    size = len(factor_base)
    left_point = factor_base[left]
    right_point = factor_base[right]
    lx, rx = point_x(left_point, p), point_x(right_point, p)
    ly, ry = point_y(left_point, p), point_y(right_point, p)
    pair_point = pair_points[support]
    pair_x, pair_y = point_x(pair_point, p), point_y(pair_point, p)
    span = abs(left - right)
    index_sum = left + right
    sx = (lx + rx) % int(p)
    px = (lx * rx) % int(p)
    sy = (ly + ry) % int(p)
    py = (ly * ry) % int(p)
    x_gap = abs(lx - rx)
    y_gap = abs(ly - ry)
    point_key = None if pair_point is None else (int(pair_point[0]) % int(p), int(pair_point[1]) % int(p))
    features = [
        f"left_bin={index_bin(left, size, bins)}",
        f"right_bin={index_bin(right, size, bins)}",
        f"span_bin={index_bin(span, size, bins)}",
        f"sum_bin={index_bin(index_sum, max(1, 2 * size), bins)}",
        f"left_x_bin={bounded_bin(lx, p, bins)}",
        f"right_x_bin={bounded_bin(rx, p, bins)}",
        f"left_y_bin={bounded_bin(ly, p, bins)}",
        f"right_y_bin={bounded_bin(ry, p, bins)}",
        f"min_x_bin={bounded_bin(min(lx, rx), p, bins)}",
        f"max_x_bin={bounded_bin(max(lx, rx), p, bins)}",
        f"x_gap_bin={bounded_bin(x_gap, p, bins)}",
        f"y_gap_bin={bounded_bin(y_gap, p, bins)}",
        f"pair_x_bin={bounded_bin(pair_x, p, bins)}",
        f"pair_y_bin={bounded_bin(pair_y, p, bins)}",
        f"sym_x_sum_bin={bounded_bin(sx, p, bins)}",
        f"sym_x_prod_bin={bounded_bin(px, p, bins)}",
        f"sym_y_sum_bin={bounded_bin(sy, p, bins)}",
        f"sym_y_prod_bin={bounded_bin(py, p, bins)}",
        f"same_x={int(lx == rx)}",
        f"same_y={int(ly == ry)}",
        f"index_parity={left % 2}:{right % 2}",
        f"span_mod4={span % 4}",
        f"sum_mod8={index_sum % 8}",
        f"x_sum_mod8={sx % 8}",
        f"x_prod_mod8={px % 8}",
        f"pair_x_mod8={pair_x % 8}",
        f"factor_x_mult_left_bin={min(7, int(factor_x_counts[lx]))}",
        f"factor_x_mult_right_bin={min(7, int(factor_x_counts[rx]))}",
        f"factor_y_mult_left_bin={min(7, int(factor_y_counts[ly]))}",
        f"factor_y_mult_right_bin={min(7, int(factor_y_counts[ry]))}",
        f"pair_x_collision_bin={min(15, int(pair_x_counts[pair_x]))}",
        f"pair_y_collision_bin={min(15, int(pair_y_counts[pair_y]))}",
        f"pair_point_collision_bin={min(15, int(pair_point_counts[point_key]))}",
    ]
    features.extend(line_features(left_point, right_point, ainvs, p, bins))
    return tuple(features)


def richer_build_public_context(
    p801: Any,
    p746: Any,
    relprobe: Any,
    base_item: dict[str, Any],
    trained_by_budget: dict[int, dict[tuple[int, int, int, int], dict[str, Any]]],
    support_budgets: list[int],
    namespace: str,
    args: argparse.Namespace,
) -> dict[str, Any]:
    p806 = richer_build_public_context.p806
    verifier, record, inv = p746.load_target(relprobe, str(base_item["target"]))
    ainvs = record["ainvs"]
    p = int(inv["p"])
    order = int(inv["base_order"])
    factor_base_size = int(base_item["factor_base_size"])
    sample_seed = (
        f"ecdlp-p807-{namespace}-{slug(base_item['target'])}:sample:"
        f"fb{factor_base_size}:w2:{args.walk_mode}"
    )
    sample_challenge, _sample_secret = relprobe.make_challenge(verifier, inv, ainvs, sample_seed, factor_base_size)
    factor_base = [
        verifier.point_from_json(point)
        for point in sample_challenge["factor_base"][: max(1, min(factor_base_size, len(sample_challenge["factor_base"])))]
    ]
    all_pairs = sorted(p801.all_support_pairs(len(factor_base)))
    pair_points = {support: p801.support_sum(verifier, factor_base, support, ainvs, p) for support in all_pairs}
    pair_x_counts = Counter(point_x(point, p) for point in pair_points.values())
    pair_y_counts = Counter(point_y(point, p) for point in pair_points.values())
    pair_point_counts = Counter(
        None if point is None else (int(point[0]) % p, int(point[1]) % p)
        for point in pair_points.values()
    )
    factor_x_counts = Counter(point_x(point, p) for point in factor_base)
    factor_y_counts = Counter(point_y(point, p) for point in factor_base)
    features_by_support = {
        support: richer_features_for_support(
            p806,
            p801,
            support,
            factor_base,
            ainvs,
            p,
            int(args.feature_bins),
            pair_points,
            pair_x_counts,
            pair_y_counts,
            pair_point_counts,
            factor_x_counts,
            factor_y_counts,
        )
        for support in all_pairs
    }
    return {
        "ainvs": ainvs,
        "all_pairs": all_pairs,
        "base_item": base_item,
        "factor_base": factor_base,
        "factor_base_size": factor_base_size,
        "features_by_support": features_by_support,
        "group_key": str(base_item["group_key"]),
        "inv": inv,
        "namespace": namespace,
        "order": order,
        "p": p,
        "requested_by_budget": {
            int(budget): p806.requested_supports(p801, trained_by_budget, int(budget))
            for budget in support_budgets
        },
        "target": str(base_item["target"]),
        "verifier": verifier,
    }


def configure_p807(p806: Any) -> None:
    richer_build_public_context.p806 = p806
    p806.build_public_context = richer_build_public_context


def map_claim_status(status: str) -> str:
    return {
        "P806_CROSS_TARGET_PUBLIC_FEATURE_CLASSIFIER_MATCHES_REQUESTED": "P807_RICH_CROSS_TARGET_PUBLIC_FEATURE_CLASSIFIER_MATCHES_REQUESTED",
        "P806_SAME_TARGET_PUBLIC_FEATURE_UPPER_BOUND_ONLY": "P807_RICH_SAME_TARGET_PUBLIC_FEATURE_UPPER_BOUND_ONLY",
        "P806_PUBLIC_FEATURE_CLASSIFIER_FAILS_REQUESTED_SIGNAL": "P807_RICH_PUBLIC_FEATURE_CLASSIFIER_FAILS_REQUESTED_SIGNAL",
        "NEGATIVE_RESULT_P806_REQUESTED_SUPPORT_SIGNAL_LOST": "NEGATIVE_RESULT_P807_REQUESTED_SUPPORT_SIGNAL_LOST",
    }.get(status, status.replace("P806", "P807"))


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p806 = load_module("ecdlp_p806_for_p807", P806_SCRIPT)
    configure_p807(p806)
    payload = p806.analyze(args)
    payload["claim_status"] = map_claim_status(str(payload["claim_status"]))
    payload["created_at"] = now_iso()
    payload["method"] = "p807_richer_public_feature_classifier"
    payload["schema"] = SCHEMA
    payload["artifacts"] = {
        **payload.get("artifacts", {}),
        "contract": str(DEFAULT_CONTRACT),
        "p806_script": str(P806_SCRIPT),
        "script": str(Path(__file__)),
    }
    payload["honesty_boundary"] = [
        "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
        "RICHER-PUBLIC-FEATURE ONLY: classifier inputs are public factor-base index, coordinate, line, pair-sum collision, graph-neighborhood, and symmetric-function features.",
        "CROSS-TARGET TEST: the main classifier trains on the other target group in the same namespace and predicts supports on the held-out group.",
        "SAME-TARGET UPPER BOUND: same-target classifier uses held-out target support labels and is diagnostic only, not a valid public derivation claim.",
        "MODEL-BOUND TARGET-ONCE SETUP: line calibration and support setup are charged once per target across fresh namespaces.",
        "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
    ]
    payload["parameters"] = {
        **payload.get("parameters", {}),
        "feature_family": "p807_rich_index_coordinate_line_collision_graph_symmetric",
    }
    return payload


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    p806 = load_module("ecdlp_p806_summary_for_p807", P806_SCRIPT)
    summary = p806.summary_from_payload(payload)
    summary["schema"] = f"{SCHEMA}.summary"
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--constructor-namespaces", default="prehitpair-p807-rich-v14,prehitpair-p807-rich-v15,prehitpair-p807-rich-v16")
    parser.add_argument("--support-budgets", default="128,256,512")
    parser.add_argument("--trial-budgets", default="256")
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--scan-seed-count", type=int, default=128)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--feature-bins", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--logodds-smoothing", type=float, default=1.0)
    parser.add_argument("--min-line-rows", type=int, default=2)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = summary_from_payload(payload)
    write_json(summary_out, summary)
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "best_cross_target_by_model": summary["summary"]["best_cross_target_by_model"],
                "best_requested_by_model": summary["summary"]["best_requested_by_model"],
                "best_same_target_upper_by_model": summary["summary"]["best_same_target_upper_by_model"],
                "claim_status": summary["claim_status"],
                "requested_grid_public_rank": summary["summary"]["requested_grid_public_rank"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
