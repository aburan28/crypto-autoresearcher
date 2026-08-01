#!/usr/bin/env python3
"""EXP-CREP-001 representation package builder (deterministic, stdlib only).

Constructs the typed representation packages for the eight frozen routes
(ROUTE-01..ROUTE-08) and the two frozen calibration fixtures
(CAL-PASS-CREP-001, CAL-FAIL-CREP-001), per the frozen route rules in
experiments/EXP-CREP-001/specification.yaml.

Each package is a static typed document: a dependency graph from the compact
pair-product generators to the z_R support-factor sink, one typed
construction map per edge (input size exponent, output size exponent, cost
exponent in B), and a declared exponent certificate. Certificate aggregates
are computed from the construction maps by the phase-max rule so that the
certificate is exactly the aggregate of the maps; the two calibration
fixtures carry the spec-frozen declared exponents (which equal the
aggregates by construction).

The declared exponents are the honest textbook bounds for each standard
algebraic route on this instance model (N = B^5, r_R of degree Theta(B^2)
over the complete chart decomposition, Theta(B^3) target-dependent scalar
coordinates when represented). Semantics live only in the frozen verifier
engine (crep-toy-v1); packages carry no executable code.
"""
import json
import os
import sys
from fractions import Fraction

BUILDER_VERSION = "crep-packages-v1"

CAP_PRE = Fraction(9, 4)
CAP_ON = Fraction(5, 4)

ROUTE_IDS = [
    "ROUTE-01-component-resultants",
    "ROUTE-02-quotient-ring-resultants",
    "ROUTE-03-split-norms",
    "ROUTE-04-multipoint-evaluation",
    "ROUTE-05-modular-composition",
    "ROUTE-06-power-projection",
    "ROUTE-07-subresultant-hgcd",
    "ROUTE-08-displacement-representation",
]


def node(nid, kind, phase, produces, retained, size_exp, params=None):
    n = {
        "id": nid,
        "kind": kind,
        "phase": phase,
        "produces": produces,
        "retained": retained,
        "declared": {"size_exponent_in_B": size_exp},
    }
    if params:
        n["params"] = params
    return n


def edge(frm, to, in_exp, out_exp, cost_exp):
    return {
        "from": frm,
        "to": to,
        "map": {
            "input_size_exponent_in_B": in_exp,
            "output_size_exponent_in_B": out_exp,
            "cost_exponent_in_B": cost_exp,
        },
    }


def aggregate_certificate(nodes, edges, advice_exp, td_coords_exp):
    """Phase-max aggregation rule (polynomial-sum; polylog factors absorbed).

    Edge phase = phase of the edge's target node (an edge into an online
    node is charged online). Retained preprocessing state = maximum declared
    size exponent over retained preprocessing nodes. Online workspace =
    maximum over online-edge output exponents and online-node size exponents.
    """
    by_id = {n["id"]: n for n in nodes}
    pre_edges = [e for e in edges if by_id[e["to"]]["phase"] == "preprocessing"]
    on_edges = [e for e in edges if by_id[e["to"]]["phase"] == "online"]
    pre_time = max([e["map"]["cost_exponent_in_B"] for e in pre_edges], default=0)
    on_time = max([e["map"]["cost_exponent_in_B"] for e in on_edges], default=0)
    pre_state = max([n["declared"]["size_exponent_in_B"]
                     for n in nodes if n["phase"] == "preprocessing" and n["retained"]], default=0)
    on_ws = max([e["map"]["output_size_exponent_in_B"] for e in on_edges]
                + [n["declared"]["size_exponent_in_B"] for n in nodes if n["phase"] == "online"],
                default=0)
    return {
        "preprocessing": {
            "time_exponent_in_B": pre_time,
            "retained_advice_exponent_in_B": advice_exp,
            "retained_state_exponent_in_B": pre_state,
        },
        "online": {
            "time_exponent_in_B": on_time,
            "workspace_exponent_in_B": on_ws,
            "materialized_target_dependent_coordinates_exponent_in_B": td_coords_exp,
        },
        "replay_accounting": {
            "dyadic_queries_per_tuple": "O(log B)",
            "positive_and_negative_queries_included": True,
            "final_exact_source_verification_included": True,
        },
        "aggregation_rule": "phase-wise maximum over typed construction-map exponents (polynomial-sum rule); polylogarithmic factors absorbed",
    }


def make_package(package_id, kind, route_id, run_id, nodes, edges, advice_exp, td_coords_exp, notes):
    sinks = [n["id"] for n in nodes if n["produces"] == "support_factor"]
    roots = sorted({n["id"] for n in nodes} - {e["to"] for e in edges})
    cert = aggregate_certificate(nodes, edges, advice_exp, td_coords_exp)
    cert["notes"] = notes
    return {
        "package_id": package_id,
        "kind": kind,
        "route_id": route_id,
        "target": "z_R",
        "dependency_graph": {
            "nodes": nodes,
            "edges": edges,
            "roots": roots,
            "sinks": sinks,
        },
        "exponent_certificate": cert,
        "semantics": {"engine": "crep-toy-v1", "options": {}},
        "provenance": {
            "built_by": "experiments/EXP-CREP-001/packages/build_packages.py",
            "built_at_run": run_id,
            "notes": notes,
        },
    }


def build_cal_pass(run_id):
    """CAL-PASS-CREP-001 (frozen must-pass synthetic fixture).

    Restricted-existence index constructor: preprocessing computes
    dyadic-interval OR-bits over the static pair-product relation table
    (declared: preprocessing work 2, retained state 1 in B, polylog
    absorbed); online per target reads B labels times O(log B) dyadic
    probes (declared online exponent 1); replay descends dyadically with
    O(log B) calls per tuple. Synthetic instrument only; NOT a curve
    construction and NOT evidence about H-CREP-001.
    """
    nodes = [
        node("n0", "load_pair_product_generators", "preprocessing", "compact_generators", False, 2),
        node("n1", "build_static_relation_table", "preprocessing", "static_relation_table", False, 2),
        node("n2", "build_dyadic_index", "preprocessing", "dyadic_index", True, 1),
        node("n3", "restricted_existence_probe", "online", "existence_bits", True, 1),
        node("n4", "dyadic_replay", "online", "replay_witness", True, 1),
        node("n5", "emit_support_factor", "online", "support_factor", True, 1),
    ]
    edges = [
        edge("n0", "n1", 2, 2, 2),
        edge("n1", "n2", 2, 1, 2),
        edge("n2", "n3", 1, 1, 1),
        edge("n0", "n4", 2, 1, 1),
        edge("n3", "n4", 1, 1, 1),
        edge("n4", "n5", 1, 1, 1),
    ]
    return make_package("CAL-PASS-CREP-001", "calibration", None, run_id, nodes, edges, 1, 0,
                        "frozen must-pass calibration fixture (spec calibration_fixtures); synthetic instrument, not a route")


def build_cal_fail(run_id):
    """CAL-FAIL-CREP-001 (frozen must-fail synthetic fixture).

    Componentwise reference constructor with declared online exponent 3 in B
    (B labels times B^2 coefficient work) and Theta(B^3) target-dependent
    translated coordinates. Expected verdict: FAIL at V3 (and V6).
    """
    nodes = [
        node("n0", "load_pair_product_generators", "preprocessing", "compact_generators", False, 2),
        node("n1", "build_chart_index", "preprocessing", "chart_index", True, 2),
        node("n2", "materialize_translated_endpoints", "online", "translated_endpoints", True, 3),
        node("n3", "componentwise_gcd", "online", "support_intermediate", True, 1),
        node("n4", "tuple_replay", "online", "replay_witness", True, 1),
        node("n5", "emit_support_factor", "online", "support_factor", True, 1),
    ]
    edges = [
        edge("n0", "n1", 2, 2, 2),
        edge("n1", "n2", 2, 3, 3),
        edge("n2", "n3", 3, 1, 2),
        edge("n0", "n4", 2, 1, 1),
        edge("n3", "n4", 1, 1, 1),
        edge("n4", "n5", 1, 1, 1),
    ]
    return make_package("CAL-FAIL-CREP-001", "calibration", None, run_id, nodes, edges, 1, 3,
                        "frozen must-fail calibration fixture (spec calibration_fixtures); expected FAIL at V3 and V6")


def build_expansion_route(route_id, run_id, algebra_kind, algebra_note):
    """Shared shape of the represented-resultant routes: materialize the
    Theta(B^3) target-dependent coefficient vector online, then apply the
    route's standard algebraic extraction (cost exponent 2 in B on the
    represented input)."""
    nodes = [
        node("n0", "load_pair_product_generators", "preprocessing", "compact_generators", True, 2),
        node("n1", "build_chart_index", "preprocessing", "chart_index", True, 2),
        node("n2", "materialize_resultant_coefficients", "online", "resultant_coefficient_vector", True, 3),
        node("n3", algebra_kind, "online", "support_intermediate", True, 1),
        node("n4", "tuple_replay", "online", "replay_witness", True, 1),
        node("n5", "emit_support_factor", "online", "support_factor", True, 1),
    ]
    edges = [
        edge("n0", "n1", 2, 2, 2),
        edge("n1", "n2", 2, 3, 3),
        edge("n2", "n3", 3, 1, 2),
        edge("n0", "n4", 2, 1, 1),
        edge("n3", "n4", 1, 1, 1),
        edge("n4", "n5", 1, 1, 1),
    ]
    return make_package(route_id, "route", route_id, run_id, nodes, edges, 1, 3, algebra_note)


def build_route_02(run_id):
    """ROUTE-02 quotient-ring-resultants: assumes r_R mod g_I has already
    been supplied (the EV-CRYPTO-002 closed sheet). The supplied resultant
    is an oracle node and a forbidden payload; recorded failed_duplicate
    with owner EV-CRYPTO-002 by the dedup control."""
    nodes = [
        node("n0", "load_pair_product_generators", "preprocessing", "compact_generators", True, 2),
        node("n1", "supplied_input", "online", "supplied_resultant", True, 3,
             params={"payload": "supplied_resultant", "assumed": "r_R mod g_I supplied (EV-CRYPTO-002 closed sheet)"}),
        node("n2", "quotient_ring_gcd", "online", "support_intermediate", True, 1),
        node("n3", "tuple_replay", "online", "replay_witness", True, 1),
        node("n4", "emit_support_factor", "online", "support_factor", True, 1),
    ]
    edges = [
        edge("n1", "n2", 3, 1, 1),
        edge("n0", "n3", 2, 1, 1),
        edge("n2", "n3", 1, 1, 1),
        edge("n3", "n4", 1, 1, 1),
    ]
    return make_package("ROUTE-02-quotient-ring-resultants", "route",
                        "ROUTE-02-quotient-ring-resultants", run_id, nodes, edges, 0, 3,
                        "quotient-ring resultant route; assumes r_R mod g_I supplied (closed sheet EV-CRYPTO-002)")


def build_route(route_id, run_id):
    if route_id == "ROUTE-01-component-resultants":
        return build_expansion_route(route_id, run_id, "componentwise_gcd",
                                     "componentwise resultant construction over the complete-chart strata; materializes the represented degree-B^2 target coefficient vector (Theta(B^3) target-dependent coordinates)")
    if route_id == "ROUTE-02-quotient-ring-resultants":
        return build_route_02(run_id)
    if route_id == "ROUTE-03-split-norms":
        return build_expansion_route(route_id, run_id, "norm_from_extension",
                                     "norm-from-extension / split-norm constructor over the represented resultant in a constant-degree splitting extension")
    if route_id == "ROUTE-04-multipoint-evaluation":
        return build_expansion_route(route_id, run_id, "multipoint_evaluate",
                                     "multipoint evaluation and interpolation (Borodin-Moenck lineage) on the represented degree-B^2 resultant at B target labels")
    if route_id == "ROUTE-05-modular-composition":
        return build_expansion_route(route_id, run_id, "modular_compose",
                                     "modular-composition constructor (Brent-Kung / Kedlaya-Umans lineage) on the represented degree-B^2 resultant")
    if route_id == "ROUTE-06-power-projection":
        return build_expansion_route(route_id, run_id, "power_project",
                                     "power-projection / transposed-evaluation constructor on the represented degree-B^2 resultant")
    if route_id == "ROUTE-07-subresultant-hgcd":
        return build_expansion_route(route_id, run_id, "subresultant_chain",
                                     "subresultant / half-gcd chain constructor including truncated resultants (Moroz-Schost lineage) on the represented resultant; matches pinned duplicate pattern IDEA-063 (post-factor subresultant)")
    if route_id == "ROUTE-08-displacement-representation":
        return build_expansion_route(route_id, run_id, "displacement_solve",
                                     "low-displacement-rank (Sylvester/Cauchy) representation constructor acting on the pair-product generators; building the displacement generators materializes the represented resultant coefficients; matches pinned duplicate pattern IDEA-071 (displacement reporting from supplied represented data)")
    raise ValueError("unknown route: %s" % route_id)


def main():
    out_root = sys.argv[1]
    run_id = sys.argv[2]
    which = sys.argv[3]  # "fixtures" | "routes-1-4" | "routes-5-8"
    built = []
    if which == "fixtures":
        packages = [build_cal_pass(run_id), build_cal_fail(run_id)]
    elif which == "routes-1-4":
        packages = [build_route(r, run_id) for r in ROUTE_IDS[:4]]
    elif which == "routes-5-8":
        packages = [build_route(r, run_id) for r in ROUTE_IDS[4:]]
    else:
        raise ValueError("unknown build set: %s" % which)
    for pkg in packages:
        pdir = os.path.join(out_root, pkg["package_id"])
        os.makedirs(pdir, exist_ok=True)
        path = os.path.join(pdir, "package.json")
        with open(path, "w") as f:
            json.dump(pkg, f, indent=2, sort_keys=True)
            f.write("\n")
        built.append(path)
        print("built %s" % path)


if __name__ == "__main__":
    main()
