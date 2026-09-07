# Implementation note: Stage B'' (PRODUCTION) -- TASK-20260907-ca8b6c

Experiment: `EXP-ECDLP-6ac801`, `specification.v3.yaml` (`status: approved`,
`approved_by: coordinator`, `frozen: true`, `execution_authorized: true`).
Executor task: `TASK-20260907-ca8b6c`. This note documents what was built and
run; it draws no conclusion about G3-style feasibility at any cell and
classifies no cell PASS/FAIL, per the task's own constraints.

## What was built

`experiments/EXP-ECDLP-6ac801/source/run_stageb_v3.py`, a new driver
alongside (not replacing) v1/v2's own `run_stageb.py`. It extends that
driver's approach -- one invocation sweeps one seed over the full `a_grid`,
reusing `experiments/EXP-ECDLP-612fb1/source_v2/instrument.py` (commit
`22e80f13361a6eb307864c52f51740db419e9e54`) for the exact-basin core (DP
predicate, walk step, pool generation) -- to the full v3 grid and the v3
control arms:

- `--n-bits {20,24}` selects the scale (`run_stageb.py` hardcoded `N=2^24`
  only); `T`, `T_sel = T/2`, `T4 = T/4`, `T8 = T/8` are read from
  `instrument.T_OF_NBITS` (64/256 respectively), matching
  `specification.v3.yaml definitions` item 4 (T is a table lookup, never
  `round(N**(1/3))` -- there is no such expression anywhere in this file or
  in `instrument.py`).
- `a_grid = {1/16, 1/8, 3/16, 1/4}`, `r = 2` fixed, unchanged from v1/v2.
- Per (N, a, seed) this script computes and reports, as **raw measured
  fields only** (no aggregation across seeds, no pass-count, no G3-style
  verdict, no PASS/FAIL classification, no comparison to Stage A''):
  - `exact_top_T_sel_share`, `exact_top_T_share`, `exact_top_T4_share`,
    `exact_top_T8_share` (`Basins.top_share`).
  - `static_T_r2_exact_coverage`, via the published Bernstein-Lange weight
    `weight_d = S_d + 4*W*h_d` (`definitions` "STATIC(T)_r pool-selection
    weight formula") over the `r*T`-DP pool, top-T selection by
    `instrument.numpy_select` (weight desc / tiebreak-key asc, tiebreak keys
    drawn from `P.seed_tiebreak` exactly as `run_stageb.py` already does).
  - `margin`, `margin_T4`, `margin_T8` (share minus `static_T_r2_exact_coverage`
    at T_sel, T/4, T/8 respectively -- the raw readings control (m)/DECAY-TSEL
    and its own tail check need; this script does not itself decide whether
    (m) fires).
  - `cycle_mass`, `capped_mass`, `capped_walks`, `residual_fraction =
    (cycle_mass + capped_mass) / N` -- read directly off `Basins.cycle_mass`,
    `Basins.capped_mass` and `PoolSnapshot.capped_walks`, per `definitions`
    items 1-2 (the WALK CAP and EXACT-BASIN RESIDUAL MASS ACCOUNTING).
  - `rho_oracle`: the smallest `T_sel'/T` at which `share_top(T_sel')` would
    reach `static_T_r2_exact_coverage`, read off the cumulative sum of
    basin sizes sorted descending against the coverage threshold.
  - `tie_count_at_T_th_weight`: count of pool entries exactly equal (float64
    equality) to the T-th-largest selection weight -- the D4 tail-check
    input.
  - The four control-arm raw quantities:
    - **(i) NULL-ORACLE-RAND (uniform), gating null**: a uniformly random
      `T_sel`-subset of the DPs of the *whole exact partition* (`basins.dps`,
      not the r*T pool), coverage read off the same basin-size array;
      `control_i_null_oracle_rand_uniform_margin` = that coverage minus
      `static_T_r2_exact_coverage`.
    - **(j) NULL-ORACLE-RAND (size-biased), diagnostic**: same substitution,
      subset drawn with probability proportional to basin size
      (`np.random.Generator.choice(..., p=probs)`).
    - **(k) NULL-RANDSEL, non-gating**: a uniformly random T-subset of the
      r*T precomputation pool (not the whole partition), coverage compared
      against `static_T_r2_exact_coverage`.
    - **(n) NULL-SHUF, diagnostic**: the pool's own basin sizes (`Basins.size`
      at the pool DPs' indices) permuted by a fresh RNG, holding the size
      multiset and the weight-based selection (`order`, from the *unshuffled*
      weights) fixed, then `cov_static_shuf` read as the sum of the shuffled
      sizes at the selected positions divided by N;
      `control_n_null_shuf_margin_diagnostic` = `exact_top_T_sel_share -
      cov_static_shuf`.
    All four control-arm RNGs use a dedicated seed derivation
    (`null_seed(seed, n_bits, a, tag)`) disjoint from every instrument stream
    (walk key, DP key, targets, phi, null_a, tiebreak), so their randomness
    is independent of the primary measurement's own randomness.
  - The three structural self-checks (o1)/(o2)/(o3), reported per cell as
    `SATISFIED`/`VIOLATED` (never as a control firing), per
    `v3_r2_addendum.required_artifacts_r2`'s three-part scheme:
    - (o1) `sum_d b(d) + cycle_mass + capped_mass == N` exactly, and every DP
      has `b(d) >= 1`.
    - (o2) `share_top(T8) <= share_top(T4) <= share_top(T_sel) <=
      share_top(T) <= 1.0` and `cov_static <= share_top(T)` (subsumes
      control (c), the exact-coverage non-exceedance check).
    - (o3) `margin(T_sel) > margin(T4) > margin(T8)`.
    A violation of any of (o1)-(o3), or the exceedance condition itself,
    marks that cell `completed_invalid` in the per-cell record and marks the
    whole run's `any_cell_invalid` flag, per `stopping_rules`; **none
    occurred** (see Observations below).

`run_stageb_v3.py` does **not** compute any per-a pass-count, any G3-style
feasibility verdict, any FIRED/NOT-FIRED determination for controls
(a)/(b)/(d)/(e)/(f)/(g)/(h)/(l)/(m) (which require aggregation across the 25
seeds and, for (h), the a = 1/4 committed reference), or any comparison
against Stage A''. Per the task's own constraints and
`specification.v3.yaml stage_plan_v3`, that aggregation and analysis is
Stage C'', a separate later Coordinator step.

## Orchestration (not a committed artifact)

A thin, non-frozen harness (`orchestrate_v3.py`, kept in the executor's own
scratchpad, not under `experiments/`) invoked `run_stageb_v3.py` once per
`(n_bits, seed)` pair -- 25 seeds at N = 2^20 (run first, per
`stopping_rules`' explicit ordering requirement), then 25 seeds at N = 2^24
-- strictly sequentially (`maximum_workers = 1`, machine protection), writing
one immutable run directory per invocation with `manifest.yaml`,
`command.txt`, `environment.json`, `stdout.log`, `stderr.log`,
`raw-result.json` and `summary.json`, per `docs/evidence-and-reproducibility.md`.
This harness is process glue, not a frozen measurement instrument, and is
not among this task's deliverables; it exists so the executor's own commands,
environment and outputs are captured identically across 50 invocations rather
than by hand.

## Runs produced

50 immutable run directories under `experiments/EXP-ECDLP-6ac801/runs/`:
`RUN-ECDLP-6ac801-v3-n20-s01` .. `RUN-ECDLP-6ac801-v3-n20-s25` (N = 2^20,
seeds 1-25, run first) and `RUN-ECDLP-6ac801-v3-n24-s01` ..
`RUN-ECDLP-6ac801-v3-n24-s25` (N = 2^24, seeds 1-25). None of
`RUN-ECDLP-6ac801-{001..006}` (v1/v2's own immutable records) was touched.

Each manifest cites `commit_executed_against:
1ddd3b649ddca99442246e9934e23a7300c615f8` (the branch tip at the start of
this task, and unchanged at its end -- verified: `git rev-parse HEAD` after
all 50 runs still returns that same commit, and `git status --short` shows
only new, untracked files under this task's own write scope: the new driver
and the 50 new run directories; no tracked file, and no byte of
`RUN-ECDLP-6ac801-{001..006}/`, `specification.yaml`, `specification.v2.yaml`
or `specification.v3.yaml`, was modified).

## Observations (raw, no interpretation)

- 50/50 runs `completed_valid`; 0 `completed_invalid`, 0 `failed_infrastructure`.
- Across all 200 (N, a, seed) cells produced: 0 self-check violations
  ((o1)/(o2)/(o3) all `SATISFIED` everywhere) and 0 exceedances (control
  (c)/(o2)'s non-exceedance clause held everywhere).
- The largest observed `residual_fraction` at N = 2^20 was ~0.0232 (a = 1/4,
  seed 2: cycle_mass 24303, capped_mass 0, capped_walks 4); at N = 2^24 it
  was ~0.0075 (a = 1/4, seed 23: cycle_mass 126501, capped_mass 107,
  capped_walks 6). Both are individual observations, not a pattern this note
  characterizes further; the tail-check aggregation across all cells at both
  scales is a Stage C'' function.
- The largest observed tie count at the T-th largest selection weight, over
  all 200 cells, was 9 pool entries.
- No expectation is stated for any of these numbers; they are reported
  exactly as measured, per `preregistered_prediction`'s
  `what_this_contract_states_about_the_open_cells: NOTHING`.

## Protocol deviations

None identified. The N = 2^20 arm ran to completion before any N = 2^24
invocation started, per the stopping-rules ordering requirement. No file
under `experiments/EXP-ECDLP-6ac801/runs/RUN-ECDLP-6ac801-{001..006}/` or any
frozen specification file was read for anything but the citation of the
commit hash and the T-table values already quoted verbatim in
`specification.v3.yaml` itself; this task did not open
`coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-4433c1/reviews/TASK-20260907-7afa98/`
(Stage A'''s own sealed cells/summary), per the handoff's own constraint.

## What this note does not do

It does not classify any cell PASS/FAIL, does not compute or report any
per-a pass-count or G3-style feasibility verdict, does not determine
FIRED/NOT-FIRED for any control, and does not compare this reading against
Stage A''. Those are Stage C'' functions and a separate, later Coordinator
step.
