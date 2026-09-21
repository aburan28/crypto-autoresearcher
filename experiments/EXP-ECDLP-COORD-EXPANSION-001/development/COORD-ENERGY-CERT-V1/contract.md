# Experiment Contract: Coordinate Energy Certificate V1

## Post-Run Audit Amendment

This file preserves the preregistered V1 gate, but the independent audit
narrows its interpretation:

- the two canonicalized null generators sample the same random-fiber law on
  these cofactor-one odd-prime-order curves, so they are two replicate batches
  rather than distinct null models;
- with 31 draws per batch, nearest-rank p99 is the sample maximum and has
  minimum one-sided permutation p-value `1/32`;
- the scalar fixture is a sign-canonicalized structured set, not a literal
  scalar arithmetic progression after canonicalization;
- predictor rows condition on positive D4 support, so the reported model is a
  post-support multiplicity stratifier, not target-wide attack advice;
- failure of the V1 conjunctive gate rules out only the registered metrics and
  one-feature predictor dictionary.

These corrections are interpretation amendments, not changes to the executed
producer or raw result.

## Hypothesis

If an audited coordinate factor base is extreme relative to matched
random-scalar and random-x controls, then the anomaly has a compact additive
certificate: Fourier concentration, popular differences, affine-progression
coverage, or a coordinate-only predictor of high-multiplicity four-sums.

This is a mechanism/barrier experiment. It is not an ECDLP relation compiler.

## Null Hypothesis

Coordinate families fail the registered energy, spectrum, and one-feature
predictor gates, or any anomaly is visible only after using diagnostic
discrete-log labels. In either case V1 has not found a coordinate-computable
attack primitive in its tested dictionary.

## Parameters

- the three generated ordinary prime-order curves in
  `TYPED-FIVE-EC-V1`, with `q in {953,3919,15583}`;
- full audited factor bases `B in {5,8,10}`;
- candidates: x-interval, source-PRF-x, and rational-union;
- fixture controls: random-x and scalar progression;
- 31 deterministic random-scalar-fiber null draws per curve, reduced to the
  same canonical y representative as the candidates;
- 31 deterministic random-x null draws per curve with the same canonical y
  policy; on these curves this is a second batch from the same random-fiber
  law, not an independent null model;
- ordered D2 and D4 representation semantics;
- first two curve sizes for coordinate-predictor training;
- largest curve held out before model fitting.

## Diagnostic Scalar Boundary

The generated generator permits a complete toy point-to-scalar census. Scalar
labels may be used only to compute exact group Fourier and additive diagnostics.
They are forbidden from:

- candidate construction;
- coordinate features;
- predictor fitting inputs;
- any claimed advice or online algorithm.

Every scalar-derived field is labeled `DIAGNOSTIC_ONLY_NOT_ATTACK_ADVICE`.

## Metrics

- exact ordered D2/D4 support, representation histograms, maximum
  multiplicity, and collision energy;
- normalized D2 energy and spectral L4 mass;
- maximum nontrivial normalized Fourier coefficient in `Z/qZ`;
- top-`B` nonzero popular-difference concentration;
- best length-`B` affine-progression coverage in the scalar diagnostic;
- nearest-rank 99th-percentile comparisons against both null families
  (`n=31`, so this threshold is the observed sample maximum, not a resolved
  population-tail estimate);
- coordinate-only held-out precision, recall, multiplicity enrichment, and
  retained oracle enrichment;
- full census/null-generation work, seeds, hashes, and wall/RSS telemetry.

## Coordinate Predictor

For every D4 output point, features may use only:

- normalized x/y bins;
- Legendre characters of public coordinate shifts;
- small public coordinate residues;
- an explicit infinity label.

The model is one auditable categorical feature plus selected buckets. It is
fit on the two smaller curves and frozen before evaluation on `q=15583`.
Rows are restricted to outputs with positive D4 multiplicity, so this is a
post-support stratification diagnostic. V1 does not charge or provide a way to
discover that support for an arbitrary target.

## Controls

- the sign-canonicalized scalar fixture must show an energy/Fourier/partial-AP
  certificate; it is not a positive control for a literal full AP or for the
  coordinate predictor;
- random-scalar and random-x nearest-rank percentiles are computed from all
  31 draws; the p99 threshold is therefore each null sample's maximum;
- the random-x fixture must not be promoted merely for matching its own null;
- all candidate points must replay to diagnostic scalars and back;
- D2/D4 representation totals must equal `B^2` and `B^4`;
- Parseval's fourth-moment identity is checked through exact D2 energy;
- all predictors must prove that no scalar label entered a feature.

## Success Criterion

A coordinate family is a positive signal only if, at all three sizes:

1. normalized D2 or D4 energy exceeds the corresponding empirical 99th
   percentile of both nulls;
2. at least one compact certificate metric exceeds both corresponding null
   percentiles; and
3. the held-out coordinate predictor retains at least 80% of oracle
   multiplicity enrichment with nonzero precision and recall.

The scalar progression is a positive control, not an eligible candidate.

## Falsification Criterion

If no candidate passes, preserve a scoped negative: these audited families
fail the V1 metric and one-feature predictor dictionary at these toy sizes.
This does not exclude other compact certificates, prove expansion for
arbitrary coordinate predicates, or extrapolate to larger fields.

## Reproduction Command

```bash
python3 src/coord_energy_certificate.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --null-draws 31
```
