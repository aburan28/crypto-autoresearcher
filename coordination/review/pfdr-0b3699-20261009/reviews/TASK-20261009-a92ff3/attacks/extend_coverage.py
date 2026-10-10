#!/usr/bin/env python3
"""TASK-20261009-a92ff3 -- SUPPLEMENTARY coverage extension (addendum AD-7).

Decided after the adopted R-14 coverages (20000 designs per kappa) were seen to
lie within 3 Monte Carlo SE of 0.945. It only reduces the binomial Monte Carlo
error of the same functional, under the same readings, bank and rule. The adopted
values stay the pre-declared 20000-design ones; this supplement is reported
beside them and never replaces them.

Seeds: designs SeedSequence([0xA92FF3, 40 + i, f]), f = 0..3 (20000 designs each);
inner structured draws SeedSequence([0xA92FF3, 50 + i, 0]); bank purpose 1.
Usage: extend_coverage.py <countdir> <simdir> <kappa_index>
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


def main(indir, outdir, i):
    kt = su.KAPPAS[i]
    curves, _ = su.load(indir)
    mod = su.model(curves, "adopted")
    bk = np.load(os.path.join(outdir, "bank_adopted_1.npz"))
    C_Rb, SEb = su.se_of(bk["T"], bk["Q"])
    t0 = time.time()
    rng_in = su.gen(50 + i, 0)
    cov_s, cov_a, n_tot = [], [], 0
    per_fam = []
    for f in range(EXT_FAMILIES):
        rng = su.gen(40 + i, f)
        Ts, Qs = su.draw_randoms(rng, mod, EXT_DESIGNS)
        CAs = su.draw_struct_totals(rng, mod, kt, (EXT_DESIGNS,))
        C_Rs, SEs = su.se_of(Ts, Qs)
        kh = CAs / C_Rs
        Us = np.empty(EXT_DESIGNS)
        Ua = np.empty(EXT_DESIGNS)
        for s0 in range(0, EXT_DESIGNS, B):
            sl = slice(s0, min(EXT_DESIGNS, s0 + B))
            k = kh[sl]
            k_eff = np.where(3 * CAs[sl] == Ts[sl], 1.0, k)
            tot = su.draw_struct_totals(rng_in, mod, k_eff, (len(k), su.FAMILIES, su.REPS))
            ks = tot / C_Rb[None]
            dev = (ks - k_eff[:, None, None]) / SEb[None]
            Us[sl] = k - np.quantile(dev, 0.05, axis=2).mean(axis=1) * SEs[sl]
            Ua[sl] = k + np.quantile(np.abs(dev), 0.95, axis=2).mean(axis=1) * SEs[sl]
        cs, ca = int(np.sum(Us >= kt)), int(np.sum(Ua >= kt))
        cov_s.append(cs)
        cov_a.append(ca)
        n_tot += EXT_DESIGNS
        per_fam.append({"family": f, "signed": cs / EXT_DESIGNS, "absdev": ca / EXT_DESIGNS})
        print(i, kt, f, cs / EXT_DESIGNS, ca / EXT_DESIGNS, time.time() - t0, flush=True)
    s, a = sum(cov_s) / n_tot, sum(cov_a) / n_tot
    out = {"kappa": kt, "designs": n_tot, "bank_purpose": 1,
           "design_seed": f"SeedSequence([0xA92FF3, {40 + i}, f]), f = 0..{EXT_FAMILIES - 1}",
           "inner_seed": f"SeedSequence([0xA92FF3, {50 + i}, 0])",
           "signed": {"coverage": s, "mc_se": math.sqrt(s * (1 - s) / n_tot), "covered": sum(cov_s)},
           "absdev_AB1": {"coverage": a, "mc_se": math.sqrt(a * (1 - a) / n_tot), "covered": sum(cov_a)},
           "per_family": per_fam, "seconds": time.time() - t0}
    json.dump(out, open(os.path.join(outdir, f"coverage_ext_{i}.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
