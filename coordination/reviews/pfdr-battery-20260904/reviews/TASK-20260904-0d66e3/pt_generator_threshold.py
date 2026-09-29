#!/usr/bin/env python3
"""How many generators does the KNOWN binary deficit need?  (TASK-20260904-0d66e3,
proves_too_much object 1, red-team extension.)

The twin has TWO generators.  On the committed binary fixture — where the deficit
is known nonzero — we hold the characteristic (p = 2), the ring, the convention
and the meter fixed and vary ONLY the number of generators, to see at what size
the deficit turns on.  If it is off at 2 generators, then "deficit 0 at the twin's
shape" is reproduced at p = 2 and cannot by itself attribute the twin's 0 to
characteristic.
"""
from __future__ import annotations

import json
import sys

sys.path.insert(0, "/home/user/crypto-autoresearcher")
from harness.macaulay_fp import Ring, analyze_layer  # noqa: E402

FIX = "/home/user/crypto-autoresearcher/harness/macaulay_fp/fixtures/chained_gf2_n12_t3_seed2026.json"


def main() -> int:
    data = json.load(open(FIX))
    ring = Ring(2, data["nb"], 0)
    gens = [{(sum(1 << v for v in m), ()): 1 for m in f} for f in data["generators"]]
    degs = [ring.degree(g) for g in gens]
    quad = [i for i, d in enumerate(degs) if d == 2]
    out = {"nb": data["nb"], "k": data["k"], "n_quadrics": len(quad), "convention": "cumulative",
           "note": "first j descended quadrics (fixture order); deficit = rows - rank - koszul_pairwise"}
    tbl = {}
    for j in range(2, len(quad) + 1):
        idx = quad[:j]
        per = {}
        for D in (2, 3, 4):
            r = analyze_layer(ring, gens, D, convention="cumulative", generator_subset=idx)
            per[str(D)] = {"rows": r.row_count, "rank": r.full_rank, "koszul": r.koszul_pairwise,
                           "deficit": r.row_count - r.full_rank - r.koszul_pairwise}
        cum = [per[str(D)]["deficit"] for D in (2, 3, 4)]
        tbl[str(j)] = {"deficit_cumulative_D2_D4": cum,
                       "deficit_graded_D2_D4": [cum[0], cum[1] - cum[0], cum[2] - cum[1]],
                       "per_degree": per}
    out["quadrics_only_ladder"] = tbl
    firing = [j for j, v in tbl.items() if any(x != 0 for x in v["deficit_cumulative_D2_D4"])]
    out["smallest_generator_count_with_nonzero_deficit"] = min((int(j) for j in firing), default=None)
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
