#!/usr/bin/env python3
"""TASK-20261009-a92ff3 -- RESUMABLE form of extend_coverage.py (addendum AD-7, DV-7, DV-8).

Written after two container restarts killed the AD-7 extension runs. It uses the
SAME seeds and the SAME draw order as extend_coverage.py:
  designs of family f: one generator SeedSequence([0xA92FF3, 40 + i, f]) (random arms
    for all 20000 designs, then their structured totals);
  inner structured draws: one generator SeedSequence([0xA92FF3, 50 + i, 0]) consumed
    sequentially over families 0..3 and batches of 16 designs.
So an uninterrupted run gives exactly the values extend_coverage.py would give.
Restart safety: each family's designs are saved once; every CK_EVERY batches the
partial bounds and the inner generator's exact bit-generator state are saved
atomically (npz first, then json), so a restart loses at most one interval.
Usage: extend_coverage_resumable.py <countdir> <simdir> <kappa_index>
"""
from __future__ import annotations

import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import simulate_ua as su  # this task's own script

EXT_FAMILIES = 4
EXT_DESIGNS = 20000
B = 16
CK_EVERY = 64


def atomic_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f)
    os.replace(tmp, path)


def atomic_npz(path, **arrs):
    tmp = path + ".tmp.npz"
    np.savez(tmp, **arrs)
    os.replace(tmp, path)


def main(indir, outdir, i):
    kt = su.KAPPAS[i]
    curves, _ = su.load(indir)
    mod = su.model(curves, "adopted")
    bk = np.load(os.path.join(outdir, "bank_adopted_1.npz"))
    C_Rb, SEb = su.se_of(bk["T"], bk["Q"])
    ckj = os.path.join(outdir, f"extR_{i}_ckpt.json")
    ckn = os.path.join(outdir, f"extR_{i}_ckpt.npz")
    rng_in = su.gen(50 + i, 0)
    start_f, start_s0, done, resumes = 0, 0, [], 0
    part = None
    if os.path.exists(ckj):
        st = json.load(open(ckj))
        start_f, start_s0, done, resumes = st["family"], st["s0"], st["done"], st["resumes"] + 1
        rng_in.bit_generator.state = st["rng_state"]
        if start_s0 > 0:
            z = np.load(ckn)
            assert int(z["family"]) == start_f and int(z["s0"]) >= start_s0
            part = (z["Us"].copy(), z["Ua"].copy())
        print(f"resume {resumes}: family {start_f} s0 {start_s0}", flush=True)
    t0 = time.time()
    for f in range(start_f, EXT_FAMILIES):
        dp = os.path.join(outdir, f"extR_{i}_fam{f}_designs.npz")
        if os.path.exists(dp):
            z = np.load(dp)
            Ts, Qs, CAs = z["Ts"], z["Qs"], z["CAs"]
        else:
            rng = su.gen(40 + i, f)
            Ts, Qs = su.draw_randoms(rng, mod, EXT_DESIGNS)
            CAs = su.draw_struct_totals(rng, mod, kt, (EXT_DESIGNS,))
            atomic_npz(dp, Ts=Ts, Qs=Qs, CAs=CAs)
        C_Rs, SEs = su.se_of(Ts, Qs)
        kh = CAs / C_Rs
        if f == start_f and part is not None:
            Us, Ua = part
            s_begin = start_s0
        else:
            Us, Ua = np.full(EXT_DESIGNS, np.nan), np.full(EXT_DESIGNS, np.nan)
            s_begin = 0
        nb = 0
        for s0 in range(s_begin, EXT_DESIGNS, B):
            sl = slice(s0, min(EXT_DESIGNS, s0 + B))
            k = kh[sl]
            k_eff = np.where(3 * CAs[sl] == Ts[sl], 1.0, k)
            tot = su.draw_struct_totals(rng_in, mod, k_eff, (len(k), su.FAMILIES, su.REPS))
            ks = tot / C_Rb[None]
            dev = (ks - k_eff[:, None, None]) / SEb[None]
            Us[sl] = k - np.quantile(dev, 0.05, axis=2).mean(axis=1) * SEs[sl]
            Ua[sl] = k + np.quantile(np.abs(dev), 0.95, axis=2).mean(axis=1) * SEs[sl]
            nb += 1
            nxt = s0 + B
            if nb % CK_EVERY == 0 and nxt < EXT_DESIGNS:
                atomic_npz(ckn, Us=Us, Ua=Ua, family=f, s0=nxt)
                atomic_json(ckj, {"family": f, "s0": nxt, "rng_state": rng_in.bit_generator.state,
                                  "done": done, "resumes": resumes})
        assert not np.isnan(Us).any() and not np.isnan(Ua).any()
        cs, ca = int(np.sum(Us >= kt)), int(np.sum(Ua >= kt))
        done.append({"family": f, "signed": cs / EXT_DESIGNS, "absdev": ca / EXT_DESIGNS,
                     "covered_signed": cs, "covered_absdev": ca})
        atomic_json(ckj, {"family": f + 1, "s0": 0, "rng_state": rng_in.bit_generator.state,
                          "done": done, "resumes": resumes})
        print(i, kt, f, cs / EXT_DESIGNS, ca / EXT_DESIGNS, time.time() - t0, flush=True)
    n_tot = EXT_FAMILIES * EXT_DESIGNS
    s = sum(d["covered_signed"] for d in done) / n_tot
    a = sum(d["covered_absdev"] for d in done) / n_tot
    out = {"kappa": kt, "designs": n_tot, "bank_purpose": 1,
           "design_seed": f"SeedSequence([0xA92FF3, {40 + i}, f]), f = 0..{EXT_FAMILIES - 1}",
           "inner_seed": f"SeedSequence([0xA92FF3, {50 + i}, 0])",
           "signed": {"coverage": s, "mc_se": math.sqrt(s * (1 - s) / n_tot),
                      "covered": sum(d["covered_signed"] for d in done)},
           "absdev_AB1": {"coverage": a, "mc_se": math.sqrt(a * (1 - a) / n_tot),
                          "covered": sum(d["covered_absdev"] for d in done)},
           "per_family": [{"family": d["family"], "signed": d["signed"], "absdev": d["absdev"]} for d in done],
           "writer": "extend_coverage_resumable.py", "resumes": resumes}
    atomic_json(os.path.join(outdir, f"coverage_ext_{i}.json"), out)
    print("done", i, flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
