import sys, time, json
sys.path.insert(0, "/Volumes/SSD990/crypto-autoresearcher/src")
from h012_peel_rank import build_system, boolean_null, semireg_rank_pred
from h012c_block_m4ri import monosets_hash
from macaulay_export import macaulay_rows

N, T, TI, D = 15, 3, 0, 6
out = {"n": N, "t": T, "ti": TI, "D": D, "seeds": {}}
for seed in (2026, 2027, 2028):
    t0 = time.time()
    sysret = build_system(N, T, TI, seed)
    if sysret is None:
        out["seeds"][seed] = {"error": "build_system None"}
        continue
    rng, nb, sem_monosets, eq_degs = sysret
    null_monosets = boolean_null(sem_monosets, nb, rng)
    sem_hash = monosets_hash(sem_monosets)
    null_hash = monosets_hash(null_monosets)
    pred, HF = semireg_rank_pred(eq_degs, nb, D)
    sr_pred = int(pred[D])
    build_s = time.time() - t0
    out["seeds"][seed] = {
        "nb": nb, "sem_hash": sem_hash, "null_hash": null_hash,
        "sr_pred_D6": sr_pred, "eq_degs_hist": {str(d): eq_degs.count(d) for d in sorted(set(eq_degs))},
        "build_s": round(build_s, 2),
    }
    print(f"seed={seed} nb={nb} sr_pred_D6={sr_pred} build_s={build_s:.1f}", flush=True)
with open("/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N15-PROBE/work/probe_result.json", "w") as f:
    json.dump(out, f, indent=1)
print("DONE")
