"""Numerical independence check for the Elkies-Watkins comparison curves (red team, TASK-20261023-7b5dc6).

For each curve: enumerate points of naive height <= 1e4, greedily keep points whose addition keeps the
height-pairing Gram matrix positive definite (min eigenvalue > 0.02; heights by the doubling limit,
k = 7, error ~1e-5), stop at the source rank.  The number kept is a NUMERICAL lower bound on the rank
(not a proof: floating-point heights).  Also reports det(Gram) (Silverman normalisation) of the kept set
and the minimal canonical height among them.  Output rt_ew_heights_output.json.
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rt_lib as L
import rt_heights as RH

CURVES = [("EW-r8-N249649566346838", [1, -1, 0, -106384, 13075804], 8),
          ("EW-r9-N32107342006814614", [1, -1, 0, -135004, 97151644], 9),
          ("EW-r10-N10189285026863130793", [0, 0, 1, -16312387, 25970162646], 10),
          ("EW-r11-N18031737725935636520843", [0, 0, 1, -16359067, 26274178986], 11)]
out = {"rows": []}
for lab, ai, r in CURVES:
    t0 = time.time()
    pts_adc = sorted(L.enumerate_points(ai, 10000), key=lambda t: max(abs(t[0]), t[1] ** 2))
    kept, M = [], None
    for a, d, c in pts_adc:
        P = L.point_from_adc(ai, a, d, c)
        trial = kept + [P]
        Mt, _ = RH.gram(ai, trial)
        if np.linalg.eigvalsh(Mt).min() > 0.02:
            kept, M = trial, Mt
        if len(kept) == r:
            break
    row = {"label": lab, "ainvs": ai, "source_rank_lower_bound": r, "independent_found": len(kept),
           "det_gram_silverman": float(np.linalg.det(M)) if M is not None else None,
           "min_eig": float(np.linalg.eigvalsh(M).min()) if M is not None else None,
           "basis_x": [str(P[0]) for P in kept], "seconds": round(time.time() - t0, 1)}
    out["rows"].append(row)
    print(row, flush=True)
json.dump(out, open(os.path.join(HERE, "rt_ew_heights_output.json"), "w"), indent=1)
