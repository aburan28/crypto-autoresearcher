"""EXP-CZLIFT-1a3453 driver: discrete-log spectrum of the torsion section's digits.

For each curve of the EXP-CZLIFT-ae0a13 family (CM-canonical lifts and
arbitrary integer lifts of random curves, prime subgroup <P> of order n != p)
compute the canonical torsion lift s_tor([k]P) for every k in Z/n at precision
PRECISION, read the p-adic digits a_i(k) of x(s_tor([k]P)) and y(s_tor([k]P))
(digit 0 is the F_p coordinate itself, the control), and for every nontrivial
additive character psi of F_p and every character chi of Z/n form

    S(psi, chi; f) = sum_k psi(f(k)) chi(k),   f = a digit function.

The sums run over the half-range k = 1..(n-1)/2 (negation makes the full
range redundant for x and real-valued for y). Under the null (digits
independent of the discrete log k) |S|^2/n_half is close to Exp(1) for each
pair, and the maximum over the N = (p-1) n pairs of a digit is about
ln N + Gumbel. The driver records, per curve and digit, the maximum
of |S|^2/n, the count of pairs above the pre-registered spike threshold
ln N + SPIKE_MARGIN, and the same statistics for a shuffled-digit control
(the same digit values re-indexed by a seeded permutation of k) and for a
synthetic uniform-digit control. Observations only; nothing is decided here.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from harness import czlift  # noqa: E402
from harness.czlift import ZpCurve  # noqa: E402
from harness.czlift_run import write_run_record  # noqa: E402
from harness.toycurve import EllipticCurve  # noqa: E402

EXP_ID = "EXP-CZLIFT-1a3453"
PRECISION = 5
SPIKE_MARGIN = 12.0
PRIMES_RANDOM_ARM = (53, 71, 101, 131, 173, 211, 263, 307, 367, 421, 487, 557)


def digits(v: int, p: int, k: int) -> list[int]:
    out = []
    for _ in range(k):
        out.append(v % p)
        v //= p
    return out


def spectrum(f: np.ndarray, p: int, n: int) -> tuple[float, int, float]:
    """max |S|^2/n_half over psi != 1 and all chi; count above threshold; threshold.

    The sum runs over the HALF-RANGE k = 1 .. (n-1)/2 only. Negation gives
    x(-R) = x(R) and y(-R) = -y(R), so a full-range sum is redundant (x) or
    real-valued (y, a chi-square with one degree of freedom instead of an
    exponential); on the half-range both coordinates have the complex-Gaussian
    null |S|^2/n_half ~ Exp(1) per (psi, chi) pair.
    """
    half = (n - 1) // 2
    N = (p - 1) * n
    threshold = math.log(N) + SPIKE_MARGIN
    best = 0.0
    above = 0
    base = np.exp(2j * np.pi * f[1:half + 1].astype(np.float64) / p)
    cur = np.ones(half, dtype=np.complex128)
    vec = np.zeros(n, dtype=np.complex128)
    for _ in range(1, p):
        cur = cur * base  # psi_t(f) = e(t f / p)
        vec[1:half + 1] = cur
        power = np.abs(np.fft.fft(vec)) ** 2 / half
        m = float(power.max())
        best = max(best, m)
        above += int((power > threshold).sum())
    return best, above, threshold


def measure_curve(arm: str, p: int, A: int, B: int, N: int, n: int, *, seed: int, label: str) -> dict:
    rng = random.Random(seed * 104_729 + p * 17 + (A % p))
    Efp = EllipticCurve(p, A % p, B % p)
    assert Efp.order() == N and N % n == 0 and n != p and N % 2 == 1
    h = N // n
    E = ZpCurve(p, PRECISION, A, B)
    P = czlift.point_of_order(Efp, n, h, rng)
    # torsion lifts of every multiple, x and y digits
    xs = np.zeros((PRECISION, n), dtype=np.int64)
    ys = np.zeros((PRECISION, n), dtype=np.int64)
    R = None
    for k in range(n):
        if k == 0:
            continue  # O has no affine coordinates; digit functions skip k = 0 (value 0)
        R = Efp.add(R, P) if R is not None else P
        Rh = E.hensel_lift(R[0], R[1], eps=rng.randrange(p))
        T, _ = E.torsion_section(Rh, n)
        aff = E.affine(T)
        assert aff is not None and E.reduce(T) == R
        for i, d in enumerate(digits(aff[0], p, PRECISION)):
            xs[i, k] = d
        for i, d in enumerate(digits(aff[1], p, PRECISION)):
            ys[i, k] = d
    perm = np.array(rng.sample(range(n), n))
    rows = []
    for coord, arr in (("x", xs), ("y", ys)):
        for i in range(PRECISION):
            best, above, thr = spectrum(arr[i], p, n)
            sh_best, sh_above, _ = spectrum(arr[i][perm], p, n)
            uni = np.array([rng.randrange(p) for _ in range(n)], dtype=np.int64)
            un_best, un_above, _ = spectrum(uni, p, n)
            rows.append({"coord": coord, "digit": i, "max_power": best, "above": above,
                         "threshold": thr, "shuffled_max_power": sh_best, "shuffled_above": sh_above,
                         "uniform_max_power": un_best, "uniform_above": un_above})
    return {"arm": arm, "label": label, "p": p, "A": A, "B": B, "N": N, "n": n,
            "precision": PRECISION, "rows": rows}


def summarize(curves: list[dict]) -> dict:
    out = {"curves": len(curves), "by_digit": {}, "spikes_total": 0, "spikes_digit0": 0,
           "spikes_higher_digits": 0, "shuffled_spikes_total": 0, "uniform_spikes_total": 0,
           "max_excess_over_threshold_higher_digits": None, "max_excess_shuffled": None}
    exc_h = []
    exc_s = []
    for c in curves:
        for r in c["rows"]:
            key = f"{r['coord']}{r['digit']}"
            d = out["by_digit"].setdefault(key, {"n": 0, "above": 0, "max_power_mean": 0.0,
                                                 "threshold_mean": 0.0, "shuffled_above": 0, "uniform_above": 0})
            d["n"] += 1
            d["above"] += r["above"]
            d["max_power_mean"] += r["max_power"]
            d["threshold_mean"] += r["threshold"]
            d["shuffled_above"] += r["shuffled_above"]
            d["uniform_above"] += r["uniform_above"]
            out["spikes_total"] += r["above"]
            out["shuffled_spikes_total"] += r["shuffled_above"]
            out["uniform_spikes_total"] += r["uniform_above"]
            if r["digit"] == 0:
                out["spikes_digit0"] += r["above"]
            else:
                out["spikes_higher_digits"] += r["above"]
                exc_h.append(r["max_power"] - r["threshold"])
            exc_s.append(r["shuffled_max_power"] - r["threshold"])
    for d in out["by_digit"].values():
        d["max_power_mean"] /= d["n"]
        d["threshold_mean"] /= d["n"]
    out["max_excess_over_threshold_higher_digits"] = max(exc_h) if exc_h else None
    out["max_excess_shuffled"] = max(exc_s) if exc_s else None
    return out


def build(seed: int, pmax: int, max_cm: int) -> tuple[dict, dict]:
    rng = random.Random(seed)
    cm = czlift.cm_curves_with_prime_subgroup(50, pmax, 11)
    rng.shuffle(cm)
    cm = sorted(cm[:max_cm])
    rand = czlift.random_curves_with_prime_subgroup([q for q in PRIMES_RANDOM_ARM if q <= pmax],
                                                    11, random.Random(seed + 1))
    curves = [measure_curve("cm_canonical", p, A, B, N, n, seed=seed, label=f"D={D}")
              for D, p, A, B, N, n in cm]
    curves += [measure_curve("random_naive", p, a, b, N, n, seed=seed, label="random")
               for p, a, b, N, n in rand]
    metrics = summarize(curves)
    metrics.update({"seed": seed, "pmax": pmax, "precision": PRECISION, "spike_margin": SPIKE_MARGIN,
                    "curves_cm": len(cm), "curves_random": len(rand)})
    return metrics, {"curves": curves}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--pmax", type=int, default=600)
    ap.add_argument("--max-cm", type=int, default=24)
    args = ap.parse_args(argv)
    t0 = time.time()
    metrics, raw = build(args.seed, args.pmax, args.max_cm)
    t1 = time.time()
    sources = [os.path.abspath(__file__), os.path.join(REPO, "harness", "czlift.py"),
               os.path.join(REPO, "harness", "czlift_run.py"), os.path.join(REPO, "harness", "toycurve.py")]
    write_run_record(args.run_dir, run_id=args.run_id, exp_id=EXP_ID, status="completed_valid",
                     command=[sys.executable] + sys.argv, sources=sources, seed=args.seed,
                     parameters={"pmax": args.pmax, "max_cm": args.max_cm, "precision": PRECISION,
                                 "spike_margin": SPIKE_MARGIN, "tier": "toy"},
                     metrics=metrics, raw=raw, started=t0, finished=t1,
                     stdout=json.dumps(metrics, indent=1) + "\n")
    print(json.dumps({k: v for k, v in metrics.items() if k != "by_digit"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
