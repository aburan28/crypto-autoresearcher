"""J3 Q9 (part 1): A6 HEUR-4765e4-H1 randomized-PIT KS per (class, m) over 12..32 and
20..32, with the frozen PIT seeds, and the per-rung max-count tail check.
Conventions: rederivation/conventions.yaml CV-18. Own implementations of the Poisson
CDF (regularized incomplete gamma) and of the exact Kolmogorov distribution
(Marsaglia, Tsang and Wang 2003 -- recalled, own code). No scipy."""
import collections, gzip, json, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RUNS, RUN, OUT, read_jsonl_gz, row_m, is_rho, dump, rl

RANDOM_ARMS = ["random_sub_r0", "random_sub_r1", "random_sub_r2",
               "random_dick_r0", "random_dick_r1", "random_dick_r2"]


def gammq(a, x):
    """Upper regularized incomplete gamma Q(a, x) (Numerical Recipes gser/gcf)."""
    if x <= 0:
        return 1.0
    gln = math.lgamma(a)
    if x < a + 1.0:
        ap, s, d = a, 1.0 / a, 1.0 / a
        for _ in range(100000):
            ap += 1.0
            d *= x / ap
            s += d
            if abs(d) < abs(s) * 1e-15:
                break
        return 1.0 - s * math.exp(-x + a * math.log(x) - gln)
    b = x + 1.0 - a
    c = 1.0 / 1e-300
    d = 1.0 / b
    hh = d
    for i in range(1, 100000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < 1e-300:
            d = 1e-300
        c = b + an / c
        if abs(c) < 1e-300:
            c = 1e-300
        d = 1.0 / d
        de = d * c
        hh *= de
        if abs(de - 1.0) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - gln) * hh


def pois_cdf(n, mu):
    if n < 0:
        return 0.0
    if mu <= 0:
        return 1.0
    return gammq(n + 1.0, mu)


def kolmogorov_cdf(n, d):
    """P(D_n < d), Marsaglia-Tsang-Wang exact algorithm (matrix power)."""
    k = int(n * d) + 1
    m = 2 * k - 1
    hh = k - n * d
    H = [[0.0] * m for _ in range(m)]
    for i in range(m):
        for j in range(m):
            if i - j + 1 >= 0:
                H[i][j] = 1.0
    for i in range(m):
        H[i][0] -= hh ** (i + 1)
        H[m - 1][i] -= hh ** (m - i)
    H[m - 1][0] += (2 * hh - 1) ** m if 2 * hh - 1 > 0 else 0.0
    for i in range(m):
        for j in range(m):
            if i - j + 1 > 0:
                for g in range(1, i - j + 2):
                    H[i][j] /= g

    def mmul(A, B):
        return [[sum(A[i][t] * B[t][j] for t in range(m)) for j in range(m)] for i in range(m)]

    def mpow(A, e):
        # returns (matrix, exponent-of-1e140 scaling)
        if e == 1:
            return [row[:] for row in A], 0
        V, eV = mpow(A, e // 2)
        B = mmul(V, V)
        eB = 2 * eV
        if e % 2 == 1:
            B = mmul(A, B)
        if B[k - 1][k - 1] > 1e140:
            B = [[x * 1e-140 for x in row] for row in B]
            eB += 140
        return B, eB

    Q, eQ = mpow(H, n)
    s = Q[k - 1][k - 1]
    for i in range(1, n + 1):
        s = s * i / n
        if s < 1e-140:
            s *= 1e140
            eQ -= 140
    return s * 10.0 ** eQ


def ks_test(us):
    n = len(us)
    s = sorted(us)
    d = 0.0
    for i, u in enumerate(s):
        d = max(d, (i + 1) / n - u, u - i / n)
    p = 1.0 - kolmogorov_cdf(n, d)
    return d, max(0.0, min(1.0, p))


def main():
    rows = read_jsonl_gz(os.path.join(RUNS, RUN["R10"], "rows.jsonl.gz"), "Q9/A6 input: R10 root rows")
    for lab in ["R11", "R12"]:
        p = os.path.join(OUT, f"canonical-{lab}-rows.jsonl.gz")
        rl.opened(p, f"Q9/A6 input: my own J2a canonical {lab} rows")
        with gzip.open(p, "rt") as f:
            rows += [json.loads(l) for l in f if l.strip()]
    data = collections.defaultdict(list)
    excluded = []
    for r in rows:
        if is_rho(r) or r.get("mode") != "census" or r.get("arm") not in RANDOM_ARMS:
            continue
        m = row_m(r)
        if r.get("status") != "completed_valid":
            excluded.append([r["bits"], r["curve"], m, r["arm"], "status"])
            continue
        hb = r["harvest"]
        for cls in ["TT", "TB", "SS"]:
            if cls == "SS":
                if hb["SS"]["at_A_fix"]["censored"]:
                    excluded.append([r["bits"], r["curve"], m, r["arm"], "SS censored"])
                    continue
                mu = hb["SS"]["at_A_fix"]["poisson_mean"]
                n = hb["SS"]["at_A_fix"]["pairs_nonformal"]
            else:
                mu = hb[cls]["at_stop"]["poisson_mean"]
                n = hb[cls]["at_stop"]["pairs_nonformal"]
            V = random.Random(f"pit-1b78f7|{r['bits']}|{r['curve']}|{m}|{r['arm']}|{cls}").random()
            F1, F0 = pois_cdf(n, mu), pois_cdf(n - 1, mu)
            u = F0 + V * (F1 - F0)
            data[(cls, m)].append({"bits": r["bits"], "curve": r["curve"], "arm": r["arm"], "u": u, "n": n, "mu": mu})
    out = {"ks": {}, "tail": {}, "excluded": excluded}
    for (cls, m), lst in sorted(data.items()):
        for lo in (12, 20):
            us = [x["u"] for x in lst if x["bits"] >= lo]
            d, p = ks_test(us)
            out["ks"][f"{cls}|m{m}|{lo}..32"] = {"n": len(us), "D": d, "p": p, "reject_1pct": p < 0.01}
        byb = collections.defaultdict(list)
        for x in lst:
            byb[x["bits"]].append(x)
        for b, xs in sorted(byb.items()):
            mx = max(x["n"] for x in xs)
            prod = 1.0
            for x in xs:
                prod *= pois_cdf(mx - 1, x["mu"])
            pt = 1.0 - prod
            out["tail"][f"{cls}|m{m}|b{b}"] = {"instances": len(xs), "max_count": mx, "P_max_ge": pt, "flag_lt_0.001": pt < 0.001}
    # self-checks of the numerical routines (known values)
    out["selfcheck"] = {"pois_cdf(3,2.5)": pois_cdf(3, 2.5),
                        "kolmogorov_cdf(10,0.274)": kolmogorov_cdf(10, 0.274)}
    dump("q9-a6.json", out)
    for k, v in out["ks"].items():
        print("KS", k, v)
    print("tail flags:", {k: v["P_max_ge"] for k, v in out["tail"].items() if v["flag_lt_0.001"]})
    print("selfcheck", out["selfcheck"], "excluded", len(excluded))


if __name__ == "__main__":
    main()
