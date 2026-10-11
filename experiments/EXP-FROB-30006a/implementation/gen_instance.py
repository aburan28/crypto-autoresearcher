#!/usr/bin/env python3
"""Koblitz point-decomposition instance generator for EXP-FROB-30006a.

Builds the Weil-descent ANF (WDSat input format of SRC-ICPERF-TRIMOSKA-WDSAT-2024)
of the point-decomposition problem

    find X_1, ..., X_m in V  with  S_{m+1}(X_1, ..., X_m, X_r) = 0

where V is an l-dimensional F_2-subspace of GF(2^n) given by an RREF basis
(v_1, ..., v_l), S_{m+1} is the Semaev summation polynomial (m = 2: S3, m = 3: S4
in the elementary-symmetric form of the Trimoska generator), and X_r is the
abscissa of the target point R.

Modelling (fixed for both arms, so the arms differ ONLY in V):
  * unary variables 1 .. m*l          : x_{i,k}, X_i = sum_k x_{i,k} v_k   (point i, basis vector k)
  * unary variables m*l+1 .. m*l+n    : e2_j, coordinates of e2 = sum_{i<i'} X_i X_i' in the
                                        polynomial basis (t^j)
  * (m = 3) m*l+n+1 .. m*l+2n         : e3_j, coordinates of e3 = X_1 X_2 X_3
  * e1 = sum_i X_i lies in V and is substituted as a linear form in the x's (no variables).
  Equations:
  * n "E" equations per e-block: e_j + (coordinate j of the product) = 0, degree 2 (e2) / 3 (e3) in x;
  * n "D" equations: the coordinates of S_{m+1}(e1, e2, e3, X_r) = 0, which are linear in the
    e-coordinates for m = 2 and quadratic in them for m = 3 (squaring is F_2-linear).
  WDSat XOR-clause semantics: "x a b ... 0" asserts a XOR b XOR ... = TRUE, and the token T
  toggles the constant, so an equation P = 0 with constant term c is written WITH "T" when c = 0
  and WITHOUT it when c = 1 (read from dimacs.c of the vendored solver; matches the shipped
  Xn15l5-11-U.anf line "x T 16 1 6 11 0" meaning e16 = x1 + x6 + x11).

Target stream: rng = random.Random(seed); candidate k is the k-th random affine point R of E
(uniform abscissa, lifted, uniform among its two y's) drawn from that stream.  Which
candidate is used is decided OUTSIDE this module by the independent certifier
(pdp_enum.c): the first candidate certified UNSAT is the target.

Usage:
  gen_instance.py --n 41 --m 2 --l 20 --vkind stable --vindex 0 --seed 2026092001 --candidate 0 --out DIR
  gen_instance.py ... --vkind random --vseed 2026092010 ...
  gen_instance.py ... --plant   (SAT control: R = X_1 + ... + X_m with random X_i in V; records the witness)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple

from gf2n import GF2n, KoblitzCurve, lowest_weight_irreducible
from frob_basis import (coset_polynomials, coordinates, in_span, is_frobenius_stable, kernel,
                        random_subspace, rref, stable_subspace)

Mono = Tuple[int, ...]          # sorted tuple of unary variable ids (1-based); () is the constant
Expr = Dict[Mono, int]          # monomial -> field coefficient (int, polynomial basis)


# ----------------------------------------------------------------------------- expression arithmetic

def ex_add(a: Expr, b: Expr) -> Expr:
    r = dict(a)
    for m, c in b.items():
        v = r.get(m, 0) ^ c
        if v:
            r[m] = v
        else:
            r.pop(m, None)
    return r


def ex_mul(F: GF2n, a: Expr, b: Expr) -> Expr:
    r: Expr = {}
    for m1, c1 in a.items():
        for m2, c2 in b.items():
            m = tuple(sorted(set(m1) | set(m2)))   # boolean variables: x^2 = x
            c = F.mul(c1, c2)
            if not c:
                continue
            v = r.get(m, 0) ^ c
            if v:
                r[m] = v
            else:
                del r[m]
    return r


def ex_sqr(F: GF2n, a: Expr) -> Expr:
    # (sum c_m m)^2 = sum c_m^2 m  in characteristic 2 with idempotent monomials
    return {m: F.sqr(c) for m, c in a.items() if F.sqr(c)}


def ex_const(c: int) -> Expr:
    return {(): c} if c else {}


def ex_scale(F: GF2n, a: Expr, c: int) -> Expr:
    r = {}
    for m, v in a.items():
        w = F.mul(v, c)
        if w:
            r[m] = w
    return r


def boolean_equations(n: int, expr: Expr) -> List[Tuple[List[Mono], int]]:
    """Coordinate j of expr = 0, for j in 0..n-1: ([monomials], constant)."""
    eqs = []
    for j in range(n):
        monos = [m for m, c in expr.items() if (c >> j) & 1 and m != ()]
        const = 1 if ((expr.get((), 0) >> j) & 1) else 0
        eqs.append((sorted(monos), const))
    return eqs


# ----------------------------------------------------------------------------- ANF writer

def anf_line(monos: List[Mono], const: int, target_var: int | None = None) -> str:
    """One WDSat XOR clause for  [target_var +] sum(monos) + const = 0."""
    pieces = ["x"]
    if const == 0:
        pieces.append("T")
    if target_var is not None:
        pieces.append(str(target_var))
    for m in monos:
        if len(m) == 1:
            pieces.append(str(m[0]))
        else:
            pieces.append(f".{len(m)}")
            pieces.extend(str(v) for v in m)
    pieces.append("0")
    return " ".join(pieces)


# ----------------------------------------------------------------------------- instance

def build_field_and_curve(n: int) -> Tuple[GF2n, KoblitzCurve, int, dict]:
    F = GF2n(n, lowest_weight_irreducible(n))
    orders = {}
    chosen = None
    for a in (0, 1):
        E = KoblitzCurve(F, a)
        N = E.order()
        fac = factor(N)
        orders[a] = {"order": N, "factorisation": fac, "largest_prime_bits": max(fac).bit_length()}
    # a with the largest prime factor of #E (recorded either way)
    chosen = max((0, 1), key=lambda a: max(orders[a]["factorisation"]))
    return F, KoblitzCurve(F, chosen), chosen, orders


def factor(N: int) -> List[int]:
    fs, m, p = [], N, 2
    while p * p <= m:
        while m % p == 0:
            fs.append(p)
            m //= p
        p += 1 if p == 2 else 2
    if m > 1:
        fs.append(m)
    return fs


def choose_V(F: GF2n, l: int, vkind: str, vindex: int, vseed: int | None) -> Tuple[List[int], dict]:
    if vkind == "stable":
        cps = coset_polynomials(F.n)
        cands = [(C, g) for C, g in cps if len(C) == l]
        if not cands:
            raise SystemExit(f"no Frobenius-stable subspace of dimension {l} in GF(2^{F.n})")
        C, g = cands[vindex]
        V = stable_subspace(F, g)
        meta = {"vkind": "stable", "vindex": vindex, "factor_poly_hex": hex(g), "factor_degree": len(C),
                "cyclotomic_coset": C, "n_factors_of_this_degree": len(cands),
                "definition": "V = ker g(sigma), sigma: x -> x^2, g an irreducible factor of (T^n-1)/(T-1)"}
    elif vkind == "random":
        rng = random.Random(vseed)
        V, tries = random_subspace(F, l, rng)
        meta = {"vkind": "random", "vseed": vseed, "sampling_tries": tries,
                "definition": "RREF basis of the span of l uniform random vectors, resampled if rank < l or Frobenius-stable"}
    elif vkind == "polybasis":
        V = rref([1 << k for k in range(l)])
        meta = {"vkind": "polybasis", "definition": "span{1, t, ..., t^(l-1)} (Trimoska's factor base; pipeline check only)"}
    else:
        raise SystemExit("vkind must be stable|random|polybasis")
    meta["frobenius_stable"] = is_frobenius_stable(F, V)
    meta["dimension"] = len(V)
    meta["basis_rref_hex"] = [hex(v) for v in V]
    return V, meta


def parity_check_rows(F: GF2n, V: List[int]) -> List[int]:
    """h_1..h_{n-l} with v in V  iff  popcount(v & h_i) even for all i (left kernel of the basis)."""
    n = F.n
    # rows of the map c -> sum c_k v_k  is V; we need the kernel of the TRANSPOSE: vectors h with <h, v_k> = 0.
    # Build matrix with rows = bit-columns of V: for bit position b, the vector over k of bit b of v_k.
    cols = []
    for b in range(n):
        cols.append(sum(((v >> b) & 1) << k for k, v in enumerate(V)))
    # h in F_2^n with sum_b h_b * cols[b] = 0  ->  kernel of the map h -> XOR_{b in h} cols[b]
    H = kernel(cols, n)
    for h in H:
        for v in V:
            assert bin(h & v).count("1") % 2 == 0
    return H


def target_candidate(E: KoblitzCurve, seed: int, k: int) -> Tuple[int, int]:
    rng = random.Random(seed)
    for _ in range(k + 1):
        R = E.random_point(rng)
    return R


def generate(n: int, m: int, l: int, vkind: str, vindex: int, vseed: int | None, seed: int,
             candidate: int, plant: bool, out: Path) -> dict:
    F, E, a, orders = build_field_and_curve(n)
    V, vmeta = choose_V(F, l, vkind, vindex, vseed)
    H = parity_check_rows(F, V)

    witness = None
    if plant:
        rng = random.Random(seed ^ 0x5A17)
        pts = []
        while len(pts) < m:
            c = rng.getrandbits(l)
            X = 0
            for k in range(l):
                if (c >> k) & 1:
                    X ^= V[k]
            lifted = E.lift_x(X)
            if lifted:
                pts.append(lifted[rng.randrange(len(lifted))])
        R = None
        for P in pts:
            R = E.add(R, P)
        if R is None:
            raise SystemExit("planted points sum to O; change seed")
        witness = {"x_hex": [hex(P[0]) for P in pts], "coords": [coordinates(V, P[0]) for P in pts]}
    else:
        R = target_candidate(E, seed, candidate)
    xr = R[0]

    # ---- variables
    nx = m * l
    var_x = lambda i, k: i * l + k + 1                      # i in 0..m-1, k in 0..l-1
    e2_base = nx
    e3_base = nx + n
    n_unary = nx + n * (1 if m == 2 else 2)

    X = []
    for i in range(m):
        X.append({(var_x(i, k),): V[k] for k in range(l)})
    e1 = {}
    for Xi in X:
        e1 = ex_add(e1, Xi)
    # products (E-equations)
    if m == 2:
        e2_prod = ex_mul(F, X[0], X[1])
        e3_prod = None
    else:
        e2_prod = ex_add(ex_add(ex_mul(F, X[0], X[1]), ex_mul(F, X[0], X[2])), ex_mul(F, X[1], X[2]))
        e3_prod = ex_mul(F, ex_mul(F, X[0], X[1]), X[2])
    e2 = {(e2_base + j + 1,): 1 << j for j in range(n)}
    e3 = {(e3_base + j + 1,): 1 << j for j in range(n)} if m == 3 else None

    lines = []
    e_eq_count = 0
    for base, prod in ((e2_base, e2_prod), (e3_base, e3_prod)):
        if prod is None:
            continue
        for j, (monos, const) in enumerate(boolean_equations(n, prod)):
            lines.append(anf_line(monos, const, target_var=base + j + 1))
            e_eq_count += 1

    # ---- descended summation polynomial
    xr_e = ex_const(xr)
    if m == 2:
        # S3 = e2^2 + e1^2 Xr^2 + e2 Xr + b,  b = 1
        S = ex_add(ex_add(ex_sqr(F, e2), ex_scale(F, ex_sqr(F, e1), F.sqr(xr))), ex_scale(F, e2, xr))
        S = ex_add(S, ex_const(1))
    else:
        xr2 = F.sqr(xr)
        xr3 = F.mul(xr2, xr)
        xr4 = F.sqr(xr2)
        e1_2, e2_2, e3_2 = ex_sqr(F, e1), ex_sqr(F, e2), ex_sqr(F, e3)
        e1_4, e2_4, e3_4 = ex_sqr(F, e1_2), ex_sqr(F, e2_2), ex_sqr(F, e3_2)
        e3_3 = ex_mul(F, e3_2, e3)
        terms = [ex_const(xr4), e1_4, e3_4, ex_scale(F, e2_4, xr4), ex_scale(F, e3_3, xr),
                 ex_scale(F, ex_mul(F, e3, e2_2), xr3), ex_scale(F, ex_mul(F, e3, e1_2), xr),
                 ex_scale(F, e3, xr3), ex_scale(F, ex_mul(F, e1_2, e3_2), xr2), ex_scale(F, e3_2, xr4),
                 e3_2, ex_scale(F, e2_2, xr2)]
        S = {}
        for t in terms:
            S = ex_add(S, t)
    d_eqs = boolean_equations(n, S)
    for monos, const in d_eqs:
        lines.append(anf_line(monos, const))
    n_eqs = len(lines)
    header = f"p cnf {n_unary} {n_eqs}"
    anf_text = header + "\n" + "\n".join(lines) + "\n"

    # ---- sizing statistics (what WDSat must be compiled for)
    monos_nonunary = set()
    maxdeg = 1
    maxterms = 0
    maxline = 0
    for ln in lines:
        maxline = max(maxline, len(ln))
        toks = ln.split()[1:-1]
        i = 0
        terms = 0
        while i < len(toks):
            t = toks[i]
            if t == "T":
                i += 1
                continue
            if t.startswith("."):
                d = int(t[1:])
                monos_nonunary.add(tuple(toks[i + 1:i + 1 + d]))
                maxdeg = max(maxdeg, d)
                i += 1 + d
            else:
                i += 1
            terms += 1
        maxterms = max(maxterms, terms)
    out.mkdir(parents=True, exist_ok=True)
    anf_path = out / "instance.anf"
    anf_path.write_text(anf_text)
    inst = {
        "schema": "EXP-FROB-30006a.instance.v1",
        "n": n, "m": m, "l": l, "ml": m * l,
        "field": {"modulus_hex": hex(F.modulus), "modulus_poly": poly_str(F.modulus), "basis": "polynomial basis 1, t, ..., t^(n-1)"},
        "curve": {"equation": f"y^2 + x y = x^3 + {a} x^2 + 1", "a": a, "b": 1,
                  "order": orders[a]["order"], "order_factorisation": orders[a]["factorisation"],
                  "orders_considered": {str(k): v for k, v in orders.items()},
                  "a_choice_rule": "a in {0,1} maximising the largest prime factor of #E"},
        "V": vmeta,
        "V_parity_check_rows_hex": [hex(h) for h in H],
        "target": {"seed": seed, "candidate_index": candidate, "planted_sat": plant,
                   "R_x_hex": hex(R[0]), "R_y_hex": hex(R[1]), "xr_in_V": in_span(V, xr),
                   "draw_rule": "random.Random(seed): candidate k = k-th uniformly random affine point (uniform x, lifted; uniform y among the roots)"},
        "planted_witness": witness,
        "variables": {"n_unary": n_unary, "x_vars": f"1..{nx} (point i, basis coord k -> {l}*i + k + 1)",
                      "e2_vars": f"{e2_base + 1}..{e2_base + n}",
                      "e3_vars": (f"{e3_base + 1}..{e3_base + n}" if m == 3 else None),
                      "e1": "substituted linear form (in V)"},
        "equations": {"total": n_eqs, "E_product_equations": e_eq_count, "D_descent_equations": len(d_eqs)},
        "anf": {"path": anf_path.name, "sha256": hashlib.sha256(anf_text.encode()).hexdigest(),
                "n_nonunary_monomials": len(monos_nonunary), "max_degree": maxdeg,
                "max_terms_per_equation": maxterms, "max_line_chars": maxline,
                "wdsat_max_id_required": n_unary + len(monos_nonunary)},
    }
    (out / "instance.json").write_text(json.dumps(inst, indent=1))
    return inst


def poly_str(f: int) -> str:
    return " + ".join(f"t^{i}" if i > 1 else ("t" if i == 1 else "1") for i in reversed(range(f.bit_length())) if (f >> i) & 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--m", type=int, required=True, choices=(2, 3))
    ap.add_argument("--l", type=int, required=True)
    ap.add_argument("--vkind", required=True)
    ap.add_argument("--vindex", type=int, default=0)
    ap.add_argument("--vseed", type=int, default=None)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--candidate", type=int, default=0)
    ap.add_argument("--plant", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    inst = generate(a.n, a.m, a.l, a.vkind, a.vindex, a.vseed, a.seed, a.candidate, a.plant, Path(a.out))
    print(json.dumps({k: inst[k] for k in ("n", "m", "l", "variables", "equations", "anf", "target")}, indent=1))


if __name__ == "__main__":
    main()
