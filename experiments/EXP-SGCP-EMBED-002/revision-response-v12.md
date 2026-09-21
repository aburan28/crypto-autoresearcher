# EXP-SGCP-EMBED-002 revision response v12

## Scope

V12 repairs the five verifier-boundary findings from the exact-commit V11
review. It changes no curve, predicate, representative compiler, graph,
objective, family gate, or mathematical interpretation. It creates no generated
curve-family density row, canonical matrix, runner, launch plan, or execution
authorization.

## Finding closure

| V11 finding | V12 response |
|---|---|
| Accounting, reservation, and registered-curve cache state was process-global | Every public `verify_document` call creates one fresh context-local state and restores the prior state in `finally`. Actual work, the active reservation, and the registered-curve cache live inside that state. Two synchronized concurrent calls and one nested call each reproduce the serial receipt exactly. |
| Transient B6/B8 legacy semantic rows were omitted from scope language | The focused suite constructs exactly three transient noncanonical frozen legacy semantic rows, at B=4,6,8, and records their row digests. They reproduce predecessor values only. They are distinct from the sole frozen-B4 density-row/document control and from generated curve-family rows, of which V12 creates zero. |
| Output used a check-then-replace overwrite path | Output parents are walked from the development root through no-follow directory descriptors. The writer uses an exclusive temporary inode and a no-overwrite descriptor-relative publish primitive where supported. On exFAT it uses an `O_EXCL` final descriptor, never overwrites, and leaves an interrupted partial destination permanently fail-closed. Preexisting, race-created, parent-symlink, temporary-cleanup, and interrupted-write controls pass. |
| Unchecked and test semantic helpers were callable outside path verification | Every registered-curve, legacy-row, density-row, document-value, production test-wrapper, and path-worker semantic entry requires the identity-checked active path permit before mathematical work. Public direct row APIs remain disabled. Repository tests inject the internal sentinel by test-file introspection and remain non-evidence; the production module exports no permit factory. |
| Raw work charging accepted weak amount types | The mutation boundary accepts only exact positive integers. Boolean, zero, negative, float, string, and null amounts raise before changing a counter. Existing completed undercharge controls suppress or reduce a positive charge without calling the mutation API with zero. |

## Filesystem boundary

The target worktree is on exFAT. Both hard-link publication and macOS
`RENAME_EXCL` returned `ENOTSUP` in the focused control. V12 therefore retains
those atomic no-overwrite paths where supported and explicitly falls back to a
descriptor-relative `O_EXCL` destination write on exFAT.

The fallback prevents overwrite and parent-component substitution, but it can
expose an incomplete destination if interrupted after the exclusive open.
Such a path is not accepted: successful writer return and the complete report
hash are both required, and the path may never be reused. An immutable external
artifact store remains a future runner obligation.

## Claim boundary

The exact completed canonical provenance/predicate vector remains
`480/112/336/218/4218`; frozen expectations remain zero. These are verifier
work receipts, not density-frontier outcomes.

The three legacy controls are not new evidence. No relation yield, matrix rank,
linear algebra, target descent, fixed-curve preprocessing crossover, rho
improvement, fitted exponent, deployment result, or ECDLP break is established.
The candidate remains `HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`, and
`NOVELTY-UNVERIFIED`.

## Next action

Validate records and ledger, freeze exact V12 artifact hashes, commit one exact
snapshot, and request fresh read-only theory, accounting, and red-team review.
Keep `maximum_runs=0`; do not design a launch plan without three explicit
scoped GO decisions on the committed V12 bytes.
