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

2. **`EXP-RELN-f202be` sibling data checked and found unusable.** Read
   `RUN-RELN-f202be-N14/N16/N18/N20/curve_results.json`: fields are
   `E3_direct_unreduced/reduced`, `delta_unreduced/reduced`,
   `forced_negation_gap_measured/expected`, `predicate_T_S_*`, an m=2
   x-class *signed* convention with a completely different statistic
   vocabulary (no `R_k`, no generic `Delta`/`E_m`/`coverage`/
   `third_factorial_moment` field). This does NOT satisfy
   `specification.yaml`'s `sibling_enumeration.primary_source` field-list
   validation, so per that clause ("the adapter validates the field set...
   and reports any missing field; it never fills one in"), this source was
   NOT used. This triggered the Stage-0e own-enumeration fallback (deviation
   #1 above).

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
