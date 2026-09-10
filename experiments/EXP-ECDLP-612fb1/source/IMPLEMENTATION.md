# EXP-ECDLP-612fb1 implementation note (Executor, TASK-20260906-3623b9)

Written inside `source/` because the task's write_scope is `runs/`, `source/`
and the task directory; the experiment-root `implementation.md` is outside it
and is left to the Coordinator. Observations only; nothing here interprets.

## Layout

| file | role |
|---|---|
| `instrument.py` | keyed random function `f(x) = mix64(x XOR K) mod N` (splitmix64 finaliser), DP predicate `mix64(x XOR K_dp) < floor(2^64/W)`, vectorised walker, exact basins by pointer jumping, Bernstein-Lange pool generation, counted top-`T_sel` selection, the ONE arm engine (`run_arm`) with arm selection by `ArmConfig`, Wilson intervals, `C_max(a)`, Borel survival / cutoff / order-statistic band |
| `run_generic.py` | one generic cell `(N, a, seed)`: basins and G1 quantities, then the G2 fixture, then every arm; writes `raw-result.json`, `summary.json`, `cost_table.json`, `basin_histogram.json.gz` |
| `curve.py` | toy prime-order curve: scalar (solver-side) and vectorised (walk-side) group law, `r = 32` adding walk, point enumeration, exact basins on the curve |
| `verify_certificate.py` | INDEPENDENT verifier: own extended-Euclid inverse, own Montgomery ladder, own primality bases; the only code that reads the seeded logarithm |
| `curve_search.py` | Stage 3 curve search (seed 1000) with independent record verification |
| `run_curve.py` | one certified curve cell (seed in {1,2,3}) through the same `run_arm` |
| `analysis.py` | Stage 4: gates first, then CI tables (stratified-by-seed paired BCa bootstrap, 2000 resamples), curve transfer check |
| `harness_run.py` | run wrapper: immutable run directory, git commit and dirty state, source hashes, single-thread env, 3600 s hard timeout, 8 GB `RLIMIT_AS`, rusage, validity rules, manifest |

## How the contract's "every arm at the same seed shares the walk" is realised

The walk is a deterministic function of its start point, and every arm at a
seed uses the same target restarts (stream `100 + s`). The outcome of a walk
(terminal DP, length, capped or not) therefore does not depend on the arm;
only WHICH walks are used (stop at first hit) and WHICH entries are credited
do. `run_generic.py` computes the outcome of all `16T x k` restarts once per
`(N, a, seed)` and every arm is pure bookkeeping over that table. Counts are
exact: `L` sums the lengths of the walks actually used (capped walks charged
at the cap), restarts = walks used, lookups = used walks that reached a DP.
At `N <= 2^24` the walker is cross-checked against the exact basin tables on
every online start (`walker_vs_exact_basins_agree`, true in every run).

## Reading of the contract's bookkeeping rules (declared, not silently chosen)

- Each walk carries exactly one `(length, +1)`: the hitting walk credits the
  hit entry at hit time; the other walks of a SOLVED target enter the pool at
  round end with their terminal DP (existing entry credited, new entry
  created). A capped walk has no DP and contributes nothing.
- NULL-A: every increment (hit credit and round-end credit) goes to a
  uniformly random entry of the pool AS OF ROUND START (stream `300 + s`); a
  new DP enters with zero evidence.
- PHI: one uniform per target from stream `200 + s`; the target's evidence
  (hit credit included) is admitted iff `u < phi`, so PHI arms are coupled
  and PHI(0) is STATIC bit-for-bit, PHI(1) is RESEL-L(T/2) bit-for-bit
  (both checked per run).
- RESEL-U: every used walk of every target enters the pool (hit walk credited
  once, at hit time).
- Ties in the weight are broken by a 63-bit random key per pool entry drawn
  from stream `400 + s` in creation order (precomputation entries first).
- Pools for `r = 4, 8` extend the `r = 2` pool (same generation sequence,
  cut when `rT` distinct DPs exist; every walk charged to P).
- `eps_ss(U)` = success over targets `[U - 2R, U)`; for RSWEEP-R the arm's own
  `R`. `eps_cum(U)` over `[0, U)`.
- `rho_T(U)`: log-linear interpolation of `eps_ss(RESEL-L(T_sel), U)` on the
  `T_sel` grid against `eps_ss(STATIC(T), U)`; censored at the grid ends and
  labelled when so.
- Fixture restarts: the next 40000 draws of stream `100 + s` after the
  `16T x k` target restarts. The fixture is computed per seed and the G2
  gate is evaluated on the 5-seed pooled value in the analysis run.
- Precomputation restarts: stream `default_rng(s)` (the walk-key seed); the
  walk key `K = mix64(golden + s)` and `K_dp = mix64(K XOR tag)` are derived
  arithmetically and recorded in every manifest.
- Re-selection integer operations are MEASURED by a counted streaming
  min-heap selection (one comparison or move = one operation) and the
  selected set is verified every round against an independent numpy lexsort
  (`selector_verified_against_numpy`, true in every run).
- Survival slope: the contract names the range `10 <= n <= W^2/4` but not
  the weighting. The primary estimator is least squares on 60 log-spaced
  integers; the integer-grid estimator and the value the EXACT
  Borel(1 - theta) law gives under the identical estimator are recorded
  beside it (labelled MODELED). This choice was made after a seed-1 smoke
  test at 2^20 showed the integer-grid estimator biased by the cutoff
  (the Borel law itself gives -0.68 on the integer grid and -0.63 on the log
  grid at W = 64); disclosed as a deviation, tolerances untouched.
- Cutoff `n_c`: least squares of `log S(n)/S(W^2/4)` on a 40-point log grid
  against the exact Borel(mu) survival ratio, `mu = 1 - sqrt(2/n_c)`, over
  120 log-spaced `n_c` in `[W^2/16, 64 W^2]`.
- Largest-basin band: 0.5% / 99.5% quantiles of the maximum of `N/W` iid
  Borel(1 - theta) samples.
- Curve arm: point identity key `2x + [y > p/2]`; a walk reaching the point
  at infinity is a miss charged at the cap (counted separately; zero
  occurred). RHO on the curve: a collision between two walks of the same
  target, both of the form `Q_u + [c]P`, gives `(c + s - c' - s')P = O` and
  no logarithm, so RHO emits no certificate; its collision count is
  reported as the contract's floor metric, not as solves.
- Curve exact basins (optional in the contract) were computed in every curve
  run (about 46 s each).

## Deviations and events (all recorded, none discarded)

1. RUN-ECDLP-612fb1-011 (analysis over Stage G) crashed with a `KeyError`
   in `analysis.py` (my bug: the seed is recorded under `seeds.walk_key_seed`);
   recorded as `failed_infrastructure`, re-run as RUN-012 after the one-line
   fix. No protocol content involved.
2. The three curve run IDs were minted as `RUN-ECDLP-612fb1-34/35/36`
   (no zero padding) by a shell arithmetic slip; run records are immutable
   and are not renamed.
3. `instrument.py` was extended (logarithm hook for the curve arm, optional
   `N_override`) AFTER all 32 generic runs; every manifest pins the source
   hashes it ran with. RUN-001 re-executed from its recorded command with
   the final source reproduces `raw-result.json` byte-for-byte and
   `summary.json` up to timing fields (scratchpad check, 2026-09-06).
4. The contract's S4 flag "0.42 at 2^30" is the a = 1/4 model value
   `C_max(1/4) + 0.03`; the per-run check applies it literally at both `a`,
   and at a = 1/2 the re-selected `T` tables exceed it (max pooled 0.514)
   while `C_max(1/2) + 0.03 = 0.555`. Both references are recorded.
5. NULL-A does not reproduce STATIC within CI: its gain is CI-separated
   BELOW zero in every cell (about -0.09 to -0.18 at 8T). Invalidation
   rule 5 (gain ABOVE zero and at least half the RESEL-L gain) does not
   fire; control (d)'s expectation ("within CI at every round") is not met.
   Recorded as an observation about the null as specified and implemented
   (reading above); no reinterpretation by the Executor.
6. `capped_mass` is 0 in most exact-basin cells: the deepest point of the
   graph sits below `8W` (e.g. 407 at 2^20, seed 1), confirmed by a naive
   walker with a 200000-step cap; capped online walks are the DP-free-cycle
   components (`cycle_mass`).
7. Primary sources were NOT fetched over the network; the contract's
   published numbers were used as frozen.

## Inference block

Every manifest records `requested_policy: executor-implementation`,
`resolved_model_id: claude-fable-5-1` (self-reported, `model_verified:
false`), the binding's model name for the policy (`claude-sonnet-5`, not
probed), `fallback_used: false` with the capability requirements of the
policy listed as met. Runs themselves are deterministic Python/NumPy.
