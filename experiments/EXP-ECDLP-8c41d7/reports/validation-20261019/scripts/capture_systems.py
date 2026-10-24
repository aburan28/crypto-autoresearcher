#!/usr/bin/env python3
"""Rebuild an EXP-ECDLP-8c41d7 instance with the COMMITTED code and dump the three msolve input systems.

usage: capture_systems.py <variant: base|p19> <L> <inst> <outdir> [arms]

Uses the committed launcher modules unchanged (block_order_m4.py, or block_order_m4_p19.py for the AMD-03 prime);
only `run_ms` is replaced so that, instead of solving, the (variables, polys, p, extra-args) are written to
<outdir>/<arm>.ms in msolve's input format.  Also records p, b, seed and the planted point via a second pass.
"""
import importlib, json, os, sys, hashlib, random

EXPDIR = "/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-8c41d7"
variant, L, inst, outdir = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
arms = sys.argv[5].split(",") if len(sys.argv) > 5 else ["A_elim_ms", "A_drl_ms", "B_ms"]
os.makedirs(outdir, exist_ok=True)
sys.path.insert(0, EXPDIR)
mod = importlib.import_module("block_order_m4" if variant == "base" else "block_order_m4_p19")
bog = mod.base.bog if variant == "p19" else mod.bog
pkm = bog.pkm

captured = {}


def fake_run_ms(vars_, polys, p, extra, timeout):
    # which arm? A_elim has extra=['-e', n]; A_drl has vars starting with x; B has only x vars
    arm = "A_elim_ms" if extra else ("B_ms" if all(v.startswith("x") for v in vars_) else "A_drl_ms")
    path = os.path.join(outdir, f"{arm}.ms")
    with open(path, "w") as f:
        f.write(",".join(vars_) + "\n" + str(p) + "\n" + ",\n".join(polys) + "\n")
    captured[arm] = dict(vars=vars_, extra=extra, npolys=len(polys), p=p)
    return dict(status="skipped", wall_s=0.0), None


bog.run_ms = fake_run_ms
plan = json.load(open(f"{EXPDIR}/trial-plan.json"))
seed = int(hashlib.sha256(f"{plan['seed']}|4|{L}|{inst}".encode()).hexdigest()[:12], 16)
kind = "planted" if inst < plan["planted_per_cell"] else "random"
job = dict(m=4, L=L, inst=inst, kind=kind, seed=seed, timeout=600, arms=arms)
out = bog.run_instance(job)
meta = dict(seed=seed, kind=kind, p=out["p"], p_bits=out["p_bits"], b=out["b"], captured=captured, status=out["results"])
json.dump(meta, open(os.path.join(outdir, "meta.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in meta.items() if k != "status"}, indent=1)[:1500])
