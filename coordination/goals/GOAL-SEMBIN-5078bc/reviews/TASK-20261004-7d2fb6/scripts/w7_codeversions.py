#!/usr/bin/env python3
"""w7_codeversions.py -- joint W7 (3): build closure.c as it stood at each of the three lane commits (d6a21306ee, a6d3b37e17, 9096320e22) and at HEAD (5e1aa460cb) from the git blobs, against my M4RI
release-20240729 build, and compare rank / standard count / leading-monomial digest / per-iteration profile on the same instances and memory caps. 'Left the rows produced unchanged' predicts equality of
everything except batch-layout-dependent quantities (the partial rank of an early stop). Scratch."""
import os, sys, json, subprocess, hashlib
SP, WS = os.environ["SP"], os.environ["WS"]; W = f"{SP}/work"; REPO = "/home/user/crypto-autoresearcher"
sys.path.insert(0, f"{WS}/scripts"); import vclos
from math import comb
PFX = os.environ["M4RI_PREFIX"]
vers = {"d6a21306ee": None, "a6d3b37e17": None, "9096320e22": None, "5e1aa460cb": None}
os.makedirs(f"{W}/ver", exist_ok=True)
for c in vers:
    src = subprocess.run(["git", "-C", REPO, "show", f"{c}:experiments/EXP-SEMBIN-7e1371/code/closure.c"], capture_output=True).stdout
    open(f"{W}/ver/closure_{c}.c", "wb").write(src)
    so = f"{W}/ver/libclosure_{c}.so"
    r = subprocess.run(f"gcc -O2 -w -fPIC -shared -I{PFX}/include {W}/ver/closure_{c}.c -o {so} -L{PFX}/lib -Wl,-rpath,{PFX}/lib -lm4ri", shell=True, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    vers[c] = so
    print(c, "closure.c sha256", hashlib.sha256(src).hexdigest()[:16], "built")
rows = []
for stem in ("chained_n9_m3_t3_k4_d0", "chained_n20_m2_t2_k10_d3", "null_n16_m2_t2_k8_d0", "null_n18_m2_t2_k9_d0", "chained_n16_m2_t2_k8_d0", "chained_n10_m3_t3_k4_d0", "null_n12_m2_t2_k9_d0", "chained_n9_m3_t3_k5_d0"):
    s = json.load(open(f"{W}/inst/{stem}.json")); N = s["N"]; ncols = sum(comb(N, d) for d in range(5))
    for capx in (8, 25, 400):
        cap = capx * ncols * ncols / 8 / 2**30
        res = {}
        for c, so in vers.items():
            cl = vclos.Clos(so)
            # the older libraries lack closure_ech_faults/closure_resumed in some versions: vclos requires them; guard
            r = cl.run(N, 4, s["equations"], mem_cap_gb=cap)
            res[c] = r
        base = res["5e1aa460cb"]
        for c, r in res.items():
            if r["rc"] != 0 or base["rc"] != 0:
                rows.append({"stem": stem, "capx": capx, "ver": c, "rc": r["rc"]}); continue
            early = r["contains_one"] and r["rank"] < r["ncols"]
            same = (r["std"] == base["std"] and r["profile"] == base["profile"] and r["contains_one"] == base["contains_one"] and (early or (r["rank"] == base["rank"] and r["lm_sha256"] == base["lm_sha256"])))
            rows.append({"stem": stem, "capx": capx, "ver": c, "rc": 0, "same_as_head_modulo_early_stop": same, "early_stop_partial_rank": early, "rank": r["rank"], "std": r["std"], "lm": r["lm_sha256"][:12]})
        print(f"{stem:26s} cap x{capx:<4d}", {c: (r["rank"] if r["rc"] == 0 else f"rc{r['rc']}") for c, r in res.items()}, "| all equal:", all(x.get("same_as_head_modulo_early_stop", True) for x in rows[-4:]), flush=True)
json.dump(rows, open(f"{WS}/outputs/w7_codeversions.json", "w"), indent=1)
done = [r for r in rows if r["rc"] == 0]
print("compared", len(done), "completed (instance, cap, version) runs;", "differences from HEAD:", sum(1 for r in done if not r["same_as_head_modulo_early_stop"]))
