# Implementation notes: EXP-MONO-670aa6

Pure-Python 3.13 + numpy 2.4.0, no CAS/solver, no network. Source under
`experiments/EXP-MONO-670aa6/implementation/`:

- `seed.py` -- SHA-256 seed derivation and rejection-sampled `Drawer`, per
  `inputs.seed_derivation_rule` (domain, label, field_bits_or_p,
  curve_ordinal, m, draw_index, counter). Labels: `prime`, `curve-a`,
  `curve-b`, `null-subset`, `null-object-pick`, `coset-pick` -- no others.
- `fields.py` -- F_p arithmetic and EC group law (unchanged from
  EXP-MONO-c819ba's own `fields.py`).
- `curve.py` -- prime construction (`construct_prime(domain, b, k)`), curve
  stream (`curve_stream(domain, p, k, ...)`), point enumeration, exact group
  structure Z/n1 x Z/n2 (elimination-of-prime-power point orders), coordinate
  map, factor-base construction. Threads `curve_ordinal` through every seed
  call per this contract's own (not EXP-MONO-c819ba's) seed rule.
- `groupstate.py` -- `CurveState`, unchanged logic from EXP-MONO-c819ba.
- `conv.py` -- two independent routes to the exact-integer m-fold circular
  autoconvolution N_m of a factor-base indicator over Z/n1 x Z/n2:
  - Route 1, `convolution_tower`/`convolve_step`: direct O(F) numpy
    roll-sum per convolution step (the literal EXP-MONO-c819ba algorithm).
  - Route 2, `fft_exact_Nm`/`cell_stats_fft`/`stat_bundle_from_coords`:
    `N_m = round(Re(ifft2(fft2(indicator)^m)))`, the SAME quantity via the
    convolution theorem. One `fft2` call yields the spectrum `Shat` from
    which Var_m (any m) and `C = max_{chi!=1}|Shat|` are both derived
    cheaply.
  Both routes compute the identical mathematical object; route 2 exists
  purely for tractability (see "Why route 2" below), not as a different
  definition. `dual_path_control` is satisfied by cross-checking route 1
  against route 2 on every one of the 100 primary-panel REAL-arm cells in
  both runs (`dual_path_control_real_arm` / `dual_path_control_all_within_1e-9`
  in `raw-result.json`; both runs report `true`, all relative residuals
  < 1e-9, most < 1e-12).
- `controls.py` -- `draw_symmetric_subset` (labels `null-subset` and
  `null-object-pick`), `subgroup_control`, `coset_union_control` (excludes
  order-2 cosets of `G/H4` FROM THE START, per CORR-20260830-2b6706 -- this
  is new code, not a patch, so there is no reason to reintroduce the known
  EXP-MONO-c819ba bug).
- `panel_primary.py` -- builds the >=100-curve primary panel (50 j0, 50
  random-ordinary), curve_ordinal 0..49 independently per family,
  `field_bits[k mod 5]` round-robin.
- `panel_legacy.py` -- builds the 8-curve legacy sub-panel (RO1-4, CM1-2,
  J0, J1728), curve_ordinal fixed at the per-role constant 0, reproducing
  EXP-MONO-c819ba's own single-curve-per-role pattern under this contract's
  domain.
- `stats.py` -- `permutation_pvalue` (the frozen `(1+count)/(n+1)` formula),
  `holm_bonferroni` (standard step-down procedure), `fisher_exact_2x2`
  (exact hypergeometric summation, no scipy dependency).
- `run_experiment.py` -- orchestrates Stage 0-4 in the frozen order, with
  the Stage-2 hard stop enforced structurally: Stage-3 real-arm code is
  never reached, called, or evaluated until after `stage2_gate_pass` (both
  families) is computed and checked `True`.

## Why route 2 (FFT) is used for the 20,100 null/null-object draws

The contract's own cost note counts "100 curves x 1 F x 1 m x 201 draws =
20,100 cell computations." Route 1's O(F) roll-sum per convolution step
means each of those draws costs O(F) numpy operations just for m=2, and
three such steps for m=4 (F up to ~500 at the largest field_bits=11 curves)
-- workable per curve, but 100 curves x 201 draws x O(1500) roll calls is
tens of millions of numpy calls, which was empirically far slower than the
budget allows. Route 2 needs exactly ONE `fft2` call per draw (both Var_4
and C/F derive from the same `Shat`), making the full 20,100-draw primary
panel plus the 8-curve legacy panel's own ~6,400 draws complete in
~7 seconds wall-clock total per run (`checkpoints` in `raw-result.json`),
comfortably inside the 7200s budget. Route 2's exactness (not merely an
approximation) is confirmed empirically: `route2_max_imag_residual` and
`route2_max_round_residual` are recorded for every draw and are of order
1e-9 or smaller at this toy scale (N <= ~2050, well inside double
precision's exact-integer range for the m<=4 convolution values involved),
and route 1/route 2 agree to <1e-9 relative on every real-arm cell where
both were run (see above).

## Interpretation notes / deviations from a naive literal reading

1. **F = N/4, forced even.** The frozen `primary_f_note` names `F=N/4`
   without specifying integer rounding. This implementation uses
   `F = floor(N/4)`, forced to the nearest even value below it
   (`F -= F % 2`), so that both the real factor base (a prefix of the
   inherently ±-paired `fb_full` list) and every random symmetric-subset
   draw stay EXACTLY symmetric by construction. This is the identical
   convention EXP-MONO-c819ba used for its own F-ladder rungs
   (`ladder_fb`), reused here for continuity of method, not because the
   frozen text mandates it verbatim.
2. **No supersingular-curve rejection in the primary panel.** The frozen
   `curve_construction` text names exactly two rejection rules: singular
   discriminant, and B=0 (j0 family) / A=0-or-B=0 (random-ordinary family).
   It does NOT reject supersingular curves. An early implementation draft
   carried over EXP-MONO-c819ba's `accept_first_ordinary` helper's
   `N % p == 1` supersingular reject, and this was found DURING
   IMPLEMENTATION to eliminate roughly half of all j0 curve_ordinal slots:
   for any prime p = 2 (mod 3), EVERY j=0 curve (A=0, any B) over F_p is
   supersingular with N=p+1 identically, so the "accept first non-singular
   candidate" loop exhausts all 20,000 t-values whenever the ordinal's own
   prime happens to be 2 mod 3, a pure function of arithmetic, not of the
   seed stream. This filter is not in the frozen text, so it was removed;
   the realized panel legitimately contains some supersingular j=0 curves
   at primes p=2 (mod 3). This is disclosed as an interpretation decision,
   not a silent deviation: with the filter in place the panel would not
   have reached the 40-curve floor.
3. **The null-object gate's Holm/Bonferroni families (i)/(ii) are Var-only,
   per the literal `multiplicity_correction` text**, which names
   "(i) j0-family null-object p-values (Var, m=4), (ii) random-ordinary-family
   null-object p-values (Var, m=4)" without C/F. This is in slight tension
   with `metrics.primary` P4's looser phrase "identical statistics ...
   applied to the null-object arm," which could be read as including C/F.
   Rather than resolve this by silently widening or narrowing a declared
   family (the frozen `invalidation_rules` explicitly forbid any
   post-hoc redefinition of the declared families), this implementation:
   (a) follows the more specific, itemized `multiplicity_correction` text
   literally for the two families that gate the hard stop (Var only), and
   (b) additionally computes and Holm-corrects the C/F null-object
   p-values as an **informational, non-gating** diagnostic, reported
   alongside but never substituted for the frozen gate
   (`cf_family_holm_informational_not_gating` in `raw-result.json`). In
   both runs this informational check also shows zero significant curves
   in both families, so the tension is moot for these two runs' outcome,
   but the distinction is recorded per "record, never discard."
4. **`master_seed` enters only the null/null-object/coset-pick draws, not
   panel construction.** The frozen `seed_derivation_rule` never mentions
   `master_seed` as a seed-string component at all -- only `domain`,
   `label`, `field_bits_or_p`, `curve_ordinal`, `m`, `draw_index`, `counter`.
   Following EXP-MONO-c819ba's own established, unchallenged pattern
   (`sampling_domain = f"{PANEL_DOMAIN}/run-{master_seed}"`), this
   implementation uses the FIXED domain `EXP-MONO-670aa6/v1` for prime and
   curve construction (so both runs share the identical 100-curve primary
   panel and 8-curve legacy panel -- confirmed: the same single j0
   construction failure, curve_ordinal 17, appears identically in both
   runs' `raw-result.json`), and a run-suffixed `sampling_domain` /
   `legacy_sampling_domain` (`.../run-<master_seed>`) for the `null-subset`,
   `null-object-pick`, and `coset-pick` draws, so the two runs' null/
   null-object/coset draws are independent while testing the identical
   panel. This is the natural, only-available reading given the frozen
   text is silent on the mechanism and `replication.interpretation`
   explicitly requires "Two runs at different master seeds" to differ.
5. **Legacy sub-panel null draws use n=200, not EXP-MONO-c819ba's n=30.**
   `inputs.null_draws_per_cell: 200` is declared once, without scope
   restriction to the primary panel; the legacy panel's own graded
   controls (L2/L3 ratios) are computed against 200-draw null populations
   here, not 30. This does not change the legacy panel's status as
   "never corrected or escalation-eligible" secondary continuity evidence
   (its L1-L4 fixed-band labels are exactly the kind of instrument
   KN-TECH-7745e6 documents as uncalibrated at small n, and are reported
   as raw labels with that caveat, never as corrected p-values).

## Construction failure encountered (both runs, identical)

`curve_ordinal=17` in the j0 family failed AFTER prime/curve construction,
during `CurveState` group-structure computation: `"coordinate map collision
at k1=4,k2=0: point already mapped (G1,G2 not independent generators)"`.
This is `build_coordinate_map`'s own structural-integrity check (unchanged
from EXP-MONO-c819ba) catching a case where the generic
max-order-point/outside-<G1>-search heuristic in `group_structure` picked a
G2 candidate that was not, in fact, independent of G1 for this particular
curve's (likely non-cyclic, small n1) group structure. Per
`factor_base_construction`/`invalidation_rules`, this is reported and the
ordinal is excluded, never patched or backfilled: realized j0 count is 49
of 50 declared, in both runs, well above the 40-curve floor.

## Budget

Both runs completed in ~7.06s and ~7.08s wall-clock respectively (peak RSS
~76-77 MB), far inside the 7200s/2GB budget; no soft-stop threshold was
approached.

## Certificate discipline

`certificate.kind: none` in both run manifests: this is a pure measurement
run (permutation p-values, Holm-Bonferroni correction, Fisher exact test),
not a discrete-log solve or relation claim, per
`docs/claims-and-verification.md`.
