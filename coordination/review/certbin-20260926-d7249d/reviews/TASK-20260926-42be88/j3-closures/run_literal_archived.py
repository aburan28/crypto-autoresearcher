"""J3 (1): own literal W_4 (and own M_3 / M_4) on archived systems, compared with the archived
closures.jsonl.gz records; plus a bit-level comparison of the final W_4 space with the pinned engine
(imported unchanged) on the SAME decoded equations.

Selection rule (fixed before reading any closure outcome; outcome-independent):
  required: the highest-index unsatisfiable system of S3-U400, of N-CONV19 and of N-ELL19;
  extras:   the highest-index unsatisfiable system of N-F219, of N-AFF19 and of each F-RANDX19 stratum,
            and the highest-index S3-SAT100 system.
usage: python3 run_literal_archived.py <snapshot_root>
"""
import gzip
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "j2-population"))
import gf219 as G  # noqa: E402
from literal_w4 import Lit, eqs_from_E, macaulay_only  # noqa: E402

ROOT = sys.argv[1]
RUN = os.path.join(ROOT, "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60")
only = sys.argv[2].split(",") if len(sys.argv) > 2 else None


def load_jsonl(path):
    with gzip.open(path, "rt") as fh:
        return [json.loads(l) for l in fh]


inst = load_jsonl(os.path.join(RUN, "instances.jsonl.gz"))


def highest(arm, role="unsat", stratum=None):
    c = [r for r in inst if r["arm"] == arm and r["role"] == role and (stratum is None or r.get("stratum") == stratum)]
    return max(c, key=lambda r: r["index"])["key"]


sel = [highest("S3-U400"), highest("N-CONV19"), highest("N-ELL19"),
       highest("N-F219"), highest("N-AFF19"),
       highest("F-RANDX19", stratum="X2E"), highest("F-RANDX19", stratum="XE-NOT-2E"), highest("F-RANDX19", stratum="TWIST"),
       highest("S3-SAT100", role="sat")]
if only:
    sel = [k for k in sel if k in only]
print("selection", sel, flush=True)
byk = {r["key"]: r for r in inst}
clo = {r["key"]: r for r in load_jsonl(os.path.join(RUN, "closures.jsonl.gz")) if r["key"] in sel}

sys.path.insert(0, os.path.join(ROOT, "src"))
from crypto_autoresearcher.gf2 import closure as gclosure  # noqa: E402
from crypto_autoresearcher.gf2 import _native, kernels  # noqa: E402

L = Lit(20, 4)
eng = gclosure.Closure(20, 4, 19)
results = []
for key in sel:
    r = byk[key]
    E = G.hex_to_E(r["E_hex"])
    assert G.E_to_hex(E) == r["E_hex"] and G.E_sha256(G.E_to_hex(E)) == r["E_sha256"]
    eqs = eqs_from_E(E)
    t = time.time()
    m3 = macaulay_only(20, 3, eqs)
    mrec, rec, per_iter, piv = L.w_closure(eqs, log=lambda d: print(key, d, flush=True))
    secs = round(time.time() - t, 1)
    a = clo[key]
    cmp = {
        "M_3": {f: [m3[f], a["M_3"][f]] for f in ("rank", "one", "dims_by_deg")},
        "M_4": {f: [mrec[f], a["M_4"][f]] for f in ("rank", "one", "dims_by_deg")},
        "W_4": {f: [rec[f], a["W_4"][f]] for f in ("dims", "iterations_to_fixpoint", "one", "one_first_iteration",
                                                   "final_dim", "dims_by_deg")},
    }
    diffs = [f"{blk}.{f}" for blk, d in cmp.items() for f, (x, y) in d.items() if x != y]
    # bit-level: engine (unchanged) on the same decoded equations; compare final W_4 space
    erec, _ = eng.w_closure(eqs, want_cert=False)
    fb, fl = eng._final
    dense = eng.unpack(fb)
    contained = 0
    for row in dense:
        x = 0
        for c in np.flatnonzero(row):
            x ^= 1 << L.pos[int(eng.col_mask[c])]
        while x:
            l = x.bit_length() - 1
            p = piv.get(l)
            if p is None:
                break
            x ^= p
        if x == 0:
            contained += 1
    engine_space_equal = (contained == dense.shape[0] == len(piv))
    results.append({"key": key, "arm": r["arm"], "role": r["role"], "seconds_literal": secs,
                    "literal_per_iteration": per_iter, "comparison_mine_vs_archived": cmp,
                    "differences": diffs,
                    "engine_rerun_record_equals_archived": erec == a["W_4"],
                    "engine_final_basis_rows": int(dense.shape[0]), "engine_rows_in_my_W4": contained,
                    "final_W4_space_bit_equal_to_engine": bool(engine_space_equal)})
    print(key, "diffs", diffs, "space_equal", engine_space_equal, "secs", secs, flush=True)

out = {"selection_rule": __doc__.split("Selection rule")[1].split("usage")[0].strip(),
       "selection": sel, "results": results,
       "engine_backend": kernels.backend(), "engine_build_info": dict(_native.build_info),
       "all_equal": all(not x["differences"] and x["final_W4_space_bit_equal_to_engine"]
                        and x["engine_rerun_record_equals_archived"] for x in results)}
name = "literal-vs-archived.json" if not only else "literal-vs-archived-" + "_".join(k.replace(":", "") for k in sel) + ".json"
with open(os.path.join(HERE, name), "w") as fh:
    json.dump(out, fh, indent=1)
print("ALL_EQUAL", out["all_equal"])
