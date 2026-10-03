#!/usr/bin/env python3
"""Regenerate the instances of the dossier and record exact closure outcomes.

For each spec (basis, zmode, seed, n, k, count): regenerate the unsatisfiable
instances with gen2.py (deterministic), then for D = 2, 3, 4 run the exact
closure (lfdclose2) until 1 in W_D, recording dims, iterations and time.
Results are cached per instance in results/cache/<name>.json, so the script
can be interrupted and resumed.
usage: tabulate.py [--maxN N]   (skip D=4 when 2k > maxN)"""
import json, os, subprocess, sys, time

SPECS = [
    # (label prefix, basis, zmode, seed, n, k, count)
    ("P", "poly", "curve", 1, 17, 9, 6),
    *[("P", "poly", "curve", 7, n, (n + 1) // 2, 4) for n in (19, 21, 23, 25, 27)],
    *[("P", "poly", "curve", 7, n, (n + 1) // 2, 3) for n in (29, 31, 33)],
    ("P", "poly", "curve", 7, 35, 18, 2),
    *[("R", "rand", "curve", 11, n, (n + 1) // 2, 3) for n in (11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31)],
    *[("R", "rand", "curve", 13, n, (n + 1) // 2, 2) for n in (33, 35, 37, 39)],
    *[("T", "tr0", "curve", 21, n, (n + 1) // 2, 2) for n in (29, 31, 33)],
    *[("U", "rand", "rand", 17, n, (n + 1) // 2, 2) for n in (33, 35)],
    ("S", "poly", "rand", 40, 40, 20, 2),
]
maxN = int(sys.argv[sys.argv.index("--maxN") + 1]) if "--maxN" in sys.argv else 99
os.makedirs("results/cache", exist_ok=True); os.makedirs("inst", exist_ok=True)

def parse(out):
    res = {}
    for line in out.splitlines():
        tok = line.split()
        if not tok: continue
        if tok[0].startswith("M") and tok[0].endswith("_dims"):
            d = int(tok[0][1:-5]); res["M_dims"] = list(map(int, tok[1:d + 2])); res["M_one"] = int(tok[d + 3])
        if tok[0].startswith("W") and tok[0].endswith("_dims"):
            d = int(tok[0][1:-5]); res["W_dims"] = list(map(int, tok[1:d + 2])); res["W_one"] = int(tok[d + 3])
            res["iters"] = int(tok[d + 5]); res["ncols"] = int(tok[d + 7])
    return res

allres = []
for (lab, basis, zmode, seed, n, k, count) in SPECS:
    d = f"inst/{basis}_{zmode}_{seed}_n{n}"
    meta = f"{d}/meta_n{n}_l{k}_{basis}_{zmode}_{seed}_unsat.json"
    if not os.path.exists(meta):
        subprocess.run(["python3", "gen2.py", str(n), str(k), str(count), str(seed), basis, "unsat", zmode, d], check=True, stdout=subprocess.DEVNULL)
    for idx, m in enumerate(json.load(open(meta))):
        name = f"{lab}{n}{'abcdefgh'[idx]}"
        cf = f"results/cache/{name}.json"
        rec = json.load(open(cf)) if os.path.exists(cf) else dict(name=name, n=n, k=k, basis=basis, zmode=zmode, seed=seed, index=idx,
                   modulus_hex=format(m["f"], "x"), a2=m["a2"], a6_hex=format(m["a6"], "x"), z_hex=format(m["xR"], "x"),
                   V_basis_hex=[format(b, "x") for b in m["basis"]], boolean_solutions=m["nsol"], closures={})
        for D in (2, 3, 4):
            if str(D) in rec["closures"]:
                if rec["closures"][str(D)].get("W_one"): break
                continue
            if D == 4 and 2 * k > maxN: break
            t0 = time.time()
            out = subprocess.run(["./lfdclose2", str(D)], stdin=open(m["file"]), capture_output=True, text=True).stdout
            r = parse(out); r["seconds"] = round(time.time() - t0, 1)
            rec["closures"][str(D)] = r
            json.dump(rec, open(cf, "w"), indent=1)
            if r.get("W_one"): break
        ones = [int(D) for D, r in rec["closures"].items() if r.get("W_one")]
        tested = sorted(int(D) for D in rec["closures"])
        rec["d_ref_exact"] = min(ones) if ones and all(not rec["closures"][str(D)]["W_one"] for D in range(2, min(ones))) else None
        rec["d_ref_lower_bound"] = (max(tested) + 1) if not ones else None
        json.dump(rec, open(cf, "w"), indent=1)
        allres.append(rec)
        print(name, "d_ref =", rec["d_ref_exact"], "lower bound", rec["d_ref_lower_bound"], flush=True)
import glob
allres = [json.load(open(f)) for f in sorted(glob.glob("results/cache/*.json"))]
json.dump(allres, open("results/instances.json", "w"), indent=1)
