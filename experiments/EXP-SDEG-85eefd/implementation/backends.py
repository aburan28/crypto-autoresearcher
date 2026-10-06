"""Backends of AMD-20260926-3479cf C-4.

Membership (C-3): R = e1 P1 + ... + e5 P5, P_i in the factor base, e_i = +-1,
repetition allowed. Serial split: U = e1 P1 + e2 P2 (forward), and
R - e3 P3 - e4 P4 - e5 P5 = +-U (backward, unordered triples with repetition
in the fixed order i3 <= i4 <= i5 over sorted V).

Point at infinity. U = O occurs (P2 = -P1) and has no x-coordinate, so the
literal T = {u : S3(x1,x2,u) = 0} omits it. Both charged backends therefore
carry an explicit INF element in the forward set (present whenever V is
non-empty). B0 sees it as a backward point equal to O; B1 sees it as a degree
drop of b(u) (the leading coefficient of S5 in u is S4(x3,x4,x5,x(R))^2 up to
a constant, which vanishes iff a signed 3-sum equals +-R). Both readings are
the same event; see implementation.md.

Charged work W for a query = the counter of the query's own loop. The table
(forward points, inserts, and F_T for B1) and the deck construction are
charged once per (fixture, deck) and reported both unamortized and amortized
over the deck's queries.
"""

from __future__ import annotations

import resource
import sys

import numpy as np

import polyfp
from fparith import INF as PINF
from fparith import Curve, Fp, OpCounter
from verify import O, VCurve, verify_decomposition

INF_KEY = "INF"
MEMORY_LIMIT_BYTES = 8 * 1024 ** 3


class MemoryLimit(RuntimeError):
    pass


def _rss_bytes() -> int:
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r if sys.platform == "darwin" else r * 1024


def _mem_guard():
    if _rss_bytes() > MEMORY_LIMIT_BYTES:
        raise MemoryLimit(f"peak RSS {_rss_bytes()} > {MEMORY_LIMIT_BYTES}")


def triples(n: int):
    for i3 in range(n):
        for i4 in range(i3, n):
            for i5 in range(i4, n):
                yield (i3, i4, i5)


def n_triples(n: int) -> int:
    return n * (n + 1) * (n + 2) // 6


# ---------------------------------------------------------------- forward table
class ForwardTable:
    """T = {x(P1 + P2), x(P1 - P2)} over unordered pairs, plus INF (P - P)."""

    def __init__(self, fx, deck, build_poly: bool):
        self.counter = OpCounter()
        F = Fp(fx["p"], self.counter)
        curve = Curve(F, fx["a"], fx["b"])
        pts = deck.points
        n = len(pts)
        self.witness = {}  # u -> (i1, s1, i2, s2) with x(s1 P_i1 + s2 P_i2) = u
        for i1 in range(n):
            for i2 in range(i1, n):
                for s2 in (1, -1):
                    S = curve.add(pts[i1], pts[i2] if s2 > 0 else curve.neg(pts[i2]))
                    key = INF_KEY if S is PINF else S[0]
                    F.probe()  # insert probe
                    if key not in self.witness:
                        self.witness[key] = (i1, 1, i2, s2)
        self.finite = sorted(k for k in self.witness if k != INF_KEY)
        self.has_inf = INF_KEY in self.witness
        self.set = set(self.witness)
        self.ops_points = self.counter.as_dict()
        self.FT = polyfp.from_roots(F, self.finite) if build_poly else None
        self.ops = self.counter.as_dict()
        self.size = len(self.finite)


def _log_entry(tag, counter, snap):
    d = counter.delta(snap)
    return [tag, d["mul"], d["inv"], d["gcd_steps"], d["probes"]]


# ---------------------------------------------------------------- B0
def b0_query(fx, deck, table: ForwardTable, R, keep_log: bool = False, counter=None) -> dict:
    """MITM calibration: per triple, <= 8 candidates x(R - e3P3 - e4P4 - e5P5)
    by point arithmetic, each looked up in the hash set of T (INF included)."""
    counter = counter if counter is not None else OpCounter()
    F = Fp(fx["p"], counter)
    curve = Curve(F, fx["a"], fx["b"])
    pts = deck.points
    negs = [curve.neg(P) for P in pts]
    n = len(pts)
    Tset = table.set
    Rp = PINF if R is O else R
    hits, log = [], []
    first_hit_W = None
    snap = counter.snapshot()
    for i3 in range(n):
        _mem_guard()
        A = [(s3, curve.add(Rp, negs[i3] if s3 > 0 else pts[i3])) for s3 in (1, -1)]
        for i4 in range(i3, n):
            B = [((s3, s4), curve.add(Pa, negs[i4] if s4 > 0 else pts[i4]))
                 for s3, Pa in A for s4 in (1, -1)]
            for i5 in range(i4, n):
                tri_hits = []
                for (s3, s4), Pb in B:
                    for s5 in (1, -1):
                        C = curve.add(Pb, negs[i5] if s5 > 0 else pts[i5])
                        key = INF_KEY if C is PINF else C[0]
                        F.probe()
                        if key in Tset:
                            tri_hits.append({"signs": (s3, s4, s5), "u": key})
                if keep_log:
                    log.append(_log_entry(f"{i3},{i4},{i5}", counter, snap))
                    snap = counter.snapshot()
                if tri_hits:
                    hits.append({"triple": (i3, i4, i5), "hits": tri_hits})
                    if first_hit_W is None:
                        first_hit_W = counter.W()
    return {"backend": "B0", "member": bool(hits), "W_query": counter.W(),
            "W_query_to_first_hit": first_hit_W, "ops": counter.as_dict(),
            "hit_triples": [h["triple"] for h in hits], "hits": hits,
            "n_triples": n_triples(n), "op_log": log if keep_log else None}


# ---------------------------------------------------------------- B1
def b1_query(fx, deck, table: ForwardTable, sem, R, keep_log: bool = False, counter=None) -> dict:
    """A1 backend: per triple b(u) = S5(u, x3, x4, x5, x(R)) by charged Horner
    specialization of the derived S5 (S4(u, x3, x4, x5) when R = O), then the
    subresultant PRS of (F_T, b) with early abort. No composed resultant."""
    counter = counter if counter is not None else OpCounter()
    F = Fp(fx["p"], counter)
    V = deck.V
    n = len(V)
    FT = table.FT
    hits, log, sub_degrees = [], [], []
    first_hit_W = None
    snap = counter.snapshot()
    if R is O:
        base, formal_deg = sem.S4, 4
        spec_R = base
    else:
        formal_deg = 8
        spec_R = sem.spec_last(F, sem.S5, R[0])
    if keep_log:
        log.append(_log_entry("specialize_R", counter, snap))
        snap = counter.snapshot()
    prs_steps = 0
    W_spec = counter.W()
    W_fixed_xR = W_spec
    for i3 in range(n):
        _mem_guard()
        w0 = counter.W()
        s3 = sem.spec_last(F, spec_R, V[i3])
        W_spec += counter.W() - w0
        for i4 in range(i3, n):
            w0 = counter.W()
            s4 = sem.spec_last(F, s3, V[i4])
            W_spec += counter.W() - w0
            for i5 in range(i4, n):
                w0 = counter.W()
                bu = polyfp.trim([int(c) for c in sem.spec_last(F, s4, V[i5])])
                W_spec += counter.W() - w0
                inf_root = polyfp.deg(bu) < formal_deg
                if not bu:
                    dgcd, gcdp, abort = table.size, list(FT), "b_identically_zero"
                else:
                    res = polyfp.subresultant_prs(F, FT, bu)
                    dgcd, gcdp, abort = res["deg_gcd"], res["gcd"], res["abort"]
                    prs_steps += res["steps"]
                sub_degrees.append(dgcd)
                hit_inf = inf_root and table.has_inf
                if keep_log:
                    log.append(_log_entry(f"{i3},{i4},{i5}", counter, snap))
                    snap = counter.snapshot()
                if dgcd >= 1 or hit_inf:
                    hits.append({"triple": (i3, i4, i5), "deg_gcd": dgcd,
                                 "gcd": gcdp if dgcd >= 1 else None, "inf_root": inf_root,
                                 "b_deg": polyfp.deg(bu), "abort": abort})
                    if first_hit_W is None:
                        first_hit_W = counter.W()
    return {"backend": "B1", "member": bool(hits), "W_query": counter.W(),
            "W_query_to_first_hit": first_hit_W, "ops": counter.as_dict(),
            "hit_triples": [h["triple"] for h in hits], "hits": hits,
            "n_triples": n_triples(n), "prs_steps": prs_steps,
            "W_components": {"S5_specialization": W_spec, "prs_and_rest": counter.W() - W_spec,
                             "fixed_xR_specialization": W_fixed_xR},
            "sub_degree_sum": int(sum(sub_degrees)),
            "sub_degree_max": int(max(sub_degrees)) if sub_degrees else 0,
            "op_log": log if keep_log else None}


# ---------------------------------------------------------------- B2
def b2_query(fx, deck, R, return_roots: bool = False) -> dict:
    """Eliminant-degree meter: number of distinct finite x(R + e3P3 + e4P4 + e5P5).
    Diagnostic only (verifier arithmetic, no charge)."""
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    pts = deck.points
    n = len(pts)
    xs, inf = set(), False
    for i3 in range(n):
        A = [vc.add(R, vc.signed(pts[i3], s)) for s in (1, -1)]
        for i4 in range(i3, n):
            B = [vc.add(P, vc.signed(pts[i4], s)) for P in A for s in (1, -1)]
            for i5 in range(i4, n):
                for P in B:
                    for s in (1, -1):
                        C = vc.add(P, vc.signed(pts[i5], s))
                        if C is O:
                            inf = True
                        else:
                            xs.add(C[0])
    out = {"backend": "B2", "elim_degree": len(xs), "infinity_occurs": inf,
           "roots_sha256": _hash_sorted(xs)}
    if return_roots:
        out["roots"] = sorted(xs)
    return out


def _hash_sorted(xs) -> str:
    import hashlib
    return hashlib.sha256(",".join(map(str, sorted(xs))).encode()).hexdigest()


# ---------------------------------------------------------------- witnesses
def extract_and_verify(fx, deck, table: ForwardTable, sem, R, triple, backend_hit) -> dict:
    """Replay one hit triple with independent arithmetic. Returns the 5-term
    decomposition and checks: (i) candidate u = x(R - s.P) lies in T (or is O
    and INF in T), (ii) for B1, the PRS gcd vanishes at u, (iii) exact S5
    evaluation S5(u, x3, x4, x5, x(R)) == 0 for finite u, (iv) the full sum
    equals R."""
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    pts = deck.points
    i3, i4, i5 = triple
    p = fx["p"]
    results = []
    for s3 in (1, -1):
        for s4 in (1, -1):
            for s5 in (1, -1):
                U = vc.sum_signed([(R, 1), (pts[i3], -s3), (pts[i4], -s4), (pts[i5], -s5)]) \
                    if R is not O else vc.sum_signed([(pts[i3], -s3), (pts[i4], -s4), (pts[i5], -s5)])
                key = INF_KEY if U is O else U[0]
                if key not in table.set:
                    continue
                i1, e1, i2, e2 = table.witness[key]
                fwd = vc.sum_signed([(pts[i1], e1), (pts[i2], e2)])
                if fwd != U:  # forward witness gives -U; flip both forward signs
                    e1, e2 = -e1, -e2
                terms = [(i1, e1), (i2, e2), (i3, s3), (i4, s4), (i5, s5)]
                ok = verify_decomposition(vc, R, pts, terms)
                s5_ok = None
                if key != INF_KEY and R is not O:
                    s5_ok = sem.eval_full(sem.S5, [key, deck.V[i3], deck.V[i4], deck.V[i5], R[0]]) == 0
                elif key != INF_KEY:
                    s5_ok = sem.eval_full(sem.S4, [key, deck.V[i3], deck.V[i4], deck.V[i5]]) == 0
                gcd_ok = None
                if backend_hit.get("gcd") and key != INF_KEY:
                    g = backend_hit["gcd"]
                    gcd_ok = sum(c * pow(key, e, p) for e, c in enumerate(g)) % p == 0
                results.append({"u": key, "terms": terms, "sum_ok": ok, "s5_zero": s5_ok,
                                "gcd_vanishes": gcd_ok})
    verified = bool(results) and all(r["sum_ok"] and r["s5_zero"] is not False
                                     and r["gcd_vanishes"] is not False for r in results)
    n_finite = len({r["u"] for r in results if r["u"] != INF_KEY})
    deg_consistent = None
    if backend_hit.get("deg_gcd") is not None and backend_hit.get("abort") != "b_identically_zero":
        # F_T is squarefree, so deg gcd(F_T, b) = number of distinct finite common roots
        deg_consistent = backend_hit["deg_gcd"] == n_finite
        verified = verified and deg_consistent
    return {"triple": list(triple), "witnesses": results, "verified": verified,
            "distinct_finite_u": n_finite, "deg_gcd_consistent": deg_consistent}
