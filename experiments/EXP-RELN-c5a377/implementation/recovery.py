"""Sparse LP log recovery over Z/q (C-4 secondary) and the scrambled-coefficient
known-false control (C-6).

Unknowns: l(x) for every factor-base x-class and every LP x-class in a
relation (the log of the canonical point, y <= (p-1)/2), and k = log_G(Q).
Equations: each two-point relation R_j = s1 V_{x1} + s2 V_{x2} gives
  s1 l(x1) + s2 l(x2) - b_j k = a_j  (mod q),
and the anchor l(x(G)) = 1 (G is canonical by fixture construction; checked).
Gauss-Jordan elimination on sparse rows, pivoting LP columns first (fewest
entries), then factor-base columns, then k; every product and inversion
mod q is charged. A variable is determined iff it is a pivot whose reduced
row carries no free column. Determined values are verified with independent
arithmetic: l(x) G == V_x and k G == Q.
"""

from __future__ import annotations

import labels
from nulls import Draws
from vcurve import VCurve


class LACounter:
    def __init__(self):
        self.mul = 0
        self.inv = 0

    def as_dict(self):
        return {"mul": self.mul, "inv": self.inv}


def build_system(relations, fb_x, B, q, G, p):
    if G[1] > (p - 1) // 2:
        raise ValueError("G not canonical; anchor sign would be -1")
    lp_cols = sorted({x for r in relations for x in (r["rel"][0], r["rel"][2]) if x >= B})
    cols = [("lp", x) for x in lp_cols] + [("fb", x) for x in fb_x] + [("k", None)]
    if ("fb", G[0]) not in cols:
        cols.insert(len(lp_cols), ("fb", G[0]))
    idx = {c: i for i, c in enumerate(cols)}
    rows = []
    for r in relations:
        x1, s1, x2, s2 = r["rel"]
        row = {}
        for x, s in ((x1, s1), (x2, s2)):
            c = idx[("lp" if x >= B else "fb", x)]
            row[c] = (row.get(c, 0) + s) % q
        if r["b"] % q:
            row[idx[("k", None)]] = (-r["b"]) % q
        row = {c: v for c, v in row.items() if v}
        rows.append((row, r["a"] % q))
    rows.append(({idx[("fb", G[0])]: 1}, 1))
    return cols, rows


def solve(cols, rows, q, ctr: LACounter) -> dict:
    rows = [(dict(r), rhs) for r, rhs in rows]
    ncol = len(cols)
    kcol = ncol - 1
    col_count = [0] * ncol
    for r, _ in rows:
        for c in r:
            col_count[c] += 1
    lp_or_fb = sorted(range(kcol), key=lambda c: (cols[c][0] != "lp", col_count[c], c))
    order = lp_or_fb + [kcol]
    pivot_row = {}
    used = set()
    for c in order:
        best = None
        for i, (r, _) in enumerate(rows):
            if i in used or c not in r:
                continue
            if best is None or len(r) < len(rows[best][0]):
                best = i
        if best is None:
            continue
        used.add(best)
        r, rhs = rows[best]
        inv = pow(r[c], -1, q)
        ctr.inv += 1
        r = {cc: v * inv % q for cc, v in r.items()}
        rhs = rhs * inv % q
        ctr.mul += len(r) + 1
        rows[best] = (r, rhs)
        pivot_row[c] = best
        for i in range(len(rows)):
            if i == best:
                continue
            ri, rhsi = rows[i]
            f = ri.get(c)
            if not f:
                continue
            for cc, v in r.items():
                nv = (ri.get(cc, 0) - f * v) % q
                if nv:
                    ri[cc] = nv
                else:
                    ri.pop(cc, None)
            ctr.mul += len(r) + 1
            rows[i] = (ri, (rhsi - f * rhs) % q)
    inconsistent = sum(1 for i, (r, rhs) in enumerate(rows) if not r and rhs % q)
    determined = {}
    for c, i in pivot_row.items():
        r, rhs = rows[i]
        if set(r) == {c}:
            determined[c] = rhs
    return {"n_rows": len(rows), "n_cols": ncol, "rank": len(pivot_row),
            "inconsistent_rows": inconsistent, "determined": determined}


def recover_and_verify(relations, fb_x, B, fx, Q, ctr: LACounter | None = None) -> dict:
    p, q = fx["p"], fx["N"]
    G = tuple(fx["G"])
    ctr = ctr or LACounter()
    cols, rows = build_system(relations, fb_x, B, q, G, p)
    sol = solve(cols, rows, q, ctr)
    vc = VCurve(p, fx["a"], fx["b"])
    lp_total = sum(1 for c in cols if c[0] == "lp")
    ok = {"lp": 0, "fb": 0, "k": 0}
    bad = {"lp": 0, "fb": 0, "k": 0}
    anchor = cols.index(("fb", G[0]))
    for c, val in sol["determined"].items():
        kind, x = cols[c]
        if kind == "k":
            good = vc.mul(val, G) == (None if Q is None else tuple(Q))
        else:
            good = vc.mul(val, G) == vc.lift_canonical(x)
        (ok if good else bad)[kind] += 1
    anchor_determined = anchor in sol["determined"]
    nontrivial_determined = len(sol["determined"]) - (1 if anchor_determined else 0)
    return {"n_relations": len(relations), "n_unknowns": len(cols), "rank": sol["rank"],
            "inconsistent_rows": sol["inconsistent_rows"],
            "lp_vertices": lp_total, "lp_determined_verified": ok["lp"],
            "lp_determined_failed": bad["lp"],
            "lp_recovery_fraction": (ok["lp"] / lp_total) if lp_total else None,
            "fb_determined_verified": ok["fb"], "fb_determined_failed": bad["fb"],
            "k_determined": (ok["k"] + bad["k"]) > 0, "k_verified": ok["k"] > 0,
            "nontrivial_determined": nontrivial_determined,
            "verification_failures": sum(bad.values()),
            "verification_passed": sol["inconsistent_rows"] == 0 and sum(bad.values()) == 0,
            "la_ops_charged": ctr.as_dict()}


def scramble(relations: list[dict], ns: str, context: str) -> list[dict]:
    """(a_j, b_j) permuted across the relations by a derangement: a SHA256
    Fisher-Yates order, each relation taking the coefficients of the next
    relation in that order (cyclic)."""
    n = len(relations)
    if n < 2:
        return [dict(r) for r in relations]
    dr = Draws(labels.lab(ns, "scramble", context))
    order = list(range(n))
    for i in range(n - 1, 0, -1):
        j = dr.uniform(i + 1)
        order[i], order[j] = order[j], order[i]
    out = [dict(r) for r in relations]
    for t in range(n):
        dst, src = order[t], order[(t + 1) % n]
        out[dst]["a"], out[dst]["b"] = relations[src]["a"], relations[src]["b"]
    return out


def known_false_outcome(res: dict) -> str:
    """'fails_verification' (control behaves), 'passes_verification' (control
    FAILED: procedure defect) or 'not_exercised' (consistent, nothing
    non-trivial determined)."""
    if res["inconsistent_rows"] > 0 or res["verification_failures"] > 0:
        return "fails_verification"
    if res["nontrivial_determined"] == 0:
        return "not_exercised"
    return "passes_verification"
