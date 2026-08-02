# Supervised Executor V8 Local Adversarial Audit

## Handoff: V8 local Gate A result

### Claim or task

Determine whether the mutable V8 design artifacts satisfy the 18 rejected-V7
repair obligations well enough to create an immutable bundle for fresh review.

### Status

OBSERVATION, MODEL-BOUND, ZERO-RUN, NOVELTY-UNVERIFIED.

This is not implementation authorization, campaign authorization, an ECDLP
result, or a cryptanalytic performance claim.

### Assumptions

- The finite source products cover the statuses named by the design contract.
- Canonical record, process-identity, capability, and Git operations remain
  models until a separately reviewed implementation exists.
- No candidate or evaluator campaign has run.

### Evidence so far

- Two consecutive complete builder runs reproduced exactly:
  - transition SHA-256
    `2952bc3c3792eb3d43a4563ab4c6b7afa20922c0846a2a44f8b854bf873d2383`;
  - control SHA-256
    `738ce578162ba70855fe704623cd73dbbf3454b1741fd29aa7bf32b8ad54f8f6`.
- The independent verifier returned `PASS` over 1,584,249 source products,
  228 controls, four verifier mutations, and 180 checks. Receipt SHA-256:
  `42a4144c1819b6bcf7bcd4b126ce00d60a8029d671929657312544fcf0f07b1a`.
- All six startup byte snapshots named by the verifier receipt still match its
  recorded lengths and SHA-256 values.
- A separate inventory found no Git write outside `repository_validation`.
- All 62 live-event controls contain a non-null exact event receipt.
- The literal recovery trace selects E013, D002, D004, and M002 with A2 action
  records at admission, start, and resource-receipt publication.
- None of the 168 E0 projection rows is a schema rejection.
- All 18 repair-obligation IDs are present and every authorization flag remains
  false.

### Failure modes

- Closed finite products do not prove that an implementation emits the modeled
  source state or enforces operating-system capabilities correctly.
- The builder and verifier are separately coded but share the same written
  contract and may share a conceptual omission.
- Git ref atomicity, kernel process identity, filesystem durability, and private
  map isolation remain outside this executable design model.
- A composed toy witness does not establish runtime crash safety.
- Passing this audit says nothing about the target-blind ECDLP hypothesis or a
  sub-square-root algorithm.

### Next concrete action

Freeze the exact V8 files and request fresh read-only Theory and Red Team
decisions against only the frozen hashes. Any counterexample creates V9; do not
implement schemas or launch the 29-mutation campaign on a `NO-GO`.

### Artifact paths

- `research/tt-supervised-executor-v8-draft/build_v8_design_artifacts.mjs`
- `research/tt-supervised-executor-v8-draft/verify_v8_design_artifacts.mjs`
- `research/tt-supervised-executor-v8-draft/supervised-executor-contract-v8.md`
- `research/tt-supervised-executor-v8-draft/supervised-executor-topology-decision-v7.md`
- `research/tt-supervised-executor-v8-draft/supervised-executor-transition-matrix-v7.json`
- `research/tt-supervised-executor-v8-draft/supervised-executor-control-matrix-v7.json`
- `research/tt-supervised-executor-v8-draft/local-verification-v8.json`
