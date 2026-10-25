"""PTM-1: run the H-CZLIFT-889c9d argument unchanged on non-anomalous ordinary class-number-one CM curves.

Known-false conclusion: Smart's ratio recovers d on the canonical lift of a non-anomalous curve.
Steps of the argument, each measured on the object:
  S1 'multiplication by p pushes everything into the formal group':   is pP = O in E(F_p)?
  S2 'non-split lift: no p-torsion point exists' (the premise of the recovery clause): #E(F_p) mod p != 0
  S3 'so [p]P^ has valuation exactly 1 and Smart's identity holds':  Smart's ratio with the
      multiplier that does reach E_1 (n = ord P, prime to p) on the CANONICAL and a pert_p lift.
  S4 rule transplant: is the degeneracy flag v_p(z([n]P^)) >= 2 a function of the curve lift
      (as on anomalous curves) or of the point lift?
"""
import json, math, random, sys
sys.path.insert(0, '.')
from rt_padic import *

K = 6
rng = random.Random(1869)
raw_models = {}
for c in json.load(open('curves_from_raw.json')):
    raw_models.setdefault(c["D"], set()).add((c["A"], c["B"], c["j_cm"]))


def order(P, N, p, A):
    n = N
    for q in range(2, N + 1):
        if q * q > N:
            break
    fac = []
    m, q = N, 2
    while q * q <= m:
        while m % q == 0:
            fac.append(q); m //= q
        q += 1
    if m > 1:
        fac.append(m)
    for q in set(fac):
        while n % q == 0 and fp_mul(n // q, P, p, A) is None:
            n //= q
    return n


def largest_prime_factor(N):
    m, q, f = N, 2, 1
    while q * q <= m:
        while m % q == 0:
            f = q; m //= q
        q += 1
    return max(f, m) if m > 1 else f


def prime_order_point(pts, N, p, A):
    ell = largest_prime_factor(N)
    while True:
        P = fp_mul(N // ell, rng.choice(pts), p, A)
        if P is not None:
            return P


results = []
for D in (-3, -11, -19, -43, -67, -163):
    models = sorted(raw_models[D])
    if D == -3:
        models = [(0, b, 0) for b in (1, 2, 3, 5, 6, 7)]
    count = 0
    for p in range(53, 420):
        if count >= 3:
            break
        if any(p % q == 0 for q in range(2, int(p ** 0.5) + 1)):
            continue
        if pow(D % p, (p - 1) // 2, p) != 1:
            continue  # inert: supersingular
        for (A, B, jcm) in models:
            if (4 * A ** 3 + 27 * B * B) % p == 0:
                continue
            pts = fp_points(p, A % p, B % p)
            N = len(pts) + 1
            if N == p:
                continue  # anomalous: not the PTM object
            ell = largest_prime_factor(N)
            if ell < 7:
                continue
            # S1, S2
            s1_pP_is_O = sum(fp_mul(p, P, p, A % p) is None for P in pts)
            cell = {"D": D, "p": p, "A": A, "B": B, "#E": N, "S1_points_with_pP=O": s1_pP_is_O, "S1_points": len(pts), "subgroup_order_ell": ell,
                    "S2_no_rational_p_torsion": N % p != 0}
            lifts = [("canonical", A, B),
                     ("pert_p", (A + p * rng.randrange(1, p)) if jcm != 0 else p * rng.randrange(1, p), B + p * rng.randrange(1, p))]
            for cls, A2, B2 in lifts:
                E = ZpK(p, K, A2, B2)
                vdj = vp_frac(j_inv(A2, B2) - jcm, p)
                succ = tot = deg = 0
                flag_by_lift = []
                for sec in ("naive", "teichmuller", "hensel_random"):
                    for _ in range(60):
                        P = prime_order_point(pts, N, p, A % p)
                        n = ell
                        d = rng.randrange(2, n - 1)
                        Q = fp_mul(d, P, p, A % p)
                        Ph = E.lift(P, sec, rng.randrange(p))
                        Qh = E.lift(Q, sec, rng.randrange(p))
                        zP, zQ = E.z_mult(n, Ph), E.z_mult(n, Qh)
                        r, vP, vQ = ratio_digit(zP, zQ, p, K)
                        tot += 1
                        succ += int(r is not None and r == d % p)
                        deg += int(vP >= 2)
                    # S4: same point, three different point lifts on this curve lift
                P = prime_order_point(pts, N, p, A % p)
                n = ell
                vs = sorted({vp(E.z_mult(n, E.lift(P, "hensel_random", eps)), p, K) >= 2 for eps in range(p)})
                cell[cls] = {"v_dj": None if vdj == float("inf") else int(vdj), "rule_predicts_degenerate": vdj >= 2 * (3 if jcm == 0 else 1),
                             "samples": tot, "smart_success": succ, "success_rate_times_p": round(succ / tot * p, 2),
                             "frac_flag_v>=2": round(deg / tot, 4), "S4_flag_values_over_all_eps_for_one_point": vs}
            results.append(cell)
            print(cell, flush=True)
            count += 1
            break

agg = {}
for cls in ("canonical", "pert_p"):
    S = sum(c[cls]["smart_success"] for c in results)
    T = sum(c[cls]["samples"] for c in results)
    E0 = sum(c[cls]["samples"] / c["p"] for c in results)
    agg[cls] = {"samples": T, "successes": S, "expected_1/p": round(E0, 2),
                "S4_flag_depends_on_point_lift_on_every_curve": all(c[cls]["S4_flag_values_over_all_eps_for_one_point"] == [False, True] for c in results)}
summary = {"curves": len(results), "S1_any_pP=O": any(c["S1_points_with_pP=O"] for c in results),
           "S2_no_rational_p_torsion_all": all(c["S2_no_rational_p_torsion"] for c in results), "smart_by_class": agg}
print(json.dumps(summary, indent=1))
json.dump({"cells": results, "summary": summary}, open("rt_ptm1_output.json", "w"), indent=1)
