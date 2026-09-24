"""Self-tests for the J1 verifier (VC-1). TASK-20260924-7e2d94.

Every test is seeded by a declared rule: the seed is the first 8 bytes of
sha256("TASK-20260924-7e2d94|<test name>"), big-endian, fed to
numpy.random.Generator(numpy.random.PCG64(seed)).
"""
import hashlib

import numpy as np

import bring as R
import descent as D
import gf2n as F
from curve_s3 import Curve


def seed_for(name):
    return int.from_bytes(hashlib.sha256(("TASK-20260924-7e2d94|" + name).encode()).digest()[:8], "big")


def rng_for(name):
    s = seed_for(name)
    return np.random.Generator(np.random.PCG64(s)), s


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


# ---------------------------------------------------------------------- ST-1
def st_modulus():
    rep = F.modulus_irreducibility_report()
    return {"passed": bool(rep["irreducible"]), "detail": rep}


# ---------------------------------------------------------------------- ST-2
def st_field_axioms(n=10000):
    rng, seed = rng_for("ST-2 field axioms")
    fails = {"comm": 0, "assoc": 0, "distrib": 0, "one": 0, "inverse": 0, "frobenius_additive": 0, "range": 0}
    A = rng.integers(0, 1 << F.N, size=n)
    B = rng.integers(0, 1 << F.N, size=n)
    C = rng.integers(0, 1 << F.N, size=n)
    for a, b, c in zip(A.tolist(), B.tolist(), C.tolist()):
        ab = F.mul(a, b)
        if ab != F.mul(b, a):
            fails["comm"] += 1
        if F.mul(ab, c) != F.mul(a, F.mul(b, c)):
            fails["assoc"] += 1
        if F.mul(a, b ^ c) != ab ^ F.mul(a, c):
            fails["distrib"] += 1
        if F.mul(a, 1) != a:
            fails["one"] += 1
        if a and F.mul(a, F.inv(a)) != 1:
            fails["inverse"] += 1
        if F.sqr(a ^ b) != F.sqr(a) ^ F.sqr(b):
            fails["frobenius_additive"] += 1
        if ab >> F.N:
            fails["range"] += 1
    # vectorised multiplication against scalar multiplication
    va = F.vmul(A.astype(np.uint64), B.astype(np.uint64)).tolist()
    vfail = sum(1 for a, b, r in zip(A.tolist(), B.tolist(), va) if F.mul(a, b) != r)
    return {"passed": all(v == 0 for v in fails.values()) and vfail == 0, "seed": seed, "triples": n,
            "failures": fails, "vmul_vs_mul_pairs": n, "vmul_vs_mul_failures": vfail}


# ---------------------------------------------------------------------- ST-3
def st_trace_halftrace(n=10000):
    rng, seed = rng_for("ST-3 trace and half-trace")
    bad_tr = 0
    bad_ht = 0
    tr0 = 0
    for c in rng.integers(0, 1 << F.N, size=n).tolist():
        t = F.trace(c)
        if t not in (0, 1):
            bad_tr += 1
            continue
        h = F.half_trace(c)
        if (F.sqr(h) ^ h) != (c ^ t):
            bad_ht += 1
        tr0 += (t == 0)
    return {"passed": bad_tr == 0 and bad_ht == 0, "seed": seed, "n": n,
            "trace_not_in_F2": bad_tr, "halftrace_failures": bad_ht, "trace_zero_fraction": tr0 / n}


# ---------------------------------------------------------------------- ST-4
def st_archived_curve(curve_json):
    A, B = curve_json["A"], curve_json["B"]
    E = Curve(A, B)
    q, h, order = curve_json["q"], curve_json["h"], curve_json["order"]
    P = tuple(curve_json["P"])
    Q = tuple(curve_json["Q"])
    kQ = curve_json["k_Q"]
    res = {
        "A": A, "B": B,
        "B_nonzero": B != 0,
        "P_on_curve": E.on_curve(P),
        "Q_on_curve": E.on_curve(Q),
        "qP_is_O": E.smul(q, P) is None,
        "qQ_is_O": E.smul(q, Q) is None,
        "P_not_O_and_not_2torsion": P is not None and E.smul(2, P) is not None,
        "kQ_P_equals_Q": E.smul(kQ, P) == Q,
        "q_prime": is_prime(q),
        "h_in_2_4": h in (2, 4),
        "order_equals_h_q": order == h * q,
    }
    n_count = E.count_points_vectorised()
    res["point_count_by_enumeration"] = n_count
    res["point_count_matches_archived_order"] = (n_count == order)
    res["passed"] = all(v for k, v in res.items() if isinstance(v, bool))
    return res, E


# ---------------------------------------------------------------------- ST-5
def st_group_law(E, order, n_assoc=200, n_lagrange=20):
    rng, seed = rng_for("ST-5 group law")
    assoc_fail = 0
    for _ in range(n_assoc):
        P1, P2, P3 = (E.random_point(rng) for _ in range(3))
        if E.add(E.add(P1, P2), P3) != E.add(P1, E.add(P2, P3)):
            assoc_fail += 1
    lag_fail = 0
    inv_fail = 0
    oncurve_fail = 0
    for _ in range(n_lagrange):
        P = E.random_point(rng)
        if not E.on_curve(P):
            oncurve_fail += 1
        if E.smul(order, P) is not None:
            lag_fail += 1
        if E.add(P, E.neg(P)) is not None:
            inv_fail += 1
    return {"passed": assoc_fail == 0 and lag_fail == 0 and inv_fail == 0 and oncurve_fail == 0,
            "seed": seed, "associativity_triples": n_assoc, "associativity_failures": assoc_fail,
            "lagrange_points": n_lagrange, "order_times_P_not_O": lag_fail,
            "P_plus_negP_not_O": inv_fail, "random_point_not_on_curve": oncurve_fail}


# ---------------------------------------------------------------------- ST-6
def st_s3_point_addition(E, curve_json, n_random=1000, n_subgroup=200):
    rng, seed = rng_for("ST-6 S3 against point addition")
    q = curve_json["q"]
    P0 = tuple(curve_json["P"])
    fails_sum = 0
    fails_diff = 0
    tested = 0
    nonvacuous_zero = 0
    pairs_random = 0
    pairs_subgroup = 0

    def one(P1, P2):
        nonlocal fails_sum, fails_diff, tested, nonvacuous_zero
        S = E.add(P1, P2)
        Dd = E.add(P1, E.neg(P2))
        if S is None or Dd is None:
            return False
        x1, x2 = P1[0], P2[0]
        if E.S3(x1, x2, S[0]) != 0:
            fails_sum += 1
        if E.S3(x1, x2, Dd[0]) != 0:
            fails_diff += 1
        P3 = E.random_point(rng)
        if P3[0] not in (S[0], Dd[0]) and E.S3(x1, x2, P3[0]) == 0:
            nonvacuous_zero += 1
        tested += 1
        return True

    while pairs_random < n_random:
        if one(E.random_point(rng), E.random_point(rng)):
            pairs_random += 1
    while pairs_subgroup < n_subgroup:
        a = int(rng.integers(1, q))
        b = int(rng.integers(1, q))
        if one(E.smul(a, P0), E.smul(b, P0)):
            pairs_subgroup += 1
    return {"passed": fails_sum == 0 and fails_diff == 0, "seed": seed,
            "pairs_random_points": pairs_random, "pairs_in_archived_subgroup": pairs_subgroup,
            "S3_nonzero_at_x_of_sum": fails_sum, "S3_nonzero_at_x_of_difference": fails_diff,
            "nonvacuity_S3_zero_at_unrelated_x3": nonvacuous_zero,
            "nonvacuity_note": "count of unrelated random x3 at which S_3 also vanished (expected about 0; S_3 is quadratic in x3)"}


# ---------------------------------------------------------------------- ST-7
def affine_basis(B):
    E0 = D.descend_symbolic(0, B)[0]
    Ej = [D.descend_symbolic(1 << j, B)[0] for j in range(F.N)]
    Ej = [[E0[k] ^ Ej[j][k] for k in range(F.N)] for j in range(F.N)]
    return E0, Ej


def affine_combination(E0, Ej, xR):
    out = [set(e) for e in E0]
    for j in range(F.N):
        if (xR >> j) & 1:
            for k in range(F.N):
                out[k] ^= Ej[j][k]
    return [frozenset(e) for e in out]


def st_descent_random(E, n_xr=20, n_v=50):
    """Route 1 vs route 2 on random x_R; scalar pointwise check; affine structure."""
    rng, seed = rng_for("ST-7 descent")
    B = E.B
    E0, Ej = affine_basis(B)
    route_fail = 0
    deg_fail = 0
    point_fail = 0
    affine_fail = 0
    for _ in range(n_xr):
        xR = int(rng.integers(0, 1 << F.N))
        f1, _S = D.descend_symbolic(xR, B)
        f2, _vals = D.descend_interpolation(xR, B)
        if f1 != f2:
            route_fail += 1
        if D.max_degree(f1) > 2:
            deg_fail += 1
        if f1 != affine_combination(E0, Ej, xR):
            affine_fail += 1
        for v in rng.integers(0, 1 << 18, size=n_v).tolist():
            x1 = v & 0x1FF
            x2 = (v >> 9) & 0x1FF
            val = E.S3(x1, x2, xR)                       # scalar F_2^17, no descent
            for k in range(F.N):
                if ((val >> k) & 1) != R.beval(f1[k], v):
                    point_fail += 1
                    break
    return {"passed": route_fail == 0 and deg_fail == 0 and point_fail == 0 and affine_fail == 0,
            "seed": seed, "random_xR": n_xr, "points_per_xR": n_v,
            "route1_vs_route2_mismatch": route_fail, "degree_above_2": deg_fail,
            "scalar_pointwise_mismatch": point_fail, "affine_decomposition_mismatch": affine_fail}, (E0, Ej)


# ---------------------------------------------------------------------- ST-8
def _rand_poly(rng, maxdeg, nterms):
    p = set()
    for _ in range(nterms):
        d = int(rng.integers(0, maxdeg + 1))
        idx = rng.choice(18, size=d, replace=False)
        m = 0
        for i in idx.tolist():
            m |= 1 << i
        p ^= {m}
    return p


def st_boolean_ring(n=200):
    rng, seed = rng_for("ST-8 Boolean ring")
    fails = {"comm": 0, "assoc": 0, "distrib": 0, "eval_hom_mul": 0, "eval_hom_add": 0,
             "idempotent_vars": 0, "packed_eval": 0}
    for _ in range(n):
        p = _rand_poly(rng, 3, 8)
        q = _rand_poly(rng, 3, 8)
        r = _rand_poly(rng, 2, 8)
        pq = R.bmul(p, q)
        if pq != R.bmul(q, p):
            fails["comm"] += 1
        if R.bmul(pq, r) != R.bmul(p, R.bmul(q, r)):
            fails["assoc"] += 1
        if R.bmul(p, R.badd(q, r)) != R.badd(pq, R.bmul(p, r)):
            fails["distrib"] += 1
        tp = R.eval_poly(p)
        tq = R.eval_poly(q)
        if not np.array_equal(R.eval_poly(pq), tp & tq):
            fails["eval_hom_mul"] += 1
        if not np.array_equal(R.eval_poly(R.badd(p, q)), tp ^ tq):
            fails["eval_hom_add"] += 1
        bits = np.unpackbits(tp)
        for v in rng.integers(0, 1 << 18, size=5).tolist():
            if R.beval(p, v) != int(bits[v]):
                fails["packed_eval"] += 1
    for i in range(18):
        if R.bmul({1 << i}, {1 << i}) != {1 << i}:
            fails["idempotent_vars"] += 1
    # zero divisor sanity: v_i (v_i + 1) = 0
    zd = all(R.bmul({1 << i}, {1 << i, 0}) == set() for i in range(18))
    return {"passed": all(v == 0 for v in fails.values()) and zd, "seed": seed, "triples": n,
            "failures": fails, "v_i_times_v_i_plus_1_is_zero": zd}


# ---------------------------------------------------------------------- ST-9
def st_checkers_synthetic(n_sys=20, n_pairs=200):
    """All three checkers accept synthetic identities and reject corrupted ones."""
    rng, seed = rng_for("ST-9 checkers on synthetic identities")
    acc_fail = 0
    rej_fail = 0
    disagree = 0
    # a hand identity: f_0 = v_0, f_1 = v_0 + 1  =>  1*f_0 + 1*f_1 = 1
    f = [set() for _ in range(17)]
    f[0] = {1}
    f[1] = {1, 0}
    C = [(0, 0), (0, 1)]
    tt = R.truth_tables(f)
    hand_ok = (R.residual_A(C, f) == {0} and R.residual_B(C, R.f_arrays(f)) == {0} and R.check_C(C, tt)[0])
    hand_rej = (R.residual_A(C[:1], f) != {0} and R.residual_B(C[:1], R.f_arrays(f)) != {0} and not R.check_C(C[:1], tt)[0])
    for _ in range(n_sys):
        f = [set()] + [_rand_poly(rng, 2, 60) for _ in range(16)]
        Cp = []
        seen = set()
        while len(Cp) < n_pairs:
            d = int(rng.integers(0, 4))
            idx = rng.choice(18, size=d, replace=False)
            m = 0
            for i in idx.tolist():
                m |= 1 << i
            k = int(rng.integers(1, 17))
            if (m, k) not in seen:
                seen.add((m, k))
                Cp.append((m, k))
        s = set()
        for m, k in Cp:
            s = R.badd(s, R.bmul({m}, f[k]))
        f[0] = R.badd(s, {0})
        C = Cp + [(0, 0)]
        farr = R.f_arrays(f)
        tt = R.truth_tables(f)
        a = R.residual_A(C, f) == {0}
        b = R.residual_B(C, farr) == {0}
        c = R.check_C(C, tt)[0]
        if not (a and b and c):
            acc_fail += 1
        if len({a, b, c}) != 1:
            disagree += 1
        # corrupted: drop the last non-vacuous Cp pair
        for j in range(len(Cp) - 1, -1, -1):
            m, k = Cp[j]
            if not R.vanishes_identically(m, tt[k]):
                break
        Cc = C[:j] + C[j + 1:]
        a = R.residual_A(Cc, f) == {0}
        b = R.residual_B(Cc, farr) == {0}
        c = R.check_C(Cc, tt)[0]
        if a or b or c:
            rej_fail += 1
        if len({a, b, c}) != 1:
            disagree += 1
    return {"passed": hand_ok and hand_rej and acc_fail == 0 and rej_fail == 0 and disagree == 0,
            "seed": seed, "hand_identity_accepted": hand_ok, "hand_identity_corruption_rejected": hand_rej,
            "synthetic_systems": n_sys, "pairs_each": n_pairs + 1,
            "synthetic_not_accepted": acc_fail, "synthetic_corrupted_not_rejected": rej_fail,
            "checker_disagreements": disagree}
