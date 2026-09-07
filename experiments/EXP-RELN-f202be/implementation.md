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
