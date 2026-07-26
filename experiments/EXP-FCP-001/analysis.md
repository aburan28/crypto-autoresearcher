# EXP-FCP-001 Fixed-curve preprocessing pilot

## Objective
Evaluate whether fixed-curve, fixed-factor-base preprocessing changes the practical cost of small S_3 decomposition measurements on toy prime fields.

## Protocol
- Generate deterministic toy ECDLP instances from `seed` and `bits` using `harness.toycurve.generate_instance`.
- Reuse one curve per `(bits, seed)`.
- Precompute a factor base once.
- Run S_3 decomposition for multiple independent targets:
  - one branch reuses the precomputed factor base (`fixed`),
  - one branch rebuilds factor base per target (`naive`).
- Record immutable run packages through `harness.fixed_curve_preprocessing`.

## Observed outcome
- Command set:
  - `python3 -m harness.fixed_curve_preprocessing --bits 8,10,12 --seeds 1,2 --factor-base 14 --targets-per-curve 3`
  - `python3 -m harness.fixed_curve_preprocessing --bits 14,16 --seeds 1,2 --factor-base 14 --targets-per-curve 3`
- Run count: 72 runs (`EXP-FCP-001`), all completed with immutable manifests.
- Fixed precompute cost is tiny in this range:
  - median precompute per curve: 0.00014 s
  - min/max observed: 0.00010 s / 0.00019 s
- Per-target Groebner wall-time (mean, s):
  - bits 8: fixed 0.105801 vs naive 0.045763
  - bits 10: fixed 0.050504 vs naive 0.093672
  - bits 12: fixed 0.050618 vs naive 0.040923
  - bits 14: fixed 0.060108 vs naive 0.051790
  - bits 16: fixed 0.079249 vs naive 0.057301
- Decomposition findings:
  - bits 8: fixed 4/6, naive 4/6
  - bits 10: fixed 3/6, naive 3/6
  - bits 12/14/16: 0/3 or 0/6 for both modes
- The data do not show a robust constant-factor win for fixed preprocessing.
- For several easy/medium targets, fixed mode is within noise of naive;
  for the harder outliers, fixed can be worse, and the occasional "win" appears
  target-instance specific.

## Interpretation
This is a scoped toy observation. It indicates that naive factor-base construction is not the dominant cost in these small S_3 tests, and fixed-curve preprocessing does not yet beat per-target setup at this scale.

## Open question
A stronger follow-up is to add target-side batching or larger field sizes where Groebner elimination variance is measurable and then compare total online cost `precompute + per_target` more aggressively.
