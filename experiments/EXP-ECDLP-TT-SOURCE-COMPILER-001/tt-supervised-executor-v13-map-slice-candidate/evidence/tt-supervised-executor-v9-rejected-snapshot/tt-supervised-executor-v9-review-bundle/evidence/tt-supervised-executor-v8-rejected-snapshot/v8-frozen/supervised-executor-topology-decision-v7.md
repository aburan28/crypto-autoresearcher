# TT Supervised Executor Topology Decision V7

## Status and Decision

`HYPOTHESIS`, `MODEL-BOUND`, `UNTESTED`, `ZERO-RUN`.

Decision: retain one lock-owning external meter and one bootstrap, and repair
the rejected V7 witness design with exact A0-A32 identity flow, literal event
receipts, composed traces, repository-only Git writes, and byte-stable
publication.

No implementation, control execution, campaign execution, or cryptanalytic
claim is authorized.

## Process Topology

```text
approval-bound invocation
-> external meter acquires campaign lock
-> entry_preflight
   -> prior_attempt_safety, when needed
   -> attempt_admission, when eligible or resuming a token
-> bootstrap/dispatcher
   -> campaign_progression
   -> live_supervisor and live_transition
   -> repository_validation
   -> recovery_reconstruction after a root crash
   -> e0_private_map only for E0 evaluate
-> meter_finalization after bootstrap reap and exact process absence
-> read-only recalculation
-> lock release
```

The meter and bootstrap may hold duplicated descriptors for the same kernel
lock. Candidate and evaluator children receive none. The lock remains held while
any exact attempt process identity is live or absence is unproved.

## Context Ownership

| Context | Reads | Durable-write authority | Exit |
|---|---|---|---|
| `entry_preflight` | lock, terminal, prior-attempt class, admission class, eligibility | bounded admission only | reject, safety, or admission |
| `attempt_admission` | current token and linked start | one linked attempt-start | progression or recovery |
| `prior_attempt_safety` | fixed precedence reason, exact launch/process identity | none | retain lock or meter handoff |
| `campaign_progression` | committed phase chain | one next-phase reservation or terminal request | live, E0 map, or meter |
| `live_supervisor` | one closed phase state | one phase action at a time | live transition or progression |
| `live_transition` | one closed event product | none | live or recovery |
| `recovery_reconstruction` | one valid recovery admission and crash residue | one replay/recovery phase action | live or progression |
| `repository_validation` | commit intent/object/ref/CAS relation | one Git action at a time | live or infrastructure request |
| `e0_private_map` | trusted E0 reservation and private-map state | one intent, receipt, or failure terminal | E0 live or recovery |
| `meter_finalization` | process absence, resources, end, request, terminal | one resource/end/terminal record per stage | recalculation and release |

Contexts are pairwise disjoint. A source schema fixes its context, and a rule
cannot dispatch itself through a differently named context.

## Admission Topology

V8 retains the bounded token before attempt-start and carries its exact ordinal
and digest through every later context:

```text
eligible normal   -> create A0 admission/consumption -> create A0 start
eligible recovery -> create next Aj recovery token   -> create Aj start
```

Only after the linked start is durable may the root inspect or mutate repository
or phase state.

Crash recovery is idempotent:

```text
token absent, start absent  -> eligibility may reserve one bounded token
token durable, start absent -> resume the same token and write one start
token durable, start durable -> dispatch; never add another start
start durable, end absent   -> prior-attempt safety and meter closure
end durable                 -> a later recovery may reserve the next token
```

The record universe enforces one admission and one start per ordinal. Approval
maximums 0, 2, and 32 have materialized exhaustion witnesses, while the
composed A2 trace executes E013, D002, D004, an external meter-observation
boundary, and M002 over literal predecessor universes.

## Prior-Attempt Safety Topology

Entry fixes terminal and prior-attempt precedence before lower campaign reads.
The safety handoff receives only:

- the immutable selected reason;
- exact launch-identity evidence; and
- kernel process-absence status.

It cannot inspect repository, phase, candidate, or evaluator semantics. Exact
absence permits meter handoff. Live identity permits exact reconciliation.
Anything ambiguous retains the lock and writes no terminal.

## Candidate and Evaluator Topology

P0-P5 each permit at most one candidate process. A candidate receives only:

- the exact approved executable image;
- fixed public argv and environment;
- public input and candidate work roots;
- descriptors 0, 1, and 2; and
- a current launch-barrier receipt.

Network, fork, later exec, IPC, debugger, task port, ptrace, private labels, and
private roots are denied. Path resolution stays beneath approved roots without
symlinks, magic links, or cross-device traversal; private mounts and unlisted
directory descriptors are absent. The syscall, resource-limit, and signal
profiles are exact. Every denial has a materialized negative transform.

E0 is trusted and is not counted as a candidate run. In evaluate mode, E0 enters
the private-map context before launch. The map receipt and reservation binding
are required fields in the later live action and event products. Closure mode
never enters or opens the private map.

## E0 Topology

```text
E0 reservation
-> private-map open intent durable
-> trusted open syscall
   -> failure: one E0 harness-failure terminal -> commit intent, no evaluator launch
   -> success: trusted descriptor, not inherited
-> private-map opened receipt durable
-> E0 launch intent
-> normal phase/Git progression
```

The event projection has 168 cases across run mode, E0 mode, map state, and
event, with canonical descriptor state shown in each row. Symbolic totality
separately enumerates all descriptor states and A0-A32 identities for 22,176
closed source products.
Root crash at every evaluate map state hands off to recovery or the closed
default. Any map event in closure mode requests infrastructure failure.

## Phase and Git Topology

Each phase advances through reservation, launch intent, spawn, reap, bounded
result, content, phase terminal, commit intent, exact object, ref CAS, and
committed receipt.

Every durable transition event resolves to the exact record path, type,
outcome, and SHA-256 that caused it. Candidate AN001-to-TN-L002 and evaluator
AE001-to-TE-L002 are composed over literal launch-intent records.

P0 alone creates the initial ref. P1-P5 and E0 update the existing ref at the
exact parent. Only `repository_validation` may create intent, object, CAS, or
committed-phase records. It derives canonical intent bytes, commit bytes, Git
OID, parent/ref relation, and CAS links; a literal self-including intent or wrong
ref relation cannot progress. CAS is counted by its durable attempt record.

## Meter Topology

The meter no longer owns a multi-file macro action:

```text
bootstrap reaped and exact current launch/kernel identity receipts prove absence
-> resource receipt only
-> attempt-end only
-> either recoverable release or one campaign terminal
-> read-only recalculation
-> final lock release
```

After a crash, the next selector is determined by the durable boundary already
present. Invalid resource, end, or terminal paths retain the lock and are never
replaced. The campaign terminal follows attempt-end and is the last
campaign-owned durable write.

## Accounting Topology

The complete record universe, not asserted totals, owns counters. An action
reducer emits exact new record bytes; an independent reducer recomputes every
counter from record type and digest.

CPU, wall, I/O, and disk are sums. Memory is the maximum connected-component
sum in the graph of possible overlap. Removing an overlap edge is itself a
material mutation and cannot silently justify a lower maximum.

## Control Topology

```text
complete pre-state + complete durable universe
-> explicit zero/one fault transform
-> observed state/universe
-> schema and evidence validation
-> rule selection
-> action reducer
-> post-state patch and record delta
-> counter/resource reduction
```

Non-`none` faults must change an exact path, value, descriptor field, resource
input, claimed result, or durable record. The generator cannot copy a verdict
into the observed product.

Four composed traces prohibit reseeding between contexts. Four verifier attacks
mutate post-state, append a conflicting occupied path, delete a prerequisite,
and replace a committed record; each must be independently rejected.

Finite source domains are exhaustively enumerated. Per-schema ordered digests,
partition cardinalities, E0 cases, meter stages, and capability denials are
independently reproduced by the verifier.

## Preservation and Handoff

The V8 artifacts bind all 11 files in the immutable V7 rejected snapshot,
including both independent `NO-GO` reviews and the obsolete local `PASS`. V8
never upgrades those artifacts to passing evidence.

The next action is deterministic regeneration and a full independent verifier
replay over all 1,584,249 source products. Only after a local adversarial audit
may an immutable V8 review bundle be created for fresh independent Theory and
Red Team review.
