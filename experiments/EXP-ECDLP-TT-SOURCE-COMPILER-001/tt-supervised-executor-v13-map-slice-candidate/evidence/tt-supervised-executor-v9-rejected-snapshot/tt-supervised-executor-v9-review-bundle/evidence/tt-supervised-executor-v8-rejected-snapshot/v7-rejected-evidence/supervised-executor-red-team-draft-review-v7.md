# Supervised Executor V7 Draft Red Team Review

## Decision

`NO-GO` for schema readiness or freezing.

Status: `NEGATIVE RESULT`, `MODEL-BOUND`, `ZERO-RUN`. No files were modified
and no runtime, control campaign, or cryptanalytic experiment was executed.

## Audited Snapshot

```text
21f83d5277c4139a0ab664040f36260dc87a52dd18d0af03964dc9ed00d2fcf9  build_v7_design_artifacts.mjs
bd0f84065ab506b3b6b3d6875b23bfbe1f163d3d891c32eae8a47b8c8a08bf14  verify_v7_design_artifacts.mjs
63352437e1d8fd97affb9cd2e22d08ac8346ed39a62d388b5dd661bd5a5a4034  supervised-executor-control-matrix-v6.json
58a5f42b3a13bbc3ce6a767c3ad191d0c989c503bf9a0e012526300f03b090c6  supervised-executor-transition-matrix-v6.json
```

## Findings

### S0. C003 emits a self-invalidating E0 reservation

`phaseId()` defaults a source without `phase_mode` to `P0`. The special C003
action writes `phases/E0/reservation.json`, but its literal payload says
`phase: P0`. Feeding that post-universe directly to P001 yields
`EVIDENCE_E0_RESERVATION_MISSING`; the advertised
`C003 -> e0_private_map` edge does not compose.

C002 has the same root defect. Successor reservation defaults to P0 rather than
deriving the next phase from `last_committed_phase`, so it can target an
occupied or incorrect phase.

### S0. Recovery identity collapses to A1

E013 may reserve A2, but the attempt-admission source loses its concrete ordinal
and `attemptOrdinal()` defaults D002 to A1. The meter permits only A0 and A1,
and entry domains omit many legitimate intermediate consumed/next pairs.
Manually seeded A1-A32 records in the exhaustion control do not prove the
execution trace.

Removing the A1 start while retaining a stale A0 start also leaves D004
selectable because evidence requires any attempt-start, not the current ordinal.

### S1. Durable events remain caller-supplied labels

`SEC7-E0-GUARD-001` selects TE-L002 and claims
`LAUNCH_INTENT_DURABLE`, but its action delta is empty and its post-universe has
no launch-intent. AN001 and TE-L002 are not composed through the same literal
record universe; the event label is trusted as durability evidence.

### S1. R005 cannot retain a recoverable result

R005 requires `recoverable_result: not_applicable`. Inputs with `true` or
`false` select DEFAULT. Its reducer always emits a phase terminal and never a
phase-result. Recovery has no modeled path from a reaped recoverable result to
`RESULT_RETAINED`.

### S1. Durable-universe semantics are incomplete

State evidence does not require phase-result, phase-content, or phase-terminal
records. Removing the phase terminal from a source claiming
`TERMINAL_VALID_OUTCOME` still permits commit-intent creation. Counters also do
not enforce phase/path agreement or logical uniqueness, so the malformed
P0-in-E0 reservation still increments the evaluator-reservation counter.

### S1. The verifier misses action postconditions

The verifier does not independently reconstruct:

- post-state;
- action path and payload;
- exact append-only `post = observed union delta` preservation;
- logical uniqueness by phase; or
- event-to-record materialization.

Digest novelty is checked instead of unoccupied-path novelty, and post-universe
validation checks length rather than set equality. Shared copies of phase and
ordinal derivation, evidence matching, and resource arithmetic allow builder
bugs to self-confirm.

### S1. Git self-reference remains an enum

The self-cycle control changes a relation label; it does not inject an OID into
serialized intent bytes. Generated commit objects omit commit bytes, OID, tree,
parent, and intent digest. G005 also omits `ref_relation` after CAS is labelled
applied. The controls prove enum routing, not a byte-derived Git hash relation.

### S2. Routing contexts and rule overlap are ambiguous

All TN/TE live-transition rules declare `live_transition` while their source
schemas fix `evaluation_context: live_supervisor`. Meter products can match
both M001 and M010; priority silently resolves the overlap. No verifier gate
checks rule-context agreement or multiple matching rules.

### S2. Publication is vulnerable to a moving-file race

The builder writes and then re-reads artifacts to bind hashes. The verifier
also parses files and later re-reads them for report hashes. Concurrent
regeneration can therefore bind bytes other than the bytes executed or parsed.
The audited snapshot above was coherent, but the publication mechanism is not
atomic.

### S2. Resource arithmetic has no input-validity model

Negative observations, observations over cap, duplicate vertex IDs, unknown
edge endpoints, and malformed overlap graphs are not rejected. The memory
component sum is a declared conservative policy, not proof that the supplied
overlap graph is complete.

## Overclaim Corrections

- `complete durable record universe` means only a supplied self-contained array
  with partial linkage checks in V7.
- `action applied/post-state derived` means isolated action synthesis; composed
  traces are not verified.
- `maximum 1+32 starts` is a seeded boundary count, not an executable A2-A32
  trace.
- `self-excluding commit intent` is enum-tagged and not byte-derived.
- `totality` covers declared finite selection products, not reachable traces or
  unique matching.
- verifier `PASS` is shared-model internal consistency only.

## Required V8 Controls

1. Compose literal post-universes into each next context without reseeding.
2. Carry an exact admission ordinal and digest through E013, D002/D004,
   recovery, and meter finalization.
3. Require exact durable event receipts for every `*_durable` event.
4. Enforce record path/payload identity, logical uniqueness, and exact
   append-only set union.
5. Require phase-result, phase-content, and phase-terminal evidence at the
   corresponding states.
6. Reconstruct Git object bytes/OIDs and validate CAS parent/ref relations.
7. Reject context mismatches, overlapping selectors, and invalid resource
   domains independently.
8. Publish and verify one immutable input snapshot.

## Handoff: V7 Red Team NO-GO

### Claim or task

Adversarially test whether the V7 generated witnesses compose into the claimed
supervised-executor topology.

### Status

`NEGATIVE RESULT`.

### Assumptions

- Only the coherent hash snapshot above was assessed.
- No runtime or cryptanalytic claim was assessed.

### Evidence so far

- `TRACE-E0-01` fails because C003 writes a P0-labelled E0 reservation.
- `TRACE-REC-A2` fails because recovery identity collapses to A1.
- Multiple high-severity evidence and verifier omissions remain.

### Failure modes

- Actual kernel identity and operating-system enforcement remain outside the
  finite model.
- Git ref atomicity remains outside the label-based V7 controls.

### Next concrete action

Cut V8 and first close the composed `C003 -> P001` and
`E013(A2) -> D002 -> M002` traces with literal records and independent
postcondition checks.

### Artifact paths

- `research/tt-supervised-executor-v7-draft/`
- `research/supervised-executor-red-team-draft-review-v7.md`
