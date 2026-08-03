# Experiment Contract: TYPED-TT-ROWSPACE-SCALE-PROBE-V1

## Hypothesis

The target-independent cut-3 row-space signal remains visible on a larger ordinary prime-field fixture without requiring a full suffix reconstruction.

## Null hypothesis

A bounded prefix budget either fails to reach a stable row-space rank or produces sampled reconstruction mismatches on fresh targets. Such a result is a scoped construction negative, not evidence against all row-space or transposed operators.

## Parameters

- generated fixture: one 16-bit ordinary prime-order curve, `p=63311`, `q=63199`;
- source sizes: `A=14`, `B=14`;
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`;
- target stream: `family.run_seed xor 0x13198A2E`;
- targets: `B+1=15` per family;
- prefix budget: `64` rows, with budget controls `16`, `32`, and `64` on `random_x`;
- sampled suffix columns: `4/196` per prefix;
- validation: direct source-advice values on the sampled entries only.

## Metrics

- discovered rank and stopping reason;
- sampled mismatches and sampled-entry fraction;
- source query and point-add work;
- retained advice and row-space construction counters;
- immutable fixture, producer, and rerun digests.

## Success criterion

The probe must finish under the prefix bound, preserve exact sampled predictions where the bounded basis is sufficient, and expose any family-specific mismatch rather than silently treating the partial basis as complete.

## Falsification criterion

Any digest mismatch, missing prefix-bound receipt, or hidden full-tensor validation falsifies the probe. A sampled match does not establish full support, relation rank, target descent, or an ECDLP improvement.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_rowspace_scale_probe.py \
  development/TYPED-TT-ROWSPACE-SCALE-PROBE-V1/RUN-001/input-fixture.json \
  --families random_x source_prf_x x_interval rational_union \
  --sample-limit 4 --target-budget-factor 1 --max-prefixes 64

PYTHONDONTWRITEBYTECODE=1 python3 src/verify_typed_tt_rowspace_scale_probe.py \
  development/TYPED-TT-ROWSPACE-SCALE-PROBE-V1/RUN-001/raw-result.json \
  development/TYPED-TT-ROWSPACE-SCALE-PROBE-V1/RUN-001/verification.json
```

## Claim boundary

`OBSERVATION`, `TOY-EVIDENCE`, and `MODEL-BOUND`. This is a bounded larger-dimension construction probe. It makes no full-support, relation, descent, exponent, or generic ECDLP claim.
