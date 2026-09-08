# Independent custody review supplement

Operational review task: TASK-20260907-cbdf6e. Reviewed committed snapshot: `7e9b565c2aaa9e38ad5bbdce4a58f9758eb2c3cb`. Comparison base: `3c70a0b50cbaefc3fc5c168c51c0f54a405119e9`. Plan: `coordination/integrity/CORR-20260907-e6f0f7/supplement-review-plan.json`.

**PASS / holds on all three supplement scopes. No blocking finding.** The three new manifest versions preserve their predecessors and payloads; the FAEST action correction preserves its history; and the seven custody queues remain prospective with unchanged scientific goal status. This is an administrative artifact and contract review, not a scientific validation, an execution receipt, or a finding that historical custody defects have been resolved.

This supplement is separate from the original `4f15ab57` review. The original report's committed copy in this snapshot has SHA-256 `d54b1c52a9b2d32ecc3faba645a4b46ff627970c12b93cea832b57976222dc2e`, matching the issued original report. That report and its original verdict were not overwritten.

The reviewer is the same independent validator subagent `/root/integrity_review`, which did not produce these changes. No sibling report was read. Policy requested: `review-adversarial`, reasoning requested: `xhigh`, no fallback or degradation. Runtime instructions identify the Codex/GPT-6 family, but exact resolved model/backend telemetry and actual reasoning-effort verification remain unavailable. No model probe or cross-model-independence attestation is invented. The prior role and harness contracts continue to govern this bounded task; no experiments were executed and no repository file was written by this reviewer.

## Three v3 replacement manifests

For each row of `merged-supersession-completions.json`, I read the original, v2, and v3 blobs at the frozen snapshot and the original/v2 blobs at the merge base. All three source-manifest bytes and all three v2 bytes are unchanged from the merge base. Every original, v2, and v3 SHA-256 matches the completion record: nine digest checks passed.

Removing exactly `run.supersedes` and `run.replaces_schema_record` from each parsed v3 produces a value exactly equal to its parsed v2. No original payload field, status, observation, timing, input, certificate, or scientific limit changes between v2 and v3. The new `supersedes` fields bind each preserved original path/hash; `replaces_schema_record` binds the preserved v2 path/hash. Registry entries retain the original source path/hash and point to the correct new v3 path/hash.

| Run | v3 SHA-256 | Outcome |
| --- | --- | --- |
| RUN-JMV-001-a | `ff34d598d10e96ae09ad4c5f8bd743b398187b1fffef28c2416c8b19de09691a` | PASS |
| RUN-JMV-004-a | `7b53958deb3cdd8647250161d0a7525fdc7d06896b6c78e5cd33839dd223e576` | PASS |
| RUN-CSIDH-c65945-001 | `69e69f848cac526291309b16d9d69811bc40991abb7731d443dc26e8c0c1fed7` | PASS |

This admits the metadata addition relative to the preserved v2 payload. It does not independently endorse the prior v2 repair's scientific assertions or historical runtime provenance. The base-to-snapshot diff adds only these three files under `experiments/`; it modifies no existing experiment/run file and no hypothesis record.

## FAEST historical action and current instruction

At `ledger/goals/GOAL-FAEST-001.yaml`, the new `next_action_prior_integrity_20260907` value exactly equals the merge-base `next_action` after YAML decoding. Both historical note values (`dispatch_queue_path_note_20260810` and `dispatch_queue_path_note_head_sweep_20260818`) are unchanged. The dated 20260907 note explicitly explains that the queue exists and that the old no-queue note is historical.

Only three goal fields differ from the merge base: the current `next_action`, the added prior-action field, and the added dated note. The current action directs resumption of existing BATCH-0ed590 at Coordinator archive TASK-20260826-07f458 after refreshing the claim-aware plan and verifying producer artifacts, and forbids recreating the queue or duplicating producers. The inherited RSF-5 requirements, citation corrections, and scientific limits remain in the preserved action; `status` remains `active`.

Original advisory A1 is addressed by this committed supplement. I am not asserting that TASK-20260826-07f458 is ready in a live session: the current instruction explicitly requires a fresh plan and artifact check, which remain the responsible Coordinator's next operational steps.

## Seven prospective custody contracts and selected goal pointers

I independently checked each new queue against the approval decision, its corresponding original queue and exact copied original, the merge-base goal head, the new goal head, the preserved whole-goal backup, the lane record, and the stored queue-validation JSON.

For all seven goals:

- The original queue bytes remain equal to the merge base and equal to the copied `original-dispatch-queue.json`. Their SHA-256 values match `recovery-contracts.json`.
- Every whole-goal backup under `goal-heads-before/` is byte-identical to that goal's merge-base file.
- Every new queue's raw SHA-256 matches its approved value in DEC-20260907-46aa8f. Queue task IDs match the recovery-contract record, and the goal's current batch and queue pointer select that same queue.
- All four tasks are `queued`, in the role order executor, Coordinator snapshot, independent validator, Coordinator administrative ledger archive. Both run-count fields are zero for all 28 handoffs.
- Dependency chains require the producer before snapshot, producer and snapshot before validator, and validator before administrative archive. Every validator requests `review-adversarial`/`xhigh`, an independent session, and forbids fallback/degradation.
- All 14 archive bindings retain null commit/parent and empty hash maps. No declared future task output path exists in the frozen tree. The comparison diff creates no claim record for these tasks. These are checks of recorded state, not independent process telemetry proving no activity anywhere outside this snapshot.
- The seven goal statuses are `active` before and after. Every existing goal field except `current_batch_id`, `dispatch_queue_path`, and `next_action` is exactly equal after YAML decoding. The only other change is the added `integrity_recovery_20260907` block, whose `prior_selection` exactly preserves those three prior field values. Objectives, hypothesis lists, criteria, budgets, impediments, checkpoints, and all other existing fields remain unchanged.

| Goal | Selected recovery batch | Task state |
| --- | --- | --- |
| GOAL-ENDO-001 | BATCH-4acfee | 4 queued |
| GOAL-MLKEM-005 | BATCH-203eff | 4 queued |
| GOAL-ICEX-001 | BATCH-1104d5 | 4 queued |
| GOAL-SIG-001 | BATCH-0c2d2a | 4 queued |
| GOAL-CRYPTO-001 | BATCH-1f4d53 | 4 queued |
| GOAL-MD5-001 | BATCH-f1f479 | 4 queued |
| GOAL-MCE-001 | BATCH-538e87 | 4 queued |

The queue objectives/constraints preserve original failures, prohibit historical hash retargeting or remaps, distinguish a new custody archive from validation of an old archive, and require explicit missing-source outcomes. MCE's producer explicitly leaves the citation/report repair and further independent scientific review unresolved; MD5's producer preserves failed/partial review scopes and requires successor checks before any completion citation. DEC-20260907-46aa8f explicitly forbids treating custody completion as discharge of MD5/MCE substantive gaps or as scientific promotion.

The seven stored dispatch plans contain one proposed producer dispatch each, empty terminal lists, and empty claims maps. Their `plan_sha256` values independently reproduce. Their `source_queue_sha256` values also reproduce after the dispatcher's documented scope normalization: `tools/research_dispatch.py:208` removes a trailing slash from scope values, lines 619/622 normalize task read/write scopes, and lines 75/81 hash canonical JSON. The plan source hashes are therefore not the raw queue file hashes; the distinct raw hashes are correctly used by the Coordinator approval decision. No stale-source finding remains after applying the actual normalization. This source/self-hash check does not claim a fresh full dispatch render or independently re-run every gate represented in the stored plan.

## Limits and handoff

This report binds only snapshot `7e9b565c` relative to base `3c70a0b5`. Remote merges, subsequent local merges, the follow-up PR, and any later execution are outside its verdict. The expanded historical AES/5cad48 read permissions were not used anew in this supplement. Historical documents named inside recovery contracts were not audited as actual recovered packages; that work is the still-queued producer and subsequent independent custody review.

No scientific measurements, certificate verifications, full-ledger validation, fresh full test suite, or live claim refresh were performed here. The actual independent work consists of immutable blob comparisons, SHA-256 recomputation, parsed-value equality checks, artifact-existence inventory, and static review of prospective task contracts. The Coordinator owns durable archival of this new report and any subsequent action.

```yaml
validation_report:
  task_id: TASK-20260907-cbdf6e
  scope: committed administrative supplement
  snapshot_commit: 7e9b565c2aaa9e38ad5bbdce4a58f9758eb2c3cb
  base_commit: 3c70a0b50cbaefc3fc5c168c51c0f54a405119e9
  run_ids:
  - RUN-JMV-001-a
  - RUN-JMV-004-a
  - RUN-CSIDH-c65945-001
  artifact_checks:
  - All three original/v2 pairs unchanged from merge base
  - All nine original/v2/v3 hashes match
  - All three v3 payloads equal v2 after removal of exactly two new metadata fields
  - All three registry bindings match
  - FAEST historical action and both dated notes preserved
  - Seven original queues and whole-goal backups preserved
  - Seven approval queue hashes match
  - All28 tasks queued and zero-run; all14 archives unbound
  - All seven goal states and other scientific fields unchanged
  - All seven normalized plan source hashes and self hashes match
  - Original review committed copy hash unchanged
  metric_recomputations: []
  control_checks: []
  heuristic_validation_checks: []
  cost_model_checks: []
  proof_architecture_checks: []
  verdict: passed
  limitations:
  - Administrative supplement scopes only
  - No historical custody completion or scientific validation
  - No live runtime/claim readiness attestation
  - Exact resolved model and actual effort telemetry unavailable
  artifact_paths:
  - /private/tmp/coordinator-a-recovery/independent-review-supplement.md
```

```yaml
review_attestation:
  task_id: TASK-20260907-cbdf6e
  review_plan: coordination/integrity/CORR-20260907-e6f0f7/supplement-review-plan.json
  joints_owned:
  - Three new v3 supersession declarations preserve original and v2 bytes and all
    original payload fields
  - FAEST current action correction preserves historical action
  - Seven recovery queues remain prospective and scientific status unchanged
  joint_verdicts:
  - scope: Three new v3 supersession declarations preserve original and v2 bytes and
      all original payload fields
    verdict: holds
  - scope: FAEST current action correction preserves historical action
    verdict: holds
  - scope: Seven recovery queues remain prospective and scientific status unchanged
    verdict: holds
  requested_policy: review-adversarial
  requested_reasoning_effort: xhigh
  resolved_model_id: null
  actual_reasoning_effort_verified: false
  model_verified: false
  independent_session: true
  sources_read:
  - coordination/goals/GOAL-CRYPTO-001/batches/BATCH-013/dispatch_queue.json
  - coordination/goals/GOAL-CRYPTO-001/batches/BATCH-1f4d53/dispatch_queue.json
  - coordination/goals/GOAL-CRYPTO-001/batches/BATCH-1f4d53/original-dispatch-queue.json
  - coordination/goals/GOAL-CRYPTO-001/batches/BATCH-1f4d53/queue-validation.json
  - coordination/goals/GOAL-CRYPTO-001/lanes/BATCH-1f4d53.lane.json
  - coordination/goals/GOAL-ENDO-001/batches/BATCH-4acfee/dispatch_queue.json
  - coordination/goals/GOAL-ENDO-001/batches/BATCH-4acfee/original-dispatch-queue.json
  - coordination/goals/GOAL-ENDO-001/batches/BATCH-4acfee/queue-validation.json
  - coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/dispatch_queue.json
  - coordination/goals/GOAL-ENDO-001/lanes/BATCH-4acfee.lane.json
  - coordination/goals/GOAL-ICEX-001/batches/BATCH-001/dispatch_queue.json
  - coordination/goals/GOAL-ICEX-001/batches/BATCH-1104d5/dispatch_queue.json
  - coordination/goals/GOAL-ICEX-001/batches/BATCH-1104d5/original-dispatch-queue.json
  - coordination/goals/GOAL-ICEX-001/batches/BATCH-1104d5/queue-validation.json
  - coordination/goals/GOAL-ICEX-001/lanes/BATCH-1104d5.lane.json
  - coordination/goals/GOAL-MCE-001/batches/BATCH-538e87/dispatch_queue.json
  - coordination/goals/GOAL-MCE-001/batches/BATCH-538e87/original-dispatch-queue.json
  - coordination/goals/GOAL-MCE-001/batches/BATCH-538e87/queue-validation.json
  - coordination/goals/GOAL-MCE-001/batches/BATCH-73a1b7/dispatch_queue.json
  - coordination/goals/GOAL-MCE-001/lanes/BATCH-538e87.lane.json
  - coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02/dispatch_queue.json
  - coordination/goals/GOAL-MD5-001/batches/BATCH-f1f479/dispatch_queue.json
  - coordination/goals/GOAL-MD5-001/batches/BATCH-f1f479/original-dispatch-queue.json
  - coordination/goals/GOAL-MD5-001/batches/BATCH-f1f479/queue-validation.json
  - coordination/goals/GOAL-MD5-001/lanes/BATCH-f1f479.lane.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-203eff/dispatch_queue.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-203eff/original-dispatch-queue.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-203eff/queue-validation.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-762807/dispatch_queue.json
  - coordination/goals/GOAL-MLKEM-005/lanes/BATCH-203eff.lane.json
  - coordination/goals/GOAL-SIG-001/batches/BATCH-002/dispatch_queue.json
  - coordination/goals/GOAL-SIG-001/batches/BATCH-0c2d2a/dispatch_queue.json
  - coordination/goals/GOAL-SIG-001/batches/BATCH-0c2d2a/original-dispatch-queue.json
  - coordination/goals/GOAL-SIG-001/batches/BATCH-0c2d2a/queue-validation.json
  - coordination/goals/GOAL-SIG-001/lanes/BATCH-0c2d2a.lane.json
  - coordination/integrity/CORR-20260907-e6f0f7/goal-heads-before/GOAL-CRYPTO-001.yaml
  - coordination/integrity/CORR-20260907-e6f0f7/goal-heads-before/GOAL-ENDO-001.yaml
  - coordination/integrity/CORR-20260907-e6f0f7/goal-heads-before/GOAL-ICEX-001.yaml
  - coordination/integrity/CORR-20260907-e6f0f7/goal-heads-before/GOAL-MCE-001.yaml
  - coordination/integrity/CORR-20260907-e6f0f7/goal-heads-before/GOAL-MD5-001.yaml
  - coordination/integrity/CORR-20260907-e6f0f7/goal-heads-before/GOAL-MLKEM-005.yaml
  - coordination/integrity/CORR-20260907-e6f0f7/goal-heads-before/GOAL-SIG-001.yaml
  - coordination/integrity/CORR-20260907-e6f0f7/independent-review.md
  - coordination/integrity/CORR-20260907-e6f0f7/merged-supersession-completions.json
  - coordination/integrity/CORR-20260907-e6f0f7/recovery-contracts.json
  - coordination/integrity/CORR-20260907-e6f0f7/supplement-review-plan.json
  - experiments/EXP-CSIDH-c65945/runs/RUN-CSIDH-c65945-001/manifest.yaml
  - experiments/EXP-CSIDH-c65945/runs/RUN-CSIDH-c65945-001/manifest_integrity_v3.yaml
  - experiments/EXP-CSIDH-c65945/runs/RUN-CSIDH-c65945-001/manifest_v2.yaml
  - experiments/EXP-JMV-001/runs/RUN-JMV-001-a/manifest.yaml
  - experiments/EXP-JMV-001/runs/RUN-JMV-001-a/manifest_integrity_v3.yaml
  - experiments/EXP-JMV-001/runs/RUN-JMV-001-a/manifest_v2.yaml
  - experiments/EXP-JMV-004/runs/RUN-JMV-004-a/manifest.yaml
  - experiments/EXP-JMV-004/runs/RUN-JMV-004-a/manifest_integrity_v3.yaml
  - experiments/EXP-JMV-004/runs/RUN-JMV-004-a/manifest_v2.yaml
  - ledger/decisions/DEC-20260907-46aa8f.yaml
  - ledger/goals/GOAL-CRYPTO-001.yaml
  - ledger/goals/GOAL-ENDO-001/goal.yaml
  - ledger/goals/GOAL-FAEST-001.yaml
  - ledger/goals/GOAL-ICEX-001.yaml
  - ledger/goals/GOAL-MCE-001/goal.yaml
  - ledger/goals/GOAL-MD5-001.yaml
  - ledger/goals/GOAL-MLKEM-005.yaml
  - ledger/goals/GOAL-SIG-001.yaml
  - tools/research_dispatch.py
  - tools/run_supersession_registry.yaml
  source_read_note: Pinned snapshot and comparison-base blobs only. Includes structured/content
    reads and byte-only hash/equality reads. Governing contracts were read during
    the original review and remain applicable; no sibling report was read.
  read_sibling_reports: false
  blind_from_respected: null
  verdict: holds
```
