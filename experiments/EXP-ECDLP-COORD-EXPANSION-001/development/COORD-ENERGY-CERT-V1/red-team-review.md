# Red-Team Review: Coordinate Energy Certificate V1

## Handoff: Gate-specific coordinate-energy negative

### Claim or task

Audit the `d80c04a7` packet and determine whether its scoped negative
conclusion is supported.

### Status

`NEGATIVE RESULT`, `TOY-EVIDENCE`, `MODEL-BOUND`, `RED-TEAM CORRECTED`.

The arithmetic replay is sound and the null-sign mismatch is resolved. The
valid negative is limited to the V1 metric and one-feature predictor
dictionary.

### Assumptions

- audited commit:
  `d80c04a78a5cb5172cc75da353afd136168c6e2e`;
- the upstream typed factor bases are accepted as frozen inputs;
- one curve and one factor-base draw are used at each toy size;
- scalar censuses are diagnostic-only generated-toy data.

### Evidence so far

- producer, raw-result, verifier, and verification hashes are mutually
  consistent;
- the verifier reruns successfully and all six focused tests pass;
- the largest curve was independently replayed at `q=15583`, `B=10`:

| family | D2 support | D2 energy | D4 support | D4 energy | max Fourier |
|---|---:|---:|---:|---:|---:|
| x-interval | 55 | 190 | 711 | 177046 | 0.881487678877 |
| signed scalar control | 34 | 382 | 75 | 2254902 | 0.999996890728 |

For x-interval, `E2=190=2B^2-B`, the ordered-pair collision floor when only
permutations collide. The largest row therefore has no non-permutation D2
collision anomaly.

The null fix is correct: both generators select distinct valid x-fibers and
apply `y=min(y,p-y)`. On these cofactor-one odd-prime-order curves, the
random-scalar-fiber and random-x constructions induce the same law. They are
replicate batches, not two distinct null models.

### Findings

1. The executed gate cannot exclude every compact coordinate certificate.
   It covers Fourier maximum, aggregate popular-difference concentration, AP
   coverage, and one categorical coordinate feature. GAP/Freiman fits,
   difference graphs, chain values, denominator strata, and certificate
   compression length remain untested.
2. Predictor rows condition on `r4(P)>0`. The reported model is a
   post-support multiplicity stratifier, not target-wide advice; support
   construction is neither supplied nor charged.
3. With 31 draws, nearest-rank p99 is the sample maximum and the minimum
   one-batch permutation p-value is `1/32`. Pooling the same-law batches gives
   only `1/63`.
4. The scalar fixture is not a full AP after sign canonicalization. On the
   largest curve, its best length-10 AP covers `5/10`. It also does not
   positive-control the coordinate predictor.
5. Features are coordinate functions, but the toy implementation obtains
   output points by scalar-census indexing. This is semantically reproducible
   by point addition, yet the literal implementation is not scalar-free.
6. Fourier argmax and top difference/count witnesses are not stored. V1
   retains metric scores, not complete replayable compact certificates.
7. Direct four-loop D4 replay is independently structured. Null, percentile,
   and predictor paths are near-duplicate implementations. The 14 registered
   mutations do not validate positive telemetry changes; timing and RSS
   inside the payload remain unreceipted self-report.
8. The normalizations are nonstandard enough to require formulas:
   `E2/B^2`, spectral L4 `E2/B^4`, and `E4/B^4`, where E4 is an ordered
   eight-tuple collision count.

### Strongest valid conclusion

> On three frozen toy curves with `q in {953,3919,15583}` and
> `B in {5,8,10}`, none of the three audited families exceeded both recorded
> canonical-fiber null sample maxima at every size, and none of the
> pre-specified one-feature stratifiers retained 80% oracle enrichment on the
> single largest held-out curve. This rules out only the V1 metric and feature
> dictionary.

### Failure modes

- promoting a failed conjunctive gate into absence of other certificates;
- treating replicate null batches as distinct models;
- applying a support-conditioned predictor without charging support
  generation;
- treating the signed fixture as a full-AP or predictor control;
- treating equality replay or mutation count as independent mathematical
  validation;
- extrapolating from one curve per size and `B<=10`.

### Next concrete action

Run `COORD-ENERGY-CERT-V2` with pooled finite-sample rank tests, multiple
independent curves and factor-base draws, a literal AP and a predictor-positive
control, all-target evaluation or an explicitly charged streaming model,
replayable certificate witnesses, and multiple-testing correction.

### Artifact paths

- `development/COORD-ENERGY-CERT-V1/contract.md`
- `development/COORD-ENERGY-CERT-V1/raw-result.json`
- `src/coord_energy_certificate.py`
- `src/verify_coord_energy_certificate.py`
- `development/COORD-ENERGY-CERT-V1/verification.json`
