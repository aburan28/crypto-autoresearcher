# Supervised Executor V7 Draft Theory Review

## Decision

`NO-GO` for freezing V7.

Status: `NEGATIVE RESULT`, scoped to the mutable V7 design draft. This review
does not assess a runtime implementation, campaign execution, or any
cryptanalytic claim.

The reviewer first observed a transient transition artifact with hash prefix
`ae9b4012` and 2,340 local checks. The draft changed during review, so that
transient artifact was not a valid frozen review target. The findings below
were subsequently reproduced against this later local snapshot:

```text
5b99597a800a3034cf7f42da6114fda5c91d0d87657ce4597ca6592caca31de7  supervised-executor-contract-v7.md
6d279ce26c44bfbf6319b3f8968e75bc68b16e96b9e1eadfe12c6a2bdbbfc2de  supervised-executor-topology-decision-v6.md
58a5f42b3a13bbc3ce6a767c3ad191d0c989c503bf9a0e012526300f03b090c6  supervised-executor-transition-matrix-v6.json
63352437e1d8fd97affb9cd2e22d08ac8346ed39a62d388b5dd661bd5a5a4034  supervised-executor-control-matrix-v6.json
21f83d5277c4139a0ab664040f36260dc87a52dd18d0af03964dc9ed00d2fcf9  build_v7_design_artifacts.mjs
bd0f84065ab506b3b6b3d6875b23bfbe1f163d3d891c32eae8a47b8c8a08bf14  verify_v7_design_artifacts.mjs
```

## Counterexamples

### 1. Recovery ordinals collapse to A1

The contract permits every integer `0 <= k <= 32` and recovery ordinals
`A1..Ak`. The source domains instantiate only `k in {0,2,32}`, while
`meter_finalization_v2` admits only `A0` and `A1`. The attempt-admission source
does not carry the concrete admission ordinal, and the reducer defaults a
recovery without `next_recovery_ordinal` to `A1`. A valid `A2` admission can
therefore be created but cannot receive its linked start or meter closure.

### 2. Attempt-start evidence is not ordinal-specific

For `linked_attempt_record = durable`, evidence validation accepts any
`attempt_start` record in the universe. A recovery source for `A1` with only an
old `A0` start can select `D004` and dispatch without an `A1` start.

### 3. Prior-process identity is assertion-only

`S001` accepts symbolic `launch_identity_evidence = complete`, but evidence
validation does not require a corresponding durable launch-identity record.
An empty identity universe plus asserted kernel absence reaches meter
finalization.

### 4. E0 failure continuation is not executable

`P003` writes the map-open failure terminal and remains in `e0_private_map`.
Its state patch does not change the event to the `P006` dispatch event, so no
ordinary edge reaches the promised E0 commit path. The terminal payload also
contains only a generic reason and omits the bounded syscall-error evidence
required by the contract.

### 5. Git authority leaks into other contexts

`AN010I`, `AN010E`, `R012I`, and `R012E` execute CAS directly from
`live_supervisor` or `recovery_reconstruction`, bypassing the topology's
exclusive `repository_validation` authority. Separately, `G005` omits
`ref_relation`; an exact object with `ref_relation = other` and
`cas_status = applied` can progress successfully.

### 6. Capability closure omits the descriptor schema value

The descriptor contains 27 fields, but only 26 field validators and denial
controls exist. The `schema` key is present yet its value is unchecked. A
mutation from `candidate_boundary_descriptor_v2` to another value retains the
same key set and is accepted by the builder validator.

### 7. Resource arithmetic accepts invalid domains

The fixed arithmetic `52/73/85/24/12` is reproduced, but the evaluator has no
closed input schema, type checks, nonnegative checks, safe-integer checks,
unique vertex checks, or overlap-edge endpoint checks. For example,
`A0.bootstrap_observed = -100` produces and accepts a negative CPU charge.

### 8. Resource arithmetic is not bound to the durable meter receipt

The numeric fixture and its derived result are separate from the
`resource_receipt` emitted by meter finalization. The design therefore does not
prove that the exact charged arithmetic is what the durable campaign record
commits to.

## Model Boundary

Actual kernel process identity, operating-system capability enforcement,
syscall-to-record crash behavior, and Git ref/receipt atomicity remain outside
the finite design model.

## Handoff: V7 Theory NO-GO

### Claim or task

Determine whether V7 is internally sufficient to freeze for independent
implementation-authority review.

### Status

`NEGATIVE RESULT`.

### Assumptions

- Only design artifacts and generated controls were assessed.
- No runtime or campaign was executed.
- The later hash snapshot above was used to reproduce each live finding.

### Evidence so far

- Eight concrete counterexamples remain reproducible.
- Local verifier success does not cover these omitted transitions and domains.

### Failure modes

- This was a moving-draft review, not a hash-stable frozen review.
- Passing a repaired local verifier would still require fresh independent
  review.

### Next concrete action

Preserve V7 as rejected draft evidence and cut a versioned V8 repair containing
executable rejection or progression controls for all eight counterexamples.

### Artifact paths

- `research/tt-supervised-executor-v7-draft/`
- `research/supervised-executor-theory-draft-review-v7.md`
