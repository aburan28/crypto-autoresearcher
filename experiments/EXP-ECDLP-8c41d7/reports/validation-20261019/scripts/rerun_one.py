#!/usr/bin/env python3
"""Re-run one (m=4, L, inst) job with the committed launcher module for a subset of arms.
usage: rerun_one.py <L> <inst> <arms,comma> <out.jsonl>
Job dict is built exactly as block_order_grid.main() builds it (same seed derivation, timeout 600)."""
import hashlib, json, sys, time
sys.path.insert(0, "/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-8c41d7")
import block_order_m4 as bm
bog = bm.bog
L, inst, arms, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3].split(","), sys.argv[4]
plan = json.load(open("/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-8c41d7/trial-plan.json"))
seed = int(hashlib.sha256(f"{plan['seed']}|4|{L}|{inst}".encode()).hexdigest()[:12], 16)
kind = "planted" if inst < plan["planted_per_cell"] else "random"
job = dict(m=4, L=L, inst=inst, kind=kind, seed=seed, timeout=plan["timeout_s"], arms=arms)
t0 = time.time(); r = bog.run_instance(job)
r["rerun_elapsed_s"] = round(time.time() - t0, 1)
open(out, "a").write(json.dumps(r) + "\n")
print(json.dumps({k: v.get("status") for k, v in r["results"].items()}), r["rerun_elapsed_s"], flush=True)
