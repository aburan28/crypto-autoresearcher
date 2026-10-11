#!/usr/bin/env python3
"""J4 step 5 (TASK-20260923-29e7af): over ALL pivots with S_k >= 1 (F-S3,
non-degenerate targets), count forced-zero (DEP / DEP_TAU) vs rank-increasing
(IND) pivots per reference, and check every forced-zero pivot has h_k = 0 and
every IND pivot is within its 99.9% band. Mine vs archived was already 0-mismatch."""
import json, os, math
import numpy as np
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("jp", os.path.join(HERE, "j4_predict.py"))
jp = importlib.util.module_from_spec(spec); spec.loader.exec_module(jp)
forms = json.load(open(os.path.join(HERE, "forms-D4.json")))["refs"]
T = jp.targets("F-S3")
out = {}
for lab in ["U1", "U2", "U3", "S1", "S2", "modal"]:
    F = forms[lab]; a0 = np.array(F["a0"], dtype=np.uint8); a = np.array(F["a"], dtype=np.int64)
    cls, _, _ = jp.classify(a)
    rs = [x for i, x, dg in T if not dg and (lab != "modal" or i > 100)]
    Sk, zk, dep, full = jp.hazard(jp.evalf(a0, a, rs))
    live = [k for k in range(len(a)) if Sk[k] >= 1 and dep[k]]
    forced = [k for k in live if cls[k] in ("DEP", "DEP_TAU")]
    ind = [k for k in live if cls[k] == "IND"]
    out[lab] = {"sampled_dependent_with_S_ge_1": len(live), "forced_zero": len(forced),
                "forced_zero_all_h0": bool(all(zk[k] == 0 for k in forced)),
                "IND": len(ind), "IND_h": [round(float(zk[k] / Sk[k]), 3) for k in ind], "IND_S": [int(Sk[k]) for k in ind],
                "IND_in_99.9_band": int(sum(abs(zk[k] / Sk[k] - 0.5) <= 3.29 / (2 * math.sqrt(Sk[k])) for k in ind)),
                "last_k_with_survivors": int(max(k for k in range(len(a)) if Sk[k] >= 1))}
json.dump(out, open(os.path.join(HERE, "allpivots-D4.json"), "w"), indent=1)
for k, v in out.items(): print(k, v)
