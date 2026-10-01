"""J5 extra (a'): coverage of A2's curve-index percentile bootstrap interval for the slope
of y_b = log2(max(kappa_b - 1, SD_null_b / C_R_b)) on a PLANTED design with a known slope.
Own simulation; the interval is computed with my sealed A2 implementation (CV-7 mechanics;
x_b fixed) from rederivation/j3_quantities.py.

Design: rungs 20..32 (7), five curves per rung, three random arms and one structured arm
per curve; curve means mu_{b,j} = 200 * 2^(0.3 (b - 20)) * exp(0.5 Z_j) (curve-to-curve
heterogeneity, shared by the four arms of a curve); structured counts Poisson(kappa_b mu),
random counts Poisson(mu); kappa_b = 1 + 0.3 * 2^(delta (x_b - 26)), delta = 0.10, so the
target slope of log2(kappa - 1) is delta (the SD floor is far below kappa - 1 here).
Coverage of delta by the nominal 95% interval, with binomial s.e.; also P(lo > 0) (the
O-ALIVE slope criterion) under delta = 0.10 and under delta = 0 (null-shaped slope; kappa
fixed at 1.3). Master seeds: random.Random('J5a2|delta=<d>')."""
import json, math, os, random, statistics, sys, time
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "rederivation"))
from j3_quantities import a2_test  # my own sealed A2 implementation


def poisson(rng, lam):
    if lam < 30:
        L, k, p = math.exp(-lam), 0, 1.0
        while True:
            p *= rng.random()
            if p <= L:
                return k
            k += 1
    # normal approximation with continuity correction for large means
    return max(0, int(round(rng.gauss(lam, math.sqrt(lam)))))


def series(rng, delta):
    cells = {}
    for b in range(20, 33, 2):
        xb = b - 0.5
        kappa = 1 + 0.3 * 2 ** (delta * (xb - 26))
        nA, nR, logN = {}, {}, {}
        for j in range(5):
            mu = 200 * 2 ** (0.3 * (b - 20)) * math.exp(0.5 * rng.gauss(0, 1))
            nA[j] = poisson(rng, kappa * mu)
            nR[j] = [poisson(rng, mu) for _ in range(3)]
            logN[j] = xb
        C_A = sum(nA.values())
        C_R = sum(sum(v) for v in nR.values()) / 3
        s2 = sum(statistics.variance(v) for v in nR.values())
        V = max(s2, C_R)
        cells[b] = {"resolved": C_R >= 10, "C_A": C_A, "C_R": C_R, "V": V, "log2N_by_curve": logN,
                    "curves_used": list(range(5)), "counts_A": [nA[j] for j in range(5)],
                    "counts_R": [nR[j] for j in range(5)]}
    return cells


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    out = {}
    t0 = time.time()
    for delta in (0.10, 0.0):
        master = random.Random(f"J5a2|delta={delta}")
        cov = lo_pos = 0
        for _ in range(n):
            rng = random.Random(master.getrandbits(64))
            res = a2_test(series(rng, delta), "all", seed=0)
            if res["lo"] <= delta <= res["hi"]:
                cov += 1
            if res["lo"] > 0:
                lo_pos += 1
        pc, pl = cov / n, lo_pos / n
        out[f"delta={delta}"] = {"coverage": pc, "coverage_se": math.sqrt(pc * (1 - pc) / n),
                                 "P_lo_gt_0": pl, "P_lo_gt_0_se": math.sqrt(pl * (1 - pl) / n), "n_series": n}
        print(delta, out[f"delta={delta}"], flush=True)
    out["_meta"] = {"seconds": round(time.time() - t0, 1), "bootstrap": "own A2 (CV-7), 2000 replicates, random.Random(0)"}
    os.makedirs(os.path.join(W, "calibration", "out"), exist_ok=True)
    json.dump(out, open(os.path.join(W, "calibration", "out", "j5-a2.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
