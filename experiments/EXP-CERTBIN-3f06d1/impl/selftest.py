#!/usr/bin/env python3
"""Phase 0 of EXP-CERTBIN-3f06d1: the generic C-SELF items and C-FIX, before
any frozen stream is drawn. Copied from EXP-CERTBIN-4e92d7/impl/selftest.py and
extended (impl-provenance.json): the descent, Macaulay-row and oracle checks
also run with a random rank-9 V basis; V-membership (linear algebra) is checked
against brute force; the [#E/2] x(2E) test is checked against a brute-force
halving search. The PER-CELL items (cell curve, cell V) are in cell_selftest()
and run in phase 1 right after the cell's curve / V are fixed and before any
reference or target stream of that cell is drawn.

All randomness: numpy.random.Generator(numpy.random.PCG64(S_selftest)),
S_selftest = 2026092410099 (one generator, consumed in the order of the tests
below); cell_selftest uses PCG64(SeedSequence([S_selftest, c])) for cell c.
Writes selftest.json; exit status 0 iff every item passes.
"""
import argparse
import datetime
import functools
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

from gf2n import Field, TableField, MODULUS, N, is_irreducible  # noqa: E402
from curve import Curve, s3_eval_school  # noqa: E402
from macaulay import (MacaulayShape, descended_E, affine_basis, affine_combine,  # noqa: E402
                      eval_equations_scalar, EQ_MONS, mu_order, degrevlex_greater, NEQ, L)
from oracles import solve_quadratic, oracle_A, oracle_B  # noqa: E402
from elim import eliminate, gf2_rank_rows  # noqa: E402
from vspace import VBasis, polynomial_V, rref_desc, int_rank  # noqa: E402
from x2e import in_2E_point, doubling_image  # noqa: E402

S_SELFTEST = 2026092410099


def rint(rng, lo, hi):
    return int(rng.integers(lo, hi))


def t_modulus():
    ok, det = is_irreducible(MODULUS)
    return {"id": "modulus_irreducible", "pass": bool(ok and MODULUS == (1 << 17) | (1 << 3) | 1),
            "modulus": "t^17 + t^3 + 1", "details": det}


def t_field_axioms(F, rng):
    n = 10000
    fails = []
    for i in range(n):
        a, b, c = rint(rng, 0, F.q), rint(rng, 0, F.q), rint(rng, 0, F.q)
        m = F.mul
        s = F.mul_school
        checks = {
            "table_eq_school": m(a, b) == s(a, b),
            "commutative": m(a, b) == m(b, a),
            "associative": m(m(a, b), c) == m(a, m(b, c)),
            "distributive": m(a, b ^ c) == m(a, b) ^ m(a, c),
            "identity": m(a, 1) == a,
            "add_inverse": (a ^ a) == 0,
            "mul_inverse": a == 0 or s(a, F.inv(a)) == 1,
            "sqrt": s(F.sqrt(a), F.sqrt(a)) == a,
            "trace_linear": F.trace(a ^ b) == F.trace(a) ^ F.trace(b),
            "trace_matches_definition": F.trace(a) == Field.trace(Field(N, MODULUS), a) if i < 200 else True,
        }
        bad = [k for k, v in checks.items() if not v]
        if bad:
            fails.append({"a": a, "b": b, "c": c, "failed": bad})
    return {"id": "field_axioms", "pass": not fails, "triples": n, "failures": fails[:20],
            "n_failures": len(fails)}


SMALL_FIELDS = [(5, (1 << 5) | (1 << 2) | 1), (7, (1 << 7) | (1 << 1) | 1), (9, (1 << 9) | (1 << 4) | 1)]


def t_point_count(rng):
    out = []
    ok_all = True
    for n, mod in SMALL_FIELDS:
        irr, _ = is_irreducible(mod)
        Fs = Field(n, mod)
        A = rint(rng, 0, Fs.q)
        B = rint(rng, 1, Fs.q)
        E = Curve(Fs, A, B)
        c1 = E.count_by_trace()
        c2 = E.count_naive()
        ok = irr and c1 == c2
        ok_all &= ok
        out.append({"n": n, "modulus_int": mod, "irreducible": irr, "A": A, "B": B,
                    "count_by_trace": c1, "count_naive": c2, "pass": ok})
    return {"id": "point_count_small_curves", "pass": ok_all, "curves": out}


def random_curve_and_points(F, rng):
    A = rint(rng, 0, F.q)
    B = rint(rng, 1, F.q)
    return Curve(F, A, B)


def random_point(E, rng):
    while True:
        x = rint(rng, 0, E.F.q)
        P = E.lift_x(x)
        if P is not None:
            if rint(rng, 0, 2):
                P = E.neg(P)
            return P


def t_s3_addition(F, rng, E=None, tag="s3_vs_point_addition"):
    if E is None:
        E = random_curve_and_points(F, rng)
    n = 1000
    fails = []
    skipped = 0
    oncurve_fail = 0
    for _ in range(n):
        P1 = random_point(E, rng)
        P2 = random_point(E, rng)
        if not (E.on_curve(P1) and E.on_curve(P2)):
            oncurve_fail += 1
        for lab, R in (("sum", E.add(P1, P2)), ("diff", E.sub(P1, P2))):
            if R is None:
                skipped += 1
                continue
            if not E.on_curve(R):
                oncurve_fail += 1
            if s3_eval_school(F, E.B, P1[0], P2[0], R[0]) != 0:
                fails.append({"P1": P1, "P2": P2, "which": lab})
    return {"id": tag, "pass": not fails and oncurve_fail == 0,
            "curve": {"A": E.A, "B": E.B}, "pairs": n, "skipped_infinity": skipped,
            "on_curve_failures": oncurve_fail, "failures": fails[:20], "n_failures": len(fails)}


def random_V(rng):
    while True:
        rows = [rint(rng, 0, F_Q) for _ in range(L)]
        if int_rank(rows) == L:
            return VBasis(rref_desc(rows), "selftest random V")


F_Q = 1 << 17


def t_descent(F, rng, V=None, B=None, n=1000, tag="descended_vs_direct"):
    if V is None:
        V = polynomial_V()
    if B is None:
        B = rint(rng, 1, F.q)
    E0, Ej = affine_basis(F, B, V.basis)
    fails = []
    aff_fails = 0
    for _ in range(n):
        xR = rint(rng, 0, F.q)
        u = rint(rng, 0, 1 << 18)
        E = descended_E(F, B, xR, V.basis)
        if not np.array_equal(E, affine_combine(E0, Ej, xR)):
            aff_fails += 1
        x1, x2 = V.comb(u & ((1 << L) - 1)), V.comb(u >> L)
        direct = s3_eval_school(F, B, x1, x2, xR)
        vals = eval_equations_scalar(E, u)
        got = sum(v << k for k, v in enumerate(vals))
        if got != direct:
            fails.append({"xR": xR, "u": u, "direct": direct, "descended": got})
    return {"id": tag, "pass": not fails and aff_fails == 0, "B": B, "V": V.label, "V_basis": V.basis, "points": n,
            "affine_identity_failures": aff_fails, "failures": fails[:20], "n_failures": len(fails)}


def naive_row(mu, fk_monos):
    acc = {}
    for m in fk_monos:
        prod = tuple(sorted(set(mu) | set(m)))
        acc[prod] = acc.get(prod, 0) ^ 1
    return {m for m, v in acc.items() if v}


def t_macaulay_rows(F, rng, V=None, B=None, tag="macaulay_rows_vs_naive"):
    if V is None:
        V = polynomial_V()
    if B is None:
        B = rint(rng, 1, F.q)
    xR = rint(rng, 0, F.q)
    E = descended_E(F, B, xR, V.basis)
    # also a random dense E (all 172 columns populated) to exercise every product
    Er = rng.integers(0, 2, size=(NEQ, len(EQ_MONS))).astype(np.uint8)
    out = []
    ok_all = True
    for D in (3, 4):
        S = MacaulayShape(D)
        # independent column order by the literal comparator of the spec
        mons = mu_order(D)
        cmp = functools.cmp_to_key(lambda a, b: -1 if degrevlex_greater(a, b) else (1 if degrevlex_greater(b, a) else 0))
        lit = sorted(mons, key=cmp)
        order_ok = lit == S.cols and S.cols[-1] == ()
        # row order literal check
        mus_lit = sorted(mu_order(D - 2), key=lambda m: (len(m), m))
        row_ok = mus_lit == S.mus
        for lab, EE in (("S3", E), ("random", Er)):
            Md = S.build_dense(EE)
            Mp = S.build(EE)
            unpack_ok = np.array_equal(S.unpack(Mp), Md)
            bad = 0
            for _ in range(50 if lab == "S3" else 25):
                row = rint(rng, 0, S.R)
                a, k = divmod(row, NEQ)
                mu = S.mus[a]
                fk = [EQ_MONS[j] for j in np.flatnonzero(EE[k])]
                want = naive_row(mu, fk)
                got = {S.cols[c] for c in np.flatnonzero(Md[row])}
                if want != got:
                    bad += 1
            ok = order_ok and row_ok and unpack_ok and bad == 0
            ok_all &= ok
            out.append({"D": D, "system": lab, "column_order_literal_ok": order_ok,
                        "row_order_literal_ok": row_ok, "pack_roundtrip_ok": unpack_ok,
                        "rows_checked": 50 if lab == "S3" else 25, "row_mismatches": bad, "pass": ok})
    return {"id": tag, "pass": ok_all, "V": V.label, "checks": out}


def t_half_trace(F, rng):
    n = 10000
    fails = []
    stats = {"no_root": 0, "two_roots": 0, "one_root": 0, "all": 0, "planted_found": 0}
    for i in range(n):
        c0 = rint(rng, 0, F.q)
        h = F.half_trace(c0)
        if F.mul(h, h) ^ h != c0 ^ F.trace(c0):
            fails.append({"i": i, "check": "H^2+H=c+Tr(c)"})
        mode = i % 4
        a = rint(rng, 0, F.q)
        b = rint(rng, 0, F.q)
        if mode == 1:
            a = 0
        if mode == 2:
            b = 0
        if i % 2 == 0:
            x0 = rint(rng, 0, F.q)
            c = F.mul_school(a, F.mul_school(x0, x0)) ^ F.mul_school(b, x0)
        else:
            x0 = None
            c = rint(rng, 0, F.q)
        kind, roots = solve_quadratic(F, a, b, c)
        if kind == "all":
            stats["all"] += 1
            if not (a == 0 and b == 0 and c == 0):
                fails.append({"i": i, "check": "all_kind"})
            continue
        for r in roots:
            if F.mul_school(a, F.mul_school(r, r)) ^ F.mul_school(b, r) ^ c != 0:
                fails.append({"i": i, "check": "root_invalid"})
        if len(set(roots)) != len(roots):
            fails.append({"i": i, "check": "duplicate_roots"})
        if x0 is not None:
            if x0 in roots:
                stats["planted_found"] += 1
            else:
                fails.append({"i": i, "check": "planted_root_missing"})
        if a != 0 and b != 0:
            d = F.div(F.mul(a, c), F.mul(b, b))
            expect = 2 if F.trace(d) == 0 else 0
            if len(roots) != expect:
                fails.append({"i": i, "check": "root_count_vs_trace"})
        stats[{0: "no_root", 1: "one_root", 2: "two_roots"}[len(roots)]] += 1
    # exhaustive cross-check of oracle A against oracle B on 3 random S_3
    # systems with the polynomial V and 3 with a random V
    ab = []
    for V in (polynomial_V(), random_V(rng)):
        for _ in range(3):
            B = rint(rng, 1, F.q)
            xR = rint(rng, 0, F.q)
            sa = oracle_A(F, B, xR, V)
            sb = oracle_B(descended_E(F, B, xR, V.basis))
            ab.append({"V": V.label, "B": B, "xR": xR, "s_A": len(sa), "s_B": len(sb), "equal_sets": sa == sb})
            if sa != sb:
                fails.append({"check": "oracleA_vs_oracleB", "B": B, "xR": xR, "V": V.label})
    return {"id": "half_trace_root_finding", "pass": not fails, "quadratics": n, "stats": stats,
            "oracle_cross_check": ab, "failures": fails[:20], "n_failures": len(fails)}


def literal_elimination(Md):
    """Literal transcription of the spec's solver on Python sets (independent
    of elim.py): for each column c in order, among rows not yet used as pivot
    rows pick the smallest original index with a 1 in column c; record (p, c)
    and XOR row p into every other unused row with a 1 in column c."""
    rows = [set(np.flatnonzero(r).tolist()) for r in Md]
    used = set()
    ops = []
    for c in range(Md.shape[1]):
        cand = [i for i in range(len(rows)) if i not in used and c in rows[i]]
        if not cand:
            continue
        p = cand[0]
        X = cand[1:]
        for x in X:
            rows[x] ^= rows[p]
        used.add(p)
        ops.append((p, c, X))
    return ops


def t_elimination_sanity(rng):
    """Extra (not a C-SELF item): column pass vs independent rank; Z vs
    non-pivot rows, on small random matrices."""
    fails = 0
    for _ in range(40):
        R = rint(rng, 5, 60)
        C = rint(rng, 5, 130)
        W = (C + 63) // 64
        dens = rng.random()
        Md = (rng.random((R, C)) < dens).astype(np.uint8)
        if rint(rng, 0, 2):
            Md[rint(rng, 0, R)] = Md[rint(rng, 0, R)] ^ Md[rint(rng, 0, R)]
        pad = np.zeros((R, W * 64 - C), dtype=np.uint8)
        Mp = np.packbits(np.concatenate([Md, pad], axis=1), axis=1, bitorder="little").view(np.uint64).reshape(R, W).copy()
        res, cpass, _ = eliminate(Mp, C)
        rk = gf2_rank_rows(Mp)
        nonpiv = sorted(set(range(R)) - set(res.p))
        lit = literal_elimination(Md)
        got = [(p, c, X.tolist()) for p, c, X in zip(res.p, res.c, res.X)]
        if res.rank != rk or not cpass or nonpiv != res.Z or lit != got:
            fails += 1
    return {"id": "extra_elimination_sanity", "pass": fails == 0, "matrices": 40, "failures": fails,
            "checks": "op log (p, c, X) equals a literal set-based transcription of the solver; rank equals an independent elimination; C-PASS; Z_D equals the non-pivot rows",
            "note": "additional check, not a C-SELF item"}


def t_vmembership(rng, V, n=10000, tag="V_membership_vs_brute_force"):
    """V-membership by linear algebra (V.coord) against brute force (the set of
    all 2^l combinations of the basis, computed by explicit XOR loops)."""
    brute = {}
    for u in range(1 << V.l):
        x = 0
        for j in range(V.l):
            if (u >> j) & 1:
                x ^= V.basis[j]
        brute[x] = u
    rank_ok = int_rank(V.basis) == V.l == 9 and len(brute) == (1 << V.l)
    fails = []
    n_in = 0
    for i in range(n):
        x = rint(rng, 0, F_Q)
        c = V.coord(x)
        want = brute.get(x)
        if c != want:
            fails.append({"x": x, "coord": c, "brute": want})
        n_in += want is not None
    all_members_ok = all(V.coord(x) == u and V.comb(u) == x for x, u in brute.items())
    return {"id": tag, "pass": rank_ok and all_members_ok and not fails, "V": V.label, "V_basis": V.basis,
            "rank_9": rank_ok, "random_elements": n, "random_elements_in_V": n_in,
            "all_2^l_members_ok": all_members_ok, "failures": fails[:20], "n_failures": len(fails)}


def t_x2e_halving(E, order, rng, npts=200, tag="x2E_test_vs_halving"):
    """[#E/2] R = O against a brute-force halving search: R in 2E iff R = O or
    x(R) = x(2S) for some point S (doubling image over every abscissa)."""
    img = doubling_image(E)
    fails = []
    n2 = 0
    for _ in range(npts):
        R = random_point(E, rng)
        a = in_2E_point(E, R, order)
        b = bool(img[R[0]])
        n2 += a
        if a != b:
            fails.append({"R": list(R), "test": a, "halving": b})
    return {"id": tag, "pass": not fails, "curve": {"A": E.A, "B": E.B, "order": order}, "points": npts,
            "in_2E": n2, "failures": fails[:20], "n_failures": len(fails)}


def t_order(E, order, q, h, rng, npts=100):
    """Cell curve order: Hasse bound, q prime, [#E] R = O for random points
    (independent of the trace-based count), and [#E / 2] != O for some point."""
    from curve import is_prime
    import math
    hasse = abs(order - (E.F.q + 1)) <= 2 * math.isqrt(E.F.q) + 2
    bad = 0
    for _ in range(npts):
        R = random_point(E, rng)
        if E.mul(order, R) is not None:
            bad += 1
    ok = hasse and is_prime(q) and order == h * q and bad == 0
    return {"id": "cell_curve_order", "pass": ok, "order": order, "h": h, "q": q, "hasse_ok": hasse,
            "q_prime": is_prime(q), "points_with_order_R_not_O": bad, "points": npts}


def cell_selftest(F, E, order, V, cls, cellno):
    """Per-cell C-SELF items (spec controls C-SELF): point counting, S_3 against
    point addition, descent against direct evaluation, Macaulay rows against
    naive multiplication, oracle A against oracle B, V rank / membership, and
    the [#E/2] x(2E) test against brute-force halving on 200 random points."""
    t0 = time.time()
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([S_SELFTEST, cellno])))
    q = order // (2 if (order // 2) % 2 == 1 else 4)
    h = order // q
    items = []
    items.append(t_order(E, order, q, h, rng))
    items.append(t_s3_addition(F, rng, E=E, tag="cell_s3_vs_point_addition"))
    items.append(t_descent(F, rng, V=V, B=E.B, tag="cell_descended_vs_direct"))
    items.append(t_macaulay_rows(F, rng, V=V, B=E.B, tag="cell_macaulay_rows_vs_naive"))
    ab = []
    ok_ab = True
    for _ in range(3):
        xR = rint(rng, 0, F.q)
        sa = oracle_A(F, E.B, xR, V)
        sb = oracle_B(descended_E(F, E.B, xR, V.basis))
        ab.append({"xR": xR, "s_A": len(sa), "s_B": len(sb), "equal_sets": sa == sb})
        ok_ab &= sa == sb
    items.append({"id": "cell_oracleA_vs_oracleB", "pass": ok_ab, "checks": ab})
    items.append(t_vmembership(rng, V, tag="cell_V_rank_and_membership_vs_brute_force"))
    items.append(t_x2e_halving(E, order, rng, tag="cell_x2E_test_vs_halving"))
    img = doubling_image(E)
    full = np.array_equal(cls == 2, img)
    items.append({"id": "cell_x2E_enumeration_vs_doubling_image_all_x", "pass": bool(full),
                  "note": "every x: [#E/2]-test class x2E iff x in the brute-force doubling image",
                  "disagreements": int(((cls == 2) != img).sum())})
    return {"cell_no": cellno, "seed": {"S_selftest": S_SELFTEST, "entropy": [S_SELFTEST, cellno],
                                        "generator": "numpy.random.Generator(numpy.random.PCG64(numpy.random.SeedSequence([S_selftest, c])))"},
            "items": items, "pass": all(i["pass"] for i in items), "wall_seconds": time.time() - t0}


def t_fixture():
    s3, s4 = MacaulayShape(3), MacaulayShape(4)
    got = {"D3": [s3.R, s3.C], "D4": [s4.R, s4.C]}
    ok = got == {"D3": [323, 988], "D4": [2924, 4048]}
    return {"id": "C-FIX", "pass": ok, "expected": {"D3": [323, 988], "D4": [2924, 4048]}, "observed": got}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if os.path.exists(args.out):
        print(f"refusing to overwrite existing {args.out}", file=sys.stderr)
        return 2
    t0 = time.time()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    rng = np.random.Generator(np.random.PCG64(S_SELFTEST))
    items = []
    items.append(t_modulus())
    if not items[-1]["pass"]:
        # stop before building tables on a reducible modulus (contract defect)
        res = {"started_at": started, "all_pass": False, "stopped": "modulus not irreducible", "items": items}
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        json.dump(res, open(args.out, "w"), indent=1)
        return 1
    F = TableField()
    items.append(t_field_axioms(F, rng))
    items.append(t_point_count(rng))
    items.append(t_s3_addition(F, rng))
    items.append(t_descent(F, rng))
    Vr = random_V(rng)
    items.append(t_descent(F, rng, V=Vr, tag="descended_vs_direct_random_V"))
    items.append(t_macaulay_rows(F, rng))
    items.append(t_macaulay_rows(F, rng, V=Vr, tag="macaulay_rows_vs_naive_random_V"))
    items.append(t_half_trace(F, rng))
    items.append(t_vmembership(rng, Vr))
    items.append(t_vmembership(rng, polynomial_V(), n=2000, tag="V_membership_vs_brute_force_polynomial"))
    Ex = random_curve_and_points(F, rng)
    items.append(t_x2e_halving(Ex, Ex.count_by_trace(), rng))
    items.append(t_elimination_sanity(rng))
    items.append(t_fixture())
    all_pass = all(i["pass"] for i in items)
    res = {
        "experiment_id": "EXP-CERTBIN-3f06d1",
        "phase": 0,
        "seed": {"S_selftest": S_SELFTEST, "generator": "numpy.random.Generator(numpy.random.PCG64(seed))"},
        "numpy_version": np.__version__,
        "argv": sys.argv,
        "cwd": os.getcwd(),
        "started_at": started,
        "finished_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "wall_seconds": time.time() - t0,
        "all_pass": all_pass,
        "C-SELF_pass": all(i["pass"] for i in items if i["id"] not in ("C-FIX",)),
        "C-FIX_pass": items[-1]["pass"],
        "items": items,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(res, f, indent=1, default=int)
    print(json.dumps({"selftest_all_pass": all_pass, "items": {i["id"]: i["pass"] for i in items}}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
