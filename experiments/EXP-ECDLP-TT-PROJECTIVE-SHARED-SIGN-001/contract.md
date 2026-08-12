# Experiment Contract: projective shared-sign source-state operator

## Hypothesis

For the source-derived suffix orbit predicate `h_Q(P,S)=g_Q(P+S)g_Q(P-S)`, a shared-Z Jacobian pair can eliminate generic source inversions. The resulting homogeneous predicate is the affine predicate multiplied by a nonzero source-state factor `Z^12`, so zero support and row-space reconstruction should be preserved while projective predicate costs are charged.

## Null hypothesis

Projective arithmetic either has an exceptional-case mismatch, fails the homogeneous-to-affine zero invariant, loses exact support/rank, or costs more after field multiplications, inversions, point additions, memory, and lift work are included.

## Parameters

- field/curve family: three fresh deterministic ordinary prime-field curves of approximately 14 bits
- seeds: `271828`, `161803`, `424242`
- dimensions: fixture progression `A=11`, factor base `B=10`, suffix pairs `B^2=100`, source orbit classes regenerated independently
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`
- budgets: `32`, `44`, `full` orbit classes
- source operator: specialized Jacobian `P+S` and `P-S` formulas sharing `H`, `J`, `V`, and `Z`; exact affine fallback when x coordinates coincide
- projective predicate: clear the affine norm denominator by `Z^6` per branch, yielding a `Z^12` source-state factor for the pair product
- comparators: same-fixture naive affine orbit quotient and original affine full predicate

## Metrics

- projective source multiplications, inversions, point additions, exceptional fallbacks, and shared-Z powers
- projective predicate multiplications and memory/cache bytes
- affine/projective zero-equivalence checks and homogeneous row reconstruction
- predicted entries, exact support, held-out support, rank, valid witnesses, and lift queries
- matched Pollard-rho group operations, wall time, CPU time, and peak RSS

## Positive control

Full projective budgets must match the affine comparator's lifted support exactly, with valid witnesses, held-out coverage, and matched rho certificates. Independent point reconstruction and homogeneous zero-equivalence checks must pass on regenerated source states, including identity, inverse, equal-x, and generic cases.

## Negative control

Every family and both sub-full budgets are retained. A source inversion reduction without zero-equivalence, row-rank, memory, lift, and point-add accounting is not a positive result. Any nonzero projective scaling factor must be shown source-state-only and target-independent.

## Success criterion

The projective operator is a scoped practical signal only if all full controls and independent arithmetic checks pass. A stronger result requires an accepted sub-full budget on all three fresh curves for at least one predeclared family, with a charged cost vector below both comparators under an explicit inversion-weight sensitivity table.

## Falsification criterion

Any projective reconstruction mismatch, zero-equivalence mismatch, target-dependent scaling, failed full control, rank loss, or no charged source-state advantage falsifies this hypothesis for the representation and size.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m crypto_autoresearcher run --allow-dirty \
  --experiment-dir experiments/EXP-ECDLP-TT-PROJECTIVE-SHARED-SIGN-001 \
  --run-id RUN-TT-PROJECTIVE-SHARED-SIGN-001 --seed 271828 -- \
  python3 experiments/EXP-ECDLP-TT-PROJECTIVE-SHARED-SIGN-001/src/run_projective_shared_sign_harness.py
```

## Claim boundary

This is toy-scale, fixed-curve, homogeneous-coordinate evidence. It does not claim a generic prime-field ECDLP break, an exponent improvement, deployed-key recovery, or cryptographic-scale superiority to Pollard rho.
