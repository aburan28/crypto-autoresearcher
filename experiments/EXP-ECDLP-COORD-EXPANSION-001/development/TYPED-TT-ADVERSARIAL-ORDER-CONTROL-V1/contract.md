# Experiment Contract: TYPED-TT-ADVERSARIAL-ORDER-CONTROL-V1

## Hypothesis

If the adaptive skeleton reflects source structure rather than an enumeration artifact, alternate prefix schedules should preserve exactness or expose the precise schedule dependency.

## Null hypothesis

Alternate schedules stop at a smaller apparent rank and fail full validation.

## Parameters

- input: fresh seed 314159 fixture;
- rows: 12, using the same four families and three curves;
- controls: lexicographic and reverse-lexicographic prefix order;
- stop rule and cut: identical to the adaptive fresh-seed run;
- validation: full tensor replay.

## Metrics

- apparent rank and examined prefixes;
- exact validation status and mismatch counts;
- query counters and rerun digest.

## Positive control

The diagonal-first fresh-seed receipt is the positive schedule control.

## Negative control

Each alternate order is expected to expose premature stopping if diagonal source alignment is essential.

## Success criterion

The receipt is valid if the control outcome, including failure or success, is reproducible and no failure is mislabeled as an attack success.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_adversarial_order_control_preflight.py \
  development/TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1/RUN-001/raw-result.json \
  --families random_x source_prf_x x_interval rational_union \
  --order lexicographic
```

## Claim boundary

This is a schedule-control experiment. A failed control is a scoped negative result about that order and stopping rule, not a theorem about ECDLP.
