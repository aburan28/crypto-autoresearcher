"""Factor bases (C-2, C-6 null) and the non-Groebner MITM membership backend B0
reused by reference from AMD-20260926-3479cf C-4 (stage 1 of C-4 here).

B0 for m = 5 (verbatim structure of EXP-SDEG-85eefd backends.b0_query):
forward table T = {x(P_i1 + s P_i2) : i1 <= i2, s = +-1} plus INF (P - P),
built once per (fixture, factor base) and charged once; per query, for every
nondecreasing index triple (i3, i4, i5) the 8 candidates
x(R - s3 P_i3 - s4 P_i4 - s5 P_i5) are computed by point arithmetic with
prefix sharing (2 adds per i3, 4 per (i3, i4), 8 per triple) and each is
probed in the hash set of T. The whole scan runs (no early abort), so a
query's charged work does not depend on where the first hit lies.

Arities m = 6, 8 (stage-cost-only, C-2): the same forward 2-sum table and a
backward (m-2)-sum by the same prefix-shared recursion (OQ-4).

Factor-base points are the canonical lifts (x, min(y, p-y)) of the L liftable
x-classes; the factor base F = {P : x(P) in V} contains both signs, carried
by the signs e_i = +-1 exactly as in B0.
"""

from __future__ import annotations

import resource
import sys

import common
from arith import INF, Cost, Curve, Fp
from verify import O, VCurve, verify_decomposition

INF_KEY = "INF"


class MemoryLimit(RuntimeError):
    pass


def rss_bytes() -> int:
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r if sys.platform == "darwin" else r * 1024


def mem_guard():
    if rss_bytes() > common.MEMORY_LIMIT_BYTES:
        raise MemoryLimit(f"peak RSS {rss_bytes()} > {common.MEMORY_LIMIT_BYTES}")


# ------------------------------------------------------------------ factor bases
class FactorBase:
    def __init__(self, kind, V, points, B, cost_dict, draws=None):
        self.kind, self.V, self.points, self.B = kind, V, points, B
        self.L = len(V)
        self.cost = cost_dict
        self.draws = draws
        self.index = {x: i for i, x in enumerate(V)}

    def summary(self) -> dict:
        return {"kind": self.kind, "B": self.B, "L": self.L, "V": self.V,
                "F_size_points": 2 * self.L, "construction_cost": self.cost,
                "random_draws": self.draws}


def interval_fb(fx, m: int) -> FactorBase:
    """C-2: F = {P : x(P) < B}, B = ceil(p^(1/m)); liftability tests and lifts charged."""
    cost = Cost()
    F = Fp(fx["p"], cost)
    curve = Curve(F, fx["a"], fx["b"])
    B = common.fb_bound(fx["p"], m)
    V, pts = [], []
    for x in range(min(B, fx["p"])):
        if curve.is_liftable(x):
            V.append(x)
            pts.append(curve.lift(x))
    return FactorBase("interval", V, pts, B, cost.as_dict())


def random_fb(fx, ns: str, size: int, B_ref: int) -> FactorBase:
    """C-6 matched null: `size` liftable x-classes drawn without replacement from
    all liftable x in [0, p) by '<ns>|randfb|<bits>|<seed>|<i>' (i = 0, 1, ...;
    a draw that is non-liftable or already chosen is rejected and i advances).
    Liftability tests of every draw are charged as construction cost."""
    cost = Cost()
    F = Fp(fx["p"], cost)
    curve = Curve(F, fx["a"], fx["b"])
    chosen, pts, i = [], [], 0
    seen = set()
    while len(chosen) < size:
        x = common.uniform(common.lab(ns, "randfb", fx["bits"], fx["seed"], i), fx["p"])
        i += 1
        if x in seen:
            continue
        seen.add(x)
        if curve.is_liftable(x):
            chosen.append(x)
    order = sorted(chosen)
    for x in order:
        pts.append(curve.lift(x))
    return FactorBase("random_x", order, pts, B_ref, cost.as_dict(), draws=i)


# ------------------------------------------------------------------ forward table
class ForwardTable:
    """T = {x(P_i1 + s P_i2)} over i1 <= i2, s = +-1, plus INF. Charged once."""

    def __init__(self, fx, fb: FactorBase):
        cost = Cost()
        F = Fp(fx["p"], cost)
        curve = Curve(F, fx["a"], fx["b"])
        pts, n = fb.points, fb.L
        self.witness = {}
        for i1 in range(n):
            for i2 in range(i1, n):
                for s2 in (1, -1):
                    S = curve.add(pts[i1], pts[i2] if s2 > 0 else curve.neg(pts[i2]))
                    key = INF_KEY if S is INF else S[0]
                    F.probe()
                    if key not in self.witness:
                        self.witness[key] = (i1, 1, i2, s2)
        self.set = set(self.witness)
        self.size = len(self.set)
        self.cost = cost.as_dict()
        self.n_pairs = n * (n + 1)


def n_multisets(n: int, d: int) -> int:
    from math import comb
    return comb(n + d - 1, d) if n > 0 else 0


# ------------------------------------------------------------------ B0 query
def b0_query(fx, fb: FactorBase, table: ForwardTable, R, m: int, cost: Cost) -> dict:
    """Decide m-membership of R exactly (full scan). Charged on `cost`.
    Returns the first hit in scan order and the hit count."""
    d = m - 2
    F = Fp(fx["p"], cost)
    curve = Curve(F, fx["a"], fx["b"])
    pts = fb.points
    negs = [curve.neg(P) for P in pts]
    n = fb.L
    Tset = table.set
    Rp = INF if R is O else R
    snap = cost.snapshot()
    state = {"first": None, "n_hits": 0, "first_units": None}

    def rec(level, start, prefix, idx):
        for i in range(start, n):
            if level == 1:
                mem_guard()
            new = [(sg + (s,), curve.add(P, negs[i] if s > 0 else pts[i]))
                   for sg, P in prefix for s in (1, -1)]
            if level == d:
                for sg, C in new:
                    key = INF_KEY if C is INF else C[0]
                    F.probe()
                    if key in Tset:
                        state["n_hits"] += 1
                        if state["first"] is None:
                            state["first"] = {"idx": idx + (i,), "signs": sg, "u": key, "C": C}
                            state["first_units"] = cost.delta(snap)["units"]
            else:
                rec(level + 1, i, new, idx + (i,))

    rec(1, 0, [((), Rp)], ())
    return {"member": state["first"] is not None, "first": state["first"],
            "n_hits": state["n_hits"], "units_to_first_hit": state["first_units"],
            "n_backward_multisets": n_multisets(n, d)}


def extract_relation(fx, fb: FactorBase, table: ForwardTable, hit, cost: Cost) -> list:
    """Solver-side relation extraction from a B0 hit (one charged add): returns
    m signed terms [(index, sign)] with R = sum sign * P_index."""
    F = Fp(fx["p"], cost)
    curve = Curve(F, fx["a"], fx["b"])
    pts = fb.points
    i1, e1, i2, e2 = table.witness[hit["u"]]
    fwd = curve.add(curve.neg(pts[i1]) if e1 < 0 else pts[i1],
                    curve.neg(pts[i2]) if e2 < 0 else pts[i2])
    C = hit["C"]
    if fwd != C:  # same x: C = -fwd, flip both forward signs
        e1, e2 = -e1, -e2
    return [(i1, e1), (i2, e2)] + list(zip(hit["idx"], hit["signs"]))


def verify_relation(fx, fb: FactorBase, R, terms, m: int) -> bool:
    """Independent point-arithmetic check (uncharged)."""
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    return verify_decomposition(vc, R, fb.points, terms, m=m)


def terms_to_row(terms, L: int, q: int) -> dict:
    row = {}
    for i, s in terms:
        row[i] = (row.get(i, 0) + s) % q
    return {i: c for i, c in row.items() if c}


# ------------------------------------------------------------------ stage 2 scan
def two_sum_scan(fx, fb: FactorBase, S, cost: Cost) -> dict:
    """C-4 stage 2 output-sensitive scan: P1 over F (2L signed points), test
    x(S - P1) < B. Each test is charged 1 unit (hash-probe unit, OQ-5); S - P1 = O
    is not a hit (O is not in F). Interval factor bases only."""
    F = Fp(fx["p"], cost)
    curve = Curve(F, fx["a"], fx["b"])
    B = fb.B
    out = []
    Sp = INF if S is O else S
    for i, P in enumerate(fb.points):
        for s in (1, -1):
            D = curve.add(Sp, P if s < 0 else curve.neg(P))  # S - s*P
            F.probe()
            if D is not INF and D[0] < B:
                out.append((i, s, fb.index[D[0]], 1 if D[1] == fb.points[fb.index[D[0]]][1] else -1))
    return {"pairs": out, "n_pairs": len(out)}
