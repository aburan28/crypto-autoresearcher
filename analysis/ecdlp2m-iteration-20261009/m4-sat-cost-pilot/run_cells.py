#!/usr/bin/env python3
"""run_cells.py -- m4-sat-cost-pilot. EXPLORATORY, hypothesis-generating; not program evidence.

Runs WDSat on the labelled instances of one cell and appends one JSON line per
(instance, config) to results/<cell>.jsonl. One solver process at a time.

usage: run_cells.py <cell> <config> [--unsat U] [--sat S] [--timeout s] [--deadline epoch] [--keep-anf N]

configs:  xg       : wdsat_solver -x                     (XOR-Gauss reasoning, branching on all
                                                          unary variables in file order: x's first, then u's)
          xg_b     : wdsat_solver -x -b -m <m> -l <k>    (stock symmetry breaking; COMPLETE only when the
                                                          system is linear in the u's once the x's are fixed, i.e. m = 3)
          xg_symfull : same flags, patched build (see wdsat_io.patch_source) that keeps branching over the u's
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRATCH = Path("/tmp/claude-0/-home-user/f42055f8-3588-569d-b7d9-926d696d2468/scratchpad/m4sat")
ap = argparse.ArgumentParser()
ap.add_argument("cell"); ap.add_argument("config", choices=["xg", "xg_b", "xg_symfull"])
ap.add_argument("--unsat", type=int, default=10); ap.add_argument("--sat", type=int, default=10)
ap.add_argument("--timeout", type=float, default=600); ap.add_argument("--deadline", type=float, default=0)
ap.add_argument("--keep-anf", type=int, default=1)
ap.add_argument("--pilot2", default="/tmp/claude-0/-home-user/f42055f8-3588-569d-b7d9-926d696d2468/scratchpad/iterate/m45closure")
ap.add_argument("--instances", default=str(SCRATCH / "instances"))
a = ap.parse_args()
sys.path.insert(0, str(HERE)); sys.path.insert(0, a.pilot2)
import wdsat_io as W  # noqa: E402
import pilot_lib as L  # noqa: E402
import pilot2_lib as P  # noqa: E402

cell = json.load(open(Path(a.instances) / f"{a.cell}.json"))
m, n, k = cell["m"], cell["n"], cell["k"]
U = [x for x in cell["instances"] if x["nsol"] == 0 and not x["dup_target"]][: a.unsat]
S = [x for x in cell["instances"] if x["nsol"] > 0 and not x["dup_target"]][: a.sat]
outp = HERE / "results" / f"{a.cell}.jsonl"
done = set()
if outp.exists():
    for line in open(outp):
        r = json.loads(line); done.add((r["id"], r["config"]))
flags = {"xg": ["-x"], "xg_b": ["-x", "-b", "-m", str(m), "-l", str(k)], "xg_symfull": ["-x", "-b", "-m", str(m), "-l", str(k)]}[a.config]
variant = "symfull" if a.config == "xg_symfull" else "stock"
(SCRATCH / "anf").mkdir(parents=True, exist_ok=True)
kept = 0
with open(outp, "a") as f:
    for inst in U + S:
        if (inst["id"], a.config) in done:
            continue
        if a.deadline and time.time() > a.deadline:
            print("deadline reached; stopping", flush=True); break
        sysm = P.build_chain(n, k, m, cell["basis"], cell["b"], inst["z"], cell["modulus"])
        text, meta = W.export_anf(sysm)
        anf = SCRATCH / "anf" / f"{inst['id']}.anf"
        anf.write_text(text)
        exe = W.build(meta["sizing"], variant=variant)
        r = W.run(exe, anf, flags, a.timeout)
        sat_ok = None
        if r["status"] == "SAT":
            if set(r["assignment"]) <= {"0", "1"}:
                mask = W.unpermute_assignment(r["assignment"], n, k, m)
                sat_ok = not any(L.eval_system(sysm["equations"], mask))
            else:
                sat_ok = False  # undefined variables in the reported model
        row = {"id": inst["id"], "cell": a.cell, "m": m, "n": n, "k": k, "l": k, "N": sysm["N"], "neq": len(sysm["equations"]),
               "nsol": inst["nsol"], "label": "UNSAT" if inst["nsol"] == 0 else "SAT", "enum_agree": inst["enum_agree"],
               "config": a.config, "flags": flags, "build_variant": variant, "build": exe.parent.name,
               "sizing": meta["sizing"], "anf_sha256": meta["anf_sha256"], "anf_eqs": meta["n_eqs"],
               "anf_nonlinear_monomials": meta["n_nonlinear_monomials"], "timeout_s": a.timeout,
               "exhaustive_2_ml": 2 ** (m * k), "sat_model_verified": sat_ok, "label_agrees_with_solver":
               (None if r["status"] not in ("SAT", "UNSAT") else (r["status"] == ("UNSAT" if inst["nsol"] == 0 else "SAT"))),
               "ts": time.time(), **{kk: v for kk, v in r.items() if kk != "assignment"}}
        f.write(json.dumps(row) + "\n"); f.flush()
        print(f"  {inst['id']} {a.config} label={row['label']} -> {r['status']} conf={r['conflicts']} nodes={r['nodes']} "
              f"fails={r['fails']} wall={r['wall_s']:.2f}s sat_ok={sat_ok} agree={row['label_agrees_with_solver']} {r['notes']}", flush=True)
        if kept < a.keep_anf:
            kept += 1
        else:
            anf.unlink()
