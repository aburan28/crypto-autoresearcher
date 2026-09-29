# Correction Addendum — F1 of TASK-20260806-1c1103 validation report

**Supersedes:** finding F1 and the closing recommendation of
`validation-report.md` in this directory (that report is immutable and is left
exactly as the validator wrote it).
**Author role:** coordinator (NOT an independent validator session)
**Date:** 2026-08-13 (UTC)
**Status:** F1 remains OPEN. This addendum records a changed artifact; it does
not discharge the finding.

## What changed since the validation report

F1 recorded that `archives/TASK-20260806-621261/snapshot-receipt.json`
(SHA-256 `e52c8cd9…`) declared `commit_sha: 1d8fe80a…` with 3 path hashes while
the queue's `archive` block for the same task declared `commit_sha: 28458db3…`
with 4 path hashes, and asked the Coordinator to reconcile the two before the
ledger transition.

The receipt has since been regenerated. The on-disk receipt is now SHA-256
`e99eeb50…`; it carries no `commit_sha`, sets `commit_pending: false`, and
records under `unexpected_observations_recorded` that the first pass declared a
stale commit hash and that the binding lives in the queue's `archive` block.
That block now names `commit_sha: 7e140114…` over parent `f03eb9b4…` with four
`path_sha256` entries.

## Effect on the ledger gate

None yet. The regenerated receipt and the new commit binding are artifacts the
validator never saw, so no independent review covers them. The ledger
transition (`TASK-20260806-ccfd8b`) stays blocked on F1 until a new validator
task verifies the `e99eeb50…` receipt against the queue's `7e140114…` archive
block and the four declared path hashes.
