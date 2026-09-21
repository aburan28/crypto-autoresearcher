# Experiment Contract: shared-sign source-state operator

## Hypothesis

For the source-derived suffix orbit predicate `h_Q(P,S)=g_Q(P+S)g_Q(P-S)`, a paired affine addition primitive can compute the two sign branches with one field inversion and a shared source cache, reducing charged source-state work while preserving exact lifted support.

## Null hypothesis

The paired primitive is not exact on exceptional cases, its field-operation or memory cost does not beat the original full predicate or naive orbit quotient, or no meaningful class budget preserves support, held-out coverage, and rank.

## Parameters

- field/curve family: two fresh deterministic 14-bit ordinary prime-field curves
- dimensions: fixture progression `A=11`, factor base `B=10`, suffix pairs `B^2=100`, orbit classes `C=55`
- seeds: `271828`, `161803`
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`
- budgets: `32`, `44`, `full` orbit classes
- source operator: paired affine computation of `P+S` and `P-S` using one shared denominator inversion, with exact affine-addition fallback when x coordinates coincide
- baseline: committed naive source-orbit quotient and original full-predicate comparator on the same deterministic fixtures

## Metrics

- paired calls, generic fallback calls, inversions, field multiplications, point additions, source-cache entries/bytes, and lift queries
- predicted quotient entries, exact support, held-out support, candidate rank, full class rank, and valid witnesses
- matched Pollard-rho group operations
- wall time, CPU time, and peak RSS

## Positive control

The full class budget must reproduce materialized baseline support exactly, with valid witnesses, held-out support, and matched rho certificates. Equal-point, inverse-point, and identity suffix cases are explicit arithmetic controls for the paired primitive.

## Negative control

Both fresh curves and all four factor-base families use the same paired operator and class partition. A field-multiplication reduction without exact lift, rank, memory, and inversion accounting is not a positive result.

## Success criterion

The operator is a scoped practical improvement only if full-budget correctness passes and the charged paired source-state vector is strictly below both the naive orbit quotient and original full-predicate comparator in the declared field/inversion model. A sub-full budget must additionally pass exact support, held-out support, and full relation rank on both curves.

## Falsification criterion

Any arithmetic mismatch, failed full control, no strict sub-full gate, or no charged source-state improvement falsifies this hypothesis for this representation and size.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m crypto_autoresearcher run --allow-dirty \
  --experiment-dir experiments/EXP-ECDLP-TT-SHARED-SIGN-OPERATOR-001 \
  --run-id RUN-TT-SHARED-SIGN-OPERATOR-001 --seed 271828 -- \
  python3 experiments/EXP-ECDLP-TT-SHARED-SIGN-OPERATOR-001/src/run_shared_sign_replication_harness.py
```

## Claim boundary

This is toy-scale, fixed-curve, affine-coordinate evidence. It does not claim a generic prime-field ECDLP break, an exponent improvement, deployed-key recovery, or cryptographic-scale superiority to Pollard rho.
