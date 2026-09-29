import sys, time, json, resource
sys.path.insert(0, "/Volumes/SSD990/crypto-autoresearcher/src")
from h012_peel_rank import build_system, boolean_null
from h012c_block_m4ri import monosets_hash
from macaulay_export import macaulay_rows

def peak_rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**30

N, T, TI, D, SEED = 15, 3, 0, 6, 2026
t0 = time.time()
sysret = build_system(N, T, TI, SEED)
rng, nb, sem_monosets, eq_degs = sysret
null_monosets = boolean_null(sem_monosets, nb, rng)
null_hash = monosets_hash(null_monosets)
del sem_monosets
t_build = time.time() - t0
print(f"[t={t_build:.1f}s] built null system nb={nb} rss={peak_rss_gb():.2f}GiB", flush=True)

t1 = time.time()
null_rows, null_colidx, null_nlow = macaulay_rows(null_monosets, nb, D)
t_null_rows = time.time() - t1
null_nrows, null_ncols = len(null_rows), len(null_colidx)
peak = peak_rss_gb()
print(f"[t={time.time()-t0:.1f}s] null macaulay_rows: nrows={null_nrows} ncols={null_ncols} "
      f"gen_s={t_null_rows:.1f} rss={peak:.2f}GiB", flush=True)
result = {
    "n": N, "t": T, "ti": TI, "D": D, "seed": SEED, "nb": nb,
    "null_hash": null_hash, "build_s": round(t_build, 2),
    "null_rows_gen_s": round(t_null_rows, 2),
    "null_nrows": null_nrows, "null_ncols": null_ncols,
    "peak_rss_gb": round(peak, 3),
}
with open("/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N15-PROBE/work/prepare_probe_null_result.json", "w") as f:
    json.dump(result, f, indent=1)
print("NULL_PHASE_DONE", flush=True)
