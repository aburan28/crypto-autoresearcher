# EXP-SGCP-EMBED-002 revision response v7

## Scope

V7 repairs the fail-fast admission, resource accounting, partial receipt,
nonblocking input, diagnostic, source-hash, zero-row-control, and independent
candidate-transcript findings from all three V6 reviews. It creates no
generated density row, canonical matrix, runner, launch plan, or execution
authorization.

## Finding closure

| V6 finding | V7 response |
|---|---|
| Registered curve derivation preceded row authentication and reservation | Static preflight now authenticates exact types, row digest, protocol, validity, ordering, scope, grid association, source-owned caps, objective, exact empty frontier, masks, and B-derived transcript lengths. The frozen transcript is built without point enumeration. Canonical curve derivation begins only after a source-bounded reservation is recorded. |
| A generated Mobius density row violated the zero-row evidence boundary | The control now builds only the generated curve and factor-base record, then independently checks the Mobius transcript. The sole density row remains the frozen p=19, B=4 fixture. |
| The standalone B4 oracle compared aggregates but not complete candidate and eligible lists | The standalone oracle now records every candidate formal, EC point, and sorted recursive parent pair, plus the complete eligible list. Both lists are directly exact-compared with verifier reconstruction. |
| FIFO input could block and oversized input was rejected only after reading beyond the trusted size | The final component is opened with `O_NONBLOCK` and `O_NOFOLLOW`, then checked by `fstat`. Initial `st_size` is rejected before the first read. Controls cover FIFO, directory, final symlink, sparse oversized file, changing snapshot, and disclosed parent-component symlink traversal. |
| Oversized masks, nonempty frontiers, wrong objectives, and late-invalid rows reached expensive work | Static B-derived admission checks canonical hex length/range, selected indices/formals, exact empty frontier, objective mode/order/bound, cache receipts, factors, representatives, graph transcripts, edge/source tables, and expansion histograms. Patched curve, replay, and proof helpers receive zero calls for these mutations. |
| Replay or proof exceptions discarded reservation and prior work | Rows run sequentially. Every cap stage catches and receipts failures. Injected second-cap replay and primary-proof failures preserve the reservation, the first cap, two cap receipts, measured counters, nested error, failing phase, and `actual_work_complete=false`. |
| Phase receipts were not truthful on every partial path | Curve/graph, replay, retained-model, and primary-proof phases are marked at their call sites. A later failure changes an earlier pass to failed. `independent_checks` includes only final passed phases. |
| Diagnostic count and bytes were unbounded | All verifier diagnostics use source ceilings of 256 items, 65,536 ASCII bytes total, and 2,048 bytes per item. Unexpected-key samples are count-bounded. An amplified forbidden-key control proves truncation. |
| Verifier source hashing reopened a mutable path and did not attest executed code | SHA-256 is frozen once at module load, never recomputed while reporting, labeled diagnostic-only, and accompanied by `verifier_source_attested=false`. Immutable commit/command attestation remains a future runner duty. |
| Curve, predicate, point-enumeration, cache, and retained-model work receipts were incomplete | The reservation now separates registered prime candidates, curve draws/hashes/point enumerations, predicate hashes, semantic and primary point enumerations, expansion/graph cells, replay/proof nodes, both replay caches, both primary caches, and retained-model calls/cells. Producer optimizer and full-model cache entries are source-enforced and authenticated per cap. |
| Gate threshold fixtures did not pin exact persistence equality | A hand-derived control accepts exact `1/4` in every stratum and rejects `999/4000` in one stratum. Existing duplicate-null, collapse, count, stratum, and anti-splicing boundaries remain. |

## Claim boundary

The mathematical candidate is unchanged. V7 improves finite verifier integrity
and work visibility but adds no evidence that a coordinate predicate beats a
hash-ranked control. The complete 46-test focused suite constructs no generated
density row and consumes no run budget.

Cache-entry ceilings are source-enforced structural bounds, not allocator-byte
or RSS measurements. JSON parser allocation, Python object overhead, wall time,
peak RSS, process count, disk, I/O, and memory bandwidth remain obligations of
a future immutable external runner.

Even a future complete PASS would remain `TOY-EVIDENCE`, `MODEL-BOUND`, and
`NOVELTY-UNVERIFIED`. It would not establish relation yield, matrix rank,
linear-algebra cost, target descent, fixed-curve preprocessing advantage, a
fitted exponent, a rho improvement, or an ECDLP break.

## Next action

Validate records and ledger, freeze exact V7 artifact hashes, commit one exact
snapshot, and request fresh read-only theory, accounting, and red-team review.
Keep `maximum_runs=0`. Do not design a launch plan unless all three reviewers
explicitly authorize that separate design step.
