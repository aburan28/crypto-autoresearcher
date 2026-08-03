# Experiment Contract: source-aware compressed projective locator

## Hypothesis

A target-independent, stratified source-prefix selector can evaluate only one
half of the projective target rows while preserving more exact support and
relation rank than contiguous prefix truncation.

## Null hypothesis

The selected prefixes miss exact target support or rank in a way that makes the
query reduction unusable; any arithmetic advantage is only a sub-cost.

## Parameters

- field/curve family: generated ordinary prime-order prime-field curve
- seed: `86420`
- field size: 16-bit primary run; smaller smoke runs permitted
- families: `source_prf_x` candidate and `random_x` negative control
- generated targets: `3B+1 = 43`, plus up to four held-out targets
- orbit budgets: `96`, `full`
- prefix selector: source-derived diagonal order, first `ceil(0.5 * |A|^3)` prefixes
- successor selectors: interleaved diagonal order and deterministic
  source-hash-ranked and parity-balanced orders at the same prefix fraction
- target dependence: none; selection uses only public source indices
- run budget: up to 24 receipts, including implementation-audit failures and
  independent verifier attempts
- predicate: corrected shared-Z projective `P+S/P-S` norm predicate
- baseline: corrected streaming full-prefix locator and matched affine controls

## Metrics

- exact support and held-out coverage
- prefix queries and query fraction
- relation rank and witness validity
- projective field operations, source-cache reads, memory, and wall time
- weighted arithmetic cost, sparse matrix operations, target descent, and rho

## Positive control

The unselected corrected streaming locator remains the exact-support oracle on
the same fixture and target transcript.

## Negative control

The `random_x` family is retained, and the full-prefix oracle is compared to
the selected-prefix candidate. A candidate that loses support must remain a
scoped negative rather than being padded with oracle hits.

## Success criterion

The independent verifier confirms source-only selection, nonzero projective
counters, exact witness checks, and reports whether the selected candidate
preserves support, held-out coverage, and rank. A useful positive signal would
retain those gates at less than 0.5 of the source-prefix queries.

## Falsification criterion

Any target-dependent selection, verifier mismatch, invalid witness, missing
projective binding, or failure to retain exact support/rank falsifies the
compressed-locator hypothesis for this selector. The failed receipt remains
valuable evidence.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m crypto_autoresearcher run --allow-dirty \
  --experiment-dir experiments/EXP-ECDLP-TT-PROJECTIVE-COMPRESSED-LOCATOR-001 \
  --run-id RUN-TT-PROJECTIVE-COMPRESSED-LOCATOR-001 --seed 86420 -- \
  python3 experiments/EXP-ECDLP-TT-PROJECTIVE-COMPRESSED-LOCATOR-001/src/run_compressed_locator_harness.py
```

## Claim boundary

This is a one-curve toy selector experiment. It does not claim a generic
prime-field ECDLP break, an exponent improvement, fixed-curve preprocessing
advantage, or deployed-key recovery.
