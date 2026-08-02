# TT Supervised Executor Contract V9

## Status

`HYPOTHESIS` | `MODEL-BOUND` | `ZERO-RUN` | `NOVELTY-UNVERIFIED`

V9 is a finite design model for possible schema implementation. It is not a
working executor, an executed cryptanalytic campaign, an ECDLP result, or
authorization to run the 29-mutation development campaign.

The following gates are false:

- independent Theory acceptance;
- independent Red Team acceptance;
- schema or runtime implementation;
- control campaign execution;
- cryptanalytic or performance claims.

## Revision Claim

V8 was independently rejected even though its local verifier passed. It bound
many bytes but did not derive one closed semantic state. Confirmed failures
included source reseeding, an A2 receipt backed by an A0/A1-only measurement,
disconnected Git parents, alternate-ref and producer attacks, unknown records,
path aliases, event substitution, and replayable capability receipts.

V9 addresses those failures with one event-sourced kernel:

```text
canonical record universe
-> closed type/path/payload/producer validation
-> semantic linkage validation
-> digest-linked action or observation journal replay
-> deriveState(universe, replayed context)
-> exact closed selector source
-> one selected rule and action
```

No source snapshot is admitted. The next source is never an input to a trace.

## Candidate Hypothesis

The eventual campaign compares public, target-blind candidate artifacts `P0`
through `P5`, then runs one trusted evaluator phase `E0`.

> A candidate may compile a public source artifact that improves the frozen
> target-translation objective without observing private evaluation rows,
> target labels, evaluator expectations, or later candidate outputs.

V9 tests only whether the executor model can preserve that boundary. It does not
test whether the candidate hypothesis is true.

## Null Hypothesis

Any apparent gain may instead arise from target leakage, predecessor transfer,
state ambiguity, omitted failures, accounting error, repository authority drift,
or a control oracle. The executor must preserve evidence for that null and may
not overwrite, silently repair, or retry away a failure.

## Closed Record Universe

Every V9 record has exactly:

```text
schema, path, record_type, payload, producer, canonical_bytes, sha256
```

The registry contains no wildcard type. Each type has:

- one canonical path derived from its campaign and typed identity;
- one exact payload key set;
- one authorized producer;
- no additional properties;
- typed digest edges to its prerequisites.

Paths must be normalized relative POSIX paths. Absolute paths, empty segments,
dot segments, parent traversal, alternate encodings, and normalized aliases are
rejected before uniqueness checks. Unknown and unreferenced records are rejected.

## Journal Replay

Sequence zero contains only the trusted campaign root and, for a recovery test,
the exact closed prior-attempt history. Every later sequence contains exactly one
of:

- an `action_receipt` from the trusted reducer; or
- an `observation_receipt` from the observation gateway.

Each receipt binds:

- the preceding receipt digest;
- the complete pre-universe digest;
- the exact domain-record delta;
- the post-domain-universe digest;
- for actions, the derived source digest, selected rule/action, and next context;
- for observations, the observation kind and unchanged context.

This receipt is the durable control bit required for actions such as `D004`,
`P005`, and context handoffs that otherwise append no campaign domain record.

## Attempts

Attempt ordinals are exactly `A0` through `A32`. Admissions must be contiguous.
`A0` is normal; `A1` through `A32` are recovery admissions. Every recovery
admission binds the preceding attempt-end digest, and every start binds its own
admission digest. A sparse A2 history, A33, duplicate ordinal, stale start, or
cross-attempt substitution is invalid.

The two V9 traces are:

1. normal `A0` from admission through P0-P5, E0, Git, and meter closure;
2. recovery `A2` from closed A0/A1 history through the same complete workflow.

## Phase And Event Identity

Reservations bind attempt, phase mode, and the preceding committed phase and OID.
Launches bind reservation, capability receipt, executable identity, attempt,
phase, and E0 private-map receipt when applicable.

Terminal records include a unique `event_kind`. Outcome and predecessor type are
derived together. A content-based validation failure cannot be reinterpreted as
a spawn failure, and a terminal cannot be detached from its result and content.

## Capability Boundary

The candidate descriptor is canonical and digest-bound. A capability receipt
binds:

- exact descriptor bytes and digest;
- opened executable identity;
- inherited descriptor targets and rights, not only descriptor numbers;
- attempt and phase;
- reservation digest;
- allow decision.

Candidate processes cannot author capability, repository, resource, terminal,
admission, or reducer records.

## Git Chain

Git evidence contains literal blob, binary tree, and commit bytes. Object IDs are
computed with the Git object framing algorithm. The commit intent binds the exact
result, content, terminal, tree, attempt, phase, message, parent, and intended ref.

For every phase after P0:

```text
commit.parent_oid == preceding committed_phase.commit_oid
```

CAS binds the exact pre-ref observation, intended ref, authorized producer,
commit object, old OID, and new OID. A post-CAS ref observation must still equal
the new OID before `committed_phase` is accepted.

## Resource Accounting

Resource measurement input is derived from literal contiguous admissions,
starts, and attempt lifetime records. The measured attempt set for closure `Ak`
is exactly `A0..Ak`. Memory vertices equal that set plus the typed closure vertex.
Possible-overlap edges are recomputed from literal half-open lifetime intervals.

The receipt ordinal must occur exactly once in the bound measurement and must
bind the matching admission and start. Rehashed arithmetic cannot repair an
omitted attempt or deleted overlap edge.

## Controls

V9 preregisters and executes 26 design mutations, including:

- sparse A2 and A33;
- source/context reseeding and event substitution;
- unknown types, extra keys, producer swaps, and normalized aliases;
- reservation/launch ordinal drift;
- disconnected parents, alternate refs, candidate CAS, and post-CAS movement;
- synthetic Git trees;
- forged/replayed capability receipts and descriptor-target substitution;
- omitted current resource attempt and deleted overlap edge;
- asserted phase outcome and unreferenced private copy;
- sequence-zero journal injection and out-of-context meter observation;
- deleted transition receipt and replayed consumed observation;
- cross-file selector swap.

The builder result is untrusted. The independent verifier must execute every
mutation again and reproduce the preregistered rejection reason.

## Publication

The mutable draft may not authorize implementation. A review bundle must include
the V7 and V8 rejected bytes, both V8 reviews, both repair handoffs, selector,
builder, verifier, contract, topology, generated artifact, local receipt, and one
manifest. Every payload must be manifest-bound exactly once; AppleDouble files
are excluded; an external root pins the manifest.

## Limitations

- The model is finite and `MODEL-BOUND`.
- Runtime OS isolation, process authority, filesystem synchronization, and Git
  ref atomicity remain implementation obligations.
- Git SHA-1 compatibility is not a SHA-1 collision-resistance claim.
- Local builder/verifier agreement does not replace independent review.
- No cryptanalytic workload has run.

## Next Concrete Action

Run the independent V9 verifier on exact draft bytes, deterministically rebuild,
freeze a self-contained review bundle, and obtain fresh Theory and Red Team
decisions before any implementation or campaign action.
