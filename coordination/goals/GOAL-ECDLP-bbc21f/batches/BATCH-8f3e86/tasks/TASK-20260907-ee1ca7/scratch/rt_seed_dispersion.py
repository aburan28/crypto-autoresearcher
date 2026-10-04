"""RED-TEAM DIAGNOSTIC (TASK-20260907-ee1ca7, joint J4/J5).  NOT A RUN RECORD.

WHAT THIS IS.  A control-strength measurement.  It re-uses the producer's own
frozen code path -- experiments/EXP-ECDLP-612fb1/source_v3/g3_predicate.py
`measure_cell`, which imports the frozen source_v2/instrument.py unchanged --
at N = 2^24, T = 256, T_sel = 128, r = 2, at the SAME four a values, on SEEDS
DISJOINT FROM THE FROZEN SET {1,2,3,4,5}.

WHAT THIS IS NOT.  It is not an experiment run, it emits no run record, it
re-scores nothing, and it changes no verdict.  The frozen protocol's seed set
is {1..5} and BATCH-8f3e86's verdicts stand exactly as executed.  The question
asked here is about the CONTROL, not about the hypothesis: under the frozen
">= 4 of 5 seeds" rule, how much of the a = 3/16 known-false object's FAIL is a
property of the cell and how much is a property of the particular five-seed
draw the contract froze -- i.e. how discriminating the proves-too-much control
actually is.

Writes only under the red-team task directory.
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.dont_write_bytecode = True

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, *([".."] * 8)))
_EXP = os.path.join(_REPO, "experiments", "EXP-ECDLP-612fb1")
sys.path.insert(0, _EXP)

from source_v3 import g3_predicate as G  # noqa: E402  (producer's frozen path)

N_BITS = 24
R = 2
A_GRID = (0.0625, 0.125, 0.1875, 0.25)


def run(seeds, a_grid=A_GRID, n_bits=N_BITS, r=R):
    rows = []
    for a in a_grid:
        for s in seeds:
            t0 = time.time()
            P = G.make_params(n_bits=n_bits, a=a, seed=s)
            basins = G.exact_basins(P)
            cell = G.measure_cell(P, basins, r)
            del basins
            rows.append({
                "n_bits": n_bits, "N": P.N, "T": P.T, "T_sel": G.t_sel_of(P.T),
                "a": a, "r": r, "seed": s,
                "margin": cell["margin"],
                "top_share_T_sel": cell["top_share_T_sel"],
                "top_share_T": cell["top_share_T"],
                "static_cov": cell["static_cov"],
                "margin_null": cell["margin_null"],
                "static_cov_null": cell["static_cov_null"],
                "margin_over_margin_null": cell["margin_over_margin_null"],
                "null_b_set_identical": cell["null_b_set_identical"],
                "exact_coverage_exceeds_top_share_T":
                    cell["exact_coverage_exceeds_top_share_T"],
                "g3": cell["g3"],
                "elapsed_s": round(time.time() - t0, 3),
            })
            print(f"a={a} s={s} margin={cell['margin']:+.9f} "
                  f"null={cell['margin_null']:+.9f} "
                  f"({rows[-1]['elapsed_s']}s)", flush=True)
    return rows


if __name__ == "__main__":
    seeds = [int(x) for x in sys.argv[1].split(",")]
    out = sys.argv[2]
    a_grid = tuple(float(x) for x in sys.argv[3].split(",")) if len(sys.argv) > 3 else A_GRID
    t0 = time.time()
    rows = run(seeds, a_grid=a_grid)
    json.dump({
        "diagnostic": "red-team seed-dispersion diagnostic, TASK-20260907-ee1ca7",
        "is_a_run_record": False,
        "changes_any_verdict": False,
        "code_path": "experiments/EXP-ECDLP-612fb1/source_v3/g3_predicate.measure_cell "
                     "(producer's frozen path, imported unchanged)",
        "frozen_seed_set_of_the_contract": [1, 2, 3, 4, 5],
        "seeds_used_here": seeds,
        "wall_seconds_total": round(time.time() - t0, 3),
        "rows": rows,
    }, open(out, "w"), indent=1)
    print("wrote", out, f"{time.time()-t0:.1f}s")
