#!/usr/bin/env python3
"""w4_bulk_scale.py -- joint W4 addendum (scratch). w4_controls.py part C stopped at nbad = 512; on the instance whose witness is a sparse
point (null_n12: 5 ones of 18 coordinates) that left the detection rate below 1, so the sentence 'a bulk defect is always caught' was not
supported there. This script extends part C to corruptions of the SIZE OBSERVED on M4RI 0.0.20200125 (about half of all output rows bad:
66,598 of 139,204 and 68,559 of 139,898 in the notes' logs) and compares the measured detection rate with the model
P(detect) = 1 - (1 - f)^nbad,  f = (# columns whose monomial is 1 at the witness) / ncols  (the chance that one flipped bit lands on a visible column).
Usage: w4_bulk_scale.py STEM [STEM ...]   -> outputs/w4_bulk_scale.{txt,json} are written by 99-style redirect in the caller; JSON written here.
"""
import sys, os, json, ctypes, tempfile
from math import comb
SP, WS = os.environ["SP"], os.environ["WS"]; W = f"{SP}/work"
sys.path.insert(0, f"{WS}/scripts")
import vclos, gen_small
import numpy as np

out = {}
for stem in sys.argv[1:]:
    s = json.load(open(f"{W}/inst/{stem}.json")); N, eqs, V = s["N"], s["equations"], s["V"]
    ok = gen_small.zeros_count(N, eqs)[1]
    zeros = [int(z) for z in np.nonzero(ok)[0]]
    w = zeros[0]
    ncols = sum(comb(N, d) for d in range(5))
    pop = bin(w).count("1")
    visible = sum(comb(pop, d) for d in range(5))
    f = visible / ncols
    rows = []
    # rank of the second elimination (the corrupted call) from an unmutated run on the evalcheck build
    def run(setup=None):
        c = vclos.Clos(f"{W}/mut/libclosure_BULK_ev.so")
        c.L.closure_ech_reset(); c.L.closure_set_witness(w); c.L.closure_set_method(1)
        if setup: setup(c)
        saved = os.dup(2); tf = tempfile.TemporaryFile(); os.dup2(tf.fileno(), 2)
        try:
            r = c.run(N, 4, eqs, mem_cap_gb=0.5)
        finally:
            os.dup2(saved, 2)
        tf.seek(0); err = tf.read().decode(errors="replace"); os.close(saved)
        a, b, d = ctypes.c_long(), ctypes.c_long(), ctypes.c_long()
        c.L.closure_ech_stats(ctypes.byref(a), ctypes.byref(b), ctypes.byref(d))
        return r, b.value, [l for l in err.splitlines() if l.startswith("[ech ") or l.startswith("[mutb")]
    r0, bad0, l0 = run()
    rank_call1 = int([l for l in l0 if l.startswith("[ech 1 ")][0].split("rank")[1].split("|")[0])
    print(f"{stem}: N={N} |V|={V} witness popcount {pop}, columns {ncols}, columns visible at the witness {visible} (f = {f:.5f}); rank of the corrupted call {rank_call1}", flush=True)
    for nbad in (512, 1024, 2048, 4096, 8192, 16384):
        trials = 12; flagged = 0; outs = []
        for seed in range(1, trials + 1):
            def setup(c, nbad=nbad, seed=seed):
                c.L.closure_mutb_set.argtypes = [ctypes.c_long, ctypes.c_long, ctypes.c_long]; c.L.closure_mutb_set(1, nbad, seed)
            r, bad, lines = run(setup)
            ln = [l for l in lines if l.startswith("[ech 1 ")]
            same = bool(ln) and ("out=0" not in ln[0]); flagged += same
            if ln: outs.append(int(ln[0].split("out=")[1].split()[0]))
        pred = 1 - (1 - f) ** nbad
        rows.append({"nbad": nbad, "trials": trials, "flagged_at_the_corrupted_call": flagged, "model_P_detect": round(pred, 4), "bad_output_rows_reported": sorted(outs)})
        print(f"  nbad {nbad:6d} ({nbad / rank_call1:5.2f} x the number of rows): flagged {flagged}/{trials}; model {pred:.4f}; out= values {sorted(outs)}", flush=True)
    out[stem] = {"N": N, "V": V, "witness": w, "witness_popcount": pop, "ncols": ncols, "columns_visible_at_witness": visible, "f": f, "rank_of_corrupted_call": rank_call1, "rows": rows}

# the same quantity at the two window witnesses (arithmetic only: no closure is run)
for tag, Nw, pw, ncw in (("n44_d5", 44, 21, 149986), ("n45_d0", 46, 25, 179447)):
    vis = sum(comb(pw, d) for d in range(5)); fw = vis / ncw
    out["window_" + tag] = {"N": Nw, "witness_popcount": pw, "ncols": ncw, "columns_visible_at_witness": vis, "f": fw,
                            "model_miss_probability": {str(n): (1 - fw) ** n for n in (1, 16, 128, 1024, 66598)}}
    print(f"window {tag}: f = {fw:.4f}; model P(miss) for nbad = 1/16/128/1024/66598: " + ", ".join(f"{(1 - fw) ** n:.3g}" for n in (1, 16, 128, 1024, 66598)))
json.dump(out, open(f"{WS}/outputs/w4_bulk_scale.json", "w"), indent=1, default=str)
