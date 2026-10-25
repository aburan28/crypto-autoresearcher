#!/usr/bin/env python3
"""Red team TASK-20261023-792040, R1 follow-up: where do the planted CHIRP / INV / LSB spikes sit?

For every (p, n) where a planted sequence of rt_leakers.py spikes, split the
spectrum into the trivial character (chi index t = 0, the DC sum, which is
invariant under any re-indexing of k) and the nontrivial characters, and run
the producer-style shuffled control (seeded permutation of all n indices,
k = 0 placeholder included, half range read). A spike that is DC-only and
reappears in the shuffled control is a value-distribution artifact (the planted
values sit on a coarse lattice of spacing about p/n), not a k-correlation; the
frozen falsification criterion would veto it.
Usage: rt_leakers_dc.py LEAKERS_OUT.json OUT.json
"""
from __future__ import annotations

import json
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt_leakers as L  # noqa: E402


def split_spectrum(f: np.ndarray, p: int, n: int):
    h = (n - 1) // 2
    d = f[1:h + 1].astype(np.int64)
    a = np.arange(1, p, dtype=np.int64)[:, None]
    z = np.zeros((p - 1, n), dtype=np.complex128)
    z[:, 1:h + 1] = np.exp(2j * np.pi * ((a * d[None, :]) % p) / p)
    X = np.abs(np.fft.fft(z, axis=1)) ** 2 / h
    T = math.log((p - 1) * n) + 12.0
    return float(X[:, 0].max()), int((X[:, 0] > T).sum()), float(X[:, 1:].max()), int((X[:, 1:] > T).sum()), T


def main(leak_path: str, out_path: str) -> None:
    rows = json.load(open(leak_path))["rows"]
    res = []
    for r in rows:
        if r["above"] == 0 or r["kind"] not in ("CHIRP", "INV", "LSB", "WEAK", "SPARSE"):
            continue
        p, n, kind = r["p"], r["n"], r["kind"]
        rng = random.Random(f"rt-{p}-{n}-{kind}")
        f = L.planted(kind, p, n, rng, r["T"])
        dc, dc_ab, ndc, ndc_ab, T = split_spectrum(f, p, n)
        prng = random.Random(f"rt-perm-{p}-{n}-{kind}")
        sh_spikes = 0
        for _ in range(20):
            perm = np.array(prng.sample(range(n), n))
            sdc, sdc_ab, sndc, sndc_ab, _ = split_spectrum(f[perm], p, n)
            sh_spikes += int(sdc_ab + sndc_ab > 0)
        res.append({"kind": kind, "p": p, "n": n, "cofactor_p_over_n": p / n, "T": T, "dc_max": dc, "dc_above": dc_ab,
                    "nondc_max": ndc, "nondc_above": ndc_ab, "shuffled_spiking_of_20": sh_spikes})
    json.dump(res, open(out_path, "w"), indent=1)
    for x in res:
        print(json.dumps({k: (round(v, 2) if isinstance(v, float) else v) for k, v in x.items()}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
