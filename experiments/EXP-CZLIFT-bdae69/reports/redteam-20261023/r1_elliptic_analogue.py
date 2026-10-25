"""Red team TASK-20261023-20d7d9, joint R1: is there an elliptic analogue of the naive-section excess?

Producer reading (DEC-20261009-44c288): the G_m excess is 'the integer section being
multiplicative below p ... it has no elliptic analogue because point addition always reduces'.
Counter-construction: on a global model E/Z with small coefficients, the naive integer section
s(x0, y0) = (integer x in [0, p-1] (or balanced in (-p/2, p/2)), Hensel lift of y0) returns the
global point itself whenever the point is the reduction of an integral point with |x| < p/2. If
P~ and [d]P~ are both integral, then s([d]P) = [d]s(P) exactly in E(Q_p), and any homomorphism
E(Q_p) -> Q_p (here the Smart-style functional t([N] s(.)) read at its first nonzero digit,
N = #E(F_p)) returns exactly d. That is the elliptic analogue of g^d < p.

Curves (both inside RQ-CZLIFT-b9f765's scope, coordinates verified here with exact rationals):
  37a1 : y^2 + y = x^3 - x, short model Y^2 = X^3 - 16 X + 16 via X = 4x, Y = 8y + 4, P~ = (0, 4)
  j=0  : y^2 = x^3 + 17 (CM by Z[zeta_3], the D = -3 family), P~ = (-2, 3)
Measurement (own code, no producer module): for good, non-anomalous p in (50, 2000) with
p > 2 max|x| of the integral multiples, the success of the ratio at d in the integral set D_int
for the naive, balanced-naive and random-Hensel sections; and at 40 random d per prime.
Usage: python3 -B r1_elliptic_analogue.py   (repository root; ~1 core, about a minute)
"""
from __future__ import annotations

import json
import random
from fractions import Fraction

K = 4      # functional precision (as EXP-CZLIFT-bdae69)
KW = 10    # working precision for Jacobian arithmetic mod p^KW
CURVES = {
    "37a1_short": {"a": -16, "b": 16, "P": (0, 4), "bad": {2, 37}},
    "j0_x3p17": {"a": 0, "b": 17, "P": (-2, 3), "bad": {2, 3, 17}},
}


# ---------- exact global multiples over Q ----------
def q_add(P, Q, a):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and y1 == -y2:
        return None
    lam = (3 * x1 * x1 + a) / (2 * y1) if (x1 == x2 and y1 == y2) else (y2 - y1) / (x2 - x1)
    x3 = lam * lam - x1 - x2
    return (x3, lam * (x1 - x3) - y1)


def global_multiples(a, b, P, dmax=12):
    P = (Fraction(P[0]), Fraction(P[1]))
    assert P[1] ** 2 == P[0] ** 3 + a * P[0] + b
    out, R = {}, None
    for d in range(1, dmax + 1):
        R = q_add(R, P, a)
        assert R[1] ** 2 == R[0] ** 3 + a * R[0] + b
        out[d] = R
    return out


# ---------- F_p arithmetic ----------
def fp_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if x1 == x2:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def fp_mul(n, P, a, p):
    R = None
    for bit in bin(n)[2:]:
        R = fp_add(R, R, a, p)
        if bit == "1":
            R = fp_add(R, P, a, p)
    return R


def count_points(a, b, p):
    sq = [0] * p
    for y in range(p):
        sq[y * y % p] += 1
    return 1 + sum(sq[(x * x * x + a * x + b) % p] for x in range(p))


# ---------- Jacobian arithmetic mod p^KW (no inversions) ----------
def j_dbl(P, a, M):
    X, Y, Z = P
    YY = Y * Y % M
    S = 4 * X * YY % M
    ZZ = Z * Z % M
    Mm = (3 * X * X + a * ZZ * ZZ) % M
    X3 = (Mm * Mm - 2 * S) % M
    return (X3, (Mm * (S - X3) - 8 * YY * YY) % M, 2 * Y * Z % M)


def j_add_raw(P, Q, M):
    X1, Y1, Z1 = P
    X2, Y2, Z2 = Q
    Z1Z1, Z2Z2 = Z1 * Z1 % M, Z2 * Z2 % M
    U1, U2 = X1 * Z2Z2 % M, X2 * Z1Z1 % M
    S1, S2 = Y1 * Z2 * Z2Z2 % M, Y2 * Z1 * Z1Z1 % M
    H, r = (U2 - U1) % M, (S2 - S1) % M
    HH = H * H % M
    HHH = H * HH % M
    X3 = (r * r - HHH - 2 * U1 * HH) % M
    return (X3, (r * (U1 * HH - X3) - S1 * HHH) % M, H * Z1 * Z2 % M), H, r


def j_add(P, Q, a, M, p, flags):
    R, H, r = j_add_raw(P, Q, M)
    if H % p == 0 and r % p == 0:   # equal reductions: cannot occur for [m]S, 1 < m < ordQ; flagged if it does
        flags["precision_loss"] += 1
    return R


def j_mul(n, P, a, M, p, flags):
    R = None
    for bit in bin(n)[2:]:
        if R is not None:
            R = j_dbl(R, a, M)
        if bit == "1":
            R = P if R is None else j_add(R, P, a, M, p, flags)
    return R


def hensel_y(x, y0, a, b, p, M):
    y = y0 % M
    for _ in range(KW + 1):
        y = (y - (y * y - (x ** 3 + a * x + b)) * pow(2 * y, -1, M)) % M
    assert (y * y - (x ** 3 + a * x + b)) % M == 0 and (y - y0) % p == 0
    return y


def section(kind, Pbar, a, b, p, M, rng):
    x0, y0 = Pbar
    if kind == "naive":
        x = x0
    elif kind == "balanced":
        x = x0 if x0 <= p // 2 else x0 - p
    elif kind == "hensel":
        x = x0 + p * rng.randrange(M // p)
    else:
        raise ValueError(kind)
    return (x % M, hensel_y(x, y0, a, b, p, M), 1)


def vp(n, p, cap):
    if n == 0:
        return cap
    v = 0
    while n % p == 0 and v < cap:
        n //= p
        v += 1
    return v


def order_mod_p(Qbar, N, a, p):
    return next(n for n in sorted({N // m for m in range(1, N + 1) if N % m == 0}) if fp_mul(n, Qbar, a, p) is None)


def functional(S, N, a, p, M, flags, ordQ):
    """log([N] S) mod p^K for S in E(Z_p) with reduction of order ordQ | N.

    [ordQ] S is computed by double-and-add; its accumulator [m]S, 1 <= m < ordQ, never reduces to
    the identity or to the base point (m != 1 mod ordQ), so no degenerate Jacobian step occurs
    before the last one (a sum with reductions -S, or a doubling of a 2-torsion reduction, both of
    which return unit X, Y and Z == 0 mod p). Then log([N]S) = (N/ordQ) log([ordQ]S), and
    log(t) = t + O(t^5) on the short Weierstrass formal group, so log == t mod p^5 when v(t) >= 1.
    N/ordQ < p is a unit (N < 2p for p > 5).
    """
    X, Y, Z = j_mul(ordQ, S, a, M, p, flags)
    if Y % p == 0 or X % p == 0 or Z % p != 0:
        flags["nonunit_Y"] += 1
        return 0
    t = (-X * Z * pow(Y, -1, M)) % (p ** K)
    return (N // ordQ) * t % (p ** K)


def ratio_success(fP, fQ, d, p):
    vg, vgd = vp(fP, p, K), vp(fQ, p, K)
    if vg >= K or vgd != vg:
        return False, vg
    return (fQ // p ** vgd) * pow((fP // p ** vg) % p, -1, p) % p == d % p, vg


def main():
    rng = random.Random(20261023)
    report = {}
    primes = [q for q in range(51, 2000) if all(q % r for r in range(2, int(q ** 0.5) + 1))]
    for name, C in CURVES.items():
        a, b = C["a"], C["b"]
        mult = global_multiples(a, b, C["P"])
        integral = {d: (int(R[0]), int(R[1])) for d, R in mult.items() if R[0].denominator == 1 and R[1].denominator == 1}
        D_int = sorted(d for d in integral if d >= 2)
        xmax = max(abs(x) for x, _ in integral.values())
        cnt = {"primes_used": 0, "anomalous_skipped": 0, "small_p_skipped": 0}
        flags = {"precision_loss": 0, "nonunit_Y": 0}
        at_int = {k: {str(d): [0, 0] for d in D_int} for k in ("naive", "balanced", "hensel")}
        rand_rows = {k: {"rows": 0, "succ": 0, "succ_excl_Dint": 0, "inv_p_all_rows": 0.0, "inv_p_rows_excl_Dint": 0.0, "d_in_Dint": 0} for k in ("naive", "balanced", "hensel")}
        undefined = {k: 0 for k in ("naive", "balanced", "hensel")}
        control = {"rows": 0, "succ": 0}   # instrument control: lift of [d]P built as [d] s_hensel(P) in E(Z/p^KW)
        for p in primes:
            if p in C["bad"]:
                continue
            if p <= 2 * xmax + 1:
                cnt["small_p_skipped"] += 1
                continue
            N = count_points(a, b, p)
            if N == p:
                cnt["anomalous_skipped"] += 1
                continue
            cnt["primes_used"] += 1
            M = p ** KW
            Pbar = (C["P"][0] % p, C["P"][1] % p)
            ordP = order_mod_p(Pbar, N, a, p)
            ds = [d for d in D_int] + [rng.randrange(2, ordP - 1) for _ in range(40)]
            SP = section("hensel", Pbar, a, b, p, M, rng)
            fPc = functional(SP, N, a, p, M, flags, ordP)
            for d in ds[len(D_int):]:
                Qbar = fp_mul(d, Pbar, a, p)
                if Qbar is None or Qbar[1] == 0:
                    continue
                X, Y, Z = j_mul(d, SP, a, M, p, flags)
                zi = pow(Z, -1, M)
                Sd = (X * zi * zi % M, Y * zi * zi * zi % M, 1)
                assert (Sd[0] - Qbar[0]) % p == 0 and (Sd[1] - Qbar[1]) % p == 0
                ok, _ = ratio_success(fPc, functional(Sd, N, a, p, M, flags, order_mod_p(Qbar, N, a, p)), d, p)
                control["rows"] += 1
                control["succ"] += ok
            for kind in ("naive", "balanced", "hensel"):
                fP = functional(section(kind, Pbar, a, b, p, M, rng), N, a, p, M, flags, ordP)
                for j, d in enumerate(ds):
                    Qbar = fp_mul(d, Pbar, a, p)
                    if Qbar is None or Qbar[1] == 0:   # identity or 2-torsion: no Hensel lift of y; skipped and counted
                        flags["skipped_identity_or_2torsion"] = flags.get("skipped_identity_or_2torsion", 0) + 1
                        continue
                    fQ = functional(section(kind, Qbar, a, b, p, M, rng), N, a, p, M, flags, order_mod_p(Qbar, N, a, p))
                    ok, vg = ratio_success(fP, fQ, d, p)
                    if vg >= K:
                        undefined[kind] += 1
                    if j < len(D_int):
                        at_int[kind][str(d)][0] += 1
                        at_int[kind][str(d)][1] += ok
                    else:
                        rr = rand_rows[kind]
                        rr["rows"] += 1
                        rr["succ"] += ok
                        rr["inv_p_all_rows"] += 1 / p
                        rr["inv_p_rows_excl_Dint"] += (d not in D_int) / p
                        rr["d_in_Dint"] += d in D_int
                        rr["succ_excl_Dint"] += ok and d not in D_int
        report[name] = {
            "curve": f"y^2 = x^3 + ({a}) x + ({b})", "P_global": C["P"],
            "integral_multiples_d_le_12": {str(d): integral[d] for d in sorted(integral)},
            "nonintegral_multiples_denominators": {str(d): [mult[d][0].denominator, mult[d][1].denominator] for d in sorted(mult) if d not in integral},
            "D_int": D_int, "counts": cnt, "flags": flags, "undefined_ratio_rows": undefined,
            "instrument_control_constructed_homomorphic_lift": control,
            "success_at_D_int_[trials,successes]": at_int,
            "random_d_rows": {k: {**v, "inv_p_all_rows": round(v["inv_p_all_rows"], 3), "inv_p_rows_excl_Dint": round(v["inv_p_rows_excl_Dint"], 3)} for k, v in rand_rows.items()},
        }
    out = "experiments/EXP-CZLIFT-bdae69/reports/redteam-20261023/r1_elliptic_analogue_output.json"
    json.dump(report, open(out, "w"), indent=1)
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
