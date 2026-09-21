# EXP-DREG-004 pre-computation: nb, eq_degs, and the semi-regular rank
# prediction sr_pred at n=21, t=3, ti=0, D=5, seed 2026 (frozen cell).
# Prints JSON to stdout. Build-only; no Macaulay matrix is formed.
import sys, json, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from math import comb
from h012_peel_rank import build_system, semireg_rank_pred

t0 = time.time()
ret = build_system(21, 3, 0, 2026)
if ret is None:
    print(json.dumps({"ok": False, "reason": "no decomposable R"}))
    sys.exit(1)
rng, nb, monosets, eq_degs = ret
t_build = time.time() - t0

Dmax = 5
pred, HF = semireg_rank_pred(eq_degs, nb, Dmax)
out = {
    "ok": True,
    "n": 21, "t": 3, "ti": 0, "seed": 2026, "D": 5,
    "nb": int(nb),
    "n_equations": len(monosets),
    "eq_degs": [int(d) for d in eq_degs],
    "HF": [int(x) for x in HF],
    "sr_pred": {str(D): int(pred[D]) for D in range(Dmax + 1)},
    "sr_pred_D5": int(pred[5]),
    "boolean_simplex_cols_D5": sum(comb(nb, j) for j in range(0, 6)),
    "build_seconds": round(t_build, 2),
}
print(json.dumps(out, indent=1))
