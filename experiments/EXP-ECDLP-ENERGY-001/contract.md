# Experiment Contract: EXP-ECDLP-ENERGY-001

## Hypothesis

`HYPOTHESIS`: At least one tested coordinate-defined sign-complete factor base has persistent additive concentration and five-term target coverage beyond a matched random factor base without hiding more than a fourfold offline group-operation cost.

## Null hypothesis

After matching cardinality, sign symmetry, curve, and targets, the coordinate-defined sets have no preregistered advantage over the random control.

## Parameters

- field/curve family: generated ordinary short-Weierstrass curves over prime fields, with a prime subgroup `q >= p/16`
- sizes: 15, 17, and 19 field bits
- seeds: base seed 1469001, deterministically domain-separated by size and family
- factor base: nearest even integer to `q^(1/5)`, minimum 8
- relation shape: five signed factor-base points summing to a target
- baseline: matched random sign-complete factor base, random-sum occupancy, and measured Pollard rho

## Metrics

- group operations: factor-base construction, table compilation, online query, and rho measured separately
- field operations: affine multiplications and inversions counted by phase
- memory: peak RSS plus deep bytes of compiled counters
- relation probability: fraction of 128 held-out targets with a five-term witness
- rank: not applicable to this pre-relation-matrix experiment
- solver degree: not applicable; no Groebner solver is used
- wall-clock: captured by the immutable run wrapper

## Positive control

A short scalar progression `+-{G, 2G, ..., (B/2)G}` should have elevated pair energy and compressed sumsets.

## Negative control

A uniformly sampled sign-complete set of subgroup point fibers at the same cardinality.

## Success criterion

Promote only if a coordinate family reaches at least 2.0x random pair energy and 1.5x random five-term target success at two of three sizes, with offline group-operation ratio at most 4.0 and an exact independent verifier pass.

## Falsification criterion

Narrow this hypothesis if no coordinate family reaches the joint threshold or any arithmetic invariant fails.

## Reproduction command

```bash
PYTHONPATH=src python3 -m crypto_autoresearcher run \
  --experiment-dir experiments/EXP-ECDLP-ENERGY-001 \
  --run-id RUN-ECDLP-ENERGY-001 --seed 1469001 --timeout 600 -- \
  python3 experiments/EXP-ECDLP-ENERGY-001/src/coordinate_energy.py \
  --bit-sizes 15 17 19 --seed 1469001 --targets 128 --rho-trials 8
```

## Claim boundary

`TOY-EVIDENCE`, `HEURISTIC`, and `MODEL-BOUND`. This preflight cannot establish a sub-rho exponent, an arbitrary-curve result, or deployment relevance.
