# Local full-gate addendum to the sealed BINSTD Lean review

**Date:** 2026-10-27 UTC. **Execution head:** `98fca453a13b0e4e1ae866a96d14c2760cfb2aeb`.
**Reviewed producer:** `6409590d9bf26201956095e87f36f25d346cba68`.
This is an addendum to the immutable [original review](../REPORT.md), not a
rewrite of its 2026-10-26 verdict or archive receipt. It changes no official
scientific hypothesis, evidence or decision status.

## Observation

After exact manifest dependencies were hydrated and the ignored 48-module
root was regenerated, a fresh local `lake build` completed all **8,980**
jobs. The repository's `autoresearch formal verify` command for target
`TASK-20261026-f485d7` returned `machine_verified`: root and named builds
passed, `AxiomAudit.lean` reported **707** project theorem declarations
using only permitted standard axioms, and its generated audit of the exact
requested theorem passed. It found no forbidden proof construct and no
infrastructure failure. The source, spec, toolchain and manifest hashes match
the frozen reviewed input. Raw command output, the original formal-verifier
receipt and a checker are in
[`lake-verified-20261027`](../../binstd_end_to_end_20261026/lake-verified-20261027/).
The earlier timed-out and missing-root attempts are retained separately at
[`lake-workspace-20261027`](../../binstd_end_to_end_20261026/lake-workspace-20261027/).

## Comparison and scoped update

| Review claim | 2026-10-26 sealed snapshot | New local result |
| --- | --- | --- |
| C1: five encoded finite values and trial counts | Independently validated in exact finite scope | Unchanged |
| C2: reviewed Lean declaration and axioms | Direct pinned check passed; full gate pending | Full target verifier passed for identical source and target bytes; validated in encoded scope |
| C3: archived direct-check receipt | Validated as a direct-check consistency record | Unchanged |
| C4: full pinned workspace and target gate | Not verified | Locally machine verified at execution head; hosted gate still blocked before runner assignment |
| C5: polynomial/runner/Frobenius bridge | Not proved by reviewed declaration | Still not proved by this target |

The original J1/J2 reviewers established the meaning of the frozen encoded
theorem and independently recomputed its 1,110 monic candidate rows. The
formal verifier does not ingest those reviews and leaves its own
`semantic_review.status` as `pending`. The addendum joins the reviewed source
hashes to the new machine receipt; it does not claim a second independent
full-workspace execution.

## Boundary and next action

The checked theorem is about the specified XOR-and-shift bitmask algorithm.
It does not prove that algorithm computes Euclidean remainder in
`(ZMod 2)[X]`, identify the archived runner with the canonical finite field,
classify all invariant subspaces, or establish a relation-yield or attack-cost
claim. A separate unmerged [PR #2484](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2484)
contains cyclotomic irreducibility and abstract canonical Frobenius proofs;
its concrete runner bridge and its current merge/check gates remain separate.

GitHub's required current-head checks still fail before runner assignment
with an account payment or spending-limit annotation. Keep PR #2599 unmerged
and do not publish Pages until those checks pass, as the owner authorized.
The diagram in this directory shows the local machine and independent
semantic paths and leaves the unsupported bridge open. It is a proof-scope
diagram; no performance values changed. The original BINSTD run graph and
its inspected PDF were checked and left unchanged because this gate supplied
no new run measurement.

[`claim-addendum.json`](claim-addendum.json) binds the exact new receipt to
the immutable original review receipt and records the scoped status update.
[`report.pdf`](report.pdf) is the rendered reading copy.
