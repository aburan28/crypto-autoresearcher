# Controlled follow-up report destination collides with immutable failed-attempt evidence

- **Status:** `open`
- **Kind:** governance / artifact destination assignment gap; no mathematical obstruction
- **Affected work:** [TASK-20261029-2f1fc7 and TASK-20261029-95abc9](../coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-cbf9d7/dispatch_queue.json); [DEC-20261030-adcc31](../ledger/decisions/DEC-20261030-adcc31.yaml)
- **Next action owner:** root publishes prospective repair; existing composition2f then final archive95
- **Last updated:** 2026-10-30

## Problem

The unclaimed successor composition and final archive cannot lawfully write their assigned four report files because `docs/reports/classical-ecdlp-controlled-followup-20261029/observations` already holds the immutable old EXP-ECDLP-956f81 / RUN-ECDLP-c8d9b0 / TASK-20261029-7e2652 failed-attempt report. The replacement destination is the fresh sibling `docs/reports/classical-ecdlp-controlled-followup-20261029/observations-080f41`. This changes report destination assignment only; original observation completeness, independent review, committed-source metrics and archival obligations remain intact.

## Evidence and uncertainty

- **Observed:** the current BATCH-cbf9d7 queue assigns all four old destinations in2f outputs and95 inputs; both tasks are queued and their standard epoch1 claim/release files are absent. All four old files exist. Their exact byte lengths/hashes, queue-before/after hashes and primary-source inventory are in [the amendment](../coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-cbf9d7/report-destination-repair-adcc31/amendment.json). The old observations identity is `classical.ecdlp.controlled-followup.failed-observations/v1`, EXP-ECDLP-956f81/RUN-ECDLP-c8d9b0.
- **Derived:** writing those exact destinations would overwrite immutable evidence. This follows from path equality, not a scientific outcome or an assumption about the successor run.
- **Suspected explanation:** a reused report scaffold; cause is not independently established and is unnecessary for this repair.
- **Missing capability:** published prospective destination and separate new metrics-reader assignment. The old `controlled_followup_observations` reader and `tools/test_progress_metrics_controlled_followup.py` specifically bind old failure evidence and stable `controlled.c8d9b0.*` series; they cannot be repointed.
- **What this evidence does not establish:** no successor scientific observation, review verdict, counter/clock qualification, performance gain, hypothesis transition or mathematical negative. Current active review artifacts and current scientific outcomes were not read.

## What would unblock it

- [ ] Root publishes the exact prospective2f/95 amendment assigning all four fresh `docs/reports/classical-ecdlp-controlled-followup-20261029/observations-080f41` files, unchanged dependencies and active review/c09 bindings, with linked DEC/problem/minimal index row and final95 custody.
- [ ] Before composition dispatch, verify the four old payload hashes and old reader/fixture remain unchanged, all four new destinations are absent, and2f remains unclaimed until unchanged dispatch gates pass.
- [ ] Future2f creates only its assigned new reports and a separate source-bound reader/fixture; historical report/reader/fixture/IDs remain preserved. Final95 binds its uniquely owned repair artifacts and actual2f outputs through unchanged source_task_ids in a verified pushed reachable archive; the admission-owned queue receives separate manual actual-Git verification metadata without duplicate95 ownership.

These conditions resolve the destination/custody obstruction. They do not satisfy scientific validation, source/native/postrun qualification, interpretation, independent-review or final6be076 obligations by themselves. This record alone resolves nothing.

## Next discriminating step

- **Action:** root compares the proposed queue with the current queue after frozen reviewer inventories finish and before any composition claim.
- **Inputs and controls:** exact old four payload hashes; existing queue before/after hashes; all other task objects byte-equivalent; source read-only reader/fixture hashes; fresh sibling path absent; [DEC-20261030-adcc31](../ledger/decisions/DEC-20261030-adcc31.yaml).
- **Execution limits and stop condition:** governance-only file/hash comparison and publication; maximum scientific runs0. No SDK/network/probe, nonce, curve work or active review access. Source implementations and all frozen records remain untouched.
- **Outcomes and next actions:** matching preconditions permit root-only publication and later existing gated2f dispatch; changed queue/claims/destinations or hash mismatch require root to stop materialization and prepare another additive correction from actual bytes. Infrastructure failure preserves this obstruction and authorizes no scientific inference.
- **Recheck trigger:** root is ready to publish after both reviewers finish frozen inventories, then before2f claim and before95 receipt verification.

## Resolution and history

Unresolved. This prospective repair is prepared outside the repository. Actual root materialization, publication and final95 custody remain required. Old B19 records and their historical wording remain byte-exact; final DEC-20261029-6be076 stays assigned and unwritten here.

V2 administrative history: unchanged validate_queue refused V1 before materialization because queue ownership overlapped082433/95. V2 removes duplicate95 queue/source-output ownership while preserving source_task_ids, dependencies and active review/c09 bytes. This is a governance correction with no scientific implication.
