"""
Capped BFS isogeny-class enumeration, structurally identical to
class_walk.enumerate_class but with an ENFORCED (checked every vertex, not
just after the fact) vertex-count and wall-clock cap, needed because some
28-bit craters are large enough that unbounded BFS blows the per-run
budget (measured: one 28-bit curve did not finish exploring its crater
within a 600s timeout with STEP_PRIMES up to 13 -- see implementation.md).
This is the actual enforcement mechanism behind the
BOUNDED_WALK_MAX_VERTICES / BOUNDED_WALK_MAX_SECONDS documented in
isogeny_transfer_census.py.
"""
from __future__ import annotations

import time

from curve_utils import j_invariant
from division_poly import kernel_polynomial, DivisionPolyError
from velu import isogenous_curve_from_kernel, VeluError
from ec_affine import fast_order_certificate
import random


def enumerate_class_capped(p, a0, b0, N, t, degrees, max_vertices, max_seconds, edge_cert_seed=1):
    t0 = time.time()
    cert_rng = random.Random(edge_cert_seed)
    j0 = j_invariant(a0, b0, p)
    vertices = [{"id": 0, "a": a0, "b": b0, "j": j0, "trace": t, "order": N}]
    seen = {(j0, t): 0}
    frontier = [0]
    edges = 0
    defects = 0
    capped = False

    while frontier and not capped:
        next_frontier = []
        for vid in frontier:
            if len(vertices) >= max_vertices or (time.time() - t0) >= max_seconds:
                capped = True
                break
            v = vertices[vid]
            a, b = v["a"], v["b"]
            for ell in degrees:
                if len(vertices) >= max_vertices or (time.time() - t0) >= max_seconds:
                    capped = True
                    break
                try:
                    kres = kernel_polynomial(a, b, p, t, ell)
                except DivisionPolyError:
                    defects += 1
                    continue
                for r in kres:
                    if r["degree"] != r["expected_degree"]:
                        defects += 1
                        continue
                    try:
                        a2, b2 = isogenous_curve_from_kernel(r["h"], a, b, p, ell)
                    except VeluError:
                        defects += 1
                        continue
                    disc2 = (4 * a2 ** 3 + 27 * b2 * b2) % p
                    if disc2 == 0:
                        defects += 1
                        continue
                    cert_ok = fast_order_certificate(a2, b2, p, N, rng=cert_rng)
                    if not cert_ok:
                        defects += 1
                        continue
                    j2 = j_invariant(a2, b2, p)
                    key = (j2, t)
                    if key in seen:
                        edges += 1
                        continue
                    if len(vertices) >= max_vertices:
                        capped = True
                        break
                    wid = len(vertices)
                    seen[key] = wid
                    vertices.append({"id": wid, "a": a2, "b": b2, "j": j2, "trace": t, "order": N})
                    edges += 1
                    next_frontier.append(wid)
            if capped:
                break
        frontier = next_frontier

    elapsed = time.time() - t0
    orders_seen = sorted(set(v["order"] for v in vertices))
    return {
        "vertices_visited": len(vertices),
        "edges": edges,
        "wall_seconds": elapsed,
        "capped": capped,
        "defects": defects,
        "orders_seen": orders_seen,
        "order_invariance_holds": orders_seen == [N],
        "vertex_keys": [(v["j"], v["trace"]) for v in vertices],
        "j_invariants_visited": sorted(set(v["j"] for v in vertices)),
    }
