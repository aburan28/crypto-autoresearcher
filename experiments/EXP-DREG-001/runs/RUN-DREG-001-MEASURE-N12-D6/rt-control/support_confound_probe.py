# RED-TEAM control (RT, read-only w.r.t. producer cells; writes only under rt-control/).
# Purpose: quantify the ncols/support confound in the n=12 D6 sem-vs-null deficit.
#   - Independently rebuild the EXACT sem and null systems from the committed seed
#     (seed=2026, t=3, ti=0) and verify their system hashes against the receipts.
#   - Verify the committed ncols (sem 174035, null 190051) and sr_pred (156520).
#   - Confirm sem support is a SUBSET of null support, and give the degree histogram
#     of the monomials present in null but ABSENT from sem (the support gap).
#   - Recompute the pure-arithmetic support-independent deficit lower bound.
# This does NOT recompute any GF(2) rank; it is a support/monomial-set audit only.
import sys, os, json, time
from pathlib import Path
from collections import Counter
from math import comb

SRC = Path("/Volumes/Volume/crypto-autoresearcher-worktrees/claude-dreg-law/src")
sys.path.insert(0, str(SRC))

from h012_peel_rank import build_system, boolean_null, semireg_rank_pred
from h012c_block_m4ri import monosets_hash
from macaulay_export import macaulay_rows
from ic_first_fall_fast import mono_deg

N, T, TI, SEED, D = 12, 3, 0, 2026, 6
COMMIT = {
    "sem_hash": "c47d17c3fd70d5d81127e8d37e21441883f720ca10187f57a3aeb47bfe3ba818",
    "null_hash": "f2f610730a7155933be2afe2d979c8535e1f35f5c0c5ddb246fabe717b147344",
    "sem_ncols": 174035, "null_ncols": 190051, "sr_pred": 156520,
    "sem_rank": 138573, "null_rank": 156520, "sem_deficit": 17947,
}

t0 = time.time()
sysret = build_system(N, T, TI, SEED)
assert sysret is not None, "build_system failed"
rng, nb, sem_monosets, eq_degs = sysret
# null uses the SAME rng state returned by build_system (matches producer order).
null_monosets = boolean_null(sem_monosets, nb, rng)

sem_hash = monosets_hash(sem_monosets)
null_hash = monosets_hash(null_monosets)

pred, HF = semireg_rank_pred(eq_degs, nb, D)
sr_pred = int(pred[D])

# Column supports (monomial sets) actually appearing in each degree-D Macaulay matrix.
sem_rows, sem_colidx, _ = macaulay_rows(sem_monosets, nb, D)
del sem_rows
null_rows, null_colidx, _ = macaulay_rows(null_monosets, nb, D)
del null_rows

sem_cols = set(sem_colidx.keys())
null_cols = set(null_colidx.keys())

full_space = sum(comb(nb, d) for d in range(0, D + 1))
missing = null_cols - sem_cols          # in null support, absent from sem support
sem_extra = sem_cols - null_cols        # in sem support, absent from null (should be empty if null full)

deg_hist = lambda S: {d: c for d, c in sorted(Counter(mono_deg(m) for m in S).items())}

out = {
    "cell": {"n": N, "t": T, "ti": TI, "seed": SEED, "D": D, "nb": nb},
    "hash_check": {
        "sem_hash": sem_hash, "sem_hash_matches_receipt": sem_hash == COMMIT["sem_hash"],
        "null_hash": null_hash, "null_hash_matches_receipt": null_hash == COMMIT["null_hash"],
    },
    "eq_degs_hist": {d: eq_degs.count(d) for d in sorted(set(eq_degs))},
    "ncols_check": {
        "sem_ncols": len(sem_cols), "sem_matches_receipt": len(sem_cols) == COMMIT["sem_ncols"],
        "null_ncols": len(null_cols), "null_matches_receipt": len(null_cols) == COMMIT["null_ncols"],
        "full_squarefree_space_deg_le_D": full_space,
        "null_is_full_support": len(null_cols) == full_space,
    },
    "sr_pred_check": {"sr_pred_recomputed": sr_pred,
                      "matches_receipt": sr_pred == COMMIT["sr_pred"]},
    "support_relation": {
        "sem_subset_of_null": len(sem_extra) == 0,
        "sem_only_monomials": len(sem_extra),
        "support_gap_null_minus_sem": len(missing),
    },
    "degree_histograms": {
        "sem_support": deg_hist(sem_cols),
        "null_support": deg_hist(null_cols),
        "missing_from_sem": deg_hist(missing),
    },
    "arithmetic_support_correction": {
        "reported_deficit_vs_sr_pred": COMMIT["sr_pred"] - COMMIT["sem_rank"],
        "support_gap": len(missing),
        "null_restricted_to_sem_support_rank_lower_bound": COMMIT["null_rank"] - len(missing),
        "support_independent_deficit_lower_bound":
            (COMMIT["null_rank"] - len(missing)) - COMMIT["sem_rank"],
        "note": ("rank(null|_sem-support) >= null_rank - support_gap by column-deletion; "
                 "sem_rank strictly below this lower bound => that many syzygies are "
                 "NOT attributable to the reduced column support."),
    },
    "elapsed_s": round(time.time() - t0, 1),
}
print(json.dumps(out, indent=1))
outp = Path(__file__).parent / "support_confound_probe.json"
with open(outp, "w") as f:
    json.dump(out, f, indent=1)
print(f"\nwrote {outp}", flush=True)
