# Polynomial claim authority and durable progress observability

- **Status:** investigating
- **Kind:** operational authority limit and missing progress observability; not a mathematical obstruction
- **Affected work:** RQ-IC-a39c7e, EXP-IC-66c447/RUN-IC-0d0c36, original Executor TASK-20261015-ff93a4; [actual terminal receipt](../experiments/EXP-IC-66c447/runs/RUN-IC-0d0c36/execution-receipt.json), [failure custody route](../research/lattice_ic_experiments_20261015/coordinator/polynomial-authority-failure-custody/actual-failure-inputs.json)
- **Next action owner:** Coordinator/root for custody TASK-20261015-8f73c8 and TASK-20261015-df3e06; telemetry Executor TASK-20261015-9638c0 under published source queue, then Coordinator fresh admission after accepted source
- **Last updated:** 2026-10-15

## Problem

The actual polynomial attempt exhausted its unchanged cached claim authority before writing complete results, and retained logs do not identify the scientific stage or completed-cell count.

The prescribed same-grid computation retains three prime curves, windows 2/4/8, m2/3 exact expanded reductions and m2/3/5 complete density oracles, fixed t/L/target/cohort/support/caps/controls, seed1729, one worker and the original 2 GiB guard. The approved specification declares no scientific wall-time cap. The run's cached authority expired at 2026-10-15T10:43:30+00:00; this operational boundary is not a scientific criterion.

## Evidence and uncertainty

- **Observed:** Native receipt status `claim_expired`, started 2026-10-15T08:43:58.076644+00:00 and finished 2026-10-15T10:43:30.038197+00:00. Driver and checker returncodes, detail and scientific conclusion are null. Exactly eight actual runtime files exist; raw-result.json and manifest.yaml are absent. Stderr is empty. Neither authority nor cached supervisor deadline was changed.
- **Derived:** Source serializes raw/manifest only after the fixed run function returns; their absence does not locate the unfinished stage. The receipt and bytes support only this operational outcome, not a completed-cell or useful-yield estimate.
- **Unknown:** Scientific cell/stage, prior completed cells, exact HNF/LLL state, per-phase time, CPU time, peak RSS, achieved norms, finite extraction, root yield and rank at expiry. Earlier observed CPU activity is not proof of useful progress or current stage.
- **Missing capability:** Durable cell/stage events in already captured stderr, and an upfront normal authority window suited to a potentially lengthy unchanged schedule.
- **Does not establish:** HNF repair failure, LLL defect, mathematical falsification, no useful roots/relations, performance or ECDLP advantage. The separate [original MemoryError obstruction](lattice-ic-integer-hnf-memory-growth.md) remains investigating; its historical traceback does not identify this attempt's stage.

## What would unblock it

- [ ] Publish actual runtime8, actually inspected terminal report and a distinct native-verified administrative actual8+own receipt9 checkpoint. Retain original scientific10 archive TASK-20261015-da409a incomplete and both missing outputs absent.
- [ ] Only afterward, publish a narrowly scoped source task implementing durable flush+fsync JSONL events to already captured stderr at real cell/stage starts and finishes. Meaningful synthetic durability, injected exception/termination, logging failure and semantic parity controls pass; source is independently archived before new admission. Partial events never score scientific completion.
- [ ] A prospective fresh EXP/RUN and additive amendment preserve exact equality of the full science configuration, controls/caps/criteria/seed and 2 GiB. New source/spec/plan/claim closures, native ready check, Coordinator standing-authority approval and published native snapshot precede execution. Use a normal upfront 1440-minute claim as an operational envelope, without midflight deadline changes or a completion guarantee.
- [ ] The new admitted attempt either completes the full grid and separate checker, or preserves its exact operational outcome with a known last durable cell/stage boundary. No outcome may be inferred before it exists.

These conditions would improve observability and authority scheduling; only actual validated complete outputs and independent review could establish a scientific result. They do not prove the schedule will complete within any selected lease.

## Next discriminating step

- **Action:** Complete the [actual failure custody](../research/lattice_ic_experiments_20261015/coordinator/polynomial-authority-failure-custody/dispatch-queue.json), then review the guarded scratch-only conditional telemetry/same-grid successor plan. The narrowly scoped [source handoff](../ledger/handoffs/TASK-20261015-9638c0.yaml) is prepared after actual published9 custody and native proof; its source queue must be published before a normal claim. Fresh scientific specification/plan/approval remain ungenerated.
- **Inputs and controls:** Immutable current terminal receipt/files; original source/spec/plan; identical full science hash; injected telemetry exceptions/termination/I/O failures and synthetic microfixture semantic parity. Tests must not execute the full scientific grid.
- **Execution limits:** Custody and source maintenance use zero scientific runs, one worker, 2 GiB. Future fresh execution retains the full original scope, one run/worker and 2 GiB; no new scientific wall-time cap, adaptive skipping, checkpoint replay or reuse of partial cells.
- **Outcomes:** A successful telemetry implementation permits only source archival and prospective same-grid admission. A logging defect blocks admission and gets a concrete software repair. Another terminal operational failure is preserved without mathematical inference. A completed grid still requires full independent review.
- **Recheck trigger:** Actual native failure9 proof, accepted telemetry source, then actual prospective ready admission and terminal outcome.

## Resolution and history

2026-10-15: opened only after the real `claim_expired` receipt appeared. No frozen file, original source archive, authority, supervisor or scientific result was modified. All future full-review gates additionally require this retained failure9 alongside the prior failure9, all four eventual successful observations, preserved old blind8 and replacement own8, and explicit SAME replacement Reviewer unblind.

Unresolved. The source repair and successor admission remain prospective until actual custody and their own gates are fulfilled.


2026-10-15 custody update: original runtime8 are published at 361275d76b4ab41f54528fe73c2dd4c5bcec83dc, the six-file terminal report at 50887941b4f628a629ef71931350bfeba080b7be (root reports both PDF pages actually inspected), and the distinct nine-content-path checkpoint at 56b8aeec3274c4a30e89b0213f99ccd6e347c946 (only one new own-receipt path). [Native proof](../research/lattice_ic_experiments_20261015/coordinator/polynomial-authority-failure-custody/snapshot-git-verification.json) verifies all9 content hashes and parent/IDs. Original scientific10 remains incomplete. The guarded conditional planner then minted prospective EXP-IC-9f9a4b/RUN-IC-fe080b reservations and prepared only telemetry source maintenance TASK-20261015-9638c0/archive TASK-20261015-ee7fbc; no canonical scientific specification/plan or trial approval exists. Full scientific configuration equality is required, not inferred from a logging change.
