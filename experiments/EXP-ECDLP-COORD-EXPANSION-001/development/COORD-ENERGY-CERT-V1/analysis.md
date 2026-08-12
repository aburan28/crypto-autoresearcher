# Coordinate Energy Certificate V1 Analysis

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`, scoped `NEGATIVE RESULT`.

The audited x-interval, source-PRF-x, and rational-union factor bases do not
exceed both registered canonical-fiber null sample maxima at every toy size.
With 31 draws per batch, the nearest-rank empirical p99 is the sample maximum,
not a resolved population-tail estimate. The two batches have the same null
law on these curves. Their held-out one-feature, support-conditioned
multiplicity stratifiers retain essentially none of the D4 multiplicity
enrichment.

The sign-canonicalized scalar control is extreme at every size, so the energy
and spectral diagnostics detect this structured signed set. It is not a
literal full-AP or coordinate-predictor positive control.

## Exact Run

- producer source commit:
  `d80c04a78a5cb5172cc75da353afd136168c6e2e`;
- producer source tree:
  `d6b2f8229714021d9e448bdc3b72cb5a3ed6efc9`;
- curves: `q in {953,3919,15583}`;
- factor-base sizes: `B in {5,8,10}`;
- eligible families: x-interval, source-PRF-x, rational-union;
- fixture controls: random-x and scalar progression;
- nulls: 31 random-scalar plus 31 random-x draws per curve;
- 15 candidate/control rows and 186 null rows;
- producer payload wall time/RSS: 1.514 seconds / 34,209,792 bytes;
- producer wrapper wall time/RSS: 1.55 seconds / 34,226,176 bytes;
- independent verifier wrapper wall time/RSS: 1.80 seconds /
  36,143,104 bytes;
- all rows, seeds, scalar censuses, D2/D4 metrics, registered sample-maximum
  comparisons, predictors, and gates replayed;
- 14 registered mutations are rejected, but the telemetry mutation checks
  cover only invalid negative values; positive changes to self-reported
  telemetry are accepted;
- independent D4 reconstruction uses direct ordered four loops rather than the
  producer's D2-convolution path.

## Energy Results

Each cell below gives candidate normalized D4 energy followed by the
random-scalar/random-x nearest-rank empirical 99th percentiles. Because each
null sample contains 31 draws, these values are the corresponding sample
maxima.

| q | family | D2 energy | D4 energy | D4 p99 scalar | D4 p99 random-x |
|---:|---|---:|---:|---:|---:|
| 953 | x-interval | 1.80 | 12.6928 | 17.2048 | 17.6656 |
| 953 | source-PRF-x | 1.96 | 17.2048 | 17.2048 | 17.6656 |
| 953 | rational-union | 1.80 | 12.6672 | 17.2048 | 17.6656 |
| 3,919 | x-interval | 1.875 | 16.3223 | 21.0332 | 21.5078 |
| 3,919 | source-PRF-x | 1.875 | 17.1328 | 21.0332 | 21.5078 |
| 3,919 | rational-union | 1.875 | 16.2402 | 21.0332 | 21.5078 |
| 15,583 | x-interval | 1.90 | 17.7046 | 19.8162 | 18.7926 |
| 15,583 | source-PRF-x | 1.90 | 17.6782 | 19.8162 | 18.7926 |
| 15,583 | rational-union | 1.90 | 18.5910 | 19.8162 | 18.7926 |

D2 energy is highly quantized at these sparse sizes: collision-light ordered
pairs sit near the unavoidable diagonal/permutation floor. D4 energy is the
first metric with useful collision resolution, and every candidate remains
below both null thresholds.

Here `D2 normalized energy` means
`sum_g r_2(g)^2 / B^2`, spectral L4 mass means
`sum_g r_2(g)^2 / B^4`, and `D4 normalized energy` means
`sum_g r_4(g)^2 / B^4`. The last numerator counts ordered eight-tuples.
These conventions must not be compared to differently normalized additive
energy without conversion.

The candidate maximum nontrivial normalized Fourier coefficients range from
`0.8394` to `0.9816`, but none exceeds both matched p99 values. A maximum over
all toy frequencies is naturally high for sparse sets; it is evidence only
relative to the preregistered nulls, not an absolute certificate.

Popular-difference concentration and length-B affine-progression coverage
also produce zero candidate certificate cells.

Both null generators use the same `sign_canonical` y representative as every
audited fixture. Random-scalar controls sample fibers before canonicalization;
random-x controls sample x-coordinates before canonicalization. On these
cofactor-one odd-prime-order curves they induce the same canonical-fiber law,
so the 31+31 draws are replicate batches, not evidence against two distinct
null models. The minimum one-batch permutation p-value is `1/32`; pooling the
same-law batches gives `1/63`.

## Positive Control

The sign-canonicalized scalar fixture passes both-batch energy and certificate
gates at all three sizes:

| q | D2 energy | D4 energy | max Fourier | AP coverage |
|---:|---:|---:|---:|---:|
| 953 | 2.28 | 32.3856 | 0.999831 | 0.80 |
| 3,919 | 3.125 | 117.5156 | 0.999969 | 0.625 |
| 15,583 | 3.82 | 225.4902 | 0.999997 | 0.50 |

The AP fraction is below one because the registered control includes its
public sign/symmetry policy rather than a literal one-sided scalar interval.
At `q=15583`, its best length-10 AP covers only `5/10` points. Its energy,
spectrum, differences, and partial progression still separate from both
null batches, but it does not validate full-AP recovery or the coordinate
predictor.

## Post-Support Stratifier

The model may use only public x/y bins, Legendre characters, small coordinate
residues, and infinity. It trains on the two smaller curves and freezes before
the `q=15583` evaluation.

| family | selected feature | precision | recall | retained oracle enrichment |
|---|---|---:|---:|---:|
| x-interval | `chi_x_minus_1` | 0.2820 | 0.4575 | -0.0050 |
| source-PRF-x | `chi_x_minus_1` | 0.3229 | 0.5381 | 0.0262 |
| rational-union | `chi_x_minus_b` | 0.3018 | 0.4951 | -0.0196 |

The nonzero precision/recall mostly reflects broad selected buckets and the
label base rate. Predicted mean multiplicity is essentially the population
mean, so none retains the required 80% enrichment. These rows include only
outputs with positive D4 multiplicity. V1 therefore measures post-support
multiplicity stratification; it neither discovers nor charges construction of
the D4 support needed to apply the model.

## Scalar-Diagnostic Boundary

Complete scalar labels are available only because these are generated toy
groups. They are used to compute exact convolution, Fourier, differences, and
progression ground truth. Feature values are functions only of the output
point coordinates, but the toy implementation obtains those output points by
indexing a scalar census. No scalar value is exposed as a predictor feature,
attack advice, or online algorithm.

The result therefore says that the registered one-feature dictionary does not
stratify the observed positive-support multiplicities. It does not establish
target-wide coordinate advice or turn the scalar diagnostics into a usable
cryptanalytic primitive.

## Certificate Boundary

The stored Fourier maximum and popular-difference concentration are scores,
not replayable certificates: V1 omits the Fourier argmax and the top
difference/count witnesses. AP start and step are retained. Thus "certificate"
in the V1 protocol names a metric gate; it does not establish a compact
coordinate-computable witness or encoding-length bound.

## Strongest Valid Conclusion

> On three frozen toy curves with `q in {953,3919,15583}` and
> `B in {5,8,10}`, none of the three audited families exceeded both recorded
> canonical-fiber null sample maxima at every size, and none of the
> pre-specified one-feature stratifiers retained 80% oracle enrichment on the
> single largest held-out curve. This rules out only the V1 metric and feature
> dictionary.

This narrows the factor-base additive-geometry lead for these concrete
families and measurements. It does not prove that `L(x)=0` sets expand on
arbitrary curves, rule out other compact certificate dictionaries, rational
maps, or unions, or establish a structured-group lower bound.

## Next Concrete Action

Run `COORD-ENERGY-CERT-V2` as a theorem-oriented expansion campaign:

1. use multiple independent ordinary prime-order curves and factor-base draws
   at each size;
2. pool at least 99-999 matched canonical-fiber null draws, report ranks and
   finite-sample permutation p-values, and preregister multiple-testing
   correction;
3. add a true full AP, the signed fixture, a known coordinate-predictor
   positive control, and a label-permutation negative control;
4. evaluate predictors over all `q` targets or explicitly charge a streaming
   support-generation model;
5. retain Fourier argmax, top differences/counts, encoding lengths, and
   coordinate linkages as replayable witnesses;
6. test richer composed rational maps and isogenous/model-transformed sets;
7. in parallel, formulate a character-sum/incidence bound for the energy of
   `x(P)`-interval or rational-map preimages under elliptic addition.
