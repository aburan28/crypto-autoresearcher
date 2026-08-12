#!/usr/bin/env python3
"""P707 public certificate-selector cost audit over the P706 corpus.

P705 used oracle min/mean/max target-relation costs.  P706 showed that all
archived direct-certificate forms transfer under the P702 factor values.  This
audit asks whether public certificate descriptors can select a bounded target
relation set on leave-one-artifact-out holdouts, charging every selected heldout
certificate rather than the cheapest selected one.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import low_term_total2_p706_archived_certificate_factor_value_transfer as p706


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P705 = STATE_DIR / "low_term_total2_p705_amortized_cost_crossover_probe.json"
DEFAULT_P706 = STATE_DIR / "low_term_total2_p706_archived_certificate_factor_value_transfer_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p707_public_certificate_selector_cost_probe.json"
DEFAULT_CERT_GLOB = p706.DEFAULT_CERT_GLOB
ORDER = p706.ORDER


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def salt_from_row_key(row_key: str) -> str:
    match = re.search(r":salt(\d+)", row_key)
    return f"salt{match.group(1)}" if match else "unknown"


def row_pair(row_keys: list[Any]) -> str:
    salts = [salt_from_row_key(str(row_key)) for row_key in row_keys]
    return "_".join(sorted(salts)) if salts else "none"


def selector_mode(selector: str) -> str:
    return selector.split("__", 1)[0] if selector else "none"


def parse_right_token(selector: str) -> str | None:
    match = re.search(r"right(20[678])", selector)
    return f"right{match.group(1)}" if match else None


def parse_anchor(selector: str) -> str | None:
    match = re.search(r"_ra(\d+)", selector)
    if match:
        return f"anchor{int(match.group(1))}"
    match = re.search(r"anchor(\d+)", selector)
    return f"anchor{int(match.group(1))}" if match else None


def parse_leaf_signature(selector: str) -> str | None:
    match = re.search(r"_L([0-9]+)_R([0-9-]+)", selector)
    return f"L{match.group(1)}_R{match.group(2)}" if match else None


def clean_feature(value: str | None) -> str | None:
    if value is None or value == "" or value == "none" or "unknown" in value:
        return None
    return value


def candidate_features(selected: dict[str, Any]) -> dict[str, str]:
    selector = str(selected.get("selector") or "")
    mode = clean_feature(selector_mode(selector))
    pair = clean_feature(row_pair(selected.get("row_keys") or []))
    top_k = int_value(selected.get("top_k"))
    top = f"top{top_k}" if top_k else None
    right = clean_feature(parse_right_token(selector))
    anchor = clean_feature(parse_anchor(selector))
    leaf = clean_feature(parse_leaf_signature(selector))
    features: dict[str, str] = {}
    base = {
        "anchor": anchor,
        "leaf_signature": leaf,
        "right_token": right,
        "row_pair": pair,
        "selector_mode": mode,
        "top_k": top,
    }
    for key, value in base.items():
        if value:
            features[key] = value

    def add(name: str, *parts: str | None) -> None:
        if all(parts):
            features[name] = "|".join(str(part) for part in parts)

    add("anchor_row_pair", anchor, pair)
    add("mode_anchor", mode, anchor)
    add("mode_anchor_row_pair", mode, anchor, pair)
    add("mode_leaf_signature", mode, leaf)
    add("mode_right_row_pair", mode, right, pair)
    add("mode_row_pair", mode, pair)
    add("mode_top_k", mode, top)
    add("right_anchor", right, anchor)
    add("right_anchor_row_pair", right, anchor, pair)
    add("right_row_pair", right, pair)
    add("row_pair_top_k", pair, top)
    return features


def load_candidates(paths: list[Path]) -> list[dict[str, Any]]:
    out = []
    for path in paths:
        payload = load_json(path)
        for cert_index, cert in enumerate(payload.get("certificates") or []):
            if int_value(cert.get("order"), ORDER) != ORDER:
                continue
            if cert.get("public_key_verified") is False:
                continue
            selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
            cost = p706.selected_cost(cert)
            if cost is None:
                continue
            features = candidate_features(selected)
            if not features:
                continue
            expected = p706.expected_secret(cert, ORDER)
            out.append(
                {
                    "artifact": str(path),
                    "certificate_index": cert_index,
                    "cost_over_rho": float_value(cost),
                    "expected_secret": expected,
                    "features": features,
                    "forms_count": int_value(cert.get("forms_count") or len(cert.get("forms") or [])),
                    "p_id": p706.p_id(path),
                    "selected": {
                        "row_keys": selected.get("row_keys") or [],
                        "selector": selected.get("selector"),
                        "target": selected.get("target"),
                        "top_k": int_value(selected.get("top_k")),
                        "transfer_index": int_value(selected.get("transfer_index")),
                    },
                }
            )
    return out


def parse_top_values(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def feature_stats(candidates: list[dict[str, Any]], feature_family: str) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        value = candidate["features"].get(feature_family)
        if not value:
            continue
        entry = grouped.setdefault(
            value,
            {"artifact_set": set(), "costs": [], "candidate_count": 0, "value": value},
        )
        entry["artifact_set"].add(candidate["artifact"])
        entry["costs"].append(float_value(candidate.get("cost_over_rho")))
        entry["candidate_count"] += 1
    stats = []
    for value, entry in grouped.items():
        costs = entry["costs"]
        stats.append(
            {
                "artifact_count": len(entry["artifact_set"]),
                "candidate_count": int_value(entry["candidate_count"]),
                "mean_cost_over_rho": round(mean(costs), 8),
                "min_cost_over_rho": round(min(costs), 8),
                "value": value,
            }
        )
    stats.sort(
        key=lambda item: (
            -int_value(item["artifact_count"]),
            float_value(item["mean_cost_over_rho"]),
            -int_value(item["candidate_count"]),
            str(item["value"]),
        )
    )
    return stats


def selected_by_values(candidates: list[dict[str, Any]], feature_family: str, values: set[str]) -> list[dict[str, Any]]:
    return [
        candidate
        for candidate in candidates
        if candidate["features"].get(feature_family) in values
    ]


def evaluate_policy(
    candidates_by_artifact: dict[str, list[dict[str, Any]]],
    feature_family: str,
    top_n: int,
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    heldout_count = len(candidates_by_artifact)
    hit_count = 0
    selected_candidate_count = 0
    selected_charge_total = 0.0
    selected_min_charge_total = 0.0
    fallback_charge_total = 0.0
    selected_secret_counter: Counter[str] = Counter()
    samples = []
    missed_artifacts = []
    for heldout_artifact, heldout_candidates in sorted(candidates_by_artifact.items()):
        training = [
            candidate
            for artifact, candidates in candidates_by_artifact.items()
            if artifact != heldout_artifact
            for candidate in candidates
        ]
        stats = feature_stats(training, feature_family)
        allowed = {str(item["value"]) for item in stats[:top_n]}
        selected = selected_by_values(heldout_candidates, feature_family, allowed)
        if not selected:
            fallback_charge_total += 1.0
            if len(missed_artifacts) < sample_limit:
                missed_artifacts.append(heldout_artifact)
            continue
        hit_count += 1
        charge = sum(float_value(candidate.get("cost_over_rho")) for candidate in selected)
        min_charge = min(float_value(candidate.get("cost_over_rho")) for candidate in selected)
        selected_candidate_count += len(selected)
        selected_charge_total += charge
        selected_min_charge_total += min_charge
        for candidate in selected:
            if candidate.get("expected_secret") is not None:
                selected_secret_counter[str(candidate["expected_secret"])] += 1
        if len(samples) < sample_limit:
            samples.append(
                {
                    "allowed_values": sorted(allowed),
                    "heldout_artifact": heldout_artifact,
                    "min_selected_charge_over_rho": round(min_charge, 8),
                    "selected_charge_over_rho": round(charge, 8),
                    "selected_count": len(selected),
                    "selected_examples": [
                        {
                            "certificate_index": candidate["certificate_index"],
                            "cost_over_rho": candidate["cost_over_rho"],
                            "expected_secret": candidate.get("expected_secret"),
                            "features": {
                                key: candidate["features"][key]
                                for key in sorted(candidate["features"])
                                if key in {feature_family, "selector_mode", "row_pair", "right_token", "anchor"}
                            },
                            "selected": candidate["selected"],
                        }
                        for candidate in selected[:3]
                    ],
                }
            )
    solved_total = factor_charge + selected_charge_total
    fallback_total = factor_charge + selected_charge_total + fallback_charge_total
    return {
        "beats_rho_on_hit_set": bool(hit_count and solved_total < hit_count),
        "beats_rho_with_fallback": bool(heldout_count and fallback_total < heldout_count),
        "feature_family": feature_family,
        "hit_count": hit_count,
        "hit_rate": round(hit_count / heldout_count, 8) if heldout_count else 0.0,
        "heldout_count": heldout_count,
        "missed_artifact_samples": missed_artifacts,
        "oracle_min_selected_charge_total_over_rho": round(selected_min_charge_total, 8),
        "policy": f"{feature_family}:top{top_n}",
        "sample_selections": samples,
        "selected_candidate_count": selected_candidate_count,
        "selected_charge_per_hit_over_rho": round(selected_charge_total / hit_count, 8) if hit_count else None,
        "selected_charge_total_over_rho": round(selected_charge_total, 8),
        "selected_secret_counts_sample": dict(list(selected_secret_counter.items())[:20]),
        "selected_with_fallback_total_over_rho": round(fallback_total, 8),
        "solved_total_charge_over_rho": round(solved_total, 8),
        "solved_total_per_hit_over_rho": round(solved_total / hit_count, 8) if hit_count else None,
        "top_n": top_n,
        "vs_independent_rho_hit_set_over_rho": hit_count,
        "vs_independent_rho_with_fallback_over_rho": heldout_count,
    }


def determine_claim(policy_reports: list[dict[str, Any]]) -> str:
    if any(
        report["beats_rho_with_fallback"] and float_value(report["hit_rate"]) >= 0.5
        for report in policy_reports
    ):
        return "P707_PUBLIC_SELECTOR_AMORTIZED_BELOW_RHO_WITH_FALLBACK"
    if any(
        report["beats_rho_on_hit_set"] and float_value(report["hit_rate"]) >= 0.5
        for report in policy_reports
    ):
        return "P707_PUBLIC_SELECTOR_HIT_SET_BELOW_RHO_ONLY"
    if any(report["hit_count"] for report in policy_reports):
        return "P707_PUBLIC_SELECTOR_RECALL_WITH_COST_OPEN"
    return "NEGATIVE_RESULT_P707_NO_PUBLIC_SELECTOR_RECALL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p705 = load_json(Path(args.p705))
    factor_charge = float_value((p705.get("summary") or {}).get("factor_bank_charge_over_rho"), 0.992)
    paths = [Path(path) for path in sorted(glob.glob(args.certificate_glob))]
    candidates = load_candidates(paths)
    by_artifact: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        by_artifact[candidate["artifact"]].append(candidate)
    feature_families = sorted({
        family
        for candidate in candidates
        for family in candidate.get("features", {})
    })
    top_values = parse_top_values(args.top_values)
    policy_reports = [
        evaluate_policy(by_artifact, family, top_n, factor_charge, int_value(args.sample_limit))
        for family in feature_families
        for top_n in top_values
    ]
    policy_reports.sort(
        key=lambda report: (
            not bool(report["beats_rho_with_fallback"]),
            -float_value(report["hit_rate"]),
            float_value(report.get("selected_with_fallback_total_over_rho"), 999999.0)
            / max(1, int_value(report.get("heldout_count"))),
            float_value(report.get("selected_charge_per_hit_over_rho"), 999999.0),
            str(report["policy"]),
        )
    )
    best = policy_reports[0] if policy_reports else None
    claim_status = determine_claim(policy_reports)
    return {
        "artifacts": {
            "certificate_glob": args.certificate_glob,
            "p705": str(Path(args.p705)),
            "p706": str(Path(args.p706)),
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: selector validation is offline over archived direct-certificate artifacts.",
            "HEURISTIC: public descriptor recall over archived certificates is not a fresh source-generation theorem.",
            "COST DISCIPLINE: every selected heldout certificate is charged; oracle-min charge is reported separately and not used for the main claim.",
        ],
        "method": "p707_public_certificate_selector_cost",
        "parameters": {
            "factor_bank_charge_over_rho": factor_charge,
            "feature_family_count": len(feature_families),
            "top_values": top_values,
        },
        "policy_reports": policy_reports,
        "schema": "ecdlp.low_term_total2_p707_public_certificate_selector_cost.v1",
        "summary": {
            "artifact_count": len(by_artifact),
            "best_policy": None if best is None else best["policy"],
            "best_policy_beats_rho_with_fallback": None if best is None else best["beats_rho_with_fallback"],
            "best_policy_hit_rate": None if best is None else best["hit_rate"],
            "best_policy_selected_with_fallback_total_over_rho": (
                None if best is None else best["selected_with_fallback_total_over_rho"]
            ),
            "candidate_count": len(candidates),
            "factor_bank_charge_over_rho": factor_charge,
            "feature_families": feature_families,
            "policy_count": len(policy_reports),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate-glob", default=DEFAULT_CERT_GLOB)
    parser.add_argument("--p705", default=str(DEFAULT_P705))
    parser.add_argument("--p706", default=str(DEFAULT_P706))
    parser.add_argument("--top-values", default="1,3,5,10")
    parser.add_argument("--sample-limit", type=int, default=6)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"best_policy": payload["policy_reports"][:1]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
