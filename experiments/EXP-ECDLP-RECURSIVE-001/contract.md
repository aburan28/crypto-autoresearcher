# Experiment Contract: EXP-ECDLP-RECURSIVE-001

## Hypothesis

`HYPOTHESIS`: A coordinate-defined factor base can retain at least `0.8x` random exact `m`-fold support while reducing the functional-advice-byte `S*T^2/(epsilon*q)` diagnostic to at most `0.8x` random.

## Null hypothesis

After matching cardinality, symmetry, curve, targets, and corrected unordered occupancy, every coordinate family either behaves like random or gains compression only by losing final target coverage.

## Parameters

- field/curve family: generated ordinary prime-order short-Weierstrass curves over seeded primes constrained to `p mod 4 = 3`; this supports deterministic square roots and is disclosed special modulus structure, not a claimed weakness
- sizes: 12, 14, and 16 field bits, with strictly increasing `q`
- seeds: 1473001 and 1473002
- factor base: smallest even `B` with `binomial(B+m-1,m)/q >= 0.5`
- relation shape: `m in {5,6,8}` factor-base points summing to a target
- baseline: matched random-scalar structure control, matched random-x construction control, scalar-progression control, corrected occupancy, and measured Pollard rho

## Metrics

- group operations: construction, split compilation, online query, witness recovery, and rho separated
- field operations: affine multiplications and inversions by phase
- memory: functional witness-map entries, CPython deep bytes, estimated traffic, and peak RSS
- relation probability: exact `|mA|/q` plus successes over 256 shared targets
- preprocessing diagnostic: `(S*T^2/(epsilon*q)) / (S_random*T_random^2/(epsilon_random*q))`, where `S` is functional advice deep bytes, `T` is average online group operations, and `epsilon=|mA|/q`
- rank: not applicable before a relation matrix exists
- solver degree: not applicable; no Groebner solver is used
- wall-clock: captured by the immutable run wrapper

## Positive control

A scalar progression should compress intermediate supports but lose final target coverage.

## Negative control

A uniformly sampled factor base at matched cardinality and sign mode.

## Success criterion

Require `>=0.8x` random-scalar exact support, `<=0.8x` matched-random functional-advice-byte `S*T^2/(epsilon*q)`, `<=4x` random-x offline work, replication in three instances across two sizes, and exact independent verification. The normalized diagnostic is implementation-specific and is not a calibrated generic preprocessing theorem.

## Falsification criterion

Narrow the hypothesis if no coordinate family meets the joint gate or any arithmetic/control invariant fails.

## Reproduction command

Protocol `v2` received an independent pre-run `GO` at commit `90ff031`, and coordinator approval is recorded in `specification.json`. Use the repository runner with the exact frozen arguments:

```bash
PYTHONPATH=src python3 -B -m crypto_autoresearcher.cli run \
  --experiment-dir experiments/EXP-ECDLP-RECURSIVE-001 \
  --run-id RUN-ECDLP-RECURSIVE-001 \
  --seed 1473001 \
  --timeout 900 \
  -- python3 -B experiments/EXP-ECDLP-RECURSIVE-001/src/recursive_expansion.py \
  --bit-sizes 12 14 16 \
  --seeds 1473001 1473002 \
  --m-values 5 6 8 \
  --targets 256 \
  --rho-trials 4 \
  --occupancy-lambda 0.5
```

Commit the first immutable run before launching the verifier so both manifests record clean Git states. Then capture the verifier as the second immutable run:

```bash
PYTHONPATH=src python3 -B -m crypto_autoresearcher.cli run \
  --experiment-dir experiments/EXP-ECDLP-RECURSIVE-001 \
  --run-id RUN-ECDLP-RECURSIVE-002 \
  --seed 1473001 \
  --timeout 900 \
  -- python3 -B experiments/EXP-ECDLP-RECURSIVE-001/src/verify_recursive_expansion.py \
  --input experiments/EXP-ECDLP-RECURSIVE-001/runs/RUN-ECDLP-RECURSIVE-001/raw-result.json
```

The generator emits both source hashes into `raw-result.json`; the run manifest hashes that artifact. The verifier independently recomputes and enforces the generator and imported arithmetic dependency hashes, then records the input artifact hash.

## Claim boundary

`TOY-EVIDENCE`, `HEURISTIC`, and `MODEL-BOUND`. A positive result would justify a source-tagged compiler experiment, not a faster-than-rho or deployed-curve claim.
