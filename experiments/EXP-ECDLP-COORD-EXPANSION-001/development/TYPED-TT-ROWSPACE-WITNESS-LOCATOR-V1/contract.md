# Experiment Contract: TYPED-TT-ROWSPACE-WITNESS-LOCATOR-V1

## Hypothesis

An adaptive cut-3 row-space basis for the target-conditioned five-term norm predicate can be reused across many public targets, producing exact source witnesses with fewer source-side point evaluations than rebuilding the basis for every target.

## Null hypotheses

- A basis built for one target fails to preserve the zero-support witness set for later targets.
- Any source-query saving disappears after row-space construction, witness replay, suffix reconstruction, relation filtering, and baseline costs are charged.

## Three research tracks

1. Conservative extension: stream source advice and use an adaptive dependent-prefix basis to reduce repeated source point additions.
2. Representation change: reuse the first target's cut-3 cross basis as a fixed-curve target-parametric representation.
3. High-risk successor: replace exhaustive suffix reconstruction with an algebraic zero locator over the compressed suffix operator.

## Parameters

- input: fresh-seed fixture with `p = 947`, `4027`, and `16267`;
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`;
- target stream: `family.run_seed xor 0x13198A2E`;
- targets: `B+1` nonzero targets per row;
- row-space construction: adaptive dependent-prefix plateau;
- positive mode: rebuild a target-conditioned basis per target;
- reuse mode: build one basis from the first target and reuse it for all targets;
- baseline: independently materialized typed D4 support and query.

## Metrics

- source-advice, target, row-space, reconstruction, witness, relation, and solve operation ledgers;
- source-query fraction of the full `A x B^4` tensor;
- predicted suffix entries, retained advice, materialized D4 advice, and peak source work;
- candidate witness validity, zero-support equality, quotient rank, and held-out target count;
- reuse-versus-per-target source-query savings and matched D4 group-operation cost.

## Success criterion

The reuse mode must reproduce the typed-D4 zero-support set and independently valid witnesses on every row, use no more source queries than per-target construction, and preserve explicit accounting for exhaustive suffix reconstruction.

## Falsification criterion

Any support mismatch, invalid witness, rerun digest mismatch, reuse query regression, or mixed cost ledger falsifies the receipt. A passing receipt does not establish a sub-square-root locator or an ECDLP improvement.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_rowspace_witness_locator.py \
  development/TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1/RUN-001/raw-result.json \
  --families random_x source_prf_x x_interval rational_union \
  --mode per_target --target-budget-factor 1

PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_rowspace_witness_locator.py \
  development/TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1/RUN-001/raw-result.json \
  --families random_x source_prf_x x_interval rational_union \
  --mode reuse --target-budget-factor 1

PYTHONDONTWRITEBYTECODE=1 python3 src/verify_typed_tt_rowspace_witness_locator.py \
  development/TYPED-TT-ROWSPACE-WITNESS-LOCATOR-V1/RUN-001/per-target.json \
  development/TYPED-TT-ROWSPACE-WITNESS-LOCATOR-V1/RUN-001/reuse.json \
  development/TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1/RUN-001/raw-result.json \
  development/TYPED-TT-ROWSPACE-WITNESS-LOCATOR-V1/RUN-001/verification.json
```

## Claim boundary

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`. This is a fixed-curve target-reuse and representation experiment. It is not a generic prime-field ECDLP break, exponent claim, or net win over materialized D4 or Pollard rho.
