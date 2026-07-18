# Analysis-side diagnostic for EXP-TRA-001 (not an experiment run).
# During RUN-TRA-001-a every exact-coarse row returned "no non-stationary eigenvalue with
# positive imaginary part", i.e. the exact coarse operator spectrum appeared entirely real.
# This script recomputes M_exact from the FROZEN instances recorded in raw.json and measures:
#   (a) max |Im(lambda)| over the exact lumped spectrum;
#   (b) detailed-balance residual max | |c|*M[c,c'] - |c'|*M[c',c] | / max |c|;
#   (c) leading non-trivial eigenvalue magnitude (mixing gap context; real, no phase).
# Output: runs/RUN-TRA-001-a/reversibility_check.json

import json
import numpy as np

RAW = "experiments/EXP-TRA-001/runs/RUN-TRA-001-a/raw.json"
OUT = "experiments/EXP-TRA-001/runs/RUN-TRA-001-a/reversibility_check.json"
CGRID = [8, 32, 128]

d = json.load(open(RAW))
rows = []
for inst in d["instances"]:
    p = int(inst["p"]); seed = int(inst["seed"]); n_int = int(inst["n"])
    E = EllipticCurve(GF(p), [GF(p)(inst["a"]), GF(p)(inst["b"])])
    P = E.gens()[0]
    for C in CGRID:
        Cc = C + 1
        cells = [0] * n_int
        R = E(0)
        for r in range(n_int):
            if R.is_zero():
                cells[r] = C
            else:
                cells[r] = min(C - 1, (int(R[0]) * C) // p)
            R = R + P
        cnt = np.zeros((Cc, Cc))
        sizes = np.zeros(Cc)
        for r in range(n_int):
            cnt[cells[r], cells[(r + 1) % n_int]] += 1.0
            sizes[cells[r]] += 1.0
        M = np.zeros((Cc, Cc))
        for c in range(Cc):
            if sizes[c] > 0:
                M[c, :] = cnt[c, :] / sizes[c]
            else:
                M[c, :] = 1.0 / Cc  # same uniform-fill convention as the experiment
        vals = np.linalg.eigvals(M)
        max_im = float(np.max(np.abs(vals.imag)))
        A = sizes[:, None] * M
        DB = np.abs(A - A.T)
        db_res = float(DB.max() / max(sizes.max(), 1.0))
        mags = sorted((float(abs(v)) for v in vals), reverse=True)
        lam2 = mags[1] if len(mags) > 1 else None
        rows.append({"p": p, "seed": seed, "C": C,
                     "max_abs_imag_eigenvalue": max_im,
                     "detailed_balance_residual": db_res,
                     "lambda2_abs": lam2,
                     "top3_mags": mags[:3]})
out = {"note": "exact coarse x-cell translation operator: reversibility/spectrum reality check, recomputed from frozen instances of RUN-TRA-001-a",
       "max_abs_imag_overall": max(r["max_abs_imag_eigenvalue"] for r in rows),
       "max_db_residual_overall": max(r["detailed_balance_residual"] for r in rows),
       "lambda2_abs_mean": sum(r["lambda2_abs"] for r in rows) / len(rows),
       "lambda2_abs_max": max(r["lambda2_abs"] for r in rows),
       "rows": rows}
def jdefault(o):
    try:
        f = float(o)
    except (TypeError, ValueError):
        return str(o)
    i = int(f)
    return i if f == i else f


with open(OUT, "w") as f:
    json.dump(out, f, indent=1, default=jdefault)
print("rows=%d max|Im lambda| = %.3e  max DB residual = %.3e  lam2 mean = %.4f max = %.4f"
      % (len(rows), out["max_abs_imag_overall"], out["max_db_residual_overall"],
         out["lambda2_abs_mean"], out["lambda2_abs_max"]))
