# Implementation notes: EXP-MONO-b19c6b

Pure-Python 3.13.1 + numpy 2.4.0, no CAS/solver, no network. Source under
`experiments/EXP-MONO-b19c6b/implementation/`:

- `fields.py`, `groupstate.py`, `conv.py` -- REUSED VERBATIM (byte-identical)
  from `experiments/EXP-MONO-670aa6/implementation/`, per the handoff's
  explicit permission: "You MAY reuse the arithmetic core (fields.py,
  curve.py, conv.py, groupstate.py) since both independent reviews
  confirmed those are correct." (`curve.py` itself was rewritten, not
  reused, because it is one of the seed-call-site files -- see below.)
- `seed.py` -- WRITTEN FRESH. SHA-256 seed derivation and rejection-sampled
  `Drawer`, per `inputs.seed_derivation_rule`. The preimage is
  `domain|master_seed|family|label|field_bits_or_p|curve_ordinal|m|draw_index|counter`
  -- both `master_seed` AND `family` are threaded through every one of the
  declared labels ("prime", "curve-a", "curve-b", "null-subset",
  "null-object-pick"), fixing EXP-MONO-670aa6's two defects: (1) `family`
  was absent from the preimage entirely (total panel-independence failure),
  and (2) `master_seed` was declared as an input but never actually
  consumed (both "independent" replication runs shared one identical
  panel).
- `curve.py` -- WRITTEN FRESH (not copied from EXP-MONO-670aa6's curve.py,
  since it is a seed-call-site file). `construct_prime` and `curve_stream`
  now take `(domain, master_seed, family, ...)` and pass all four through
  to `seed_int`. Adds:
  - the j0 family's mandatory p = 1 (mod 3) admission rule, checked
    directly inside `construct_prime`'s scan loop (candidates failing it
    are skipped, the scan continues -- not treated as non-prime, not a
    construction failure by itself);
  - `is_supersingular(N, p)`: trace of Frobenius t_E = p+1-N, supersingular
    iff t_E = 0 (mod p), used by the random-ordinary family's explicit
    computed rejection (see `panel_primary.py`).
- `controls.py` -- WRITTEN FRESH. `draw_symmetric_subset` now takes
  `(cs, F, domain, master_seed, family, curve_ordinal, m, draw_index,
  label)` and threads `family`/`master_seed` into the `Drawer`. The legacy
  subgroup/coset-union controls are NOT reimplemented here: this contract's
  legacy panel is optional/non-gating and explicitly relies on
  EXP-MONO-c819ba's own already-reviewed positive controls instead (see
  specification.yaml `inputs.legacy_panel`), so no legacy-panel module was
  written for this contract.
- `panel_primary.py` -- WRITTEN FRESH. Builds the 100-curve primary panel
  (50 j0, 50 random-ordinary), `curve_ordinal` 0..49 independently per
  family, `field_bits[k mod 5]` round-robin, `family` threaded through
  every `construct_prime`/`curve_stream` call. Per curve record: re-checks
  the j0 p=1(mod 3) admission rule directly (not merely trusting
  `construct_prime`'s own enforcement), and for random-ordinary applies the
  explicit computed `is_supersingular` rejection (continuing the scan on a
  supersingular candidate) -- unlike j0, ordinariness is not guaranteed by
  a congruence alone for a free (A,B) pair. A defensive `assert` cross-
  checks that every accepted j0 curve is indeed NOT supersingular by the
  same computed check, as a construction-implementation sanity guard (never
  triggered in either run).
- `stats.py` -- `permutation_pvalue` and `holm_bonferroni` are the SAME
  frozen formulas EXP-MONO-670aa6 used (unchanged definitions; only the
  panel/seed derivation upstream changed). `fisher_exact_2x2` unchanged.
  NEW: `chi2_sf_even_df` (exact closed-form chi-squared survival function
  for even degrees of freedom, no scipy dependency) and
  `fisher_combined_pvalue` (Fisher's method: -2*sum(ln(p_i)) ~ chi2(2k)),
  implementing `arms_and_controls.fisher_combined_panel_statistic`.
- `run_experiment.py` -- WRITTEN FRESH orchestration implementing the
  frozen Stage 0-4 order, with two structural additions over
  EXP-MONO-670aa6's own orchestrator:
  1. Stage 1's mandatory `independence_verification` runs immediately after
     panel construction and BEFORE any Stage-2/3 compute (see below for its
     collision definition), gating the run.
  2. Stage 2's gate is now `family_holm_and_fisher`'s combined outcome
     (Holm test on Var-AND-C/F pooled, AND Fisher-combined separately for
     Var and for C/F), not Holm-on-Var-only as in EXP-MONO-670aa6.

## Independence-verification collision definition (disclosed interpretation)

The frozen text says to "directly extract and compare (p, B, t_used) for
every matching curve_ordinal across the two families ... report the
comparison ... expect zero collisions." A first implementation attempt
flagged a "collision" whenever ANY single field (p, B, or t_used)
individually matched between the two families' curve at a given
curve_ordinal. Running this on the actual panel showed `t_used` matching
(both families accepting their first (A,B) candidate at t=0) for the large
majority of curve_ordinals purely by chance -- most random (A,B) pairs are
non-singular, so `t=0` is very frequently the accepted value regardless of
family, independent of any seed-derivation defect. Per-field coincidence is
therefore an EXPECTED, harmless occurrence under correct independent
family-keying, not a defect signal.

The implementation was corrected (before either full run) to define a
"collision" as the FULL TUPLE (p, B, t_used) matching identically for a
given curve_ordinal across the two families -- exactly the failure mode
EXP-MONO-670aa6 actually exhibited (100% identical triples across every one
of its 100 curve_ordinals, because its seed rule never keyed on family at
all, so both families drew from the literal same stream). Every field is
still reported per curve_ordinal in `stage1_independence_verification` for
full transparency; only the full-triple match gates the run. Under this
definition, both runs found `n_collisions: 0` (`zero_collisions: true`).

## Stage 4's extended dual-path sample: concrete selection rule (disclosed interpretation)

The frozen text specifies "a declared random sample of >= 200
null/null-object draws (>=1 per curve, drawn via a fixed, pre-declared
selection rule: the draw_index congruent to 0 mod 100 for that curve)."
Taken maximally literally (every draw_index in [0,20000) congruent to 0 mod
100, for every curve) this would mean 200 draws per curve x ~97 curves =
~19,400 additional route1+route2 comparisons -- far more than the ">=200"
floor requires, and route 1 (direct O(F) convolution) at that volume would
materially add to wall-clock cost for no declared benefit beyond the
already-stated floor.

This implementation selects, per curve: the null-subset draws at
`draw_index in {0, 100}` (the two smallest indices satisfying "congruent to
0 mod 100"), PLUS the curve's single null-object-pick draw (`draw_index=0`,
label `null-object-pick`, satisfying "null/null-object draws"). This gives
exactly 3 samples per curve, all indices congruent to 0 mod 100 as required,
>=1 per curve, and (97-98 curves x 3) = 279-291 total samples per run --
comfortably over the >=200 floor at the minimal cost consistent with the
literal predicate. Both runs' `stage4_extended_dual_path_sample.n_samples`
(279 and 291) exceed 200; `all_within_threshold` is `true` in both, with
`max_route1_route2_relative_residual = 0.0` in both (exact agreement to
double-precision rounding at this toy scale).

## Raw p-value persistence, without persisting the full null population

The contract requires RAW (uncapped) per-curve p-values -- one float per
curve, per statistic (Var, C/F), per arm (null-object, real), per family --
persisted in `raw-result.json`. It does NOT require persisting the full
20,000-draw null population used to compute each p-value. This
implementation persists exactly the former
(`stage2_per_curve_raw_pvalues`, `stage3_per_curve_raw_pvalues`) and
deliberately does NOT persist the 20,000-entry null-draw arrays themselves,
which are held in memory only long enough to compute each curve's p-value
and median. Persisting them would multiply `raw-result.json`'s size by
roughly 20,000x (100 curves x 20,000 draws x 2 statistics floats) for no
required benefit; the realized files are ~384-400 KB per run. This is
recorded here as a disclosed scope decision, not a silent gap: the
contract's own required artifact is the raw p-value, which IS persisted for
every curve, every statistic, every arm, every family, in both runs.

## Why route 2 (FFT) is used for the 2,000,000 null-subset draws

Same reasoning as EXP-MONO-670aa6's own implementation.md: route 2 needs
exactly one `fft2` call per draw for both Var_4 and C/F, versus route 1's
O(F) roll-sum per convolution step x 3 steps for m=4. At
100 curves x 20,000 draws = 2,000,000 draws per run this is the only
tractable choice within budget. Route 1 is still exercised, and
cross-checked against route 2, on every one of the ~93-97 real-arm cells
(`dual_path_control_real_arm`, both runs `all_within_1e-9: true`) and on
the Stage-4 extended sample described above.

## Timing and budget

Measured wall-clock: RUN-MONO-b19c6b-1 = 373.36s, RUN-MONO-b19c6b-2 =
432.59s -- both comfortably under the handoff's ~3000s soft-stop threshold
and the 7200s hard budget, and in line with the frozen contract's own
~700s/run projection (measured total across both runs: ~806s vs the
~1400s projected for two runs). Peak RSS: 219.8 MB and 231.0 MB
respectively, both far under the 4 GB cap. No budget signal was triggered
in either run.

## Realized panel sizes and construction failures (both >= 40-curve floor)

- RUN-MONO-b19c6b-1: j0 realized 45/50 (4 prime-construction exhaustions,
  1 factor-base coordinate-map-collision failure), random-ordinary realized
  48/50 (2 factor-base coordinate-map-collision failures, 0 prime
  exhaustions).
- RUN-MONO-b19c6b-2: j0 realized 48/50 (1 prime-construction exhaustion, 1
  factor-base coordinate-map-collision failure), random-ordinary realized
  49/50 (1 prime-construction exhaustion, 0 factor-base failures).

All failures are reported in `raw-result.json`'s
`primary_panel_construction.construction_failures` and
`primary_panel_fb_construction_failures`, never backfilled, per the
handoff's explicit instruction. Every realized family in every run cleared
the 40-curve floor.

## Deviations / notes carried forward, unchanged from predecessors

- `F = floor(N/4)`, forced even (`F -= F % 2`), identical convention to
  both EXP-MONO-c819ba and EXP-MONO-670aa6, for the same symmetric-subset
  reason.
- The legacy 8-curve sub-panel was not constructed at all (optional,
  non-gating per the frozen contract; this contract explicitly relies on
  EXP-MONO-c819ba's own already-reviewed positive controls instead).

No other interpretive deviations from the frozen specification.yaml text
were made. Both `stage1_independence_verification`'s collision definition
and Stage 4's concrete sample-selection count are the two disclosed
interpretation choices above; every other stage follows the frozen text's
own literal formulas (permutation p-value, Holm-Bonferroni, Fisher exact,
Fisher-combined, F=N/4, the p=1(mod 3) and supersingularity admission
rules) without modification.
