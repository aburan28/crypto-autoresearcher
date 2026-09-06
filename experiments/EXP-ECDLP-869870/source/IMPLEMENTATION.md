# EXP-ECDLP-869870 implementation notes (Executor, TASK-20260906-d17254, 2026-09-06)

Placed under `source/` because the experiment-root `implementation.md` of the
reproduction-package layout is outside this task's write_scope; the Coordinator
may copy or link it.

## What the instrument does (one code path, rule by configuration)

- `instrument.py`: keyed walk `f(x) = top log2N bits of mix64(x XOR K)`
  (splitmix64 finalizer), DP predicate `mix64(x XOR K2) < floor(2^64 / W)`,
  exact first-DP / distance for every point by pointer jumping with DPs as
  absorbing fixed points (doubling continues until 2^k > N, so distances are
  exact for every reaching point); basin sizes at a cap are thresholds on the
  exact distance; `select_rule` is the single selection function for all five
  rules (published weight S_d + 4 W h_d, count-only, unselected, generated-set
  oracle, global oracle), ties by the seeded permutation (400 + s).
- `run_generic_exact.py`: one (N, seed) run over a in {1/8,1/4,1/2,1}: basin
  multisets at 8W and 20W (compressed histogram + top 1000), survival slope on
  [10, W^2/4] with multinomial bootstrap CI, joint cutoff fit, Borel 99% band
  for the largest basin, depth-profile histograms (stored only), global oracle
  share, the generation stream (200 + s) taken as nested prefixes for r in
  {1,2,4,8,16} (pool = first r T DISTINCT DPs, every walk charged, capped walks
  charged at 8W), the unselected law at m in T*{1/4..16} (prefixes of the same
  stream), the HEUR-BLT-2 regression on the first 16 T walks, M = 40000 online
  walks (100 + s) shared by every table, relabelling null (300 + s), sigma
  decay (500 + s, one Z per (a, r, rule) shared across sigma), fixture cells.
- `run_generic_sampled.py`: Stage 3 at 2^30 with real lockstep walks (no exact
  basins; oracle rules, exact coverage, basin law and HEUR-BLT-2 are reported
  as not computable at this N).
- `curve.py`, `run_curve_search.py`, `run_curve.py`: seeded prime-order curve
  search with Euler-criterion point counting; full enumeration [i]P by block
  addition; the r-adding walk as an index map f(i) = i + m_{j(x([i]P))} mod N
  (isomorphic functional graph) fed into the SAME `run_cell`; online walks on
  REAL points from Q_i + [c_i]P with a certificate for every hit.
- `verify_certificate.py`: independent pure-Python arithmetic, [k]P == Q and
  k == seeded log; shares no code with the walk.
- `run.py`: immutable run directory, 3600 s wall clock and 8 GB RLIMIT_AS,
  stdout/stderr, peak RSS via wait4, manifest with commit, dirty state, source
  sha256, inference block, seeds. Refuses to touch an existing directory.
- `analysis.py`: Stage 5 over completed runs; fixture gate first.

## Deviations and recorded executor choices (protocol untouched)

1. WALK PROJECTION. The contract writes `mix64(x XOR K) mod N`; the code takes
   the TOP log2N bits of the mixer output (an equally valid projection). Chosen
   before Stage 1 and kept for consistency. Verified by
   `diagnostics/walk_quality_check.py`: over 12 keys the construction is
   statistically indistinguishable from a true random table.
2. GENERATION-START SEED. The contract's seed policy names walk-key s, online
   100+s, relabelling 300+s, tie-break 400+s, noise 500+s but no stream for the
   generation-walk starts; 200 + s is used. Bootstrap resampling uses 600 + s;
   curve-walk scalars m_j use 700 + s; enumeration spot checks 900 + s.
3. CAP AS THRESHOLD. "Under cap 8W and separately under 20W" is implemented as
   two thresholds on the one exact distance map; the resulting basins are
   identical to two capped passes.
4. DP DISTANCE 0. A start that is itself a DP is a hit at 0 group operations.
5. ONLINE WALKS AT EXACT STAGES are lookups into the exact map (the walk from
   x is deterministic, so its terminal and length are p[x], d[x]); at 2^30 and
   on the curve online walks are executed step by step.
6. HEUR-BLT-2 DISPERSION. "variance/mean in [0.9, 1.1]" is ambiguous for a
   mixture; both the raw marginal var/mean over all DPs and the Pearson
   dispersion sum((h - lambda)^2 / lambda) / n with lambda = T_gen n / N are
   reported. Neither is interpreted.
7. NON-INTEGER W. W = sqrt(aN/T) is kept exact; cap = round(8W) and round(20W);
   the DP density is floor(2^64/W)/2^64 (recorded per cell).
8. RHO CONTROL. The listed control "Pollard rho with distinguished points and
   no table ... sampled only" has no meaning on the generic arm (nothing to
   solve) and was NOT run on the curve arm in this batch; reported as not run.
9. CERTIFICATE SCOPE. A certificate is one per online walk whose terminal DP
   lies in ANY evaluated table (all evaluated tables are subsets of the r = 16
   pool union the global-oracle table); k = idx(d) - c - s mod N is the same
   for every table the walk hits. Every hit of every table is therefore
   certified; per-table hit counts are recorded beside the certificate counts.
10. THE ANALYSIS RUN 016 FAILED (SyntaxError in a Python 3.11 f-string) and is
    kept as failed_infrastructure; the corrected analysis is a new run id.
11. SCRATCHPAD COLLISION. The concurrent executor of EXP-ECDLP-612fb1 shares
    the session scratchpad and overwrote this task's console log
    `stage2.log`; no run record was affected (all state is in runs/). Later
    scratch files use the prefix `exp869870_`.
12. A diagnostic (item 1) was executed while Stage 2 runs were in progress in
    the same container; it is not a contract run, but it consumed CPU
    concurrently. Wall clock is never a decision variable.
13. CURVE INFINITY. Index 0 of the enumeration is the point at infinity; it is
    never a DP and x(O) is taken as 0 for the step index; online walks that
    pass through O are counted and reported (`walks_hit_infinity`).
