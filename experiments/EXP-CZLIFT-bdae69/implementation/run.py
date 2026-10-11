"""EXP-CZLIFT-bdae69 driver: the multiplicative-group calibration.

For primes p in a seeded sample, the group F_p^* with generator g and the
exact sequence 1 -> 1 + p Z_p -> Z_p^* -> F_p^* -> 1 is the controlling
example of a p-adic lift that is known not to help the discrete logarithm.
Sections of Z_p^* -> F_p^* measured here (precision k):

  teichmuller : omega(x) = lim x^{p^m}, the unique homomorphic section (image
                mu_{p-1}); log_p(omega(x)) = 0.
  naive       : the integer x in [1, p-1];
  hensel      : x + p * eps with random eps;
and the "Smart-style" ratio log_p(s(g^d)^{p-1}) / log_p(s(g)^{p-1}) read at
its first nonzero digit (log_p(u) for u in 1 + pZ_p via the series, to
precision k; u^{p-1} lands in 1 + p Z_p for any unit u). Records per
section: homomorphism rate s(xy) = s(x) s(y), vanishing rate of the
functional on the section, and success rate of the ratio against d mod p
with the 1/p reference. Same statistic as EXP-CZLIFT-ae0a13 with E replaced
by G_m. Observations only.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time

import sympy

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from harness.czlift import teichmuller, val_p  # noqa: E402
from harness.czlift_run import write_run_record  # noqa: E402

EXP_ID = "EXP-CZLIFT-bdae69"
PRECISION = 4


def log1p_padic(u: int, p: int, k: int) -> int:
    """log_p(u) mod p^k for u = 1 mod p, by the series on t = u - 1 (v(t) >= 1)."""
    M = p ** k
    t = (u - 1) % M
    assert t % p == 0
    out = 0
    tm = 1
    # terms t^m / m: valuation >= m - v_p(m) >= k once m >= k + 1 for m < p; include m up to k + 2 safely
    for m in range(1, k + 3):
        tm = tm * t % (M * p ** 3)
        if m % p == 0:
            # t^m / m has a p in the denominator; v(t^m) >= m >= p > k, so the term is 0 mod p^k for m < 2p
            continue
        sign = 1 if m % 2 == 1 else -1
        out = (out + sign * tm * pow(m, -1, M)) % M
    return out % M


def functional(u: int, p: int, k: int) -> int:
    """log_p(u^{p-1}) mod p^k for any unit u mod p^k."""
    M = p ** k
    return log1p_padic(pow(u, p - 1, M), p, k)


def section(kind: str, x: int, p: int, k: int, rng: random.Random) -> int:
    M = p ** k
    if kind == "teichmuller":
        return teichmuller(x, p, k)
    if kind == "naive":
        return x % p
    if kind == "hensel":
        return (x % p + p * rng.randrange(M // p)) % M
    raise ValueError(kind)


def measure_prime(p: int, *, seed: int, samples: int) -> dict:
    rng = random.Random(seed * 65_537 + p)
    k = PRECISION
    M = p ** k
    g = int(sympy.primitive_root(p))
    rows = []
    for _ in range(samples):
        d = rng.randrange(2, p - 2)
        x = pow(g, rng.randrange(1, p - 1), p)
        y = pow(g, rng.randrange(1, p - 1), p)
        row = {"d": d, "sections": {}}
        for kind in ("teichmuller", "naive", "hensel"):
            s_g = section(kind, g, p, k, rng)
            s_gd = section(kind, pow(g, d, p), p, k, rng)
            s_x, s_y, s_xy = section(kind, x, p, k, rng), section(kind, y, p, k, rng), section(kind, x * y % p, p, k, rng)
            fg, fgd = functional(s_g, p, k), functional(s_gd, p, k)
            vg, vgd = val_p(fg, p, k), val_p(fgd, p, k)
            if vg >= k or vgd < vg:
                ratio = None
            elif vgd > vg:
                ratio = 0
            else:
                ratio = (fgd // p ** vgd) * pow((fg // p ** vg) % p, -1, p) % p
            row["sections"][kind] = {
                "hom": s_xy == s_x * s_y % M,
                "functional_vanishes": fg % M == 0,
                "v_functional": vg,
                "ratio_defined": ratio is not None,
                "success": ratio is not None and ratio == d % p,
            }
        rows.append(row)
    return {"p": p, "generator": g, "precision": k, "rows": rows}


def summarize(primes: list[dict]) -> dict:
    out = {}
    for kind in ("teichmuller", "naive", "hensel"):
        n = hom = van = defined = succ = 0
        inv = 0.0
        for pr in primes:
            for r in pr["rows"]:
                s = r["sections"][kind]
                n += 1; hom += s["hom"]; van += s["functional_vanishes"]; defined += s["ratio_defined"]; succ += s["success"]
                inv += 1.0 / pr["p"]
        ref = inv / n
        rate = succ / n
        sigma = (ref * (1 - ref) / n) ** 0.5
        out[kind] = {"n": n, "homomorphism_rate": hom / n, "functional_vanishing_rate": van / n,
                     "ratio_defined_rate": defined / n, "success_rate": rate, "reference_inv_p": ref,
                     "z_score": (rate - ref) / sigma if sigma else None}
    return {"sections": out, "primes": len(primes)}


def build(seed: int, pmin: int, pmax: int, n_primes: int, samples: int):
    rng = random.Random(seed)
    primes = sorted(rng.sample(list(sympy.primerange(pmin, pmax)), n_primes))
    recs = [measure_prime(p, seed=seed, samples=samples) for p in primes]
    m = summarize(recs)
    m.update({"seed": seed, "pmin": pmin, "pmax": pmax, "samples": samples, "precision": PRECISION, "prime_list": primes})
    return m, {"primes": recs}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True); ap.add_argument("--run-id", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--pmin", type=int, default=50); ap.add_argument("--pmax", type=int, default=2000)
    ap.add_argument("--n-primes", type=int, default=40); ap.add_argument("--samples", type=int, default=40)
    a = ap.parse_args(argv)
    t0 = time.time(); m, raw = build(a.seed, a.pmin, a.pmax, a.n_primes, a.samples); t1 = time.time()
    write_run_record(a.run_dir, run_id=a.run_id, exp_id=EXP_ID, status="completed_valid", command=[sys.executable] + sys.argv,
                     sources=[os.path.abspath(__file__), os.path.join(REPO, "harness", "czlift.py"), os.path.join(REPO, "harness", "czlift_run.py")],
                     seed=a.seed, parameters={"pmin": a.pmin, "pmax": a.pmax, "n_primes": a.n_primes, "samples": a.samples, "precision": PRECISION, "tier": "toy"},
                     metrics=m, raw=raw, started=t0, finished=t1, curve_id="multiplicative-group-F_p-star", stdout=json.dumps(m, indent=1) + "\n")
    print(json.dumps(m["sections"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
