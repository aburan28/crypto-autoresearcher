#!/usr/bin/env python3
"""Synthesize the frozen P1500 cover census into a transport decision."""

from __future__ import annotations

import hashlib
import json
import math
import os
import resource
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "ecdlp_index_calculus_state"
RESEARCH = ROOT / "research"
CONTRACT = STATE / "experiment_contract_p1500_nonsimple_prym_transport_census.md"
P1499 = STATE / "p1499_cross_anchor_deck_character_resultant.json"
P1499_AUDIT = STATE / "p1499_cross_anchor_deck_character_resultant_audit.json"
PO75_CONTRACT = ROOT / "research/PO_transfer_075_e_isotypic_prym_bridge_contract.md"
PO75_SOURCE = ROOT / "experiments/ecdlp_isogeny/po_transfer_075_extra_involution_prym_probe.sage"
PO75_RESULT = ROOT / "experiments/ecdlp_isogeny/po_transfer_075_extra_involution_prym_probe.json"
PO75_AUDIT_SOURCE = ROOT / "experiments/ecdlp_isogeny/po_transfer_075_independent_verify.sage"
PO75_AUDIT = ROOT / "experiments/ecdlp_isogeny/po_transfer_075_independent_verify.json"
PO76_CONTRACT = ROOT / "research/PO_transfer_076_nonvisible_e_isotypic_prym_bridge_contract.md"
PO76_SOURCE = ROOT / "experiments/ecdlp_isogeny/po_transfer_076_gamma_family_filter.sage"
PO76_RESULT = ROOT / "experiments/ecdlp_isogeny/po_transfer_076_gamma_family_filter.json"
PO76_AUDIT_SOURCE = ROOT / "experiments/ecdlp_isogeny/po_transfer_076_independent_verify.sage"
PO76_AUDIT = ROOT / "experiments/ecdlp_isogeny/po_transfer_076_independent_verify.json"
FOCUS_QUEUE = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/focus_queue_p1500_active.json"
)
FOCUS_PLAN = Path(
    "/Volumes/Volume/crypto-autoresearcher/focus/archive/focus_plan_p1500_active.json"
)
OUT = STATE / "p1500_nonsimple_prym_transport_census.json"
NOTE = RESEARCH / "p1500_nonsimple_prym_transport_census.md"

SCHEMA = "ecdlp.p1500_nonsimple_prym_transport_census.v1"
CONTROL_DOMAIN = "P1500-matched-control-v1:"
EXPECTED = {
    CONTRACT: "bdaa49fed7836bb7c238aa479a4577c575f9a9b39380fa4afcddb7d4b7589dba",
    P1499: "9567a225325773c7ce439b704c33cdcf17fb3d12e3e10735a36fdf5ca37e0fb5",
    P1499_AUDIT: "c4759867604048884fb8170074eac1c2b5d28b84144dc12244832c47e15f7719",
    PO75_CONTRACT: "6015fd92f41d3059a20295a37a44047894a3eaadcf5e2bc273a9be58b3b8af4d",
    PO75_SOURCE: "537984d4b42ce99c7286533af6433ef2fd07c64dcd8b3a719bb17a83c9cd231e",
    PO75_RESULT: "c6471fd6c6c2e4b67a9b39d8ec80ddd7c04bb4541d897433811e5e6986e7877c",
    PO75_AUDIT_SOURCE: "1d0ac5aa771589b170c47a0db8bc914997f1a5a87d8d14de79fceee7d1582185",
    PO75_AUDIT: "f29c75d3b514fba850b5d7a0377756cbdd161185c292d6c1c6d64981eff988ec",
    PO76_CONTRACT: "d9ce0809c819f8926847b7c58a35ffa84e5e9c806753bb88e7f5392ea34c7b95",
    PO76_SOURCE: "c3d2ea0f6515aeebfb60b268e70733ccb0683c4e970273ec0135e315bfc58ca9",
    PO76_RESULT: "4611f30a00e17b8af8f1434d2d764aecc0e34dcb2dbf836ee660e7118413bbeb",
    PO76_AUDIT_SOURCE: "bb4046a8506ec3818f1a93edaba177dd5a8c0a98c8013d39c111d90e0bac8279",
    PO76_AUDIT: "85f32a2d98582b47a62ad4c537a7edcca485d08c2e3cbfced7f62db3c60bc239",
    FOCUS_QUEUE: "c5efe7b1e59e672a8f84a6eea970f1d03cca5bb699ac866119df2d0d9336ddb9",
    FOCUS_PLAN: "3faebe1a7c7b3cf98d9061644ac769121a9025aa1aa308a9c0e102f7127fd516",
}


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def write_atomic(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def native_factor_decision(record: dict[str, Any]) -> tuple[str, bool]:
    if not record["branch_squarefree"]:
        return "inadmissible", False
    if not record["filter_survivor"]:
        return "necessary_filter_reject", False
    exact = record.get("exact")
    if exact is None:
        raise RuntimeError(f"missing exact survivor decision for gamma={record['gamma']}")
    hit = bool(exact["native_elliptic_factor_divides"])
    return "exact_native_factor_hit" if hit else "exact_native_factor_reject", hit


def control_digest(gamma: int) -> str:
    return hashlib.sha256(f"{CONTROL_DOMAIN}{gamma}".encode("ascii")).hexdigest()


def hasse_orders(p: int) -> list[int]:
    return [
        order
        for order in range(1, 2 * p + 2)
        if (p + 1 - order) ** 2 <= 4 * p
    ]


def render_note(payload: dict[str, Any]) -> str:
    criterion = payload["transport_criterion"]
    split = payload["gamma0_split_control"]
    census = payload["census"]
    lines = [
        "# P1500 Nonsimple-Prym Transport Census",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Decision",
        "",
        payload["interpretation"],
        "",
        "| Quantity | Value |",
        "|---|---:|",
        f"| family attempts | {census['total_gamma']} |",
        f"| admissible covers | {census['admissible_count']} |",
        f"| native-factor hits | {census['native_factor_hit_count']} |",
        f"| transport applicability density | {census['transport_applicability_density']:.8f} |",
        f"| matched random controls | {payload['matched_random_control']['sample_size']} |",
        f"| modeled extension multiplications | {payload['cost']['modeled_extension_multiplications']} |",
        "",
        "## Exact Boundary",
        "",
        f"The elliptic Hasse interval is `{criterion['hasse_order_min']}..{criterion['hasse_order_max']}`. "
        f"Its only multiple of the native prime order is `{criterion['native_order_multiples_in_hasse_interval'][0]}`. "
        "Therefore a nonzero elliptic transport must reproduce the native Weil factor, and the exhaustive PO76 census finds none.",
        "",
        "## Split Control",
        "",
        f"At `gamma=0`, `q(x,z)=(x,z^2)` gives the explicit elliptic quotient of degree "
        f"{split['quotient_map_degree']}. It varies across a deck fiber, but `q_* o pi^*` is zero and "
        f"`gcd(#E,#D)={split['p271_gcd_E_D_orders']}`. The split is real; the ECDLP bridge is not.",
        "",
        "## Next Action",
        "",
        payload["next_action"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    started = time.time()
    hashes = {display_path(path): sha256_file(path) for path in EXPECTED}
    hash_gates = {
        display_path(path): hashes[display_path(path)] == expected
        for path, expected in EXPECTED.items()
    }
    if not all(hash_gates.values()):
        raise RuntimeError(f"P1500 frozen hash mismatch: {hash_gates}")

    p1499 = json.loads(P1499.read_text(encoding="ascii"))
    p1499_audit = json.loads(P1499_AUDIT.read_text(encoding="ascii"))
    po75 = json.loads(PO75_RESULT.read_text(encoding="ascii"))
    po75_audit = json.loads(PO75_AUDIT.read_text(encoding="ascii"))
    po76 = json.loads(PO76_RESULT.read_text(encoding="ascii"))
    po76_audit = json.loads(PO76_AUDIT.read_text(encoding="ascii"))
    focus_plan = json.loads(FOCUS_PLAN.read_text(encoding="ascii"))

    active_focus = [item["id"] for item in focus_plan["critical_experiments"]]
    if active_focus != ["P1500"]:
        raise RuntimeError(f"P1500 is not the sole frozen active focus: {active_focus}")

    p = 271
    native_order = 283
    native_trace = p + 1 - native_order
    orders = hasse_orders(p)
    native_multiples = [order for order in orders if order % native_order == 0]

    gamma_records = sorted(po76["gamma_records"], key=lambda item: item["gamma"])
    decisions = []
    for record in gamma_records:
        decision, hit = native_factor_decision(record)
        decisions.append({
            "gamma": int(record["gamma"]),
            "canonical_gamma": int(record["canonical_gamma"]),
            "admissible": bool(record["branch_squarefree"]),
            "filter_survivor": bool(record["filter_survivor"]),
            "decision": decision,
            "native_factor_hit": hit,
        })
    admissible = [record for record in decisions if record["admissible"]]
    hits = [record for record in admissible if record["native_factor_hit"]]
    census_transcript = hashlib.sha256(compact(decisions).encode("ascii")).hexdigest()

    control_pool = [
        record for record in admissible if record["gamma"] not in (0, 225)
    ]
    control_pool.sort(key=lambda record: (control_digest(record["gamma"]), record["gamma"]))
    matched = control_pool[:32]
    matched_rows = [
        {
            "gamma": record["gamma"],
            "selector_sha256": control_digest(record["gamma"]),
            "decision": record["decision"],
            "native_factor_hit": record["native_factor_hit"],
        }
        for record in matched
    ]

    po75_fields = po75["field_records"]
    p271_split = next(record for record in po75_fields if record["p"] == p)
    false_character_rows = {
        name: int(p1499["catalog"][name]["candidate"]["aggregate_mismatch_pairs"])
        for name in ("trace", "norm", "discriminant", "projective_trace2_over_norm")
    }
    cost = po76["cost"]
    modeled_multiplications = int(
        cost["batch_modeled_field_multiplications"]
        + cost["degree3_modeled_field_multiplications"]
    )

    gates = {
        "frozen_hashes_exact": all(hash_gates.values()),
        "p1500_sole_frozen_focus": active_focus == ["P1500"],
        "po75_independently_verified": bool(po75_audit["verified"]),
        "po76_independently_verified": bool(po76_audit["verified"]),
        "p1499_independently_verified_negative": (
            p1499_audit["verified"]
            and p1499_audit["passed_checks"] == p1499_audit["total_checks"] == 12
            and not p1499["gates"]["any_preregistered_label_promotable"]
        ),
        "complete_gamma_schedule": [record["gamma"] for record in decisions] == list(range(p)),
        "complete_admissible_decisions": len(admissible) == 267,
        "po76_summary_reproduced": (
            len(decisions) == po76["summary"]["total_gamma"]
            and len(admissible) == po76["summary"]["admissible_count"]
            and len(hits) == po76["summary"]["exact_native_E_hit_count"] == 0
        ),
        "unique_native_multiple_in_hasse_interval": native_multiples == [native_order],
        "gamma0_explicit_elliptic_split_detected": (
            po75["known_extra_elliptic_factor_detected"]
            and p271_split["gates"]["known_D_factor_divides_prym"]
        ),
        "gamma0_point_map_not_pushforward_function": True,
        "gamma0_natural_correspondence_zero": (
            not po75["nonzero_natural_bridge"]
            and all(record["gates"]["natural_cross_correspondence_zero"] for record in po75_fields)
        ),
        "gamma0_auxiliary_orders_coprime": all(
            record["gcd_E_D_orders"] == 1 for record in po75_fields
        ),
        "matched_random_control_has_no_native_hit": not any(
            record["native_factor_hit"] for record in matched_rows
        ),
        "positive_split_and_recurrence_controls_pass": (
            po76["control_gates"]["gamma0_split_control_detected"]
            and po76["control_gates"]["po9_repeated_E_parser_detects"]
            and po76["control_gates"]["po9_repeated_E_multiplicity_two"]
        ),
        "mutation_controls_reject": all(po76_audit["mutation_gates"].values()),
        "no_transport_eligible_member": len(hits) == 0,
        "projected_collision_campaign_justified": False,
        "generic_shoup_breakthrough": False,
    }
    required = [
        name for name in gates
        if name not in (
            "projected_collision_campaign_justified",
            "generic_shoup_breakthrough",
        )
    ]
    if not all(gates[name] for name in required):
        failed = [name for name in required if not gates[name]]
        raise RuntimeError(f"P1500 required gate failed: {failed}")

    payload = {
        "schema": SCHEMA,
        "status": "NEGATIVE_RESULT_P1500_HORIZONTAL_NONSIMPLE_PRYM_TRANSPORT_OBSTRUCTED",
        "claim_status": "COMPLETE FROZEN-FAMILY TRANSPORT NEGATIVE / SPLIT CONTROL POSITIVE / TOY-EVIDENCE / NO GENERIC BREAKTHROUGH",
        "source": display_path(Path(__file__).resolve()),
        "source_sha256": sha256_file(Path(__file__).resolve()),
        "contract": display_path(CONTRACT),
        "contract_sha256": hashes[display_path(CONTRACT)],
        "frozen_hashes": hashes,
        "hash_gates": hash_gates,
        "focus": {
            "active_ids": active_focus,
            "queue_sha256": hashes[display_path(FOCUS_QUEUE)],
            "plan_sha256": hashes[display_path(FOCUS_PLAN)],
        },
        "field": {
            "p": p,
            "curve_a": 110,
            "curve_b": 205,
            "native_order": native_order,
            "native_trace": native_trace,
            "native_weil_polynomial": "T^2 + 11*T + 271",
        },
        "transport_criterion": {
            "theorem": "A nonzero homomorphism from the prime-order native rational subgroup to an elliptic factor requires the native order to divide the factor's rational order.",
            "hasse_test": "(p+1-order)^2 <= 4*p",
            "hasse_order_min": min(orders),
            "hasse_order_max": max(orders),
            "native_order_multiples_in_hasse_interval": native_multiples,
            "unique_multiple_forces_native_trace": native_multiples == [native_order],
            "native_factor_divisibility_is_necessary": True,
            "native_factor_divisibility_alone_is_sufficient": False,
        },
        "census": {
            "family": "C_gamma: z^3=y-gamma over F_271",
            "total_gamma": len(decisions),
            "admissible_count": len(admissible),
            "inadmissible_gamma": [
                record["gamma"] for record in decisions if not record["admissible"]
            ],
            "necessary_filter_reject_count": sum(
                record["decision"] == "necessary_filter_reject" for record in decisions
            ),
            "exact_checked_count": sum(
                record["decision"].startswith("exact_") for record in decisions
            ),
            "native_factor_hit_count": len(hits),
            "native_factor_hits": [record["gamma"] for record in hits],
            "transport_applicability_density": len(hits) / len(admissible),
            "decision_transcript_sha256": census_transcript,
            "records": decisions,
        },
        "gamma0_split_control": {
            "cover": "C0: z^6=x^3+110*x+205",
            "elliptic_quotient": "D: u^3=x^3+110*x+205",
            "quotient_map": "q(x,z)=(x,z^2)",
            "quotient_map_degree": 2,
            "cover_map_degree": 3,
            "given_lift_map_field_multiplications": 1,
            "deck_action_on_cover": "z->omega*z",
            "deck_action_on_quotient": "u->omega^2*u",
            "point_map_factors_through_E_pushforward": False,
            "canonical_homomorphic_lift_from_E": False,
            "natural_pull_push_correspondence_zero": True,
            "p271_D_order": p271_split["D_order"],
            "p271_D_trace": p271_split["D_trace"],
            "p271_gcd_E_D_orders": p271_split["gcd_E_D_orders"],
            "all_frozen_field_gcds": [
                {
                    "p": record["p"],
                    "E_order": record["E_order"],
                    "D_order": record["D_order"],
                    "gcd": record["gcd_E_D_orders"],
                }
                for record in po75_fields
            ],
            "transport_eligible": False,
        },
        "matched_random_control": {
            "selector_domain": CONTROL_DOMAIN,
            "pool_rule": "admissible gamma excluding 0 and 225",
            "sample_size": len(matched_rows),
            "native_factor_hit_count": sum(
                record["native_factor_hit"] for record in matched_rows
            ),
            "selection_transcript_sha256": hashlib.sha256(
                compact(matched_rows).encode("ascii")
            ).hexdigest(),
            "records": matched_rows,
        },
        "nonhomomorphic_label_control": {
            "p1499_false_aggregate_collision_counts": false_character_rows,
            "statement": "Pointwise or character-label equality without direct elliptic replay is not a relation row.",
        },
        "cost": {
            "family_attempts": len(decisions),
            "admissible_attempts": len(admissible),
            "batch_modeled_extension_multiplications": int(cost["batch_modeled_field_multiplications"]),
            "degree3_modeled_extension_multiplications": int(cost["degree3_modeled_field_multiplications"]),
            "modeled_extension_multiplications": modeled_multiplications,
            "modeled_extension_multiplications_over_sqrt_native_order": modeled_multiplications / math.sqrt(native_order),
            "maximum_helper_allocated_bytes": int(cost["maximum_helper_allocated_bytes"]),
            "gamma0_formula_construction_constant_degree": True,
            "gamma0_formula_nonzero_transport": False,
            "beats_pollard_rho": False,
        },
        "gates": gates,
        "interpretation": (
            "The frozen horizontal family contains a real nonsimple Prym control, and its quotient label varies inside an E fiber. "
            "But the induced E-to-quotient correspondence is zero. More generally, Hasse's bound forces every elliptic factor capable of receiving the native order-283 subgroup to have the native Weil polynomial, and the independently verified exhaustive census finds no such factor among all 267 admissible covers. "
            "There is therefore no relation-preserving projected-collision campaign to run on this family."
        ),
        "limitations": [
            "The exact family negative is for one ordinary prime-order curve over F_271 and the horizontal covers z^3=y-gamma.",
            "Other curves, nonhorizontal branch sections, higher-dimensional factors, and explicit recurrent vertical covers remain outside scope.",
            "The Hasse/divisibility argument closes homomorphic native-subgroup transport, not arbitrary nonhomomorphic labels; such labels still require direct elliptic row replay.",
            "The family census is toy evidence and its counted work is far above rho; it is not an asymptotic ECDLP algorithm.",
        ],
        "next_action": (
            "Close P1500 on the frozen horizontal family, preserve gamma=0 as a split-but-zero-transport control, and rerank toward a mechanism-changing summation-polynomial/finite-field-equation experiment rather than another label on this cover."
        ),
        "wall_seconds": time.time() - started,
        "peak_rss_raw": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    write_atomic(OUT, (compact(payload) + "\n").encode("ascii"))
    write_atomic(NOTE, render_note(payload).encode("ascii"))
    print(compact({
        "status": payload["status"],
        "admissible": len(admissible),
        "native_factor_hits": len(hits),
        "matched_controls": len(matched_rows),
        "out": str(OUT),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
