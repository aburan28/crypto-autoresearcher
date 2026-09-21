"""
selftest_semaev.py -- brute-force toy-scale validation of S3, xDBL, xADD, and the
S4-via-resultant computation, against direct elliptic-curve arithmetic.
Run: python3 -m driver.selftest_semaev
"""
import random
from . import curve, semaev


def run():
    print("=== selftest_semaev ===")
    p = 10007
    a, b = 1, 2
    assert (4 * a ** 3 + 27 * b * b) % p != 0
    rng = random.Random(7)

    n_checks = 200
    s3_ok = 0
    dbl_ok = 0
    add_ok = 0
    for _ in range(n_checks):
        P = curve.random_point(a, b, p, rng)
        Q = curve.random_point(a, b, p, rng)
        if P[0] == Q[0]:
            continue
        R = curve.add(P, Q, a, p)
        if R is None:
            continue
        # S3(xP, xQ, xR) should vanish (R = P+Q, one of the two sign choices)
        val = semaev.S3(P[0], Q[0], R[0], a, b, p)
        assert val == 0, f"S3 nonzero for real sum: P={P} Q={Q} R={R} val={val}"
        s3_ok += 1

        D = curve.add(P, P, a, p)
        if D is not None:
            xd = semaev.xDBL(P[0], a, b, p)
            assert xd == D[0], f"xDBL mismatch: P={P} true={D[0]} got={xd}"
            dbl_ok += 1

        PmQ = curve.add(P, curve.neg(Q, p), a, p)
        if PmQ is not None and R is not None:
            xadd = semaev.xADD(P[0], Q[0], PmQ[0], a, b, p)
            assert xadd == R[0], f"xADD mismatch: P={P} Q={Q} R={R} got={xadd}"
            add_ok += 1

    print(f"  S3 vanishing on real sums: {s3_ok}/{n_checks} checked, all OK")
    print(f"  xDBL matches curve doubling: {dbl_ok} checked, all OK")
    print(f"  xADD matches curve addition: {add_ok} checked, all OK")

    # Cross-check the S4-via-resultant tool against a direct 4-point relation:
    # if P1+P2+P3+P4=O then S4(x1,x2,x3,x4) should vanish. We don't have S4_TERMS
    # hardcoded yet (derived in derive_semaev_s4.py); this just validates the
    # resultant machinery by checking S3-consistency (resultant eliminates the
    # shared X = x(P1+P2) = x(-(P3+P4)) root when P1+P2 = -(P3+P4)).
    s4_ok = 0
    for _ in range(n_checks):
        P1 = curve.random_point(a, b, p, rng)
        P2 = curve.random_point(a, b, p, rng)
        if P1[0] == P2[0]:
            continue
        S = curve.add(P1, P2, a, p)
        if S is None:
            continue
        # pick P3, P4 with P3+P4 = -S
        P3 = curve.random_point(a, b, p, rng)
        target = curve.add(curve.neg(S, p), curve.neg(P3, p), a, p)
        if target is None or P3[0] == target[0]:
            continue
        P4 = target
        val = semaev.S4_via_resultant(P1[0], P2[0], P3[0], P4[0], a, b, p)
        assert val == 0, f"S4_via_resultant nonzero for real 4-relation: {val}"
        s4_ok += 1
    print(f"  S4_via_resultant vanishing on real 4-point relations: {s4_ok} checked, all OK")
    print("ALL SEMAEV SELFTESTS PASSED")


if __name__ == "__main__":
    run()
