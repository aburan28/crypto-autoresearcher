# SUPERSEDED

Kept immutable per the run-record discipline; not deleted.

**Defect (distinct from RUN-VOLC-sr1-sr5-plus-t5-gate's).**
`harness.exp_icinv_fullgroup.measure_curve_all_arms` iterates the MODULE-LEVEL
constants `fg.SEEDS` / `fg.TARGET_COUNTS` (the frozen EXP-ICINV-4d33aa grid:
seeds `[20260807, 20260808, 11235813]`, T `[100, 400, 1600]`) to decide which
`(arm, seed, T)` keys to read out of `pkg.targets` -- it does NOT take a
seeds/T parameter of its own, and is unaffected by the `seeds=`/
`target_counts=` kwargs passed to `build_curve_package`. This run's driver
declared this contract's own 8-seed grid
(`replication.seeds`, spec) and passed it into `build_curve_package`, but
never overrode the module globals `measure_curve_all_arms` actually reads.
Consequence: only the single seed (`11235813`) and the two T values (`100`,
`400`) common to BOTH grids were ever scored -- 1 of the 8 declared seeds,
silently, no error, no exception. This violates C-SEEDS ("full per-seed
distribution... at least the declared seed count") for BOTH the SR3 rate
measurement (`per-vertex-measurements.json`) and the SR4 matched-null cells
(`matched-null-verdict.json`) in this run.

Found by inspecting `matched-null-verdict.json`'s cell keys after the run
completed: only `seed=11235813` appears, where 8 seeds x 3 fb-sizes x 2 T
= 48 cells were expected per null arm and only 6 exist.

**Correction.** The superseding run `RUN-VOLC-sr1-sr5-plus-t5-gate-v3`
overrides `fg.SEEDS = SEEDS` and `fg.TARGET_COUNTS = TARGET_COUNTS` (this
contract's own declared grid) once, at driver start, before any
`build_curve_package`/`measure_curve_all_arms` call, and rebuilds every stage
from that point. SR1, SR2 family construction/census and the
kernel-rationality check are unaffected by this defect (they never call
`measure_curve_all_arms`) and are numerically identical between this run and
v3.

**Disposition.** `status` here is `completed` as originally written (the
immutable manifest is not edited); this file records that the run is
superseded and its SR3/SR4 seed coverage should not be relied on. v3 is the
run of record for SR3/SR4.
