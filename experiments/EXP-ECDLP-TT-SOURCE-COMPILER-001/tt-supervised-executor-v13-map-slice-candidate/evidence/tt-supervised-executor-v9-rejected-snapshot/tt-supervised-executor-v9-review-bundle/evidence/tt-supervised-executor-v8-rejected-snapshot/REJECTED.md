# Supervised Executor V8 Rejected Snapshot

## Decision

`NO-GO` | `NEGATIVE RESULT` | `MODEL-BOUND` | `ZERO-RUN`

V8 is rejected for schema implementation and campaign execution. The rejection
is specific to the supervised-executor model. It is not an ECDLP result and does
not support a cryptanalytic, scaling, or deployment claim.

## Frozen subject

The exact V8 review payloads are under `v8-frozen/`. Their original manifest is
`v8-frozen/SHA256SUMS`.

The exact V7 rejected evidence bytes are under `v7-rejected-evidence/`. Their
original manifest is `v7-rejected-evidence/SHA256SUMS`.

The original V7-to-V8 obligation handoff is preserved as
`supervised-executor-repair-handoff-v7.yaml`.

## Independent decisions

- Theory Agent: `NO-GO`; see `supervised-executor-v8-theory-review.md`.
- Red Team Agent: `NO-GO`; see `supervised-executor-v8-red-team-review.md`.
- Local post-freeze counterexample: confirmed; see
  `supervised-executor-v8-postfreeze-counterexamples.md`.

The local V8 `PASS` receipt and own-audit remain preserved as untrusted evidence,
not as acceptance evidence.

## Confirmed counterexample classes

1. A2 resource receipt binds an A0/A1-only measurement.
2. Composed traces chain record arrays but reseed source/context/post-state.
3. P1's modeled parent is not P0's actual modeled commit OID.
4. Unknown record types, payloads, producers, and normalized path aliases pass.
5. Sparse ordinal histories and cross-attempt identity drift pass.
6. Terminal labels can be substituted over the same generic failure terminal.
7. Candidate-produced alternate-ref CAS records pass.
8. Capability receipts are replayable and forgeable because they are not bound
   to descriptor, executable, attempt, phase, reservation, and launch identity.
9. Resource overlap completeness is asserted rather than derived.
10. Publication is not one self-contained, atomically pinned snapshot.

## Strongest valid statement

V8 supports a restricted local selector result over declared finite products.
It does not establish reachable workflow traces, a closed durable-record model,
exact Git history, exact per-attempt resource accounting, or capability closure.

## What remains open

A repaired closed-universe reducer may still support the intended executor
invariants. V9 must make every confirmed counterexample executable and reject it
before another implementation decision.

## Next concrete action

Implement and independently verify the obligations in
`supervised-executor-repair-handoff-v8.yaml` in a mutable V9 draft. Do not modify
this rejected snapshot and do not authorize a campaign from it.

