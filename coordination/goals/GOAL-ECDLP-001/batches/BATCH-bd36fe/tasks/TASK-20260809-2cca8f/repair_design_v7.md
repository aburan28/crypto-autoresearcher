# BATCH-bd36fe v7 executable control repair

This is a superseding, design-only control repair after the independent v6
review `TASK-20260809-46ba3c` returned `REVISE`. The archived v6 snapshot and
all v4/v5 records remain immutable. The v7 package does not implement ECDLP,
define a frozen experiment, authorize an Executor, execute a run, create
evidence, or change research status.

## Residual findings and closure

| v6 review finding | v7 closure |
|---|---|
| Arithmetic selection/lift binding | Bind the canonical integer-search bounds and selection, derive the exact first lexicographic order-6 point, recompute lift roots, selected root, point encoding, input-domain text, and the canonical synthetic `F`/`R_star` values. The selected lift root must equal the selected point's y-coordinate. |
| Empty or phase-collapsed event stream | Require a nonempty stream whose phase indices are nondecreasing, every declared phase occurs, and first-occurrence order is exactly input → curve → factor_base → table → query → verify → serialize. The v6 event equations still run first. |
| Accepted cases and manifest authority | Apply a strict v7 JSON Schema to every v6 accepted case, check the complete case payload against the v6 contract, and introduce a v7 manifest whose validator version and strict mutation list are explicitly checked. Malformed unattempted-arm fields are rejected. |
| Matrix run/source binding | Add a deterministic per-arm run-index rule and key digest check for all 400 arms. Resolve every legacy source-blob token through a v7 source-binding record and recompute each referenced v6 source hash plus the matrix hash. |
| Stale embedded validator command | Preserve the stale v6 command as historical immutable input, but make a corrected v7 metadata record authoritative. The v7 validator rejects any metadata that still uses `--control-fixtures` and validates the v7 command scope. |

## Execution boundary

`validate_xor_v7.py` invokes the exact v6 fixture-only command as a predecessor
gate, then performs the v7 strict checks and twelve declared in-memory
mutations. It reads the v6 canonical run, event ledger, matrix, accepted cases,
and source artifacts; it never writes them. A successful `VALIDATION_PASS`
means only that the synthetic control package rejects the named malformed
records. It is not an ECDLP observation, a performance result, a security
claim, or an approval to run.

The next gate remains a fresh independent `review-adversarial` review of the
archived v7 package. Only a passing review can permit a separate Coordinator
specification/freeze task.
