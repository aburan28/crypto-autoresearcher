# Experiment Contract: TT Zero-Locator Rank Census V1

## Hypothesis

For the exact five-source elliptic point-sum tensor, the first quadratic norm
locator `h_Q = g_Q g_Q^p` may retain a nontrivial low-rank unfolding at an
early 2-versus-3 cut on at least one registered coordinate family. If such a
signal survives target and curve controls, it identifies a concrete algebraic
object for a future compact selector or transposed operator.

This is a rank-census hypothesis only. It does not assert that a low-rank
unfolding can be constructed, applied, inverted, or turned into an ECDLP
relation compiler.

## Null Hypotheses

1. The first norm product and its powers have ranks near the tensor support
   limits for every ordinary toy curve and coordinate family.
2. Any low rank of the final zero indicator is explained by its sparse support
   and is matched by a support-preserving random tensor.
3. Any apparent signal is target-independent, a projective or affine
   representation artifact, or a one-curve accident.

## Status and Boundaries

`HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`.

The experiment uses exact finite-field values and exact modular row rank over
`F_p`. It measures a fully enumerated five-way tensor on generated ordinary
prime-field curves. It does not measure a deployed-size algorithm, fixed-curve
preprocessing, a relation matrix, target descent, or a discrete-log solve.

## Parameters

- immutable input: `TYPED-FIVE-EC-V1/raw-result.json`;
- three generated ordinary curves with `q=953,3919,15583`;
- registered coordinate families: `random_x`, `source_prf_x`, `x_interval`,
  `rational_union`;
- dimensions `[|A|,B,B,B,B]`, with the recorded public progression and factor
  base, and every ordered tuple included;
- targets: the recorded `planted` target, held-out target, and deterministic
  `shifted_control = planted + generator`;
- locator: affine residual norm
  `h_Q=(x(Q)-x(T))^2-nu(y(Q)-y(T))^2`, with a fixed field nonsquare `nu`;
- stages: `h`, `h2`, `h4`, `h8`, and the exact zero indicator;
- matched-random control: a deterministic binary tensor with exactly the
  observed indicator support at each cell;
- rank: exact row rank at cuts 1, 2, 3, and 4 over `F_p`;
- order: `[A,R0,R1,R2,R3]`, with sequential affine point addition.

## Metrics

- unfolding rank at every cut and stage;
- ambient row/column dimensions;
- exact zero and nonzero support;
- matched-random indicator ranks and support;
- point additions, field inversions, field multiplications, tensor entries,
  wall time, and peak RSS;
- deterministic value digests and source/input hashes.

## Positive Controls

- an all-one tensor has rank one at every unfolding;
- producer and verifier agree on affine point addition and exact rank;
- target translation and tensor dimensions are replayable from public input;
- every serialized row has the exact product of its dimensions as its entry
  count;
- verifier mutations change at least one required check.

## Negative Controls

- the shifted target is not used as a planted relation target;
- the exact zero-indicator support is compared with a deterministic
  support-matched random binary tensor;
- all four candidate families are compared across all three curves and the
  held-out/shifted target schedule.

## Provisional Signal Gate

A diagnostic early-rank signal requires, on at least two of three curves and
for at least one non-control target, that `h` and every power stage have a
2-versus-3 rank below `0.8` times the smaller ambient dimension, while the
matched-random indicator does not have the same rank profile. This is a
follow-up selector-design signal only. It cannot promote an attack.

The final indicator is never accepted as a positive low-rank signal solely
because it is sparse. A rank claim must identify the stage, cut, support, and
matched-random comparison.

## Falsification Criteria

- independent replay or mutation testing fails;
- any point or tensor accounting mismatch occurs;
- no family has a cross-curve early-stage signal;
- low rank appears only for the sparse indicator or only on the scalar
  progression control;
- the observed rank is at the ambient limit after accounting for zero rows or
  repeated support.

Failure is a scoped negative for this exact norm-power unfolding, not a claim
about all TT, tensor-network, nonlinear, or coordinate-specific approaches.

## Reproduction Commands

```bash
python3 src/tt_zero_locator_rank_census.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union
```

```bash
python3 src/verify_tt_zero_locator_rank_census.py \
  /path/to/raw-result.json
```
