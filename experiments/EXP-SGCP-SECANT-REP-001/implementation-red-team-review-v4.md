# Handoff: EXP-SGCP-SECANT-REP-001 V4 red team

## Claim or task

Seek source implementations or payloads that satisfy a plausible V4 reading
while violating the intended source-stage semantics at exact commit
`c05dabbf4cddae8e196448de174e6daab7eba0d7`.

## Status

`HYPOTHESIS` - **REVISE**

Source implementation remains unauthorized. No run or child was executed.

## Assumptions

- V4 cannot silently override repository coordinator authority.
- Review is static and limited to source authorization.

## Evidence so far

The exact commit and all V4 file hashes matched. V4 improves key-set, coverage,
exhaustion, and accounting-category closure but does not yet close semantics.

## Failure modes

1. Reviewer GO is not an unambiguous coordinator state transition.
2. Scalars, tuples, enums, digests, nulls, and rational encodings are untyped.
3. Stream, fixture, compiler, attempt, verification, and decision references
   can be orphaned or permuted.
4. Fourteen false checks, one failed control, or one unrejected mutation can
   coexist with structurally complete records.
5. Normative hashes and independent verifier-audit provenance are incomplete.
6. An empty-stream partial artifact can mark all 4,608 cells missing.
7. Counter serialization, failed supervisor charging, and concurrency
   enforcement are non-deterministic.

Static negative vectors must cover false verification, compiler permutation,
orphan references, failed controls and mutations, empty partial streams,
invalid attempt caps, renamed shared helpers, altered normative bindings,
undercharged supervisor failure, and overlapping development children.

## Next concrete action

Publish a V5 typed relational schema, exhaustive bindings/accounting rules, and
a separate coordinator source-writing transition while retaining every
execution lock.

## Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/implementation-contract-v4.md`
- `experiments/EXP-SGCP-SECANT-REP-001/source-schema-v4.json`
- `experiments/EXP-SGCP-SECANT-REP-001/mutation-amendment-v4.json`
