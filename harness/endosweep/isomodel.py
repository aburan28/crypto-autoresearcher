"""Isogenous-model screen: is k*P cheaper on a small-degree isogenous neighbour?

For a prime-field curve E with order h*n, an F_p-rational isogeny
phi: E -> E' of degree d coprime to n gives

    k P = phi_hat( k' phi(P) ),    k' = k d^(-1) mod n,

so a variable-base scalar multiplication may be carried out on E' in the
cheapest model E' admits, paying for phi, its dual and the model changes.
Group order is an isogeny invariant, so the cofactor, and with it whether
a Montgomery or twisted-Edwards model can exist at all, never changes; what
can change along an edge is the short-Weierstrass coefficient class (an
``a = -3`` model needs ``-3/a`` to be a fourth power), the rational 2-torsion
structure (only along 2-isogenies) and the endomorphism-ring conductor
(volcano level).  This module measures, per curve:

* **model arm** -- breadth-first search over rational ell-isogenies,
  ell in ``--ells``, to ``--depth``; on every node the cheapest available
  model (short Weierstrass with ``curvesweep.arithmetic``'s doubling class,
  twisted Edwards ``a = -1`` or general ``a`` when a Montgomery model
  exists); the counted wNAF cost of a random-scalar multiplication on the
  node, against the best model available on E itself, with and without the
  conversion (forward chain, dual chain, model maps, scalar adjustment);
* **ascent arm** -- the exact fundamental discriminant and conductor of
  ``t^2 - 4p`` when ``|D_K| <= --disc-bound``: a large conductor over a small
  ``D_K`` is a volcano whose crater curve carries a cheap endomorphism;
* **verification** -- every best route is executed on points: forward chain,
  the scalar multiplication in the node's chosen model, the dual chain found
  among the node's rational kernels (``iso o psi o phi = +-[d]``), and the
  result compared with ``k P`` computed on E, for ``--verify-scalars``
  random scalars.

All costs are operation counts in the conventions of ``curvesweep`` (field
squaring counted as one multiplication, ``M_eq = M + S``); they are
**modelled**, not measured.  A modelled gain is a candidate for a timed
comparison, nothing more, and a known-scalar multiplication gain is never an
ECDLP gain.

    python -m harness.endosweep.isomodel --std-curves STD_CURVES --out-dir DIR
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import random
import statistics
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from math import gcd

from . import chainsweep as CS
from . import curvesweep as CW
from . import explicit as EX
from . import quadorder as QO
from .targets import Target, _e_add, _m_add, _mul, deployed_targets, verify, weierstrass_target
from .toyverify import Curve, isomorphism_to, prime_nth_roots

VARIANT = "optimised"
WIDTHS = (3, 4, 5, 6, 7)

# ---------------------------------------------------------------------------
# models available on a short Weierstrass curve
# ---------------------------------------------------------------------------

# twisted Edwards counts (EFD, provenance recalled from the EFD listing, as in costmodel.py):
#   a = -1 extended: dbl-2008-hwcd 4M+4S, add-2008-hwcd-3 8M, madd-2008-hwcd-3 7M
#   general a extended: dbl-2008-hwcd 4M+4S+1D(a), add-2008-hwcd 9M+1D(a)... charged as 10M, madd 9M
EDWARDS_M1 = dict(dbl=(4, 4), add=(8, 0), madd=(7, 0))
EDWARDS_GEN = dict(dbl=(5, 4), add=(10, 0), madd=(9, 0))
# model-map charges (M, S): affine forward maps take one batched inversion when
# they leave the affine chart (Weierstrass -> Edwards), projective returns need none
MAP_COSTS = {
    "weierstrass": ((0, 0), (0, 0)),        # same model: nothing
    "weierstrass_iso": ((2, 0), (1, 0)),    # (u^2 x, u^3 y) forward; Z/u back (Jacobian)
    "edwards": ((6, 0), (6, 1)),            # W -> Montgomery (2M) -> Edwards (x/y, (x-1)/(x+1)): 1 I + 4M; back projective
}
SCALAR_ADJUST_M = 1                         # k' = k d^-1 mod n: one modular multiplication (charged as 1 M)


def sqrt_mod(a: int, p: int) -> int | None:
    a %= p
    if a == 0:
        return 0
    r = prime_nth_roots(a, 2, p)
    return int(r[0]) if r else None


def is_square(a: int, p: int) -> bool:
    a %= p
    return a == 0 or pow(a, (p - 1) // 2, p) == 1


def cubic_roots(p: int, a: int, b: int) -> list[int]:
    fl = EX._flint()
    ctx = fl.fmpz_mod_poly_ctx(p)
    return sorted({int(r) % p for r, _m in ctx([b % p, a % p, 0, 1]).roots()})


@dataclass
class Model:
    kind: str                  # 'weierstrass' | 'edwards_a=-1' | 'edwards_general'
    arith: CW.Arith
    note: str
    data: dict = field(default_factory=dict)   # map parameters (alpha, s, c) for verification


def models_on(p: int, a: int, b: int) -> list[Model]:
    """Every model this screen prices on y^2 = x^3 + a x + b, with its arithmetic."""
    inv = (bin(p - 2).count("1"), (p - 2).bit_length())
    w = CW.arithmetic(p, a)
    out = [Model("weierstrass", w, w.note)]
    # Montgomery B v^2 = u^3 + A u^2 + u exists iff some root alpha of the cubic has 3 alpha^2 + a a
    # nonzero square (Okeya-Kurumatani-Sakurai 2000, provenance recalled): u = s (x - alpha), v = s y,
    # B = s, A = 3 alpha s with s = 1/sqrt(3 alpha^2 + a).  Twisted Edwards a_E = (A+2)/B, d_E = (A-2)/B,
    # and (a_E, d_E) ~ (a_E c^2, d_E c^2), so a_E = -1 is reachable iff -a_E is a square.
    best_e = None
    for alpha in cubic_roots(p, a, b):
        g = (3 * alpha * alpha + a) % p
        if g == 0 or not is_square(g, p):
            continue
        r = sqrt_mod(g, p)
        for root in (r, (-r) % p):
            s = pow(root, -1, p)
            A, B = 3 * alpha * s % p, s
            if (A * A - 4) % p == 0:
                continue
            aE = (A + 2) * pow(B, -1, p) % p
            dE = (A - 2) * pow(B, -1, p) % p
            if is_square(-aE, p):
                c = sqrt_mod((-aE) * 1, p)          # c^2 = -a_E: x -> x / c makes a_E -> -1 ... see verify
                cand = Model("edwards_a=-1", CW.Arith(EDWARDS_M1["dbl"], EDWARDS_M1["add"], EDWARDS_M1["madd"], inv),
                             "twisted Edwards a = -1, extended: dbl 4M+4S, add 8M, madd 7M",
                             {"alpha": alpha, "s": s, "A": A, "B": B, "aE": aE, "dE": dE, "c": c})
                best_e = cand
                break
            if best_e is None:
                best_e = Model("edwards_general", CW.Arith(EDWARDS_GEN["dbl"], EDWARDS_GEN["add"], EDWARDS_GEN["madd"], inv),
                               "twisted Edwards general a, extended: dbl 4M+4S+1D, add 9M+1D, madd 9M",
                               {"alpha": alpha, "s": s, "A": A, "B": B, "aE": aE, "dE": dE, "c": None})
        if best_e is not None and best_e.kind == "edwards_a=-1":
            break
    if best_e is not None:
        out.append(best_e)
    return out


# ---------------------------------------------------------------------------
# counted scalar multiplication (curvesweep's recoding and table model)
# ---------------------------------------------------------------------------

def scalar_cost(ar: CW.Arith, ks: list[int], s_weight: float = 1.0) -> tuple[float, str]:
    """Cheapest table/width schedule; M_eq = M + s_weight * S (curvesweep's convention is s_weight = 1)."""
    best, where = None, ""
    for table in ("affine", "jacobian"):
        for w in WIDTHS:
            c = statistics.fmean(m + s_weight * q for m, q in (CW.baseline_ops(ar, k, w, table) for k in ks))
            if best is None or c < best:
                best, where = c, f"{table}/w{w}"
    return best, where


def conversion_cost(path: list[int], model_kind: str, weier_note: str) -> float:
    """M_eq of one round trip: forward chain on an affine input, dual chain on a Jacobian input, model maps."""
    fwd = sum(sum(CW.step_ops(ell, VARIANT, i == 0)) for i, ell in enumerate(path))
    back = sum(sum(CW.step_ops(ell, VARIANT, False)) for ell in path)
    if path:
        fwd += sum(CS.tail_ops(VARIANT))
        back += sum(CS.tail_ops(VARIANT))
    if model_kind.startswith("edwards"):
        key = "edwards"
    elif "isomorphic" in weier_note:
        key = "weierstrass_iso"
    else:
        key = "weierstrass"
    (fm, fs), (bm, bs) = MAP_COSTS[key]
    inv = 0
    if key == "edwards":
        inv = 1
    return fwd + back + fm + fs + bm + bs + (SCALAR_ADJUST_M if path else 0) + inv * INV_M_EQ[0]


INV_M_EQ = [0.0]   # set per curve: Fermat inversion M_eq for p


# ---------------------------------------------------------------------------
# breadth-first search over the isogeny class
# ---------------------------------------------------------------------------

@dataclass
class Edge:
    ell: int
    kernel: list[int]


@dataclass
class Node:
    a: int
    b: int
    j: int
    path: list[Edge]
    models: list[dict] = field(default_factory=list)


def neighbours(E: Curve, trace: int, ells: list[int]) -> list[tuple[int, list[int], Curve]]:
    out = []
    fdiv = EX.division_polynomials_flint(E.p, E.a, E.b, max(ells))
    for ell in ells:
        for h in EX.rational_kernels(E, ell, fdiv, trace=trace):
            phi = EX.KernelIsogeny(E, h, ell)
            out.append((ell, h, phi.codomain))
    return out


def bfs(E: Curve, trace: int, n: int, ells: list[int], depth: int, max_nodes: int) -> list[Node]:
    root = Node(E.a, E.b, E.j(), [])
    seen = {root.j}
    frontier, nodes = [root], [root]
    for _ in range(depth):
        nxt = []
        for nd in frontier:
            cur = Curve(E.p, nd.a, nd.b)
            for ell, h, C in neighbours(cur, trace, [l for l in ells if n % l]):
                jj = C.j()
                if jj in seen:
                    continue
                seen.add(jj)
                child = Node(C.a, C.b, jj, nd.path + [Edge(ell, h)])
                nodes.append(child)
                nxt.append(child)
                if len(nodes) >= max_nodes:
                    return nodes
        frontier = nxt
    return nodes


# ---------------------------------------------------------------------------
# verification on points
# ---------------------------------------------------------------------------

def _forward_maps(E: Curve, path: list[Edge]):
    maps, cur = [], E
    for e in path:
        phi = EX.KernelIsogeny(cur, e.kernel, e.ell)
        maps.append(phi)
        cur = phi.codomain
    return maps, cur


def _dual(phi, ell: int, trace: int, P):
    """The rational ell-isogeny psi on phi's codomain with iso o psi o phi = +-[ell], or None."""
    E, C = phi.E, phi.codomain
    Q = phi(P)
    target = E.mul(ell, P)
    fdiv = EX.division_polynomials_flint(C.p, C.a, C.b, ell)
    for h in EX.rational_kernels(C, ell, fdiv, trace=trace):
        psi = EX.KernelIsogeny(C, h, ell)
        iso = isomorphism_to(psi.codomain, E)
        if iso is None:
            continue
        R = iso(psi(Q))
        if R == target:
            return psi, iso, 1
        if R == E.neg(target):
            return psi, iso, -1
    return None


def _scalar_in_model(Cw: Curve, model: Model, k: int, P):
    """k*P computed in the node's model and mapped back to the Weierstrass model Cw."""
    p = Cw.p
    if model.kind == "weierstrass":
        return Cw.mul(k, P)
    d = model.data
    s, alpha, A, B = d["s"], d["alpha"], d["A"], d["B"]
    if P is None:
        return None
    x, y = P
    u, v = s * (x - alpha) % p, s * y % p                       # Montgomery
    assert (B * v * v - u ** 3 - A * u * u - u) % p == 0, "Montgomery map"
    if v == 0 or (u + 1) % p == 0:
        return Cw.mul(k, P)                                     # exceptional points: not on the Edwards chart
    X, Y = u * pow(v, -1, p) % p, (u - 1) * pow(u + 1, -1, p) % p
    aE, dE = d["aE"], d["dE"]
    assert (aE * X * X + Y * Y - 1 - dE * X * X * Y * Y) % p == 0, "Edwards map"
    if model.kind == "edwards_a=-1":
        c = d["c"]                                              # c^2 = -aE; X' = c X gives -X'^2 + Y^2 = 1 + (dE/-aE) X'^2 Y^2
        a1, d1 = (-1) % p, dE * pow((-aE) % p, -1, p) % p
        X1 = c * X % p
        assert (a1 * X1 * X1 + Y * Y - 1 - d1 * X1 * X1 * Y * Y) % p == 0, "a = -1 rescaling"
        R = _mul(lambda P1, Q1: _e_add(p, a1, d1, P1, Q1), (0, 1), k, (X1, Y))
        R = (R[0] * pow(c, -1, p) % p, R[1])
    else:
        R = _mul(lambda P1, Q1: _e_add(p, aE, dE, P1, Q1), (0, 1), k, (X, Y))
    Xr, Yr = R
    if Yr == 1 and Xr == 0:
        return None
    if Xr == 0 or Yr == 1:
        return Cw.mul(k, P)
    ur = (1 + Yr) * pow(1 - Yr, -1, p) % p
    vr = ur * pow(Xr, -1, p) % p
    xr, yr = (ur * pow(s, -1, p) + alpha) % p, vr * pow(s, -1, p) % p
    return (xr, yr)


def verify_route(E: Curve, trace: int, n: int, cof: int, node: Node, model: Model, scalars: int, seed: int) -> dict:
    t0 = time.time()
    P = EX.point_of_order(E, n, cof, seed=seed)
    maps, C = _forward_maps(E, node.path)
    # duals, innermost last: back = dual_1 o ... o dual_r
    duals, cur_P = [], P
    for phi, e in zip(maps, node.path):
        d = _dual(phi, e.ell, trace, cur_P)
        if d is None:
            return {"ok": False, "reason": f"no rational dual found for the degree-{e.ell} step", "seconds": time.time() - t0}
        duals.append(d)
        cur_P = phi(cur_P)
    deg = 1
    for e in node.path:
        deg *= e.ell
    sign = 1
    for _psi, _iso, sg in duals:
        sign *= sg
    rng = random.Random(seed)
    checked = 0
    for _ in range(scalars):
        k = rng.randrange(1, n)
        want = E.mul(k, P)
        Q = P
        for phi in maps:
            Q = phi(Q)
        kk = k * pow(deg, -1, n) * sign % n
        R = _scalar_in_model(C, model, kk, Q)
        for psi, iso, _sg in reversed(duals):
            R = iso(psi(R))
        if R != want:
            return {"ok": False, "reason": f"k P mismatch at scalar {k}", "checked": checked, "seconds": time.time() - t0}
        checked += 1
    return {"ok": True, "checked": checked, "degree": deg, "dual_sign": sign, "seconds": round(time.time() - t0, 2)}


# ---------------------------------------------------------------------------
# one curve
# ---------------------------------------------------------------------------

def screen_curve(T: Target, *, ells: list[int], depth: int, max_nodes: int, disc_bound: int,
                 samples: int, verify_scalars: int, seed: int, role: str = "population") -> dict:
    t0 = time.time()
    Tw = weierstrass_target(T)
    p, a, b, n, h = Tw.p, Tw.coeffs["a"] % Tw.p, Tw.coeffs["b"] % Tw.p, Tw.n, Tw.h
    trace = Tw.trace
    E = Curve(p, a, b)
    INV_M_EQ[0] = float(sum(CW.arithmetic(p, a).inv))
    rng = random.Random(seed)
    ks = [rng.randrange(1, n) for _ in range(samples)]
    native = {"montgomery": "edwards", "edwards": "edwards"}.get(T.model, "weierstrass")

    def price(na: int, nb: int) -> list[dict]:
        rows = []
        for m in models_on(p, na, nb):
            c, where = scalar_cost(m.arith, ks)
            c08, _w08 = scalar_cost(m.arith, ks, 0.8)
            rows.append({"kind": m.kind, "note": m.note, "M_eq": round(c, 1), "schedule": where,
                         "M_eq_s08": round(c08, 1)})
        return rows

    nodes = bfs(E, trace, n, ells, depth, max_nodes)
    for nd in nodes:
        nd.models = price(nd.a, nd.b)
    # unit-endomorphism 2-GLV on every j = 0 / 1728 node the walk reaches (the crater of a D_K = -3 / -4
    # volcano); on the root it is part of the baseline, on any other node it is the priced ascent route
    glv_rows = {}
    for nd in nodes:
        if not ((nd.j == 0 and nd.a == 0) or (nd.j == 1728 % p and nd.b == 0)):
            continue
        poly = [1, 1, 1] if nd.j == 0 else [1, 0, 1]          # lambda^2 + lambda + 1, lambda^2 + 1 (low first)
        lams = EX._flint().fmpz_mod_poly_ctx(n)(poly).roots()
        if not lams:
            continue
        sm = CW.scalar_model(CW.arithmetic(p, nd.a), n, int(lams[0][0]), CW.chain_ops((), VARIANT),
                             samples=samples, seed=seed)
        glv_rows[nd.j if nd.path else "root"] = (nd, sm["glv"][sm["best_glv"]], sm["best_glv"])
    base_rows = list(nodes[0].models)
    if "root" in glv_rows:
        _nd, g, where = glv_rows["root"]
        base_rows.append({"kind": "weierstrass+GLV(unit)", "note": "unit endomorphism 2-GLV on E itself",
                          "M_eq": round(g, 1), "schedule": where})
    base = min(base_rows, key=lambda r: r["M_eq"])
    best = None
    for nd in nodes[1:]:
        path = [e.ell for e in nd.path]
        for r in nd.models:
            conv = conversion_cost(path, r["kind"], r["note"])
            row = {"path": path, "j": nd.j, "a": nd.a, "b": nd.b, **r,
                   "conversion_M_eq": round(conv, 1),
                   "oneshot_M_eq": round(r["M_eq"] + conv, 1),
                   "persistent_gain": round(1 - r["M_eq"] / base["M_eq"], 5),
                   "oneshot_gain": round(1 - (r["M_eq"] + conv) / base["M_eq"], 5),
                   "persistent_gain_s08": (round(1 - r["M_eq_s08"] / base["M_eq_s08"], 5)
                                           if base.get("M_eq_s08") else None)}
            if best is None or row["persistent_gain"] > best["persistent_gain"] or (
                    row["persistent_gain"] == best["persistent_gain"] and row["oneshot_gain"] > best["oneshot_gain"]):
                best = row
    # ascent arm: exact small-discriminant scan.  The scan certifies D_K and f_pi (Z[pi] = O_(f_pi));
    # f_E is certified here only for a root that is itself a j = 0 / 1728 crater (f_E = 1), else unresolved.
    scan = QO.small_discriminant_scan(trace * trace - 4 * p, disc_bound)
    root_crater = "root" in glv_rows
    ascent = {"D_K": scan.found, "f_pi": scan.conductor, "certificate": scan.certificate,
              "f_E": 1 if root_crater else "unresolved",
              "small_D_K": scan.found is not None}
    glv = None
    for key, (nd, g, where) in glv_rows.items():
        if key == "root":
            continue
        path = [e.ell for e in nd.path]
        conv = conversion_cost(path, "weierstrass", "")
        row = {"path": path, "j": nd.j, "glv_M_eq": round(g, 1), "schedule": where,
               "persistent_gain": round(1 - g / base["M_eq"], 5),
               "oneshot_gain": round(1 - (g + conv) / base["M_eq"], 5), "conversion_M_eq": round(conv, 1),
               "note": "unit endomorphism on the reached crater curve; 2-GLV priced with curvesweep.scalar_model"}
        if glv is None or row["oneshot_gain"] > glv["oneshot_gain"]:
            glv = row
    ascent["glv_on_reached_crater"] = glv
    ver = None
    if best is not None and best["persistent_gain"] > 0 and verify_scalars:
        nd = next(x for x in nodes if x.j == best["j"])
        model = next(m for m in models_on(p, nd.a, nd.b) if m.kind == best["kind"])
        ver = verify_route(E, trace, n, h, nd, model, verify_scalars, seed)
    # instrument check: on a curve of odd order no Montgomery/Edwards model may ever be reported
    order_odd = (h * n) % 2 == 1
    edwards_seen = any(r["kind"].startswith("edwards") for nd in nodes for r in nd.models)
    return {
        "name": T.name, "role": role, "family": T.family, "native_model": T.model, "bits": p.bit_length(),
        "p": hex(p), "a": hex(a), "b": hex(b), "n": hex(n), "cofactor": h, "trace": trace,
        "baseline": base, "baseline_models": base_rows,
        "nodes": len(nodes), "edges_by_ell": {str(l): sum(1 for nd in nodes[1:] if nd.path[-1].ell == l) for l in ells},
        "neighbour_models": [{"path": [e.ell for e in nd.path], "j": hex(nd.j),
                              "models": [(r["kind"], r["M_eq"]) for r in nd.models],
                              "weierstrass_class": nd.models[0]["note"]} for nd in nodes[1:]],
        "best": best, "verification": ver, "ascent": ascent,
        "instrument_check": {"order_odd": order_odd, "edwards_reported": edwards_seen,
                             "pass": not (order_odd and edwards_seen)},
        "native_cost_model": T.cost_model, "native_model_family": native,
        "seconds": round(time.time() - t0, 2),
    }


# ---------------------------------------------------------------------------
# controls
# ---------------------------------------------------------------------------

def positive_control(sources: list[Target], ells: list[int]) -> Target | None:
    """A curve one rational isogeny away from a deployed a = -3 curve, itself not a = -3-equivalent.

    Rule (frozen): the first source, in the order given, with a rational ell-isogeny (ell ascending)
    whose codomain is not a = -3-equivalent.  The detector must find the way back to the source.
    """
    for S in sources:
        p, a, b = S.p, S.coeffs["a"] % S.p, S.coeffs["b"] % S.p
        E = Curve(p, a, b)
        for ell, _h, C in neighbours(E, S.trace, [l for l in ells if S.n % l]):
            if "a = -3" in CW.arithmetic(p, C.a).note or "isomorphic to an a = -3" in CW.arithmetic(p, C.a).note:
                continue
            T = Target(f"control+: {ell}-isogenous neighbour of {S.name}", p, "weierstrass",
                       {"a": C.a, "b": C.b}, S.n, S.h, cost_model="weierstrass_jacobian_generic_a",
                       family="control", notes=f"constructed: {ell}-isogeny from {S.name}")
            return verify(T)
    return None


def ascent_control(bits: int, ells: list[int], seed: int = 1) -> tuple[Target | None, dict]:
    """A curve one descending step below a j = 0 crater (D_K = -3, f = ell): the ascent arm must fire."""
    from sympy import isprime, nextprime
    rng = random.Random(seed)
    while True:
        p = nextprime(rng.getrandbits(bits) | (1 << (bits - 1)))
        if p % 3 != 1:
            continue
        # 4p = t^2 + 3 v^2 (Cornacchia), the six j = 0 orders are p + 1 - t for t in the unit orbit
        reps = QO_cornacchia_4p(p)
        if reps is None:
            continue
        t0, v0 = reps
        traces = {t0, -t0, (t0 + 3 * v0) // 2, -(t0 + 3 * v0) // 2, (t0 - 3 * v0) // 2, -(t0 - 3 * v0) // 2}
        for t in sorted(traces):
            N = p + 1 - t
            for hh in (1, 2, 3, 4, 6, 8, 12):
                if N % hh == 0 and isprime(N // hh) and (N // hh).bit_length() > bits - 8:
                    break
            else:
                continue
            nn = N // hh
            for bb in range(1, 200):
                E0 = Curve(p, 0, bb)
                P = E0.point(bb)
                if E0.mul(N, P) is not None:
                    continue
                for ell, hk, C in neighbours(E0, t, [l for l in ells if nn % l]):
                    if C.j() == 0:
                        continue
                    T = Target(f"control+ascent: {ell}-descendant of a j = 0 curve ({bits}-bit)", p, "weierstrass",
                               {"a": C.a, "b": C.b}, nn, hh, cost_model="weierstrass_jacobian_generic_a",
                               family="control", notes=f"constructed: D_K = -3, f = {ell}")
                    return verify(T), {"p": hex(p), "crater_b": bb, "ell": ell, "trace": t}
                break


def QO_cornacchia_4p(p: int):
    """t, v with 4p = t^2 + 3 v^2, or None."""
    r = sqrt_mod(-3, p)
    if r is None:
        return None
    if r % 2 != 1:
        r = p - r
    a, bb = 2 * p, r
    from math import isqrt
    lim = isqrt(4 * p)
    while bb > lim:
        a, bb = bb, a % bb
    rest = 4 * p - bb * bb
    if rest % 3:
        return None
    v2 = rest // 3
    v = isqrt(v2)
    return (bb, v) if v * v == v2 else None


# ---------------------------------------------------------------------------
# population and report
# ---------------------------------------------------------------------------

def population(std_root: str | None, max_bits: int) -> list[tuple[Target, str]]:
    from .corpus import load_std_curves
    out, keys = [], set()

    def add(T, role):
        if T is None or T.ext_degree != 1 or T.model == "structural":
            return
        if not T.verified:
            return
        if T.p.bit_length() > max_bits:
            return
        try:
            Tw = weierstrass_target(T)
        except Exception:
            return
        key = (Tw.p, Curve(Tw.p, Tw.coeffs["a"], Tw.coeffs["b"]).j(), Tw.n)
        if key in keys:
            return
        keys.add(key)
        out.append((T, role))

    for T in deployed_targets():
        add(verify(T), "population")
    if std_root:
        for T, entry, _raw in load_std_curves(std_root):
            if T is not None:
                add(verify(T), "population")
    return out


def markdown(rows: list[dict], args) -> str:
    L = ["# Isogenous-model screen", "",
         f"ells {args.ells}, depth {args.depth}, {args.samples} random scalars per cost, "
         f"|D_K| bound {args.disc_bound}. Costs are modelled M_eq (M + S) in curvesweep's wNAF model; "
         "`persistent` keeps the point on the neighbour, `one-shot` charges forward chain, dual chain, "
         "model maps and the scalar adjustment.", "",
         "| curve | role | bits | h | E model (baseline M_eq) | nodes | best neighbour | path | persistent | one-shot | verified | D_K, conductors | crater GLV one-shot |",
         "|:--|:--|--:|--:|:--|--:|:--|:--|--:|--:|:--|:--|--:|"]
    for r in rows:
        b = r["best"]
        bn = f"{b['kind']} ({b['M_eq']})" if b else "none"
        path = "·".join(map(str, b["path"])) if b else ""
        pg = f"{100 * b['persistent_gain']:+.2f}%" if b else ""
        og = f"{100 * b['oneshot_gain']:+.2f}%" if b else ""
        v = r["verification"]
        vs = "" if v is None else ("yes ({} k)".format(v.get("checked")) if v["ok"] else "FAIL: " + v["reason"])
        asc = r["ascent"]
        cr = asc.get("glv_on_reached_crater")
        cg = "" if not cr else f"{100 * cr['oneshot_gain']:+.2f}% via {'·'.join(map(str, cr['path']))}"
        dk = f"{asc['D_K']}, f_pi={asc['f_pi']}, f_E={asc['f_E']}" if asc["D_K"] is not None else f"> {args.disc_bound}"
        L.append(f"| {r['name']} | {r['role']} | {r['bits']} | {r['cofactor']} | {r['baseline']['kind']} "
                 f"({r['baseline']['M_eq']}) | {r['nodes']} | {bn} | {path} | {pg} | {og} | {vs} | {dk} | {cg} |")
    return "\n".join(L) + "\n"


def _provenance(args) -> dict:
    def git(*c):
        try:
            return subprocess.check_output(["git", *c], text=True).strip()
        except Exception:
            return None
    return {"command": " ".join(sys.argv), "commit": git("rev-parse", "HEAD"),
            "dirty": bool(git("status", "--porcelain")), "python": sys.version, "platform": platform.platform(),
            "flint": __import__("flint").__version__, "args": vars(args),
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--std-curves", default=None)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--ells", default="2,3,5,7,11,13")
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--max-nodes", type=int, default=64)
    ap.add_argument("--disc-bound", type=int, default=1 << 20)
    ap.add_argument("--samples", type=int, default=200)
    ap.add_argument("--verify-scalars", type=int, default=8)
    ap.add_argument("--max-bits", type=int, default=521)
    ap.add_argument("--seed", type=int, default=20261016)
    ap.add_argument("--only", default=None, help="comma-separated substrings of curve names")
    args = ap.parse_args(argv)
    ells = [int(x) for x in args.ells.split(",")]
    os.makedirs(args.out_dir, exist_ok=True)
    prov = _provenance(args)
    pop = population(args.std_curves, args.max_bits)
    if args.only:
        keys = args.only.split(",")
        pop = [(T, r) for T, r in pop if any(k in T.name for k in keys)]
    a3 = [T for T, _r in pop if T.model == "weierstrass" and (T.coeffs["a"] + 3) % T.p == 0]
    controls = []
    pc = positive_control(a3, ells)
    if pc is not None:
        controls.append((pc, "control+model"))
    ac, ac_info = ascent_control(256, ells)
    if ac is not None:
        controls.append((ac, "control+ascent"))
    prov["ascent_control"] = ac_info
    rows = []
    jl = open(os.path.join(args.out_dir, "rows.jsonl"), "w")
    for T, role in controls + pop:
        if role == "population" and T.name in ("NIST P-256", "nist/P-256"):
            role = "control-"
        if role == "population" and T.name in ("Curve25519", "other/Curve25519"):
            role = "control-"
        try:
            r = screen_curve(T, ells=ells, depth=args.depth, max_nodes=args.max_nodes, disc_bound=args.disc_bound,
                             samples=args.samples, verify_scalars=args.verify_scalars, seed=args.seed, role=role)
        except Exception as exc:  # recorded, never dropped
            r = {"name": T.name, "role": role, "error": f"{type(exc).__name__}: {exc}"}
        rows.append(r)
        jl.write(json.dumps(r) + "\n")
        jl.flush()
        b = r.get("best")
        print(f"{r['name']:<48} nodes={r.get('nodes')} best={None if not b else (b['kind'], b['path'], b['persistent_gain'], b['oneshot_gain'])}"
              f" ver={None if not r.get('verification') else r['verification']['ok']} {r.get('error', '')}", flush=True)
    jl.close()
    prov["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    ok = [r for r in rows if "error" not in r]
    json.dump({"provenance": prov, "rows": rows}, open(os.path.join(args.out_dir, "isomodel.json"), "w"), indent=1)
    open(os.path.join(args.out_dir, "isomodel.md"), "w").write(markdown(ok, args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
