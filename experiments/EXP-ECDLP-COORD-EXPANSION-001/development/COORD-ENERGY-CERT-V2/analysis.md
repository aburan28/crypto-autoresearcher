# Coordinate Energy Certificate V2 Analysis

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`, `CONTROL-INVALID`.

The confirmatory computation and its independent arithmetic replay are valid,
but the mandatory predictor-negative control failed its preregistered
enrichment bound. This packet therefore cannot support either a positive
signal or a scoped negative conclusion about the three candidate factor-base
families.

The failed control is informative about the protocol. The frozen one-bucket
learner selected a bucket represented by only six of 14,854 training targets
and three of 48,227 held-out targets. Two of those three held-out targets had
positive permuted labels, producing `0.333982` retained enrichment despite
`0.000083` recall, `0.000062` pooled coverage, reference-tail rank `0.335938`,
and a predictor gate that otherwise failed. A raw enrichment bound is
unstable for such vanishingly rare buckets.

## Frozen Run

- source commit:
  `17f004d97c883444319dd0b11cc97e209ce917f1`;
- source tree:
  `51ee6fa6405437401e42f599685094561f4bf538`;
- source worktree was clean at launch;
- curve sizes: 10, 12, and 14 bits;
- three generated prime-order curves at each size, with seeds 101, 211, and
  307;
- subgroup orders: 941 through 16,607;
- factor-base sizes: five on the 10- and 12-bit curves and seven on the
  14-bit curves;
- candidate families: `coset_prefix_chain`,
  `quartic_composition_chain`, and `reciprocal_denominator_chain`;
- 2,047 canonical-random-fiber null sets per curve;
- 27 candidate cells and 18,423 null sets;
- 127 deterministic label permutations per fitted predictor;
- producer wall time and peak RSS: 80.905 seconds and 328,302,592 bytes;
- independent verifier wall time and peak RSS: 75.51 seconds and
  374,456,320 bytes.

The producer charged 63,081 subgroup-census additions, 107 curve-generation
attempts, 104,594 null-sampling attempts, 609,444 D2 pair updates, 7,577,470
D4 convolution updates, 18,468 FFTs, 189,243 target rows, and 640 predictor
fits. This boundary excludes the external wrapper, serialization, manifest
construction, and independent verification.

## Arithmetic Results

No candidate cell passed a primary energy or certificate multiple-testing
gate:

| Quantity | Result |
|---|---:|
| Holm-rejected exact E4 cells | 0 / 27 |
| Holm-rejected certificate tests | 0 / 81 |
| producer screening signals | 0 / 3 families |
| independently verified provisional signals | 0 / 3 families |
| independently verified positive signals | 0 / 3 families |

The smallest unadjusted exact E4 reference-tail rank was `0.034180` for the
12-bit seed-211 `coset_prefix_chain` cell. It did not survive the
preregistered 27-test Holm family. Every popular-difference and Freiman
reference-tail rank was one.

The frozen family predictors also failed their individual gates:

| Family | Selected bucket | Train coverage | Held-out coverage | Retained enrichment | Recall | Rank |
|---|---|---:|---:|---:|---:|---:|
| coset prefix | denominator `-0+` | 0.027% | 0.004% | -0.0132 | 0 | 1 |
| quartic composition | denominator `--0` | 0.027% | 0.008% | -0.0132 | 0 | 1 |
| reciprocal denominator | `chi(x-a)=0` | 0.054% | 0.008% | -0.0132 | 0 | 1 |

These are descriptive observations only because the mandatory control suite
did not pass.

## Controls

The literal AP, signed-AP, and predictor-positive controls passed. The
predictor-negative control did not:

| Control | Result |
|---|---|
| literal full AP | pass |
| signed AP | pass |
| public-coordinate predictor positive | pass |
| within-curve permuted-label predictor negative | fail |

The negative predictor selected `y_bin_8=O`, meaning the infinity bucket.
Its learned predictor itself did not pass the Bonferroni, coverage, recall,
or per-curve gates. The control nevertheless failed because its pooled
held-out retained enrichment was `0.333982`, above the frozen maximum of
`0.20`. With only three predictions, this quantity is governed by individual
labels rather than a stable out-of-sample rate.

This failure does not show candidate predictability. It shows that the
learner's candidate-bucket eligibility rule needs a minimum training support
constraint before enrichment is meaningful.

## Independent Verification

The independent verifier reconstructed all nine curves, 18,423 null sets, 27
candidate cells, and 189,243 target rows. It recomputed D4 by a direct ordered
four-loop method rather than the producer's D2-convolution route, replayed the
public EC difference and Freiman witnesses, reconstructed predictors and
controls, checked exact ranks and Holm order, and verified the scalar-free
candidate-construction boundary.

All 14 registered mutations were rejected, including candidate points,
configuration, control payloads, difference witnesses, Freiman bases, Holm
order, null values, predictor buckets, scalar boundaries, source hashes,
summary telemetry, and both positive and negative telemetry changes.

Independent verification establishes arithmetic and packet integrity. It
does not repair the failed mandatory control.

## Strongest Valid Conclusion

> On nine generated toy prime-order curves of 10-14 bits, the frozen
> computation produced no multiplicity-adjusted energy, certificate, or
> predictor screening signal for three coordinate families. However, the
> mandatory permuted-label predictor control violated its enrichment bound
> because the learner could select a vanishingly rare bucket. The run is
> control-invalid and cannot be used as a negative result for those families.

This is not an ECDLP improvement, an exponent claim, or evidence about
deployment-sized curves.

## Next Concrete Action

Freeze a successor before looking at fresh confirmatory curves:

1. require every eligible bucket to cover at least 1% of pooled training rows
   and at least 1% on every training curve;
2. calibrate the repaired positive and negative controls on development-only
   seeds disjoint from the next confirmatory seeds;
3. retain the existing held-out per-curve coverage, recall, enrichment, and
   permutation gates;
4. use fresh confirmatory curve seeds and never reinterpret this packet as
   candidate evidence;
5. preserve exact energy and witness checks unchanged so the protocol repair
   is isolated to predictor eligibility and controls.
