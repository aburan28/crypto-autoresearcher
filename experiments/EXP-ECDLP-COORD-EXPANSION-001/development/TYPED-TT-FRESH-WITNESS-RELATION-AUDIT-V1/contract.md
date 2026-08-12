# Experiment Contract: TYPED-TT-FRESH-WITNESS-RELATION-AUDIT-V1

## Hypothesis

The source-native `A+4R` evaluator can emit fresh, independently verifiable witness-bearing relations without materializing the full `B^4` suffix table or scanning the full `A x B^4` tensor.

## Null hypothesis

Source-side witness validity does not reproduce typed `D4` support, or a bounded prefix scan cannot retain support and quotient rank without approaching the exhaustive tensor scan.

## Parameters

- input: fresh-seed fixture with `p = 947`, `4027`, and `16267`;
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`;
- relation stream: `family.run_seed xor 0x13198A2E`;
- target budget: `min(q-1, 4(B+1))`;
- candidate witness policy: first exact norm zero per `A` after the declared prefix/suffix order;
- positive control: full source-advice tensor scan;
- negative control: first prefix only;
- baseline: independently rebuilt typed `D4` support and quotient basis.

## Metrics

- witness validity and support equality;
- candidate and baseline quotient rank;
- candidate unique queries divided by `A x B^4`;
- source-advice, target, query, matrix, and solve operation ledgers;
- retained advice and materialized-advice sizes;
- rerun digests and independent verifier status.

## Success criterion

The full control reproduces all source witnesses and support, while the truncated control is visibly rank-deficient or support-incomplete. Every operation class and input hash must be sealed.

## Falsification criterion

Any witness mismatch, support mismatch in full mode, rerun digest mismatch, or missing cost class falsifies the receipt. A passing full scan is not evidence of a sub-exhaustive algorithm.

## Reproduction commands

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_fresh_witness_relation_audit.py \
  development/TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1/RUN-001/raw-result.json \
  --families random_x source_prf_x x_interval rational_union --mode full \
  --target-budget-factor 4

PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_fresh_witness_relation_audit.py \
  development/TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1/RUN-001/raw-result.json \
  --families random_x source_prf_x x_interval rational_union --mode truncated \
  --target-budget-factor 4

PYTHONDONTWRITEBYTECODE=1 python3 src/verify_typed_tt_fresh_witness_relation_audit.py \
  development/TYPED-TT-FRESH-WITNESS-RELATION-AUDIT-V1/RUN-001/raw-result.json \
  development/TYPED-TT-FRESH-WITNESS-RELATION-AUDIT-V1/RUN-001/truncated.json \
  development/TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1/RUN-001/raw-result.json \
  development/TYPED-TT-FRESH-WITNESS-RELATION-AUDIT-V1/RUN-001/verification.json
```

## Claim boundary

`OBSERVATION`, `TOY-EVIDENCE`, and `MODEL-BOUND`. This is a witness-generation and cost-boundary audit. It is not a generic prime-field ECDLP break, an exponent claim, or evidence that the exhaustive scan has been replaced.
