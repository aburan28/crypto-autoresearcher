# Stage 8 additive schema repair

**DEC-20260908-f43f40 approves the administrative mapping only**, conditional
on exact source/copy checks, completed archival and full ledger validation.
The parent reported 27 schema errors in the imported shared plan and its
three referring handoffs. This note does not claim the repair has already
passed those gates.

The corrected plan preserves every original field. It adds canonical aliases
for `claim`, `prior`, joint ID/owner and the existing known-false-object/control
description. Explicit metadata marks this as later schema adoption and binds
the original path/hash. Three effective handoff copies preserve their IDs and
all other fields, changing only the shared `review_plan` reference. Three
hash-pinned `kind: ledger` routes select those copies. Original files,
scientific records and historical assertions remain immutable; no validator
rule is relaxed.

The source's independence explanation is **not adopted as a valid evidence
standard**. PD-S8R1 explicitly says the producer's session also performed the
review, with `independent_session: false`. The required policy and actual
same-session disclosure must both remain visible. A `blind_from` boundary can
restrict access; it does not create an independent session. Adding canonical
review-plan fields cannot establish independence or attest retrospectively to
preregistration, chronology or scientific correctness.

The original Stage 8 claim, prior, degree/nnz observations, fixture/gamma
assertions and recorded timing/commit fields remain historical assertions.
Neither this note nor the schema decision reviews or confirms them. No
hypothesis, experiment, goal or scientific status changes. No Stage 8 or Stage
9 execution is authorized. Other-owner Stage 9 work retains its own authority
and live state without an assertion about it here.

The parent must verify the four original source hashes, recursively compare
all preserved fields, check the exact allowed additions/substitutions and
three registry bindings, then archive the exact resulting bytes and run the
full ledger gate. The decision identifies the immutable source hashes and
mechanical correction paths. Future output hashes and archive completion are
not invented in these approval files.

All source reads, hashes and validator findings were transmitted by
`parent_control_plane/01a07d9c-ceb4-7892-ae01-260e4b5f0374`. This Coordinator
performed no commands, experiments, tests, proofs or scientific evidence
review. Exact native model identity is unverified; no fallback or degradation
is authorized.

Before future scientific reliance, the responsible Stage 8 Coordinator must
set up an actual prospective independent review under the required policy and
record its genuine session/access provenance. The unrelated recall design
does not depend on these Stage 8 claims, so its schema publication prerequisite
can clear once the assembled ledger passes. The full pending approval/design
objective remains active, with the parent's recorded next candidate
EXP-ECDLP-9cd134 considered after that prerequisite clears.
