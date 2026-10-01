"""Pollard rho baseline (AMD-20260926-ced670 C-6): negation map, r = 32 adding
walk, 64 targets per fixture, measured in the C-3 units. Adapted from
EXP-SDEG-85eefd implementation/rho.py (same walk, fruitless-cycle escape and
collision store); arithmetic and labels are this implementation's.

Walk: W <- canon(W + M_{x(W) mod 32}); canon picks y <= (p-1)/2 and negates the
(a, b) coefficients when it flips. M_j = c_j G + d_j Q and the start come from
'<ns>|rho_walk|<bits>|<seed>|<t>|<restart>.<tag>' (not fixed by the protocol).
Every visited canonical point is stored (memory O(sqrt q), trivial at q < 2^21);
the store's insert/lookup is charged one hash probe per step (OQ-6). A revisit
with equal coefficients is a fruitless cycle: escape by doubling the min-x
point of the cycle. Units are reported total, walk-only and precompute-only.
"""

from __future__ import annotations

import math

import common
from arith import INF, Cost, Curve, Fp
from verify import VCurve


def rho_target_k(fx, t: int, ns: str) -> int:
    return common.uniform(common.lab(ns, "rho", fx["bits"], fx["seed"], t), fx["N"])


def solve(fx, Q, t: int, ns: str, max_restarts: int = 64) -> dict:
    p, q = fx["p"], fx["N"]
    cost = Cost()
    F = Fp(p, cost)
    curve = Curve(F, fx["a"], fx["b"])
    G = tuple(fx["G"])
    half = (p - 1) // 2
    fruitless = restarts = 0
    pre_units = 0

    def canon(P, a, b):
        if P is not INF and P[1] > half:
            return (P[0], p - P[1]), (-a) % q, (-b) % q
        return P, a, b

    def wl(tag):
        return common.lab(ns, "rho_walk", fx["bits"], fx["seed"], t, f"{restarts}.{tag}")

    if Q is INF:
        return {"t": t, "k": 0, "solved": True, "degenerate_target": True, "cost": cost.as_dict()}
    while restarts <= max_restarts:
        s0 = cost.snapshot()
        M = []
        for j in range(32):
            c = common.uniform(wl(f"{j}c"), q)
            d = common.uniform(wl(f"{j}d"), q)
            M.append((curve.add(curve.mul(c, G), curve.mul(d, Q)), c, d))
        a0, b0 = common.uniform(wl("start_a"), q), common.uniform(wl("start_b"), q)
        W = curve.add(curve.mul(a0, G), curve.mul(b0, Q))
        W, a, b = canon(W, a0, b0)
        pre_units += cost.delta(s0)["units"]
        seen, path = {}, []
        while True:
            key = W if W is not INF else "INF"
            F.probe()
            if key in seen:
                a2, b2, pos = seen[key]
                if (b - b2) % q:
                    k = (a2 - a) * pow((b - b2) % q, -1, q) % q
                    ok = VCurve(p, fx["a"], fx["b"]).mul(k, G) == Q
                    tot = cost.as_dict()
                    return {"t": t, "k": k, "solved": ok, "degenerate_target": False, "cost": tot,
                            "units": tot["units"], "precompute_units": pre_units,
                            "walk_units": tot["units"] - pre_units,
                            "group_ops": tot["pt_add"] + tot["pt_dbl"],
                            "fruitless_cycles": fruitless, "restarts": restarts}
                if (a - a2) % q == 0:
                    fruitless += 1
                    cyc = [e for e in path[pos:] if e[0] is not INF] or [path[-1]]
                    Pm, am, bm = min(cyc, key=lambda e: e[0][0])
                    W, a, b = canon(curve.add(Pm, Pm), 2 * am % q, 2 * bm % q)
                    continue
                break
            seen[key] = (a, b, len(path))
            path.append((W, a, b))
            j = (W[0] if W is not INF else 0) % 32
            P, c, d = M[j]
            W, a, b = canon(curve.add(W, P), (a + c) % q, (b + d) % q)
        restarts += 1
    tot = cost.as_dict()
    return {"t": t, "solved": False, "degenerate_target": False, "cost": tot, "units": tot["units"],
            "precompute_units": pre_units, "walk_units": tot["units"] - pre_units,
            "fruitless_cycles": fruitless, "restarts": restarts}


def run_rho(fx, ns: str, n_targets: int) -> dict:
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    G = tuple(fx["G"])
    res = []
    for t in range(n_targets):
        k = rho_target_k(fx, t, ns)
        Q = vc.mul(k, G)
        r = solve(fx, Q, t, ns)
        r["k_true_matches"] = r.get("k") == k or (Q is None)
        res.append(r)
    units = [r["units"] for r in res if r.get("solved")]
    return {"targets": res, "n_targets": n_targets, "n_solved": sum(1 for r in res if r.get("solved")),
            "mean_units": (sum(units) / len(units)) if units else None,
            "mean_walk_units": (sum(r["walk_units"] for r in res if r.get("solved")) / len(units)) if units else None,
            "reference_13x0886_sqrt_q": common.rho_reference_units(fx["N"]),
            "sqrt_q": math.sqrt(fx["N"])}
