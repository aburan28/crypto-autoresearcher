#!/usr/bin/env python3
"""w5_singlelevel.py -- joint W5 (1) single-level path (Q-B relevance): closure.c with max_iter = 1 (what closure_cert.macaulay_single_level runs) against my reference rank of the
single-level Macaulay matrix of the ORIGINAL generators (g and mu*g, 1 <= |mu| <= D - deg g). Several caps (batch boundaries). Also confirms the recorded single-level
field 'rows' = ngens + n_prod of the original generators. Usage: w5_singlelevel.py STEM[:D]..."""
import sys, os, json, subprocess
from math import comb
SP, WS = os.environ["SP"], os.environ["WS"]; W = f"{SP}/work"
sys.path.insert(0, f"{WS}/scripts"); import vclos
libs = {"orig": f"{W}/build/libclosure_orig.so", "STRESS32": f"{W}/mut/libclosure_STRESS32.so"}
for spec in sys.argv[1:]:
    stem, _, dd = spec.partition(":"); D = int(dd) if dd else 4
    s = json.load(open(f"{W}/inst/{stem}.json")); N = s["N"]
    ref = subprocess.run([f"{W}/refclos", "macaulay", f"{W}/inst/{stem}.sys", str(D), "x"], capture_output=True, text=True).stdout.strip()
    kv = dict(x.split("=") for x in ref.split()); rr = int(kv["rank"])
    ncols = sum(comb(N, d) for d in range(D + 1))
    for name, lib in libs.items():
        c = vclos.Clos(lib)
        for capx in (4, 12, 100):
            cap = capx * ncols * ncols / 8 / 2**30
            r = c.run(N, D, s["equations"], max_iter=1, mem_cap_gb=cap)
            nprod_ref = int(kv["products"]); rows_expected = len(s["equations"]) + nprod_ref
            print(f"{stem:26s} D={D} {name:9s} cap=x{capx:<4d} rc={r['rc']} rank={r['rank']} reference={rr} equal={r['rank']==rr} | profile rows {r['profile'][-1][0] if r['profile'] else None} expected ngens+n_prod = {rows_expected}", flush=True)
