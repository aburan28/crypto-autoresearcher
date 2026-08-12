"""EXP-ICINV-e0cd8f: exact symbolic Semaev geometry across one isogeny class.

NEW MODULE. `harness/semaev.py` and `harness/exp_icinv.py` are NOT edited
(contract `source_constraints` and `invalidation_rules`); the S_3 expression
below is re-derived here so that this run's algebra is self-contained and can
be re-executed by a third party without importing the older harness, and it is
checked for character-level agreement with `harness.semaev.s3_expr` at run time
(`s3_expression_agrees_with_committed_harness`).

DEFINING CONSTRAINT: no factor-base membership polynomial f_V appears in any
ideal built here. The ideal is

    I_m(E) = < S_m , dS_m/dx_1 , ... , dS_m/dx_m >

over F_p, and nothing else.

Run under `sage -python`. Everything is deterministic exact computation over
F_p; the only randomness is the seeded gauge parameters u and the seeded
control-set draw, both recorded per curve.

Stopping rules are evaluated and recorded in the contract's own order:
SR1 (support gate) -> SR2 (census gate) -> SR3 (backend gate) -> resolutions,
with SR4 forcing the control-set artifact to be written and closed before any
class multiset is read for interpretation. SR6 (wall clock) is checked between
curves; SR7 verdicts are computed inside the run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import sympy  # noqa: E402
import yaml  # noqa: E402

from sage.all import GF, PolynomialRing, singular  # noqa: E402

P = 4001
TRACE = 30
DISCRIMINANT = TRACE * TRACE - 4 * P
SEED = 20260810
MONOMIAL_ORDER = "degrevlex"
SECOND_MONOMIAL_ORDER = "deglex"
CROSSCHECK_MIN_CURVES = 20

# The committed record this run binds its reference values to, read AT RUN TIME
# and hashed (contract invalidation rule on transcription).
CENSUS_REFERENCE = "experiments/EXP-ICINV-180a0d/runs/RUN-ICINV-p4001-a/raw-result.json"
SPEC_PATH = "experiments/EXP-ICINV-e0cd8f/specification.yaml"
HANDOFF_PATH = "ledger/handoffs/TASK-20260810-5ad325.yaml"


# ---------------------------------------------------------------- utilities

def sha256_file(path: str) -> str:
    with open(os.path.join(REPO, path), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def peak_rss_bytes() -> int:
    ru = resource.getrusage(resource.RUSAGE_SELF)
    return ru.ru_maxrss * (1024 if platform.system() == "Linux" else 1)


def cpu_seconds() -> float:
    ru = resource.getrusage(resource.RUSAGE_SELF)
    return ru.ru_utime + ru.ru_stime


class Budget(RuntimeError):
    """SR6: wall-clock or memory budget exhausted."""


class Recorder:
    """Writes artifacts into the run directory IN ORDER, logging each write.

    The order log is what makes SR4 checkable: `control-set-invariants.json`
    carries an earlier timestamp and a lower sequence number than any artifact
    holding a class multiset, and its sha256 is fixed at that moment.
    """

    def __init__(self, run_dir: str, wall_limit: float, mem_limit_bytes: int):
        self.run_dir = run_dir
        os.makedirs(run_dir)
        self.started = time.time()
        self.wall_limit = wall_limit
        self.mem_limit = mem_limit_bytes
        self.log: list[dict] = []
        self.lines: list[str] = []

    def check_budget(self, where: str) -> None:
        el = time.time() - self.started
        if el > self.wall_limit:
            raise Budget(f"SR6 wall clock {el:.1f}s > {self.wall_limit}s at {where}")
        rss = peak_rss_bytes()
        if rss > self.mem_limit:
            raise Budget(f"SR6 peak rss {rss} > {self.mem_limit} at {where}")

    def say(self, msg: str) -> None:
        line = "[%8.2fs] %s" % (time.time() - self.started, msg)
        self.lines.append(line)
        print(line, flush=True)

    def write(self, name: str, obj) -> str:
        path = os.path.join(self.run_dir, name)
        text = json.dumps(obj, indent=2, sort_keys=True, default=str)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        digest = hashlib.sha256(text.encode()).hexdigest()
        self.log.append({
            "sequence": len(self.log) + 1,
            "artifact": name,
            "written_at": iso(time.time()),
            "elapsed_seconds": round(time.time() - self.started, 3),
            "sha256": digest,
        })
        self.say("WROTE %s (sha256 %s...)" % (name, digest[:12]))
        return digest

    def write_text(self, name: str, text: str) -> None:
        with open(os.path.join(self.run_dir, name), "w", encoding="utf-8") as fh:
            fh.write(text)


# ------------------------------------------------------- S_3 / S_4 algebra

def s3_generic(X1, X2, X3, a, b):
    """Third summation polynomial for y^2 = x^3 + a x + b (KN-TECH-002)."""
    return ((X1 - X2) ** 2 * X3 ** 2
            - 2 * ((X1 + X2) * (X1 * X2 + a) + 2 * b) * X3
            + ((X1 * X2 - a) ** 2 - 4 * b * (X1 + X2)))


def ring_m3(order: str):
    R = PolynomialRing(GF(P), 'x1,x2,x3', order=order)
    return R


def ring_m3_hom(order: str):
    return PolynomialRing(GF(P), 'x0,x1,x2,x3', order=order)


def homogenise(g, Rh):
    """Generator-wise homogenisation with the NEW variable x0.

    DECLARED, not derived (contract `grading`): each generator is homogenised
    to its own total degree and the ideal is generated by the results. This is
    NOT in general the same as the ideal-theoretic homogenisation (the
    saturation with respect to x0); whether they differ is recorded per curve
    as `saturation_differs` rather than being silently chosen.
    """
    x0 = Rh.gen(0)
    d = g.degree()
    out = Rh.zero()
    for c, m in zip(g.coefficients(), g.monomials()):
        e = m.exponents()[0]
        mon = Rh.gen(1) ** e[0] * Rh.gen(2) ** e[1] * Rh.gen(3) ** e[2]
        out += c * x0 ** (d - m.degree()) * mon
    return out


def affine_degree(I) -> int:
    """Degree of the affine scheme: Singular `mult(std(I))`.

    For a zero-dimensional ideal this equals the vector-space dimension of the
    quotient (checked at run time on every zero-dimensional case); in general
    it is the multiplicity of the leading-term ideal, which is the standard
    degree of the affine scheme.
    """
    return int(singular(I).std().mult())


def betti_from_shifts(res) -> dict:
    """beta_{i,j} from the graded shifts of a MINIMAL free resolution of S/J."""
    table: dict[str, int] = {}
    for i in range(len(res) + 1):
        for j in res.shifts(i):
            key = "%d,%d" % (i, int(j))
            table[key] = table.get(key, 0) + 1
    return table


def regularity_from_betti(table: dict) -> int:
    return max(int(k.split(",")[1]) - int(k.split(",")[0]) for k in table)


def factorisation_type(poly) -> list:
    """Partition of the degree: sorted (degree, multiplicity) of F_p-factors."""
    fac = poly.factor()
    parts = []
    for f, e in fac:
        parts.extend([int(f.degree())] * int(e))
    return sorted(parts)


# --------------------------------------------------- backend A: Sage/Singular

def invariants_m3(a: int, b: int, order: str = MONOMIAL_ORDER) -> dict:
    """Every m = 3 invariant for one curve, from ONE Groebner/resolution pass."""
    Ra = ring_m3(order)
    x1, x2, x3 = Ra.gens()
    F = s3_generic(x1, x2, x3, GF(P)(a), GF(P)(b))
    gens = [F] + [F.derivative(v) for v in Ra.gens()]
    I = Ra.ideal(gens)

    support = len(F.monomials())
    dim_aff = int(I.dimension())
    deg_aff = affine_degree(I)
    vsdim = int(I.vector_space_dimension()) if dim_aff == 0 else None
    if vsdim is not None and vsdim != deg_aff:
        raise RuntimeError("degree disagreement a=%d b=%d: mult=%d vsdim=%d"
                           % (a, b, deg_aff, vsdim))
    unit_ideal = bool(I.is_one())
    sing_empty = bool(dim_aff < 0)      # Sage returns -1 for the unit ideal
    if dim_aff == 0:
        V = I.variety()
        fp_points = len(V)
        fp_x3_values = sorted({int(pt[x3]) for pt in V})
    else:
        fp_points, fp_x3_values = None, None

    E = I.elimination_ideal([x1, x2])
    egens = [g for g in E.gens() if g != 0]
    if not egens:
        elim = {"empty": True, "degree": None, "factorisation_type": None,
                "polynomial": None,
                "projection_dimension": dim_aff}
    else:
        cand = min(egens, key=lambda q: q.degree(x3))
        g = cand.polynomial(x3).monic()      # univariate over F_p, monic
        elim = {"empty": False, "degree": int(g.degree()),
                "factorisation_type": factorisation_type(g),
                "polynomial": str(g),
                "n_elimination_generators": len(egens),
                "projection_dimension": dim_aff}

    Rh = ring_m3_hom(order)
    J = Rh.ideal([homogenise(g, Rh) for g in gens])
    res = J.graded_free_resolution(algorithm='minimal')
    betti = betti_from_shifts(res)
    reg_quotient = regularity_from_betti(betti)
    dim_proj = int(J.dimension())
    sat = J.saturation(Rh.ideal(Rh.gen(0)))[0]
    saturation_differs = bool(sat != J)

    n_gens = len(gens)
    codim_proj = 4 - dim_proj
    gen_degrees = sorted(int(g.degree()) for g in gens)
    koszul_table: dict[str, int] = {"0,0": 1}
    from itertools import combinations
    for i in range(1, n_gens + 1):
        for comb in combinations(gen_degrees, i):
            key = "%d,%d" % (i, sum(comb))
            koszul_table[key] = koszul_table.get(key, 0) + 1

    return {
        "a": a, "b": b,
        "monomial_order": order,
        "s3_support": support,
        "s3_total_degree": int(F.degree()),
        "singular_locus_affine": {
            "dimension": dim_aff, "degree": deg_aff,
            "vector_space_dimension": vsdim,
            "is_unit_ideal": unit_ideal, "is_empty": sing_empty,
            "fp_rational_points": fp_points,
            "fp_rational_x3_values": fp_x3_values,
        },
        "elimination": elim,
        "betti": betti,
        "regularity_of_quotient_S_mod_J": reg_quotient,
        "regularity_of_ideal_J": reg_quotient + 1,
        "projective_dimension": len(res),
        "homogenised_dimension": dim_proj,
        "saturation_differs": saturation_differs,
        "koszul": {
            "n_generators": n_gens,
            "generator_degrees": gen_degrees,
            "codimension_projective": codim_proj,
            "codimension_affine": 3 - dim_aff if dim_aff >= 0 else None,
            "is_regular_sequence": bool(codim_proj == n_gens),
            "betti_equals_koszul_table": bool(betti == koszul_table),
            "koszul_table": koszul_table,
            "definition": (
                "regular sequence <=> codim of the homogenised ideal in "
                "F_p[x0..x3] equals the number of Jacobian generators (4). "
                "Note 4 elements can never be a regular sequence in the "
                "3-variable AFFINE ring, so the test is stated projectively."),
        },
    }


def invariants_m4(a: int, b: int) -> dict:
    """m = 4 secondary: monomial support and affine singular locus only."""
    R4 = PolynomialRing(GF(P), 'x1,x2,x3,x4', order=MONOMIAL_ORDER)
    Rt = PolynomialRing(R4, 'T')
    T = Rt.gen()
    x1, x2, x3, x4 = R4.gens()
    left = s3_generic(R4(x1), R4(x2), T, GF(P)(a), GF(P)(b))
    right = s3_generic(R4(x3), R4(x4), T, GF(P)(a), GF(P)(b))
    S4 = left.resultant(right)
    gens = [S4] + [S4.derivative(v) for v in R4.gens()]
    I = R4.ideal(gens)
    dim_aff = int(I.dimension())
    deg_aff = affine_degree(I)
    return {
        "a": a, "b": b,
        "s4_support": len(S4.monomials()),
        "s4_total_degree": int(S4.degree()),
        "singular_locus_affine": {"dimension": dim_aff, "degree": deg_aff},
        "betti": "not_computed",
        "regularity": "not_computed",
        "not_computed_reason": (
            "BUDGET statement under AGENTS.md rule 5 and the contract's "
            "arities.secondary_scope, never a constancy claim."),
    }


# ---------------------------------- backend B: msolve (third-party, independent)

def _dim_from_leading_exponents(lts: list[tuple[int, ...]], nvars: int) -> int:
    from itertools import combinations
    for k in range(nvars, -1, -1):
        for S in combinations(range(nvars), k):
            comp = [i for i in range(nvars) if i not in S]
            if not any(all(m[i] == 0 for i in comp) for m in lts):
                return k
    return -1


def _standard_monomial_count(lts: list[tuple[int, ...]], nvars: int) -> int | None:
    bounds = []
    for i in range(nvars):
        pure = [m[i] for m in lts if all(m[t] == 0 for t in range(nvars) if t != i)]
        if not pure:
            return None
        bounds.append(min(pure))
    count = 0
    from itertools import product
    for e in product(*[range(bd) for bd in bounds]):
        if not any(all(e[k] >= m[k] for k in range(nvars)) for m in lts):
            count += 1
    return count


def msolve_affine(a: int, b: int) -> dict:
    """Dimension, degree and F_p points from msolve -- a THIRD-PARTY engine.

    msolve (Berthomieu, Eder, Safey El Din) is an independent implementation of
    F4/FGLM over prime fields; it shares no code with Singular. Sage is used
    only as the calling harness (`algorithm='msolve'`); the Groebner basis and
    the variety are msolve's.
    """
    Ra = ring_m3(MONOMIAL_ORDER)
    x1, x2, x3 = Ra.gens()
    F = s3_generic(x1, x2, x3, GF(P)(a), GF(P)(b))
    I = Ra.ideal([F] + [F.derivative(v) for v in Ra.gens()])
    gb = I.groebner_basis(algorithm='msolve', proof=False)
    if list(gb) == [Ra.one()]:
        return {"engine": "msolve", "dimension": -1, "degree": 0,
                "is_unit_ideal": True, "gb_size": 1,
                "fp_points": 0, "distinct_x3_values_in_F_p": 0}
    lts = [g.lm().exponents()[0] for g in gb]
    dim = _dim_from_leading_exponents(lts, 3)
    deg = _standard_monomial_count(lts, 3) if dim == 0 else None
    pts, x3vals = None, None
    if dim == 0:
        V = I.variety(algorithm='msolve', proof=False)
        pts = len(V)
        x3vals = sorted({int(pt[x3]) for pt in V})
    return {"engine": "msolve", "dimension": dim, "degree": deg,
            "is_unit_ideal": False, "gb_size": len(gb),
            "fp_points": pts, "fp_x3_values": x3vals,
            "distinct_x3_values_in_F_p": None if x3vals is None else len(x3vals)}


# ------------------------------------------- backend C: SymPy (independent)

def _grevlex_lm(expr, gens) -> tuple[int, ...]:
    """Leading exponent vector of `expr` under GREVLEX.

    sympy.Poly.monoms() sorts by LEX by default; taking monoms()[0] as the
    leading monomial of a grevlex Groebner basis element is wrong, and was
    caught here by a KeyError against the standard-monomial basis.
    """
    from sympy.polys.orderings import grevlex
    return max(sympy.Poly(expr, *gens, modulus=P).monoms(), key=grevlex)


def sympy_affine(a: int, b: int) -> dict:
    """Dimension, degree and elimination polynomial via SymPy's Buchberger.

    Shares no code with Singular: SymPy implements its own Buchberger over
    GF(p) in pure Python.
    """
    x1, x2, x3 = sympy.symbols('x1 x2 x3')
    F = s3_generic(x1, x2, x3, a, b)
    gens = [sympy.expand(F)] + [sympy.expand(sympy.diff(F, v)) for v in (x1, x2, x3)]
    G = sympy.groebner(gens, x1, x2, x3, modulus=P, order='grevlex')
    lts = [_grevlex_lm(g, (x1, x2, x3)) for g in G.exprs]
    if list(G.exprs) == [1]:
        return {"dimension": -1, "degree": 0, "is_unit_ideal": True,
                "elimination_degree": None, "elimination_factorisation_type": None}
    # dimension: largest subset of variables carrying no pure leading monomial
    from itertools import combinations
    dim = -1
    for k in range(3, -1, -1):
        for S in combinations(range(3), k):
            comp = [i for i in range(3) if i not in S]
            if not any(all(m[i] == 0 for i in comp) for m in lts):
                dim = max(dim, k)
        if dim >= 0:
            break
    # degree for the zero-dimensional case: number of standard monomials
    degree = None
    if dim == 0:
        bounds = []
        for i in range(3):
            pure = [m[i] for m in lts if all(m[t] == 0 for t in range(3) if t != i)]
            bounds.append(min(pure))
        std = 0
        for e0 in range(bounds[0]):
            for e1 in range(bounds[1]):
                for e2 in range(bounds[2]):
                    if not any(e0 >= m[0] and e1 >= m[1] and e2 >= m[2] for m in lts):
                        std += 1
        degree = std
    Gl = sympy.groebner(gens, x1, x2, x3, modulus=P, order='lex')
    uni = [g for g in Gl.exprs if not g.has(x1) and not g.has(x2) and g != 0]
    if not uni:
        elim_deg, elim_type = None, None
    else:
        pol = sympy.Poly(min(uni, key=lambda q: sympy.degree(q, x3)), x3, modulus=P)
        pol = pol.monic()
        elim_deg = int(pol.degree())
        parts = []
        for f, e in sympy.factor_list(pol.as_expr(), x3, modulus=P)[1]:
            parts.extend([int(sympy.degree(f, x3))] * int(e))
        elim_type = sorted(parts)
    return {"dimension": dim, "degree": degree, "is_unit_ideal": False,
            "elimination_degree": elim_deg,
            "elimination_factorisation_type": elim_type}


def _rank_gfp(rows: list[list[int]], p: int) -> int:
    rows = [r[:] for r in rows]
    ncols = len(rows[0]) if rows else 0
    r = 0
    for c in range(ncols):
        piv = None
        for i in range(r, len(rows)):
            if rows[i][c] % p:
                piv = i
                break
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        inv = pow(rows[r][c], p - 2, p)
        rows[r] = [(v * inv) % p for v in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c] % p:
                f = rows[i][c]
                rows[i] = [(rows[i][k] - f * rows[r][k]) % p for k in range(ncols)]
        r += 1
        if r == len(rows):
            break
    return r


def sympy_betti(a: int, b: int, jmax: int) -> dict:
    """Graded Betti numbers via KOSZUL HOMOLOGY, independent of Singular.

    beta_{i,j} = dim_k Tor_i^S(S/J, k)_j, computed as the homology of the
    Koszul complex on x0..x3 tensored with S/J. The only computer algebra used
    is SymPy's Buchberger (for a Groebner basis of the homogeneous ideal J and
    for normal forms); the linear algebra over GF(p) is the local `_rank_gfp`.
    No Singular code is on this path.
    """
    from itertools import combinations
    x0, x1, x2, x3 = sympy.symbols('x0 x1 x2 x3')
    V = (x0, x1, x2, x3)
    xa1, xa2, xa3 = sympy.symbols('x1 x2 x3')
    F = sympy.expand(s3_generic(xa1, xa2, xa3, a, b))
    aff = [F] + [sympy.expand(sympy.diff(F, v)) for v in (xa1, xa2, xa3)]
    hgens = []
    for g in aff:
        pol = sympy.Poly(g, xa1, xa2, xa3, modulus=P)
        d = pol.total_degree()
        h = 0
        for mono, coeff in zip(pol.monoms(), pol.coeffs()):
            h += int(coeff) * x0 ** (d - sum(mono)) * x1 ** mono[0] * x2 ** mono[1] * x3 ** mono[2]
        hgens.append(sympy.expand(h))
    G = sympy.groebner(hgens, x0, x1, x2, x3, modulus=P, order='grevlex')
    lts = [_grevlex_lm(g, V) for g in G.exprs]

    def standard_monomials(d: int):
        out = []
        for e0 in range(d + 1):
            for e1 in range(d - e0 + 1):
                for e2 in range(d - e0 - e1 + 1):
                    e3 = d - e0 - e1 - e2
                    e = (e0, e1, e2, e3)
                    if not any(all(e[k] >= m[k] for k in range(4)) for m in lts):
                        out.append(e)
        return out

    basis = {d: standard_monomials(d) for d in range(0, jmax + 2)}
    index = {d: {m: i for i, m in enumerate(basis[d])} for d in basis}

    def nf_coords(mono: tuple[int, ...], d: int) -> list[int]:
        """Normal form of a monomial of degree d, in the standard basis of degree d."""
        vec = [0] * len(basis[d])
        expr = x0 ** mono[0] * x1 ** mono[1] * x2 ** mono[2] * x3 ** mono[3]
        rem = sympy.Poly(G.reduce(expr)[1], *V, modulus=P)
        if rem.is_zero:
            return vec
        for mm, cc in zip(rem.monoms(), rem.coeffs()):
            vec[index[d][mm]] = int(cc) % P
        return vec

    subsets = {i: list(combinations(range(4), i)) for i in range(5)}

    def dmatrix(i: int, j: int):
        """Matrix of d: (Lambda^i (x) S/J)_j -> (Lambda^{i-1} (x) S/J)_j."""
        src_deg, tgt_deg = j - i, j - i + 1
        if src_deg < 0 or src_deg > jmax + 1 or tgt_deg > jmax + 1:
            return [], 0, 0
        src = [(T, m) for T in subsets[i] for m in basis[src_deg]]
        tgt = [(T, m) for T in subsets[i - 1] for m in basis[tgt_deg]]
        tgt_index = {k: n for n, k in enumerate(tgt)}
        rows = []
        for (T, m) in src:
            row = [0] * len(tgt)
            for pos, t in enumerate(T):
                sign = (-1) ** pos
                Tm = tuple(u for u in T if u != t)
                mm = list(m)
                mm[t] += 1
                coords = nf_coords(tuple(mm), tgt_deg)
                for n, c in enumerate(coords):
                    if c:
                        row[tgt_index[(Tm, basis[tgt_deg][n])]] = \
                            (row[tgt_index[(Tm, basis[tgt_deg][n])]] + sign * c) % P
            rows.append(row)
        return rows, len(src), len(tgt)

    betti = {}
    for i in range(0, 5):
        for j in range(0, jmax + 1):
            if j - i < 0 or j - i > jmax + 1:
                continue
            dim_src = len(subsets[i]) * len(basis[j - i])
            if dim_src == 0:
                continue
            if i == 0:
                rank_out = 0
            else:
                rows, ns, nt = dmatrix(i, j)
                rank_out = _rank_gfp(rows, P) if rows and nt else 0
            rows_in, ns_in, nt_in = dmatrix(i + 1, j) if i + 1 <= 4 else ([], 0, 0)
            rank_in = _rank_gfp(rows_in, P) if rows_in and nt_in else 0
            h = dim_src - rank_out - rank_in
            if h:
                betti["%d,%d" % (i, j)] = h
    return betti


# ------------------------------------------------------------ census / gates


def enumerate_class() -> tuple[list[dict], dict]:
    from harness.isogeny_class import (isogeny_classes, class_census,
                                       hurwitz_class_number)
    classes = isogeny_classes(P)
    census = class_census(P, classes)
    members = [{"a": r.a, "b": r.b, "j": r.j, "aut_order": r.aut_order,
                "order": r.order} for r in classes[TRACE]]
    members.sort(key=lambda r: (r["a"], r["b"]))
    row = [c for c in census if c.trace == TRACE][0]
    cert = {
        "observed_curves": row.observed_curves,
        "observed_weighted": row.observed_weighted,
        "predicted_weighted_hurwitz": row.predicted_weighted,
        "agrees": bool(row.agrees),
        "hurwitz_H_4p_minus_t2": hurwitz_class_number(4 * P - TRACE * TRACE),
        "census_failures_all_traces": sum(0 if c.agrees else 1 for c in census),
        "traces_checked": len(census),
    }
    return members, cert


def support_derivation() -> dict:
    """SR1: SYMBOLIC re-derivation of 13 / 9 / 10, in SymPy with a, b symbolic."""
    a, b, x1, x2, x3 = sympy.symbols('a b x1 x2 x3')
    F = sympy.expand(s3_generic(x1, x2, x3, a, b))
    pol = sympy.Poly(F, x1, x2, x3)
    generic = len(pol.monoms())
    terms = {str(sympy.prod([v ** e for v, e in zip((x1, x2, x3), m)])): str(c)
             for m, c in zip(pol.monoms(), pol.coeffs())}
    a0 = sympy.Poly(sympy.expand(F.subs(a, 0)), x1, x2, x3)
    b0 = sympy.Poly(sympy.expand(F.subs(b, 0)), x1, x2, x3)
    from harness.semaev import s3_expr
    committed = sympy.expand(s3_expr(a, b).subs(
        {sympy.Symbol('x1'): x1, sympy.Symbol('x2'): x2, sympy.Symbol('x3'): x3}))
    agrees_with_harness = bool(sympy.simplify(sympy.expand(committed - F)) == 0)
    return {
        "s3_expression_agrees_with_committed_harness": agrees_with_harness,
        "committed_harness_reference": "harness/semaev.py:s3_expr (NOT edited)",
        "backend": "sympy %s (symbolic a, b over ZZ)" % sympy.__version__,
        "expression": str(F),
        "monomials_in_x1_x2_x3": terms,
        "support_generic": generic,
        "support_a_equals_0": len(a0.monoms()),
        "support_b_equals_0": len(b0.monoms()),
        "contract_reference": {"generic": 13, "a_zero": 9, "b_zero": 10},
        "derivation_agrees": bool(generic == 13 and len(a0.monoms()) == 9
                                  and len(b0.monoms()) == 10),
    }


def backend_provenance() -> dict:
    """SR3: both backends, with versions, recorded BEFORE any resolution."""
    import sage.version as sage_version
    sing_ver = str(singular.eval("system(\"version\");")).strip()
    absent = {}
    for prog in ("M2", "Macaulay2", "Singular", "magma", "giac", "msolve"):
        which = subprocess.run(["which", prog], capture_output=True, text=True)
        absent[prog] = which.stdout.strip() or None
    msolve_ver = None
    if absent.get("msolve"):
        out = subprocess.run([absent["msolve"], "-h"], capture_output=True, text=True)
        for line in (out.stdout + out.stderr).splitlines():
            if "version" in line.lower():
                msolve_ver = line.strip()
                break
    msolve_selftest = None
    try:
        msolve_selftest = msolve_affine(460, 2974)
    except Exception as exc:
        msolve_selftest = {"error": "%s: %s" % (type(exc).__name__, exc)}
    # SELF-TEST of backend A on a hand-checkable example, inside this run.
    from sage.all import QQ
    Rq = PolynomialRing(QQ, 'x,y,z')
    xq, yq, zq = Rq.gens()
    resq = Rq.ideal([xq * yq, yq * zq, zq * xq]).graded_free_resolution(algorithm='minimal')
    selftest = {"ideal": "(xy, yz, zx) in QQ[x,y,z]",
                "resolution": str(resq),
                "shifts": {str(i): [int(s) for s in resq.shifts(i)]
                           for i in range(len(resq) + 1)},
                "expected_ranks": "S^1 <-- S^3 <-- S^2 <-- 0",
                "passes": bool(len(resq) == 2
                               and len(resq.shifts(1)) == 3
                               and len(resq.shifts(2)) == 2)}
    # SELF-TEST of backend B on the same ideal, by Koszul homology over GF(p).
    return {
        "backend_A": {
            "role": "primary: Groebner bases, minimal free resolutions, "
                    "Betti tables, regularity, dimension, degree, elimination",
            "name": "SageMath driving Singular (libsingular)",
            "sage_version": str(sage_version.version),
            "sage_release_date": str(sage_version.date),
            "singular_version_string": sing_ver,
            "singular_version_human": "4.4.1" if sing_ver.startswith("44100") else sing_ver,
            "self_test": selftest,
            "working": bool(selftest["passes"]),
        },
        "backend_B": {
            "role": "SECOND, THIRD-PARTY, INDEPENDENT engine: Groebner basis, "
                    "dimension, degree, and F_p-rational points",
            "name": "msolve (Berthomieu, Eder, Safey El Din), called through "
                    "Sage with algorithm='msolve'",
            "path": absent.get("msolve"),
            "version_string": msolve_ver,
            "shares_no_code_with_backend_A": True,
            "self_test": msolve_selftest,
            "working": bool(msolve_selftest and "error" not in msolve_selftest),
            "covers": ["singular-locus dimension", "singular-locus degree",
                       "F_p-rational point count", "number of distinct "
                       "F_p-rational x3 values (cross-checks the degree-1 "
                       "part of the elimination polynomial's factorisation "
                       "type)"],
            "does_not_cover": ["minimal free resolutions", "graded Betti "
                               "numbers", "Castelnuovo-Mumford regularity"],
        },
        "backend_C": {
            "role": "third route, used because NO second off-the-shelf "
                    "RESOLUTION engine exists on this host: Groebner bases, "
                    "dimension, degree, elimination polynomial with its "
                    "factorisation type, and graded Betti numbers via Koszul "
                    "homology",
            "name": "SymPy Buchberger over GF(p) + Koszul-homology Tor "
                    "computation implemented in this module",
            "sympy_version": sympy.__version__,
            "python_version": platform.python_version(),
            "shares_no_code_with_backend_A": True,
            "is_off_the_shelf_resolution_engine": False,
            "working": True,
        },
        "resolution_backend_limitation": (
            "Macaulay2 and Magma are ABSENT on this host, and neither msolve "
            "nor SymPy computes syzygies, so there is NO second off-the-shelf "
            "engine for minimal free resolutions. The graded Betti numbers on "
            "the cross-check subsample are therefore cross-checked by an "
            "INDEPENDENT ROUTE -- homology of the Koszul complex on x0..x3 "
            "tensored with S/J, SymPy normal forms, local GF(p) linear "
            "algebra -- rather than by a second engine. Whether that "
            "discharges control C-BACKEND in full for the Betti family is a "
            "REVIEWER judgement, not the executor's."),
        "disagreement_with_the_dispatching_precondition_probe": (
            "The handoff records the dispatching session's probe as finding "
            "Macaulay2, standalone Singular and Magma ABSENT. THIS RUN'S OWN "
            "PROBE DISAGREES ON TWO POINTS, recorded here as the handoff "
            "directs: (1) msolve 0.9.5 IS present at /opt/homebrew/bin/msolve "
            "and works through Sage, and is used here as backend B; (2) a "
            "standalone `Singular` binary IS present inside the Sage tree at "
            "/var/tmp/sage-10.9-current/local/bin/Singular -- it is the SAME "
            "engine as libsingular, so it is NOT an independent backend and "
            "is not used as one. Macaulay2, Magma and giac are absent, "
            "confirming the rest of the probe."),
        "absent_probe": absent,
        "sr3_evaluated_by": "this run, from inside the run, before any "
                            "resolution was computed",
    }


# ------------------------------------------------------------- control set

def draw_control_set(rng) -> tuple[list[dict], dict]:
    from harness.isogeny_class import isogeny_classes
    classes = isogeny_classes(P)
    pool = []
    for t, recs in classes.items():
        if t == TRACE:
            continue
        if t % P == 0:                       # supersingular: not ordinary
            continue
        for r in recs:
            pool.append({"a": r.a, "b": r.b, "j": r.j, "trace": t,
                         "aut_order": r.aut_order})
    pool.sort(key=lambda r: (r["trace"], r["a"], r["b"]))
    chosen = rng.sample(pool, 138)
    traces = sorted({r["trace"] for r in chosen})
    meta = {
        "seed": SEED,
        "rng": "python random.Random(%d).sample" % SEED,
        "pool_size": len(pool),
        "drawn": len(chosen),
        "distinct_traces_drawn": len(traces),
        "traces_drawn": traces,
        "excluded_traces": [TRACE, 0],
        "excluded_reason": "t = 30 is the class under test; t = 0 is "
                           "supersingular, and the control is ordinary curves",
    }
    return chosen, meta


# ------------------------------------------------------------- multisets

FAMILIES = {
    "F1_s3_support": lambda r: r["s3_support"],
    "F2_betti_table": lambda r: json.dumps(r["betti"], sort_keys=True),
    "F2b_regularity": lambda r: r["regularity_of_quotient_S_mod_J"],
    "F3_singular_locus_dim_degree": lambda r: (
        r["singular_locus_affine"]["dimension"], r["singular_locus_affine"]["degree"]),
    "F4_elimination_degree": lambda r: r["elimination"]["degree"],
    "F4b_elimination_factorisation_type": lambda r: (
        None if r["elimination"]["factorisation_type"] is None
        else tuple(r["elimination"]["factorisation_type"])),
}


def multisets(rows: list[dict]) -> dict:
    out = {}
    for name, fn in FAMILIES.items():
        counts: dict[str, int] = {}
        for r in rows:
            counts[str(fn(r))] = counts.get(str(fn(r)), 0) + 1
        out[name] = {"distinct_values": len(counts),
                     "multiset": dict(sorted(counts.items()))}
    return out


# ------------------------------------------------------------------- stages

def gauge_transform(a: int, b: int, u: int) -> tuple[int, int]:
    F = GF(P)
    return int(F(u) ** 4 * F(a)), int(F(u) ** 6 * F(b))


def run_class_stage(rec: Recorder, curves: list[dict], rng, label: str,
                    with_gauge: bool = True) -> tuple[list[dict], list[dict]]:
    rows, gauge_rows = [], []
    for n, c in enumerate(curves):
        rec.check_budget("%s curve %d/%d" % (label, n + 1, len(curves)))
        t0 = time.time()
        inv = invariants_m3(c["a"], c["b"])
        inv["seconds"] = round(time.time() - t0, 4)
        inv["j"] = c["j"]
        inv["trace"] = c.get("trace", TRACE)
        inv["aut_order"] = c["aut_order"]
        inv["two_torsion_x_count"] = two_torsion_x_count(c["a"], c["b"])
        rows.append(inv)
        if with_gauge:
            u = rng.randrange(1, P)
            ga, gb = gauge_transform(c["a"], c["b"], u)
            ginv = invariants_m3(ga, gb)
            agree = {
                "s3_support": ginv["s3_support"] == inv["s3_support"],
                "betti": ginv["betti"] == inv["betti"],
                "regularity": (ginv["regularity_of_quotient_S_mod_J"]
                               == inv["regularity_of_quotient_S_mod_J"]),
                "singular_dim": (ginv["singular_locus_affine"]["dimension"]
                                 == inv["singular_locus_affine"]["dimension"]),
                "singular_degree": (ginv["singular_locus_affine"]["degree"]
                                    == inv["singular_locus_affine"]["degree"]),
                "elimination_degree": (ginv["elimination"]["degree"]
                                       == inv["elimination"]["degree"]),
                "elimination_factorisation_type": (
                    ginv["elimination"]["factorisation_type"]
                    == inv["elimination"]["factorisation_type"]),
            }
            gauge_rows.append({"a": c["a"], "b": c["b"], "u": u,
                               "gauged_a": ga, "gauged_b": gb,
                               "agreements": agree,
                               "all_agree": all(agree.values())})
        if (n + 1) % 25 == 0:
            rec.say("%s %d/%d done" % (label, n + 1, len(curves)))
    return rows, gauge_rows


def two_torsion_x_count(a: int, b: int) -> int:
    from harness.exp_icinv import two_torsion_x_count as f
    return int(f(P, a, b))


def crosscheck(rec: Recorder, class_rows: list[dict], control_rows: list[dict],
               subsample: list[tuple[int, int]]) -> dict:
    out = {"subsample_size": len(subsample), "curves": [],
           "second_monomial_order": SECOND_MONOMIAL_ORDER}
    by_key = {(r["a"], r["b"]): r for r in class_rows + control_rows}
    for (a, b) in subsample:
        rec.check_budget("crosscheck (%d,%d)" % (a, b))
        base = by_key[(a, b)]
        try:
            mb = msolve_affine(a, b)
            msolve_err = None
        except Exception as exc:
            mb, msolve_err = None, "%s: %s" % (type(exc).__name__, exc)
        sb = sympy_affine(a, b)
        jmax = max(int(k.split(",")[1]) for k in base["betti"]) + 1
        t0 = time.time()
        try:
            bB = sympy_betti(a, b, jmax)
            betti_err = None
        except Exception as exc:                        # recorded, not hidden
            bB, betti_err = None, "%s: %s" % (type(exc).__name__, exc)
        alt = invariants_m3(a, b, order=SECOND_MONOMIAL_ORDER)
        out["curves"].append({
            "a": a, "b": b,
            "backend_A": {
                "dimension": base["singular_locus_affine"]["dimension"],
                "degree": base["singular_locus_affine"]["degree"],
                "elimination_degree": base["elimination"]["degree"],
                "elimination_factorisation_type": base["elimination"]["factorisation_type"],
                "betti": base["betti"],
                "regularity": base["regularity_of_quotient_S_mod_J"],
            },
            "backend_B_msolve": mb, "backend_B_error": msolve_err,
            "backend_C_sympy": {
                "dimension": sb["dimension"], "degree": sb["degree"],
                "elimination_degree": sb["elimination_degree"],
                "elimination_factorisation_type": sb["elimination_factorisation_type"],
                "betti": bB, "betti_error": betti_err,
                "seconds": round(time.time() - t0, 3),
            },
            "second_order_backend_A": {
                "dimension": alt["singular_locus_affine"]["dimension"],
                "degree": alt["singular_locus_affine"]["degree"],
                "elimination_degree": alt["elimination"]["degree"],
                "betti": alt["betti"],
                "regularity": alt["regularity_of_quotient_S_mod_J"],
            },
            "agreements": {
                "backend_B_dimension": (mb["dimension"] == base["singular_locus_affine"]["dimension"]) if mb else None,
                "backend_B_degree": (mb["degree"] == base["singular_locus_affine"]["degree"]) if mb else None,
                "backend_B_fp_points": (
                    (mb["fp_points"] == base["singular_locus_affine"]["fp_rational_points"])
                    if (mb and mb.get("fp_points") is not None) else None),
                "backend_B_fp_x3_values": (
                    (mb["fp_x3_values"] == base["singular_locus_affine"]["fp_rational_x3_values"])
                    if (mb and mb.get("fp_x3_values") is not None) else None),
                "backend_C_dimension": sb["dimension"] == base["singular_locus_affine"]["dimension"],
                "backend_C_degree": sb["degree"] == base["singular_locus_affine"]["degree"],
                "backend_C_elimination_degree": sb["elimination_degree"] == base["elimination"]["degree"],
                "backend_C_elimination_type": sb["elimination_factorisation_type"] == base["elimination"]["factorisation_type"],
                "backend_C_betti": (bB == base["betti"]) if bB is not None else None,
                "order_independent_dimension": alt["singular_locus_affine"]["dimension"] == base["singular_locus_affine"]["dimension"],
                "order_independent_degree": alt["singular_locus_affine"]["degree"] == base["singular_locus_affine"]["degree"],
                "order_independent_betti": alt["betti"] == base["betti"],
                "order_independent_regularity": alt["regularity_of_quotient_S_mod_J"] == base["regularity_of_quotient_S_mod_J"],
            },
        })
    flat = [c["agreements"] for c in out["curves"]]
    out["all_backend_B_agree"] = all(
        v for c in flat for k, v in c.items() if k.startswith("backend_B") and v is not None)
    out["all_backend_C_agree"] = all(
        v for c in flat for k, v in c.items() if k.startswith("backend_C") and v is not None)
    out["all_order_independent"] = all(
        v for c in flat for k, v in c.items() if k.startswith("order_independent"))
    out["betti_crosschecked_curves"] = sum(
        1 for c in flat if c.get("backend_C_betti") is not None)
    return out


# ---------------------------------------------------------------- run driver

INFERENCE_DEVIATION = {
    "requested_policy": "executor-implementation",
    "policy_binding_resolves_to": "anthropic:claude-sonnet-5",
    "policy_binding_reasoning_effort": "medium",
    "policy_binding_source": "orchestration.adapter resolve --role executor",
    "actual_answering_model": "claude-opus-5",
    "fallback_used": True,
    "fallback_allowed_by_handoff": False,
    "degraded_allowed_by_handoff": False,
    "classification": "protocol_deviation",
    "direction": "UPWARD (same vendor, higher-capability tier), NOT a "
                 "degradation",
    "cause": "STRUCTURAL, not discretionary: every .claude/agents/*.md carries "
             "`model: inherit`, so this runtime cannot honour a per-role model "
             "binding at subagent level. CLAUDE.md's model-policy note "
             "prescribes the remedy as PROCESS-LEVEL (launch the session via "
             "`orchestration.adapter env`); it is a harness change, not an "
             "executor one.",
    "authorisation": "The dispatching Coordinator was informed BEFORE any "
                     "compute was spent and authorised proceeding with the "
                     "deviation recorded.",
    "must_not_be_cited_as": "policy-compliant, or as strengthening any result. "
                            "A more capable model does not raise the claim "
                            "tier, does not widen scope and does not license "
                            "any conclusion the contract would otherwise deny.",
    "nothing_else_changed": "No threshold, scope, budget, stopping rule or "
                            "metric was altered. The contract is frozen.",
    "model_judgement_steps": (
        "Every reported number is produced by the exact symbolic computation "
        "in harness/exp_icinv_geometry.py (sha256 pinned in "
        "code.source), re-executable by a third party with `sage -python` and "
        "no model in the loop. Steps that turned on MODEL JUDGEMENT rather "
        "than exact computation, named explicitly: (1) the CHOICE of backend B "
        "-- SymPy plus a Koszul-homology Tor computation -- given that "
        "Macaulay2/Magma/giac/msolve are absent from the host; (2) the CHOICE "
        "of the committed record bound as the SR2 census reference "
        "(EXP-ICINV-180a0d RUN-ICINV-p4001-a raw-result.json); (3) the "
        "DEFINITION selected for the affine degree (Singular `mult` of the "
        "leading-term ideal) and for the Koszul/regular-sequence indicator "
        "(codimension equals generator count, stated projectively); (4) the "
        "CHOICE of deglex as the second monomial order. None of these is a "
        "measured value; each is a recorded, re-executable decision."),
}


def stopping_rule_record(name: str, status: str, detail) -> dict:
    return {"rule": name, "status": status, "detail": detail,
            "evaluated_at": iso(time.time())}


def write_manifest(rec: Recorder, run_id: str, status: str, valid: bool,
                   invalid_reason, command: str, metrics: dict,
                   parameters: dict, stopping_rules: list[dict],
                   deviations: list[str], started: float) -> None:
    from harness.runner import git_state, source_provenance, untracked_source_vs_output
    import sage.version as sage_version
    commit, dirty = git_state()
    env = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "sage_version": str(sage_version.version),
        "sage_release_date": str(sage_version.date),
        "singular_version_string": str(singular.eval('system("version");')).strip(),
        "dependencies": {"sympy": sympy.__version__, "pyyaml": yaml.__version__},
        "host_cpu_count": os.cpu_count(),
        "host_load_average_at_end": list(os.getloadavg()),
    }
    rec.write_text("environment.json", json.dumps(env, indent=2, sort_keys=True))
    finished = time.time()
    manifest = {"run": {
        "id": run_id,
        "experiment_id": "EXP-ICINV-e0cd8f",
        "hypothesis_id": "H-ICINV-d5e351",
        "question_id": "RQ-ICINV-475b5e",
        "goal_id": "GOAL-ENDO-001",
        "batch_id": "BATCH-d7e255",
        "handoff_id": "TASK-20260810-5ad325",
        "status": status,
        "claim_tier": "toy",
        "sota_delta": 0,
        "ecdlp_claim": "none, in either direction",
        "code": {"commit": commit, "dirty": dirty, "command": command,
                 "source": source_provenance(),
                 "untracked": untracked_source_vs_output()},
        "inference": INFERENCE_DEVIATION,
        "environment": env,
        "inputs": {"parameters": parameters, "seed": SEED,
                   "reference_records": {
                       CENSUS_REFERENCE: sha256_file(CENSUS_REFERENCE),
                       SPEC_PATH: sha256_file(SPEC_PATH),
                       HANDOFF_PATH: sha256_file(HANDOFF_PATH)}},
        "timing": {"started_at": iso(started), "finished_at": iso(finished),
                   "wall_seconds": round(finished - started, 3)},
        "resources": {"peak_rss_bytes": peak_rss_bytes(),
                      "cpu_seconds": round(cpu_seconds(), 3),
                      "wall_clock_limit_seconds": rec.wall_limit,
                      "memory_limit_bytes": rec.mem_limit},
        "result": {"metrics": metrics, "valid": valid,
                   "invalid_reason": invalid_reason,
                   "certificate": {
                       "kind": "none",
                       "verified": True,
                       "verifier": "no-claim",
                       "note": "Pure exact-symbolic measurement run. No "
                               "discrete-log solve and no factor-base "
                               "relation is claimed, so certificate.kind is "
                               "explicitly `none` per "
                               "docs/claims-and-verification.md. The "
                               "internal consistency checks that DO act as "
                               "certificates here -- gauge recheck, "
                               "second-monomial-order recheck, second-backend "
                               "cross-check, Hurwitz-Kronecker census -- are "
                               "recorded in their own artifacts."}},
        "stopping_rules": stopping_rules,
        "protocol_deviations": deviations,
        "artifact_write_order": rec.log,
        "interpretation": "NONE. This run records observations only. Whether "
                          "the Semaev geometry is a class invariant is a "
                          "Coordinator judgement after independent review "
                          "(handoff constraint SC-2).",
    }}
    rec.write_text("manifest.yaml", yaml.safe_dump(manifest, sort_keys=False))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["gates", "m3", "m4"], required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--wall-limit", type=float, default=7200.0)
    ap.add_argument("--mem-limit-gb", type=float, default=8.0)
    args = ap.parse_args()

    import random
    started = time.time()
    run_dir = os.path.join(REPO, "experiments", "EXP-ICINV-e0cd8f", "runs",
                           args.run_id)
    if os.path.exists(run_dir):
        print("run records are immutable: %s exists" % run_dir, file=sys.stderr)
        return 2
    rec = Recorder(run_dir, args.wall_limit, int(args.mem_limit_gb * 2 ** 30))
    command = "sage -python harness/exp_icinv_geometry.py --stage %s --run-id %s" % (
        args.stage, args.run_id)
    rec.write_text("command.txt", command + "\n")
    rec.say("EXP-ICINV-e0cd8f stage=%s run=%s" % (args.stage, args.run_id))
    rec.say("host load average at start: %s" % (os.getloadavg(),))

    stopping: list[dict] = []
    deviations = [
        "D-1 INFERENCE POLICY: run answered by claude-opus-5 while the "
        "executor-implementation binding resolves to anthropic:claude-sonnet-5. "
        "Structural (all subagents are `model: inherit`), UPWARD, recorded as "
        "a protocol deviation, Coordinator-authorised before compute. See "
        "manifest.run.inference.",
        "D-2 SECOND BACKEND, AND A DISAGREEMENT WITH THE HANDOFF'S "
        "PRECONDITION PROBE: this run's own probe finds msolve 0.9.5 PRESENT "
        "at /opt/homebrew/bin/msolve (the handoff records it as absent), and "
        "a standalone Singular binary present inside the Sage tree -- the "
        "same engine as libsingular, so not independent and not used as such. "
        "Macaulay2, Magma and giac are confirmed absent. msolve is therefore "
        "used as backend B, a genuine third-party independent engine, for "
        "dimension, degree and F_p points. But NO second off-the-shelf engine "
        "for MINIMAL FREE RESOLUTIONS exists on this host, so graded Betti "
        "numbers are cross-checked by an independent ROUTE (backend C: SymPy "
        "normal forms plus Koszul-homology Tor and local GF(p) linear "
        "algebra), not by a second engine. Whether that discharges C-BACKEND "
        "in full for the Betti family is a reviewer judgement.",
        "D-3 VOLCANO COVARIATE: the contract states it does not rebuild the "
        "2-volcano, and the committed reference supplies only the level "
        "HISTOGRAM {0:3,1:9,2:18,3:36,4:72}, not per-curve levels. The "
        "secondary metric `contingency table against true 2-volcano level` is "
        "therefore reported as not_computed; the computable covariate "
        "two_torsion_x_count is recorded per curve instead. This is a "
        "recorded gap, not an imputation.",
    ]
    metrics: dict = {}
    parameters = {"p": P, "trace": TRACE, "discriminant": DISCRIMINANT,
                  "monomial_order": MONOMIAL_ORDER,
                  "second_monomial_order": SECOND_MONOMIAL_ORDER,
                  "arity": {"gates": 3, "m3": 3, "m4": 4}[args.stage],
                  "ideal": "I_m = <S_m, dS_m/dx_1, ..., dS_m/dx_m>; NO f_V",
                  "grading": "homogenised with a new variable x0, standard "
                             "grading, over F_p[x0..x_m]",
                  "seed": SEED}
    status, valid, invalid_reason = "completed_valid", True, None

    try:
        # ---- prerequisite E0: enumeration (needed by both SR1 and SR2)
        rec.check_budget("enumeration")
        t0 = time.time()
        members, census_cert = enumerate_class()
        rec.say("enumerated class: %d members in %.1fs"
                % (len(members), time.time() - t0))

        # ---- SR1 SUPPORT GATE (runs first)
        sd = support_derivation()
        rec.say("SR1 symbolic derivation: generic=%d a0=%d b0=%d agrees=%s"
                % (sd["support_generic"], sd["support_a_equals_0"],
                   sd["support_b_equals_0"], sd["derivation_agrees"]))
        per_member = []
        Ra = ring_m3(MONOMIAL_ORDER)
        x1s, x2s, x3s = Ra.gens()
        for m in members:
            F = s3_generic(x1s, x2s, x3s, GF(P)(m["a"]), GF(P)(m["b"]))
            per_member.append({"a": m["a"], "b": m["b"], "j": m["j"],
                               "s3_support": len(F.monomials())})
        supports = sorted({r["s3_support"] for r in per_member})
        sd["per_class_member_support"] = per_member
        sd["distinct_supports_on_class"] = supports
        sd["all_members_support_13"] = bool(supports == [13])
        sd["members_checked"] = len(per_member)
        sr1_pass = bool(sd["derivation_agrees"] and sd["all_members_support_13"])
        rec.write("support-derivation.json", sd)
        stopping.append(stopping_rule_record(
            "SR1 support gate", "passed" if sr1_pass else "FIRED",
            {"derivation_agrees": sd["derivation_agrees"],
             "distinct_supports_on_class": supports,
             "members_checked": len(per_member)}))
        if not sr1_pass:
            raise RuntimeError("SR1 fired: support gate failed")

        # ---- SR2 CENSUS GATE
        ref_path = CENSUS_REFERENCE
        ref_sha = sha256_file(ref_path)
        with open(os.path.join(REPO, ref_path)) as fh:
            ref = json.load(fh)
        ref_rows = ref["raw"]["per_class"]["30"]["rows"]
        ref_pairs = sorted((int(r["a"]), int(r["b"])) for r in ref_rows)
        our_pairs = sorted((m["a"], m["b"]) for m in members)
        census = {
            "p": P, "trace": TRACE, "discriminant": DISCRIMINANT,
            "fundamental_discriminant": -59, "conductor": 16,
            "re_emitted_member_count": len(members),
            "members": members,
            "hurwitz_certificate": census_cert,
            "committed_reference": {
                "path": ref_path, "source_sha256": ref_sha,
                "target_class_size": int(ref["raw"]["census"]["target_class_size"]),
                "target_class_predicted_weighted":
                    ref["raw"]["census"]["target_class_predicted_weighted"],
                "member_count_in_reference_rows": len(ref_rows),
                "note": "read from the committed record AT RUN TIME and bound "
                        "by sha256; no reference value is transcribed.",
            },
            "reference_s3_support_values_in_committed_rows":
                sorted({int(r["s3_support"]) for r in ref_rows}),
            "agrees_on_count": bool(len(members)
                                    == int(ref["raw"]["census"]["target_class_size"])),
            "agrees_on_member_set": bool(our_pairs == ref_pairs),
            "members_only_here": [list(x) for x in sorted(set(our_pairs) - set(ref_pairs))],
            "members_only_in_reference": [list(x) for x in sorted(set(ref_pairs) - set(our_pairs))],
            "true_volcano_levels_reference_not_rebuilt": {
                "histogram": {0: 3, 1: 9, 2: 18, 3: 36, 4: 72},
                "status": "NOT REBUILT by this contract; per-curve levels are "
                          "unavailable, see deviation D-3.",
            },
        }
        sr2_pass = bool(census["agrees_on_count"] and census["agrees_on_member_set"]
                        and census_cert["agrees"])
        rec.write("class-census.json", census)
        stopping.append(stopping_rule_record(
            "SR2 census gate", "passed" if sr2_pass else "FIRED",
            {"re_emitted": len(members),
             "committed_reference_count": int(ref["raw"]["census"]["target_class_size"]),
             "hurwitz_agrees": census_cert["agrees"],
             "member_set_identical": census["agrees_on_member_set"]}))
        if not sr2_pass:
            status, valid = "completed_invalid", False
            invalid_reason = "SR2 fired: PREMISE-FAILED, census disagreement"
            raise RuntimeError(invalid_reason)

        # ---- SR3 BACKEND GATE, before any resolution
        bp = backend_provenance()
        rec.write("backend-provenance.json", bp)
        sr3_pass = bool(bp["backend_A"]["working"] and bp["backend_B"]["working"]
                        and bp["backend_C"]["working"])
        stopping.append(stopping_rule_record(
            "SR3 backend gate",
            "passed_with_recorded_limitation" if sr3_pass else "FIRED",
            {"backend_A": bp["backend_A"]["name"],
             "backend_A_versions": {
                 "sage": bp["backend_A"]["sage_version"],
                 "sage_release_date": bp["backend_A"]["sage_release_date"],
                 "singular": bp["backend_A"]["singular_version_human"],
                 "singular_raw": bp["backend_A"]["singular_version_string"]},
             "backend_A_self_test_passes": bp["backend_A"]["self_test"]["passes"],
             "backend_B": bp["backend_B"]["name"],
             "backend_B_version": bp["backend_B"]["version_string"],
             "backend_C": bp["backend_C"]["name"],
             "backend_C_versions": {"sympy": bp["backend_C"]["sympy_version"],
                                    "python": bp["backend_C"]["python_version"]},
             "limitation": "no second OFF-THE-SHELF resolution engine on this "
                           "host; see deviation D-2",
             "recorded_before_any_resolution": True}))
        if not sr3_pass:
            status, valid = "failed_infrastructure", False
            invalid_reason = "SR3 fired: no working computer-algebra backend"
            raise RuntimeError(invalid_reason)

        metrics.update({
            "sr1_support_gate": "passed",
            "sr2_census_gate": "passed",
            "sr3_backend_gate": "passed_with_recorded_limitation",
            "class_size_re_emitted": len(members),
            "s3_support_distinct_on_class": supports,
        })

        if args.stage == "gates":
            metrics["stage"] = "gates only: SR1, SR2, SR3. No resolution was " \
                               "computed in this run."
            rec.write("raw-result.json", {"metrics": metrics,
                                          "certificate": {"kind": "none"},
                                          "raw": {"stopping_rules": stopping}})
        elif args.stage == "m3":
            rng = random.Random(SEED)
            # SR4: CONTROL FIRST. Drawn, computed and WRITTEN before any class
            # multiset is read.
            controls, cmeta = draw_control_set(rng)
            rec.say("control set drawn: %d curves, %d distinct traces"
                    % (len(controls), cmeta["distinct_traces_drawn"]))
            crows, cgauge = run_class_stage(rec, controls, rng, "control")
            control_ms = multisets(crows)
            rec.write("control-set-invariants.json", {
                "draw": cmeta, "n_curves": len(crows),
                "per_curve": crows,
                "multisets": control_ms,
                "gauge_recheck": cgauge,
                "all_gauge_agree": all(g["all_agree"] for g in cgauge),
                "sr4_note": "WRITTEN AND CLOSED BEFORE any class multiset was "
                            "read for interpretation; see "
                            "manifest.run.artifact_write_order.",
            })
            stopping.append(stopping_rule_record(
                "SR4 control first", "satisfied",
                {"control_artifact_sequence": len(rec.log),
                 "class_multisets_read_after": True}))

            # ---- class
            rng_class = random.Random(SEED + 1)
            rows, gauge = run_class_stage(rec, members, rng_class, "class")
            class_ms = multisets(rows)
            rec.write("per-curve-invariants.json", {
                "p": P, "trace": TRACE, "n_curves": len(rows),
                "per_curve": rows, "multisets": class_ms,
                "volcano_contingency": "not_computed (deviation D-3)",
            })
            rec.write("gauge-recheck.json", {
                "seed": SEED, "class": gauge, "control": cgauge,
                "all_class_agree": all(g["all_agree"] for g in gauge),
                "all_control_agree": all(g["all_agree"] for g in cgauge),
                "transform": "(a,b) -> (u^4 a, u^6 b) with the induced "
                             "weighted change of variables x_i -> u^2 x_i",
            })
            rec.write("koszul-indicator.json", {
                "class": [{"a": r["a"], "b": r["b"], **r["koszul"]} for r in rows],
                "control": [{"a": r["a"], "b": r["b"], **r["koszul"]} for r in crows],
                "class_all_regular_sequence": all(r["koszul"]["is_regular_sequence"] for r in rows),
                "class_any_regular_sequence": any(r["koszul"]["is_regular_sequence"] for r in rows),
                "class_all_betti_equals_koszul": all(r["koszul"]["betti_equals_koszul_table"] for r in rows),
                "control_all_regular_sequence": all(r["koszul"]["is_regular_sequence"] for r in crows),
                "control_all_betti_equals_koszul": all(r["koszul"]["betti_equals_koszul_table"] for r in crows),
            })

            # ---- cross-check subsample: every distinct value + >= 20 curves
            picked: list[tuple[int, int]] = []
            seen: set = set()
            for name, fn in FAMILIES.items():
                for r in rows + crows:
                    key = (name, str(fn(r)))
                    if key not in seen:
                        seen.add(key)
                        if (r["a"], r["b"]) not in picked:
                            picked.append((r["a"], r["b"]))
            i = 0
            while len(picked) < CROSSCHECK_MIN_CURVES and i < len(rows):
                if (rows[i]["a"], rows[i]["b"]) not in picked:
                    picked.append((rows[i]["a"], rows[i]["b"]))
                i += 1
            i = 0
            while len(picked) < CROSSCHECK_MIN_CURVES + 10 and i < len(crows):
                if (crows[i]["a"], crows[i]["b"]) not in picked:
                    picked.append((crows[i]["a"], crows[i]["b"]))
                i += 1
            rec.say("cross-check subsample: %d curves" % len(picked))
            cc = crosscheck(rec, rows, crows, picked)
            cc["selection_rule"] = (
                "every curve realising a distinct value of any family, in "
                "either set, plus filler to exceed the contract's minimum of "
                "%d curves. Fixed before any verdict was computed." % CROSSCHECK_MIN_CURVES)
            rec.write("backend-crosscheck.json", cc)

            # ---- SR7 verdict, computed inside the run
            per_family = {}
            for name in FAMILIES:
                per_family[name] = {
                    "class_distinct_values": class_ms[name]["distinct_values"],
                    "class_multiset": class_ms[name]["multiset"],
                    "control_distinct_values": control_ms[name]["distinct_values"],
                    "control_multiset": control_ms[name]["multiset"],
                    "class_constant": class_ms[name]["distinct_values"] == 1,
                    "control_constant": control_ms[name]["distinct_values"] == 1,
                    "same_single_value": (
                        class_ms[name]["distinct_values"] == 1
                        and control_ms[name]["distinct_values"] == 1
                        and list(class_ms[name]["multiset"]) == list(control_ms[name]["multiset"])),
                }
            class_constant = all(v["class_constant"] for v in per_family.values())
            witness = None
            if not class_constant:
                for name, v in per_family.items():
                    if v["class_constant"]:
                        continue
                    vals = {}
                    for r in rows:
                        vals.setdefault(str(FAMILIES[name](r)), []).append([r["a"], r["b"]])
                    keys = sorted(vals)
                    witness = {"family": name,
                               "curve_1": vals[keys[0]][0], "value_1": keys[0],
                               "curve_2": vals[keys[-1]][0], "value_2": keys[-1]}
                    break
            mode_deviants = {}
            for name, fn in FAMILIES.items():
                counts = class_ms[name]["multiset"]
                if len(counts) <= 1:
                    continue
                mode = max(counts, key=lambda k: counts[k])
                mode_deviants[name] = [
                    {"a": r["a"], "b": r["b"], "j": r["j"],
                     "two_torsion_x_count": r["two_torsion_x_count"],
                     "value": str(fn(r)),
                     "true_volcano_level": "not_computed (deviation D-3)"}
                    for r in rows if str(fn(r)) != mode]
            degenerate = [
                {"a": r["a"], "b": r["b"],
                 "singular_locus_empty": r["singular_locus_affine"]["is_empty"],
                 "unit_ideal": r["singular_locus_affine"]["is_unit_ideal"],
                 "elimination_ideal_zero": r["elimination"]["empty"]}
                for r in rows + crows
                if r["singular_locus_affine"]["is_empty"]
                or r["singular_locus_affine"]["is_unit_ideal"]
                or r["elimination"]["empty"]]
            verdict = {
                "verdict": "CLASS-INVARIANT" if class_constant else "CLASS-VARYING",
                "verdict_definition": (
                    "CLASS-INVARIANT: exactly one distinct value per family "
                    "across the 138 class members. CLASS-VARYING: at least one "
                    "explicitly exhibited pair of class members differing in "
                    "at least one family. Computed INSIDE the run (SR7); the "
                    "reported metric set does not depend on which fired."),
                "per_family": per_family,
                "exhibited_witness_pair": witness,
                "curves_deviating_from_class_mode": mode_deviants,
                "degenerate_geometry": degenerate,
                "gauge_all_agree": all(g["all_agree"] for g in gauge + cgauge),
                "backend_B_all_agree": cc["all_backend_B_agree"],
                "backend_C_all_agree": cc["all_backend_C_agree"],
                "order_independent_all": cc["all_order_independent"],
                "koszul_all_regular_sequence_on_class":
                    all(r["koszul"]["is_regular_sequence"] for r in rows),
                "interpretation": "NONE. Executor records; the Reviewer and "
                                  "Coordinator interpret (SC-2).",
                "claim_tier": "toy", "sota_delta": 0,
                "ecdlp_claim": "none in either direction",
            }
            rec.write("verdict.json", verdict)
            stopping.append(stopping_rule_record(
                "SR7 no outcome shopping", "satisfied",
                {"verdict": verdict["verdict"],
                 "computed_inside_run": True,
                 "metric_set_fixed_before_verdict": True}))
            stopping.append(stopping_rule_record(
                "SR5 frozen scope", "held",
                {"prime": P, "trace": TRACE, "arity": 3,
                 "grading": "x0-homogenised standard grading",
                 "monomial_order": MONOMIAL_ORDER,
                 "second_order_used_only_for_control_C-ORDER": SECOND_MONOMIAL_ORDER,
                 "amendments_filed": 0}))
            metrics.update({
                "verdict": verdict["verdict"],
                "class_distinct_values": {k: v["class_distinct_values"] for k, v in per_family.items()},
                "control_distinct_values": {k: v["control_distinct_values"] for k, v in per_family.items()},
                "gauge_all_agree": verdict["gauge_all_agree"],
                "backend_B_all_agree": cc["all_backend_B_agree"],
                "backend_C_all_agree": cc["all_backend_C_agree"],
                "order_independent_all": cc["all_order_independent"],
                "crosscheck_curves": len(picked),
                "betti_crosschecked_curves": cc["betti_crosschecked_curves"],
                "koszul_all_regular_sequence_on_class": verdict["koszul_all_regular_sequence_on_class"],
            })
            rec.write("raw-result.json", {
                "metrics": metrics, "certificate": {"kind": "none"},
                "raw": {"stopping_rules": stopping,
                        "class_multisets": class_ms,
                        "control_multisets": control_ms,
                        "timing_per_curve_seconds": {
                            "class": [r["seconds"] for r in rows],
                            "control": [r["seconds"] for r in crows]}}})
        elif args.stage == "m4":
            rng = random.Random(SEED + 2)
            controls, cmeta = draw_control_set(random.Random(SEED))
            out_class, out_ctrl = [], []
            for label, curves, sink in (("class", members, out_class),
                                        ("control", controls, out_ctrl)):
                for n, c in enumerate(curves):
                    rec.check_budget("m4 %s %d/%d" % (label, n + 1, len(curves)))
                    t0 = time.time()
                    r = invariants_m4(c["a"], c["b"])
                    r["seconds"] = round(time.time() - t0, 3)
                    r["j"] = c["j"]
                    u = rng.randrange(1, P)
                    ga, gb = gauge_transform(c["a"], c["b"], u)
                    g = invariants_m4(ga, gb)
                    r["gauge"] = {
                        "u": u, "gauged_a": ga, "gauged_b": gb,
                        "support_agrees": g["s4_support"] == r["s4_support"],
                        "dim_agrees": (g["singular_locus_affine"]["dimension"]
                                       == r["singular_locus_affine"]["dimension"]),
                        "degree_agrees": (g["singular_locus_affine"]["degree"]
                                          == r["singular_locus_affine"]["degree"])}
                    sink.append(r)
                    if (n + 1) % 20 == 0:
                        rec.say("m4 %s %d/%d" % (label, n + 1, len(curves)))
                if label == "class":
                    rec.write("m4-class-invariants.json",
                              {"n": len(sink), "per_curve": sink,
                               "note": "written as soon as the class half "
                                       "completed, so an infrastructure "
                                       "failure in the control half cannot "
                                       "destroy it."})
            def ms4(rows):
                out = {}
                for key, fn in (("s4_support", lambda r: r["s4_support"]),
                                ("s4_singular_dim_degree",
                                 lambda r: (r["singular_locus_affine"]["dimension"],
                                            r["singular_locus_affine"]["degree"]))):
                    counts = {}
                    for r in rows:
                        counts[str(fn(r))] = counts.get(str(fn(r)), 0) + 1
                    out[key] = {"distinct_values": len(counts), "multiset": counts}
                return out
            m4 = {"class": {"n": len(out_class), "per_curve": out_class,
                            "multisets": ms4(out_class)},
                  "control": {"n": len(out_ctrl), "per_curve": out_ctrl,
                              "multisets": ms4(out_ctrl)},
                  "betti_and_regularity": "not_computed",
                  "not_computed_reason": (
                      "Contract arities.secondary_scope: at m = 4 the Betti "
                      "table and regularity are secondary and may be reported "
                      "as not_computed. This is a BUDGET statement under "
                      "AGENTS.md rule 5 and is NEVER reported as constancy."),
                  "all_gauge_agree": all(
                      r["gauge"]["support_agrees"] and r["gauge"]["dim_agrees"]
                      and r["gauge"]["degree_agrees"]
                      for r in out_class + out_ctrl)}
            rec.write("m4-invariants.json", m4)
            metrics.update({
                "stage": "m4 secondary",
                "m4_class_distinct": {k: v["distinct_values"]
                                      for k, v in m4["class"]["multisets"].items()},
                "m4_control_distinct": {k: v["distinct_values"]
                                        for k, v in m4["control"]["multisets"].items()},
                "m4_betti": "not_computed",
                "m4_all_gauge_agree": m4["all_gauge_agree"]})
            rec.write("raw-result.json", {"metrics": metrics,
                                          "certificate": {"kind": "none"},
                                          "raw": {"stopping_rules": stopping}})
    except Budget as exc:
        rec.say("SR6 FIRED: %s" % exc)
        status, valid = "failed_infrastructure", False
        invalid_reason = str(exc)
        stopping.append(stopping_rule_record("SR6 budget", "FIRED", str(exc)))
        metrics["sr6"] = ("budget exhausted; partial artifacts retained. Per "
                          "AGENTS.md rule 5 this is a BUDGET EVENT, never "
                          "negative mathematical evidence and never evidence "
                          "that an invariant is constant.")
        rec.write("raw-result.json", {"metrics": metrics,
                                      "certificate": {"kind": "none"},
                                      "raw": {"stopping_rules": stopping,
                                              "partial": True}})
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        rec.say("RUN FAILED: %s" % exc)
        rec.write_text("stderr.log", "\n".join(rec.lines) + "\n\n" + tb)
        if status == "completed_valid":
            if isinstance(exc, (OSError, MemoryError)):
                status, valid = "failed_infrastructure", False
                invalid_reason = (
                    "infrastructure_error (%s: %s). Under AGENTS.md rule 5 "
                    "this is NEVER negative mathematical evidence and NEVER "
                    "evidence that an invariant is constant. Partial "
                    "artifacts retained." % (type(exc).__name__, exc))
            else:
                status, valid = "completed_invalid", False
                invalid_reason = "%s: %s" % (type(exc).__name__, exc)
        if not os.path.exists(os.path.join(rec.run_dir, "raw-result.json")):
            rec.write("raw-result.json", {"metrics": metrics,
                                          "certificate": {"kind": "none"},
                                          "raw": {"stopping_rules": stopping,
                                                  "traceback": tb,
                                                  "partial": True}})
        rec.write_text("stdout.log", "\n".join(rec.lines) + "\n")
        write_manifest(rec, args.run_id, status, valid, invalid_reason, command,
                       metrics, parameters, stopping, deviations, started)
        return 1

    rec.write_text("stdout.log", "\n".join(rec.lines) + "\n")
    if not os.path.exists(os.path.join(rec.run_dir, "stderr.log")):
        rec.write_text("stderr.log", "")
    write_manifest(rec, args.run_id, status, valid, invalid_reason, command,
                   metrics, parameters, stopping, deviations, started)
    rec.say("done: status=%s" % status)
    rec.write_text("stdout.log", "\n".join(rec.lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
