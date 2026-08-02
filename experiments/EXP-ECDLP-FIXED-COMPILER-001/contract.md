# Experiment Contract: Fixed-curve five-term relation compiler

## Status

`HYPOTHESIS`, `TOY-EVIDENCE`, `HEURISTIC`, and `MODEL-BOUND`.

No canonical run is approved by this document. Development tests must be labeled non-frozen and cannot be promoted into evidence.

## Hypothesis

On clean generated prime-order curves, at least one coordinate-defined sign-complete factor base preserves at least `0.8x` the exact five-term support of each matched random-x and random-scalar base, reaches full relation rank and verified target descent, and has an advice-bit online-query-squared diagnostic at most `0.8x` both matched-null values.

## Null hypothesis

After all offline work, witness payloads, unsuccessful probes, relation targets, modular linear algebra, and descent are charged, the coordinate families provide no reproducible advantage over both matched random-x and random-scalar controls, or they fail rank or descent.

## Model and parameters

- Group: a prime-order group `G=<P>=E(F_p)` on a generated short-Weierstrass curve.
- Curve policy: nonsingular, ordinary, trace not in `{0,1}`, `j` not in `{0,1728}`, cofactor one.
- Field policy: the first seeded prime selected independently of `p-1` factorization, with `p mod 4 = 3`; the complete factorization of toy `p-1` is disclosed.
- Generator: fixed per curve and identical for all factor-base families.
- Factor-base size: the smallest sign-complete even `B=2f` for which the exact formal signed five-term class count is at least `0.5q`. The raw `B^5/q` heuristic is recorded only as an asymptotic sanity check because it overcounts permutations and cancellation-equivalent tuples.
- Candidate families: `x_interval`, `square_map`, and `rational_union`.
- Null controls: independently seeded `random_x` and `random_scalar`.
- Compression-positive control: `scalar_progression`, ineligible for promotion.
- Advice: every distinct four-term sum plus at most `w` lexicographically first unordered source witnesses, for `w in {1,4}`.
- Relation shape: `aP = F_i1 + F_i2 + F_i3 + F_i4 + F_i5`.
- Query: scan `F_i5`, compute `aP-F_i5`, and probe the four-sum advice.
- Relation solve: modular Gaussian elimination over `F_q`, followed by pointwise verification of every recovered factor-base logarithm.
- Individual logarithm: randomize an unknown target by a charged known multiple of `P`, query for a five-term witness, subtract the randomizer, and verify the recovered scalar.

## Cost model

Report, without combining away any category:

- factor-base construction group, field, exponentiation-proxy, and map operations;
- pair and four-multiset enumeration operations and attempted tuples;
- advice keys, witnesses, payload-bit lower estimate, canonical serialized bytes, and Python deep bytes;
- target-generation scalar-multiplication operations;
- successful and unsuccessful relation-query operations and table probes;
- logical key and witness bytes read;
- modular row additions, multiplications, and inversions;
- individual-descent randomization and query operations;
- matched Pollard-rho group and field operations;
- an actually executed fixed-base BSGS table using no more than the candidate's full advice-bit budget, including factor-base logarithms;
- number of targets attempted, targets supported, equations retained, matrix rank, and descent success probability.

The diagnostic

`S_bits * T_group_queries^2 / (epsilon * q)`

uses the disclosed advice payload bits, exact one-query support probability, and measured group additions in a single first-witness query. It is `MODEL-BOUND`: the generic theorem uses bits and generic-oracle queries and hides polylogarithmic factors. Serialized and deep-memory variants are reported separately. None is called a lower-bound violation.

## Metrics

- exact four-term support and exact five-term support;
- exact one-query success probability;
- witness multiplicity retained per four-sum;
- offline operations and advice storage;
- average and maximum first-witness query probes over every toy group target;
- relation targets needed for full rank;
- unique equation count and rank trajectory;
- factor-base logarithms verified pointwise;
- individual-log attempts and recovered scalars;
- total end-to-end costs and matched rho costs;
- fitted slopes across at least three sizes, reported as exploratory only.

## Positive controls

1. `random_scalar` should usually give random-like support and a full-rank functional path.
2. `scalar_progression` should compress sumsets but lose coverage or reveal why scalar-defined structure is ineligible.
3. A deliberately altered relation coefficient, right-hand side, witness, or descent randomizer must be rejected by the independent verifier.

## Negative controls

1. `random_x` is the primary matched constructor control for coordinate selection cost.
2. `random_scalar` tests whether any signal is merely generic point-set behavior.
3. `w=1` tests whether functional witness compression destroys matrix rank relative to `w=4`.

## Functional success criterion

For a row to pass the functional gate:

1. exact witness arithmetic and exact five-term support agree;
2. the relation matrix reaches rank `B` within the frozen target budget;
3. every solved factor-base logarithm reproduces its point;
4. every scheduled randomized individual-log challenge is recovered and verified;
5. the independent verifier exactly reconstructs the row.

## Research-routing success criterion

A coordinate family is routed to a larger successor only if, on every claimed instance:

1. the functional gate passes;
2. exact five-term support is at least `0.8x` each matched null;
3. the advice-bit query-squared diagnostic is at most `0.8x` each matched null;
4. no charged offline category exceeds either matched null by more than `4x`;
5. both sampled-average and deterministic-worst-case online group operations beat fixed-base BSGS under the same disclosed advice-bit budget;
6. the signal appears at all three sizes and at least two seeds per size.

## Breakthrough gate

No result is an exponent improvement unless a later experiment on random curves fits a total end-to-end exponent below `0.5` with preprocessing, memory, relation collection, linear algebra, descent, failures, and matched rho included. This experiment is not sized to meet that gate.

## Falsification criterion

The current candidate is narrowed or rejected if all coordinate families fail the routing criterion, if rank or descent fails despite full support, if the win depends on the scalar-progression control, or if independent replay exposes an uncharged or scalar-oracle path.

## Reproduction command

Canonical commands will be hash-frozen in `specification.json` only after independent theory, source, and red-team review. Until then, use the explicitly non-frozen development test command:

```bash
PYTHONPATH=src python3 -B tests/test_fixed_curve_compiler.py -v
```

## Interpretation boundary

This is an authorized toy index-calculus experiment. A verified toy discrete logarithm demonstrates pipeline correctness only. It does not break a deployed curve, improve the generic square-root exponent, or establish that fixed-curve preprocessing beats the generic frontier.

The first protocol uses one independently seeded draw from each null constructor per curve. A local instance gate is therefore not a finite-null significance claim. Aggregate routing additionally requires two passing seeds at every scheduled size; any surviving signal must still receive a multi-replicate null-calibration successor.
