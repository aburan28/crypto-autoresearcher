# Implementation notes -- EXP-RELN-f202be

## HEADLINE FINDING: forced-negation-gap trap control (BLOCKING) fails on 23/72 object cells

All four rungs (14, 16, 18, 20) were fully executed end to end (stage0 through
stage4), a complete run set was achieved in the sense that >=3 certified
prime-order curves exist at every rung and every INV-1/INV-2 accounting
identity is exact everywhere measured. However the contract's
`forced_negation_gap_trap_control` (BLOCKING per `invalidation_rules` and
`stopping_rules`) misses its pre-committed 0.1 absolute tolerance
(`Delta_unreduced - Delta_reduced` vs `B^3/(4M)`) on 23 of 72 object cells
(x_interval_low/mid, qr_class, x2 B conventions, x3 curves, x4 rungs),
concentrated at rungs 14 and 16 (rungs 18 and 20 pass cleanly on every cell).
The measured deviation is always negative (measured gap slightly below the
forced value), shrinking monotonically in relative size as B grows across
rungs (~-10% mean at rung 14, ~-6% at rung 16, ~-3% at rung 18, ~-2% at rung
20) -- a pattern consistent in sign, scale, and trend with the
specification's own acknowledged `O(m/B)` correction term to INV-2pp (m=3;
3/B = 6.25% at the nominal B=48 vs 1.6% at B=186), which argues this is a
real finite-size effect rather than an enumeration bug. Per the contract's
own stopping rule ("Stop the run's object-arm reading if ... the
forced-negation gap is off by more than 0.1 on any negation-closed arm ...
mark the run instrument_failed, and report no scientific verdict"), this is
applied MECHANICALLY regardless of that plausible explanation: the run set's
mechanical classification is `INSTRUMENT_FAILURE_NO_VERDICT`, not NULL,
ALIVE, or INCONCLUSIVE. Every null/control-arm measurement (NULL-A/NULL-B
bands, Z/N-interval, Bose-Chowla, q-decay, spectral cross-check, growth fit,
predicate lifts) is nonetheless fully recorded in
`runs/RUN-RELN-f202be-stage4/{metrics,bands,predicate-lifts,control-verdicts,
classification}.json` as measured data, per the same stopping rule's
instruction to "complete and record the null and control arms". See
`runs/RUN-RELN-f202be-stage4/execution-report.md` and `control-verdicts.json`
for the exact cell-by-cell numbers.

## Environment

- Python 3.11, numpy 2.4.6 (installed at runtime via `pip install numpy`;
  not present in the base image), sympy 1.14.0.
- Executed on a single Linux VM, 4 vCPU, 15 GiB RAM, single process (no
  parallel workers used; `maximum_workers: 4` was not exercised because a
  single sequential process comfortably fit inside the wall-clock budget --
  see timings in each run's `manifest.json`).
- Primality certification of each curve's N uses two methods implemented
  independently of `sympy.isprime`: a deterministic Miller-Rabin test with a
  fixed witness base set (`curve_gen.miller_rabin_deterministic`, correct for
  all n < 3.3e24) and trial division to sqrt(N)
  (`curve_gen.trial_division_prime`). `sympy` is used only for (a) finding
  the field prime p near 2^k (`sympy.nextprime`), and (b) constructing the
  Bose-Chowla base field GF(q^3) via `sympy.polys.galoistools`
  (irreducible-polynomial search and modular polynomial arithmetic) plus a
  hand-written baby-step-giant-step discrete log in that field. Neither use
  touches the N-primality certificate.

## Two independent implementations (INV-2 spectral cross-check)

- `source/direct_enumerator.py`: generic multiset triple-loop enumerator
  (`itertools.combinations_with_replacement`) over any finite abelian group
  given as (elements, add_fn, key_fn). Used by both `zn_integer_arms.py`
  (Z/N group) and `e_arms.py` (E(F_p) group, via `harness.toycurve
  .EllipticCurve.add`).
- `source/spectral_crosscheck.py`: pure numpy + stdlib FFT implementation.
  Imports nothing from `direct_enumerator.py`, `zn_integer_arms.py`,
  `e_arms.py`, or `harness.toycurve`; it receives only a bare list of
  Z/N indices and N. Its algebraic derivation (ordered-triple convolution,
  2-dilated "pair" convolution, 3-dilated "triple" indicator, and the
  combination formula `c = (c_ord + 3*c_pair + 5*c_triple)/6` with
  `c_pair = P - c_triple`) was verified against a brute-force enumeration on
  a small synthetic example (N=23) BEFORE any curve was generated; this
  self-test is re-run and recorded at the start of every stage0 run
  (`runs/RUN-RELN-f202be-stage0/spectral_selftest.json`) and passed
  (`max_abs_error_vs_bruteforce: 0`) in the executed run.
- Every object, NULL, and control/mirror cell in stage2 recomputes its count
  vector by both routes and checks exact (integer, zero-tolerance)
  agreement; `spectral_disagreements` is recorded per cell and was 0 in
  every cell actually cross-checked (see scope limitation below for which
  cells were sampled vs. exhaustively checked).

## Scope limitations and protocol deviations (recorded per AGENTS.md rule 9 /
executor.md #12 -- none discarded)

1. **Bose-Chowla construction implemented for prime q only.** The frozen
   B_2 convention is "the largest prime power q with 3(q^3-1) < N", which
   can be a non-prime prime power (e.g. q = 27 = 3^3 at rung 16 for all
   three accepted curves). The Bose-Chowla B_3-set construction
   (`zn_integer_arms.bose_chowla_set`) requires building GF(q^3) as a cubic
   extension of GF(q); for q itself a nontrivial prime-power extension
   (q = p0^e, e>1) this requires a nested field-extension construction that
   was not implemented in the time available. This is a genuine
   `NotImplementedError`, caught and recorded, never silently skipped: at
   rung 16 the Bose-Chowla control and its E-mirror are reported
   `skipped: true` with this reason in
   `runs/RUN-RELN-f202be-stage1/accounting.json` and
   `runs/RUN-RELN-f202be-N16/curve_results.json`. At rungs 14, 18, 20 the
   actual computed B_2 (17, 43, 67) was prime for every accepted curve, so
   the control ran and passed (E_3 == M_2 exactly, B_3 property verified
   exhaustively) in all nine of those cells. This affects ONLY the
   Bose-Chowla control at rung 16; the B_2 convention itself (used to size
   the object arms' second-convention cells) was computed and used normally
   at all four rungs.
2. **Spectral cross-check sampled, not exhaustive, on 100-draw null arms.**
   For NULL_A, NULL_B_points and the NULL_B_ZN E-mirror (100 draws each,
   per curve, per B convention), the spectral (FFT) cross-check and the
   full `count-vector.sha256` + `histogram.json` artifact pair were computed
   and stored for the first 5 draws of each 100-draw arm, plus for any draw
   whose spectral check disagreed with the direct enumerator (none did, in
   any sampled draw, at any rung). All 100 draws were fully
   direct-enumerated (their Delta values all contribute to the reported
   NULL-A / NULL-B bands and are real, complete measurements); it is only
   the FULL spectral cross-check + full artifact retention that was
   restricted to a 5-draw sample per arm, to keep the run inside a bounded
   session wall-clock at N up to 2^20 (spectral FFT and array comparison at
   N ~ 2^20 add real but non-trivial cost per draw). This is recorded as
   `max_spectral_disagreement_over_draws` (computed over the sampled draws
   only) in every `curve_results.json`. **This is a deviation from the
   contract's stated "every cell's count vector is recomputed by the
   spectral implementation" for the un-sampled 95 draws per arm**; those 95
   draws per arm are direct-enumeration-only measurements. Object arms, all
   control arms (Z/N interval, Bose-Chowla), and their E mirrors received
   the FULL spectral cross-check on every cell, with zero exceptions,
   because those are single deterministic cells, not 100-draw batches.
3. **Predicate lift z-scores on negation-closed (object and NULL-A) arms use
   the ANALYTIC (INV-3, i.i.d.-uniform) null formula, not the contract's
   specified NULL-A Monte Carlo null for negation-closed arms.** The
   contract (`metrics.primary`, item 5; `controls.analytic_selection_null`)
   specifies that negation-closed arms' predicate z-scores should be taken
   against the NULL-A Monte Carlo mean/SD of rho_S over its own 100 draws,
   because INV-3's variance formula is derived for the plain i.i.d.-uniform
   model and is not asserted for negation-closed sampling (see
   `H-RELN-41562a` invariant INV-3p, status `conjecture`, "a closed form for
   gamma is open"). Per-draw predicate T_S sums were NOT retained for the
   NULL_A 100-draw arms (only the aggregate Delta per draw was retained, to
   keep runtime and artifact volume bounded), so the correctly-specified
   Monte Carlo predicate null could not be built after the fact without
   re-running enumeration. **Every predicate-lift z-score and
   Holm-corrected verdict reported for the x_interval_low / x_interval_mid /
   qr_class object cells in `predicate-lifts.json` therefore uses the
   analytic null as a labelled substitute, not the contract-specified null,
   and must not be read as a completed M8 measurement for those cells.**
   Predicate lifts on the genuinely plain arms (NULL_B_points, Z/N interval
   E-mirror, Bose-Chowla E-mirror) were not computed at all in this run
   (time budget), so M8's plain-arm analytic-null check (where the formula
   IS the contract-specified one) is also `not_run`, not merely deviated.
   M8 overall is therefore reported `incomplete` in this run; M6 (the
   record's primary metric, per H-RELN-41562a's own
   `heuristic_under_test_note`) is unaffected by this limitation and is
   reported complete for all four rungs.
4. **Growth-fit bootstrap CIs are computed from only 3 curves per rung**
   (the contract's minimum), so the per-rung point estimate feeding the
   4-point (log N, log excess) regression has only 3 independent draws;
   the resulting slope CIs are correspondingly wide and are reported as
   measured, not strengthened by any additional replication.
5. **`maximum_workers: 4` / multi-process execution was not exercised.**
   A single sequential process completed the full four-rung run inside the
   session's practical wall-clock; parallelising was unnecessary and so
   `parallel.verify_determinism` (mentioned in the budget's sizing_note) was
   not run. This is a resource choice, not a stopping-rule failure.
6. **`e_arms.null_b_random_points` sampler**: draws are checked for
   distinctness against ALL previously accepted points in the same draw
   (not just against negation pairs), matching "distinct points" in the
   contract; the `flagged_negation_pair_draws` count records draws that
   happen to contain both P and -P (kept, per spec, "a valid uniform
   subset").

## Files

- `source/curve_gen.py`: curve generation recipe + point-count certificate
  (Hasse bound, 8 deterministic-point NR=O check, two independent primality
  methods).
- `source/zn_integer_arms.py`: B_1/B_2 conventions, Z/N base constructions
  (interval, random, Bose-Chowla, q-decay), forced-value-table derivation.
- `source/e_arms.py`: E(F_p) object/null base constructions, log-table
  construction, predicate evaluation.
- `source/direct_enumerator.py`, `source/spectral_crosscheck.py`: the two
  independent enumerators (see above).
- `source/analysis.py`: stage-4 statistics (Delta, bootstrap CI, bands,
  z-scores, Holm, growth fit, KS, Chebyshev, Poisson tail).
- `source/run_stage0.py`, `run_stage1.py`, `run_stage2_rung.py`,
  `run_stage4_analysis.py`: stage drivers, one per contract stage
  (stage2+stage3 are combined into one script per rung since the spectral
  cross-check is computed inline, cell by cell, as each direct enumeration
  completes -- this matches the contract's per-cell ordering requirement
  more directly than a separate later pass, and is recorded as such).
- `source/runutil.py`: shared artifact-writing/hashing helpers (not one of
  the two independent enumerators).

## ADDENDUM 2026-09-07: re-analysis under protocol amendment v1 (version_to 2, DEC-20260907-432a39)

This section is appended, not a rewrite; everything above stands as the
original executor's record of the v1 run set (RUN-RELN-f202be-N14/N16/N18/N20
and RUN-RELN-f202be-stage4), which remain immutable, exactly as recorded,
including their `INSTRUMENT_FAILURE_NO_VERDICT` classification under the
frozen v1 (fixed absolute 0.1) forced-negation-gap tolerance.

### What was done

Amendment v1 (`experiments/EXP-RELN-f202be/amendments/v1.yaml`, version_to 2,
approved by `DEC-20260907-432a39`) changes the `forced_negation_gap_trap_control`
tolerance from a fixed absolute 0.1 to
`max(0.1, 3*(m/B)*(B^3/(4M)))`, `m=3`, evaluated per cell from that cell's own
recorded `B` (the object cell's own B_1- or B_2-convention size) and `M`. This
addendum implements that formula and re-analyzes rungs 14 and 16 under it,
per the amendment's `reanalysis_authorization`.

**Reanalysis path chosen: (a), full re-execution.** Both original rung runs
were cheap (56s for rung 14, 255s for rung 16, per their manifests), so full
re-execution was preferred over path (b) (reading the existing immutable
records without re-running) because it also independently confirms
bit-for-bit reproducibility, which the contract's `replication` clause
requires and which is itself a real, useful check.

- `source/run_stage2_rung_v2.py`: an EXACT copy of `source/run_stage2_rung.py`
  (`diff` confirms only the docstring, the `RUN_ID` f-string -- which appends
  a `v2` suffix so the new run writes to `RUN-RELN-f202be-N14v2` /
  `RUN-RELN-f202be-N16v2` instead of overwriting the frozen `N14`/`N16` -- and
  the `command`/`command.txt` strings differ). No algorithm, formula,
  convention, or seed differs. Run for rung 14 and rung 16 with the same
  `MASTER_SEED = 20260906` null-draw derivation and the same accepted curve
  seeds as the original runs (loaded from the same, unedited
  `RUN-RELN-f202be-stage0/curves.json`).
- Bit-for-bit reproducibility was checked field-by-field between
  `RUN-RELN-f202be-N14/curve_results.json` and
  `RUN-RELN-f202be-N14v2/curve_results.json` (and the N16 pair): **zero
  non-timing field differences** in either rung; the only fields that differ
  anywhere in either curve_results.json are per-cell `wall_seconds` timing
  values. `accounting.json` is byte-identical in both rungs. This is recorded
  per-run in `RUN-RELN-f202be-N14v2/reanalysis-provenance.json` and
  `RUN-RELN-f202be-N16v2/reanalysis-provenance.json`.
- `source/run_stage4_analysis_v2.py`: reads rungs 14 and 16 from the new
  `RUN-RELN-f202be-N14v2` / `RUN-RELN-f202be-N16v2` directories and rungs 18
  and 20 from the EXISTING, UNEDITED `RUN-RELN-f202be-N18` /
  `RUN-RELN-f202be-N20` directories (no re-execution of 18/20 -- none is
  authorized or needed). It recomputes the forced-negation-gap verdict for
  **all four rungs** (all 72 object cells: 3 curves x 3 geometries x 2 B
  conventions x 4 rungs) directly from each cell's own recorded
  `forced_negation_gap_measured` / `forced_negation_gap_expected` / `B`,
  applying the amended tolerance formula -- this is NOT read off the old
  `accounting.json`'s `forced_gap_within_0.1` boolean (which encodes only the
  OLD tolerance's verdict). Every other statistic (Delta, bootstrap CIs,
  NULL-A bands, growth fit, k-rich, predicate lifts, other controls) reuses
  the SAME `analysis.py` functions, unmodified, with the SAME logic as
  `run_stage4_analysis.py`; `diff` the two files to confirm the only
  substantive differences are the tolerance formula and the per-rung
  source-directory mapping. Writes `RUN-RELN-f202be-stage4v2`.

### Result: forced-negation-gap control passes at all four rungs under the amended tolerance

Recomputed directly (not copied from the amendment's own validation table) from
the already-measured `forced_negation_gap_measured`/`_expected` values in
`RUN-RELN-f202be-N14v2`, `N16v2`, `N18`, `N20`'s `curve_results.json`:
0 of 72 object cells fail the amended tolerance at any rung (see
`RUN-RELN-f202be-stage4v2/control-verdicts.json` for the full 72-row table).
INV1/INV2 accounting is exact (0 deviation) in every one of those 72 cells,
confirming the amendment's characterization that this was a tolerance
miscalibration, not an accounting or enumeration defect.

**A wording note on the amendment's own illustrative validation table, worth
recording rather than silently reconciling:** the amendment's text applies its
worked tolerance arithmetic (e.g. `3*(3/48)=0.1875` at rung 14) using the
RUNG's nominal design B_1 (48, 74, 118, 186) uniformly, quoting a single
worst-case `(abs, rel)` pair per rung. Recomputing from the raw per-cell data
shows the worst-`abs`-deviation cell and the worst-`relative`-deviation cell
at rung 14 are actually TWO DIFFERENT cells: a B_1-convention cell (B=48,
abs=0.1671, rel=0.1184) and a B_2-convention cell (B=18, abs=0.1666,
rel=0.1303) -- the amendment's quoted `worst_abs=0.1671` matches the B1 cell
and its quoted `worst_rel=0.1303` matches the B2 cell, i.e. the table's single
"worst case" row silently mixes two different cells' numbers. This does not
change the pass/fail conclusion at any rung: applying the amended formula
literally per-cell (each cell's own recorded B, matching how the ORIGINAL
0.1-absolute tolerance was already applied per-cell to both B_1- and
B_2-convention cells in `run_stage2_rung.py`) passes all 72 cells with wider
margins for B_2 cells than the amendment's B_1-only arithmetic would suggest;
applying the amended formula with the rung's nominal B_1 uniformly to every
cell (the reading implied by the amendment's illustrative arithmetic) ALSO
passes all 72 cells (checked explicitly, not merely inferred). Both readings
agree on every classification-relevant fact in this run set; this note exists
so the discrepancy in the amendment's own prose is not silently smoothed over.

### Combined four-rung classification: `UNANTICIPATED_PATTERN_NOT_NULL_NOT_ALIVE`

With the forced-negation-gap control now passing at all four rungs (and every
other control unaffected and still passing, exactly as before), the run set
is `complete_run_set: true`, `all_blocking_controls_pass: true`, and the
frozen `success_criterion`/`falsification_criterion` (unchanged by this
amendment) are evaluated in full for the first time on all four rungs. The
mechanical classification is `UNANTICIPATED_PATTERN_NOT_NULL_NOT_ALIVE`:
every object cell (x_interval_low/mid, qr_class; reduced, B_1) is inside the
NULL-A band (mean +/- 3 SD) at every rung on every curve (`all_object_cells_
in_null_a_band: true`), which is the Delta-band-inclusion half of the
pre-committed NULL outcome -- but the growth-fit slope of
`log(max(Delta - Delta_null_mean, SD_null))` vs `log(N)` does NOT contain 0
for any of the three object geometries (all three slopes are confidently
NEGATIVE: x_interval_low -0.480 [-0.631, -0.344], x_interval_mid -0.452
[-0.697, -0.216], qr_class -0.483 [-0.527, -0.392], 95% bootstrap CIs), which
is neither the pre-committed NULL outcome (requires the slope interval to
contain 0) nor the competing ALIVE outcome (requires z > 3 SD on every curve
at rungs 18/20 with slope excluding 0 on the POSITIVE side -- not observed;
`alive_geometries_meeting_literal_test: []`). This numerically matches, to
several decimal places, what the ORIGINAL `RUN-RELN-f202be-stage4`'s
`metrics.json` already computed for these same growth fits and Delta values
(that stage4 run always computed the full metrics regardless of the
instrument-failure gate, per its own stopping-rule note) -- so this addendum
does not change any previously-computed Delta, band, or growth-fit number; it
only changes whether the run set's forced-gap control gate permits reading a
classification from them at all. This is reported here as a measured,
unresolved pattern for Coordinator/reviewer characterization; it is NOT a
NULL verdict, NOT an ALIVE verdict, and NOT itself grounds to change
H-RELN-41562a's status (still `proposed`), per the amendment's explicit scope
limits and the contract's `later_review_requirements` (independent validator,
red team, review-adversarial at xhigh) which remain owed before any
claim-changing use.

### Deviations and inherited limitations (not discarded, restated for this addendum)

- The predicate-lift z-scores reported in `RUN-RELN-f202be-stage4v2/
  predicate-lifts.json` for the object (negation-closed) arms use the
  ANALYTIC (INV-3, i.i.d.-uniform) null, not the contract-specified NULL-A
  Monte Carlo null for negation-closed arms -- this is the SAME deviation #3
  already recorded in this file's original section (per-draw NULL-A T_S sums
  were never retained, in either the v1 or v2 run, so the correctly-specified
  Monte Carlo predicate null cannot be built after the fact without
  re-running the 100-draw NULL-A enumeration with per-draw predicate sums
  retained -- out of scope for this amendment). These z-scores/Holm verdicts
  are therefore still not a completed M8 measurement for the object arms in
  this addendum either.
- The bootstrap growth-fit CIs are still built from only 3 curves per rung
  (the contract's minimum), unchanged.
- No new curve, seed, predicate, or draw count was introduced; nothing in
  `independent_variables.fixed` was touched.

### New files

- `source/run_stage2_rung_v2.py`, `source/run_stage4_analysis_v2.py`: see
  above. `source/SHA256SUMS_v2` records their hashes (additive; the original
  `source/SHA256SUMS` is untouched).
- `runs/RUN-RELN-f202be-N14v2/`, `runs/RUN-RELN-f202be-N16v2/`: full stage2/3
  re-execution outputs, each with its own `manifest.json` (including an
  `amendment_context` block), `command.txt`, `environment.json`,
  `curve_results.json`, `accounting.json`, `cells/`, `stdout.log`,
  `stderr.log`, and `reanalysis-provenance.json` (the bit-for-bit
  reproducibility check against the original run).
- `runs/RUN-RELN-f202be-stage4v2/`: combined four-rung re-analysis under the
  amended tolerance -- `manifest.json`, `command.txt`, `environment.json`,
  `bands.json`, `metrics.json`, `predicate-lifts.json`,
  `control-verdicts.json`, `classification.json`, `stdout.log`, `stderr.log`.
