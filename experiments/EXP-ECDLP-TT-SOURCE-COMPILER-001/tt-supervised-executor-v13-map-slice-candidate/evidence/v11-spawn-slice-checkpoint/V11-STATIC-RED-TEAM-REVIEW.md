# V11 P0 Spawn-Failure Static Red-Team Review

## Review boundary

Status: `NEGATIVE RESULT` | `MODEL-BOUND` | `ZERO-RUN`

This read-only review examined builder hash
`371a1224f548faf013e614fce6ded2675fb73f8aeb899f9bbdc0692881256b67`
and artifact hash
`9558d490cc2d33b3892d716e969164a34380c2618ad9198d9b7b805bde5531f1`.
The reviewer did not execute the builder, verifier, regressions, a runtime
executor, Git publication, or a cryptanalytic workload.

## Findings

### High: falsy observation context bypassed the builder

The builder compared an observation receipt's `context` only when that field
was truthy. A digest- and journal-relinked spawn receipt with `context: ""`
could therefore retain the correct request, subject, value, and domain while
being accepted by the builder. The independent verifier required exact context
equality and rejected the same record. This was a concrete decision-parity
counterexample, not merely a missing test.

The affected boundary was the observation branch of `replayKernel` in
`build_v11_closed_kernel.mjs`; the strict counterpart was the observation
branch of `replayTrace` in `verify_v11_closed_kernel.mjs`.

### Medium: C004 evidence did not cover C004's full domain

The sole positive failure witness was a P0 spawn failure. The inherited C004
selector accepts non-valid predecessor terminals at P0 through P5, including
harness-failure and quarantine outcomes. C005 also accepts several committed
E0 outcomes. The P0 witness therefore supports only the canonical P0 path; it
does not validate generalized later-phase, runtime-failure, quarantine, or
failed-E0-close behavior.

### Medium: relinked mutations establish first rejection only

The focused mutation runner rehashes changed records, propagates digest and Git
object changes, and reconstructs journal roots. It does not regenerate every
downstream selector source and selected action. Some mutations consequently
retain secondary contradictions. They establish the exact first rejection on
the current validators, not the necessity or sufficiency of the targeted
predicate in isolation.

In particular, the original AN002 mutation moved an observation-gateway spawn
to the AN002 sequence. It tested temporal invalidity but did not directly test
producer authority.

### Medium: verifier independence remained common-mode

The builder and verifier are separate implementations, but they share the same
canonicalization and reducer architecture. Both initialized selector-domain
fields from the first declared domain value before overwriting supplied fields,
contrary to the theory handoff's explicit-source requirement. Fixed-corpus
agreement should be called second-implementation parity, not independent
acceptance evidence.

### Confirmed finite-model property: failure envelopes are deterministic

Within exact replay, a non-valid terminal has a canonical envelope binding the
campaign, ordinal, phase, terminal digest, event kind, outcome, predecessor,
and null success links. Blob, tree, commit, intent, and ref linkage are checked.
This confirms deterministic serialization only; it does not establish live Git
object-database acceptance, ref atomicity, durability, or crash behavior.

## Post-review remediation

The main research process subsequently:

- changed the builder to reject every non-exact observation context, including
  empty string and null values;
- added `spawn_observation_empty_context` with expected rejection
  `OBSERVATION_CONTEXT_MISMATCH`;
- removed first-domain-value initialization from both source constructors and
  required every non-fixed source field explicitly;
- relabeled mutation evidence as first-rejection evidence;
- added a direct `root_supervisor` producer forgery for `phase_spawn`, with
  expected rejection `PRODUCER_UNAUTHORIZED`.

These remediations require fresh builder, verifier, and mutation receipts; this
review itself does not certify them.

## Handoff: V11 P0 spawn-failure static red team

### Claim or task

Independently test whether the V11 P0 spawn-failure slice supports its
observation, failure-publication, C004/E0-close, regression, and
validator-independence claims.

### Status

`NEGATIVE RESULT` | `MODEL-BOUND` | `ZERO-RUN`

### Assumptions

- Review is bounded to the finite artifact model and the byte hashes above.
- OS truthfulness, crash atomicity, Git durability, and producer authentication
  remain outside the evidence.
- Request, subject, and value binding is evaluated only under complete journal
  replay.

### Evidence so far

- Request, subject, and value were exact-replay bound, but falsy context was not
  bound by the reviewed builder.
- Failure-terminal envelope serialization and Git-object linkage were
  deterministic within the model.
- C004 admitted substantially more predecessor shapes than the sole P0 witness
  covered.
- Several relinked controls retained secondary semantic contradictions.

### Failure modes

- A falsy observation context bypasses one reducer.
- A generalized C004 claim is inferred from one P0 witness.
- An early rejection hides stale downstream semantics.
- Copied reducer logic creates common-mode acceptance.
- Static Git-compatible bytes are overread as live publication evidence.

### Next concrete action

Add a journal-relinked `spawn_observation_empty_context` control and require
both reducers to reject `OBSERVATION_CONTEXT_MISMATCH`.

### Artifact paths

- `build_v11_closed_kernel.mjs`
- `verify_v11_closed_kernel.mjs`
- `supervised-executor-closed-kernel-v11.json`
- `run_spawn_failure_regressions_v11.mjs`
- `spawn-failure-regressions-v11.json`
- `mandatory-regressions-v11.json`
- `supervised-executor-v11-theory-handoff.md`
