# Experiment Contract: Direct Equality Pair V2 Independent Cross-Tree

## Hypothesis

For valid points on the recorded toy curves, the simultaneous-zero residual
pair

`(zq X-xq Z, zq Y-yq Z)`

has the same zero semantics for every distinct permutation of four factor-base
points, every full binary addition tree on the five leaves, both cut-2 and
cut-3 decompositions, and arbitrary nonzero projective rescalings.

This is a semantic prerequisite for a rank-two net, divisor, or resultant
compiler. It is not a compression or ECDLP claim.

## Null Hypotheses

1. An addition order or tree changes the affine output.
2. A cut-2 or cut-3 recombination differs from direct addition.
3. Projective rescaling changes the canonical residual class or zero status.
4. Simultaneous zero differs from direct affine equality.
5. Infinity, doubling, inverse pairs, repeated points, or target mutation
   exposes an unhandled semantic case.

## Parameters

- immutable `TYPED-FIVE-EC-V1/raw-result.json`;
- immutable `DIRECT-EQUALITY-PAIR-V1/raw-result.json` for the two recorded
  targets per family;
- curves `q=953,3919,15583`;
- random-x, source-PRF-x, x-interval, rational-union;
- every progression point;
- every four-index multiset from the factor base;
- every distinct permutation of each multiset;
- all 14 ordered full binary trees on five leaves;
- cut 2: `(A+R1)+(R2+R3+R4)`;
- cut 3: `(A+R1+R2)+(R3+R4)`;
- deterministic nonzero output and target scales.

## Independent Model

The audit uses a standalone affine short-Weierstrass group law. It does not
import the RCB, polynomial, factor, rank, or verifier implementations used by
V1. The V1 artifact supplies target coordinates only.

## Metrics

- canonical tuple, ordered tuple, and tree evaluations;
- affine permutation/tree mismatches;
- cut-2 and cut-3 recombination mismatches;
- simultaneous-zero/equality mismatches;
- projective residual scale mismatches;
- planted and held-out witness counts;
- infinity output count;
- edge-case and mutation-control outcomes;
- operation counts, wall time, and peak RSS;
- authenticated row and witness digests.

## Positive Controls

- the 14 generated trees are distinct and complete;
- identity, inverse, doubling, and repeated-point additions match the curve
  law;
- a planted output gives simultaneous zero;
- scaling output and target projective representatives preserves canonical
  residual class and zero status;
- mutating one target coordinate destroys a planted zero.

## Negative Control

A deterministic off-target mutation must not pass the simultaneous-zero
predicate for the planted output.

## Success Criterion

Across every recorded row, all tree, permutation, cut, zero-semantic, and
scale mismatch counts are zero; every planted target has at least one
witness; all edge and mutation controls pass; and a separately implemented
verifier exactly reproduces the authenticated aggregate digests.

Passing certifies only the tested semantic boundary.

## Falsification Criterion

Any mismatch falsifies use of the V1 residual pair as a compiler leaf until
the failing case is explained. Passing does not certify polynomial factors,
minimal dimensions, succinct indexing, relation rank, or sub-rho cost.

## Reproduction Command

```bash
python3 src/direct_equality_pair_cross_tree.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  development/DIRECT-EQUALITY-PAIR-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union
```
