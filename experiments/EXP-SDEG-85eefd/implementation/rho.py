"""Pollard rho baseline (C-8): negation map, r = 32 adding walk, fruitless-cycle
handling; group operations reported against 0.886 sqrt(q).

Walk: W_{i+1} = canon(W_i + M_{j(W_i)}), j(W) = x(W) mod 32, canon picks the
representative with y <= (p - 1) / 2 and negates the (a, b) coefficients
when it flips. M_j = c_j G + d_j Q with (c_j, d_j) and the start from labels
'<ns>|rho_walk|L<L>|<seed>|<t>|<j>' (not fixed by the protocol; see
implementation.md). Collision detection stores every visited canonical point
(memory O(sqrt q), trivial at q <= 2^25). A revisit with equal coefficients is
a fruitless cycle: escape by doubling the minimum-x point of the cycle.
Group operations are counted via the instrumented curve (field ops too).
"""

from __future__ import annotations

import math

import labels
from fparith import INF, Curve, Fp, OpCounter
from verify import VCurve

R_WALK = 32


def rho_target_k(fx, t: int, ns: str) -> int:
    return labels.h(labels.cell_lab(ns, "rho", fx["L"], fx["seed"], t)) % fx["N"]


def solve(fx, Q, t: int, ns: str, max_restarts: int = 64) -> dict:
    p, q = fx["p"], fx["N"]
    counter = OpCounter()
    F = Fp(p, counter)
    curve = Curve(F, fx["a"], fx["b"])
    G = tuple(fx["G"])
    half = (p - 1) // 2
    group_ops = {"walk": 0, "precompute": 0, "escape": 0}
    fruitless = 0
    restarts = 0

    def canon(P, a, b):
        if P is not INF and P[1] > half:
            return (P[0], p - P[1]), (-a) % q, (-b) % q
        return P, a, b

    def counted_mul(k, P, bucket):
        before = counter.inv
        R = curve.mul(k, P)
        group_ops[bucket] += counter.inv - before  # one inversion per affine add/double
        return R

    if Q is INF:
        return {"t": t, "k": 0, "solved": True, "degenerate_target": True, "group_ops": group_ops,
                "ops": counter.as_dict(), "fruitless_cycles": 0, "restarts": 0}
    while restarts <= max_restarts:
        M = []
        for j in range(R_WALK):
            c = labels.uniform(labels.cell_lab(ns, "rho_walk", fx["L"], fx["seed"], t, f"{restarts}.{j}c"), q)
            d = labels.uniform(labels.cell_lab(ns, "rho_walk", fx["L"], fx["seed"], t, f"{restarts}.{j}d"), q)
            P = curve.add(counted_mul(c, G, "precompute"), counted_mul(d, Q, "precompute"))
            group_ops["precompute"] += 1
            M.append((P, c, d))
        a0 = labels.uniform(labels.cell_lab(ns, "rho_walk", fx["L"], fx["seed"], t, f"{restarts}.start_a"), q)
        b0 = labels.uniform(labels.cell_lab(ns, "rho_walk", fx["L"], fx["seed"], t, f"{restarts}.start_b"), q)
        W = curve.add(counted_mul(a0, G, "precompute"), counted_mul(b0, Q, "precompute"))
        group_ops["precompute"] += 1
        W, a, b = canon(W, a0, b0)
        seen = {}
        path = []
        while True:
            key = W if W is not INF else "INF"
            if key in seen:
                a2, b2, pos = seen[key]
                if (b - b2) % q:
                    k = (a2 - a) * pow((b - b2) % q, -1, q) % q
                    vc = VCurve(p, fx["a"], fx["b"])
                    ok = vc.mul(k, G) == Q
                    return {"t": t, "k": k, "solved": ok, "degenerate_target": False,
                            "group_ops": group_ops,
                            "group_ops_total": sum(group_ops.values()),
                            "walk_ops_over_sqrt_q": (group_ops["walk"] + group_ops["escape"]) / math.sqrt(q),
                            "ops": counter.as_dict(), "fruitless_cycles": fruitless,
                            "restarts": restarts}
                if (a - a2) % q == 0:
                    fruitless += 1
                    cyc = [pt for pt in path[pos:] if pt[0] is not INF] or [path[-1]]
                    Pm, am, bm = min(cyc, key=lambda e: e[0][0])
                    W = curve.add(Pm, Pm)
                    group_ops["escape"] += 1
                    W, a, b = canon(W, 2 * am % q, 2 * bm % q)
                    continue
                break  # b equal, a different: impossible for a valid walk; restart
            seen[key] = (a, b, len(path))
            path.append((W, a, b))
            j = (W[0] if W is not INF else 0) % R_WALK
            P, c, d = M[j]
            W = curve.add(W, P)
            group_ops["walk"] += 1
            W, a, b = canon(W, (a + c) % q, (b + d) % q)
        restarts += 1
    return {"t": t, "solved": False, "degenerate_target": False, "group_ops": group_ops,
            "ops": counter.as_dict(), "fruitless_cycles": fruitless, "restarts": restarts}
