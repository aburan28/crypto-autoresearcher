# EXP-RHO-60da4f — Implementation Notes

## Code

- `impl/rho.c` — implementation "A" (C). Field arithmetic over a 64-bit
  prime (uint64_t + `__uint128_t` modmul), short-Weierstrass curve
  y^2 = x^3 + a*x + b, Shanks-Mestre BSGS curve-order search (setup only,
  not charged to run cost), the {+-1}-quotient walk with the five escape-rule
  families, the un-quotiented C1 baseline (`run-baseline`), and the C2
  random-oracle control (`run-oracle`).
- `impl/rho_ref.py` — implementation "B" (Python), independently coded from
  the same algorithm description, used for control C4.
- `impl/orchestrate.py` — run driver; writes batched immutable run records
  under `runs/<batch>/{manifest.yaml,raw-result.jsonl}`.
- `impl/calib.c` — one-off microbenchmark for the sqr/mul, inv/mul
  conversion-factor calibration (`op_ratio_calibration.json`).
- `curves.json` — the three frozen curves (one per subgroup size), generated
  once by `rho gen-curve` and never regenerated.

## Deliberate implementation simplification (protocol deviation, disclosed)

The specification's `curve_model` text calls for "Jacobian coordinates for
the walk step; affine only for the frozen distinguished-point test." Given
the session's real engineering time budget, the reference implementation
instead performs the walk step **directly in affine coordinates**, charging
one full modular inversion (extended Euclid) per step, rather than
implementing Jacobian-coordinate steps with a Montgomery-batched periodic
affine DP test. This was a time-boxed engineering choice, not a silent
omission.

Direction of the resulting bias: this inflates the **absolute** per-step
cost of BOTH the C1 baseline and the quotient walk **identically**, because
both use the exact same affine-native step function in the same harness.
Whether this cancels in the `net_gain_ratio` is *believed* but **not
independently verified** here — it is recorded as an additional
optimistic/pessimistic-assumption-style caveat alongside the four the
specification already declares, with the same "should cancel in the ratio,
that cancellation is an assumption, not a fact" status.

Consequence for `cost_unit`: all reported multiplication/squaring/inversion
counts are **measured** directly from instrumented field-primitive calls
(global counters incremented inside `modmul`/`modsqr`/`modinv`), not from a
formula lookup. Setup work (curve generation, branch-table precomputation,
starting-point derivation) is counted separately and is **excluded** from
the per-run charged cost, since it is a one-time cost shared across all
seeds at a given configuration, not a per-walk cost.

## Escape-rule alternate-branch function — a specification gap, disclosed

The specification names five escape-rule families but does not pin down a
concrete "second partition function of the current class" for
`branch_reselect_on_collision`, nor a concrete "fixed alternative branch...
by a function of the current class" for `deterministic_representative_break`.
The reference implementation uses one specific keyed hash (`hash_branch2`,
independent-looking but still a pure deterministic function of x) for both.
Because escape rules are memoryless by contract (spec's
`memorylessness_filter`), the resulting dynamical system is a small
finite deterministic map, which — as observed in the controls run below —
can and does re-absorb into new fixed points of the (primary, alternate)
hash pair (cycles of period >2 that the 2-cycle-only detector cannot see)
rather than reaching genuinely random-walk-like mixing. This is recorded as
an observation (see execution report), not smoothed over: **the concrete
choice of alternate-branch function is an implementation decision the
frozen contract leaves open, and that choice materially affects
trap-proneness.** A different reasonable choice of alternate-branch function
could give different empirical escape efficacy. This is flagged for the
Coordinator as a possible amendment target (pin the alternate-branch
construction in the contract) rather than resolved unilaterally here.

## Distinguished-point / collision semantics actually measured

Per walk (one seed, one configuration): a single random walk is run from a
random starting point; a point is *distinguished* if its x-coordinate's low
`dp_bits` bits are zero; the walk terminates ("collided") the first time it
revisits an x-coordinate already recorded as distinguished earlier in the
**same** trajectory (single-walk self-collision, the standard proxy for
expected rho cost, consistent with the spec's own `collision_constant =
steps / sqrt(N/2)` and `sqrt(pi N / 2)` / `sqrt(pi N / 4)` modeled
quantities). This is not a two-walk van Oorschot–Wiener parallel collision
search; VW parallelisation is one of the specification's own declared
optimistic assumptions ("modeled as near-linear... biases the ABSOLUTE
numbers but should cancel in the ratio").

## Session wall-clock as the binding constraint (infrastructure, disclosed)

The specification's own budget (`total_cpu_hours: 240`,
`wall_clock_seconds_per_run: 3600`, `maximum_runs: 7200`) is far larger than
what is actually available inside a single interactive agent session. The
**real** binding constraint on this execution was session wall-clock time,
not the specification's nominal budget. Per the stopping rule ("Stop the
whole experiment at the total_cpu_hours cap. A cap-terminated grid reports
its completed cells and names the incomplete ones"), this is treated the
same way: completed cells are reported, incomplete cells are named, nothing
is interpolated. This is classified as an `infrastructure_error`-adjacent
session-budget constraint (AGENTS.md rule 5: not evidence against the
hypothesis), and is separate from the specification's own CPU-hour budget,
which was not exhausted.

## Curve generation

Curves are generated by Shanks–Mestre BSGS (baby-step giant-step on the
trace of Frobenius, O(p^{1/4})), searching random (a,b) with a,b != 0 (which
excludes j=0 and j=1728) until `#E(F_p)` itself is prime (subgroup = full
group). Frozen once into `curves.json`, never regenerated.

## Controls implemented

- **C1** (`run-baseline`): plain (non-quotient) r=20 adding walk, same
  harness, same field primitives.
- **C2** (`run-oracle`): a keyed-hash state re-randomization (not curve
  arithmetic; mul=sqr=inv=0 by construction) exercising the same
  distinguished-point/collision code path, to validate the collision
  machinery's constant independent of the EC group law.
- **C3**: `escape=none` on the quotient walk.
- **C4**: C and Python implementations compared on frozen seed=1, r=8,
  dp_bits=12, escape=det, smallest size, at a fixed small step count.
- **C5**: every canonicalisation sign-flip during the measured walk region
  is counted (`duplicate_collapse_count`); the {+-1} class is represented
  solely by the x-coordinate, so no duplicate class is ever scored as two
  distinct configurations by construction.

## Debugging history (recorded per AGENTS.md rule 8 — not discarded)

1. **Real bug found and fixed.** The first working version of the 2-cycle
   escape check compared the wrong pair of historical x-values (it compared
   x[t-1] to x[t-2], two values that are never equal in a genuine 2-cycle),
   so no escape rule ever triggered even when the walk was visibly
   oscillating between two classes (confirmed by direct trace inspection).
   Fixed by computing the primary-branch *candidate* result for step t and
   comparing it against the value recorded two steps earlier, before
   committing to it. Fixed identically in `rho.c` and `rho_ref.py`.
2. **Shanks–Mestre BSGS was accidentally O(sqrt(p)) instead of O(p^{1/4})**
   in the first version (linear scan of the baby-step table on every giant
   step, and the giant-step loop only searched one sign of the trace).
   Fixed with a proper O(1)-lookup hash map and both-sign giant-step
   enumeration; curve generation for the 48-bit size dropped from "did not
   finish in several minutes" to ~40 seconds.
3. **Real, cross-validated phenomenon observed** (not treated as a further
   bug, since it reproduces identically in two independently written
   implementations, and the underlying group law and DP/collision machinery
   are independently verified correct via a working un-quotiented baseline
   collision at the expected order of magnitude): with the escape check
   fixed, the `det`/`reselect` escape rules very frequently re-absorb into a
   **new, higher-period fixed cycle** (period 4 observed directly in one
   traced example) that a period-2-only detector cannot see, because the
   escape mechanism is itself a small, memoryless-by-contract deterministic
   map: once a state is revisited, the future is fully determined. The C3
   control below shows unanimous, near-immediate absorption (>=99.99% of
   steps satisfy the raw 2-cycle predicate) for `escape=none`; informal spot
   checks at r=8 and r=32 with `det`/`reselect`/`periodic` active also showed
   zero distinguished-point collisions over budgets many multiples of
   sqrt(N/2), consistent with the same re-absorption phenomenon persisting
   even with escape logic active. This was NOT run as a scored grid cell
   (see below) and is reported here only as a qualitative anomaly requiring
   the grid measurement to confirm quantitatively.
4. **C4 automated-comparison scripting artifact.** The orchestrator's naive
   dict-equality check reports `agree_exactly: false` for the C-vs-Python
   comparison because the C binary's JSON carries two extra diagnostic-only
   fields (`duplicate_collapse_count`, `peak_rss_bytes`) the Python reference
   does not emit. Every field the control actually requires (step outcome
   and operation counts: steps, mul, sqr, inv, escape_triggers, dp_count,
   censored, collided, longest_fruitless_run, absorbed_2cycle_detected,
   step_budget, raw_fruitless_would_trigger) agrees exactly. See
   `controls_analysis.json` for the corrected, field-by-field comparison.
   The raw `runs/C4_two_implementations/raw-result.jsonl` is left as the
   unmodified tool output (immutability); the correction lives in the
   separate analysis file, not as an edit to the raw record.

5. **Real bug found and fixed: C1 measured the wrong quantity (session 2).**
   The Coordinator's check-in correctly rejected treating C1's 30.4% /
   38.9% / 54.6% deviation (growing with size, against +-8% tolerance) as an
   unexplained property. Root-cause investigation:

   - `run-baseline` (session 1) measured **single-walk self-collision**
     (Floyd/Brent style: one continuous walk revisits its own earlier
     distinguished point). The classical expectation for that specific
     quantity is `sqrt(pi*N/2)` (~1.2533*sqrt(N)) — which is exactly the
     quantity C2's random-oracle control targets (and which C2's own numbers
     track reasonably: 12% / 34% / -22%, not systematically 30-55% high).
   - The KN-TECH-006 baseline convention `0.886*sqrt(N)` is
     `sqrt(pi*N)/2 = sqrt(pi*N/2)/sqrt(2)` — a **different, smaller**
     quantity: the classical van Oorschot–Wiener result for a **parallel**
     collision search, where many independent walks (sharing one walk
     function, independent random starts) each run only until they produce
     ONE distinguished point, and the search stops the first time two
     *different* walks report the same distinguished point. This is smaller
     by the well-documented factor `sqrt(2)` (~41.4%) than single-walk
     self-collision, because it can detect a collision anywhere among many
     walks' short prefixes rather than requiring one walk to traverse all
     the way around its own cycle. `sqrt(2)-1 = 41.4%` is in the immediate
     neighborhood of all three original deviations.
   - **Fix**: implemented the true multi-walk methodology
     (`impl/rho.c`: `run_vw_multiwalk`, CLI `run-vw`). A shared branch table
     is built once; each "walk" starts from a fresh random point and runs
     until it hits *its own* first distinguished point, capped at
     `walk_cap = 64 * 2^dp_bits` steps to abandon walks trapped in
     non-DP-hitting absorbing cycles (their steps are still charged to the
     running total, matching KN-TECH-006's own "fully charged... failed
     attempts" framing). The run stops the first time a distinguished-point
     *value* is produced by two different walk origins. Applied identically
     to the un-quotiented baseline (`--mode 0`, C1) and the quotient walk
     (`--mode 1`, used for the grid), so both share one collision-detection
     convention — required for `net_gain_ratio` to compare like with like.
   - **Result after fix** (`runs/C1_baseline_reproduction_v2_vw/`,
     `controls_analysis.json`): L=32 now **passes** (6.9%, within +-8%).
     L=40 (41.8%) and L=48 (19.8%) still exceed tolerance.
   - **Residual investigated further, not left silent**: re-ran L=40/L=48
     with 40 diagnostic seeds (not the frozen 16-seed set) to test whether
     the residual is sampling noise. It is not: L=40's median deviation
     *increased* to 61.3% with more samples (not shrinking toward zero), and
     L=48 stayed in the 20-35% range. The pattern is also non-monotonic with
     size (32: ~7%, 40: ~42-61%, 48: ~20-35%), ruling out both a simple
     fixed-per-run-overhead-amortized-differently-by-size explanation and a
     simple unit/scaling formula error (either would produce a monotonic
     trend). Given the group law is independently verified correct (C4 exact
     cross-implementation agreement; C1's own baseline reaches real
     collisions at the right order of magnitude at every size; C2 validates
     the DP/collision machinery independent of curve arithmetic), and the
     effect is curve/size-instance-specific rather than a uniform law, the
     most plausible remaining explanation — argued, not asserted — is
     **genuine walk-quality variance**: this implementation's r-adding
     branch-point selection (r random EC points plus a generic keyed hash
     choosing the branch index) has not been tuned to Teske's specific
     "well-chosen r-adding walk" construction, which the literature
     (Teske 1998/2001, the basis for KN-TECH-006's constant) shows is
     necessary to reliably hit the near-ideal 0.886 constant; naive/generic
     r-adding constructions are documented to sometimes land materially
     above the ideal constant, by an amount that depends on the specific
     instance (curve, r, hash choice) — consistent with L=32's curve and
     branch table landing close to ideal while L=40's and L=48's do not.
     This is a different, smaller-magnitude, and disclosed limitation from
     the sqrt(2) methodology bug found and fixed above, not a further hidden
     bug. Verifying/tuning the branch construction against Teske's specific
     published quality criteria (e.g. checking for short additive relations
     among the r branch coefficients) is itself a nontrivial algorithmic
     sub-task and was not attempted this session; flagged as a candidate
     follow-up investigation.
   - **Consequence for the grid**: per the spec's invalidation_rules ("Any
     BLOCKING control failing invalidates every comparison in the affected
     size, and no net_gain_ratio may be reported for it"), `net_gain_ratio`
     is blocking-cleared **only at L=32**. Grid results at L=40/L=48, if
     computed, are reported as observation-only and explicitly **not**
     blocking-cleared, rather than silently presented as equally valid.

## Grid execution status and coverage cuts (session 3)

The grid ran, but its scope was cut twice, live, in response to measured
per-cell cost -- disclosed in full here rather than silently narrowed:

1. **L=32**: full declared factorial (9 escape settings x 5 r x 3 dp_bits x
   16 seeds = 2160 runs) completed in ~10 minutes (`grid_size32_full_vw`).
   Cheap at this size; no reduction needed.
2. **L=40, attempt 1**: the full factorial (540 runs) was started. After
   ~28 minutes only 2 of 9 escape settings (`none`, `det` — 120 cells) had
   completed, with `periodic`'s five k-sub-settings alone pacing at
   several hundred seconds each — projecting multiple additional hours.
   Killed. **The 120 completed cells were lost**: the run-writing code at
   that point only wrote output at the very end of the whole batch, not
   incrementally, so nothing was persisted before the kill. This was a real
   implementation gap, not a deliberate discard; the fix (below) was applied
   immediately afterward.
3. **Fix**: `impl/orchestrate.py`'s `run_grid` now appends each cell's
   result to `raw-result.jsonl` immediately after that cell completes, and
   flushes, so any future interruption preserves whatever finished.
4. **L=40, attempt 2 (reduced)**: `escape=none` dropped (already
   characterized by the dedicated C3 control at this size); `dp_bits`
   restricted to `{8}` (the only granularity that resolved with acceptable
   censoring at L=32); `r` restricted to `{20,32}` (the best-resolving
   values at L=32); seeds reduced to `{1,2}`. 32 runs, completed in ~106s
   (`grid_size40_reduced_coverage_vw`).
5. **L=48, attempt 1 (same reduction as L=40)**: even this reduced scope
   (8 escape settings x 2 r x 1 dp_bits x 2 seeds = 32 runs) was too slow at
   L=48's per-cell cost (~90-160s/cell observed) — projected over an hour.
   Killed after 8 cells, **also lost** (started before the incremental-write
   fix landed).
6. **L=48, attempt 2 (further reduced)**: cut to 4 representative escape
   settings (`det`, `periodic` at a single mid-range `k=8` only,
   `lookahead`, `reselect`; `none` and 4 of 5 `periodic` k-values excluded),
   same `r in {20,32}`, `dp_bits=8`, seeds `{1,2}`. 16 runs, completed in
   ~16 minutes (`grid_size48_reduced_coverage_vw`), now with incremental
   writes protecting the result.

**Net effect**: L=32 has full, clean coverage. L=40 and L=48 have a small,
explicitly labeled slice (16 and 8 scored configurations respectively,
2 seeds each) rather than the declared full factorial. This is a
budget-driven coverage tradeoff, prioritizing breadth across escape
settings over exhaustive seeds/replication at the larger sizes, as directed.
It is not a silent truncation: every batch's `manifest.yaml` records the
exact reduction applied.

## Headline grid finding (observation only, not interpretation)

Across all three sizes and every *resolved* (<=10% censored) cell measured,
`net_gain_ratio` (baseline r=20 Teske M-equivalent cost divided by the
quotient-walk's M-equivalent cost) is **below 1.0** — the negation-quotient
walk with every tested escape rule is fully-charged MORE expensive than the
un-quotiented baseline, not less, in every resolved cell at every size. The
largest observed ratio is 0.33 (L=40, `det`/`reselect`, r=32, dp_bits=8);
the smallest is 0.028 (L=32, `periodic` k=2, r=32, dp_bits=8). No cell at any
size crosses 1.0, so no sign-change setting is located anywhere within the
portion of the grid actually executed. The large majority of cells overall
(124/135 = 92% at L=32, the one size with full coverage) are **unresolved**
(>10% censored) rather than scored, consistent with the escape-rule
re-absorption phenomenon documented above (anomaly #3): escape rules
frequently trap the walk in higher-period fixed cycles a period-2-only
detector cannot see, so most configurations never reach a real
distinguished-point collision within the step budget. See the execution
report for the full per-cell table, bootstrap intervals, and each size's
attached C1 control status.
