"""Pollard rho baseline with the negation map (AMD-20260926-a7d25d C-6):
64 targets per fixture, group operations / sqrt(q) against 0.886.

Walk: W <- canon(W + M_{x(W) mod 32}); canon takes y <= (p-1)/2 and negates
the (c, d) coefficients when it flips. M_j = c_j G + d_j Q, start a_0 G + b_0 Q,
from '<ns>|rho_walk|<bits>|<seed>|<t>|<restart>.<j><c|d>' (walk labels are not
fixed by the protocol). Every visited canonical point is stored (memory
O(sqrt q), trivial at q < 2^24). A revisit with equal coefficients (up to the
joint sign) is a fruitless cycle, escaped by doubling the minimum-x point of
the cycle. Walk and escape operations are the reported group operations;
precomputation is reported separately. Solutions are verified with the
independent verifier arithmetic.
"""

from __future__ import annotations

import math

import labels
from ecarith import O, Curve, Fp, OpCounter
from vcurve import VCurve

R_WALK = 32


def target(fx, ns, t):
    return labels.uniform(labels.lab(ns, "rho", fx["bits"], fx["seed"], t), fx["N"])


def solve(fx, t: int, ns: str, max_restarts: int = 16) -> dict:
    p, q = fx["p"], fx["N"]
    G = tuple(fx["G"])
    vc = VCurve(p, fx["a"], fx["b"])
    k_true = target(fx, ns, t)
    Q = vc.mul(k_true, G)
    ctr = OpCounter()
    E = Curve(Fp(p, ctr), fx["a"], fx["b"])
    half = (p - 1) // 2
    ops = {"walk": 0, "escape": 0, "precompute": 0}
    fruitless = 0

    def canon(P, a, b):
        if P is not O and P[1] > half:
            return (P[0], p - P[1]), (-a) % q, (-b) % q
        return P, a, b

    def lbl(restart, s):
        return labels.lab(ns, "rho_walk", fx["bits"], fx["seed"], t, f"{restart}.{s}")

    if Q is None:
        return {"t": t, "solved": True, "degenerate_target": True, "ops": ops}
    for restart in range(max_restarts + 1):
        snap = ctr.group_ops
        M = []
        for j in range(R_WALK):
            c, d = labels.uniform(lbl(restart, f"{j}c"), q), labels.uniform(lbl(restart, f"{j}d"), q)
            M.append((E.add(E.mul(c, G), E.mul(d, Q)), c, d))
        a0, b0 = labels.uniform(lbl(restart, "start_a"), q), labels.uniform(lbl(restart, "start_b"), q)
        W, a, b = canon(E.add(E.mul(a0, G), E.mul(b0, Q)), a0, b0)
        ops["precompute"] += ctr.group_ops - snap
        seen, path = {}, []
        while True:
            key = W if W is not O else "O"
            if key in seen:
                a2, b2, pos = seen[key]
                if (b - b2) % q:
                    k = (a2 - a) * pow((b - b2) % q, -1, q) % q
                    walk = ops["walk"] + ops["escape"]
                    return {"t": t, "solved": vc.mul(k, G) == Q, "k_matches_label": k == k_true,
                            "degenerate_target": False, "ops": ops, "walk_ops": walk,
                            "walk_ops_over_sqrt_q": walk / math.sqrt(q),
                            "fruitless_cycles": fruitless, "restarts": restart,
                            "stored_points": len(seen), "field_ops": ctr.as_dict()}
                if (a - a2) % q == 0:
                    fruitless += 1
                    cyc = [e for e in path[pos:] if e[0] is not O] or [path[-1]]
                    Pm, am, bm = min(cyc, key=lambda e: e[0][0])
                    snap = ctr.group_ops
                    W = E.add(Pm, Pm)
                    ops["escape"] += ctr.group_ops - snap
                    W, a, b = canon(W, 2 * am % q, 2 * bm % q)
                    continue
                break  # inconsistent walk: restart with fresh multipliers
            seen[key] = (a, b, len(path))
            path.append((W, a, b))
            P, c, d = M[(W[0] if W is not O else 0) % R_WALK]
            snap = ctr.group_ops
            W = E.add(W, P)
            ops["walk"] += ctr.group_ops - snap
            W, a, b = canon(W, (a + c) % q, (b + d) % q)
    return {"t": t, "solved": False, "degenerate_target": False, "ops": ops,
            "fruitless_cycles": fruitless, "restarts": max_restarts + 1}


def summary(results: list[dict], q: int) -> dict:
    ok = [r for r in results if r.get("solved") and not r.get("degenerate_target")]
    ratios = [r["walk_ops_over_sqrt_q"] for r in ok]
    return {"n_targets": len(results), "n_solved": len(ok),
            "n_failed": sum(1 for r in results if not r.get("solved")),
            "mean_walk_ops_over_sqrt_q": (sum(ratios) / len(ratios)) if ratios else None,
            "reference_constant": 0.886, "sqrt_q": math.sqrt(q)}
