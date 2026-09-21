# Experiment Contract: Scheme-Aware Point DAG V1

## Hypothesis

An oriented point-cycle product DAG over `F_(p^2)` can represent and query
four-sum image cycles while preserving the distinct multiplicities of:

1. reduced support;
2. canonical source multisets;
3. ordered fourfold convolution;
4. unique-D2-pair pushforward.

The preflight tests exact semantics, witness descent, and state growth. It does
not claim a resultant compression or ECDLP improvement.

## Null Hypotheses

1. The four cycle types are conflated or have incorrect total degree.
2. Their reduced point supports differ.
3. The oriented encoding `x+omega*y` collides on affine points.
4. Characteristic-polynomial roots do not match exact point membership.
5. A reported hit cannot descend to source factor-base indices and replay.
6. Infinity multiplicity is lost.
7. Product-DAG state or work is already comparable to explicit route
   enumeration, leaving no compression signal.

## Parameters

- fixed recorded curve `p=971`, `q=953`;
- nested `B in {2,3,4,5}`;
- one recorded seed per family;
- x-interval candidate;
- scalar-progression compression control;
- random-x matched subgroup control;
- source-PRF-x matched solvable-x control;
- nonsquare quadratic extension `F_p[omega]/(omega^2-delta)`;
- complete affine addition with typed infinity branch.

This 16-cell run is an implementation and state-growth preflight. It is not
the multi-seed 48-cell scaling experiment.

## Typed Cycles

- `reduced`: coefficient one on every canonical-D4 image point;
- `canonical`: one route for every `i1<=i2<=i3<=i4`;
- `ordered`: one route for every ordered four-tuple;
- `unique_d2_pair`: coefficient one for every unordered pair of unique
  canonical-D2 image points.

No squarefree conversion is allowed on canonical or ordered cycles.

## Point DAG

For each typed cycle:

1. construct the exact point/multiplicity map and first source witness;
2. split infinity multiplicity;
3. encode finite points injectively as `x+omega*y`;
4. build
   `Phi(T)=product_P (T-iota(P))^m(P)`
   with a balanced product tree;
5. query deterministic positive and negative targets;
6. replay every returned first witness by independent curve addition.

The characteristic polynomial is a cycle encoding, not a claim about a
scheme-theoretic image.

## Metrics

- total cycle degree, reduced point support, x support, infinity multiplicity;
- multiplicity histogram/digest and witness digest;
- characteristic-polynomial degree/digest;
- product-tree nodes, maximum live coefficients, coefficient operations, and
  serialized bytes;
- source route attempts and curve additions;
- query extension-field operations;
- first-witness descent/replay work;
- numerical `sqrt(q)`, balanced-BSGS records, and explicit route baselines.

## Controls

- exact degree formulas:
  - canonical: `binomial(B+3,4)`;
  - ordered: `B^4`;
  - unique D2 pair: `binomial(|supp(D2)|+1,2)`;
  - reduced: reduced canonical support;
- all four reduced supports equal;
- oriented finite encodings are injective;
- every polynomial positive is a root and every negative is not;
- every first witness replays to its image point;
- explicit infinity, repeated-index, doubling, and inverse-pair cases are
  retained when present.

## Success Criterion

Every typed cycle passes degree, support, polynomial, query, and witness
checks under an independent verifier. Passing establishes exact point-DAG
semantics only.

## Falsification Criterion

Any coefficient, support, infinity, membership, or witness mismatch makes the
run invalid. If retained polynomial state or build work tracks explicit cycle
degree without structural savings, preserve that as a scoped negative for
the explicit oriented product representation.

## Reproduction Command

```bash
python3 src/scheme_aware_point_dag.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families x_interval scalar_progression_control random_x source_prf_x \
  --b-values 2 3 4 5
```
