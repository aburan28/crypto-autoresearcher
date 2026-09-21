#!/usr/bin/env python3
"""RED TEAM independent re-measurement of the ENCODED rule.  TASK-20260806-250b29.

Loads the frozen constants OUT OF amendment_v3.yaml with its own loader, asserts
their parsed type, and measures the realized size of THOSE values on validation
draws under seeds of my own choosing (SHA-256 of this task id, not the
producer's seed namespace).  Also measures:
  * the q-sensitivity rows at +-1/2/3 SE and the breakdown grid;
  * the FAMILYWISE flag rate of the multi-k battery under the exact null.

Claim tier TOY.  Every draw is from S ~ Binomial(n_e, q) under an explicit
null.  No HQC object is constructed and no (T) arm is sampled.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time

import numpy as np
import yaml

AMD = ("/home/user/crypto-autoresearcher/coordination/goals/GOAL-HQC-001/batches/"
       "BATCH-0a65c0/tasks/TASK-20260806-6086cb/amendment_v3.yaml")
BLOCK_FAILURES = {"PS-A": 8122, "PS-R1": 5200049, "PS-R3": 9159668, "PS-R5": 13187613}
ACCEPT = (0.002, 0.004)
CHUNK = 100_000


def myseed(*parts):
    key = "RT/TASK-20260806-250b29|" + "|".join(str(p) for p in parts)
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")


def load_cfgs():
    A = yaml.safe_load(open(AMD))["protocol_amendment"]
    out = {}
    for cfg in A["R1_INV_NULL_v3"]["frozen_intervals"]["configurations"]:
        cells = {}
        for c in cfg["cells"]:
            if c.get("c_lo") is None or c.get("status") != "REPORTED":
                continue
            assert isinstance(c["c_lo"], float) and isinstance(c["c_hi"], float), \
                ("NON-FLOAT CONSTANT", cfg["set"], c["k"], type(c["c_lo"]))
            cells[c["k"]] = (c["c_lo"], c["c_hi"])
        out[(cfg["set"], cfg["allocation"])] = dict(
            n_e=cfg["n_e"], q_hat=cfg["q_hat"], T=cfg["T"], cells=cells)
    return out


def binom_pmf(n_e, q):
    p = np.array([math.comb(n_e, i) * q ** i * (1 - q) ** (n_e - i)
                  for i in range(n_e + 1)], dtype=np.float64)
    return p / p.sum()


def log2_A(H, n_e, ks, C):
    Hf = H.astype(np.float64)
    T = Hf.sum(axis=1)
    q = (Hf @ np.arange(n_e + 1, dtype=np.float64)) / (T * n_e)
    mu = (Hf @ C) / (T[:, None] * np.array([float(math.comb(n_e, k)) for k in ks]))
    out = np.full(mu.shape, np.nan)
    good = (mu > 0) & (q[:, None] > 0)
    lq = np.log2(np.where(q > 0, q, 1.0))[:, None]
    kk = np.array(ks, dtype=np.float64)[None, :]
    out[good] = (np.log2(np.where(good, mu, 1.0)) - kk * lq)[good]
    return out


def measure(n_e, q_draw, T, ks, lo, hi, n_rep, seed):
    """Returns per-cell (firings, finite) and the familywise firing count."""
    C = np.array([[float(math.comb(s, k)) for k in ks] for s in range(n_e + 1)])
    pmf = binom_pmf(n_e, q_draw)
    rng = np.random.Generator(np.random.PCG64(seed))
    fire = np.zeros(len(ks), dtype=np.int64)
    fin = np.zeros(len(ks), dtype=np.int64)
    fam = 0
    done = 0
    while done < n_rep:
        c = min(CHUNK, n_rep - done)
        V = log2_A(rng.multinomial(T, pmf, size=c), n_e, ks, C)
        ok = np.isfinite(V)
        f = ok & ((V < lo[None, :]) | (V > hi[None, :]))
        fin += ok.sum(axis=0)
        fire += f.sum(axis=0)
        fam += int(f.any(axis=1).sum())
        done += c
    return fire, fin, fam, n_rep


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return None, None
    p = k / n
    d = 1 + z * z / n
    ctr = p + z * z / (2 * n)
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (ctr - hw) / d, (ctr + hw) / d


def main():
    which = sys.argv[1:] or ["PS-R3@1e7", "PS-A@1e8"]
    cfgs = load_cfgs()
    N_VAL = 1_000_000
    N_SENS = 400_000
    out = {}
    for w in which:
        sid, alab = w.split("@")
        F = cfgs[(sid, alab)]
        n_e, q0, T = F["n_e"], F["q_hat"], F["T"]
        ks = sorted(F["cells"])
        lo = np.array([F["cells"][k][0] for k in ks])
        hi = np.array([F["cells"][k][1] for k in ks])
        se = math.sqrt((1 - q0) / BLOCK_FAILURES[sid])
        t0 = time.time()
        fire, fin, fam, nrep = measure(n_e, q0, T, ks, lo, hi, N_VAL, myseed(sid, alab, "val"))
        cells = []
        for j, k in enumerate(ks):
            s = fire[j] / fin[j]
            l, u = wilson(int(fire[j]), int(fin[j]))
            cells.append(dict(k=k, size=s, ci=[l, u], in_gate=bool(ACCEPT[0] <= s <= ACCEPT[1]),
                              c_lo=float(lo[j]), c_hi=float(hi[j])))
        famrate = fam / nrep
        fl, fu = wilson(fam, nrep)
        # q-sensitivity, my own draws
        sens = []
        grid = sorted({0.0} | {m * se * sgn for m in (1, 2, 3) for sgn in (1, -1)}
                      | {d * sgn for d in (0.0025, 0.005, 0.01, 0.02, 0.04) for sgn in (1, -1)})
        for d in grid:
            fr, fi_, _, _ = measure(n_e, q0 * (1 + d), T, ks, lo, hi, N_SENS,
                                    myseed(sid, alab, "sens", repr(d)))
            sens.append(dict(rel_shift=d, se_multiple=d / se,
                             sizes={int(k): float(fr[j]) / float(fi_[j]) for j, k in enumerate(ks)}))
        per_k_break = {}
        for j, k in enumerate(ks):
            bad = [abs(r["rel_shift"]) for r in sens
                   if r["rel_shift"] != 0.0 and not (ACCEPT[0] <= r["sizes"][k] <= ACCEPT[1])]
            per_k_break[int(k)] = min(bad) if bad else None
        out[w] = dict(n_e=n_e, q_hat=q0, T=T, n_validation=N_VAL, n_sens_per_point=N_SENS,
                      se_rel_q_hat=se, three_se_rel=3 * se, cells=cells,
                      size_range=[min(c["size"] for c in cells), max(c["size"] for c in cells)],
                      cells_outside_gate=[c["k"] for c in cells if not c["in_gate"]],
                      familywise_rate=famrate, familywise_ci=[fl, fu],
                      per_k_breakdown_rel_shift=per_k_break,
                      all_in_band_over_pm3SE=all(
                          ACCEPT[0] <= r["sizes"][k] <= ACCEPT[1]
                          for r in sens if abs(r["se_multiple"]) <= 3 + 1e-9 for k in ks),
                      sens=sens, seconds=time.time() - t0)
        print("== %s  n_e=%d q=%.8g T=%.0e  cells=%d" % (w, n_e, q0, T, len(ks)))
        print("   size range %.5f - %.5f   outside gate: %s"
              % (out[w]["size_range"][0], out[w]["size_range"][1], out[w]["cells_outside_gate"]))
        print("   familywise (any cell fires) %.5f  95%% CI [%.5f, %.5f]  = %.2fx per-cell nominal"
              % (famrate, fl, fu, famrate / 0.0026997960632601866))
        print("   3SE_rel=%.6f  all cells in band over +-3SE: %s"
              % (3 * se, out[w]["all_in_band_over_pm3SE"]))
        print("   breakdown rel shift per k: %s" % per_k_break)
        print("   (%.0f s)" % out[w]["seconds"])
    json.dump(out, open("resize_results.json", "w"), indent=1)


if __name__ == "__main__":
    main()
