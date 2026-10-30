"""Known-answer tests for the EXP-MONO-1a1be2 toolchain (TASK-20261029-a97206).

Rules these tests follow (card constraints IM-2, IM-3, IM-4, IM-5):
  * Cells are KAT cells disjoint from every contract cell: F_Q with q in {5, 13} at degree n <= 3, and
    prime fields (n = 1) with q not a contract (q, n) pair. No contract cell is computed.
  * Every counter test compares the optimised (kernel) counter with a naive enumeration written directly
    from the definition on the same cell. No test asserts an identity between different conventions, a
    predicted ratio, a split frequency, or any value from the specification's predictions.
  * Raw outputs are recorded: set KAT_LOG_PATH to write them (as text) to a JSON file at session end.

Run:  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider experiments/EXP-MONO-1a1be2/code/tests/test_kat.py
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import shutil
import sys
import tempfile
from collections import Counter

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, CODE)

import counters  # noqa: E402
import curves  # noqa: E402
import fqn  # noqa: E402
import launcher  # noqa: E402
import make_trial_plan as mtp  # noqa: E402
import semaev  # noqa: E402
from curves import Curve, WCurve  # noqa: E402
from fqn import FQ, FQ2  # noqa: E402

LOG: list[dict] = []


def record(kat_id: str, cell: str, output) -> None:
    LOG.append({"kat_id": kat_id, "cell": cell,
                "output_text": output if isinstance(output, str) else json.dumps(output, sort_keys=True, default=str)})


@pytest.fixture(scope="session", autouse=True)
def _write_log():
    yield
    path = os.environ.get("KAT_LOG_PATH")
    if path:
        with open(path, "w") as fh:
            json.dump({"task": "TASK-20261029-a97206", "note": "raw KAT outputs as text; KAT cells are disjoint from "
                       "every contract cell; no contract cell computed; nothing here is a run",
                       "entries": LOG}, fh, indent=1)
            fh.write("\n")


@pytest.fixture(scope="session")
def kernel():
    tmp = tempfile.mkdtemp(prefix="mono1a1be2-kat-kernel-")
    k = counters.Kernel(counters.build_kernel(tmp))
    record("K1-build", "-", {"compiler": counters.compiler_record(), "so_sha256": counters.file_sha256(k.so_path),
                             "kernel_c_sha256": counters.file_sha256(os.path.join(CODE, "kernel.c"))})
    yield k
    shutil.rmtree(tmp, ignore_errors=True)


# KAT cells. Field/curve KATs: q in {5, 13}, n <= 3, plus prime fields. None is a contract (q, n) pair.
EXT_FIELDS = [(5, 2), (5, 3), (13, 2), (13, 3)]
PRIME_FIELDS = [7, 11, 17, 19, 23, 101, 1009]
ALL_FIELDS = EXT_FIELDS + [(p, 1) for p in PRIME_FIELDS]


def fld(q, n):
    return FQ(q, n)


def kat_curve(q, n, tag):
    F = fld(q, n)
    E, info = curves.generate_curve(F, f"kat|{tag}|{q}|{n}")
    return F, E, info


def rng_for(tag):
    return curves.make_rng("kat|rng|" + tag)


def disjoint_from_contract(q, n):
    return (q, n) not in mtp.contract_cells_qn()


# =============================================================================== K: kernel / disjointness
def test_kat_cells_disjoint_from_contract():
    for q, n in ALL_FIELDS:
        assert disjoint_from_contract(q, n), (q, n)
        if n > 1:
            assert q in (5, 13) and n <= 3
    record("K0-disjoint", "-", {"kat_fields": ALL_FIELDS, "contract_pairs": sorted(mtp.contract_cells_qn())})


def test_no_binary_in_code_dir():
    found = [f for f in os.listdir(CODE) if f.endswith((".so", ".o", ".dll", ".dylib"))]
    assert not found


# =============================================================================== F: field
def brute_least_irreducible(q, n):
    """Definition: first monic degree-n polynomial (lexicographic by constant term upward) with no factor of
    degree 1..n//2, found by trial division by every monic polynomial of those degrees."""
    def polymod(a, b):  # a, b low-first, b monic
        a = list(a)
        while len(a) >= len(b):
            c = a[-1]
            if c:
                for j in range(len(b)):
                    a[len(a) - len(b) + j] = (a[len(a) - len(b) + j] - c * b[j]) % q
            a.pop()
        return a
    for c in itertools.product(range(q), repeat=n):
        g = list(c) + [1]
        ok = True
        for d in range(1, n // 2 + 1):
            for h in itertools.product(range(q), repeat=d):
                if not any(polymod(g, list(h) + [1])):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return tuple(c)


@pytest.mark.parametrize("q,n", EXT_FIELDS)
def test_least_irreducible_matches_definition(q, n):
    got = fqn.least_irreducible(q, n)
    want = brute_least_irreducible(q, n)
    assert got == want
    record("F1-least-irreducible", f"q={q},n={n}", {"g": got})


@pytest.mark.parametrize("q,n", ALL_FIELDS)
def test_field_arithmetic(q, n, kernel):
    F = fld(q, n)
    rng = rng_for(f"field{q}{n}")
    els = [F.random_element(rng) for _ in range(40)]
    squares = {F.mul(e, e) for e in F.elements()} if F.Q <= 2197 else None
    for a, b, c in zip(els, els[1:], els[2:]):
        assert F.mul(a, F.mul(b, c)) == F.mul(F.mul(a, b), c)
        assert F.mul(a, F.add(b, c)) == F.add(F.mul(a, b), F.mul(a, c))
        assert F.mul(a, b) == F.mul(b, a)
        assert F.pow(a, 5) == F.mul(F.mul(F.mul(F.mul(a, a), a), a), a)
        assert F.frobenius(a) == F.pow(a, q)
        if not F.is_zero(a):
            assert F.inv(a) == F.inv_fermat(a)
            assert F.mul(a, F.inv(a)) == F.one
            assert F.pow(a, F.Q - 1) == F.one
        r = F.sqrt(F.mul(a, a))
        assert r is not None and F.mul(r, r) == F.mul(a, a)
        if squares is not None:
            assert (F.chi(a) >= 0) == (a in squares)
    if squares is not None:
        # chi from definition: +1 for nonzero squares
        for e in F.elements():
            want = 0 if F.is_zero(e) else (1 if e in squares else -1)
            assert F.chi(e) == want
    record("F2-field-arithmetic", f"q={q},n={n}", {"checked_elements": len(els), "g": F.g})


@pytest.mark.parametrize("q,n", ALL_FIELDS)
def test_kernel_field_ops_match_python(q, n, kernel):
    F, E, _ = kat_curve(q, n, "kfield")
    rng = rng_for(f"kfield{q}{n}")
    for _ in range(60):
        a, b = F.random_element(rng), F.random_element(rng)
        assert kernel.mul(E, a, b) == F.mul(a, b)
        if not F.is_zero(a):
            assert kernel.inv(E, a) == F.inv(a)
            assert kernel.inv(E, a, ref=True) == F.inv(a)
    record("F3-kernel-field", f"q={q},n={n}", {"pairs": 60})


@pytest.mark.parametrize("q,n", ALL_FIELDS)
def test_quadratic_extension(q, n):
    F = fld(q, n)
    F2 = FQ2(F)
    rng = rng_for(f"f2{q}{n}")
    assert F.chi(F2.d) == -1
    for _ in range(30):
        a = (F.random_element(rng), F.random_element(rng))
        b = (F.random_element(rng), F.random_element(rng))
        assert F2.mul(a, b) == F2.mul(b, a)
        if not F2.is_zero(a):
            assert F2.mul(a, F2.inv(a)) == F2.one
        y2 = F.random_element(rng)
        y = F2.lift_y(y2)
        assert F2.mul(y, y) == F2.embed(y2)


# =============================================================================== C: seeds, curves, counting
def test_seed_rule():
    for s in ["f15270|A|2|61|0", "f15270|C|7|23|2", "f15270|base|A-n2-q61-c0|random|0"]:
        digest = hashlib.sha256(s.encode("utf-8")).digest()
        want = int.from_bytes(digest[:16], "big")
        assert curves.seed_int(s) == want
        g1 = curves.make_rng(s)
        g2 = np.random.Generator(np.random.PCG64(want))
        assert g1.integers(0, 10 ** 9, size=8).tolist() == g2.integers(0, 10 ** 9, size=8).tolist()
        assert curves.make_rng(s).integers(0, 97, size=5).tolist() == curves.make_rng(s).integers(0, 97, size=5).tolist()
    record("C1-seed-rule", "-", {s: str(curves.seed_int(s)) for s in ["f15270|A|2|61|0", "f15270|C|7|23|2"]})


def test_plan_seed_strings():
    assert mtp.curve_seed("A", 2, 61, 0) == "f15270|A|2|61|0"
    assert mtp.base_seed("A-n2-q61-c0", "twin", 1) == "f15270|base|A-n2-q61-c0|twin|1"
    assert mtp.tuple_seed("B1-n2-q251-c0", 0) == "f15270|tuples|B1-n2-q251-c0|0"
    assert mtp.target_seed("C-n2-q32771-c0") == "f15270|targets|C-n2-q32771-c0"


@pytest.mark.parametrize("q,n", EXT_FIELDS)
def test_curve_selection_rules(q, n):
    F = fld(q, n)
    # explicit rejects
    zero = F.zero
    one = F.one
    assert Curve(F, zero, one).j_in_Fq()                       # a = 0: j = 0
    assert Curve(F, one, zero).j_in_Fq()                       # b = 0: j = 1728
    sing = Curve(F, F.neg(F.from_int(3)), F.from_int(2))       # x^3 - 3x + 2 = (x-1)^2 (x+2)
    assert sing.is_singular()
    for i in range(30):
        E, info = curves.generate_curve(F, f"kat|sel|{q}|{n}|{i}")
        assert not E.is_singular() and not E.j_in_Fq()
        # j in F_q iff j^q = j (independent test)
        j = E.j_invariant()
        assert F.pow(j, q) != j
    # a generated sequence includes at least one rejected attempt across seeds is not asserted (data dependent)


@pytest.mark.parametrize("p", PRIME_FIELDS)
def test_curve_selection_prime_fields(p):
    F = fld(p, 1)
    for i in range(10):
        E, info = curves.generate_curve(F, f"kat|selp|{p}|{i}")
        assert not E.is_singular()
        assert E.j_in_Fq()          # vacuous at n = 1: documented, only singular rejected


@pytest.mark.parametrize("q,n", EXT_FIELDS)
def test_group_law(q, n):
    F, E, _ = kat_curve(q, n, "grp")
    rng = rng_for(f"grp{q}{n}")
    pts = []
    while len(pts) < 12:
        x = F.random_element(rng)
        P = E.lift(x)
        if P is not None:
            pts.append(P)
    for P in pts:
        assert E.on_curve(P)
        assert E.add(P, E.neg(P)) is None
        assert E.add(P, None) == P
    for P, R, S in zip(pts, pts[1:], pts[2:]):
        assert E.on_curve(E.add(P, R))
        assert E.add(P, R) == E.add(R, P)
        assert E.add(E.add(P, R), S) == E.add(P, E.add(R, S))
        assert E.mul(5, P) == E.add(E.add(E.add(E.add(P, P), P), P), P)
    N = E.count_points_naive()
    for P in pts[:4]:
        assert E.mul(N, P) is None            # Lagrange: N P = O


def naive_points(E):
    """All affine points by the definition (x, y) with y^2 = f(x), plus nothing else."""
    F = E.F
    out = []
    for x in F.elements():
        fx = E.f(x)
        for y in F.elements():
            if F.mul(y, y) == fx:
                out.append((x, y))
    return out


@pytest.mark.parametrize("q,n", [(5, 2), (5, 3), (13, 2), (7, 1), (11, 1), (23, 1)])
def test_point_counting_all_methods_and_definition(q, n, kernel):
    for i in range(3):
        F, E, _ = kat_curve(q, n, f"cnt{i}")
        pts = naive_points(E)                                   # Q^2 pairs from the definition
        N_def = len(pts) + 1
        assert E.count_points_naive() == N_def
        assert E.count_points_chi() == N_def
        assert kernel.count_points(E) == N_def
        assert E.count_points_bsgs()[0] == N_def
        assert abs(N_def - (F.Q + 1)) <= 2 * math.isqrt(F.Q) + 2
        Nk, mask = kernel.valid_mask(E)
        assert Nk == N_def and int(np.count_nonzero(mask & 1)) == N_def
        # target index: kernel equals the Python formula on every point
        assert kernel.point_index(E, None) == counters.target_index(F, None) == 2 * F.Q
        idxs = set()
        for P in pts[:200]:
            ki = kernel.point_index(E, P)
            assert ki == counters.target_index(F, P)
            assert mask[ki] & 1
            idxs.add(ki)
        record("C3-point-count", f"q={q},n={n},curve={i}", {"a": E.a, "b": E.b, "N": N_def})


def _twenty_random_curves():
    """20 curves with Q < 2^27 outside the contract cells: 8 prime fields and 12 over q in {5, 13}, n in {2, 3}."""
    cells = []
    for p in [1009, 10007, 65537, 100003, 1000003, 4000037, 16000057, 100000007]:
        cells.append((fqn.next_prime_above(p - 1), 1))
    for q, n in EXT_FIELDS:
        cells += [(q, n)] * 3
    return cells


def test_point_counting_twenty_random_curves_exhaustive_vs_bsgs(kernel):
    cells = _twenty_random_curves()
    assert len(cells) == 20
    rows = []
    for k, (q, n) in enumerate(cells):
        F = fld(q, n)
        assert F.Q < 2 ** 27 and disjoint_from_contract(q, n)
        E, _ = curves.generate_curve(F, f"kat|twenty|{k}|{q}|{n}")
        N_exh = kernel.count_points(E)
        N_bsgs, used = E.count_points_bsgs()
        assert N_exh == N_bsgs
        rows.append({"q": q, "n": n, "a": E.a, "b": E.b, "N_exhaustive": N_exh, "N_bsgs": N_bsgs, "bsgs_point_pairs": used})
    record("C4-twenty-random-curves", "Q<2^27 outside contract", rows)


def test_bsgs_beyond_exhaustive_range_agrees_with_independent_count(kernel):
    """A prime field above 2^27 (not a contract cell): BSGS against the quadratic-character sum done in the
    compiled kernel through the exhaustive routine is too slow in Python, so cross-check with the group
    order property instead: the BSGS value N satisfies N P = O for random P and lies in the Hasse interval."""
    p = fqn.next_prime_above(2 ** 28)
    F = fld(p, 1)
    E, _ = curves.generate_curve(F, "kat|bigp")
    N, used = E.count_points_bsgs()
    rng = rng_for("bigp")
    assert abs(N - (p + 1)) <= 2 * math.isqrt(p) + 1
    k = 0
    while k < 5:
        P = E.lift(F.random_element(rng))
        if P is not None:
            assert E.mul(N, P) is None
            k += 1
    # and the exhaustive routine (kernel) agrees; p ~ 2.7e8 is a few seconds of C
    assert kernel.count_points(E) == N
    record("C5-bsgs-above-2^27", f"p={p}", {"N": N, "point_pairs": used})


@pytest.mark.parametrize("q,n", [(5, 2), (13, 2), (5, 3), (13, 3), (11, 1), (23, 1)])
def test_factor_base_and_torsion_from_definition(q, n):
    F, E, _ = kat_curve(q, n, "fb")
    pts = naive_points(E) if F.Q <= 2197 else None
    D, X, t2 = E.factor_base()
    if pts is None:
        pts = []
        for xv in range(q):
            x = F.from_int(xv)
            for y in F.elements():
                if F.mul(y, y) == E.f(x):
                    pts.append((x, y))
    line = [P for P in pts if F.is_scalar(P[0])]
    assert sorted(D) == sorted(line)
    assert len(D) == len(line)
    assert t2 == sum(1 for P in line if F.is_zero(P[1]))
    assert sorted(X) == sorted({P[0] for P in line})
    # two-torsion over F_Q from the definition
    roots = sorted((x for x in F.elements() if F.is_zero(E.f(x))), key=F.to_code)
    assert E.two_torsion_roots() == roots
    assert len(D) == t2 + 2 * (len(X) - t2)
    record("C6-factor-base", f"q={q},n={n}", {"B": len(D), "t2": t2, "size_X": len(X), "r2": len(roots)})


# =============================================================================== P: polynomials, S_{n+1}
def test_polynomial_tools():
    F = fld(13, 2)
    rng = rng_for("poly")
    # f = (x - r1)(x - r2)(x^2 + c)(irreducible quadratic) with known factors
    rts = [F.from_code(5), F.from_code(77), F.from_code(100)]
    f = [F.one]
    for r in rts:
        f = fqn.pmul(F, f, [F.neg(r), F.one])
    assert fqn.roots(F, f) == sorted(rts, key=F.to_code)
    # an irreducible quadratic over F_{13^2}: x^2 - nonsquare-of-F_Q-in-the-quadratic-sense: x^2 - d with d nonsquare
    d = F.nonsquare()
    irr = [F.neg(d), F.zero, F.one]
    g = fqn.pmul(F, f, irr)
    assert fqn.is_squarefree(F, g)
    fac = fqn.ddf(F, g)
    assert [(dd, len(h) - 1) for dd, h in fac] == [(1, 3), (2, 2)]
    assert not fqn.splits_completely_ddf(F, g) and not fqn.splits_completely_xq(F, g)
    assert fqn.splits_completely_ddf(F, f) and fqn.splits_completely_xq(F, f)
    assert fqn.roots(F, g) == sorted(rts, key=F.to_code)
    assert not fqn.is_squarefree(F, fqn.pmul(F, g, [F.neg(rts[0]), F.one]))
    # roots by brute force on random polynomials
    for _ in range(10):
        poly = [F.random_element(rng) for _ in range(5)]
        fqn.ptrim(F, poly)
        if len(poly) < 2:
            continue
        brute = sorted((x for x in F.elements() if F.is_zero(fqn.peval(F, poly, x))), key=F.to_code)
        assert fqn.roots(F, poly) == brute
    record("P1-polynomial-tools", "F_{13^2}", {"known_factorisation": "3 linear + 1 irreducible quadratic"})


def _random_points(F, E, rng, k):
    pts = []
    while len(pts) < k:
        P = E.lift(F.random_element(rng))
        if P is None or F.is_zero(P[1]):
            continue
        if rng.integers(0, 2):
            P = E.neg(P)
        pts.append(P)
    return pts


SEMAEV_FIELDS = [(13, 2), (5, 3), (13, 3), (101, 1), (1009, 1)]


SEMAEV_CASES = [(q, n, L) for (q, n) in SEMAEV_FIELDS for L in (2, 3, 4, 5) if not ((q, n) == (13, 3) and L >= 4)]


@pytest.mark.parametrize("q,n,tuple_len", SEMAEV_CASES)
def test_semaev_defining_property_200_tuples(q, n, tuple_len):
    """S_{k+1}(x(P_1), ..., x(P_k), x(P_1 + ... + P_k)) = 0 for 200 random point tuples (sum != O).
    (13, 3) is run for tuple lengths 2 and 3 only; lengths 4 and 5 are covered by the other fields."""
    F, E, _ = kat_curve(q, n, "sem")
    assert F.Q >= 2 ** tuple_len + 2           # enough points to interpolate
    rng = rng_for(f"semdp{q}{n}{tuple_len}")
    done = 0
    while done < 200:
        P = _random_points(F, E, rng, tuple_len)
        S = None
        for R in P:
            S = E.add(S, R)
        if S is None:
            continue
        xs = [R[0] for R in P]
        val = semaev.semaev_eval(F, E.a, E.b, xs, S[0])
        assert F.is_zero(val), (q, n, tuple_len)
        done += 1
    record("S1-defining-property", f"q={q},n={n},tuple_len={tuple_len}", {"tuples": done})


@pytest.mark.parametrize("q,n", [(13, 2), (5, 3), (101, 1)])
@pytest.mark.parametrize("tuple_len", [2, 3, 4, 5])
def test_semaev_roots_agree_with_group_law_signed_sums(q, n, tuple_len):
    F, E, _ = kat_curve(q, n, "sem2")
    assert F.Q >= 2 ** tuple_len + 2
    rng = rng_for(f"semgl{q}{n}{tuple_len}")
    F2 = FQ2(F)
    k = 0
    agree = 0
    while k < 200:
        xs = [F.random_element(rng) for _ in range(tuple_len)]
        if any(F.is_zero(E.f(x)) for x in xs):
            continue
        res = semaev.analyse_fibre(F, E, xs)
        roots_gl, ninf = semaev.roots_via_group_law(F, E, xs, F2)
        if res["squarefree"] and res["full_degree"]:
            assert res["roots_Fq"] == roots_gl, (xs,)
            agree += 1
            # the two completeness tests agree
            assert res["split_completely"] == res["split_check_xq"]
            # number of distinct x of the signed sums over F_{Q^2} equals the degree for generic tuples
        k += 1
    record("S2-roots-vs-group-law", f"q={q},n={n},tuple_len={tuple_len}", {"tuples": k, "generic_compared": agree})


def test_semaev_s3_matches_definition_and_known_answer():
    """S_3 as a polynomial identity: vanishes on x-triples of points summing to O, checked exhaustively on a
    small curve; and the n = 2 resultant recursion is S_3 itself (formal degree 2)."""
    F, E, _ = kat_curve(13, 2, "s3")
    D, X, t2 = E.factor_base()
    pts = naive_points(E)
    zero_triples = set()
    for P in pts[:40]:
        for R in pts[:40]:
            S = E.add(P, R)
            if S is None:
                continue
            T = E.neg(S)
            assert F.is_zero(semaev.s3_eval(F, E.a, E.b, P[0], R[0], T[0]))
            zero_triples.add((P[0], R[0], T[0]))
    # converse on a sample: if S_3(x1,x2,x3)=0 then some sign choice sums to O (exhaustive over x3 for fixed x1,x2)
    x1, x2 = pts[3][0], pts[7][0]
    P1, P2 = E.lift(x1), E.lift(x2)
    sums = set()
    for s1, s2 in itertools.product((1, -1), repeat=2):
        S = E.add(P1 if s1 == 1 else E.neg(P1), P2 if s2 == 1 else E.neg(P2))
        if S is not None:
            sums.add(S[0])
    roots = {x3 for x3 in F.elements() if F.is_zero(semaev.s3_eval(F, E.a, E.b, x1, x2, x3))}
    assert roots == sums
    poly = semaev.semaev_poly(F, E.a, E.b, [x1, x2])
    assert poly == semaev.s3_quad(F, E.a, E.b, x1, x2)
    record("S3-s3-definition", "q=13,n=2", {"x1": x1, "x2": x2, "roots": sorted(F.to_code(r) for r in roots)})


def test_semaev_recursion_matches_nested_definition():
    """S_4 two ways over a small field: the interpolating recursion against the resultant of S_3(x1,x2,X) and
    S_3(X,x3,T) computed by an independent Sylvester determinant over F_Q[T] evaluated at every T."""
    F, E, _ = kat_curve(13, 2, "s4")
    rng = rng_for("s4")

    def sylvester_res(A, B):
        """Resultant of A, B (low-first coefficient lists with formal degrees len-1) by determinant."""
        m, n = len(A) - 1, len(B) - 1
        size = m + n
        M = [[F.zero] * size for _ in range(size)]
        for i in range(n):
            for j, c in enumerate(reversed(A)):
                M[i][i + j] = c
        for i in range(m):
            for j, c in enumerate(reversed(B)):
                M[n + i][i + j] = c
        det = F.one
        for col in range(size):
            piv = next((r for r in range(col, size) if not F.is_zero(M[r][col])), None)
            if piv is None:
                return F.zero
            if piv != col:
                M[col], M[piv] = M[piv], M[col]
                det = F.neg(det)
            det = F.mul(det, M[col][col])
            inv = F.inv(M[col][col])
            for r in range(col + 1, size):
                if not F.is_zero(M[r][col]):
                    f = F.mul(M[r][col], inv)
                    for c in range(col, size):
                        M[r][c] = F.sub(M[r][c], F.mul(f, M[col][c]))
        return det

    for _ in range(6):
        x1, x2, x3 = (F.random_element(rng) for _ in range(3))
        poly = semaev.semaev_poly(F, E.a, E.b, [x1, x2, x3])        # S_4(x1,x2,x3,T)
        A = semaev.s3_quad(F, E.a, E.b, x1, x2)                      # S_3(x1,x2,X) in X
        for T in [F.from_code(c) for c in range(0, 40, 3)]:
            Bq = semaev.s3_quad(F, E.a, E.b, x3, T)                  # S_3(x3,T,X) in X (symmetric)
            assert sylvester_res(A, Bq) == fqn.peval(F, poly, T)
    record("S4-recursion-vs-sylvester", "q=13,n=2", {"tuples": 6, "T_points_each": 14})


# =============================================================================== E: counters vs naive
def pt_sum(E, pts):
    S = None
    for P in pts:
        S = E.add(S, P)
    return S


def naive_TA(E, D, m):
    c = Counter()
    for tup in itertools.product(D, repeat=m):
        c[counters.target_index(E.F, pt_sum(E, tup))] += 1
    return c


def naive_TM(E, D, m):
    c = Counter()
    for tup in itertools.combinations_with_replacement(D, m):
        c[counters.target_index(E.F, pt_sum(E, tup))] += 1
    return c


def naive_TS(E, lifts, m):
    c = Counter()
    for xt in itertools.product(lifts, repeat=m):
        for eps in itertools.product((1, -1), repeat=m):
            pts = [P if e == 1 else E.neg(P) for P, e in zip(xt, eps)]
            c[counters.target_index(E.F, pt_sum(E, pts))] += 1
    return c


def naive_TX_TMre(E, D, m):
    """x-multisets over the distinct x of D; for each, all distinct point multisets over it (each x
    contributes any of the points of D with that x); c(R) = number of those multisets with sum R."""
    F = E.F
    by_x = {}
    for P in D:
        by_x.setdefault(P[0], []).append(P)
    xs = sorted(by_x, key=F.to_code)
    TX, TMre = Counter(), Counter()
    for xm in itertools.combinations_with_replacement(xs, m):
        choices = [by_x[x] for x in xm]
        multisets = {tuple(sorted(c, key=lambda P: (F.to_code(P[0]), F.to_code(P[1]))))
                     for c in itertools.product(*choices)}
        cR = Counter(counters.target_index(F, pt_sum(E, ms)) for ms in multisets)
        for R, c in cR.items():
            TX[R] += 1
            TMre[R] += c
    return TX, TMre


def arr_to_counter(arr):
    nz = np.nonzero(arr)[0]
    return Counter({int(i): int(arr[i]) for i in nz})


def naive_S_and_masks(E, D, m, N):
    F = E.F
    S = set()
    for mp in range(m - 2, -1, -2):
        for ms in itertools.combinations_with_replacement(D, mp):
            S.add(counters.target_index(F, pt_sum(E, ms)))
    return S


EXH_CELLS = [  # (q, n, m): KAT cells only
    (13, 2, 2), (13, 2, 3), (5, 2, 4), (5, 3, 2), (5, 3, 3), (13, 3, 2), (13, 3, 3), (7, 1, 4), (11, 1, 3), (7, 1, 5),
]


@pytest.mark.parametrize("q,n,m", EXH_CELLS)
@pytest.mark.parametrize("base_kind", ["line", "random", "twin"])
def test_exhaustive_counters_match_naive_enumeration(q, n, m, base_kind, kernel):
    F, E, _ = kat_curve(q, n, "exh")
    N, vmask = kernel.valid_mask(E)
    D, X, t2 = E.factor_base()
    rng = rng_for(f"exh{q}{n}{m}{base_kind}")
    if base_kind == "random":
        base = counters.matched_random_base(E, len(D), t2, rng)
    elif base_kind == "twin":
        base = counters.twin_base(E, len(D), t2, rng)
    else:
        base = D
    lifts = counters.x_lifts(F, base)
    res = counters.exhaustive_cell(kernel, E, base, lifts, m, N, vmask, recount=True, keep=True)
    arr = res["arrays"]
    assert arr_to_counter(arr["A"]) == naive_TA(E, base, m)
    assert arr_to_counter(arr["M"]) == naive_TM(E, base, m)
    assert arr_to_counter(arr["S"]) == naive_TS(E, lifts, m)
    TXn, TMren = naive_TX_TMre(E, base, m)
    assert arr_to_counter(arr["X"]) == TXn
    assert arr_to_counter(arr["Mre"]) == TMren
    # the weighted helper arrays equal their own naive definitions
    cw = Counter()
    for tup in itertools.product(base, repeat=m):
        j = sum(1 for P in tup if F.is_zero(P[1]))
        cw[counters.target_index(F, pt_sum(E, tup))] += 2 ** j
    assert arr_to_counter(arr["A2"]) == cw
    cm = Counter()
    for tup in itertools.combinations_with_replacement(range(len(base)), m):
        w = math.factorial(m)
        for _, grp in itertools.groupby(tup):
            w //= math.factorial(len(list(grp)))
        cm[counters.target_index(F, pt_sum(E, [base[i] for i in tup]))] += w
    assert arr_to_counter(arr["MW"]) == cm
    # S set, special targets, generic targets against the definition
    Sset = naive_S_and_masks(E, base, m, N)
    assert res["S_size"] == len(Sset)
    mask = res["mask"]
    special = {i for i in range(len(mask)) if (mask[i] & 3) == 3}
    two_tors = {counters.target_index(F, (r, F.zero)) for r in E.two_torsion_roots()} | {2 * F.Q}
    assert special == two_tors
    n_generic = int(N - len(two_tors | Sset))
    assert res["generic_targets"] == n_generic
    # generic histogram of T_M from the naive counter
    nm = naive_TM(E, base, m)
    hist_gen = Counter()
    for i in range(len(mask)):
        if (mask[i] & 7) == 1:
            hist_gen[nm.get(i, 0)] += 1
    assert {int(k): v for k, v in res["conventions"]["M"]["hist_gen"].items()} == dict(hist_gen)
    # recount agrees with the primary pass in every convention (self-consistency of two code paths)
    for key, ent in res["recount"].items():
        assert ent["differ"] == 0 and ent.get("differ_second", 0) == 0, key
    # raw output (no cross-convention quantity is recorded)
    raw = {c: {"hist_all": res["conventions"][c]["hist_all"], "hist_gen": res["conventions"][c]["hist_gen"]}
           for c in ("A", "M", "S", "X")}
    if (q, n) in [(5, 2), (5, 3), (13, 2), (13, 3)]:
        record("E1-exhaustive-vs-naive", f"q={q},n={n},m={m},base={base_kind}",
               {"B": len(base), "t2": res["t2"], "N": N, "size_X": len(lifts), "S_size": res["S_size"],
                "generic_targets": res["generic_targets"], "raw_histograms": raw, "recount": res["recount"]})
    else:
        record("E1-exhaustive-vs-naive", f"q={q},n={n},m={m},base={base_kind}",
               {"B": len(base), "N": N, "recount": res["recount"]})


def test_ncf_coefficient_function_matches_series_expansion():
    """The function that evaluates the generating-function coefficient, against an independent expansion
    (each +- pair contributes 1 + 2z + 2z^2 + ..., each 2-torsion point 1 + z). Arithmetic of the formula
    only: no comparison with any enumerated count."""
    def series(B, t2, m):
        poly = [1] + [0] * m
        for _ in range((B - t2) // 2):
            new = [0] * (m + 1)
            for i, c in enumerate(poly):
                for j in range(m + 1 - i):
                    new[i + j] += c * (1 if j == 0 else 2)
            poly = new
        for _ in range(t2):
            new = poly[:]
            for i in range(m):
                new[i + 1] += poly[i]
            poly = new
        return poly[m]
    for B, t2 in [(6, 0), (7, 1), (10, 2), (13, 3), (24, 0)]:
        if (B - t2) % 2:
            continue
        for m in range(0, 6):
            assert counters.ncf_coefficient(B, t2, m) == series(B, t2, m)


# =============================================================================== A: arm C counter vs naive
ARMC_CELLS = [(13, 2, 2), (13, 2, 3), (5, 2, 4), (5, 3, 3), (13, 3, 2), (101, 1, 2), (103, 1, 2)]


@pytest.mark.parametrize("q,n,m", ARMC_CELLS)
@pytest.mark.parametrize("base_kind", ["line", "random"])
def test_sampled_counter_matches_naive_enumeration(q, n, m, base_kind, kernel):
    F, E, _ = kat_curve(q, n, "armc")
    N, _ = kernel.valid_mask(E)
    D, X, t2 = E.factor_base()
    rng = rng_for(f"armc{q}{n}{m}{base_kind}")
    base = D if base_kind == "line" else counters.matched_random_base(E, len(D), t2, rng)
    Sx0 = {i >> 1 for i in naive_S_and_masks(E, base, m, N) if i != 2 * F.Q}
    eligible = sum(1 for x in F.elements() if F.chi(E.f(x)) == 1 and F.to_code(x) not in Sx0)
    assert eligible >= 2, "KAT cell has fewer than two eligible generic classes"
    s = max(min(30, eligible // 2), 1)
    tr = curves.make_rng(f"kat|targets|{q}|{n}|{m}|{base_kind}")
    r = counters.arm_c_cell(kernel, E, base, m, s, tr, N)
    Sset = naive_S_and_masks(E, base, m, N)
    keys = [int(k) for k in r["keys"]]
    # sampled targets: distinct classes, chi = +1, not in S, uniform-rule structure
    assert len(keys) == s == len(set(k >> 1 for k in keys))
    Sx = {i >> 1 for i in Sset if i != 2 * F.Q}
    for k in keys:
        x = F.from_code(k >> 1)
        assert F.chi(E.f(x)) == 1 and (k >> 1) not in Sx
    cnt = Counter()
    ncf = mS = 0
    for ms in itertools.combinations_with_replacement(base, m):
        idx = counters.target_index(F, pt_sum(E, ms))
        cnt[idx] += 1
        cf = True
        for P in ms:
            if ms.count((P[0], F.neg(P[1]))) > 0 and not F.is_zero(P[1]):
                cf = False
            if F.is_zero(P[1]) and ms.count(P) >= 2:
                cf = False
        if cf:
            ncf += 1
            if idx in Sset:
                mS += 1
    assert [cnt.get(k, 0) for k in keys] == [int(c) for c in r["sampled_counts"]]
    sorted_S = sorted(Sset)
    assert [cnt.get(k, 0) for k in sorted_S] == [int(c) for c in r["S_counts"]]
    assert r["S_size"] == len(Sset)
    assert r["cancellation_free"] == ncf and r["m_S"] == mS
    assert r["multisets"] == math.comb(len(base) + m - 1, m)
    # determinism
    r2 = counters.arm_c_cell(kernel, E, base, m, s, curves.make_rng(f"kat|targets|{q}|{n}|{m}|{base_kind}"), N)
    assert [int(k) for k in r2["keys"]] == keys
    record("A1-sampled-vs-naive", f"q={q},n={n},m={m},base={base_kind}",
           {"B": len(base), "N": N, "s": s, "sampled_counts": [int(c) for c in r["sampled_counts"]],
            "S_counts": [int(c) for c in r["S_counts"]], "cancellation_free": ncf, "m_S": mS})


def test_poisson_helpers_against_independent_computation():
    rng = np.random.default_rng(12345)
    counts = rng.poisson(0.4, size=500)
    lam = 0.4
    summ = counters.poisson_summary(counts, lam)
    # independent: pmf by exp/factorial, cdf cumulative sums
    pm = [math.exp(-lam) * lam ** k / math.factorial(k) for k in range(int(counts.max()) + 1)]
    cdf = np.cumsum(pm)
    emp = np.cumsum([int((counts == k).sum()) for k in range(int(counts.max()) + 1)]) / counts.size
    assert max(abs(emp - cdf)) == pytest.approx(summ["ks_stat"], abs=1e-12)
    assert summ["zero_fraction"] == pytest.approx(float((counts == 0).mean()))
    assert summ["dispersion_index"] == pytest.approx(float(counts.var(ddof=1) / counts.mean()))
    tail = 1 - sum(pm[: int(counts.max())])
    assert counters.poisson_upper_tail(lam, int(counts.max())) == pytest.approx(tail, rel=1e-6)
    pmax = 1 - (1 - tail) ** counts.size
    assert summ["p_max_pred"] == pytest.approx(pmax, rel=1e-6)
    assert summ["max_count"] == int(counts.max()) and sum(summ["hist"].values()) == counts.size


def test_poisson_chi2_known_answer_when_counts_equal_expectation():
    lam, s = 1.0, 200000
    pm = [math.exp(-lam) * lam ** k / math.factorial(k) for k in range(12)]
    counts = np.concatenate([np.full(int(round(s * p)), k) for k, p in enumerate(pm)])
    summ = counters.poisson_summary(counts, lam)
    assert summ["chi2_stat"] < 1.0 and summ["chi2_df"] >= 5
    assert summ["ks_stat"] < 1e-3


# =============================================================================== B: bases and samplers
@pytest.mark.parametrize("q,n", EXT_FIELDS)
def test_random_and_twin_bases_structure(q, n):
    F, E, _ = kat_curve(q, n, "bases")
    D, X, t2 = E.factor_base()
    B = len(D)
    roots = set(E.two_torsion_roots())
    for kind in ("random", "twin"):
        rng = curves.make_rng(f"kat|base|{q}|{n}|{kind}")
        base = (counters.matched_random_base(E, B, t2, rng) if kind == "random"
                else counters.twin_base(E, B, t2, rng))
        again = (counters.matched_random_base(E, B, t2, curves.make_rng(f"kat|base|{q}|{n}|{kind}")) if kind == "random"
                 else counters.twin_base(E, B, t2, curves.make_rng(f"kat|base|{q}|{n}|{kind}")))
        assert base == again                                          # deterministic by seed
        assert all(E.on_curve(P) for P in base) and len(set(base)) == len(base)
        assert set(E.neg(P) for P in base) == set(base)               # symmetric
        tors = [P for P in base if F.is_zero(P[1])]
        assert len(tors) == t2 and all(P[0] in roots for P in tors)   # t2 matched, from E(F_Q)[2]
        pairs = (B - t2) // 2 if kind == "random" else -(-(B - t2) // 4)
        assert len(base) == t2 + 2 * pairs
        assert len({P[0] for P in base if not F.is_zero(P[1])}) == pairs   # distinct classes


def test_target_sampler_chi_and_uniform_rule(kernel):
    F, E, _ = kat_curve(13, 2, "tsamp")
    rng = curves.make_rng("kat|targets|sampler")
    keys, draws = counters.sample_targets(kernel, E, 25, rng, set())
    assert len(set(k >> 1 for k in keys.tolist())) == 25
    for k in keys.tolist():
        x = F.from_code(k >> 1)
        assert F.chi(E.f(x)) == 1 and (k & 1) in (0, 1)
    # kernel chi equals Python chi on random x
    rr = rng_for("chi")
    xs = rr.integers(0, 13, size=(200, 2))
    kc = kernel.chi_batch(E, xs).tolist()
    assert kc == [F.chi(E.f(tuple(int(v) for v in row))) for row in xs]
    for (qq, nn) in [(5, 3), (13, 3), (101, 1)]:
        F3, E3, _ = kat_curve(qq, nn, "chi3")
        xs = rr.integers(0, qq, size=(200, nn))
        assert kernel.chi_batch(E3, xs).tolist() == [F3.chi(E3.f(tuple(int(v) for v in row))) for row in xs]


# =============================================================================== T: trial plan rules
def _sieve_least_prime(n):
    limit = 2 ** 20
    sieve = bytearray([1]) * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    for p in range(4, limit + 1):
        if sieve[p] and p ** n >= 2 ** 30:
            return p


def test_q_rule_against_sieve_and_report_against_expected_list():
    got = {n: mtp.q_rule(n) for n in range(2, 8)}
    assert got == {n: _sieve_least_prime(n) for n in range(2, 8)}
    record("T1-q-rule", "n=2..7", {"generated": got, "specification_list": mtp.EXPECTED_QN,
                                   "agrees_with_specification_list": got == mtp.EXPECTED_QN})


def test_sample_size_rule_against_float_formula():
    got = {n: mtp.sample_size_rule(n) for n in range(2, 8)}
    for n in range(2, 8):
        lam = 1 / math.factorial(n)
        c = -math.expm1(-lam)
        val = math.exp(-lam) / (c * 0.03 ** 2)
        assert abs(got[n] - val) <= 1.0
        assert got[n] == math.ceil(val) or abs(val - round(val)) < 1e-6
    record("T2-sample-size-rule", "n=2..7", {"generated": got})


class _StubBuilder:
    def __init__(self):
        self.calls = []

    def get(self, arm, n, q, i):
        self.calls.append((arm, n, q, i))
        return {"q": q, "n": n, "stub": True, "curve_seed": {"seed_string": mtp.curve_seed(arm, n, q, i), "seed_int": "0"},
                "B": 2 * n + 1}


def test_trial_plan_enumeration_and_seed_derivation():
    sb = _StubBuilder()
    plan = mtp.build_plan(None, builder=sb)
    assert plan["cell_counts"] == {"A": 54, "B1": 12, "B2": 12, "C": 18}
    ids = [c["cell_id"] for c in plan["cells"]]
    assert len(ids) == len(set(ids)) == 96
    for c in plan["cells"]:
        if c["arm"] == "A":
            assert c["base_roles"]["matched_random"]["seed_string"] == f"f15270|base|{c['cell_id']}|random|0"
            assert c["base_roles"]["half_twin"]["seed_string"] == f"f15270|base|{c['cell_id']}|twin|0"
        if c["arm"] in ("B1", "B2"):
            assert c["tuple_seed"]["seed_string"] == f"f15270|tuples|{c['cell_id']}|0"
        if c["arm"] == "C":
            assert c["target_seed"]["seed_string"] == f"f15270|targets|{c['cell_id']}"
    # arm B reuses the arm-A curves of the same (n, q)
    assert {arm for (arm, _, _, _) in sb.calls} == {"A", "C"}          # arm B instances use arm-A seed strings
    b_calls = {(n, q, i) for (arm, n, q, i) in sb.calls if arm == "A"}
    for n in (2, 3, 4, 5):
        for q in (mtp.ARM_A_LADDER[n][0], mtp.ARM_A_LADDER[n][1]):
            for i in range(3):
                assert (n, q, i) in b_calls
    a_cells = [c for c in plan["cells"] if c["arm"] == "A"]
    assert sorted({c["n"] for c in a_cells}) == [1, 2, 3, 4, 5]
    assert set(plan["arm_c_q_n"]) == {"2", "3", "4", "5", "6", "7"}


def test_plan_is_deterministic_for_a_cell_subset(kernel):
    """Identity fields of two small cells built twice are identical (the full plan is regenerated twice
    separately and compared byte for byte; see kat-report)."""
    ib1, ib2 = mtp.InstanceBuilder(kernel), mtp.InstanceBuilder(kernel)
    # contract cells are not computed here: use the builder on KAT parameters through the same code path
    for (arm, n, q, i) in [("K", 2, 13, 0), ("K", 3, 5, 1), ("K", 1, 101, 2)]:
        assert json.dumps(ib1.get(arm, n, q, i), sort_keys=True) == json.dumps(ib2.get(arm, n, q, i), sort_keys=True)
    ident = ib1.get("K", 2, 13, 0)
    assert set(["q", "n", "g", "a", "b", "N", "t2", "B", "size_X", "curve_seed"]) <= set(ident)
    assert ident["N_exhaustive"] == ident["N_bsgs"] == ident["N"]


# =============================================================================== L: launcher
def test_launcher_refuses_contract_cell_while_specification_not_approved(tmp_path):
    import yaml
    if yaml.safe_load(open(launcher.SPEC_PATH))["experiment"]["status"] == "approved":
        pytest.skip("specification is approved; the refusal is exercised with synthetic specs below")
    runs_before = os.path.exists(launcher.RUNS_DIR)
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"cells": [{"cell_id": "A-n2-q61-c0"}]}))
    ok, reasons = launcher.check_approval(plan_path=str(plan))
    assert not ok
    assert any("status" in r for r in reasons) and any("lock missing" in r for r in reasons)
    rc = launcher.main(["cell", "--cell-id", "A-n2-q61-c0", "--plan", str(plan), "--run-id", "RUN-should-not-exist"])
    assert rc == launcher.EXIT_REFUSED
    assert os.path.exists(launcher.RUNS_DIR) == runs_before
    assert not os.path.exists(os.path.join(launcher.RUNS_DIR, "RUN-should-not-exist"))
    record("L1-refusal", "status as on disk", {"exit_code": rc, "reasons": reasons})


def test_launcher_approval_gate_logic_with_synthetic_specs(tmp_path):
    spec = tmp_path / "specification.yaml"
    lock = tmp_path / "approval.lock"
    plan = tmp_path / "plan.json"
    plan.write_text("{}")
    spec.write_text("experiment:\n  status: approved\n  approved_by: someone\n")
    ok, reasons = launcher.check_approval(str(spec), str(lock), str(plan))
    assert not ok and any("lock missing" in r for r in reasons)
    lock.write_text(json.dumps({"approved_by": "someone", "specification_sha256": "0" * 64,
                                "code_sha256": "0" * 64, "trial_plan_sha256": "0" * 64}))
    ok, reasons = launcher.check_approval(str(spec), str(lock), str(plan))
    assert not ok and len(reasons) == 3
    lock.write_text(json.dumps({"approved_by": "someone", "specification_sha256": launcher.sha256_file(str(spec)),
                                "code_sha256": launcher.code_sha256(), "trial_plan_sha256": launcher.sha256_file(str(plan))}))
    assert launcher.check_approval(str(spec), str(lock), str(plan)) == (True, [])
    spec.write_text("experiment:\n  status: approved\n  approved_by: null\n")
    ok, reasons = launcher.check_approval(str(spec), str(lock), str(plan))
    assert not ok and any("approved_by" in r for r in reasons)
    spec.write_text("experiment:\n  status: review_required\n  approved_by: null\n")
    assert not launcher.check_approval(str(spec), str(lock), str(plan))[0]


def test_launcher_kat_flag_required_and_contract_cells_refused():
    assert launcher.main(["kat", "--arm", "A", "--q", "13", "--n", "2", "--curve-seed", "x"]) == launcher.EXIT_REFUSED
    assert launcher.main(["--kat", "kat", "--arm", "A", "--q", "61", "--n", "2", "--curve-seed", "x"]) == launcher.EXIT_REFUSED
    assert launcher.main(["--kat", "cell", "--cell-id", "A-n2-q61-c0", "--plan", "x", "--run-id", "x"]) == launcher.EXIT_REFUSED


@pytest.mark.parametrize("arm,q,n", [("A", 13, 2), ("C", 13, 2), ("B1", 13, 3), ("B2", 5, 3)])
def test_launcher_kat_cell_writes_package_in_temp_dir_only(arm, q, n, kernel, capsys):
    runs_before = os.path.exists(launcher.RUNS_DIR)
    rc = launcher.main(["--kat", "kat", "--arm", arm, "--q", str(q), "--n", str(n), "--curve-seed", "kat|launcher",
                        "--s", "20", "--tuples", "20"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    d = out["kat_dir"]
    try:
        assert not os.path.abspath(d).startswith(os.path.abspath(launcher.RUNS_DIR))
        for f in ("manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json",
                  "summary.json"):
            assert os.path.getsize(os.path.join(d, f)) > 0 or f == "stderr.log"
        man = open(os.path.join(d, "manifest.yaml")).read()
        assert "kat: true" in man and "code_sha256" in man and "derived_statistics_withheld: true" in man
        raw = json.load(open(os.path.join(d, "raw-result.json")))
        if arm == "A":
            for role, r in raw["bases"].items():
                assert "identities" not in r                        # no cross-convention comparison in KAT mode
        if arm == "C":
            assert os.path.exists(os.path.join(d, "results", "KAT-C-n2-q13.cdf.json"))
        record("L2-kat-cell-package", f"arm={arm},q={q},n={n}", {"files": sorted(os.listdir(d))})
    finally:
        shutil.rmtree(d, ignore_errors=True)
    assert os.path.exists(launcher.RUNS_DIR) == runs_before


def test_environment_record_has_compiler_and_flags():
    env = launcher.environment_record()
    assert env["compiler"]["flags"] and env["compiler"]["version"]
    assert set(launcher.CODE_FILES) == set(env["code_file_sha256"])
    assert env["libraries"]["numpy"]


def test_launcher_derived_summaries_on_synthetic_inputs_only():
    """The derived-statistics paths (used on contract cells, withheld on KAT cells) are exercised here on
    fabricated inputs, not on any counted cell."""
    from fractions import Fraction
    r = {"sampled_counts": np.array([0, 0, 1, 2, 0, 1, 0, 3]), "S_counts": np.array([5, 7]), "t2": 1, "S_size": 2,
         "draws": 1024, "multisets": 100, "cancellation_free": 80, "m_S": 4, "N_cf_formula": 80,
         "lambda": Fraction(3, 8)}
    e = launcher.arm_c_entry(r, 10, True, 0.5)
    flat = launcher.arm_c_flat(e, True)
    for k in ("hist", "lambda", "exceptional_targets", *launcher.CDF_POISSON_KEYS):
        assert k in flat
    assert flat["coverage"] == pytest.approx(0.5) and flat["zero_fraction"] == pytest.approx(0.5)
    assert flat["exceptional_targets"] == [5, 7] and flat["max_count"] == 3
    e2 = launcher.arm_c_flat(launcher.arm_c_entry(r, 10, False, 0.5), False)
    assert "coverage" not in e2 and "hist" in e2
    fake = {"line": {"B": 4, "t2": 0, "N": 9, "size_X": 2, "S_size": 1, "generic_targets": 6,
                     "special_targets_O_and_E2": 1, "identities": {}, "recount": {},
                     "conventions": {c: {"stats": {"all": {"targets": 9, "sum": 9, "sumsq": 9, "zeros": 3, "max": 2},
                                                   "generic": {"targets": 6, "sum": 6, "sumsq": 6, "zeros": 2, "max": 2}}}
                                     for c in ("A", "M", "S", "X")}}}
    summ = launcher._cell_summary_arm_a(fake, True)
    assert summ["line"]["derived"]["M"]["coverage_generic"] == [4, 6] and summ["line"]["derived"]["A"]["mean_all"] == "1"
    assert "derived" not in launcher._cell_summary_arm_a(fake, False)["line"]


def test_launcher_watchdog_marks_cell_failed_resource_exhaustion(tmp_path, kernel):
    spec = {"arm": "B1", "cell_id": "KAT-B1-watchdog", "n": 3, "q": 13, "m": 3, "curve_index": 0,
            "curve_seed": "kat|watchdog", "tuples": 400000, "group_law_subsample_fraction": 0.1,
            "tuple_seed": "kat|tuples|watchdog|0", "instances": [{"q": 13, "curve_seed": "kat|watchdog"}]}
    man = launcher.run_cell(spec, str(tmp_path / "w"), kat=True, kernel=kernel, timeout_seconds=0.3)
    assert man["status"] == "failed" and man["failure_class"] == "resource_exhaustion"
    assert "watchdog" in open(tmp_path / "w" / "stderr.log").read()


def test_launcher_arm_b_chi_patterns_are_recorded(tmp_path, kernel):
    spec = {"arm": "B1", "cell_id": "KAT-B1-patterns", "n": 3, "q": 13, "m": 3, "curve_index": 0,
            "curve_seed": "kat|patterns", "tuples": 60, "group_law_subsample_fraction": 0.1,
            "tuple_seed": "kat|tuples|patterns|0", "instances": [{"q": 13, "curve_seed": "kat|patterns"}]}
    man = launcher.run_cell(spec, str(tmp_path / "p"), kat=True, kernel=kernel)
    assert man["status"] == "completed"
    raw = json.load(open(tmp_path / "p" / "raw-result.json"))
    tally = raw["instances"][0]["tally"]
    assert sum(tally["chi_patterns"].values()) == tally["tuples"] == 60
    record("L3-arm-B-kat-tally", "q=13,n=3 (60 tuples)", {"tally_keys": sorted(tally)})


def test_launcher_approval_gate_refuses_empty_or_non_object_lock(tmp_path):
    spec = tmp_path / "specification.yaml"
    lock = tmp_path / "approval.lock"
    plan = tmp_path / "plan.json"
    plan.write_text("{}")
    spec.write_text("experiment:\n  status: approved\n  approved_by: someone\n")
    for content in ("{}", "[]", "null", "0", '""'):
        lock.write_text(content)
        ok, reasons = launcher.check_approval(str(spec), str(lock), str(plan))
        assert not ok and any("empty or not a JSON object" in r for r in reasons), content
        assert any("approved_by" in r for r in reasons) and any("code_sha256" in r for r in reasons), content


def test_launcher_empty_tuple_list_yields_complete_zero_tally():
    F, E, _ = kat_curve(13, 2, "empty-tally")
    tally = launcher._analyse_all(F, E, [], [], 1)
    assert all(tally[k] == 0 for k in launcher.TALLY_KEYS)
    assert tally["chi_patterns"] == {}
    record("L4-empty-tally", "q=13,n=2 (0 tuples)", {"tally_keys": sorted(tally)})


def test_launcher_b1_runs_the_aa_tuple_sample(tmp_path, kernel):
    cell = {"arm": "B1", "cell_id": "B1-synthetic", "n": 3, "q": 13, "tuple_size_m": 4, "tuples": 30,
            "group_law_subsample_fraction": 0.1, "tuple_seed": {"seed_string": "kat|tuples|aa|0"},
            "tuple_seed_aa": {"seed_string": "kat|tuples|aa|1"},
            "identity": {"curve_seed": {"seed_string": "kat|aa"}}}
    spec = launcher.spec_from_plan_cell(cell)[0]
    assert spec["tuple_seed_aa"] == "kat|tuples|aa|1"
    spec["cell_id"] = "KAT-B1-aa"
    spec["instances"] = [{"q": 13, "curve_seed": "kat|aa"}]                # no contract identity to check
    man = launcher.run_cell(spec, str(tmp_path / "aa"), kat=True, kernel=kernel)
    assert man["status"] == "completed"
    inst = json.load(open(tmp_path / "aa" / "raw-result.json"))["instances"]
    assert [i["sample"] for i in inst] == ["primary", "aa"]
    assert [i["tuple_seed"] for i in inst] == ["kat|tuples|aa|0", "kat|tuples|aa|1"]
    assert all(i["tally"]["tuples"] == 30 for i in inst)
    summary = json.load(open(tmp_path / "aa" / "summary.json"))
    assert [i["sample"] for i in summary["instances"]] == ["primary", "aa"]
    no_aa = dict(cell)
    del no_aa["tuple_seed_aa"]
    assert launcher.spec_from_plan_cell(no_aa)[0]["tuple_seed_aa"] is None
    record("L5-b1-aa-sample", "q=13,n=3 (30 tuples x 2 seeds)", {"samples": [i["sample"] for i in inst]})


@pytest.mark.parametrize("q,n,tuple_len", [(13, 2, 3), (5, 3, 3), (13, 3, 4), (101, 1, 4)])
def test_analyse_fibre_fast_path_agrees_with_detailed_path(q, n, tuple_len):
    F, E, _ = kat_curve(q, n, "fast")
    rng = rng_for(f"fast{q}{n}{tuple_len}")
    for _ in range(40):
        xs = [F.random_element(rng) for _ in range(tuple_len)]
        a = semaev.analyse_fibre(F, E, xs, detail=True)
        b = semaev.analyse_fibre(F, E, xs, detail=False)
        for k in ("degree", "full_degree", "squarefree", "chis", "split_completely", "zero_poly"):
            assert a[k] == b[k]
