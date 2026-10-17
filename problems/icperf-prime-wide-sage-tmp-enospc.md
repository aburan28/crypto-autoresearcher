# Prime 63-bit Sage backend precheck exhausted frozen temporary storage

- **Status:** `resolved` for the frozen scratch and claim-publication precheck; full-width solver feasibility remains open in [the IC arity-grid problem](full-width-ic-arity-grid-unmeasured.md)
- **Kind:** resource limit; claim-publication access/tool limit
- **Affected work:** [TASK-20261017-6b60b8](../ledger/handoffs/TASK-20261017-6b60b8.yaml), [BATCH-25c5e3](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-25c5e3/dispatch_queue.json), [DEC-20261017-41a497](../ledger/decisions/DEC-20261017-41a497.yaml), and [the full-width IC arity grid](full-width-ic-arity-grid-unmeasured.md)
- **Next action owner:** Coordinator for a separately runnable solver-to-certificate pilot; Executor for its prospective launcher and checker
- **Last updated:** 2026-10-17

## Problem

The frozen 63-bit prime GF(p) backend engineering task could not pass admission on this macOS host because `TMPDIR=/private/tmp` had insufficient free space and the shell reported ENOSPC during input inspection; its local GOAL-lane claim also could not be published because the sandbox denied creation of the shared worktree `index.lock`. The task stopped before implementing the backend or starting any Sage controls. The resource and claim-publication faults are separate requirements for lawful retry.

## Evidence and uncertainty

- **Observed in the original attempt:** [validation.json](../research/icperf_prime_wide_backend_20261017/validation.json) classifies the task `not_started_resource_exhaustion` and every prescribed control `not_started`. [environment.json](../research/icperf_prime_wide_backend_20261017/environment.json), [raw stdout](../research/icperf_prime_wide_backend_20261017/test-stdout.log) and the [report](../research/icperf_prime_wide_backend_20261017/report.md) bind the frozen environment and show /private/tmp free space at 469 MiB, 110 MiB at the failed here-document, then 156 MiB. The shell error was transcribed from tool output because that invocation could not create its own log. The [claim](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-25c5e3/claims/TASK-20261017-6b60b8.1.claim.json) and [failed release](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-25c5e3/claims/TASK-20261017-6b60b8.1.release.json) were retained in the [corrective nine-path snapshot](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-25c5e3/archives/TASK-20261017-271dc0/snapshot-receipt.json). Four of eleven declared implementation/control artifacts never existed in that original task.
- **Derived or proved:** Neither the backend interface nor any planned control was tested in this attempt. The original eleven-file success snapshot TASK-20261017-8a1771 cannot correctly archive the seven-file partial output.
- **Suspected explanation:** Insufficient /private/tmp space caused the shell ENOSPC. The `index.lock` denial may be a separate sandbox permission issue; moving scratch alone does not prove claim publication will work.
- **Missing capability:** A task-specific writable SSD990-2 scratch root with bounded capacity and a published claim visible to the dispatcher, followed by independent Sage controls and exact partial-failure custody.
- **What this evidence does not establish:** It gives no solver, degree-of-regularity, factor-base, relation-yield, or end-to-end ECDLP evidence.

## What would unblock it

- [x] Archive the nine exact present precheck/claim/release files and verify absence of the four unproduced artifacts under [DEC-20261017-41a497](../ledger/decisions/DEC-20261017-41a497.yaml), with a [separate receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-25c5e3/archives/TASK-20261017-271dc0/snapshot-receipt.json) and no placeholder source files.
- [x] Freeze and archive [replacement TASK-20261017-68782f](../ledger/handoffs/TASK-20261017-68782f.yaml) with the same 64 field, 32 S3, four synthetic ideal, small-field m=2, and 21-system parse controls, and bounded task-specific SSD990-2 scratch.
- [x] Publish and independently read back the [replacement claim](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-25c5e3/claims/TASK-20261017-68782f.1.claim.json) from live refs before starting Sage; the [completed release](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-25c5e3/claims/TASK-20261017-68782f.1.release.json) is separately committed.
- [x] Complete the frozen controls and independent checker with exact raw logs and a [content-first source snapshot](../coordination/design/icperf-prime-wide-backend-retry-20261017/archives/TASK-20261017-d24229/snapshot-receipt.json) before any solver-panel approval.

These gates establish only an admitted, tested backend interface. They do not establish natural relation yield or complete index-calculus cost.

## Next discriminating step

- **Action or proof obligation:** Retest the direct pinned Sage binary and all original unit controls under the prospectively frozen SSD990-2 scratch setting after failure custody and claim publication.
- **Inputs and controls:** Reuse the nine frozen inputs and original control counts; preserve exact p=9223372021248595841 as a decimal string in JSON and independently check coefficients above 2^53. The old failure is a separate infrastructure observation, not a control outcome.
- **Execution limits and stop condition:** One process; original four-hour watchdog; new fixed scratch/RSS/free-space limits in the replacement handoff. Stop before a Sage call if the path is unwritable, capacity is low, or the claim is not published. Retain partial output.
- **Outcomes and next actions:** Passing all controls enables a separately approved solver pilot. Arithmetic/certificate disagreement returns for implementation repair. Resource or publication failure preserves a new infrastructure receipt and does not classify the backend mathematics.
- **Recheck trigger:** Reachable failed-precheck receipt, accepted replacement queue and a published task claim on a writable, bounded scratch volume.

## Resolution and history

2026-10-17: Opened after TASK-20261017-6b60b8 stopped before controls. The corrective custody and bounded retry were prospective at opening.

2026-10-17: Resolved the specific precheck obstruction through the archived failed-precheck receipt, prospectively corrected SSD retry, published live-ref claim, and [passing engineering-control record](../research/icperf_prime_wide_backend_retry_20261017/validation.json), bound by source snapshot commit `6a587d75d3c415cea4f7ea21a81a5618e359b667` and its separate receipt. The retry parsed all 21 archived systems without solving them; 64/64 field identities, 16/16 valid and 16/16 altered S3 triples, four ideals, and the small-prime m=2 enumeration control passed. The sampled supervisor and its failed earlier attempts are described in the [retry report](../research/icperf_prime_wide_backend_retry_20261017/report.md). This resolution admits no full-width solver result, relation yield, rank, target solve, matched rho comparison, or end-to-end speed claim. The next separately frozen solver-to-certificate pilot must implement a genuine 64-primary-model stop and full independent point certificates.
