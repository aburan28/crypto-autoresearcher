# Direct Equality Pair V2 Independent Cross-Tree Analysis

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

The simultaneous-zero residual semantics are stable across every tested
permutation, all 14 five-leaf binary trees, both cut allocations, projective
rescaling, repeated points, inverse pairs, doubling, and infinity outputs.
On the frozen canonical toy fixtures, this is a replicated abstract-affine
observation. It does not independently certify the V1 polynomial factors or
construct a simultaneous-zero index.

## Exact Run

- source commit:
  `a6eac6cead1ed48d22b8bf3674de1915c39bd596`;
- curves: `q in {953,3919,15583}`;
- families: random-x, source-PRF-x, x-interval, rational-union;
- progression sizes: 7, 6, 11;
- factor-base sizes: 5, 8, 10;
- every four-index multiset and every distinct permutation;
- all 14 ordered full binary trees on the five leaves;
- cut-2 and cut-3 recombination;
- deterministic nonzero output and target rescaling;
- standalone affine group law with no V1 RCB, polynomial, factor, rank, or
  verifier imports;
- independently implemented arithmetic replay: valid;
- strict envelope successor: valid, including eight rejection mutations.

The producer ran in 24.05 seconds with 27,869,184 bytes peak RSS. The
independent verifier ran in 27.07 seconds with 25,903,104 bytes peak RSS.

## Coverage

Across 12 rows:

- ordered tuples: 555,804;
- tree evaluations: 7,781,256;
- affine tree mismatches: 0;
- cut-2 recombination mismatches: 0;
- cut-3 recombination mismatches: 0;
- residual-zero/equality mismatches: 0;
- projective-class or zero-status scale mismatches: 0;
- mutation-control failures: 0;
- planted ordered witnesses: 316;
- incidental held-out ordered witnesses: 84;
- infinity outputs: 36.

The partial instrumented affine-group-law proxy counts were:

| operation | count |
|---|---:|
| affine additions attempted | 28,346,004 |
| inversions | 25,563,926 |
| multiplications | 154,009,346 |
| doublings | 312,895 |
| identity returns | 2,780,318 |
| inverse-pair returns | 1,760 |

These are validation-path proxy counts, not complete executed-field,
memory-traffic, compiler, or ECDLP costs.

## Independent Replay

The verifier has its own:

- affine addition implementation;
- tree generator and evaluator;
- projective residual normalization;
- tuple enumeration;
- witness and aggregate digest construction.

For every row supplied to it, the original verifier reproduced:

- tuple and tree counts;
- all mismatch counters;
- planted and held-out witness counts and first witnesses;
- infinity counts;
- authenticated row and witness digests.

The original verifier did not enforce row completeness, aggregate totals,
controls, operation fields, mutation counters, or tree digests. A strict
successor now derives the expected 12-row sequence, checks that full envelope,
and rejects dropped/duplicate-row, summary, control, operation, tree, mutation,
and cross-cut-target changes.

The producer and verifiers share the immutable typed fixture and V1 target
coordinates. Planted provenance and cross-cut target equality were
independently recounted. Held-out target-selection derivation is not
regenerated.

## Strongest Valid Conclusion

> For the three recorded prime-order toy curves, four coordinate families,
> two affine targets per family, and every enumerated `A+4R` ordered tuple,
> the abstract elliptic-curve sum and simultaneous-zero equality residual are
> invariant under all distinct R permutations, all 14 five-leaf binary trees,
> cut-2/cut-3 recombination, and the sampled nonzero projective rescalings.

Two arithmetic implementations, an independent aggregate recount, and the
strict envelope agree on this fixed-fixture statement. Arbitrary-scale
invariance is an algebraic consequence of bilinearity, not an exhaustive
empirical scale sweep.

It does not close:

- independent coefficient-level verification of the V1 direct factors;
- V1 RCB implementation equivalence on every edge case;
- minimal factor dimensions or intrinsic predicate rank;
- simultaneous-zero reporting below explicit `B^3` state;
- relation rank, memory traffic, target amortization, or descent;
- any asymptotic or deployment-relevant ECDLP claim.

Canonical residual direction remains non-injective. Only simultaneous zero,
not residual direction, certifies target equality.

## Next Concrete Action

Before a scheme-aware resultant run treats the factorization itself as
certified, add an independent coefficient-level audit:

1. emit authenticated suffix coordinate/factor chunks from V1;
2. independently reduce polynomials modulo the Weierstrass cubic;
3. evaluate random and planted prefix/suffix pairs;
4. mutate coefficients and targets as negative controls;
5. reproduce the 24/12 ambient ranks without importing producer algebra.

Then run `ITERATED-DIVISOR-RESULTANT-V1-SCHEME-AWARE`, keeping reduced,
canonical-multiset, ordered-convolution, and unique-D2-pair divisors separate.
