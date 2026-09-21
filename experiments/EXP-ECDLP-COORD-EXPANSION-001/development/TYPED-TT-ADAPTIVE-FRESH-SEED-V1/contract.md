# Experiment Contract: TYPED-TT-ADAPTIVE-FRESH-SEED-V1

## Hypothesis

The adaptive dependent-prefix plateau rule will discover an exact cut-3 tensor skeleton on fresh ordinary prime-field curves, without an imported rank budget.

## Null hypothesis

Fresh curves or any of the four public factor-base families produce a delayed independent prefix, premature stopping, target mismatch, or construction counter mismatch.

## Parameters

- fixture seed: `314159`;
- field sizes: 10, 12, and 14 bits;
- curves: p = 947, 4027, and 16267;
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`;
- cut: `(A,R0,R1)|(R2,R3)`;
- stop rule: `max(4, floor(B/2))` dependent prefix fibers;
- targets: first eight relation targets plus first held-out target;
- validation: full tensor replay, separately charged.

## Metrics

- discovered rank and prefix fibers examined;
- construction and specialization query counts;
- full validation mismatches;
- field operation counters and wall time;
- source hash, input hash, and verifier rerun digest.

## Positive control

The diagonal-first adaptive schedule on the fresh fixture.

## Negative control

The separate adversarial order experiment uses lexicographic and reverse-lexicographic prefix schedules.

## Success criterion

All 12 fresh rows stop adaptively, match construction counters, and reconstruct all relation and held-out targets exactly.

## Falsification criterion

Any row with a mismatch, rank instability, full-prefix scan, or counter disagreement falsifies fresh-seed replication for that row.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_adaptive_skeleton_preflight.py \
  development/TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1/RUN-001/raw-result.json \
  --families random_x source_prf_x x_interval rational_union
```

## Claim boundary

`OBSERVATION`, `TOY-EVIDENCE`, and `MODEL-BOUND`. This is a fresh tensor-skeleton replication, not a generic ECDLP algorithm or break.
