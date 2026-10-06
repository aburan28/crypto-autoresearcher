"""J5 -- interval calibration at five curves per rung (MC-5), own simulation code.
Uses no blind_from path and no Stage 0 review material. stats.py is loaded by file
path and used with its frozen settings (reps=2000, level=0.95, seed=0).

(a) stats.bootstrap_slope on synthetic series, 11 rungs x 5 curves (bits 12..32) and
    7 rungs x 5 curves (bits 20..32 and 12..24), known slope, residuals (i) Gaussian,
    (ii) Student-t with 3 d.o.f. scaled to the same variance. x = log2 N drawn as
    bits - 1 + U(0,1) per curve (as log2 N of a bits-bit prime-order curve), groups =
    bits. Coverage of the nominal 95% interval, one-sided miss rates, binomial s.e.
(b) A4: stats.fit_exponent over 12..32, five instances per rung, and the paired
    bootstrap of delta (my CV-11 implementation, identical to the one used in J3), on
    paired synthetic designs with known exponent and delta = 0 (shared instance effect
    plus mode-specific noise). Coverage; P(hi < truth); P(hi < truth + 0.03);
    P(|delta_hat| <= 0.03).
(c) See calibration/derivation-note.md for the (n-1)/n deflation; the predicted
    coverages are computed here too.
Master seeds are declared per configuration (random.Random(<label>)); every synthetic
series draws from its own seeded stream. Usage: python j5_calibration.py <part> <nseries>"""
import hashlib, importlib.util, json, math, os, random, statistics, sys, time

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-census-a32e70808"
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa: E402

OUTD = os.path.join(W, "calibration", "out")
os.makedirs(OUTD, exist_ok=True)


def load_stats():
    path = os.path.join(WT, "src", "crypto_autoresearcher", "index_calculus", "stats.py")
    rl.opened(path, "J5: frozen stats.py loaded by file path")
    spec = importlib.util.spec_from_file_location("stats_frozen_j5", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def t3(rng):
    # Student-t with 3 d.o.f., scaled to unit variance (var of t3 = 3)
    z = rng.gauss(0, 1)
    c = sum(rng.gauss(0, 1) ** 2 for _ in range(3))
    return (z / math.sqrt(c / 3)) / math.sqrt(3)


def noise(rng, law, sigma):
    return sigma * (rng.gauss(0, 1) if law == "gauss" else t3(rng))


def binom(k, n):
    p = k / n
    return {"k": k, "n": n, "rate": p, "se": math.sqrt(p * (1 - p) / n)}


def part_a(stats, nseries):
    out = {}
    designs = {"11x5_12..32": list(range(12, 33, 2)), "7x5_20..32": list(range(20, 33, 2)),
               "7x5_12..24": list(range(12, 25, 2))}
    beta, sigma = 0.6, 0.3
    for dname, bits in designs.items():
        for law in ("gauss", "t3"):
            label = f"J5a|{dname}|{law}"
            master = random.Random(label)
            cover = miss_lo = miss_hi = 0
            widths = []
            for s in range(nseries):
                rng = random.Random(master.getrandbits(64))
                xs, ys, gs = [], [], []
                for b in bits:
                    for _ in range(5):
                        x = b - 1 + rng.random()
                        xs.append(x)
                        ys.append(1.0 + beta * x + noise(rng, law, sigma))
                        gs.append(b)
                r = stats.bootstrap_slope(xs, ys, gs)  # frozen: reps 2000, level 0.95, seed 0
                if r["lo"] <= beta <= r["hi"]:
                    cover += 1
                elif r["hi"] < beta:
                    miss_hi += 1
                else:
                    miss_lo += 1
                widths.append(r["hi"] - r["lo"])
            out[label] = {"coverage": binom(cover, nseries), "P_hi_lt_truth": binom(miss_hi, nseries),
                          "P_lo_gt_truth": binom(miss_lo, nseries), "median_width": statistics.median(widths),
                          "beta": beta, "sigma": sigma, "master_seed": label, "bootstrap": "stats.bootstrap_slope reps=2000 level=0.95 seed=0"}
            print(label, out[label]["coverage"], flush=True)
    return out


def paired_delta(ps, seed=0, reps=2000):
    import collections
    strata = collections.OrderedDict()
    for i, p in enumerate(ps):
        strata.setdefault(p["bits"], []).append(i)
    xs = [p["log2N"] for p in ps]
    yc = [math.log2(p["s3_census"]) for p in ps]
    yo = [math.log2(p["s3_on"]) for p in ps]
    rng = random.Random(seed)
    boots = []

    def ols(x, y):
        mx, my = sum(x) / len(x), sum(y) / len(y)
        sxx = sum((a - mx) ** 2 for a in x)
        return sum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx

    for _ in range(reps):
        idx = [rng.choice(members) for members in strata.values() for _ in members]
        xi = [xs[i] for i in idx]
        boots.append(ols(xi, [yo[i] for i in idx]) - ols(xi, [yc[i] for i in idx]))
    boots.sort()
    n = len(boots)
    return boots[int(math.floor(0.025 * (n - 1)))], boots[int(math.ceil(0.975 * (n - 1)))]


def part_b(stats, nseries):
    out = {}
    bits = list(range(12, 33, 2))
    theta = 0.62
    for law in ("gauss", "t3"):
        for per_rung in (5,):
            label = f"J5b|11x{per_rung}|{law}"
            master = random.Random(label)
            c_cov = c_hi = c_lo = c_hi03 = 0
            d_cov = d_hi = d_lo = d_hi03 = d_pt = 0
            for s in range(nseries):
                rng = random.Random(master.getrandbits(64))
                ps = []
                for b in bits:
                    for j in range(per_rung):
                        x = b - 1 + rng.random()
                        u = noise(rng, law, 0.25)      # shared instance effect (curve/target)
                        ec = noise(rng, law, 0.15)
                        eo = noise(rng, law, 0.15)
                        yc = 2.0 + theta * x + u + ec
                        yo = 1.0 + theta * x + u + eo  # delta = 0
                        ps.append({"bits": b, "log2N": x, "s3_census": 2 ** yc, "s3_on": 2 ** yo})
                rows = [{"bits": p["bits"], "log2N": p["log2N"], "s3_solves": p["s3_on"]} for p in ps]
                f = stats.fit_exponent(rows, "s3_solves")
                rowc = [{"bits": p["bits"], "log2N": p["log2N"], "s3_solves": p["s3_census"]} for p in ps]
                fc = stats.fit_exponent(rowc, "s3_solves")
                if f["lo"] <= theta <= f["hi"]:
                    c_cov += 1
                elif f["hi"] < theta:
                    c_hi += 1
                else:
                    c_lo += 1
                if f["hi"] < theta + 0.03:
                    c_hi03 += 1
                lo, hi = paired_delta(ps, seed=0)
                if lo <= 0 <= hi:
                    d_cov += 1
                elif hi < 0:
                    d_hi += 1
                else:
                    d_lo += 1
                if hi < 0.03:
                    d_hi03 += 1
                if abs(f["slope"] - fc["slope"]) <= 0.03:
                    d_pt += 1
            out[label] = {"exponent_on": {"coverage": binom(c_cov, nseries), "P_hi_lt_truth": binom(c_hi, nseries),
                                          "P_lo_gt_truth": binom(c_lo, nseries), "P_hi_lt_truth_plus_0.03": binom(c_hi03, nseries)},
                          "delta_paired": {"coverage": binom(d_cov, nseries), "P_hi_lt_0": binom(d_hi, nseries),
                                           "P_lo_gt_0": binom(d_lo, nseries), "P_hi_lt_0.03": binom(d_hi03, nseries),
                                           "P_abs_delta_hat_le_0.03": binom(d_pt, nseries)},
                          "theta": theta, "noise": "shared u sd 0.25, mode e sd 0.15 (" + law + ")", "master_seed": label}
            print(label, out[label]["exponent_on"]["coverage"], out[label]["delta_paired"]["coverage"], flush=True)
    return out


def predicted():
    # normal-theory prediction of percentile-bootstrap coverage with (n-1)/n deflation:
    # z_eff = 1.96 * sqrt((n-1)/n); coverage ~ P(|T_df| <= z_eff)
    def t_cdf(t, df):
        # regularized incomplete beta via continued fraction (own code)
        x = df / (df + t * t)
        a, b = df / 2.0, 0.5

        def betacf(a, b, x):
            qab, qap, qam = a + b, a + 1, a - 1
            c, d = 1.0, 1 - qab * x / qap
            d = 1 / d
            h = d
            for m in range(1, 300):
                m2 = 2 * m
                aa = m * (b - m) * x / ((qam + m2) * (a + m2))
                d = 1 + aa * d; c = 1 + aa / c; d = 1 / d; h *= d * c
                aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
                d = 1 + aa * d; c = 1 + aa / c; d = 1 / d
                de = d * c
                h *= de
                if abs(de - 1) < 1e-14:
                    break
            return h
        bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
        ib = bt * betacf(a, b, x) / a
        return 1 - 0.5 * ib if t > 0 else 0.5 * ib
    out = {}
    for n in (5, 15):
        z = 1.959964 * math.sqrt((n - 1) / n)
        out[f"n_per_stratum={n}"] = {"z_eff": z, "normal_known_var": 2 * (0.5 * math.erfc(-z / math.sqrt(2))) - 1}
        for df in (28, 44, 154):
            out[f"n_per_stratum={n}"][f"t_df{df}"] = 2 * t_cdf(z, df) - 1
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    nser = int(sys.argv[2])
    stats = load_stats()
    t0 = time.time()
    if part == "a":
        res = part_a(stats, nser)
    elif part == "b":
        res = part_b(stats, nser)
    else:
        res = predicted()
    res["_meta"] = {"part": part, "nseries": nser, "seconds": round(time.time() - t0, 1),
                    "script_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest()}
    with open(os.path.join(OUTD, f"j5-{part}.json"), "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
    print("done", part, res["_meta"])
