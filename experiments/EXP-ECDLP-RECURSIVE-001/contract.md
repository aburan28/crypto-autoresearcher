# Experiment Contract: EXP-ECDLP-RECURSIVE-001

## Hypothesis

`HYPOTHESIS`: A coordinate-defined factor base can retain at least `0.8x` random `m`-fold target coverage while reducing split advice or online query work to at most `0.8x` random.

## Null hypothesis

After matching cardinality, symmetry, curve, targets, and corrected unordered occupancy, every coordinate family either behaves like random or gains compression only by losing final target coverage.

## Parameters

- field/curve family: generated ordinary prime-order short-Weierstrass curves over prime fields
- sizes: 12, 14, and 16 field bits, with strictly increasing `q`
- seeds: 1473001 and 1473002
- factor base: smallest even `B` with `binomial(B+m-1,m)/q >= 0.5`
- relation shape: `m in {5,6,8}` factor-base points summing to a target
- baseline: matched random-scalar structure control, matched random-x construction control, scalar-progression control, corrected occupancy, and measured Pollard rho

## Metrics

- group operations: construction, split compilation, online query, witness recovery, and rho separated
- field operations: affine multiplications and inversions by phase
- memory: advice entries, deep bytes, estimated traffic, and peak RSS
- relation probability: exact successes over 256 shared targets
- rank: not applicable before a relation matrix exists
- solver degree: not applicable; no Groebner solver is used
- wall-clock: captured by the immutable run wrapper

## Positive control

A scalar progression should compress intermediate supports but lose final target coverage.

## Negative control

A uniformly sampled factor base at matched cardinality and sign mode.

## Success criterion

Require `>=0.8x` random-scalar target success, `<=0.8x` random-scalar advice or online work, `<=4x` random-x offline work, replication in three instances across two sizes, and exact independent verification.

## Falsification criterion

Narrow the hypothesis if no coordinate family meets the joint gate or any arithmetic/control invariant fails.

## Reproduction command

The specification remains `review_required`; the immutable runner must reject execution until coordinator approval is recorded. After an independent pre-run `GO`, use the repository runner with the frozen source and no parameter overrides:

```bash
PYTHONPATH=src python3 -B -m crypto_autoresearcher.cli run \
  --experiment-dir experiments/EXP-ECDLP-RECURSIVE-001 \
  --run-id RUN-ECDLP-RECURSIVE-001 \
  --seed 1473001 \
  --timeout 900 \
  -- python3 -B experiments/EXP-ECDLP-RECURSIVE-001/src/recursive_expansion.py
```

The verifier must then be captured as a distinct immutable run against the resulting `raw-result.json`; its exact command and input hash belong in that run manifest.

## Claim boundary

`TOY-EVIDENCE`, `HEURISTIC`, and `MODEL-BOUND`. A positive result would justify a source-tagged compiler experiment, not a faster-than-rho or deployed-curve claim.
