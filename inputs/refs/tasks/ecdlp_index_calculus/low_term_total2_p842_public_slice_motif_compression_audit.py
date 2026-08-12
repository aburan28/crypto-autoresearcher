#!/usr/bin/env python3
"""P842 public slice motif-compression audit.

P841 showed that a global public slice policy preserves most heldout roots but
selects too much work.  This audit learns compact public slice motifs from
calibration oracle slice-quadratic factors, then applies those motifs to heldout
public slice candidates without selected-leaf access.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from statistics import mean
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
PUBLIC_SLICE_SCRIPT = (
    TASK_DIR
    / "frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_public_slice_predictor_probe.py"
)
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_PUBLIC_SLICE = (
    STATE_DIR
    / "frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_public_slice_predictor_probe.json"
)
DEFAULT_SLICE_QUADRATIC = (
    STATE_DIR
    / "frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_slice_quadratic_root_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p842_public_slice_motif_compression_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p842_public_slice_motif_compression_audit.md"
SCHEMA = "ecdlp.low_term_total2_p842_public_slice_motif_compression_audit.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_module(name: str, path: Path) -> Any:
    sys.path.insert(0, str(path.resolve().parent))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot import {name} from {path}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        if sys.path[0] == str(path.resolve().parent):
            sys.path.pop(0)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def transfer_index(surface: dict[str, Any]) -> int:
    text = str(surface.get("surface_id") or "") + "|" + str(surface.get("challenge_seed") or "")
    match = re.search(r"shared-transfer:(\d+)", text)
    if match:
        return int(match.group(1))
    return 10**9


def split_surface_ids(surfaces: list[dict[str, Any]], calibration_fraction: float) -> tuple[list[str], list[str]]:
    ordered = sorted(
        surfaces,
        key=lambda surface: (
            transfer_index(surface),
            str(surface.get("target")),
            str(surface.get("surface_id")),
        ),
    )
    split = max(1, min(len(ordered) - 1, round(len(ordered) * float(calibration_fraction))))
    return [str(item["surface_id"]) for item in ordered[:split]], [str(item["surface_id"]) for item in ordered[split:]]


def factor_terms(factor: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    return tuple((int(power), int(coeff)) for power, coeff in factor.get("terms") or [])


def oracle_factor_motifs(oracle_surface: dict[str, Any]) -> list[dict[str, Any]]:
    candidate = oracle_surface.get("best_preserving_candidate") or {}
    motifs = []
    for factor in candidate.get("factors") or []:
        motifs.append(
            {
                "axis": str(candidate.get("axis")),
                "degree": int(factor.get("degree") or 0),
                "fixed_value": int(factor.get("fixed_value") or 0),
                "monomials": int(factor.get("monomials") or 0),
                "terms": factor_terms(factor),
            }
        )
    return motifs


def learn_motif_sets(oracle_by_id: dict[str, dict[str, Any]], calibration_ids: list[str]) -> list[dict[str, Any]]:
    motifs = []
    for surface_id in calibration_ids:
        for motif in oracle_factor_motifs(oracle_by_id.get(surface_id) or {}):
            motifs.append(motif)

    exact = Counter((m["axis"], m["fixed_value"], m["degree"], m["terms"]) for m in motifs)
    axis_fixed = Counter((m["axis"], m["fixed_value"]) for m in motifs)
    axis_terms = Counter((m["axis"], m["degree"], m["terms"]) for m in motifs)
    axis_monomials = Counter((m["axis"], m["degree"], m["monomials"]) for m in motifs)
    b_repeated_fixed = {
        key
        for key, count in axis_fixed.items()
        if key[0] == "b" and count >= 2
    }

    def materialize(name: str, values: set[tuple[Any, ...]] | list[tuple[Any, ...]], min_seen: int) -> dict[str, Any]:
        return {
            "min_seen": int(min_seen),
            "motif_count": len(values),
            "motifs": [list(value) for value in sorted(values, key=str)],
            "name": name,
        }

    motif_sets = [
        materialize("exact_factor", set(exact), 1),
        materialize("axis_fixed", set(axis_fixed), 1),
        materialize("axis_terms", set(axis_terms), 1),
        materialize("axis_monomials", set(axis_monomials), 1),
        materialize("b_repeated_fixed", b_repeated_fixed, 2),
    ]
    return motif_sets


def candidate_factor_signatures(candidate: dict[str, Any]) -> list[tuple[str, int, int, tuple[tuple[int, int], ...]]]:
    axis = str(candidate.get("axis"))
    out = []
    for factor in candidate.get("factors") or []:
        out.append(
            (
                axis,
                int(factor.get("fixed_value") or candidate.get("fixed_value") or 0),
                int(factor.get("degree") or 0),
                factor_terms(factor),
            )
        )
    return out


def candidate_matches(candidate: dict[str, Any], motif_set: dict[str, Any]) -> bool:
    name = str(motif_set["name"])
    motifs = {tuple(value) for value in motif_set.get("motifs") or []}
    axis = str(candidate.get("axis"))
    fixed_value = int(candidate.get("fixed_value") or 0)
    max_degree = int(candidate.get("selected_factor_max_degree") or 0)
    monomials = int(candidate.get("selected_factor_monomials") or 0)
    if not motifs:
        return False
    if name == "exact_factor":
        return any(signature in motifs for signature in candidate_factor_signatures(candidate))
    if name == "axis_fixed":
        return (axis, fixed_value) in motifs
    if name == "axis_terms":
        return any((sig[0], sig[2], sig[3]) in motifs for sig in candidate_factor_signatures(candidate))
    if name == "axis_monomials":
        return (axis, max_degree, monomials) in motifs
    if name == "b_repeated_fixed":
        return (axis, fixed_value) in motifs
    raise ValueError(f"unknown motif set {name!r}")


def evaluate_chosen(ps: Any, surface_record: dict[str, Any], chosen: list[dict[str, Any]], motif_name: str) -> dict[str, Any]:
    original_pairs = ps.remainder_factor_probe.selected_pair_set(surface_record, surface_record["surface"])
    selected_pairs = {
        (int(leaf), int(root))
        for candidate in chosen
        for leaf, root in candidate.get("selected_pairs") or []
    }
    missing_pairs = sorted(original_pairs - selected_pairs)
    extra_pairs = sorted(selected_pairs - original_pairs)
    relevant_leaf_evals = sum(int(candidate["relevant_leaf_count"]) for candidate in chosen)
    factor_zero_leaf_evals = sum(int(candidate["factor_zero_leaf_count"]) for candidate in chosen)
    recovered_root_count = sum(int(candidate["recovered_root_count"]) for candidate in chosen)
    factor_work = sum(int(candidate["selected_factor_monomials"]) for candidate in chosen)
    cost = surface_record["cost_inputs"]
    selected_hit_events = int(cost["selected_hit_events"])
    all_hit_core = (
        int(surface_record["built"]["selected_signed_pair_count"])
        + ceil(int(surface_record["built"]["row_pool"]) / 512)
        + ceil(relevant_leaf_evals / 4096)
        + len(surface_record["components"]["hit_roots"])
    )
    quadratic_root_work = 2 * factor_zero_leaf_evals
    ops = (
        all_hit_core
        + factor_work
        + relevant_leaf_evals
        + quadratic_root_work
        + recovered_root_count
        + 2 * selected_hit_events
    )
    rho = int(cost["generic_rho_steps"])
    return {
        "chosen_count": len(chosen),
        "chosen_slices": [
            {
                "axis": candidate.get("axis"),
                "fixed_value": candidate.get("fixed_value"),
                "factor_zero_leaf_count": candidate.get("factor_zero_leaf_count"),
                "relevant_leaf_count": candidate.get("relevant_leaf_count"),
                "selected_factor_monomials": candidate.get("selected_factor_monomials"),
                "min_leaf_index": candidate.get("min_leaf_index"),
            }
            for candidate in chosen[:12]
        ],
        "extra_selected_root_pairs": [[leaf, root] for leaf, root in extra_pairs[:8]],
        "factor_work": int(factor_work),
        "factor_zero_leaf_evals": int(factor_zero_leaf_evals),
        "missing_selected_root_pairs": [[leaf, root] for leaf, root in missing_pairs[:8]],
        "motif_policy": motif_name,
        "original_selected_root_pair_count": len(original_pairs),
        "preserves_selected_root_pairs": not missing_pairs,
        "public_slice_motif_beats_rho": bool(ops < rho),
        "public_slice_motif_ops": int(ops),
        "public_slice_motif_ops_over_rho": ratio(ops, rho),
        "quadratic_root_work": int(quadratic_root_work),
        "recovered_root_count": int(recovered_root_count),
        "relevant_leaf_evals": int(relevant_leaf_evals),
        "same_selected_root_pairs": not missing_pairs and not extra_pairs,
        "selected_root_pair_count": len(selected_pairs),
    }


def metrics_for(rows: list[dict[str, Any]]) -> dict[str, Any]:
    selections = [row["selection"] for row in rows]
    ratios = [
        float(item["public_slice_motif_ops_over_rho"])
        for item in selections
        if item.get("public_slice_motif_ops_over_rho") is not None
    ]
    preserving = [item for item in selections if item.get("preserves_selected_root_pairs")]
    below = [item for item in selections if item.get("public_slice_motif_beats_rho")]
    preserving_below = [
        item
        for item in selections
        if item.get("preserves_selected_root_pairs") and item.get("public_slice_motif_beats_rho")
    ]
    missing_pairs = sum(len(item.get("missing_selected_root_pairs") or []) for item in selections)
    return {
        "below_rho_count": len(below),
        "max_ops_over_rho": round(max(ratios), 8) if ratios else None,
        "mean_ops_over_rho": round(mean(ratios), 8) if ratios else None,
        "min_ops_over_rho": round(min(ratios), 8) if ratios else None,
        "missing_pair_event_count": int(missing_pairs),
        "preserving_below_rho_count": len(preserving_below),
        "preserving_below_rho_rate": ratio(len(preserving_below), len(selections)),
        "preserving_count": len(preserving),
        "preserving_rate": ratio(len(preserving), len(selections)),
        "surface_count": len(selections),
    }


def materialize_surface_records(ps: Any, args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    signature = ps.load_json(args.signature_source)
    positive_cases = [case for case in signature.get("positive_cases") or [] if isinstance(case, dict)]
    if args.max_cases and args.max_cases > 0:
        positive_cases = positive_cases[: args.max_cases]
    bank = ps.load_json(args.bank_source)
    config_source = ps.load_json(args.config_source)
    direct_source = ps.load_json(args.direct_source)
    transfer_source = ps.load_json(args.transfer_source)
    params = transfer_source.get("parameters") if isinstance(transfer_source, dict) else {}
    radius = int(args.radius if args.radius is not None else (params or {}).get("radius") or 4)
    bank_rows = {
        ps.cross_surface_probe.compress_probe.row_key(row): row
        for row in bank.get("bank_rows") or []
        if isinstance(row, dict) and ps.cross_surface_probe.compress_probe.row_key(row)
    }
    specs_by_target = ps.cross_surface_probe.leaf_trim_probe.specs_by_target_and_key(
        ps.cross_surface_probe.salt_neighborhood_probe.witness_specs(direct_source, bank_rows, radius)
    )
    verifier = ps.cross_surface_probe.relation_probe.load_verifier_module()
    records = verifier.load_records()
    return ps.cross_surface_probe.materialize_surface_records(
        verifier,
        records,
        config_source,
        specs_by_target,
        positive_cases,
        args,
    )


def public_slice_args(ps: Any) -> argparse.Namespace:
    return argparse.Namespace(
        allow_combined_coefficients=False,
        bank_source=ps.cross_surface_probe.compress_probe.DEFAULT_BANK_SOURCE,
        config_source=ps.cross_surface_probe.compress_probe.DEFAULT_CONFIG_SOURCE,
        direct_source=ps.cross_surface_probe.compress_probe.DEFAULT_DIRECT_SOURCE,
        factor_base_size=16,
        max_cases=0,
        max_factor_degree=1,
        max_relations=96,
        min_distinct_indices=4,
        min_unsigned_distinct_indices=2,
        out=DEFAULT_PUBLIC_SLICE,
        product_factor=4096,
        radius=None,
        require_unit_coefficients=True,
        row_count=128,
        row_factor=512,
        row_pool=512,
        scout_limit=192,
        scout_mode="s3_coeff_spread",
        scout_order="eval_cover_hits_high",
        seed="ecdlp-frontier-signed-dual-sieve-v1",
        selected_limit=64,
        signature_source=ps.DEFAULT_SIGNATURE_SOURCE,
        state_dir=STATE_DIR,
        transfer_source=ps.cross_surface_probe.compress_probe.DEFAULT_TRANSFER_SOURCE,
    )


def evaluate_motif_policy(
    ps: Any,
    surface_records_by_id: dict[str, dict[str, Any]],
    candidates_by_id: dict[str, list[dict[str, Any]]],
    motif_set: dict[str, Any],
    surface_ids: list[str],
) -> list[dict[str, Any]]:
    rows = []
    for surface_id in surface_ids:
        record = surface_records_by_id[surface_id]
        chosen = [
            candidate
            for candidate in candidates_by_id[surface_id]
            if candidate_matches(candidate, motif_set)
        ]
        selection = evaluate_chosen(ps, record, chosen, str(motif_set["name"]))
        rows.append(
            {
                "row_key": record.get("row_key"),
                "surface_id": surface_id,
                "target": record.get("target"),
                "transfer_index": transfer_index(record),
                "selection": selection,
            }
        )
    return rows


def choose_policy(policy_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    return sorted(
        policy_summaries,
        key=lambda item: (
            int(item["calibration_metrics"]["preserving_below_rho_count"]),
            int(item["calibration_metrics"]["preserving_count"]),
            -int(item["calibration_metrics"]["missing_pair_event_count"]),
            -(float(item["calibration_metrics"]["mean_ops_over_rho"]) if item["calibration_metrics"]["mean_ops_over_rho"] is not None else 10**9),
            -int(item["motif_set"]["motif_count"]),
            item["motif_set"]["name"],
        ),
        reverse=True,
    )[0]


def determine_claim(heldout_metrics: dict[str, Any]) -> str:
    if int(heldout_metrics["preserving_below_rho_count"]) > 0:
        return "P842_HELDOUT_PUBLIC_MOTIF_BELOW_RHO_SIGNAL"
    if int(heldout_metrics["preserving_count"]) > 0:
        return "P842_HELDOUT_PUBLIC_MOTIF_PRESERVES_ABOVE_RHO"
    if int(heldout_metrics["below_rho_count"]) > 0:
        return "P842_HELDOUT_PUBLIC_MOTIF_CHEAP_BUT_MISSES_ROOTS"
    return "NEGATIVE_RESULT_P842_PUBLIC_MOTIFS_NO_HELDOUT_SIGNAL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    ps = load_module("ecdlp_public_slice_for_p842", PUBLIC_SLICE_SCRIPT)
    public_slice = load_json(args.public_slice)
    slice_quadratic = load_json(args.slice_quadratic)
    public_surfaces = [surface for surface in public_slice.get("surfaces") or [] if surface.get("surface_id")]
    calibration_ids, heldout_ids = split_surface_ids(public_surfaces, float(args.calibration_fraction))
    oracle_by_id = {str(surface["surface_id"]): surface for surface in slice_quadratic.get("surfaces") or []}
    motif_sets = learn_motif_sets(oracle_by_id, calibration_ids)

    ps_args = public_slice_args(ps)
    print("materializing slice surfaces for motif evaluation", flush=True)
    surface_records, _case_results = materialize_surface_records(ps, ps_args)
    surface_records_by_id = {str(surface["surface_id"]): surface for surface in surface_records}
    candidates_by_id = {
        surface_id: ps.build_public_candidates(surface_records_by_id[surface_id], int(ps_args.max_factor_degree))
        for surface_id in calibration_ids + heldout_ids
        if surface_id in surface_records_by_id
    }
    missing_ids = [surface_id for surface_id in calibration_ids + heldout_ids if surface_id not in candidates_by_id]
    if missing_ids:
        raise RuntimeError(f"missing rematerialized surface ids: {missing_ids[:3]}")

    policy_summaries = []
    for motif_set in motif_sets:
        calibration_rows = evaluate_motif_policy(ps, surface_records_by_id, candidates_by_id, motif_set, calibration_ids)
        heldout_rows = evaluate_motif_policy(ps, surface_records_by_id, candidates_by_id, motif_set, heldout_ids)
        policy_summaries.append(
            {
                "calibration_metrics": metrics_for(calibration_rows),
                "heldout_metrics": metrics_for(heldout_rows),
                "motif_set": motif_set,
            }
        )
    selected = choose_policy(policy_summaries)
    selected_name = str(selected["motif_set"]["name"])
    selected_motif_set = next(item for item in motif_sets if item["name"] == selected_name)
    calibration_rows = evaluate_motif_policy(ps, surface_records_by_id, candidates_by_id, selected_motif_set, calibration_ids)
    heldout_rows = evaluate_motif_policy(ps, surface_records_by_id, candidates_by_id, selected_motif_set, heldout_ids)
    heldout_metrics = metrics_for(heldout_rows)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "public_slice_source": str(args.public_slice),
            "script": str(Path(__file__)),
            "slice_quadratic_source": str(args.slice_quadratic),
        },
        "calibration": {
            "surface_count": len(calibration_ids),
            "surface_results": calibration_rows,
            "transfer_range": [
                min(transfer_index(surface_records_by_id[surface_id]) for surface_id in calibration_ids),
                max(transfer_index(surface_records_by_id[surface_id]) for surface_id in calibration_ids),
            ],
        },
        "claim_status": determine_claim(heldout_metrics),
        "created_at": now_iso(),
        "heldout": {
            "metrics": heldout_metrics,
            "surface_count": len(heldout_ids),
            "surface_results": heldout_rows,
            "transfer_range": [
                min(transfer_index(surface_records_by_id[surface_id]) for surface_id in heldout_ids),
                max(transfer_index(surface_records_by_id[surface_id]) for surface_id in heldout_ids),
            ],
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "MOTIF-CALIBRATED: motif families are learned from oracle slice-quadratic factors on calibration surfaces.",
            "HELDOUT-GATE: heldout scoring applies the selected motif family without per-surface selected-leaf access.",
            "PUBLIC-CANDIDATE BOUNDARY: candidates are still built from public slice-factor enumeration.",
            "POLLARD-RHO BOUNDARY: this is a relation-generation subproblem and not a complete faster-than-rho ECDLP algorithm.",
            "NO DEPLOYED-CURVE CLAIM: no production-key relevance or deployed-prime break is implied.",
        ],
        "method": "p842_public_slice_motif_compression_audit",
        "motif_policy_candidates": policy_summaries,
        "oracle_comparison": {
            "oracle_slice_quadratic_all_hit_below_rho_count": int(
                slice_quadratic["summary"]["slice_quadratic_all_hit_below_rho_count"]
            ),
            "oracle_slice_quadratic_min_all_hit_ops_over_rho": slice_quadratic["summary"][
                "min_slice_quadratic_all_hit_ops_over_rho"
            ],
            "public_per_surface_min_ops_over_rho": public_slice["summary"]["min_public_slice_quadratic_ops_over_rho"],
            "public_per_surface_preserving_below_rho_count": int(
                public_slice["summary"]["public_preserving_selection_below_rho_count"]
            ),
        },
        "parameters": {
            "calibration_fraction": float(args.calibration_fraction),
        },
        "red_team_handoff": {
            "assumptions": [
                "Repeated oracle slice motifs on calibration surfaces are plausible public slice-compression features.",
                "Exact factor-term and axis/fixed-value motif reuse can be tested as a heldout public selector.",
                "Rematerialized public candidates reproduce the public-slice candidate space used by earlier artifacts.",
            ],
            "failure_modes": [
                "A motif can be too specific and select no heldout slices.",
                "A structural motif can select too many slices and remain above rho.",
                "Calibration oracle motifs may not transfer across targets or transfer windows.",
            ],
            "next_concrete_action": (
                "If motif policies fail below rho, test a true bivariate factor backend or a learned public feature model with heldout calibration; "
                "if a motif succeeds, replicate on disjoint signature banks before residual-gap accounting."
            ),
        },
        "schema": SCHEMA,
        "selected_policy": selected,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-slice", type=Path, default=DEFAULT_PUBLIC_SLICE)
    parser.add_argument("--slice-quadratic", type=Path, default=DEFAULT_SLICE_QUADRATIC)
    parser.add_argument("--calibration-fraction", type=float, default=0.5)
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
                "heldout_metrics": payload["heldout"]["metrics"],
                "oracle_comparison": payload["oracle_comparison"],
                "selected_policy": payload["selected_policy"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
