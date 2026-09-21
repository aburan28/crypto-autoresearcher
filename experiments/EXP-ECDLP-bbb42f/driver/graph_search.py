"""
Bounded ordinary isogeny graph search from a starting curve, up to the
degree budget ell_max = floor(sqrt(N)) (specification.yaml
inputs.isogeny_degree_budget), checking the E1/E2/E3 special-family
predicates at every visited node.

STEP-PRIME SET: {2, 3} (specification.yaml inputs.isogeny_step_primes).
ell_0=2 alone was tried first and found STRUCTURALLY VACUOUS for every
curve this experiment samples: curve_sampling_rule requires prime N, and a
rational point of order 2 needs 2 | N (Lagrange), impossible for odd N --
confirmed empirically (0/60 census curves had any 2-torsion) before being
proven. ell_0=3 does not have this obstruction: a degree-3 kernel {O,T,-T}
only needs T's x-coordinate to be Frobenius-fixed (a root of the 3-division
polynomial in F_p), not T itself to be an F_p-point, so Lagrange on N never
applies to it (see isogeny3.py). ell_0=2 is kept in the step set (it is
correctly implemented and does fire for curves without a prime-order
constraint, e.g. within isogeny3.py's own test suite) but is not expected
to contribute any edges for this experiment's own curve population; this
is disclosed here rather than silently dropped from the driver.

IMPLEMENTATION NOTE ON "MEET-IN-THE-MIDDLE" (protocol-relevant, recorded
in implementation.md): Tate's isogeny theorem (1966) -- two elliptic curves
over the same finite field are isogenous over that field IFF they have the
same number of points -- means every curve reachable from the origin by any
same-field isogeny (any degree, any composition) has EXACTLY the origin's N.
Since E1 (N == p) and E2 (k = ord_N(p)) depend only on N, their truth value
is fixed at the origin, before any walk begins, and cannot change along the
walk. There is therefore no independent "target side" to meet from: the
target set, if the origin's own class is special, coincides with the whole
reachable class; if the origin's class is not special, the target set
intersected with the reachable class is provably empty. A genuine two-sided
meet-in-the-middle needs two independently generated frontiers converging on
a shared unknown midpoint; here the only "other side" IS the class being
explored, so this driver implements a single bounded BFS of the reachable
class (still charged and reported in the same group-operation-equivalent
units the MITM cost model uses) rather than fabricating a second, vacuous
search side. This is disclosed as a protocol deviation from the literal
"BFS/MITM" phrasing, justified by the theorem above, not silently
substituted.
"""
from __future__ import annotations
import math
import time
from .isogeny2 import two_torsion_roots, isogenous_curve_2
from .isogeny3 import psi_3_roots, isogenous_curve_3
from .predicates import classify
from .ecc import OpCounter
from .curve_order import compute_group_order
from .ecc import seeded_rng
from .exitmap import is_self_map


def degree_budget_steps(N: int) -> int:
    """Retained name for compatibility with callers; now returns ell_max
    itself (a total-degree budget, since steps mix primes 2 and 3), not a
    single-prime step count."""
    return math.isqrt(N)


def bounded_isogeny_search(
    a0: int, b0: int, p: int, N0: int, k_max: int,
    max_steps: int, max_nodes: int, time_budget_seconds: float,
    spot_check_every: int = 200,
):
    """BFS over the {2,3}-isogeny graph from (a0,b0), up to total degree
    ell_max = max_steps (a misnomer kept for call-site compatibility; see
    degree_budget_steps) or max_nodes visited nodes, whichever binds first,
    or time_budget_seconds wall clock. Each frontier node carries its
    accumulated total isogeny degree; a step is taken only if the
    resulting degree stays within ell_max.

    Returns a dict: status (NOT_FOUND | FOUND | HALTED_ON_BUDGET), min_ell
    (int or None), hit (node dict or None), nodes_visited, max_degree_reached,
    crater_closed (bool), field_ops (OpCounter dict), tate_spot_checks
    (list of pass/fail), wall_seconds.
    """
    ell_max = max_steps
    t_start = time.time()
    ctr = OpCounter()
    origin_key = (a0, b0)
    visited = {origin_key: 1}
    frontier = [(a0, b0, 1)]  # (a, b, accumulated_degree)
    max_degree_reached = 1
    tate_checks = []
    nodes_visited = 1
    status = None
    hit = None
    min_ell = None
    exitmap_voids = []

    # origin predicate check at ell=0 (this is where E1/E2/E3 membership is
    # actually decided, per the module docstring)
    cls0 = classify(N0, p, k_max)
    if cls0["special"]:
        return {
            "status": "FOUND",
            "min_ell": 0,
            "hit": {"a": a0, "b": b0, "N": N0, "classification": cls0, "depth": 0},
            "nodes_visited": 1,
            "max_depth_reached": 0,
            "crater_closed": False,
            "field_ops": ctr.to_dict(),
            "tate_spot_checks": [],
            "exitmap_voids": [],
            "wall_seconds": time.time() - t_start,
            "note": "special at ell=0 (origin curve itself); no walk needed or performed",
        }

    def _consider(a2, b2, new_degree):
        nonlocal nodes_visited, max_degree_reached, hit, min_ell, status
        key = (a2, b2)
        if key in visited:
            return None
        visited[key] = new_degree
        nodes_visited += 1
        max_degree_reached = max(max_degree_reached, new_degree)

        if nodes_visited % spot_check_every == 0:
            # empirical Tate-invariance spot check (see module docstring);
            # any mismatch is a fatal implementation bug, not a research finding
            Nk, _, _ = compute_group_order(a2, b2, p, seeded_rng(a2, b2, p))
            tate_checks.append({"node": key, "N": Nk, "matches_origin": Nk == N0})
            if Nk != N0:
                raise AssertionError(
                    f"Tate isogeny-invariance violated at node {key}: N={Nk} != origin N={N0}. "
                    "This contradicts a proven theorem and indicates an isogeny-formula bug, "
                    "not a research finding; halting rather than reporting corrupted data."
                )

        cls = classify(N0, p, k_max)  # N is provably identical to origin's; see Tate note
        if cls["special"]:
            if is_self_map(a0, b0, a2, b2, p):
                # INV-EXITMAP: this is an endomorphism of the origin curve
                # (isomorphic return), not a genuine transfer to a distinct
                # E''. Void per CTRL-EXITMAP-CONSISTENCY; do not credit or
                # stop on it, keep searching.
                exitmap_voids.append({"a": a2, "b": b2, "degree": new_degree})
                return "continue"
            hit = {"a": a2, "b": b2, "N": N0, "classification": cls, "degree": new_degree}
            min_ell = new_degree
            status = "FOUND"
            return "stop"
        return "continue"

    qi = 0
    depth_capped = False
    while qi < len(frontier):
        cur_a, cur_b, cur_degree = frontier[qi]
        qi += 1
        if time.time() - t_start > time_budget_seconds:
            status = "HALTED_ON_BUDGET"
            break
        if nodes_visited >= max_nodes:
            status = "HALTED_ON_BUDGET"
            break

        # ell_0 = 2 step (see module docstring: expected vacuous for this
        # experiment's prime-N population, kept for correctness/generality)
        if cur_degree * 2 <= ell_max:
            for x0 in two_torsion_roots(cur_a, cur_b, p):
                a2, b2, t = isogenous_curve_2(cur_a, cur_b, p, x0)
                ctr.field_mults += 3
                outcome = _consider(a2, b2, cur_degree * 2)
                if outcome is not None:
                    frontier.append((a2, b2, cur_degree * 2))
                if outcome == "stop":
                    break
            if status == "FOUND":
                break
        else:
            depth_capped = True

        # ell_0 = 3 step
        if cur_degree * 3 <= ell_max:
            for x0 in psi_3_roots(cur_a, cur_b, p):
                a3, b3 = isogenous_curve_3(cur_a, cur_b, p, x0)
                ctr.field_mults += 10
                outcome = _consider(a3, b3, cur_degree * 3)
                if outcome is not None:
                    frontier.append((a3, b3, cur_degree * 3))
                if outcome == "stop":
                    break
            if status == "FOUND":
                break
        else:
            depth_capped = True

    crater_closed = False
    if status is None:
        # loop exhausted the frontier without hitting the wall-clock or
        # node-count safety caps. Per specification.yaml stopping_rules
        # ("Every path search stops at ell_max and reports NOT_FOUND"),
        # reaching the degree budget (depth_capped) or closing the whole
        # reachable class before it (not depth_capped) are both legitimate
        # NOT_FOUND outcomes -- crater_closed distinguishes a stronger
        # negative (whole class enumerated, no special curve anywhere in
        # it) from an ordinary budget-bound negative.
        status = "NOT_FOUND"
        crater_closed = not depth_capped

    return {
        "status": status,
        "min_ell": min_ell,
        "hit": hit,
        "nodes_visited": nodes_visited,
        "max_depth_reached": max_degree_reached,
        "crater_closed": crater_closed,
        "field_ops": ctr.to_dict(),
        "tate_spot_checks": tate_checks,
        "exitmap_voids": exitmap_voids,
        "wall_seconds": time.time() - t_start,
    }
