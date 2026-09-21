# V2.1 Confirmatory Analysis

## Status

`NEGATIVE RESULT`, `TOY-EVIDENCE`, `MODEL-BOUND`

This is a scoped negative for the three frozen coordinate-family
constructions, certificate dictionary, and one-feature public-coordinate
predictor class. It is not a negative result for elliptic-curve index
calculus, recursive addition-law circuits, multi-stage predictors, or batch
point decomposition.

## Hypothesis

At least one of `coset_prefix_chain`, `quartic_composition_chain`, or
`reciprocal_denominator_chain` will show reproducible scalar-space D4
concentration or certificate structure on all nine fresh curves and a
public-coordinate predictor that transfers to every held-out 14-bit curve.

The construction is scalar-free. Diagnostic scalar labels are used only to
measure the hidden additive structure and are not attack advice.

## Frozen Profile

- source commit: `8bf9505accbcd86d410ec41f9b4b63bf941995e5`;
- source tree: `95a484a5850c1db04001fafcef5d2d0ade161a9c`;
- curve sizes: 10, 12, and 14 bits;
- post-freeze curve seeds: `885755949`, `379235646`, `1122339152`;
- curves: nine generated prime-order ordinary curves;
- null draws: 2,047 per curve;
- predictor permutations: 127;
- candidate-matched negative sentinels: eight per family;
- factor-base sizes: five on 10/12-bit curves and seven on 14-bit curves.

The producer launched exactly once from a clean worktree. The independent
verifier launched exactly once against the resulting raw artifact.

## Controls

All frozen confirmatory controls pass:

- true and signed arithmetic-progression controls;
- exact 0.9%, 1%, 2%, and 5% eligibility boundaries;
- pooled-eligible but per-curve-ineligible boundary;
- balanced 50/50 predictor null;
- just-above-1% planted positive;
- public-coordinate `chi(x-1)=+` positive predictor;
- all 24 heavy-tailed candidate-matched negative sentinels.

The worst negative-sentinel retained enrichment is `0.002644`; the minimum
negative reference-tail rank is `0.03125`. The
`predictor_calibration_pass` field is false by construction in the
confirmatory profile because it denotes the registered development-only
calibration gate. The confirmatory control gate is `controls.all_pass`, which
is true.

## Candidate Result

| Family | Minimum D4 rank | Minimum certificate rank | Predictor rank | Held-out enrichment | Held-out recall |
|---|---:|---:|---:|---:|---:|
| coset prefix | `0.014160` | `0.003418` Fourier | `0.445313` | `0.000296` | `0.135703` |
| quartic composition | `0.033203` | `0.140137` Fourier | `1.000000` | `-0.001478` | `0.112360` |
| reciprocal denominator | `0.069336` | `0.176758` Fourier | `1.000000` | `-0.000232` | `0.127186` |

The nearest isolated value, the coset-family Fourier rank `0.003418`, does
not pass the frozen 81-test Holm threshold `0.000617` and does not repeat on
every curve. Across the complete packet:

- D4-energy Holm rejections: zero of 27;
- certificate Holm rejections: zero of 81;
- candidate predictors passing every held-out curve: zero of three;
- producer screening signals: zero;
- independently verified positive signals: zero.

No family passes `energy_all_nine`, `certificate_each_curve`, or
`predictor_pass`. The algorithm-promotion gate is false.

## Independent Verification

The verifier reports `valid=true` and independently reconstructs:

- nine curves;
- 18,423 canonical null sets;
- 27 candidate cells;
- 186,153 target rows;
- direct ordered four-loop D4 multiplicities;
- exact reference-tail ranks, Holm decisions, predictors, controls, family
  gates, source identities, seed lock, and telemetry.

All 23 check categories pass. All 19 registered semantic and integrity
mutations are rejected, including changes to the eligibility threshold,
eligible and selected bucket counts, per-curve coverage, and one negative
replicate.

## Accounting

The producer records 608,335 curve-order Legendre tests, 609,444 D2 counter
updates, 7,577,248 D4 convolution updates, 18,468 FFT transforms, 104,547
null canonicalizations, 46,594 predictor feature-candidate evaluations, and
3,586 model fits.

Producer wall time and peak RSS are 1,144.23 seconds and 317,390,848 bytes.
Independent verification wall time and peak RSS are 6,762.93 seconds and
504,856,576 bytes. The preserved packet occupies 8,722,774 bytes.
Verification overhead is evidence cost, not attack cost.

## Strongest Valid Conclusion

No promotable D4 concentration, registered additive certificate, or
single-feature public-coordinate predictor was found for the three frozen
families under the V2.1 confirmatory model.

This does not rule out:

- intersections or learned compositions of multiple public predicates;
- recursive S3/S4 addition-law joins that avoid materializing D4 support;
- batch decomposition amortized across many targets;
- factor bases designed for additive-combinatorial expansion or failure of
  expansion;
- fixed-curve preprocessing with explicit storage and online-cost tradeoffs.

## Next Concrete Action

Freeze a successor contract for a batch, multi-stage public-coordinate join.
Its positive hypothesis should be that two independently cheap coordinate
filters reduce an exact recursive D4 witness search below the direct
square-root frontier after charging build cost, storage, memory traffic,
failed queries, and witness recovery. Its negative track should prove or
measure expansion of the retained coordinate sets under EC addition.
