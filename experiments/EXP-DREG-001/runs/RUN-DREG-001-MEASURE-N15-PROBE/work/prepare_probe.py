import sys, time, json, resource
sys.path.insert(0, "/Volumes/SSD990/crypto-autoresearcher/src")
from h012_peel_rank import build_system, boolean_null, semireg_rank_pred
from h012c_block_m4ri import monosets_hash
from macaulay_export import macaulay_rows

def peak_rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**30

N, T, TI, D, SEED = 15, 3, 0, 6, 2026
t0 = time.time()
sysret = build_system(N, T, TI, SEED)
rng, nb, sem_monosets, eq_degs = sysret
null_monosets = boolean_null(sem_monosets, nb, rng)
sem_hash = monosets_hash(sem_monosets)
null_hash = monosets_hash(null_monosets)
t_build = time.time() - t0
print(f"[t={t_build:.1f}s] built systems nb={nb} n_eqs={len(sem_monosets)} rss={peak_rss_gb():.2f}GiB", flush=True)

t1 = time.time()
sem_rows, sem_colidx, sem_nlow = macaulay_rows(sem_monosets, nb, D)
t_sem_rows = time.time() - t1
sem_nrows, sem_ncols = len(sem_rows), len(sem_colidx)
print(f"[t={time.time()-t0:.1f}s] sem macaulay_rows: nrows={sem_nrows} ncols={sem_ncols} "
      f"gen_s={t_sem_rows:.1f} rss={peak_rss_gb():.2f}GiB", flush=True)

result = {
    "n": N, "t": T, "ti": TI, "D": D, "seed": SEED, "nb": nb,
    "n_eqs": len(sem_monosets), "sem_hash": sem_hash, "null_hash": null_hash,
    "build_s": round(t_build, 2), "sem_rows_gen_s": round(t_sem_rows, 2),
    "sem_nrows": sem_nrows, "sem_ncols": sem_ncols,
    "peak_rss_gb_after_sem": round(peak_rss_gb(), 3),
}
with open("/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N15-PROBE/work/prepare_probe_sem_result.json", "w") as f:
    json.dump(result, f, indent=1)
print("SEM_PHASE_DONE", flush=True)

t2 = time.time()
null_rows, null_colidx, null_nlow = macaulay_rows(null_monosets, nb, D)
t_null_rows = time.time() - t2
null_nrows, null_ncols = len(null_rows), len(null_colidx)
print(f"[t={time.time()-t0:.1f}s] null macaulay_rows: nrows={null_nrows} ncols={null_ncols} "
      f"gen_s={t_null_rows:.1f} rss={peak_rss_gb():.2f}GiB", flush=True)
result.update({
    "null_rows_gen_s": round(t_null_rows, 2),
    "null_nrows": null_nrows, "null_ncols": null_ncols,
    "peak_rss_gb_after_null": round(peak_rss_gb(), 3),
    "total_elapsed_s": round(time.time() - t0, 2),
})
with open("/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N15-PROBE/work/prepare_probe_sem_result.json", "w") as f:
    json.dump(result, f, indent=1)
print("ALL_DONE", flush=True)
