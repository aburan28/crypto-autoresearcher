# Supervised Executor V8 Post-Freeze Counterexamples

## Status

`NEGATIVE RESULT` | `MODEL-BOUND` | `ZERO-RUN`

V8 is `NO-GO` for implementation and campaign execution. This result rejects the
V8 supervised-executor specification and its local verifier; it is not an ECDLP
algorithm result and does not authorize any experiment run.

## Frozen subject

The counterexample was reproduced against the immutable review bundle at:

`/Volumes/Volume/autolab/research/tt-supervised-executor-v8-review-bundle`

Relevant frozen hashes:

```text
f3d1b96578c5322a7f391bf612b227eb0458e320591d2edd0dce8769c55331da  build_v8_design_artifacts.mjs
5e8089c9e0264d5aa24bc3751cecc2ed5a44fa78a81bf50d16c7cec82c548d87  verify_v8_design_artifacts.mjs
6883c450d01dd01287f0789079d87bc97720e0cd388f9812e2dd2ed6191ea17c  supervised-executor-contract-v8.md
2952bc3c3792eb3d43a4563ab4c6b7afa20922c0846a2a44f8b854bf873d2383  supervised-executor-transition-matrix-v7.json
738ce578162ba70855fe704623cd73dbbf3454b1741fd29aa7bf32b8ad54f8f6  supervised-executor-control-matrix-v7.json
42a4144c1819b6bcf7bcd4b126ce00d60a8029d671929657312544fcf0f07b1a  local-verification-v8.json
0287b1519a48a5f853b0f54e0c14e703d3d4ca9cd3b9836ecf034aa795014ed5  supervised-executor-v8-own-audit.md
```

## Counterexample V8-CE-001: A2 receipt binds an A0/A1-only measurement

### Claim or task

Test whether the composed recovery trace binds the meter receipt for the exact
current admitted ordinal to a resource measurement that includes that ordinal.

### Assumptions

- The frozen control matrix is the authoritative V8 generated artifact.
- A resource receipt for ordinal `Ak` must be backed by a measurement whose
  measured-attempt set contains `Ak`.
- Digest equality proves byte binding, not semantic coverage.

### Reproduction

Run from the frozen review bundle:

```bash
node -e 'const c=require("./supervised-executor-control-matrix-v7.json"); const t=c.controls.find(x=>x.id==="SEC8-TRACE-REC-A2").fixture; const m=t.observation_boundaries[0].observation_record_delta.find(r=>r.record_type==="resource_measurement"); const q=t.steps.at(-1).fixture.action_record_delta.find(r=>r.record_type==="resource_receipt"); console.log(JSON.stringify({receiptOrdinal:q.payload.ordinal,measurementAttemptIds:m.payload.input.attempts.map(x=>x.id),receiptBindsMeasurement:q.payload.measurement_sha256===m.sha256,omitsReceiptOrdinal:!m.payload.input.attempts.some(x=>x.id===q.payload.ordinal)}))'
```

Observed output:

```json
{"receiptOrdinal":"A2","measurementAttemptIds":["A0","A1"],"receiptBindsMeasurement":true,"omitsReceiptOrdinal":true}
```

### Evidence

- Trace: `SEC8-TRACE-REC-A2`.
- Receipt ordinal: `A2`.
- Measurement attempt identifiers: `A0`, `A1`.
- The receipt correctly binds the measurement SHA-256.
- The bound measurement omits the receipt ordinal.
- The frozen local verifier nevertheless reports `PASS` with 180 checks.

### Failure mode

The builder reused a global resource fixture in a later recovery attempt. The
verifier reconstructed and authenticated the same fixture, so it checked shared
structure and hashes but not the cross-record invariant:

```text
resource_receipt.ordinal is an element of resource_measurement.input.attempts[*].id
```

This is a builder/verifier common-mode semantic omission. It falsifies V8's
resource-accounting closure for recovery attempts and shows that the 180-check
local `PASS` is insufficient for admission.

### Narrowest valid conclusion

V8 does not prove exact per-attempt resource accounting across recovery. This
counterexample does not show that the overall supervised-executor design is
unrepairable, and it says nothing about ECDLP complexity or cryptanalytic value.

### V9 repair obligation

1. Derive the measured-attempt set from the exact admitted attempt records for
   each composed trace; do not inject a shared fixture.
2. Require the current receipt ordinal and attempt identity to occur exactly
   once in the bound measurement input.
3. Reject missing, duplicate, future, or unrelated measured attempts.
4. Add an executable mutation that replaces an A2 measurement with a validly
   hashed A0/A1-only measurement and require rejection.
5. Make an independent verifier reconstruct this invariant from literal records,
   not from builder-supplied summary fields.

## Additional proof obligations under audit

These are not promoted to counterexamples by this note. V9 must independently
test whether V8 merely asserted rather than derived:

- the last phase outcome from the exact terminal and committed Git content;
- exact Git ref-name equality across intent, observation, and CAS records;
- reservation, admission, and capability bindings from literal records.

## Handoff: cut V9

### Status

`OPEN`

### Failure modes

- Repairing only the A2 fixture can leave other assertion-only fields intact.
- Reusing the V8 verifier architecture can reproduce the same common-mode gap.
- Modifying the frozen V8 bundle would destroy the evidence boundary.

### Next concrete action

Create a mutable V9 draft from copies of the frozen V8 inputs, add all confirmed
independent-review objections as explicit obligations, and implement the smallest
falsifying controls before any implementation or campaign authorization.

### Artifact paths

- `/Volumes/Volume/autolab/research/tt-supervised-executor-v8-review-bundle`
- `/Volumes/Volume/autolab/research/supervised-executor-v8-postfreeze-counterexamples.md`
