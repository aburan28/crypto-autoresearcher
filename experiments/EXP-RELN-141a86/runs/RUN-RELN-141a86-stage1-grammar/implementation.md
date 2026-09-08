# Implementation notes -- RUN-RELN-141a86-stage1-grammar (TASK-20260907-8fd098)

## Status at handoff-return time

This run was launched as a detached, checkpointed background process and was
STILL RUNNING (own-enumeration table construction, not yet into grammar
enumeration/fitting) when this executor turn ended. See `manifest.yaml`
(`status: running`) and `driver-progress.log` / `own-enumeration-cache.jsonl`
for live progress. Nothing below is a scientific conclusion; it is a record
of what was built, what data is and is not available, and what deviations
from the frozen protocol were made and why.

## Protocol deviations (disclosed, per AGENTS.md rule 5 and this run's
manifest)

1. **Own enumeration performed inside Stage 1's write_scope, not a separate
   Stage 0e run.** `specification.yaml` assigns own-enumeration to Stage 0e
   with its own run directory and budget. This handoff's `write_scope` only
   authorizes `runs/RUN-RELN-141a86-stage1*/` and `source/`. Rather than
   silently skip the scientifically necessary held-out data or fabricate it,
   the own-enumeration code (`source/stage1_own_enumeration.py`, new this
   dispatch, calling the frozen, unmodified `count_vectors.py`) was run
   *inside* this run directory and disclosed as a stage-attribution
   deviation. See `manifest.yaml`'s
   `scope_and_protocol_deviation_disclosure` for the full reasoning.

2. **`EXP-RELN-f202be` sibling data checked and found unusable -- CORRECTED
   and expanded on 2026-09-07 (follow-up dispatch, same TASK).** The prior
   note here said "an m=2 x-class signed convention"; that was WRONG and is
   corrected: f202be's own `specification.yaml` fixes `arity_m: 3` (line
   375, `fixed: {arity_m: 3, ...}`), the same m=3 as this contract. Re-read
   directly (`RUN-RELN-f202be-N20/curve_results.json`, its `cells/` tree's
   `histogram.json`/`count-vector.npy`, and f202be's `specification.yaml`
   `object_bases`/`sign_conventions`/`base_size_conventions` blocks) to
   pin down the ACTUAL mismatch precisely, since "field-incompatible" was
   too compressed to act on:
   - **Geometry**: f202be's object bases are `x_interval_low` (smallest-x),
     `x_interval_mid` (smallest-x >= p/2), and `qr_class` (smallest QR-class
     x) -- constructed by a *smallest-x* selection rule. This contract's
     E-arm geometries are `high_bit_interval` (TOP bit-window, largest-x),
     `small_height` (rational-reconstruction height ordering, unrelated to
     x-magnitude) and `coset_union` (multiplicative-subgroup cosets).
     Different constructions, not just different names for the same object.
   - **Sign convention**: every one of f202be's object bases is
     NEGATION-CLOSED, `W = V union -V`, run under its `unreduced` (all
     `C(B+2,3)` multisets from `W`, including forced `{P,-P,Q}` triples) or
     `reduced` (excludes any multiset containing a `{P,-P}` pair)
     convention. This contract's `fb3_unsigned_m3` convention is explicitly
     "a base of B elements NOT required to be negation-closed" (this
     contract's own `inputs.committed_fb3_cells.convention`) -- f202be's own
     spec calls that case "plain" and reserves "plain" for its NULL/CONTROL
     bases (random points, Z/N random, Z/N interval, E small-multiples,
     Bose-Chowla) only, never for an x-interval-shaped OBJECT arm. So the
     one convention that WOULD be compatible (`plain`) exists in f202be only
     for objects that are not the E-arm geometry this contract needs.
   - **B convention**: f202be uses `B_1`/`B_2` (even-rounded for
     negation-closed arms; `B_2` from a Bose-Chowla `q^3-1` rule), not this
     contract's single `B0 = ceil((6N)^(1/3))`.
   - **Statistic vocabulary**: f202be's per-cell fields are
     `E3_direct/spectral/ord`, `delta_unreduced/reduced`, a
     `forced_negation_gap` diagnostic, and Boolean-predicate counts
     `P1..P7`/`ANCHOR-LOG` -- no `R_k`, no `coverage`, no
     `third_factorial_moment`, and one `NULL_A` band per (curve, B-conv,
     sign-conv) rather than a null_mean/null_sd per statistic.
   Conclusion (unchanged from before, now with the actual reasons instead of
   "field-incompatible"): this is a genuine construction/convention
   mismatch across geometry, sign convention and B-rule simultaneously, not
   a field-naming difference an adapter could paper over -- doing so would
   be exactly the "convention mismatch resolved by rescaling ... rather
   than by reading each record's convention" `invalidation_rules` forbid.
   f202be's data was correctly NOT used as a stand-in for the E-arm held-out
   check. This triggered the Stage-0e own-enumeration fallback (deviation
   #1 above), which itself explicitly declines to synthesize E-arm data via
   a Z/N surrogate (deviation #4) -- see deviation #9 below for how the
   actual gap this leaves was closed.

3. **No committed FB3 2^20 data exists at all** (`EXP-FB3-001/runs/` has
   only N14, N16, N18, FAMILY, CTRL). Consequently the E x-interval arms
   (`fb3_unsigned_m3` convention, geometries `high_bit_interval`,
   `small_height`, `coset_union` -- the pack `later_review_requirements`
   explicitly names for the independent validator's blind re-derivation)
   have **no available held-out check in this run**. Own-enumeration in Z/N
   is NOT used as a substitute for this: a Z/N arithmetic interval base is a
   qualitatively different structure from an elliptic-curve x-coordinate
   interval -- it literally *is* the `ZN_interval` positive control, which
   the frozen contract predicts and requires to DEPART from INV-A1, not a
   stand-in for the null-hypothesis geometry. Using it as such would be
   exactly the geometry-substitution `invalidation_rules` forbid. This is a
   genuine, disclosed data-availability gap, not a result: `stage1_fb3_table.py`
   rows carry `held_out_status: "not_available_no_2^20_fb3_data"` explicitly,
   never a computed or estimated value.

4. **Own enumeration used ONLY for the random-base and Z/N-native control
   arms.** `E_matched_random_analog` (a uniformly random B-subset of Z/N,
   standing in for the `held_out_transfer_anchor` control's "INV-A1
   evaluated on the RANDOM arms at 2^20" requirement -- valid because
   HEUR-H1's random-base model is stated group-agnostic to leading order),
   `ZN_interval` (natively a Z/N construction, no surrogate needed), and
   `ZN_random_relabelled` (ditto). No E-arm data was synthesized.

5. **Statistics scope reduced to `Delta` and `E_3` for this dispatch**,
   not the full `R_1..R_8`, `coverage`, `third_factorial_moment` list in
   `independent_variables.statistic`. Each additional statistic
   multiplicatively increases the per-expression constant-fitting cost
   (measured this dispatch: a 2-free-constant fit costs on the order of
   several thousand weighted-SSE evaluations per (expression, target)
   pair). Given the observed container restart cadence (~20-30 minutes) and
   the measured own-enumeration table-build cost (~20-30 minutes before any
   fitting even starts), completing more than `Delta`/`E_3` within available
   compute was judged infeasible for this dispatch. `R_1..R_8` and
   `coverage` were already computed and cached per-cell in
   `own-enumeration-cache.jsonl` and `stage1_fb3_table.py`'s output (so a
   future extension does not need to recompute the count vectors), only the
   grammar-fit stage was scoped down.

6. **Packs scope reduced to `fb3_unsigned_m3_and_enum_unsigned_m3` only**,
   not the other five leaf packs (`enum_xclass_signed_m2`, `symmetric_m3`,
   `degree_table`, `dreg_semaev_D5`, `enum_zn_and_sidon`) named in
   `frozen_pipeline.primary_engine.grammar.leaves_by_pack`. This is the pack
   central to the hypothesis's own headline prediction (Delta/E_3 on the
   E-arm family and its controls) and the one `later_review_requirements`
   names; the others were not reached within this turn or the wall-clock
   budget observed so far. `C_complete` for those packs is `0` (not
   started), reported honestly, not silently extended.

7. **Constant-fitting is a purpose-built deterministic grid search
   (`stage1_fit_engine.py`), not `constant_fit.py`'s existing 1-D linear-
   detection fitter.** `constant_fit.py`'s `least_squares_fit_constant` only
   auto-detects the single-linear-in-c case; Stage 1's enumerated
   expressions with 2 free CONST leaves are frequently NOT linear in either
   constant (division/pow nesting), and a first version of a naive joint
   2-D coarse-to-fine grid was found, BY THIS DISPATCH'S OWN SELF-TEST
   (`stage1_fit_engine.py __main__`), to converge to a badly wrong local
   optimum and fail to recover INV-A1's own two (tied, both =1) constants
   from noiseless synthetic data generated directly from INV-A1's formula
   -- a fitter that cannot recover a law from noiseless data generated by
   that exact law cannot be trusted for anything harder. Replaced with
   deterministic alternating-coordinate-descent from 7 fixed starting
   points (no randomness, same result every re-run); the self-test now
   recovers `[1.0, ~1.003]` (matches ONLY within the grid's finite
   resolution, not exactly, and correctly flags `matches_known_candidates:
   ["INV-A1"]` at the 1e-6 relative tolerance used). This fitter is
   NEW code and is NOT validated against an independent re-derivation --
   flagged for the independent validator's blind Delta-front re-derivation
   requirement.

8. **Candidate-list scoring is numeric-equivalence-only against three known
   closed forms** (`INV-A1`, `INV-1`, `INV-2prime`), not full symbolic
   equivalence against all 19 `candidate-list.yaml` entries. Implementing a
   general symbolic-equivalence checker against arbitrary enumerated forms
   (beyond the hand-coded closed-form comparison already used) was judged
   out of scope for this dispatch's remaining time; this is a stated scope
   limit on the `scored-candidate-list.json`-equivalent output, not a
   silently narrowed claim.

9. **REAL held-out 2^20 E-arm data generated (2026-09-07, follow-up
   dispatch), closing deviation #3's gap rather than leaving it
   unaddressed.** Deviations #2/#3 correctly ruled out both available
   external sources (f202be genuinely incompatible; committed FB3 has no
   2^20 run at all) and deviation #4 correctly ruled out a Z/N surrogate for
   the E-arm geometries specifically (that IS the `ZN_interval` positive
   control, not a stand-in for the null geometry). Rather than stop there
   and report "not available" as final, `source/stage1_e_arm_holdout.py`
   (new this follow-up) generates the missing data directly: it imports
   `EXP-FB3-001/implementation/fb3_core.py` UNMODIFIED (no new curve or
   geometry definition invented) and calls its own frozen `find_curve`,
   `matched_size`, `geom_high_bit_interval`, `geom_small_height`,
   `geom_coset_union` at `bits=20` -- a bit-length FB3-001 itself never ran,
   so this collides with none of its existing curves under the identical
   seed formula (`curve_seed_base*1000 + bits*10 + curve_index`) -- to build
   4 new real prime-order curves at N ~ 2^20, select the three E-arm bases
   on each, and count exact decomposition vectors via `count_vectors.py`'s
   cyclic-convolution engine (same module Stage 0e already uses,
   unmodified). Before trusting any 2^20 number, the module's own
   `self_test_reproduce_committed_n14()` runs the IDENTICAL code path at
   `bits=14, curve_index=1` and asserts its output (`N`, `B`, `sum_counts`,
   `mean`, `coverage`, `concentration`, `window_W`, `x_min`, `x_max`) equal,
   bit-for-bit, to the already-committed `RUN-FB3-001-N14` cell
   (`geometry=high_bit_interval, curve_index=1, rep_seed=1,
   evaluation_domain=whole_group`) -- this PASSED exactly (see the module's
   `__main__` output, reproduced verbatim in the executor's turn transcript:
   every one of the 9 checked fields matched to the value printed, `mean =
   1.1276087887875634`, `concentration = 1.254666748271008`, etc.) before
   any 2^20 curve was generated. The 2^20 build was then launched as its own
   detached, per-(geometry,curve_index)-checkpointed background process,
   writing `e-arm-holdout-cache.jsonl` in this run directory (12 target
   cells: 3 geometries x 4 curve replicates, ~290s/cell measured, so ~1h
   total; `coset_union`/`small_height` may report `infeasible_reason` per
   cell if the geometry cannot reach size B on a given curve -- recorded,
   never silently dropped or estimated). `stage1_grammar_driver.py`'s
   `build_targets` was extended (read defensively: absent-file is a no-op,
   identical to pre-follow-up behaviour) to merge these rows into the
   `E_arms_fb3_<geometry>` and `E_arms_fb3_combined` target groups as
   `held_out=True` rows, so the EXISTING train/held split and fit/scoring
   logic in `evaluate_level_for_targets` picks them up with no other
   change. **This wiring is NOT yet live in the currently-running
   `RUN-RELN-141a86-stage1-grammar` grammar-fit process (PID recorded in
   `command.txt`/`driver-progress.log`)**: that process was started before
   this module existed and already has the old `build_targets` loaded in
   memory (Python does not hot-reload); it was deliberately left
   undisturbed per this follow-up's explicit instruction not to touch it,
   and because `stage1_grammar_driver.py` has no true resume-from-checkpoint
   for the grammar ENUMERATION itself (only the row-generation caches
   resume; `by_complexity`/`front_state` restart at complexity 1 on any
   fresh process, a pre-existing limitation, not introduced here -- see
   `experiments/EXP-RELN-141a86/amendments/v1.yaml` if referenced above, or
   record it there if not). Consequence: this run's own `pareto-fronts-raw.json`
   for the `E_arms_fb3_*` targets will finish with `held_out: null` /
   `metric_kind: train_weighted_sse_no_held_out_available`, exactly as
   deviation #3 disclosed, UNLESS a follow-up task launches a fresh
   `stage1_grammar_driver.py` invocation (same command, new/adjacent run
   directory or this one after the current process reaches a terminal
   state) after `e-arm-holdout-cache.jsonl` has 12 (or fewer, with
   `infeasible_reason` accounting for the rest) rows. That re-run is
   NECESSARY to actually score the E-arm Delta/E_3 held-out check the
   contract's success/falsification criteria depend on; it is bounded,
   ordinary re-computation (re-deriving the SAME grammar enumeration up to
   complexity 12, now against a target list that additionally has real
   held-out rows for 4 of its groups), not a new protocol.

## PySR re-check (stage1_pysr_fits)

See `environment.json`. `pip install pysr` succeeds (version 2.2.1, a
change from Stage 0a's `pysr_available: false`), but (a) no pin was ever
established at Stage 0a for this dispatch to install against, and (b) a
genuine fresh install attempt's required Julia backend fails in this
environment (SHA-256 mismatch downloading the Julia 1.11.9 binary --
plausibly a network/proxy interference in this sandbox, not investigated
further). Both facts independently require `stage1_pysr_fits` to be
`failed_infrastructure` for the PySR arm. No unpinned PySR version was run
or used for any fit; the primary `exhaustive_grammar` engine stands alone,
per the frozen contract's own pinning clause.

## What a follow-up task should do

0. Check on the E-arm holdout job (`pgrep -af stage1_e_arm_holdout.py`;
   `e-arm-holdout-stderr.log`'s last lines; `wc -l e-arm-holdout-cache.jsonl`,
   target 12). When it reaches 12 rows (or fewer + accounted
   `infeasible_reason`s), launch a FRESH `stage1_grammar_driver.py`
   invocation (same command as `command.txt`, over the SAME
   `e-arm-holdout-cache.jsonl` this run directory now has) so the
   `build_targets` wiring (deviation #9) actually scores the E-arm
   Delta/E_3 held-out check -- the currently-running grammar-fit process
   (item 1 below) does NOT have this data, having started before it existed.
1. Check on the detached job (`pgrep -af stage1_grammar_driver.py`; read
   `driver-progress.log`'s last lines and `enumeration-checkpoint.json` /
   `pareto-fronts-raw.json`'s `last_updated_utc`).
2. If dead, decide whether to relaunch (same command, in `command.txt`;
   the row-level and per-level checkpoints mean a relaunch resumes rather
   than restarts from zero for the table, though the grammar enumeration
   itself still re-derives from complexity 1 on every relaunch, per the
   same not-yet-built true-resume limitation recorded in
   `experiments/EXP-RELN-141a86/amendments/v1.yaml`).
3. When the job reaches a terminal state, update this manifest's
   `status`/`result` fields in place (pre-archival) and produce the
   remaining `required_artifacts` this run has not yet produced
   (`pareto-fronts/<statistic>-<pack>-<engine>.json` in the frozen naming
   convention, `collision-sets.json`, `scored-candidate-list.json`,
   `survivors.json`, `k-rich-profile.json`, `tail-checks.json`,
   `execution-report.md`) by reading `pareto-fronts-raw.json` -- the raw
   per-level records already contain everything needed (best expression,
   fitted constants, collision set, held-out error, candidate matches) to
   derive those files without re-running anything.
4. Extend to the deferred statistics (`R_1..R_8`, `coverage`,
   `third_factorial_moment`) and packs (see deviations 5-6 above) as
   budget allows -- the count-vector data for `R_k`/`coverage` is already
   cached and does not need to be regenerated.

## Crash diagnosis and fix (this dispatch's follow-up, 2026-09-07 21:xx UTC)

Both background jobs were found dead: the fourth container restart of this
session killed the e-arm-holdout job cleanly mid-row (no exception, ordinary
infrastructure interruption), but the grammar-fit driver died from a REAL bug:
`OverflowError: (34, 'Numerical result out of range')` in
`stage1_fit_engine.py`'s `held_out_error`, at `sq.append(e_se ** 2)`, after
complexity level 1 completed cleanly for all 14 targets (see the protective
snapshot commit `0d3a63bed` for the exact traceback and pre-fix artifacts).

**Root cause (diagnosed, not assumed):** the crash is NOT a data bug. Read
back `own-enumeration-cache.jsonl`'s held-out rows: `ZN_interval`'s `Delta`
statistic legitimately runs 57-12609 (vs ~1.0 for the random arms) because
`ZN_interval` is the arithmetic-progression POSITIVE CONTROL -- its whole
purpose (see `stage1_own_enumeration.py`'s own docstring) is to depart
sharply from the null model built from random draws, so `null_sd` stays at
the same tiny (~0.004) scale as the random arms while the observed statistic
is orders of magnitude larger. That is the control working as designed, not
a bug. The actual defect is purely numerical: CPython's float `**` raises
`OverflowError` when a result mathematically exceeds `float` range (confirmed
directly: `1e160 ** 2` raises, but `1e160 * 1e160` returns `inf` silently),
while `+`, `-`, `*`, `/` never raise for the same overflow -- they return
`inf`, which IS the mathematically correct value, not a clamp. `e_se ** 2`
in `held_out_error` was the only place in the numeric pipeline still using
`**` on a value with no bounded range. A grid-searched early-complexity
expression against a badly-fitting held-out cell (e.g. `ZN_interval`, or any
`exp(N/B)`-shaped candidate whose predicted value is a legitimately huge but
finite float) produces exactly this: `e_se` finite but squaring it crosses
the float-range boundary.

Confirmed via direct reproduction on the committed cache data (this
dispatch, no fabricated numbers): `stage1_fit_engine.eval_expr` already
handles internal overflow correctly (its own `try/except (ValueError,
OverflowError)` around `**`, `math.exp`, etc. returns `None`, never raises).
The SAME hazard exists, independently, on the TRAINING side:
`_weighted_sse`'s `((pred - obs) / sd) ** 2` -- reproduced directly by fitting
`exp(div(N,B))` against `ZN_random_relabelled`'s real training rows (`N=16411,
B=24` gives `pred~9.27e296`, `obs~1`, `sd~0.004`, so `e_se~2.3e299` and
`e_se**2` overflows). This second instance had NOT yet crashed the committed
run only because complexity 1 (single leaves) never produces predictions
that large; it started firing immediately at complexity 4 once the driver was
first relaunched (see below) -- caught cleanly by the new per-expression
guard (item 3), confirming the guard's value independent of the root-cause
fix.

**Fix applied (both instances, `stage1_fit_engine.py`):**
- `held_out_error`: `e_se ** 2` -> `e_se * e_se`. Each per-row entry now
  carries an explicit `"overflow": bool` flag (never silently indistinguishable
  from a well-behaved small metric), and the returned dict carries a top-level
  `"held_out_error_overflow": bool`. `rms_null_se` can legitimately be `inf`
  for a genuinely catastrophic fit -- that is the correct, honest value, not
  suppressed or clamped.
- `_weighted_sse` (training-side fit objective, same hazard, found only after
  relaunching once with the `held_out_error` fix alone -- see below):
  `((pred - obs) / sd) ** 2` -> `term = (pred - obs) / sd; term * term`. Same
  reasoning; `total` can legitimately become `inf`, correctly representing
  "this candidate does not fit," and grid-search comparisons (`<`) with `inf`
  behave correctly.
- Added a regression self-test in `stage1_fit_engine.py`'s `__main__` block
  reproducing the exact overflow shape and asserting no exception, a flagged
  `held_out_error_overflow: True`, and `rms_null_se == inf`. Passes
  (`python3 stage1_fit_engine.py`).

**Defense-in-depth guard added (`stage1_grammar_driver.py`,
`evaluate_level_for_targets`):** the per-expression fit+score body is now
wrapped in `try/except Exception`; any exception is logged (`SKIPPED expr
(implementation_error, not evidence): target=... complexity=... expr=...
error=...`) and that ONE expression is skipped, never the whole run. Skip
counts are recorded per target/complexity in `front_state` (`n_skipped_errors`)
so a skip is visible in `pareto-fronts-raw.json`, never silently dropped. This
is a backstop, not a substitute for the two root-cause fixes above: with only
the `held_out_error` fix and NOT yet the `_weighted_sse` fix, the first
relaunch of the grammar driver hit the second (training-side) instance of the
same bug at complexity 4 and the guard caught it cleanly (415 `SKIPPED` lines
logged, process stayed alive) -- this was itself the evidence that led to
finding and fixing `_weighted_sse` before the second relaunch, after which
zero `SKIPPED` lines occur.

**Relaunch, honestly reported:** neither driver supports resuming an
in-flight *enumeration/evaluation* level -- `stage1_grammar_driver.py`'s
`main()` has no checkpoint-read path and always restarts the grammar
enumeration from complexity 1. In practice this is cheap: complexity 1's
logged 1368.7s elapsed was almost entirely the one-time
`own-enumeration-cache.jsonl` data build (`oe.build_own_enumeration_rows_resumable`,
which IS row-level resumable and skipped all 108 already-cached rows in
under a second on relaunch), not the grammar evaluation itself (all 14
complexity-1 per-target log lines land within under 1 second of each other).
The e-arm-holdout job (`stage1_e_arm_holdout.py`) IS genuinely resumable at
per-`(geometry, curve_index)` granularity (`build_e_arm_holdout_rows_resumable`,
keyed off the same cache file) -- confirmed on relaunch: it found `curve_index=1`
again (curve-finding is fast, not cached) but skipped straight past its
already-cached geometries and started fresh work at `curve_index=2`, exactly
as expected, without recomputing the three curve_index=1 rows already in
`e-arm-holdout-cache.jsonl`.

Both jobs were relaunched (grammar driver twice -- once immediately after the
`held_out_error` fix alone, then killed and relaunched again after finding
and fixing the `_weighted_sse` instance, so the currently-running process has
BOTH fixes) as detached background processes, same commands as
`command.txt` / the e-arm-holdout invocation pattern established by the prior
dispatch. Both confirmed alive and checkpointing/logging within a few minutes
of launch; the grammar driver reached complexity 4 with zero exceptions
before this report was written.

## Checkpoint-resume fix for stage1_grammar_driver.py (this dispatch, 2026-09-08)

**Bug (confirmed by direct source reading, not assumed):** the note directly
above was correct and remained true across every subsequent relaunch for
~20 restart cycles: `stage1_grammar_driver.py`'s `main()` always initialized
`checkpoint_levels = []` / `front_state = {}` fresh and never read
`enumeration-checkpoint.json` / `pareto-fronts-raw.json` back in on startup,
even though `write_all_checkpoints()` writes both progressively, one
complexity level at a time, as each level's `evaluate_level_for_targets`
pass completes. Because own-enumeration/E-arm-holdout row data IS cached and
cheap to rebuild (confirmed above, ~1s), but constant-fitting + held-out
scoring is NOT, every container restart cheaply re-derived the row data and
then re-paid the FULL expensive fit/score climb from complexity 1, so the
run had essentially never gotten past complexity 4-5 across ~20 restarts.

**Fix applied to `source/stage1_grammar_driver.py`** (same class of fix as
`stage1_e_arm_holdout.py`'s intra-cell checkpointing, commit `46fe1eca9`, but
at the coarser per-complexity-level granularity that fits this loop): the
level-registration logic (previously inlined once before the main loop for
complexity 1 and again inside the loop for complexity >=2) was factored into
a shared `build_level_exprs(c)` helper. `main()` now checks, on startup,
whether `enumeration-checkpoint.json`/`pareto-fronts-raw.json` already exist
in the SAME `--out-dir` for the SAME `pack`/`max_complexity`. If so, it
re-derives (registration only, via `build_level_exprs`, NEVER re-fitting or
re-scoring) every already-completed level to rebuild the enumeration state
(`by_complexity`, `seen_string_hashes`, `seen_fp_hashes`), verifying at each
level that the re-derived `new_registered` count matches the count the
original run recorded -- if any level disagrees, the resume is aborted and
the run falls back to a clean from-scratch enumeration rather than trusting
a possibly-nondeterministic partial rebuild. On success, `front_state` is
reloaded verbatim from `pareto-fronts-raw.json` and the fit/score loop
resumes at the next incomplete complexity level -- no already-completed
level is ever re-scored.

**Granularity justification:** one full complexity level's
`evaluate_level_for_targets` pass across every target is the natural atomic
unit, because `write_all_checkpoints()` only ever commits after that pass
completes for ALL targets at that level -- a level is either fully scored
and committed, or not started at all, never partially committed. Finer
(sub-level, per-target) checkpointing was considered but rejected: unlike
`stage1_e_arm_holdout.py`'s per-cell draws (which are independent,
long-running units worth checkpointing individually), a single level's
per-target fit/score pass across the observed target count (14, all 14
scored within seconds of each other at low complexity per the timestamps in
this file's earlier sections) is itself fast relative to the whole level;
the expensive part scales with the NUMBER of complexity-C expressions
enumerated, not the number of targets, so per-level is the correct atomic
unit here, not per-target.

**Regression test (`source/test_stage1_grammar_resume.py`, real
kill-and-resume, same rigor as `stage1_e_arm_holdout.py`'s
`self_test_reproduce_committed_n14()`):** runs the actual driver subprocess
twice against copies of the REAL cached `own-enumeration-cache.jsonl` /
`e-arm-holdout-cache.jsonl` data from this run directory (read-only copy,
never synthetic data) -- an uninterrupted control run to `max_complexity=4`,
and a second run polled until `enumeration-checkpoint.json` shows complexity
2 complete, `SIGKILL`ed (a real kill, not a clean shutdown -- exactly what a
container restart delivers), then relaunched with the identical command over
the same `--out-dir`. All four assertions passed (this dispatch, verified
directly, not assumed):
  1. the resumed run's second launch actually logs a `RESUME: enumeration
     state rebuilt` line;
  2. that second launch's log segment contains zero fit/score lines for the
     already-completed complexity 1-2 (no re-scoring);
  3. `enumeration-checkpoint.json`'s `(complexity, new_registered)` pairs are
     identical between the control and resumed runs:
     `[(1, 6), (2, 14), (3, 162), (4, 794)]` for both;
  4. `pareto-fronts-raw.json`'s `front_state` (every target, every
     complexity, including the fitted constants and held-out metrics) is
     deep-equal between the control and resumed runs -- byte-identical
     results, not merely "close."

**Applying the fix to this run, honestly reported:** per this dispatch's
explicit instruction, the then-currently-running `RUN-RELN-141a86-stage1-grammar`
process (PID 3440, launched with the PRE-fix code, already at complexity
level 4 when this dispatch started) was left completely undisturbed while
the fix was developed and tested against a separate temp directory (never
this run's own files). PID 3440 was NOT killed by this dispatch: it ran
uninterrupted for the rest of its natural lifetime and exited on ITS OWN
(no container restart intervened this time) with `stopped_reason:
wall_clock_cap` after reaching complexity level 6 (`total_elapsed=39501.0s`,
well past its `21600s` cap -- the cap check only fires after a level
completes, so a very slow level 6 for some targets pushed total elapsed
past 21600s before the check ran; not a bug in this dispatch's scope, a
pre-existing property of the cap check firing only between levels, disclosed
here rather than silently ignored). Once PID 3440 had exited (confirmed via
`ps`/`kill -0`), the FIXED driver was relaunched with the exact same command
recorded in `command.txt`. Its `driver-progress.log` confirms the resume
path activated correctly in production: `RESUME: found checkpoint complete
through complexity 6` -> `RESUME: enumeration state rebuilt through
complexity 6 (new_registered counts matched at every level, confirming
byte-identical re-derivation) ... resuming fit/score at complexity 7` --
the rebuild of levels 1-6 took ~19s (registration only), versus the many
hours the original process spent scoring those same levels, and complexity
7 began scoring fresh with zero levels re-scored. This is the exact
climb-loss bug fixed and confirmed fixed in production, not just in the
isolated test.

**Currently running:** PID (see `command.txt`'s recorded invocation and
`ps aux | grep stage1_grammar_driver` for the live PID) is alive as of this
report, resumed cleanly at complexity 7, `--max-complexity 12
--wall-clock-cap-seconds 21600`. A future container restart will now lose at
most the in-progress level's fit/score work, never the whole climb back from
complexity 1 -- the bug this dispatch was asked to fix. Continued monitoring
(relaunch-on-death, extend to deferred statistics/packs per the "What a
follow-up task should do" section above) remains a later Coordinator
check-in's task, unchanged from this run's established mechanical
restart-recovery loop.

## TERMINAL OUTCOME (this dispatch, 2026-09-08, follow-up executor turn)

This section records this run's actual, final, decidable state. Nothing
above this heading is edited; this appends the closing chapter the prior
sections anticipated.

**PID 3440 (the process the previous section called "currently running")
finished on its own.** It ran uninterrupted from its launch at
2026-09-08T07:18:08.656670Z (driver-progress.log line 1810 -- the last of
roughly 21 relaunches in this run directory's history, and the first to run
with BOTH the `held_out_error` and `_weighted_sse` overflow fixes applied
simultaneously) through 2026-09-08T18:16:29.616426Z, when it stopped itself
with `stopped_reason: wall_clock_cap` after exhaustively completing
complexity levels 1 through 6 for all 14 targets
(`total_elapsed=39501.0s`, well past the 21600s advisory ceiling -- the cap
check fires only between levels, so the slow level 6 pushed total elapsed
past the cap before the check could fire; disclosed, not a bug introduced
this dispatch). Per-level elapsed time from `enumeration-checkpoint.json`
(cumulative `elapsed_seconds_total`, deltas computed): level 1 = 0.607s,
level 2 = 0.476s, level 3 = 25.767s, level 4 = 216.565s, level 5 = 3864.995s,
level 6 = 35392.471s. Level 6 alone consumed 89.6% of the run's total
measured elapsed time -- the combinatorial per-level growth (roughly 18x
from level 4 to level 5, roughly 9x from level 5 to level 6) that motivated
the standing decision described next. No container restart or crash ended
PID 3440 this time; it exited cleanly on its own logic.

**The checkpoint-resume fix worked correctly in production.** Immediately
after PID 3440 exited (confirmed via `ps`/`kill -0`), a separately-dispatched
agent relaunched the fixed driver as PID 16763 with the identical command
in `command.txt`. Its log confirms the resume path activated exactly as
designed: `RESUME: found checkpoint complete through complexity 6` ->
`RESUME: enumeration state rebuilt through complexity 6 (new_registered
counts matched at every level, confirming byte-identical re-derivation) ...
resuming fit/score at complexity 7` (2026-09-08T18:17:13.633175Z) -- the
levels-1-6 rebuild (registration only, zero re-fitting/re-scoring) took
~19 seconds, versus the many hours PID 3440 spent actually scoring those
same levels. This is the exact climb-loss bug this dispatch was asked to
fix, confirmed fixed in a real production run, not merely in the isolated
`test_stage1_grammar_resume.py` regression test. Commits `eb3ed46bc` (fix +
test) and `923a0840a` (production application) are the record of this work.

**THE COORDINATOR then deliberately stopped PID 16763.** A later session
(this same day, 2026-09-08) sent `SIGTERM` to PID 16763 and confirmed it
dead, specifically to enforce a STANDING PRIOR DECISION recorded in commit
`83b4739ee`: cap this experiment's exhaustive search at `C_complete=6`,
given the demonstrated combinatorial per-level cost growth documented in
that commit's own message (level 6 alone consumed roughly 9.8 of the run's
roughly 11 total hours; the growth pattern level 4 -> 5 -> 6 predicts level
7 would be substantially more expensive still). This is explicitly NOT a
correction of, or a loss of confidence in, the checkpoint-resume fix -- the
fix worked exactly as intended and is retained unchanged in
`source/stage1_grammar_driver.py` and `source/test_stage1_grammar_resume.py`
for any future dispatch that reopens this search. It was a deliberate
scope/cost judgment, legitimate under the contract's own `stopping_rules`
clause: "If enumeration at some complexity C <= 12 does not complete within
the Stage-1 grammar budget, the engine reports the largest completed
complexity C_complete ... not reaching C_max is a scoping fact, not a
failure and not a result." PID 16763 never completed or checkpointed any
part of complexity 7: `pareto-fronts-raw.json`'s `last_updated_utc`
(2026-09-08T18:16:29.539344Z) and `enumeration-checkpoint.json`'s
`last_updated_utc` (2026-09-08T18:16:29.537685Z) are both unchanged from the
state PID 3440 wrote before it exited. Zero additional wall-clock compute
contributed to this run's terminal data; no exact `SIGTERM` timestamp is
separately logged by the driver (a `SIGTERM` produces no log line).

**Terminal artifacts produced by this follow-up dispatch:** `raw-result.json`
(pure measurements: per-target Pareto fronts and collision-set sizes through
complexity 6, candidate-list scoring against INV-A1/INV-1/INV-2prime with
zero matches found -- and the explicit note that INV-A1 and INV-1, at
canonical node count 9, are structurally unreachable at `C_complete=6` so
their candidate-list verdict is undecidable from this run rather than "no
match"; INV-2prime, at node count 5, was genuinely reachable and searched
with no match found; engine-agreement stated as primary-engine-only since
the PySR arm remains `failed_infrastructure`; held-out isolation statement)
and `manifest.yaml` (replacing the prior `status: running` manifest,
recording `status: completed_valid`, the full timeline above, real measured
per-level timing, and an honest `required_artifacts_status` accounting of
which of `specification.yaml`'s full required-artifact list this
Delta/E_3-only, one-pack, `C_complete=6` run did and did not produce).
`manifest_pending_v2.yaml` (an intermediate draft written before this
terminal outcome was known, and before the checkpoint-resume fix's
production verification and the Coordinator's deliberate stop had happened)
has been deleted from this run directory now that its still-valid content
(environment/PySR-recheck detail, scope-deviation disclosures, candidate-list
hash reverification) has been fully incorporated into `manifest.yaml`; its
prior content remains readable in git history.

**What this terminal state is NOT:** it is not a NULL or ALIVE
classification of H-RELN-427bfd, and no such classification is asserted
anywhere in `raw-result.json` or `manifest.yaml`. It is not a claim that the
recovery-control gate, the held-out transfer anchor, or any named control in
`specification.yaml`'s `controls` block has been separately PASS/FAIL
re-evaluated by this run (see `raw-result.json`'s `controls_status` block).
It is not an extension of scope beyond the one pack / two statistics this
dispatch chain actually fitted (`R_1..R_8`, `coverage`,
`third_factorial_moment`, and the other five leaf packs remain fully
un-started, `C_complete=0`, honestly reported, not silently extended or
assumed complete). Per `TASK-20260907-8fd098`'s `review_reservation`, every
one of these open items — the NULL/ALIVE judgment on the E x-interval Delta
front chief among them — awaits independent validator and red-team review
before it can back any claim or change any status.
