# EXP-EC-CODE-001 — Elliptic AG-code sparse-syndrome bridge

## Purpose

Reproduce an exact toy correspondence between elliptic-curve point relations and sparse dependencies in an evaluation code, then use the exhaustive enumerator as an oracle for future support-ranking experiments.

This experiment is **not** a faster-than-rho claim and is **not** evidence that generic list decoding or generic Schur closure solves ECDLP.

## Scope

Curve:

`E/F_1009: y^2 = x^3 + 2x + 25`

The group has prime order 991. The factor base is selected without discrete logs: take the first 32 increasing x-coordinates that admit a point, choosing the smaller y-root.

For an affine point `P=(x,y)`, evaluate the basis of `L(4O)`:

`v(P) = (1, x, y, x^2)^T`.

For four distinct affine points, the experiment checks exhaustively that evaluation-column singularity is equivalent to the EC relation `P1+P2+P3+P4=O`.

It then selects an independent target by coordinate enumeration, tests all 3-subsets of the factor base, collects target decompositions, solves the factor relation matrix modulo the group order, and recovers the target discrete log.

## Run

```bash
python3 experiments/EXP-EC-CODE-001/src/toy_code_bridge.py \
  --output experiments/EXP-EC-CODE-001/results/toy_results.json
```

The script uses only the Python standard library.

## Expected exact results

- group order: 991
- four-point subsets checked: 35,960
- singular four-point supports: 36
- correspondence mismatches: 0
- factor relation rank: 31 / 31 maximum
- target 3-subsets checked: 4,960
- target decompositions: 5
- recovered target log: 780
- scalar-multiplication verification: true
- row-code dimension: 4
- row-code Schur-square dimension: 8
- seeded random comparator Schur-square dimension: 10

## Negative result recorded by this experiment

Dimension-only shortening is non-discriminative on this instance. Exhaustively forcing 1, 2, or 3 evaluation zeros gives constant `(dimension, Schur-square dimension)` profiles:

- 1 point: `(3, 6)` across all 32 choices
- 2 points: `(2, 3)` across all 496 choices
- 3 points: `(1, 1)` across all 4,960 choices

Future agents must not report these dimensions as a support-ranking signal.

## Next experiment

Keep exhaustive support membership as a hidden oracle and compute richer target-aware features from the actual multiplication maps of the evaluation spaces. Candidate features should be evaluated as classifiers/rankers of partial supports, then validated on unseen curves and increasing sizes.

Required controls:

- random linear codes of equal dimensions;
- random curve-point factor bases;
- arbitrary syndromes vs curve-valued syndromes;
- independently chosen targets;
- full accounting of preprocessing, candidate scoring, support verification, relation rank gain, and memory.

Any method that materializes all source tuples or reconstructs a source-evaluation tensor fails the experiment boundary.
