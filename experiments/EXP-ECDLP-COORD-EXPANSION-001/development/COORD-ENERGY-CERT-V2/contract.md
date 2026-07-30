# Experiment Contract: Coordinate Energy Certificate V2

## Candidate

Exploit low-degree coordinate-chain predicates to obtain reproducible
four-sum collision structure that has both a replayable additive certificate
and a target-wide coordinate-computable predictor.

This is a factor-base mechanism experiment. It does not implement relation
collection, matrix solving, target descent, or an ECDLP attack.

## Hypothesis

At least one registered coordinate-chain family has:

1. D4 additive energy above matched canonical-fiber nulls on independent
   curves;
2. a replayable Fourier, popular-difference, or Freiman-relation certificate;
3. a predictor using only public target coordinates that retains at least 80%
   of oracle multiplicity enrichment on held-out curves.

## Null Hypothesis

The registered coordinate-chain sets have null-like D4 energy after
family-wide multiple-testing correction, any scalar-space structure lacks a
replayable compact witness, or target coordinates do not predict
multiplicity over the full subgroup.

## Curve Family

- generated ordinary short-Weierstrass curves over prime fields;
- cofactor one and prime group order;
- `p mod 4 = 3`;
- bit sizes `10, 12, 14`;
- three frozen curve seeds per bit size: `17, 53, 89`;
- no rejection based on `p-1` smoothness, `j`, factor-base behavior, or
  candidate score;
- one independently seeded factor-base construction per candidate and curve;
- target factor-base size
  `B=max(5, round(q^(1/5)))`, with exact cardinality enforced.

All curves, seeds, selection attempts, `p-1` factors, and generator checks are
recorded.

## Registered Candidate Families

### Coset-prefix chain

Enumerate deterministic multiplicative-subgroup cosets in `F_p^*`, with
subgroup order chosen as the largest divisor of `p-1` not exceeding `2B`.
Visit complete cosets in a public order and retain the first `B` valid
canonical elliptic fibers. Record the subgroup generator, coset tags,
enumeration rank, and truncation boundary.

This is a ranked prefix of a coset-union predicate, not a complete PKM factor
base. Its `p-1` dependence is reported explicitly.

### Quartic-composition chain

Enumerate `t=0,1,...` through

`u=t+c`, `v=u^2+d`, `x=v^2+e mod p`,

deduplicate x-coordinates, and retain the first `B` valid canonical fibers.
Record every chain value and the public coefficients.

### Reciprocal-denominator chain

Enumerate `t=0,1,...` through

`u=t+c`, `d_t=t+d`, `x=u^2/d_t+e mod p`,

skip zero denominators, require the preregistered Legendre stratum of `d_t`,
deduplicate x-coordinates, and retain the first `B` valid canonical fibers.
Record numerator, denominator, inverse, character stratum, x-coordinate, and
enumeration rank.

The three families are attack-eligible only as public coordinate predicates.
Their toy discrete logarithms are diagnostics, not construction inputs.

## Matched Null

For each curve, generate `2,047` independent sets of `B` distinct random
canonical fibers. Sampling a random nonzero subgroup scalar and sampling a
random valid x-fiber induce the same law under the registered sign section on
these curves, so V2 uses one pooled null rather than naming duplicate null
models.

For a statistic where larger values are more structured, report

`p=(1 + number of null values >= candidate)/(2048)`.

For Freiman dimension, where smaller values are more structured, reverse the
inequality. Record rank, exceedance count, ties, and the full null-statistic
digest. The minimum attainable p-value is `1/2048`.

## Exact Additive Metrics

For scalar diagnostic set `A` of cardinality `B` in `Z/qZ`, let

`r2(g)=#{(a,b) in A^2: a+b=g}`

and

`r4(g)=#{(a,b,c,d) in A^4: a+b+c+d=g}`.

Record:

- D2 support, histogram, maximum multiplicity, and
  `E2=sum_g r2(g)^2`;
- V2 D2 normalized energy `E2/B^3`;
- spectral L4 mass `E2/B^4`;
- D4 support, histogram, maximum multiplicity, and
  `E4=sum_g r4(g)^2`;
- V2 D4 normalized energy `E4/B^7`;
- all representation totals, including `sum r2=B^2` and `sum r4=B^4`.

The D4 numerator is an ordered eight-tuple collision count. V2 uses the
standard scale-free normalizations above; V1's historical `E2/B^2` and
`E4/B^4` fields are not reused under the same names.

## Replayable Certificates

### Fourier witness

Compute the exact toy-group DFT of the indicator of `A`. Record the
nontrivial argmax frequency, real and imaginary coefficients, magnitude
normalized by `B`, conjugate symmetry check, and replay tolerance.

### Popular-difference witness

Record the top `B` nonzero differences, ordered multiplicities, all directed
edges induced by those differences, edge density, component sizes, and a
canonical digest.

### Freiman-relation witness

For every nontrivial equality `a_i+a_j=a_k+a_l`, form
`e_i+e_j-e_k-e_l`. Record a canonical independent relation basis, its exact
rational rank, and

`Freiman dimension = B - relation_rank - 1`.

Record the witness encoding length in logical field/index words. A metric
score without its argmax, differences, edges, or relation basis is not a
certificate.

## Target-Wide Predictor

Construct one row for every scalar `s in {0,...,q-1}`, including
`r4(s)=0`. The label threshold is the larger of one and the nearest-rank 95th
percentile of all `q` multiplicities.

Features may use only:

- target infinity;
- normalized target x/y bins;
- Legendre characters of registered coordinate shifts;
- small target-coordinate residues;
- membership in the candidate x-set;
- Legendre-character patterns of complete-addition denominators
  `x(target)-x(anchor)` for the first three public factor-base anchors;
- the registered target-side map or denominator stratum when computable.

The toy implementation may index the subgroup census to obtain a target
point, but scalar values may not appear in a feature. The verifier must
reconstruct the same target points by group addition.

Train on all six `10`- and `12`-bit curves and freeze before evaluation on all
three `14`-bit curves. Fit one categorical feature plus selected buckets.
Report full-target precision, recall, F1, mean multiplicity, oracle
enrichment, retained enrichment, and zero-support false-positive rate.

Use 127 deterministic label permutations to estimate a family-specific
predictor p-value. Bonferroni-correct the three candidate predictor tests at
family-wise alpha `0.05`.

## Controls

### True AP control

Use the literal scalar set `{a+jd: 0<=j<B}` without sign canonicalization.
It must have full AP coverage, Freiman dimension one, a replayable relation
basis, and extreme energy/Fourier diagnostics.

### Signed AP control

Retain the V1 sign-canonicalized scalar fixture as a separate structured-set
control. It is not required to have full AP coverage.

### Predictor-positive control

Across the same training/held-out curves, label all subgroup targets by the
public feature `chi(x-1)=+1`. The one-feature learner must retain at least
95% enrichment with nonzero precision and recall.

### Predictor-negative control

Deterministically permute labels within every curve. The same learner must
retain at most 20% enrichment on held-out curves and must not pass the
Bonferroni predictor gate.

## Multiple Testing

The primary energy family contains 27 preregistered D4 tests:
three candidates times nine curves. Apply Holm's step-down procedure at
family-wise alpha `0.05`.

The certificate family contains 81 preregistered tests:
27 cells times Fourier, popular-difference, and Freiman-dimension statistics.
Apply a separate Holm correction at family-wise alpha `0.05`.

Raw p-values, sorted Holm order, critical values, adjusted p-values, and ties
must be stored. Controls are reported separately and may not reduce the
candidate multiplicity penalty.

## Success Criterion

A candidate family is a V2 positive signal only if:

1. every one of its nine D4 tests survives the primary Holm correction;
2. every curve has at least one replayable certificate test surviving the
   certificate Holm correction;
3. its held-out all-target predictor retains at least 80% oracle enrichment,
   has nonzero precision and recall, and survives the Bonferroni permutation
   test;
4. all positive and negative controls pass;
5. no scalar enters candidate construction or predictor features.

A positive V2 signal authorizes a separate relation-compiler contract. It is
not an algorithmic promotion or an ECDLP improvement.

## Falsification Criterion

If no family passes, preserve only the scoped negative for these three
ranked coordinate chains, nine toy curves, and the V2 certificate/predictor
dictionary. Generate the next positive question from the narrowest failure:

- no energy signal: pursue an expansion/character-sum bound or new predicate;
- energy without certificate: enlarge the inverse-additive dictionary;
- scalar certificate without predictor: search coordinate linkages;
- predictor without charged support/decomposition: build a costed streaming
  compiler;
- curve-specific signal: isolate the responsible modulus, model, or map
  structure and test it without generic extrapolation.

## Metrics And Cost Accounting

- curve-generation attempts and order-count work;
- factor-base field operations, inversions, Legendre tests, and rejected x
  candidates;
- null-generation work;
- D2/D4 additions and counter updates;
- FFT/DFT method and transforms;
- relation rows and exact-rank operations;
- predictor rows, feature evaluations, permutations, and fitting work;
- wall time, peak RSS, artifact bytes, and source/input hashes.

## Reproduction Command

```bash
python3 experiments/EXP-ECDLP-COORD-EXPANSION-001/src/coord_energy_certificate_v2.py \
  --bits 10 12 14 \
  --curve-seeds 17 53 89 \
  --null-draws 2047 \
  --predictor-permutations 127
```
