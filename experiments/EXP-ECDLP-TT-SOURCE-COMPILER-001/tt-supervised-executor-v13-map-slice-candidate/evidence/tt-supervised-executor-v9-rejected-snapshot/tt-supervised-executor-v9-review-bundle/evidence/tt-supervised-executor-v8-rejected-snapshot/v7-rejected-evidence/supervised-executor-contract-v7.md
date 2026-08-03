# TT Supervised Executor Contract V7

## Status

`HYPOTHESIS`, `MODEL-BOUND`, `UNTESTED`, `ZERO-RUN`.

This is a design contract for possible schema implementation. It is not a
working executor, an executed control suite, an ECDLP result, or authorization
to run the 29-mutation campaign.

The following remain false until a newly frozen V7 bundle receives independent
Theory and Red Team `GO` decisions on its exact hashes:

- artifact freeze authorization;
- schema or code implementation authorization;
- control execution authorization;
- development campaign authorization;
- production campaign authorization; and
- cryptanalytic or performance claims.

## Revision Claim

V7 replaces the frozen V6 executable-oracle design. V6 is preserved byte for
byte as negative evidence and is not treated as a trusted control source.

V7 repairs the reviewed V6 counterexamples by:

1. publishing a bounded admission token before every linked attempt-start;
2. resuming a crash between those writes with the same token;
3. deriving every executable control through a closed witness pipeline,
   `pre-state -> fault transform -> selection -> action -> post-state`;
4. binding counters to a complete literal durable-record universe;
5. placing E0 private-map state in the closed launch-event schema;
6. making each meter durable write a separate idempotent stage;
7. materializing every non-`none` fault as an actual changed value or record;
8. evaluating CPU, memory, wall, I/O, and disk formulas numerically;
9. closing candidate capabilities over process, filesystem, descriptor, and
   launch-barrier authority; and
10. materializing Git self-cycle, ref-relation, terminal lower-field, and
    maximum-recovery boundary controls.

Passing the V7 builder or verifier would establish only internal consistency of
this design model.

## Candidate and Hypothesis

The supervised campaign compares six public, target-blind candidate artifacts
`P0` through `P5`, followed by one trusted evaluator phase `E0`.

Candidate hypothesis:

> A candidate may compile a public source artifact that improves the frozen
> target-translation objective without observing private evaluation rows,
> target labels, evaluator expectations, or later candidate outputs.

The evaluator opens the private map only after every candidate phase has
committed or after an earlier phase has produced a typed harness failure or
quarantine outcome.

## Null Hypothesis

The null is that all apparent gains are attributable to target leakage,
unreviewed predecessor transfer, state-machine ambiguity, omitted failures,
resource-accounting error, or control-oracle construction rather than a genuine
target-blind source artifact.

The executor must preserve evidence supporting the null. It may not silently
retry away a failure, overwrite an occupied artifact, repair a candidate output,
or infer success from a builder/verifier receipt.

## Trust Boundary

Trusted components:

- approval and artifact signers;
- the external meter;
- the bootstrap and dispatcher;
- canonical parsers and schema validators;
- exact process-identity reconciliation;
- Git object and ref verification;
- the E0 evaluator; and
- the V7 witness verifier.

Untrusted components:

- P0-P5 candidate processes;
- candidate-created files and process output;
- inherited environment, descriptors, and process state not named by the
  boundary descriptor; and
- all prose or expected values not independently derived from durable evidence.

The evaluator is not a seventh candidate run. It is trusted evaluation work and
must be charged separately.

## Durable Publication

Every campaign-owned durable record uses:

1. canonical closed-schema bytes;
2. a path derived from campaign ID, approval digest, phase or attempt ordinal,
   and record type;
3. no-replace creation;
4. file synchronization;
5. directory synchronization; and
6. exact reparse after publication.

An occupied path is accepted only when its canonical digest is identical to the
record being replayed. A different digest is an integrity failure. No recovery
path overwrites, truncates, renames over, or deletes an occupied campaign path.

## Root Lock and Attempts

One kernel-held campaign lock spans one external meter/bootstrap pair. Candidate
and evaluator children never inherit the lock descriptor.

The approval fixes `maximum_recovery_bootstraps = k`, where `0 <= k <= 32`.
The campaign has at most `1+k` root admissions and at most one attempt-start per
admission.

### Admission Order

The only valid durable order is:

```text
bounded admission token
-> linked attempt-start
-> repository or phase action
```

The normal `A0` admission is also the one-time campaign-consumption record.
Recovery admissions `A1` through `Ak` are numbered, approval-bounded, and
created no-replace. Each attempt-start contains the ordinal and digest of its
admission token.

The following invariants are checked from the complete durable universe:

```text
normal admissions use ordinal A0
recovery admissions use ordinals A1..Ak
each ordinal has at most one admission
each admission has at most one attempt-start
every attempt-start names an existing admission
root_attempt_starts <= root_admissions <= 1+k
recovery_slots <= k
```

### Crash Boundaries

If the root dies after admission publication but before attempt-start
publication, the next lock holder classifies the dangling admission before
ordinary eligibility. It dispatches `attempt_admission` and writes or reparses
the one linked attempt-start for that same ordinal. It does not allocate another
token and performs no repository or phase work first.

If the root dies after attempt-start publication, the start is unmatched and is
handled by prior-attempt precedence. Closing that attempt never consumes a new
admission. A later recovery may allocate the next token only after the previous
attempt has an immutable end record and exact process absence is established.

Boundary controls instantiate `k = 0`, `k = 2`, and `k = 32`, with respectively
1, 3, and 33 admissions and starts at exhaustion.

## Entry Precedence

Entry preflight uses this order:

```text
lock identity and acquisition
-> occupied campaign terminal
-> prior unmatched attempt
-> dangling admission without a start
-> invocation eligibility
-> bounded admission reservation
-> linked attempt-start
-> campaign progression or recovery reconstruction
```

An occupied valid terminal exits read-only. An occupied invalid terminal is
unrecoverable and is never replaced.

Normal replay, recovery without the normal consumption, and exhausted recovery
reject before a new admission or attempt-start and make no campaign write.

Eligible normal and recovery products are closed over every field. In
particular, they bind:

- run mode;
- normal consumption;
- private selection relation;
- approval maximum and consumed recovery slots;
- next recovery ordinal;
- recovery-slot status;
- repository identity;
- phase-chain validity;
- ref relation;
- initial phase state; and
- the compound entry-product relation.

An omitted, out-of-domain, or inconsistent field is schema rejection or the
explicit default. It cannot select a launch rule.

## Prior-Attempt Safety Context

Selecting a prior unmatched attempt fixes the precedence reason before any
lower campaign state is read. A separate `prior_attempt_safety` context may then
read only:

- exact launch-identity records; and
- kernel process-identity status for those records.

It may not read repository state, phase semantics, candidate results, private
evaluation artifacts, or any field capable of changing the selected precedence
reason.

If every named identity is kernel-confirmed absent, the dispatcher may hand off
to meter finalization with an infrastructure request. If one identity is live,
it retains the lock and reconciles that exact process. If evidence is absent,
ambiguous, invalid, or unkillable, it retains the lock and publishes no
terminal. Process absence is a safety condition, not a reason-selection input.

## Disjoint Contexts

The transition artifact defines ten disjoint contexts:

1. `entry_preflight`;
2. `attempt_admission`;
3. `prior_attempt_safety`;
4. `live_supervisor`;
5. `live_transition`;
6. `recovery_reconstruction`;
7. `campaign_progression`;
8. `repository_validation`;
9. `meter_finalization`; and
10. `e0_private_map`.

Every source names one closed schema and one context. A rule from another
context cannot be selected. Within a schema, first matching priority wins;
equal-priority overlap is invalid; unmatched valid products request
infrastructure failure. Invalid closed-schema products reject before selection.

## Phase Protocol

The live states are:

```text
UNSEEN
RESERVED
LAUNCH_INTENT_DURABLE
SPAWN_FAILED
SPAWNED
REAPED
RESULT_RETAINED
CONTENT_PUBLISHED
TERMINAL_VALID_OUTCOME
TERMINAL_HARNESS_FAILURE
TERMINAL_QUARANTINE
COMMIT_INTENT_DURABLE
COMMIT_OBJECT_EXACT
REF_APPLIED
COMMITTED
```

Every phase uses at most one reservation, launch intent, spawn, reap, bounded
result, content record, phase terminal, commit intent, exact commit object, ref
CAS attempt, and committed phase receipt.

P0 uses initial-ref CAS. P1-P5 and both E0 modes use existing-ref CAS. The
phase-conditioned CAS relation is present in the closed event products and in
the repository-validation context.

Every root-crash state hands off to `recovery_reconstruction`; ordinary live
progression cannot select a recovery-only quarantine rule.

## Candidate Capability Descriptor

Before launch, the trusted bootstrap validates exact
`candidate_boundary_descriptor_v2` fields:

- executable path and SHA-256;
- complete argument vector;
- complete environment;
- working directory;
- readable and writable roots;
- inherited descriptors;
- private-artifact label policy;
- path-resolution policy;
- mount namespace and inherited-directory-handle policy;
- syscall profile and resource limits;
- signal authority;
- network authority;
- fork authority;
- post-image exec authority;
- IPC authority;
- debugger, task-port, and ptrace authority;
- positive timeout;
- kill and exact-reap policy; and
- the current launch-barrier receipt.

The approved candidate descriptor permits only the named executable, public
input and candidate work roots, descriptors 0-2, a fixed public environment,
and the initial executable image. It denies private labels, network, fork,
further exec, IPC, debugger, task port, and ptrace.

Arguments, environment, readable roots, and inherited descriptors are treated
as data channels. The private map, evaluator expectation, target labels, and
private receipts may not appear in any of them.

Twenty-six negative controls each change exactly one descriptor field and must be
rejected. One positive control validates the exact descriptor. Candidate spawn
is illegal until the descriptor and launch-barrier receipt have both passed.

## E0 Private-Map Protocol

E0 has two modes:

- `evaluate`; and
- `close_prior_failure`.

The private-map state and binding are fields in both the E0 live-action schema
and the E0 live-event schema. An evaluate launch-intent transition is admitted
only with `MAP_OPENED_RECEIPT_DURABLE` bound to the current E0 reservation.

Evaluate states are:

```text
MAP_UNSEEN
MAP_OPEN_INTENT_DURABLE
MAP_OPENED_UNRECEIPTED
MAP_OPENED_RECEIPT_DURABLE
MAP_OPEN_FAILED_DURABLE
```

The trusted meter writes the open intent before the syscall. A successful open
is held only by the trusted evaluator/meter path and is followed by a durable
opened receipt before live dispatch. A syscall error publishes one E0
`harness_failure` phase terminal containing bounded error evidence. It does not
pretend the evaluator ran. That durable terminal then creates one E0 commit
intent and enters repository validation; it cannot launch the evaluator.

The generated E0 event projection enumerates:

```text
2 run modes
x 2 E0 modes
x 6 map states including not_applicable
x 7 declared event symbols
= 168 cases
```

For each row it derives the canonical descriptor state from the map state. The
independent finite-source suite separately enumerates all four descriptor-state
values, for 672 closed `e0_private_map_v2` source products. Thus descriptor
inconsistency is not pruned from totality.

Closure mode never opens the private map. Any private-map event dispatched in
closure mode requests infrastructure failure. Every evaluate map state has an
explicit root-crash handoff or a closed default.

## Git and Repository Validation

Every commit intent is canonical and self-excluding: it binds all intended
inputs and object content except the commit OID that does not exist until object
creation. The exact commit object is then created and reparsed. A materialized
negative control changes `valid_self_excluding` to `invalid_self_including` and
must select `GIT_COMMIT_INTENT_SELF_CYCLE`.

Repository validation separately binds:

- phase mode;
- commit-intent relation;
- commit-object state;
- expected ref relation; and
- CAS status.

P0 requires an absent initial ref. Later phases require the ref at the exact
parent. A changed relation defaults to infrastructure failure and cannot execute
CAS. Every CAS action adds one literal `ref_cas_attempt` record to the complete
universe.

## Meter Finalization

The external meter owns attempt resource, attempt-end, and campaign-terminal
publication. It retains the campaign lock through bootstrap reap and exact
process absence.

No meter rule writes resource, attempt-end, and terminal as one macro. Reachable
stages are:

```text
resource absent        -> write resource receipt only
resource durable       -> write attempt-end only
attempt-end durable    -> release recoverable lock, or publish one terminal
terminal published     -> perform read-only recalculation
recalculation complete -> release final lock
```

Each campaign-owned write action emits at most one durable record. A replay
accepts an identical occupied record and rejects a conflicting one. Invalid
resource, attempt-end, or terminal records retain the lock and are never
overwritten.

The campaign terminal follows resource and attempt-end. It is the last
campaign-owned durable write. Recalculation and lock release are read-only with
respect to campaign artifacts.

## Literal Record Universe and Counters

Every transition witness carries the complete fixture record universe before
the fault, after the fault, and after the selected action. Each record includes:

- exact path;
- closed record type;
- canonical payload;
- producing action;
- canonical bytes; and
- SHA-256 of those bytes.

Paths and admission ordinals are unique. Counter snapshots are reductions of
these records, never numeric inputs. The counters are:

```text
root_admissions
root_attempt_starts
normal_consumptions
recovery_slots
phase_reservations
candidate_phase_reservations
evaluator_phase_reservations
phase_spawns
phase_reaps
commit_intents
commit_objects
ref_cas_attempts
committed_phases
meter_finalizations
```

Every countable record appears in the corresponding evidence list. Every
noncountable record appears in the noncounter list. Their union must equal the
complete universe. Missing, extra, duplicate, unreferenced, noncanonical, or
digest-invalid records reject the witness.

Action deltas are computed by the action reducer. In particular, spawn, reap,
commit-intent, commit-object, CAS, committed-phase, and attempt-end actions must
change their counters when executed.

## Numeric Resource Accounting

For attempt `j`, CPU charge is:

```text
(bootstrap_observed_j if valid else bootstrap_cap_j)
+ (meter_observed_preterminal_j if valid else meter_preterminal_cap_j)
+ meter_terminal_cap_j
```

Total CPU is the sum over attempts. Wall, I/O, and disk are sums of the approved
attempt charges.

For memory, vertices are attempts or closure finalizers with approved
capacities. An edge means overlap is possible or nonoverlap is unproved. Charge
each connected component by the sum of its capacities, then take the maximum
component charge. Serial maximum is therefore permitted only when exact
nonoverlap separates vertices.

The fixed numeric control has:

```text
CPU    = 52
memory = 73
wall   = 85
I/O    = 24
disk   = 12
```

Negative controls alter a terminal CPU cap, remove overlap edges, claim CPU 51,
and claim memory 37 while overlap is unproved. The independent verifier
recomputes every result and rejects each mismatch.

## Closed Transition Witness

An executable control is not an oracle-labelled before/after pair. It is
generated as:

```text
complete pre-state and complete pre-record universe
-> exactly zero or one explicit fault transform
-> complete observed state and record universe
-> closed-schema validation and rule selection
-> action reducer
-> derived post-state patch and action record delta
-> independently reduced counters and resources
```

Every non-`none` fault records a path, exact before value, and exact after value.
Record removal names the exact path and digest. A non-`none` fault that makes no
material change is a builder error.

The V7 control artifact contains:

- one selection control for every rule;
- targeted admission, entry, precedence, E0, meter, counter, terminal, and Git
  controls;
- recovery-boundary controls at 0, 2, and 32;
- one exact capability positive and twenty-six capability denials;
- five numeric resource controls; and
- generated closed-product manifests.

## Generated Products

The builder enumerates every finite source-schema product. It records per-schema
case counts and an ordered case-stream SHA-256, plus every nonempty rule,
schema-rejection, and default partition cardinality. The verifier independently
reenumerates and compares all counts, partitions, and digests.

The builder also materializes:

- the 168-case E0 event projection plus all 672 closed descriptor products;
- all seven reachable meter stages; and
- all twenty-six denied capability mutations.

Implicit legal-state pruning is forbidden. Invalid compound budget products are
classified by executable schema invariants.

## Preservation

The V7 transition and control artifacts bind the six frozen V6 files by exact
SHA-256. V6 reviews and local audit remain separate durable negative evidence.
V7 does not rewrite, delete, or relabel those failures as passes.

## Gates

### Gate A: local internal consistency

Required before freezing a V7 review bundle:

- deterministic builder output across two clean runs;
- independent verifier pass;
- exact transition and control hash binding;
- all source products and partitions independently reproduced;
- all non-`none` faults materially changed;
- action deltas and counter reductions independently reproduced;
- admission linkage and 0/2/32 boundaries reproduced;
- E0 receipt and 168-case product reproduced;
- meter stage restarts reproduced;
- capability and numerical accounting controls reproduced; and
- no authorization flag set true.

Gate A is not sufficient for schema implementation.

### Gate B: independent review

Fresh Theory and Red Team reviewers receive only the frozen V7 hashes and
bundle. Both must return `GO` for possible schema implementation. Any concrete
counterexample creates a versioned V8 repair; V7 remains immutable.

### Gate C: implementation and controls

Only after Gate B may reviewed schemas and runtime controls be implemented.
Passing implementation controls is still not campaign authorization.

### Gate D: campaign execution

The 29-mutation campaign requires a separate nonzero-run approval with exact
commit, inputs, limits, seeds, output paths, and stop conditions. No V7 design
artifact grants it.

## Handoff: Supervised Executor V7

### Claim or task

Determine whether the V7 executable-witness design is internally sufficient to
authorize only possible schema implementation.

### Status

`HYPOTHESIS`, `MODEL-BOUND`, `UNTESTED`, `ZERO-RUN`.

### Assumptions

- The finite source domains model all implementation-relevant statuses.
- Canonical record bytes and exact process identity can be implemented as
  specified.
- No control or campaign has run.

### Evidence so far

- Builder generation and local verification are required but not independent
  evidence.
- Frozen V6 Theory, Red Team, and local counterexamples motivated every V7
  repair obligation.
- The literature review does not claim a cryptanalytic result from this harness.

### Failure modes

- A missing source field or action effect can admit an unmodeled transition.
- A fixture universe can still omit a record class needed by a real runtime.
- A capability denial may not map cleanly to every supported operating system.
- Passing schema review says nothing about the ECDLP hypothesis.

### Next concrete action

Run a deterministic local rebuild and independent verifier, perform a local
adversarial audit, freeze exact V7 hashes, and request fresh read-only Theory and
Red Team decisions.

### Artifact paths

- `supervised-executor-transition-matrix-v6.json`
- `supervised-executor-control-matrix-v6.json`
- `build_v7_design_artifacts.mjs`
- `verify_v7_design_artifacts.mjs`
