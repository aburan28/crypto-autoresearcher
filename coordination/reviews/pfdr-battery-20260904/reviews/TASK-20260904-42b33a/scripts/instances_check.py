"""JOINT V3 (phase A part): instance and decomposition-certificate checks with my
own arithmetic, from the parameters in params.py only.

For each declared (p, a, b, x_R):
  - a, b nonzero; 4a^3 + 27b^2 != 0 (non-singular); j-invariant reported
  - the on-curve x in the planting window [0, 4)
  - an INDEPENDENT decomposition certificate: x_R = x(P_1 + P_2) for window points
    P_1, P_2 with signs, exhibited explicitly
  - the full set of x(P_1 + P_2) over window pairs and signs (bounds the number of
    distinct generator systems a curve can contribute to a cell)
  - cross-check that the digit solution set Z of S~ equals the window pairs
"""
import json
import sys

sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/"
                   "pfdr-battery-20260904/reviews/TASK-20260904-42b33a/scripts")

from hky import semaev_S3_digit, zero_set
from params import INSTANCES, WINDOW, S_VALUES

OUT = ("/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/"
       "reviews/TASK-20260904-42b33a/tables/instance_checks.json")


def sqrt_mod(n, p):
    n %= p
    if n == 0:
        return 0
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    # Tonelli-Shanks
    q, ss = p - 1, 0
    while q % 2 == 0:
        q //= 2
        ss += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = ss, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c = i, b * b % p
        t = t * c % p
        r = r * b % p
    return r


def ec_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + a) * pow(2 * y1 % p, p - 2, p) % p
    else:
        lam = (y2 - y1) * pow((x2 - x1) % p, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def main():
    out = {"instances": [], "per_curve": {}}
    for (p, cs, a, b, ts, xR) in INSTANCES:
        disc = (4 * pow(a, 3, p) + 27 * b * b) % p
        j_num = (1728 * 4 * pow(a, 3, p)) % p
        j = j_num * pow(disc, p - 2, p) % p if disc else None
        window_pts = []
        oncurve_x = []
        for x in range(WINDOW):
            f = (pow(x, 3, p) + a * x + b) % p
            y = sqrt_mod(f, p)
            if y is None:
                continue
            oncurve_x.append(x)
            window_pts.append((x, y))
            if y != 0:
                window_pts.append((x, (p - y) % p))
        sums = {}
        for i, P in enumerate(window_pts):
            for jj, Q in enumerate(window_pts):
                S = ec_add(P, Q, a, p)
                if S is None:
                    continue
                sums.setdefault(S[0], []).append((P, Q))
        cert = None
        if xR in sums:
            P, Q = sums[xR][0]
            cert = {"P1": list(P), "P2": list(Q),
                    "x_P1": P[0], "x_P2": Q[0],
                    "n_witness_pairs": len(sums[xR])}
        rec = {
            "p": p, "curve_seed": cs, "target_seed": ts, "a": a, "b": b, "x_R": xR,
            "a_nonzero": a != 0, "b_nonzero": b != 0,
            "discriminant_4a3_27b2_mod_p": disc, "nonsingular": disc != 0,
            "j_invariant": j, "j_is_0": j == 0, "j_is_1728": j == 1728 % p,
            "oncurve_x_in_window": oncurve_x,
            "n_oncurve_x_in_window": len(oncurve_x),
            "n_window_points": len(window_pts),
            "distinct_xR_reachable": sorted(sums),
            "n_distinct_xR_reachable": len(sums),
            "xR_is_window_pair_sum": xR in sums,
            "decomposition_certificate": cert,
        }
        # cross-check the digit solution set against the window pairs, per s
        rec["digit_solutions_per_s"] = {}
        for s in S_VALUES:
            gen = semaev_S3_digit(p, a, b, xR, s)
            Z = zero_set(gen, 2 * s, p)
            pairs = sorted((z & ((1 << s) - 1), z >> s) for z in Z)
            rec["digit_solutions_per_s"][str(s)] = {
                "count": len(pairs), "pairs": pairs,
                "all_in_window": all(u < WINDOW and v < WINDOW for u, v in pairs),
            }
        key = f"p{p}_curve{cs}"
        out["per_curve"].setdefault(key, {
            "p": p, "curve_seed": cs, "a": a, "b": b,
            "oncurve_x_in_window": oncurve_x,
            "n_window_points": len(window_pts),
            "distinct_xR_reachable": sorted(sums),
            "n_distinct_xR_reachable": len(sums),
        })
        out["instances"].append(rec)
        print(f"p={p} curve={cs} target={ts} xR={xR}: nonsing={disc != 0} "
              f"oncurve_x={oncurve_x} #pts={len(window_pts)} "
              f"#distinct_xR={len(sums)} xR_is_sum={xR in sums} "
              f"digitZ={rec['digit_solutions_per_s']['5']['pairs']}")
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print("\nwrote", OUT)
    print("\nper curve, distinct reachable x_R (bound on distinct generator systems):")
    for k, v in sorted(out["per_curve"].items()):
        print(f"  {k}: {v['n_distinct_xR_reachable']} -> {v['distinct_xR_reachable']}")


if __name__ == "__main__":
    main()
