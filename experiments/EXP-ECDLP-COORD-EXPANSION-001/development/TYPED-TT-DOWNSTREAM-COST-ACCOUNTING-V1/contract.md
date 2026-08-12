# Experiment Contract: TYPED-TT-DOWNSTREAM-COST-ACCOUNTING-V1

## Hypothesis

The public typed `A+4R` fixture contains enough immutable information to independently rebuild its D3/D4 source advice, relation transcript, quotient linear solve, and held-out D4/R+D3 descent. A downstream ledger can therefore attach complete relation and target-coefficient costs to the streaming batch evaluator without treating inherited fixture counters as proof.

## Null hypothesis

The public records do not reproduce their own compiler, relation, matrix, or descent digests; the batched evaluator does not bind to the full relation/descent target set; or the downstream cost model omits a declared operation class.

## Parameters

- input: fresh seed `314159` fixture;
- curves: `p = 947`, `4027`, and `16267`;
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`;
- public source points: the frozen progression and factor-base records in the fixture;
- relation seed: `family.run_seed xor 0x13198A2E`;
- held-out seed: `family.run_seed xor 0x03707344`;
- candidate batch: the sealed diagonal full-batch receipt;
- negative control: the sealed lexicographic full-batch receipt.

## Metrics

- D3/D4 support entries, persistent bytes, builder bytes, and independent support-build operations;
- relation target generation, D4 lookup, incremental basis, and full quotient-solve operations;
- held-out target construction, D4 and R+D3 query operations, and coefficient-recovery arithmetic;
- quotient rank, relation/equation/solution digests, descent transcript digest, and verified-target count;
- candidate full-batch exactness and negative-control binding;
- hashes, rerun digest, and explicit separation of source-native versus typed-five downstream counters.

## Positive control

Independent regeneration must match every family’s frozen compiler digest, relation transcript and independent-equation digest, quotient solution/rank, and held-out descent transcript. The diagonal full batch must remain exact and direct-reference exact.

## Negative control

The linked lexicographic full batch must retain direct-reference arithmetic exactness while reproducing the schedule-sensitive adaptive failure.

## Success criterion

All 12 rows pass the independent verifier, all declared operation ledgers are present, all supported held-out targets verify, and the source-native and downstream ledgers remain separately labeled.

## Falsification criterion

Any digest mismatch, rank mismatch, relation or descent verification failure, missing operation class, or accidental mixed-cost promotion falsifies this accounting receipt. Passing the receipt does not establish an asymptotic improvement or a complete ECDLP attack.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_downstream_cost_accounting_preflight.py \
  development/TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1/RUN-001/raw-result.json \
  development/TYPED-TT-CIRCUIT-NATIVE-ACCOUNTING-V1/RUN-001/raw-result.json \
  development/TYPED-TT-STREAMING-BATCH-ACCOUNTING-V1/RUN-001/raw-result.json \
  development/TYPED-TT-STREAMING-BATCH-ACCOUNTING-V1/RUN-001/lexicographic.json \
  --families random_x source_prf_x x_interval rational_union
```

## Claim boundary

`OBSERVATION`, `TOY-EVIDENCE`, and `MODEL-BOUND`. This is an independent downstream accounting and binding result. It is not a generic prime-field ECDLP break, exponent claim, or cross-model cost comparison.
