"""A6 (HEUR-4765e4-H1) -- J6(c) MC-2 alternative PIT seed family, J6(e) multiplicity of the
A6 KS family under H1, J7(c) ALT-c (E't replaced by stored table entries), and the first
moment / dispersion of the random-arm pair counts behind the H1 rejections.

Frozen A6: per (class, m) over the main-panel random arms (census), randomized PIT
u = F(n-1) + V (F(n) - F(n-1)) with V = random.Random(f"pit-1b78f7|{bits}|{c}|{m}|{arm}|{class}"),
KS against U(0, 1) over 12..32 and 20..32; H1 refuted for (class, m) if either rejects at 1%.
Seeds: alternative PIT V = random.Random(f"rt-f29c96-pit|{s}|...") for s = 1..200; H1-true
simulation numpy default_rng(20261102), 20000 replicates of iid U(0,1) PITs (exact under H1).
KS p-values: the exact Marsaglia-Tsang-Wang routine as in analyze_census.py (reimplemented
here, same asymptotic switch); in the loops the 1% decision uses D_crit(n), found once per n
by bisection on that routine.
Output: attacks/out/08_a6.json
"""
import json
import math
import os
import random
import statistics
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtlib import OUT, RANDOM_ARMS, canonical_rows, m_of, safe_analysis, usable  # noqa: E402


def poisson_cdf(n, mu):
    if n < 0:
        return 0.0
    if mu <= 0:
        return 1.0
    total, lm = 0.0, math.log(mu)
    for i in range(n + 1):
        total += math.exp(-mu + i * lm - math.lgamma(i + 1))
    return min(1.0, total)


def ks_pvalue(d, n):
    if d <= 0:
        return 1.0
    if d >= 1:
        return 0.0
    if n > 400 or n * d > 60:
        lam = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * d
        return max(0.0, min(1.0, 2 * sum((-1) ** (j - 1) * math.exp(-2 * j * j * lam * lam) for j in range(1, 101))))
    k = int(n * d) + 1
    m = 2 * k - 1
    h = k - n * d
    H = [[1.0 if i - j + 1 >= 0 else 0.0 for j in range(m)] for i in range(m)]
    for i in range(m):
        H[i][0] -= h ** (i + 1)
        H[m - 1][i] -= h ** (m - i)
    H[m - 1][0] += (2 * h - 1) ** m if 2 * h - 1 > 0 else 0.0
    for i in range(m):
        for j in range(m):
            if i - j + 1 > 0:
                for g in range(1, i - j + 2):
                    H[i][j] /= g

    def mm(A, B):
        return [[sum(A[i][t] * B[t][j] for t in range(m)) for j in range(m)] for i in range(m)]

    def mp(A, e):
        if e == 1:
            return [r[:] for r in A], 0
        V, eV = mp(A, e // 2)
        B = mm(V, V)
        eB = 2 * eV
        if e % 2:
            B = mm(A, B)
        if B[k - 1][k - 1] > 1e140:
            B = [[x * 1e-140 for x in r] for r in B]
            eB += 140
        return B, eB

    Q, eQ = mp(H, n)
    s = Q[k - 1][k - 1]
    for i in range(1, n + 1):
        s = s * i / n
        if s < 1e-140:
            s *= 1e140
            eQ -= 140
    return max(0.0, min(1.0, 1.0 - s * 10.0 ** eQ))


def ks_D(us):
    xs = np.sort(np.asarray(us))
    n = len(xs)
    i = np.arange(n)
    return float(max(((i + 1) / n - xs).max(), (xs - i / n).max()))


def d_crit(n, alpha=0.01):
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if ks_pvalue(mid, n) < alpha:
            hi = mid
        else:
            lo = mid
    return hi


def main():
    rows = canonical_rows("census-m3") + canonical_rows("census-m4") + canonical_rows("census-m5")
    inst = defaultdict(list)   # (class, m) -> list of dicts
    for r in rows:
        if r.get("arm") not in RANDOM_ARMS or r.get("mode") != "census" or not usable(r):
            continue
        m = m_of(r)
        h = r["harvest"]
        for c in ("TT", "TB", "SS"):
            if c == "SS":
                n, mu = h["SS"]["at_A_fix"]["pairs_nonformal"], h["SS"]["at_A_fix"]["poisson_mean"]
            else:
                n, mu = h[c]["at_stop"]["pairs_nonformal"], h[c]["at_stop"]["poisson_mean"]
            E = h["table"]["entries"]
            mu_alt = (E * (E - 1) / 2 * 2 / r["N"] if c == "TT" else E * r["fb_size"] * 2 / r["N"] if c == "TB" else mu)
            inst[(c, m)].append({"bits": r["bits"], "curve": r["curve"], "arm": r["arm"], "n": n, "mu": mu,
                                 "mu_alt": mu_alt})
    an = safe_analysis()["A6_poisson"]
    out = {"per_class_m": {}}
    Dc = {}

    def pit(recs, vfun, key="mu"):
        u_all, u_hi = [], []
        for x in recs:
            V = vfun(x)
            F1, F0 = x["F_" + key]
            u = F0 + V * (F1 - F0)
            u_all.append(u)
            if 20 <= x["bits"] <= 32:
                u_hi.append(u)
        return u_all, u_hi

    for recs in inst.values():
        for x in recs:
            for key in ("mu", "mu_alt"):
                x["F_" + key] = (poisson_cdf(x["n"], x[key]), poisson_cdf(x["n"] - 1, x[key]))

    for (c, m), recs in sorted(inst.items(), key=str):
        frozen_v = lambda x, c=c, m=m: random.Random(f"pit-1b78f7|{x['bits']}|{x['curve']}|{m}|{x['arm']}|{c}").random()
        ua, uh = pit(recs, frozen_v)
        for nn in (len(ua), len(uh)):
            if nn not in Dc:
                Dc[nn] = d_crit(nn)
        Da, Dh = ks_D(ua), ks_D(uh)
        pa, ph = ks_pvalue(Da, len(ua)), ks_pvalue(Dh, len(uh))
        arch = an[f"{c}|{m}"]
        rej = (pa < 0.01) or (ph < 0.01)
        # alternative PIT seed family
        flips = 0
        rej_alt = 0
        for s in range(1, 201):
            v2 = lambda x, s=s, c=c, m=m: random.Random(f"rt-f29c96-pit|{s}|{x['bits']}|{x['curve']}|{m}|{x['arm']}|{c}").random()
            a2, h2 = pit(recs, v2)
            r2 = ks_D(a2) > Dc[len(a2)] or ks_D(h2) > Dc[len(h2)]
            rej_alt += r2
            flips += r2 != rej
        # ALT-c
        ua_c, uh_c = pit(recs, frozen_v, key="mu_alt")
        pa_c, ph_c = ks_pvalue(ks_D(ua_c), len(ua_c)), ks_pvalue(ks_D(uh_c), len(uh_c))
        ns = [x["n"] for x in recs]
        mus = [x["mu"] for x in recs]
        out["per_class_m"][f"{c}|{m}"] = {
            "n_instances_12_32": len(ua), "n_instances_20_32": len(uh),
            "frozen_p_12_32": pa, "frozen_p_20_32": ph,
            "archived_p_12_32": arch["ks_12_32"]["p"], "archived_p_20_32": arch["ks_20_32"]["p"],
            "frozen_reject_1pct": rej,
            "altPIT_reject_fraction_200_seeds": rej_alt / 200, "altPIT_flip_fraction": flips / 200,
            "ALT_c_p_12_32": pa_c, "ALT_c_p_20_32": ph_c, "ALT_c_reject_1pct": (pa_c < 0.01) or (ph_c < 0.01),
            "first_moment_sum_n_over_sum_mu": sum(ns) / sum(mus) if sum(mus) > 0 else None,
            "index_of_dispersion_sum_(n-mu)^2_over_sum_mu": sum((a - b) ** 2 for a, b in zip(ns, mus)) / sum(mus) if sum(mus) > 0 else None}
        print(c, m, out["per_class_m"][f"{c}|{m}"], file=sys.stderr)
    # FWER of the A6 family under H1 true.  Under H1 the randomized PIT is exactly U(0, 1)
    # whatever mu is, so the family is simulated with iid uniforms on the actual (class, m)
    # instance counts and 20..32 subsets (classes treated as independent, as H1 states).
    rng = np.random.default_rng(20261102)
    R = 20000
    fam_rej = np.zeros(R, dtype=int)
    for (c, m), recs in sorted(inst.items(), key=str):
        hi = np.array([20 <= x["bits"] <= 32 for x in recs])
        n_all, n_hi = len(recs), int(hi.sum())
        U = rng.random((R, n_all))
        for r in range(R):
            u = U[r]
            fam_rej[r] += (ks_D(u) > Dc[n_all]) or (ks_D(u[hi]) > Dc[n_hi])
    out["FWER_under_H1"] = {"tests": "9 (class, m) x 2 ranges; a (class, m) is rejected if either range rejects at 1%",
                            "P_at_least_one_class_m_rejected": float((fam_rej >= 1).mean()),
                            "E_rejected_class_m": float(fam_rej.mean()),
                            "P_ge_6_rejected": float((fam_rej >= 6).mean()), "R": R,
                            "observed_rejected": sorted(k for k, v in out["per_class_m"].items() if v["frozen_reject_1pct"])}
    out["D_crit_1pct"] = {str(k): v for k, v in Dc.items()}
    with open(os.path.join(OUT, "out", "08_a6.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out["FWER_under_H1"]), file=sys.stderr)


if __name__ == "__main__":
    main()
