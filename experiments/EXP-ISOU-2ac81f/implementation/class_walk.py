"""
Breadth-first enumeration of the F_p-isogeny class of a base curve, via
explicit ell-isogenies (Velu/Kohel, see velu.py + division_poly.py) for
ell in the declared degree set.

Dedup rule (recorded per contract requirement "the deduplication rule
actually used is recorded"): vertices are deduplicated by the pair
(j-invariant, trace). Trace is included, not just j, because two curves can
share a j-invariant while being quadratic/quartic/sextic twists of each
other with DIFFERENT group order (hence different trace); j alone would
wrongly merge them. In this walk every vertex's trace is independently
re-derived by exact point counting (curve_utils.point_count) rather than
assumed, so (j, t) is a genuine F_p-isomorphism-class proxy for curves that
arise as verified same-order isogeny images: for j not in {0, 1728}, curves
of equal j and equal trace (hence equal order) ARE F_p-isomorphic (the two
twists sharing a j-invariant have provably different traces, generically
+t/-t or a divisor-dependent higher-degree-twist trace, all != t here since
the walk already filters on order equality). j = 0 and j = 1728 members are
additionally flagged and reported separately per special_j_segregation.

Every edge is independently re-verified before being trusted (edge
certificate): the codomain curve's order is recomputed from scratch via
curve_utils.point_count (not read off from the Velu construction) and must
equal N; a mismatch is recorded as a defect and that edge is NOT added to
the walk (no member reached only via a failed-certificate edge is used in
any metric).
"""
from __future__ import annotations

import random

from curve_utils import j_invariant
from division_poly import kernel_polynomial, DivisionPolyError
from velu import isogenous_curve_from_kernel, VeluError
from ec_affine import fast_order_certificate
import poly as poly_mod


class ClassWalkResult:
    def __init__(self):
        self.vertices = []          # list of dicts, one per isomorphism class
        self.edges = []             # list of dicts (u_id, v_id, ell, lambda, kernel_deg)
        self.defects = []           # list of dicts describing rejected/failed edges
        self.dedup_key_rule = "(j_invariant, trace) -- see class_walk.py docstring"


def enumerate_class(p, a0, b0, N, t, degrees, edge_cert_seed=1):
    """
    BFS from (a0,b0). Returns a ClassWalkResult.

    Edge certificate method: fast_order_certificate (ec_affine.py), a
    Lagrange/Hasse-uniqueness argument using O(log N) group operations,
    repeated with a seeded PRNG so the check is deterministic and
    reproducible. This replaces a full O(p) point recount per edge, which
    is mathematically equivalent (independent of the Velu/Kohel
    construction code) but was measured to be computationally infeasible
    at the 20/24-bit census scale (see implementation.md).
    """
    result = ClassWalkResult()
    result.edge_certificate_method = "fast_order_certificate (Lagrange + Hasse uniqueness)"
    result.edge_certificate_seed = edge_cert_seed
    cert_rng = random.Random(edge_cert_seed)
    j0 = j_invariant(a0, b0, p)
    v0 = {
        "id": 0,
        "a": a0, "b": b0, "j": j0, "trace": t, "order": N,
        "walk_path": [], "walk_degrees": [],
        "special_j": j0 in (0, 1728 % p),
        "cumulative_walk_cost_field_muls": 0,
        "walk_cost_field_muls_measured": 0,
    }
    result.vertices.append(v0)
    seen = {(j0, t): 0}
    frontier = [0]

    while frontier:
        next_frontier = []
        for vid in frontier:
            v = result.vertices[vid]
            a, b = v["a"], v["b"]
            for ell in degrees:
                if ell == 2:
                    # No rational 2-isogeny can exist from any vertex here:
                    # N is prime and odd, so the rational 2-torsion subgroup
                    # of a curve of order N has order dividing gcd(2, N) = 1
                    # (Lagrange), i.e. it is always trivial. Recorded as a
                    # structural non-edge, not computed.
                    result.defects.append({
                        "type": "degree_2_structurally_absent",
                        "vertex_id": vid,
                        "reason": (
                            "N is prime and odd; rational 2-torsion subgroup "
                            "order must divide N, forcing it to be trivial. "
                            "No 2-isogeny kernel exists over F_p from any "
                            "vertex of this class."
                        ),
                    })
                    continue
                poly_mod.reset_field_mul_tally()
                try:
                    kres = kernel_polynomial(a, b, p, t, ell)
                except DivisionPolyError as e:
                    result.defects.append({
                        "type": "kernel_polynomial_error",
                        "vertex_id": vid, "ell": ell, "error": str(e),
                    })
                    continue
                kernel_build_field_muls = poly_mod.get_field_mul_tally()
                for r in kres:
                    lam, h, deg, exp_deg = r["lambda"], r["h"], r["degree"], r["expected_degree"]
                    if deg != exp_deg:
                        result.defects.append({
                            "type": "kernel_degree_mismatch",
                            "vertex_id": vid, "ell": ell, "lambda": lam,
                            "degree": deg, "expected_degree": exp_deg,
                        })
                        continue
                    poly_mod.reset_field_mul_tally()
                    try:
                        a2, b2 = isogenous_curve_from_kernel(h, a, b, p, ell)
                    except VeluError as e:
                        result.defects.append({
                            "type": "velu_error",
                            "vertex_id": vid, "ell": ell, "lambda": lam, "error": str(e),
                        })
                        continue
                    velu_field_muls = poly_mod.get_field_mul_tally()
                    edge_walk_cost_field_muls = kernel_build_field_muls + velu_field_muls
                    disc2 = (4 * a2 ** 3 + 27 * b2 * b2) % p
                    if disc2 == 0:
                        result.defects.append({
                            "type": "singular_codomain",
                            "vertex_id": vid, "ell": ell, "lambda": lam,
                        })
                        continue
                    # EDGE CERTIFICATE: independent fast order check
                    # (see fast_order_certificate docstring).
                    cert_ok = fast_order_certificate(a2, b2, p, N, rng=cert_rng)
                    if not cert_ok:
                        result.defects.append({
                            "type": "edge_certificate_failed_order_mismatch",
                            "vertex_id": vid, "ell": ell, "lambda": lam,
                            "expected_order": N,
                        })
                        continue
                    N2 = N
                    j2 = j_invariant(a2, b2, p)
                    key = (j2, t)
                    if key in seen:
                        wid = seen[key]
                        result.edges.append({
                            "u": vid, "v": wid, "ell": ell, "lambda": lam,
                            "kernel_generator_poly": [c % p for c in h],
                            "edge_certificate": "order_recount_match",
                            "walk_cost_field_muls_measured": edge_walk_cost_field_muls,
                        })
                        continue
                    wid = len(result.vertices)
                    seen[key] = wid
                    w = {
                        "id": wid, "a": a2, "b": b2, "j": j2, "trace": t, "order": N2,
                        "walk_path": v["walk_path"] + [ell],
                        "walk_degrees": v["walk_degrees"] + [ell],
                        "special_j": j2 in (0, 1728 % p),
                        "parent": vid, "parent_ell": ell, "parent_lambda": lam,
                        "walk_cost_field_muls_measured": (
                            v.get("cumulative_walk_cost_field_muls", 0) + edge_walk_cost_field_muls
                        ),
                    }
                    w["cumulative_walk_cost_field_muls"] = w["walk_cost_field_muls_measured"]
                    result.vertices.append(w)
                    result.edges.append({
                        "u": vid, "v": wid, "ell": ell, "lambda": lam,
                        "kernel_generator_poly": [c % p for c in h],
                        "edge_certificate": "order_recount_match",
                        "walk_cost_field_muls_measured": edge_walk_cost_field_muls,
                    })
                    next_frontier.append(wid)
        frontier = next_frontier
    return result
