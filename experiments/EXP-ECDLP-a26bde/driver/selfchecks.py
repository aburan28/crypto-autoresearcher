"""Stage 1 (blocking): the five self-checks of IDEA-20260905-dacf4f part (C),
run against the p-adic instrument (padic.py, formalgroup.py, instrument.py)
before any Stage 2/3 computation. Prints a pass/fail transcript per check and
exits nonzero on any failure (the module is not to be used for Stage 2/3 if
any check fails -- per the contract's stopping rule).
"""
from __future__ import annotations

import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from harness.toycurve import EllipticCurve  # noqa: E402

from formalgroup import FormalGroup  # noqa: E402
from padic import padd  # noqa: E402
from instrument import (  # noqa: E402
    split_point, hensel_lift_point, non_canonical_section, digit as digit_fn,
    torsion_section, anomalous_log, AnomalousBreak, PrecisionInsufficient,
    eval_series_mod, curve_lift_projective, valuation_modp,
)

MARGIN = 40
WORKING_DEGREE = 80


def _torsion(fg, p, K, n, R_mod):
    lift_fn = lambda N: hensel_lift_point(fg, p, N, R_mod[0], R_mod[1])
    t, d, v = split_point(p, K, lift_fn, n, fg)
    return t, d, v


def check1_homomorphism(transcript):
    """torsion_section is a homomorphism: t(R1+R2) == t(R1)+t(R2), on random
    pairs and exhaustively for a small n."""
    p, A, B = 1009, 2, 3
    E = EllipticCurve(p, A, B)
    for x in range(1, p):
        R = E.lift_x(x)
        if R is not None:
            base = R
            break
    n = 1
    Q = base
    while Q is not None:
        Q = E.add(Q, base)
        n += 1
    fg = FormalGroup(A, B, D=WORKING_DEGREE)
    K = 3
    NK = p ** K

    def torsion_affine(Rpt):
        t, _d, _v = _torsion(fg, p, K, n, Rpt)
        return t

    random.seed(42)
    mismatches = []
    trials = 0
    # random pairs
    while trials < 30:
        j1 = random.randrange(1, n)
        j2 = random.randrange(1, n)
        R1 = E.mul(j1, base)
        R2 = E.mul(j2, base)
        R3 = E.add(R1, R2)
        if R3 is None:
            continue  # skip the R1 = -R2 coincidence; covered exhaustively below
        t1, t2, t3 = torsion_affine(R1), torsion_affine(R2), torsion_affine(R3)
        lhs = padd((t1[0], t1[1], 1), (t2[0], t2[1], 1), A, NK)
        Xl, Yl, Zl = lhs
        Zinv = pow(Zl % NK, -1, NK)
        lhs_aff = ((Xl * Zinv) % NK, (Yl * Zinv) % NK)
        trials += 1
        if lhs_aff != t3:
            mismatches.append(("random", j1, j2, lhs_aff, t3))
    # exhaustive at a small size: use a curve/point with small order n2 = 7,
    # so both j1 + j2 == n2 (R3 = O) and other wraps are exercised.
    p2, A2, B2 = 101, 1, 1
    E2 = EllipticCurve(p2, A2, B2)
    base2 = (3, 43)
    assert E2.is_on_curve(base2)
    n2 = 1
    Q2 = base2
    while Q2 is not None:
        Q2 = E2.add(Q2, base2)
        n2 += 1
    assert n2 == 7
    fg2 = FormalGroup(A2, B2, D=WORKING_DEGREE)
    K2c = 3
    NK2 = p2 ** K2c

    def torsion_affine2(Rpt):
        if Rpt is None:
            return None  # t(O) = O by definition; handled separately below
        t, _d, _v = _torsion(fg2, p2, K2c, n2, Rpt)
        return t

    exhaustive_pairs = 0
    for j1 in range(1, n2):
        for j2 in range(1, n2):
            R1 = E2.mul(j1, base2)
            R2 = E2.mul(j2, base2)
            R3 = E2.add(R1, R2)
            t1, t2, t3 = torsion_affine2(R1), torsion_affine2(R2), torsion_affine2(R3)
            exhaustive_pairs += 1
            if t3 is None:
                # R1 = -R2 mod p (torsion): t(R1)+t(R2) must equal O too.
                lhs = padd((t1[0], t1[1], 1), (t2[0], t2[1], 1), A2, NK2)
                if lhs[2] % NK2 != 0:
                    mismatches.append(("exhaustive-O", j1, j2, lhs, None))
                continue
            lhs = padd((t1[0], t1[1], 1), (t2[0], t2[1], 1), A2, NK2)
            Xl, Yl, Zl = lhs
            if Zl % p2 == 0:
                mismatches.append(("exhaustive-unexpected-O", j1, j2, lhs, t3))
                continue
            Zinv = pow(Zl % NK2, -1, NK2)
            lhs_aff = ((Xl * Zinv) % NK2, (Yl * Zinv) % NK2)
            if lhs_aff != t3:
                mismatches.append(("exhaustive", j1, j2, lhs_aff, t3))
    passed = len(mismatches) == 0
    transcript["check1_homomorphism"] = {
        "passed": passed, "random_trials": trials,
        "exhaustive_curve": {"p": p2, "n": n2, "pairs_tested": exhaustive_pairs},
        "mismatches": mismatches[:10],
    }
    return passed


def check2_defect_non_additivity(transcript):
    """The naive (non-canonical) section's defect is non-additive: exhibit
    pairs with u(R1+R2) != u(R1)+u(R2) at a rate near 1, where u(R) is the
    formal-group digit of the naive section's own defect from the torsion
    section, i.e. defect(R) = log(s(R) - t(R))."""
    p, A, B = 1009, 2, 3
    E = EllipticCurve(p, A, B)
    for x in range(1, p):
        R = E.lift_x(x)
        if R is not None:
            base = R
            break
    n = 1
    Q = base
    while Q is not None:
        Q = E.add(Q, base)
        n += 1
    fg = FormalGroup(A, B, D=WORKING_DEGREE)
    K = 3
    K_big = K + 30  # compute s(R) - t(R) at deep precision, THEN truncate the
    # digit down to K -- doing this subtraction at bare p^K (as an earlier
    # version of this check did) collapses to an exact-zero Z-coordinate
    # every time (BUG-EXP-a26bde-004, see derivation_note.md): the same
    # "normal minus normal, near-O result" precision loss as
    # BUG-EXP-a26bde-002, here in a check rather than in the instrument.
    NK = p ** K

    def defect_digit(Rpt):
        t_big, _d, _v = _torsion(fg, p, K_big, n, Rpt)
        s_big = non_canonical_section(A, B, p, K_big, Rpt[0], Rpt[1])
        N_big = p ** K_big
        neg_t = (t_big[0] % N_big, (-t_big[1]) % N_big, 1)
        diff = padd((s_big[0], s_big[1], 1), neg_t, A, N_big)
        if diff[2] % p == 0:
            from padic import is_identity
            if is_identity(diff):
                return 0  # exact canonical case (s == t); zero defect
        t2, w2, N2 = __import__("padic").to_tw(diff, N_big, p)
        ell = eval_series_mod(fg.log, t2, N2, p)
        v = valuation_modp(ell, p, K)
        if v >= K:
            return 0
        return ((ell % (p ** K)) // (p ** v)) % p

    random.seed(7)
    non_additive = 0
    trials = 0
    while trials < 30:
        j1 = random.randrange(1, n)
        j2 = random.randrange(1, n)
        R1 = E.mul(j1, base)
        R2 = E.mul(j2, base)
        R3 = E.add(R1, R2)
        if R3 is None:
            continue
        u1, u2, u3 = defect_digit(R1), defect_digit(R2), defect_digit(R3)
        trials += 1
        if (u1 + u2) % p != u3:
            non_additive += 1
    rate = non_additive / trials if trials else 0.0
    passed = rate >= 0.9  # "at a rate near 1"
    transcript["check2_defect_non_additivity"] = {
        "passed": passed, "trials": trials, "non_additive": non_additive, "rate": rate,
    }
    return passed


def check3_precision_consistency(transcript):
    """Every output at precision k+1, truncated, equals the output at
    precision k, for k = 2, 3."""
    p, A, B = 1009, 2, 3
    E = EllipticCurve(p, A, B)
    for x in range(1, p):
        R = E.lift_x(x)
        if R is not None:
            base = R
            break
    n = 1
    Q = base
    while Q is not None:
        Q = E.add(Q, base)
        n += 1
    fg = FormalGroup(A, B, D=WORKING_DEGREE)
    ok = True
    details = []
    for k in (2, 3):
        t_k, d_k, v_k = _torsion(fg, p, k, n, base)
        t_k1, d_k1, v_k1 = _torsion(fg, p, k + 1, n, base)
        NK = p ** k
        agree = (t_k1[0] % NK, t_k1[1] % NK) == t_k and d_k1 == d_k and v_k1 == v_k
        details.append({"k": k, "agree": agree})
        ok = ok and agree
    transcript["check3_precision_consistency"] = {"passed": ok, "details": details}
    return ok


def check4_first_order_identity(transcript):
    """x(P + X) - x(P) == 2 y(P) * formal_log(X) mod p^2, on random pairs
    (P, X) with X in the formal group (constructed with a small explicit t
    value so X is genuinely in E_1)."""
    p, A, B = 1009, 2, 3
    fg = FormalGroup(A, B, D=WORKING_DEGREE)
    E = EllipticCurve(p, A, B)
    from padic import from_tw
    K = 2
    margin = MARGIN
    N = p ** (K + margin)
    NK = p ** K
    random.seed(99)
    trials = 0
    mismatches = []
    for _ in range(20):
        x0 = random.randrange(1, p)
        R = E.lift_x(x0)
        if R is None:
            continue
        Pfull = hensel_lift_point(fg, p, N, R[0], R[1])
        Pproj = curve_lift_projective(Pfull, N)
        t_z = p * random.randrange(1, p)  # valuation-1 formal parameter
        w_z = eval_series_mod(fg.w, t_z % N, N, p)
        Zpt = from_tw(t_z % N, w_z)
        summed = padd(Pproj, Zpt, A, N)
        xs, ys, Ns = __import__("padic").to_affine(summed, N, p)
        ell = eval_series_mod(fg.log, t_z % N, N, p)
        lhs = (xs - Pproj[0]) % NK
        rhs = (2 * Pfull[1] * ell) % NK
        trials += 1
        if lhs != rhs:
            mismatches.append((x0, lhs, rhs))
    passed = len(mismatches) == 0 and trials > 0
    transcript["check4_first_order_identity"] = {
        "passed": passed, "trials": trials, "mismatches": mismatches[:10],
    }
    return passed


def check5_anomalous(transcript):
    """anomalous_log recovers m (certified [m]P == Q) on several anomalous
    toy curves, and the non-anomalous torsion-section construction refuses
    (raises AnomalousBreak) when n == p is forced on a non-anomalous curve."""
    import sympy
    candidates = []
    for pcand in sympy.primerange(1000, 4000):
        for A in range(1, 6):
            for B in range(1, 6):
                try:
                    E = EllipticCurve(pcand, A, B)
                except ValueError:
                    continue
                if E.order() == pcand:
                    candidates.append((pcand, A, B))
        if len(candidates) >= 6:
            break

    random.seed(123)
    total, certified = 0, 0
    details = []
    for (p, A, B) in candidates[:6]:
        E = EllipticCurve(p, A, B)
        fg = FormalGroup(A, B, D=WORKING_DEGREE)
        for x in range(1, p):
            R = E.lift_x(x)
            if R is not None:
                base = R
                break
        for _ in range(4):
            m_true = random.randrange(1, p)
            Qpt = E.mul(m_true, base)
            if Qpt is None:
                continue
            try:
                m = anomalous_log(fg, p, base, Qpt)
            except Exception as e:
                details.append({"p": p, "m_true": m_true, "error": str(e)})
                total += 1
                continue
            cert = E.mul(m, base) == Qpt
            total += 1
            certified += int(cert)
            if not cert:
                details.append({"p": p, "m_true": m_true, "m_recovered": m, "certified": False})

    # negative control: force n = p on a non-anomalous curve
    p0, A0, B0 = 1009, 2, 3
    E0 = EllipticCurve(p0, A0, B0)
    for x in range(1, p0):
        R = E0.lift_x(x)
        if R is not None:
            base0 = R
            break
    fg0 = FormalGroup(A0, B0, D=WORKING_DEGREE)
    lift_fn0 = lambda N: hensel_lift_point(fg0, p0, N, base0[0], base0[1])
    refusal_correct = False
    refusal_detail = None
    try:
        split_point(p0, 2, lift_fn0, p0, fg0)
        refusal_detail = "no exception raised -- DEFECT"
    except AnomalousBreak as e:
        refusal_correct = True
        refusal_detail = str(e)
    except Exception as e:
        refusal_detail = f"wrong exception type {type(e).__name__}: {e}"

    passed = (total >= 20) and (certified == total) and refusal_correct
    transcript["check5_anomalous"] = {
        "passed": passed, "total": total, "certified": certified,
        "curves_tested": len(candidates[:6]),
        "refusal_correct": refusal_correct, "refusal_detail": refusal_detail,
        "failures": details,
    }
    return passed


def run_all():
    transcript = {"working_degree": WORKING_DEGREE, "precision_margin": MARGIN}
    t0 = time.time()
    results = {}
    for name, fn in [
        ("check1_homomorphism", check1_homomorphism),
        ("check2_defect_non_additivity", check2_defect_non_additivity),
        ("check3_precision_consistency", check3_precision_consistency),
        ("check4_first_order_identity", check4_first_order_identity),
        ("check5_anomalous", check5_anomalous),
    ]:
        ts = time.time()
        ok = fn(transcript)
        elapsed = time.time() - ts
        transcript[name]["wall_seconds"] = elapsed
        results[name] = ok
        print(f"{name}: {'PASS' if ok else 'FAIL'} ({elapsed:.2f}s)")
    transcript["total_wall_seconds"] = time.time() - t0
    transcript["all_passed"] = all(results.values())
    return transcript, results


if __name__ == "__main__":
    import json
    transcript, results = run_all()
    print(json.dumps(transcript, indent=2, default=str))
    sys.exit(0 if transcript["all_passed"] else 1)
