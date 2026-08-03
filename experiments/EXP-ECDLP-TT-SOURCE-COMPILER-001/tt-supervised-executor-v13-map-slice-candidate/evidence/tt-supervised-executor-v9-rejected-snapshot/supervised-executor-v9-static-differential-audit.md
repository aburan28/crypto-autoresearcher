# Supervised Executor V9 Static Differential Audit

## Status

`OBSERVATION` | `MODEL-BOUND` | `ZERO-RUN` | `INDEPENDENT-REVIEW-PENDING`

This audit compares the frozen V9 builder and independent verifier. It does not
modify the frozen review bundle or authorize implementation/campaign execution.

## Frozen Root

```text
b5426daa7d9ebf66db356ae2080780712e8318f03bec04c37d12b45580bd2b1c  tt-supervised-executor-v9-review-bundle/SHA256SUMS
```

## Executable Finding

The unchanged independent verifier accepts a fully rehashed A2 trace whose
`recalculation_receipt` binds a nonexistent campaign-terminal digest and a
fabricated resource-total digest. The lock release, M008/M009 journal receipts,
and final roots were all relinked. The verifier returned `PASS` with 132 checks
and 26/26 stored regressions.

It also accepts an isolated mutation that changes only the final A2 action
receipt's `schema` literal, rehashes that receipt, and updates the final journal
and universe roots. That run also returned `PASS` with all 132 checks and all 26
stored regressions.

Artifacts:

- `tt-supervised-executor-v9-counterexample-a2-work/mutate_recalculation_a2.mjs`
- `tt-supervised-executor-v9-counterexample-a2-work/counterexample-summary.json`
- accepted receipt SHA-256:
  `4890ae3c9f7dc8836f6e4fb8eb60a7ddf3cf4bab7a712fe2ae78922af9a0ef1a`
- `tt-supervised-executor-v9-counterexample-schema-work/mutate_final_journal_schema_a2.mjs`
- schema-mutated artifact SHA-256:
  `e0bb1e384978f0e09dfc6bc9a36becac0dccfb54013144b0b7642f6a9282daac`
- schema-mutation accepted receipt SHA-256:
  `2ec2e96b610ba64fddef519ada7740acf8f31d0508cf37c0227e5afcd1f9ffa8`

## Direct Differential

The builder enforces recalculation and lock-release linkage at lines 669-676 of
`build_v9_closed_kernel.mjs`. The verifier's `semanticAudit` returns at line 432
of `verify_v9_closed_kernel.mjs` after campaign-terminal validation and contains
neither loop.

Builder-only semantic rejection codes found by static comparison include:

```text
ATTEMPT_END_OUTCOME_INVALID
LAUNCH_PRIVATE_MAP_MISMATCH
LAUNCH_PRIVATE_MAP_UNEXPECTED
LOCK_RELEASE_LINKAGE_MISMATCH
RECALCULATION_LINKAGE_MISMATCH
RECORD_SCHEMA_MISMATCH
RESOURCE_OBSERVATION_INVALID
RESOURCE_POLICY_INVALID
RESOURCE_RECEIPT_MEASUREMENT_MISMATCH
```

Some additional builder-only codes describe action construction or use a
different verifier name and are not automatically defects. The nine above name
semantic predicates visibly absent or weaker in the verifier:

- record `schema` is never checked against `tt-supervised-record-v3`;
- the exact resource-policy object is not checked;
- observed resource values are not checked to be integers within their caps;
- a resource receipt is not required to copy the linked measurement input/result;
- attempt-end outcomes are not restricted to the closed vocabulary;
- E0 launch is not bound to its private-map receipt, and non-E0 launches are not
  required to carry `null`;
- recalculation is not bound to campaign terminal or measurement totals;
- lock release is not semantically validated by the independent verifier.

## Claim Impact

If independently reproduced, this is a `NO-GO` for V9 schema/control
implementation. It falsifies `V9-DIFFERENTIAL-01` and narrows the strongest valid
V9 result to the two generated happy-path universes plus the stored mutation
set. It does not invalidate the selector partition or establish any ECDLP claim.

## V10 Repair Shape

V10 should not patch only the observed recalculation fields. It needs:

1. an explicit predicate-parity inventory covering every builder semantic check;
2. an independently authored verifier predicate for every inventory row;
3. fully rehashed negative controls for each closure/identity predicate;
4. a differential harness that fails if either side accepts a universe the other
   rejects, apart from preregistered constructor-only checks;
5. a new portable freeze and fresh independent decisions.

## Next Concrete Action

Obtain independent Theory and Red Team reproduction, then preserve V9 as a
rejected snapshot and issue a V10 repair handoff covering the full predicate
differential rather than the first counterexample alone.
