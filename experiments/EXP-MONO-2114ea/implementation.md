# EXP-MONO-2114ea implementation notes

Graded multi-curve positive control for H-MONO-663fb4's Fisher-combined
statistic. Full frozen contract: `specification.yaml`. This file records
implementation decisions, reuse boundaries, and disclosed protocol
deviations/edge cases, per AGENTS.md's "record, never discard" rule.

## Reuse boundaries (what was imported vs. copied vs. written fresh)

- **Imported directly, byte-identical, not copied**: `fields.py`, `curve.py`,
  `conv.py`, `groupstate.py`, `stats.py` from
  `experiments/EXP-MONO-b19c6b/implementation/`, via `sys.path` insertion in
  `run.py`. None of `fisher_combined_pvalue`, `permutation_pvalue`,
  `holm_bonferroni`, `chi2_sf_even_df`, `character_spectrum`,
  `var_from_character_side`, `max_C`, `convolution_tower`, `exact_stats`,
  `cell_stats_fft`, or `stat_bundle_from_coords` were modified or
  reimplemented.
- **Copied verbatim + diffed at run time**: `subgroup_control`, copied
  byte-for-byte from `experiments/EXP-MONO-c819ba/implementation/controls.py`
  into this directory's own `controls.py`. `run.py` calls
  `controls.verify_subgroup_control_source_verbatim()` (mirroring
  EXP-MONO-b1423c's own `run.py::verify_subgroup_control_source_verbatim`
  pattern exactly) BEFORE any Stage 1 cell is computed; the run halts as
  `failed_infrastructure` on any mismatch. Result: match confirmed
  (`raw-result.json` `stage1_ro3_reproduction.subgroup_control_source_verbatim_match:
  true`).
- **Imported (not copied) for Stage 1 ONLY**:
  `experiments/EXP-MONO-b1423c/implementation/controls.py::draw_symmetric_null_subset`
  and that contract's own `seed.py::NullSubsetDrawer`, loaded via
  `importlib` at run time under EXP-MONO-b1423c's own frozen
  `domain="EXP-MONO-b1423c/v1"` and `master_seed=20260901`, so that Stage
  1's 20000-draw-per-cell null populations are bit-for-bit identical to
  that contract's own archived draws. Because both b19c6b's and b1423c's
  own `seed.py` modules are named `seed`, `run.py::
  load_b1423c_draw_symmetric_null_subset` temporarily overrides
  `sys.modules['seed']` to b1423c's own seed module ONLY while loading
  b1423c's `controls.py` (whose own `from seed import NullSubsetDrawer`
  needs to resolve there), then restores the prior binding. This does not
  affect `curve.py`'s own already-resolved `seed_int` name, which was
  bound at `curve.py`'s own import time, before this swap.
- **New to this contract**: `implementation/seed_stage2.py` (this
  contract's own frozen `seed_derivation_rule`, keyed on
  `(p, F, curve_ordinal, draw_index)`, used for every Stage 2/3 null
  population); `implementation/controls.py`'s own NEW functions below the
  verbatim-copy marker (`smallest_admissible_subgroup_index`,
  `fixed_coset_for_curve`, `take_symmetric_prefix`,
  `construct_perturbed_factor_base`); `implementation/run.py` (this
  contract's own orchestration script, including `primary_F_of`, a literal
  reproduction-by-value of EXP-MONO-b19c6b's own `run_experiment.py::
  primary_F_of` formula, needed to reconstruct each pool curve's real,
  unperturbed factor base deterministically from its archived (p,A,B) --
  that driver script is not one of the five files this contract must
  import byte-identical, since it is the panel-construction driver, not
  the reused statistical instrument).

## Disclosed engineering decisions (made BEFORE any Stage-2/3 number was observed)

1. **Fixed coset choice**: the "ONE fixed proper-subgroup coset" per curve
   (`inputs.planted_perturbation_construction`) is realized as the
   subgroup `H_k` ITSELF (the trivial/identity coset), where `k` is the
   smallest divisor >1 of that curve's own `n2` (the smallest-index proper
   subgroup its own group admits, via `subgroup_control`, generalized from
   RO3's own `n1=3,n2=96` to each pool curve's own `(n1,n2)`). A
   non-trivial shifted coset `gH_k` would have produced an IDENTICAL
   `|Shat(chi)|` spectrum magnitude (hence identical `C`, `Var`) at every
   character, since `|chi(g)|=1`; using `H_k` itself is simplest and keeps
   the closed-form identity directly legible. Disclosed in
   `controls.py::fixed_coset_for_curve`'s own docstring.

2. **Real factor base reconstruction**: each pool curve's own real,
   unperturbed x-coordinate factor base is `cs.fb_full[:F]`, F =
   `primary_F_of(N) = N//4 forced even`, EXACTLY reproducing
   EXP-MONO-b19c6b's own `run_experiment.py::primary_F_of` +
   `cs.fb_full[:F]` prefix-truncation convention (NOT `curve.py`'s own
   `factor_base_x_coords`'s full, untruncated QR set, which is
   substantially larger than `N/4` at these curve sizes -- confirmed by a
   direct check during implementation: the untruncated set for
   curve_ordinal 0 (N=70) has 68 elements, not the archived F=16).
   Verified against every pool curve's own archived (N, n1, n2, F) before
   any Stage 0/2 compute for that curve (`raw-result.json`'s
   curve-reconstruction gate; all 15 pool curves matched exactly, no
   `failed_infrastructure`).

3. **Odd swap-count parity handling**: `round(r * F)` can be ODD with NO
   self-negating (2-torsion, or `(0,0)`) candidate available in either the
   removal side (the curve's own real factor base prefix) or the addition
   side (the fixed coset's elements not already in the factor base) at
   these toy curve sizes -- an odd symmetric (`FB=-FB`-preserving) swap is
   then genuinely impossible. `controls.py::construct_perturbed_factor_base`
   decrements such a count by 1 to the nearest even number, disclosed as
   `count_parity_adjusted: true` and `count_requested_raw` vs. `count`
   (the count actually used) in every affected cell's Stage 0 record.
   This mirrors this lane's own precedent (`primary_F_of`'s "F=N/4, forced
   even") and is decided by a pure parity/feasibility check on the
   swap-candidate lists -- BEFORE any Stage-2/3 number is computed or
   observed -- so it is not a post-hoc protocol change under
   `invalidation_rules`. **22 of the 45 (curve, fraction) combinations in
   the candidate pool required this adjustment** (full list in
   `raw-result.json`'s `stage0_per_curve_elevation`); several of these
   (e.g. curve ordinal 0 at fraction 0.05, adjusted count 1 -> 0) result in
   ZERO actual perturbation being applied at that (curve, fraction) pair --
   the curve's own real factor base is small enough (F=16) that 2%/5% of it
   rounds to 0 or 1 with no available odd slot, so the "planted effect" at
   that specific (curve, fraction) combination is, in fact, no effect at
   all. This is reported as-is, not patched around, because the frozen
   `planted_perturbation_construction` text does not specify a minimum
   swap count and the pool/fraction combination was fixed before any run.

4. **Grid does not contain a joint (10%, 15-curve) cell.** H-MONO-d9dc51's
   own `falsification_conditions[2]` and this spec's own
   `falsification_criterion(d)` both name "the strongest tested cell (10%
   perturbation, 15 curves)" as if it is one of the tested grid cells. The
   COORDINATOR-APPROVED 5-cell L-shaped grid (all three fractions at
   panel size 10; all three panel sizes at fraction 5%) shares only the
   `(0.05, 10)` cell between the two ladders and does NOT test
   `(0.10, 15)`. This is reported explicitly in `raw-result.json`'s
   `strongest_tested_cell_note` rather than silently substituting a nearby
   cell: the oracle outcome is reported at BOTH tested edges instead
   (`r=0.10,k=10` -- the highest tested fraction, at its own tested panel
   size -- and `r=0.05,k=15` -- the largest tested panel, at its own
   tested fraction). Neither edge cell's oracle arm rejects in this run
   (see Results below), so this gap in grid coverage does not change this
   run's own outcome-label classification, but it is a real mismatch
   between the hypothesis's own falsification language and the approved
   grid design, which the Coordinator/Validator/Red Team should be aware
   of independent of this run's own result.

## Stage-by-stage summary of what the code does

- **Stage 0** (`run.py::stage0_gate_floor_vs_threshold`,
  `stage0_exact_elevation_check`): BEFORE any of the 20000 Stage-2 null
  draws are spent, (a) reports the Fisher combination's own
  floor-vs-threshold ceiling at k in {5,10,15,48} (all-floor panels DO
  reject at alpha=0.05 at every tested k, per `raw-result.json`'s
  `stage0_floor_vs_threshold` -- expected, since this is the maximally
  favorable case, not an observed result); (b) for every pool curve and
  every fraction, directly computes the perturbed factor base's own
  `Shat(chi)` spectrum (`conv.py::character_spectrum`) and independently
  reconstructs it via linearity (`Shat_perturbed = Shat_orig - Shat_removed
  + Shat_added`), comparing the two -- an exact algebraic identity, not an
  approximation. Max observed relative error across all 45 (curve,
  fraction) combinations: `6.42e-13`, well under the 1e-9 gate.
- **Stage 1** (`run.py::run_stage1_ro3_reproduction`): reproduces
  EXP-MONO-b1423c's own RO3 cells (h=N/2=144, h=N/4=72) bit-for-bit,
  using that contract's own domain/master_seed for the null draws. All
  four archived targets (S1-S4) and both cells' S5 raw p-values matched to
  well under the 1e-9 relative gate. PASSED; Stage 2/3 proceeded.
- **Stage 2** (`run.py::main`, per-pool-curve loop): for each of the 15
  candidate-pool curves (curve_ordinals 0-14, the first 15 by ascending
  ordinal of the archived 48-curve random-ordinary background panel), one
  20000-draw null population (Var and C/F, m=4) is computed ONCE, keyed on
  `(p, F, curve_ordinal)` per this contract's own frozen
  `seed_derivation_rule`, and reused across every fraction and every grid
  cell that curve participates in (no redraw per cell -- confirmed by
  construction, not merely asserted). Each curve's own perturbed
  permutation p-value (Var, C/F) is computed at each of the three
  fractions against that SAME null population.
- **Stage 2 matched-null-panel control**: for panel sizes {5,10,15}, the
  full-panel and oracle Fisher combinations of the SAME pool curves' own
  ALREADY-ARCHIVED (unperturbed) raw p-values are reported -- no new
  draws are spent for this arm, per the spec's own "read directly from
  RUN-MONO-b19c6b-1's raw-result.json" instruction. Because the full-panel
  arm always combines the SAME 48 archived values regardless of which k
  curves are nominally "selected," its value is identical across all
  three panel sizes by construction -- reported as an observation, not a
  bug (see `matched_null_panel_control` in `raw-result.json`, where
  `T3_full_panel_var`/`T3_full_panel_cf` are numerically identical at
  k=5,10,15).
- **Stage 3** (`run.py::main`, grid-cell loop): for each of the 5 declared
  grid cells, reports T1 (full-panel Fisher), T2 (oracle Fisher), T4
  (per-curve Holm outcome on the same mixed panel), alongside T3 (matched
  null-panel, reported once per panel size) and T5 (Stage 1 reproduction).

## Results (observations only; no verdict on H-MONO-d9dc51 or H-MONO-663fb4)

- Stage 0: both gates passed (see above).
- Stage 1: reproduced EXP-MONO-b1423c's own archived S1-S4 and both
  cells' S5 raw p-values exactly.
- Dual-path control (route 1 direct convolution vs. route 2 FFT):
  within 1e-9 relative tolerance on every real-arm cell (unperturbed and
  perturbed), every pool curve (`dual_path_control_all_within_1e-9: true`).
- Matched null-panel control: clean at every tested panel size -- no
  full-panel or oracle rejection at alpha=0.05 anywhere
  (`matched_null_panel_clean_at_every_panel_size: true`).
- Detection-power surface: NO cell (full-panel or oracle, either
  statistic) rejects at alpha=0.05 anywhere in the tested 5-cell grid
  (`stage3_any_cell_rejects: false`, `stage3_smallest_rejecting_cell: null`).
  Both tested "edge" cells in place of the untested `(0.10,15)` joint
  corner (see disclosed decision 4 above) also fail to reject in the
  oracle arm.
- Per-curve Holm outcome (T4): zero curves reach Holm-corrected
  significance at any grid cell, either statistic -- the per-curve test
  ALSO does not detect the planted effect at any tested combination.
- Per `specification.yaml`'s own `outcomes` block: Stage 0/1 passed; the
  matched null-panel control is clean at every panel size; no cell
  rejects anywhere in the grid, including both tested edges of the
  untested `(0.10,15)` corner. This matches the definition of
  `sensitivity_gap_confirmed_everywhere_tested` (H-MONO-d9dc51's outcome
  B) as stated in the spec's own `outcomes` block -- reported as the
  applicable label per the spec's own success_criterion, which is
  decidable under either outcome A or B from the same required artifacts.
  This is a report of which label applies per the frozen contract's own
  text, not an interpretation of what it means for H-MONO-663fb4 or the
  broader research question; that judgment is reserved for the Validator,
  Red Team, and Coordinator.

## Certificate

`certificate.kind: none` -- pure measurement/statistics run; no DLOG solve
or relation collected or claimed, per `docs/claims-and-verification.md`.

## Reproducibility

`python3 experiments/EXP-MONO-2114ea/implementation/run.py`, run from that
directory, with no arguments and no external state beyond the two reused
raw-result.json files it reads and the reused implementation files on
`sys.path`. Two independent invocations of the identical command
(47.87s and 47.55s wall-clock) produced numerically identical Stage
0/1/2/3 results to full float precision; only the final invocation's
stdout/stderr logs are retained as this run's artifacts, matching this
lane's own established precedent (EXP-MONO-b1423c's manifest.yaml
`timing.note`).
