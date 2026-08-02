# EXP-SGCP-EMBED-002 V15 Revision Response

## Reviewed boundary

V15 responds to the three fresh exact-commit reviews of
`371790de7418aee8b1f56b7fa872f91bbec43899` and coordinator decision
`DEC-SGCP-EMBED-002-014`. Theory issued scoped `GO`; accounting and red team
issued `REVISE before launch-plan design`. No V14 review authorized a generated
row, canonical matrix, runner, launch plan, execution, or budget increase.

## Finding disposition

| V14 finding | V15 disposition |
|---|---|
| `Path` construction normalizes raw `.` and repeated empty separator components before the claimed rejection checks | The contract now makes normalization the policy: those in-root spellings are aliases of one normalized destination. Explicit `..` parent traversal is rejected before normalization, normalized outside-root paths remain rejected, and no raw-spelling-preservation claim remains. |
| The path control covered parent traversal but not the normalized-alias behavior | The existing control now publishes through a raw `./` and repeated-separator spelling, requires one normalized destination and receipt path, and requires production and standalone status to attribute the same accepted pair. It separately retains the `..` rejection and no-outside-artifact assertions. |
| The handoff and active ledger row still described completed V14 validation, hashing, commit, and reviews as pending | Both records now identify the committed V14 review outcome and the V15 implementation and validation state. |
| Four committed V7 records were absent from the durable-artifact inventory | `protocol-amendment-v7.json`, `revision-response-v7.md`, `development-test-log-v7.md`, and `source-self-review-v7.md` are restored. The specification also preserves the complete V14 implementation, review, provenance, and decision inventory before adding V15. |

The V14 theory review found no mathematical defect. Accounting and red team
found no containment escape, accounting error, or budget widening. V15 therefore
changes claim precision, control coverage, and record inventory only.

## Output-path policy

Every public writer, receipt-path, and status entry applies the same boundary:

- reject any explicit `..` path component before absolute normalization;
- normalize in-root `.` components and repeated separators as aliases;
- reject the development root itself and every normalized path outside it,
  while admitting an absolute in-root destination under the same rule;
- derive one development-root-relative destination for receipt binding.

The descriptor walker repeats the `..` check and opens the normalized
root-relative parent chain with no-follow semantics. It does not claim to
preserve or reject raw spellings already erased by normalization.

This policy preserves the V14 containment result while aligning the prose and
test oracle with actual Python path semantics.

## Retained V14 publication protocol

V15 does not redesign publication. It retains:

- a fresh random 256-bit publication identifier per attempt;
- deterministic data and receipt name preflight;
- descriptor-relative no-overwrite publication;
- receipt binding to basename, root-relative path, payload bytes and hash,
  protocol, experiment, identifier, and canonical self-digest;
- exact-attempt reconciliation after an ordinary synchronous receipt-publication
  exception;
- fail-closed observed direct-write inode type or size mismatch;
- production and structurally separate standalone receipt validation;
- actual hard-link branch controls on a test-only capable filesystem.

The receipt remains unkeyed, sequentially validated, and non-atomic as a pair.
It is not hostile same-user authentication or proof that every durability
syscall succeeded.

## Current-state and inventory repair

The primary handoff now records V15 as an implementation preflight and names
fresh exact-commit review as the next action. The active research-ledger row
likewise records zero V15 generated density rows and zero runs.

The durable inventory keeps the four restored V7 records, all V14 source
amendments and test records, all three exact V14 reviews, V14 provenance, and
the V14 decision. Historical records are not rewritten.

## Claim and budget boundary

The curve grid, predicates, compiler, ordering digest, graph, cap schedule,
five-field objective, family gate, and completed operation vector
`480/112/336/218/4218` are unchanged.

No relation yield, rank, linear algebra, target descent, fixed-curve
preprocessing crossover, rho improvement, fitted exponent, deployment result,
or ECDLP break is established. V15 remains `HYPOTHESIS`, `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

No generated V15 curve-family density row, canonical matrix, runner, launch
plan, or run is authorized. `maximum_runs=0`.

## Next action

Validate and commit one exact V15 snapshot, then obtain fresh independent
read-only theory, accounting, and red-team reviews. Even three scoped `GO`
decisions could authorize only a separate hash-complete launch-plan design, not
execution.
