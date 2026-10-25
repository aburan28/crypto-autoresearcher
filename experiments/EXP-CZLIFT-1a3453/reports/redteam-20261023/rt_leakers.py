#!/usr/bin/env python3
"""Red team TASK-20261023-792040, joint R1 and PTM-1: leaking digit functions the statistic cannot see.

Runs the producer's UNCHANGED instrument run.spectrum (imported from the frozen
implementation, sha256 307756d6...) on planted digit sequences f(k), k = 1..n-1
(k = 0 placeholder 0, as in the driver), at every (p, n) of the 72 admissible
curve records. Every planted sequence is a deterministic or seeded function of
the discrete log k, so the conclusion "this digit does not carry the discrete
log" is KNOWN FALSE for each of them:

  PTM     floor(p k / n) mod p                      linear leak (the plan's PTM-1)
  CHIRP   floor(p (k^2 mod n) / n)                  determines k on the half range (k^2 -> +-k)
  INV     floor(p (k^-1 mod n) / n)                 determines k (Kloosterman-type phase)
  LEGMSB  random QR if k <= h/2 else random QNR     one exact bit of k, carried by the Legendre symbol
  LSB     2U + (k mod 2), U uniform < (p-1)/2       parity of k in the digit's low bit (a visible calibration)
  SPARSE  PTM on m random half-range positions, uniform elsewhere, m = ceil(0.6 sqrt(T h))
  WEAK    PTM with probability rho = 0.6 sqrt(T/h) per k, uniform otherwise

Usage: rt_leakers.py OUT.json
"""
from __future__ import annotations

import json
import math
import os
import random
import sys

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "experiments", "EXP-CZLIFT-1a3453", "implementation"))
import run as driver  # noqa: E402  (the frozen instrument)

BASE = os.path.join(REPO, "experiments", "EXP-CZLIFT-1a3453")
RUNS = ["RUN-CZLIFT-037e5f", "RUN-CZLIFT-d37ca4"]


def legendre(v: int, p: int) -> int:
    return pow(v, (p - 1) // 2, p)


def planted(kind: str, p: int, n: int, rng: random.Random, T: float) -> np.ndarray:
    h = (n - 1) // 2
    f = np.zeros(n, dtype=np.int64)
    qr = [v for v in range(1, p) if legendre(v, p) == 1]
    qnr = [v for v in range(1, p) if legendre(v, p) == p - 1]
    sparse_pos = set(rng.sample(range(1, h + 1), min(h, math.ceil(0.6 * math.sqrt(T * h)))))
    rho = min(1.0, 0.6 * math.sqrt(T / h))
    for k in range(1, n):
        if kind == "PTM":
            f[k] = (p * k // n) % p
        elif kind == "CHIRP":
            f[k] = (p * (k * k % n) // n) % p
        elif kind == "INV":
            f[k] = (p * pow(k, -1, n) // n) % p
        elif kind == "LEGMSB":
            r = k if k <= h else n - k
            f[k] = rng.choice(qr) if r <= h // 2 else rng.choice(qnr)
        elif kind == "LSB":
            f[k] = 2 * rng.randrange((p - 1) // 2) + (k % 2)
        elif kind == "SPARSE":
            f[k] = (p * k // n) % p if k in sparse_pos else rng.randrange(p)
        elif kind == "WEAK":
            f[k] = (p * k // n) % p if rng.random() < rho else rng.randrange(p)
    return f


def info_bits(kind: str, p: int, n: int) -> str:
    h = (n - 1) // 2
    if kind == "PTM":
        return "k exactly (injective when p >= n)"
    if kind == "CHIRP":
        vals = {(p * (k * k % n) // n) % p for k in range(1, h + 1)}
        return f"{len(vals)}/{h} distinct values on the half range"
    if kind == "INV":
        vals = {(p * pow(k, -1, n) // n) % p for k in range(1, h + 1)}
        return f"{len(vals)}/{h} distinct values on the half range"
    if kind == "LEGMSB":
        return "1 exact bit ([k] <= h/2) via the Legendre symbol of the digit"
    if kind == "LSB":
        return "1 exact bit (k mod 2) via the digit's low bit"
    return "partial"


def main(out_path: str) -> None:
    seen = {}
    for run in RUNS:
        raw = json.load(open(os.path.join(BASE, "runs", run, "raw-result.json")))
        for c in raw["raw"]["curves"]:
            seen.setdefault((c["p"], c["n"]), []).append(f"{run}:{c['arm']}:{c['label']}")
    kinds = ["PTM", "CHIRP", "INV", "LEGMSB", "LSB", "SPARSE", "WEAK"]
    rows = []
    for (p, n), where in sorted(seen.items()):
        h = (n - 1) // 2
        T = math.log((p - 1) * n) + driver.SPIKE_MARGIN
        for kind in kinds:
            rng = random.Random(f"rt-{p}-{n}-{kind}")
            f = planted(kind, p, n, rng, T)
            best, above, thr = driver.spectrum(f, p, n)
            assert abs(thr - T) < 1e-12
            rows.append({"p": p, "n": n, "h": h, "T": T, "blind": h <= T, "records": where, "kind": kind,
                         "max_power": best, "above": above, "excess": best - T, "info": info_bits(kind, p, n)})
    # aggregate over the 72 records (weights = number of records at that (p, n))
    agg = {}
    for r in rows:
        w = len(r["records"])
        a = agg.setdefault(r["kind"], {"records": 0, "records_spiking": 0, "power_bearing_records": 0,
                                        "power_bearing_spiking": 0, "max_excess": -1e9, "max_ratio_to_T": 0.0})
        a["records"] += w
        a["records_spiking"] += w * int(r["above"] > 0)
        if not r["blind"]:
            a["power_bearing_records"] += w
            a["power_bearing_spiking"] += w * int(r["above"] > 0)
            a["max_ratio_to_T"] = max(a["max_ratio_to_T"], r["max_power"] / r["T"])
        a["max_excess"] = max(a["max_excess"], r["excess"])
    out = {"instrument": "experiments/EXP-CZLIFT-1a3453/implementation/run.py:spectrum (unchanged)",
           "aggregate_over_72_records": agg, "rows": rows}
    json.dump(out, open(out_path, "w"), indent=1)
    print(json.dumps(agg, indent=1))
    for kind in ("CHIRP", "INV", "LEGMSB"):
        big = [r for r in rows if r["kind"] == kind and not r["blind"]]
        big.sort(key=lambda r: -r["n"])
        for r in big[:3]:
            print(kind, r["p"], r["n"], round(r["max_power"], 2), "T", round(r["T"], 2), r["info"])


if __name__ == "__main__":
    main(sys.argv[1])
