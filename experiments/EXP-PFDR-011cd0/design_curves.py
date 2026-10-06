"""EXP-PFDR-011cd0 R11 step (1): build every design curve and its bases' sizes (no solver).

    <PY> experiments/EXP-PFDR-011cd0/design_curves.py --spec experiments/EXP-PFDR-011cd0/specification.yaml \
        --out RUN_DIR/curves.jsonl [--workers 4]

Imports only curve.py and factor_base.py of the engine (EC-9).  For every rung b in
20..32 step 2 and curve seed c it records the curve of cells.design_curves,

    generate_prime_order_curve(b, c, p_filter=subgroup_prime_filter([3, 4, 5], 0.15)),

its (p, a, b, N, P), X_fix = 20 * isqrt(N), and per m in {3, 4, 5}: size0 =
default_fb_size(N, m), |F_sub| = len(FactorBase.subgroup(E, size0, c)), s_sub = max(4,
|F_sub|), |F_dick| = len(FactorBase.dickson(E, size0, c)), s_dick = max(4, |F_dick|).

Curve seeds: c = 10 .. 10 + n - 1.  At 20..28 bits n = 100 (the declared n, which P0 never
changes there).  At 30 and 32 bits n = 3 x the largest declared n of any (panel, m), so that
P0's frozen raising rule (multipliers up to 3) can be evaluated on real design curves; the
curves P0 does not select are recorded here and never run.  The output is sorted by (bits, c)
and is independent of --workers.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import yaml

from crypto_autoresearcher.index_calculus.curve import generate_prime_order_curve
from crypto_autoresearcher.index_calculus.factor_base import (FactorBase, default_fb_size,
                                                              subgroup_prime_filter)

LAMBDA_XFIX = 20
C0 = 10
RAISE_MAX = 3


def one_curve(job: tuple[int, int]) -> dict:
    bits, c = job
    pf = subgroup_prime_filter([3, 4, 5], 0.15)
    E, P = generate_prime_order_curve(bits, c, p_filter=pf)
    N = E.order
    sizes = {}
    for m in (3, 4, 5):
        size0 = default_fb_size(N, m)
        nsub = len(FactorBase.subgroup(E, size0, c))
        ndick = len(FactorBase.dickson(E, size0, c))
        sizes[str(m)] = {"size0": size0, "F_sub": nsub, "s_sub": max(4, nsub),
                         "F_dick": ndick, "s_dick": max(4, ndick)}
    return {"bits": bits, "curve": c, "p": E.p, "a": E.a, "b": E.b, "N": N,
            "P": [int(P[0]), int(P[1])], "log2N": math.log2(N),
            "X_fix": LAMBDA_XFIX * math.isqrt(N), "sizes": sizes, "p_filter": pf.label}


def declared(spec: dict) -> dict:
    cells = spec["experiment"]["cells"]
    t = cells["table_panel_T"]["curves_per_rung_declared"]
    s = cells["search_panel_S"]["curves_per_rung_declared"]
    return {"table": {int(k[1:]): v for k, v in t.items()},
            "search": {int(k[1:]): v for k, v in s.items()}}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if os.path.exists(a.out):
        print(f"refusing: {a.out} exists", file=sys.stderr)
        return 3
    spec = yaml.safe_load(open(a.spec))
    dec = declared(spec)
    n_low = max(v["b20_to_b28"] for p in dec.values() for v in p.values())
    n_high = max(max(v["b30"], v["b32"]) for p in dec.values() for v in p.values())
    jobs = [(b, c) for b in range(20, 29, 2) for c in range(C0, C0 + n_low)]
    jobs += [(b, c) for b in (30, 32) for c in range(C0, C0 + RAISE_MAX * n_high)]
    if a.workers <= 1:
        recs = [one_curve(j) for j in jobs]
    else:
        with ProcessPoolExecutor(max_workers=min(4, a.workers)) as pool:
            recs = list(pool.map(one_curve, jobs, chunksize=16))
    recs.sort(key=lambda r: (r["bits"], r["curve"]))
    with open(a.out, "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(json.dumps({"curves": len(recs), "declared": dec, "n_low": n_low,
                      "n_high_generated": RAISE_MAX * n_high}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
