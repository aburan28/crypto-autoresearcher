# Experiment Contract: Coordinate Energy Certificate V2

## Pre-Run Review Amendment

The producer was smoke-tested on one development curve per size with seeds
`17, 53, 89`. Those curves are excluded from confirmation. The frozen run
uses fresh seeds `101, 211, 307`.

The review also fixes these interpretation boundaries before the confirmatory
run:

- Fourier witnesses are exact toy-scalar diagnostics, not public-coordinate
  certificates;
- only popular-difference and Freiman witnesses that replay as elliptic-point
  equalities may satisfy the certificate gate;
- statistical rejection must also have local candidate-versus-null AUC at
  least `0.65`;
- the three constructions are ranked coordinate-chain prefixes and are not
  claimed novel relative to PKM-style rational-map factor bases;
- the all-target predictor is diagnostic association only. V2 does not credit
  post-generation filtering with avoided point-generation work.
- the producer may emit only a provisional screening signal. A positive V2
  signal requires an independently structured verifier to replay public
  certificates, exact ranks, predictors, controls, provenance, and the exact
  confirmatory configuration;
- canonical-random comparisons are reference-tail ranks. They become exact
  finite-sample p-values only under the additional conditional-exchangeability
  hypothesis that a candidate statistic follows the uniform canonical-fiber
  reference law. V2 does not assert that theorem for these deterministic
  coordinate chains.

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
2. a replayable popular-difference or Freiman-relation certificate, with
   Fourier retained only as a scalar diagnostic;
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
- three frozen curve seeds per bit size: `101, 211, 307`;
- no rejection based on `p-1` smoothness, `j`, factor-base behavior, or
  candidate score;
- one independently hash-seeded factor-base construction per candidate and
  curve, giving nine exact deterministic instances per family;
- target factor-base size
  `B=max(5, round(q^(1/5)))`, with exact cardinality enforced.

All curves, seeds, selection attempts, `p-1` factors, and generator checks are
recorded. Curve identifiers must be distinct.

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
Record every selected chain value, the public coefficients, and the
truncation boundary. The verifier recomputes every examined value through
that boundary.

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

`r=(1 + number of null values >= candidate)/(2048)`.

For Freiman dimension, where smaller values are more structured, reverse the
inequality. Record rank, exceedance count, ties, tie-aware AUC, and the full
null-statistic digest. Call `r` a
`canonical_random_reference_tail_rank`; absent a proved exchangeability null,
do not call it an exact p-value. Its minimum is `1/2048`.

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

Compute a full-census numerical FFT of the indicator of `A`. Record the
nontrivial argmax frequency, real and imaginary coefficients, magnitude
normalized by `B`, conjugate symmetry check, NumPy version, and replay
tolerance. This is floating numerical evidence, not an exact Fourier
certificate.

This witness uses diagnostic discrete-log indexing. It is not
coordinate-computable advice and cannot satisfy the public-certificate
promotion condition.

### Popular-difference witness

Record the top `B` nonzero differences, ordered multiplicities, all directed
edges induced by those differences, the corresponding public elliptic point
for each difference, edge density, component sizes, and a canonical digest.
Replay checks every edge by elliptic subtraction without using the stored
diagnostic scalar difference.

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
three `14`-bit curves. Fit one categorical feature plus exactly one selected
bucket. Report pooled and per-held-out-curve full-target precision, recall,
predicted coverage, F1, mean multiplicity, oracle enrichment, retained
enrichment, and zero-support false-positive rate.

Use 127 deterministic label permutations to estimate a family-specific
predictor reference-tail rank. Bonferroni-screen the three candidate
predictors at family-wise alpha `0.05`. Every held-out curve must have at
least 1% predicted coverage, at least 10% recall, nonzero precision, and at
least 80% retained enrichment.

The permutation statistic is
`max(0, retained_oracle_enrichment) * recall`; per-curve coverage remains a
separate mandatory gate. Raw enrichment alone is forbidden because a tiny
random bucket can tie the oracle while recovering negligible mass.

## Controls

### True AP control

Use the literal scalar set `{a+jd: 0<=j<B}` without sign canonicalization.
It must have full AP coverage, Freiman dimension one, a replayable relation
basis, and extreme energy/Fourier diagnostics.

### Signed AP control

Retain the V1 sign-canonicalized scalar fixture as a separate structured-set
control. It is not required to have full AP coverage. Its exact `E4`
reference-tail rank must be at most `0.01`, and every stored public EC
relation must replay.

### Predictor-positive control

Across the same training/held-out curves, label all subgroup targets by the
public feature `chi(x-1)=+1`. The one-feature learner must retain at least
95% enrichment, recover `chi_x_minus_1`, pass every per-curve
coverage/recall gate, and pass the same permutation/Bonferroni pipeline.

### Predictor-negative control

Deterministically permute labels within every curve. The same learner must
retain at most 20% enrichment on held-out curves and must not pass the
same permutation/Bonferroni predictor gate.

## Multiple Testing

The primary energy family contains 27 preregistered exact-integer `E4`
screens:
three candidates times nine curves. Apply Holm's step-down procedure at
family-wise alpha `0.05`.

The certificate family contains 81 preregistered screens:
27 cells times Fourier, popular-difference, and Freiman-dimension statistics.
Apply a separate Holm correction at family-wise alpha `0.05`.

Rank D4 by integer `E4`, popular differences by the exact top-B count sum,
and Freiman structure by integer relation rank/dimension. Rounded display
ratios and floating Fourier coefficients may not determine exact ties.

Raw reference ranks, sorted Holm order, critical values, adjusted screening
ranks, and ties must be stored. Also report tie-aware local
candidate-versus-null AUC, with the candidate direction fixed by the metric.
Controls are reported separately and may not reduce the candidate
multiplicity penalty.

## Success Criterion

A candidate family is a verified V2 positive signal only if:

1. every one of its nine D4 tests survives the primary Holm correction;
2. every D4 cell has local AUC at least `0.65`;
3. every curve has at least one public EC-replayable popular-difference or
   Freiman test surviving the certificate Holm correction with local AUC at
   least `0.65`;
4. its held-out all-target predictor retains at least 80% oracle enrichment,
   satisfies the per-curve coverage/recall gates, and survives the Bonferroni
   permutation screen;
5. all positive and negative controls pass;
6. no scalar census enters candidate construction and no scalar enters
   predictor features;
7. the command is the exact frozen 3-by-3 configuration, the recorded source
   tree is clean, all curve identifiers are distinct, and independent
   verification passes.

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

The producer records its internal boundary. External wrapper time/RSS,
serialized artifact bytes, final commit/tree cleanliness, and verifier costs
are pinned in the immutable run manifest; they may not be inferred from the
producer's self-report.

## Reproduction Command

```bash
python3 experiments/EXP-ECDLP-COORD-EXPANSION-001/src/coord_energy_certificate_v2.py \
  --bits 10 12 14 \
  --curve-seeds 101 211 307 \
  --null-draws 2047 \
  --predictor-permutations 127
```

Any other parameters require `--development`; development runs disable
confirmatory promotion.
