#!/usr/bin/env python3
"""Phase 0 of EXP-CERTBIN-e94b27: C-SRC (first, writes inputs.json next to
--out), then C-SELF (seed S_selftest = 2026092430099) and C-FIX. Writes
selftest.json. Exit status 0 iff all pass; any failure is a STOP (SR-2)."""
import argparse
import os
import resource
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from common import c_src, dump_json, now, S_SELFTEST, MEM_LIMIT  # noqa: E402
from gf2n import TableField, Field, is_irreducible, MODULUS  # noqa: E402
from curve import Curve, s3_eval_school  # noqa: E402
from macaulay import MacaulayShape, descended_E, EQ_MONS, mono_mask  # noqa: E402
from closure import Closure, eval_cert  # noqa: E402

A_CURVE, B_CURVE = 97044, 126251


def popc(x):
    return bin(x).count("1")


# ---------------------------------------------------------------------------
# brute-force W_D for small systems: Python ints, no numpy, no echelon()
# ---------------------------------------------------------------------------
def bf_W(eqs, nv, D):
    """Literal iteration of the spec definition with plain Python integers.
    A polynomial is an int whose bit m is the coefficient of monomial m."""
    mons = [m for m in range(1 << nv) if popc(m) <= D]
    hi = [m for m in mons if popc(m) == D]
    lo = [m for m in mons if popc(m) < D]
    # coordinate permutation: degree-D monomials on the HIGH positions
    perm = {m: i for i, m in enumerate(lo + hi)}
    inv = {i: m for m, i in perm.items()}
    nlo = len(lo)

    def enc(p):
        x = 0
        while p:
            b = p & -p
            x |= 1 << perm[b.bit_length() - 1]
            p ^= b
        return x

    def dec(x):
        p = 0
        while x:
            b = x & -x
            p |= 1 << inv[b.bit_length() - 1]
            x ^= b
        return p

    def mulv(j, p):
        out = 0
        while p:
            b = p & -p
            m = b.bit_length() - 1
            out ^= 1 << (m | (1 << j))
            p ^= b
        return out

    def span_add(basis, x):
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                basis[h] = x
                return True
        return False

    basis = {}
    mus = [m for m in range(1 << nv) if popc(m) <= D - 2]
    for mu in mus:
        for f in eqs:
            p = 0
            for m in f:
                p ^= 1 << (mu | m)
            span_add(basis, enc(p))
    dims = [len(basis)]
    first = 0 if not span_add(dict(basis), enc(1)) else None
    while True:
        low = [dec(x) for h, x in basis.items() if h < nlo]   # elements of W cap B_{<=D-1}
        nb = dict(basis)
        for g in low:                                          # EVERY basis element (literal rule)
            for j in range(nv):
                span_add(nb, enc(mulv(j, g)))
        if len(nb) == len(basis):
            break
        basis = nb
        dims.append(len(basis))
        if first is None and not span_add(dict(basis), enc(1)):
            first = len(dims) - 1
    one = not span_add(dict(basis), enc(1))
    return {"dims": dims, "iterations_to_fixpoint": len(dims) - 1, "final_dim": dims[-1], "one": one,
            "one_first_iteration": first}


def random_system(rng, nv, neq, planted):
    eqs = []
    allq = [m for m in range(1 << nv) if popc(m) <= 2]
    for _ in range(neq):
        f = [m for m in allq if rng.integers(0, 2)]
        eqs.append(f)
    if planted is not None:
        # force f_k(planted) = 0 by toggling the constant
        for f in eqs:
            val = sum(1 for m in f if (m & planted) == m) & 1
            if val:
                if 0 in f:
                    f.remove(0)
                else:
                    f.append(0)
    return eqs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (MEM_LIMIT, MEM_LIMIT))
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    t0 = time.time()
    # ---- C-SRC first (EX-1)
    src = c_src()
    dump_json(os.path.join(os.path.dirname(out), "inputs.json"), src)
    print(f"[selftest] C-SRC pass={src['pass']}", flush=True)
    if not src["pass"]:
        dump_json(out, {"C-SRC": src["pass"], "stopped": "C-SRC failure (SR-2, INV-2)", "pass": False})
        return 2

    rng = np.random.default_rng(S_SELFTEST)
    items = {}
    F = TableField()
    G = Field(17, MODULUS)

    ok, det = is_irreducible(MODULUS)
    items["modulus_irreducible"] = {"pass": bool(ok), "details": det}

    # field axioms on 10^4 triples
    fails = 0
    tri = rng.integers(0, 1 << 17, size=(10000, 3))
    for a, b, c in tri.tolist():
        m = G.mul_school
        if m(a, b) != m(b, a) or m(m(a, b), c) != m(a, m(b, c)) or m(a, b ^ c) != m(a, b) ^ m(a, c):
            fails += 1
        if F.mul(a, b) != m(a, b):
            fails += 1
        if a and m(a, F.inv(a)) != 1:
            fails += 1
    items["field_axioms_1e4"] = {"pass": fails == 0, "failures": fails, "triples": 10000}

    # S_3 against point addition on 10^3 pairs
    E = Curve(F, A_CURVE, B_CURVE)

    def rand_point():
        while True:
            x = int(rng.integers(1, 1 << 17))
            P = E.lift_x(x)
            if P is not None:
                assert E.on_curve(P)
                return P

    fails, used = 0, 0
    for _ in range(1000):
        P1, P2 = rand_point(), rand_point()
        for R in (E.add(P1, P2), E.sub(P1, P2)):
            if R is None:
                continue
            used += 1
            if s3_eval_school(G, B_CURVE, P1[0], P2[0], R[0]) != 0:
                fails += 1
    items["S3_vs_point_addition_1e3_pairs"] = {"pass": fails == 0, "failures": fails, "evaluations": used}

    # descended equations against direct F_{2^17} evaluation on 10^3 (v, x_R)
    fails = 0
    eqmask = [mono_mask(m) for m in EQ_MONS]
    cache = {}
    for _ in range(1000):
        u = int(rng.integers(0, 1 << 18))
        xR = int(rng.integers(0, 1 << 17))
        Em = descended_E(F, B_CURVE, xR)
        bits = 0
        for k in range(17):
            acc = 0
            for j in np.flatnonzero(Em[k]):
                if (eqmask[j] & u) == eqmask[j]:
                    acc ^= 1
            bits |= acc << k
        direct = s3_eval_school(G, B_CURVE, u & 511, u >> 9, xR)
        if bits != direct:
            fails += 1
    items["descent_vs_direct_1e3"] = {"pass": fails == 0, "failures": fails}

    # M_5 rows against naive multiplication on 50 random rows (+ full-matrix
    # equality of the generic builder with the copied MacaulayShape at D = 4, 5)
    xR = int(rng.integers(512, 1 << 17))
    Em = descended_E(F, B_CURVE, xR)
    eqs = [[eqmask[j] for j in np.flatnonzero(Em[k])] for k in range(17)]
    cl5 = Closure(18, 5, 17)
    M5 = cl5.build_M(eqs)
    sh5 = MacaulayShape(5)
    same5 = bool(np.array_equal(M5, sh5.build(Em)))
    cl4 = Closure(18, 4, 17)
    same4 = bool(np.array_equal(cl4.build_M(eqs), MacaulayShape(4).build(Em)))
    fails = 0
    rows = rng.integers(0, cl5.R, size=50).tolist()
    dense = cl5.unpack(M5[rows])
    for t, r in enumerate(rows):
        mu, k = cl5.row_pair(r)
        naive = {}
        for m in eqs[k]:
            x = mu | m
            naive[x] = naive.get(x, 0) ^ 1
        naive = sorted(x for x, p in naive.items() if p)
        got = sorted(int(cl5.col_mask[c]) for c in np.flatnonzero(dense[t]))
        if naive != got:
            fails += 1
    items["M5_rows_vs_naive_50"] = {"pass": fails == 0 and same4 and same5, "failures": fails, "x_R": xR,
                                    "generic_builder_equals_copied_MacaulayShape_D4": same4,
                                    "generic_builder_equals_copied_MacaulayShape_D5": same5}

    # W_D on random small Boolean systems (6 variables) vs brute force.
    # Candidates are drawn in order from the S_selftest stream with the fixed
    # schedule below; EVERY drawn system is compared. Drawing continues until
    # at least 5 systems have been compared AND the compared systems include a
    # refutation at iteration 0, a refutation at iteration >= 1, a planted
    # (satisfiable) system and an unrefuted system with >= 1 iteration
    # (cap 2000 draws). The spec's "5 systems" is the floor.
    schedule = [(3, 5, False), (3, 6, False), (4, 6, True), (3, 4, False), (4, 5, False), (3, 6, True)]
    cases = []
    allok = True
    cover = {"refuted_it0": 0, "refuted_it_ge1": 0, "planted": 0, "unrefuted_multi_iteration": 0}
    draws = 0
    while draws < 2000:
        D, neq, plant = schedule[draws % len(schedule)]
        planted = int(rng.integers(0, 64)) if plant else None
        eqs6 = random_system(rng, 6, neq, planted)
        draws += 1
        cl = Closure(6, D, neq)
        rec, cert = cl.w_closure(eqs6)
        bf = bf_W(eqs6, 6, D)
        match = (rec["dims"] == bf["dims"] and rec["iterations_to_fixpoint"] == bf["iterations_to_fixpoint"]
                 and rec["one"] == bf["one"] and rec["one_first_iteration"] == bf["one_first_iteration"])
        cert_ok = None
        if rec["one"]:
            cert_ok = eval_cert(cert, eqs6) == [0]
        if planted is not None and rec["one"]:
            match = False            # soundness: a planted system cannot be refuted
        allok &= match and (cert_ok is not False)
        if rec["one"]:
            cover["refuted_it0" if rec["one_first_iteration"] == 0 else "refuted_it_ge1"] += 1
        elif rec["iterations_to_fixpoint"] >= 1:
            cover["unrefuted_multi_iteration"] += 1
        if planted is not None:
            cover["planted"] += 1
        cases.append({"draw": draws, "D": D, "neq": neq, "planted": planted, "engine": rec,
                      "brute_force": bf, "match": match, "certificate_evaluates_to_1": cert_ok})
        if draws >= 5 and all(v > 0 for v in cover.values()):
            break
    covered = all(v > 0 for v in cover.values())
    items["W_D_vs_brute_force_random_systems"] = {
        "pass": bool(allok and covered), "systems_compared": draws, "coverage": cover,
        "all_match": bool(allok), "coverage_reached": covered, "cases": cases}

    # C-FIX
    fix = {"M_4": [cl4.R, cl4.C], "M_5": [cl5.R, cl5.C],
           "copied_MacaulayShape_M_4": [MacaulayShape(4).R, MacaulayShape(4).C],
           "copied_MacaulayShape_M_5": [sh5.R, sh5.C]}
    fix_ok = fix["M_4"] == [2924, 4048] and fix["M_5"] == [16796, 12616] \
        and fix["copied_MacaulayShape_M_4"] == [2924, 4048] and fix["copied_MacaulayShape_M_5"] == [16796, 12616]

    c_self = all(v["pass"] for v in items.values())
    res = {"experiment_id": "EXP-CERTBIN-e94b27", "S_selftest": S_SELFTEST, "C-SRC": src["pass"],
           "C-SELF": {"pass": c_self, "items": items}, "C-FIX": {"pass": bool(fix_ok), "dimensions": fix},
           "pass": bool(c_self and fix_ok and src["pass"]), "started_wall_s": t0, "finished_at": now(),
           "wall_seconds": time.time() - t0,
           "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024}
    dump_json(out, res)
    print(f"[selftest] C-SELF pass={c_self} C-FIX pass={fix_ok} ({time.time() - t0:.1f}s)", flush=True)
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
