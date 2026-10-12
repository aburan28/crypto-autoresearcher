#!/usr/bin/env python3
"""Run implementation B (indep_verify.py / indep_verify_t3.py) at D = 4 on named
instances, `workers` at a time, one output file verify/out_b5_<name>.txt each.
usage: b_queue.py workers name..."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
here = os.path.dirname(os.path.abspath(__file__)); res = os.path.join(here, "..", "results")
recs = {r["name"]: r for f in ("instances.json", "instances_sat.json", "instances_t3.json")
        for r in json.load(open(os.path.join(res, f)))}
def run(name):
    r = recs[name]
    script = "indep_verify_t3.py" if r.get("t") == 3 else "indep_verify.py"
    args = ["nice", "-n", "5", "python3", os.path.join(here, script), str(r["n"]), r["modulus_hex"], str(r["a2"]),
            r["a6_hex"], r["z_hex"], "4"] + r["V_basis_hex"]
    with open(os.path.join(here, f"out_b5_{name}.txt"), "w") as fh:
        subprocess.run(args, stdout=fh, stderr=subprocess.STDOUT)
    return name
with ThreadPoolExecutor(int(sys.argv[1])) as ex:
    for name in ex.map(run, sys.argv[2:]):
        print("finished", name, flush=True)
