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
