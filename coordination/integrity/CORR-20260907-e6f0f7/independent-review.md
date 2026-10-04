# Independent custody and code review

Task: TASK-20260907-cbdf6e. Frozen Coordinator snapshot: `4f15ab57f8ae76c4d8cff6deb78604485a077563`. Comparison base: `759fa5693d9f7ed77ef7e0c7f3520d0feb91f5a3`. Review plan: `coordination/integrity/CORR-20260907-e6f0f7/review-plan.json`.

**J1 PASS / holds; J2 PASS / holds; J3 PASS / holds.** No blocking defect was found in the assigned preservation, fallback, or scientific-boundary joints. One low-severity documentation advisory is recorded below. This report validates the administrative repair within those joints. It does not independently validate any cryptographic result, certificate, historical producer-valid label, research hypothesis, or goal closure.

The reviewer is a separate validator subagent (`/root/integrity_review`), did not produce the reviewed changes, and did not read sibling review reports. Requested policy is `review-adversarial`, requested reasoning effort is `xhigh`; fallback and degradation are forbidden by the plan. The runtime instructions describe a Codex agent based on the GPT-6 family. No exact resolved model identifier, backend attestation, model probe receipt, or independently observable actual reasoning-effort telemetry was exposed to this reviewer. Those fields remain unknown; this is not a fabricated model-verification or cross-model-independence attestation. The Coordinator must preserve that provenance limitation in archival use.

## J1: original preservation and source-grounded companions

The base-to-snapshot Git diff modifies no pre-existing experiment/run file and no pre-existing immutable evidence or checkpoint file. It adds the replacements and companion files. The only six modified pre-existing paths are the two mutable goal heads, the two registries, `tools/validate_ledger.py`, and `tools/test_run_supersession.py`. Both goal-head diffs are single queue-path changes. No hypothesis file changes.

Independent byte and SHA-256 checks found:

- 18 replacement pairs: all original bytes equal the base blobs, and every source/replacement digest matches the provenance record.
- 16 appended run-registry entries and two appended schema-registry entries: every newly added source and replacement hash matches its snapshot blob. All prior registry records retain their values. This does not attest historical correctness of pre-existing registry entries.
- Six bbb42f `raw-result.json` additions: exact byte copies of the corresponding tracked `results.json`, which all six original manifests designate as `artifacts.results_json`. The inspected producer driver calls `write_results_json` and records that artifact name. No result or certificate was recomputed here.
- MLKEM command: exact transcription of the preserved command field, with terminal newline. Its environment JSON contains the preserved environment mapping with an explicit transcription provenance wrapper. Its raw-result file exactly equals `terminal_receipt.json`.
- SSI command: exact transcription of the preserved command field, with terminal newline. Its stdout/stderr companions are exact copies of the archived `.txt` streams, including the empty stdout stream.
- Every companion digest declared in the six a98ea9/5cad48 replacement manifests matches its snapshot blob.

The first verification script performed 163 discrete preservation/hash/copy checks, with zero failures. A separate value comparison made 207 comparisons of original run fields against their replacements, including the documented a98ea9 field relocation and in-memory quoting of malformed dirty summaries; it found zero differences. The original status and result labels were preserved. The MLKEM environment mapping equality was also inspected directly. The scripts read Git blobs and did not modify repository artifacts.

## J2: narrow malformed dirty-summary identity fallback

The code change at `tools/validate_ledger.py:995` only recovers an identity from the known flat-manifest encoding defect. The input must start with a literal valid `run_id`, have one narrowly located dirty-summary field whose rows match the accepted porcelain grammar, terminate that field at `environment:`, and parse as a complete document after quoting only that field in memory. The composed node inspection rejects duplicate keys, nested identity fields, merge keys, and aliases. The ordinary identity loader also rejects duplicate mapping keys. This function does not repair source bytes or independently register an admissible run.

I executed the exact snapshot AST functions `_flat_run_id_with_malformed_dirty_summary`, `_run_id_of`, `check_run_supersessions`, `load_yaml`, and `check_run` in a small in-memory harness. File reads and existence checks were backed by a dictionary; no tests wrote files or invoked an experiment. This tests the frozen functions with isolated fixtures, rather than claiming a fresh full-suite or full-ledger execution.

The positive malformed fixture recovered `RUN-SUP-001`. Thirteen negative identity variants all returned `None`: duplicate same ID, duplicate conflicting ID, nested `run`, nested flow identity, absent/nonleading identity, leading comment, non-porcelain continuation, duplicate git mapping, merge key, alias, second document, wrong ID header, and list-valued identity. The committed added tests were also read, including their additional commented-ID, nested block, and substituted-continuation cases.

The required proves-too-much controls behaved as follows:

| Control | Independent observed result |
| --- | --- |
| Complete registered replacement of malformed source | No errors |
| Source bytes changed after pinning | `registered superseded run manifest hash changed` |
| Replacement missing timing, with its new hash registered | `run missing required field 'timing'` |
| Replacement declares a different run ID | `registered superseding run manifest declares run id 'RUN-SUP-002'` |
| Same malformed source without registration | Ordinary check rejects invalid YAML |

`check_run_supersessions` still checks both whole-file hashes before identity matching; `check_run` still validates the replacement's ordinary required fields. No fallback path bypasses these checks in the inspected call sequence. The parent-reported 46-test/full-ledger/run-immutability results were not used as substitute independent evidence, and their external log files were not read.

## J3: scientific boundaries and queue bindings

5cad48's raw result and preserved manifest agree with the replacement's existing observation flags. The replacement explicitly records `code.commit_meaning: archival_source_only`, `code.execution_commit: null`, and `reproducibility.execution_binding_verified: false`. After a scoped Coordinator authorization to inspect the exact archival source, SHA-256 of `experiments/EXP-ECDLP-5cad48/implementation/stage2.py` at `e6689b272047e22eb3e66d82c4a12847abe9637a` was `48007b638be0ff5dd8c764030ce5cbf5cf9a60497468d186ca9210689a91595a`, exactly the replacement pin. This establishes archived source custody; it supplies no evidence that those bytes were the executed revision. Original producer-valid labels remain attributed and unverified by this review.

MLKEM's recovered raw-result file is byte-identical to its supervisor terminal receipt, which records `worker_result_exists: false`. The replacement retains `terminal_cause: hard_cap`, exit 143, and `bkz_tour_completed: false`, adds no solve certificate, and explicitly states that the repair supplies no independent validation. Its historical validity statement is a preserved producer assertion, not a new successful BKZ observation. SSI's result labels likewise remain unchanged and subject to the explicit repair interpretation limitation.

The ECRANK evidence replacement adds `direction: neutral`, `strength: preliminary`, `claim_tier: toy`, and `proof_status: empirical_only`. It retains the original control/success assertions with explicit producer attribution, states that independent review remains pending, and records the certifier and density-test limitations. The checkpoint replacement only adds its required wrapper and supersession metadata. This review has not validated its `all_iv_pass` assertion, the construction's mathematical certification, or HEUR-1. No scientific claim is promoted or closed by this repair.

The AES replacement queue changes exactly one archive hash plus associated additive provenance. All nine `archive.path_sha256` values independently match their blobs at the declared source commit `cc660597e3bcc616521bce443b9a17eafa4393c2`. The eight producer artifacts also equal the snapshot and base versions. The receipt is the intentional exception: its archived hash is `d58e80deaffbc7ae89bfad3ac6159c58ad56aaa4a908f4ad3b7fa9aa3fe715d5`, while its later preserved snapshot/base bytes hash to `7ae1d254ae02678b07d0cb9ca2d7ccb13eeba6f82e853e5e2ee4453519405384`. The new queue correctly pins the declared archive version and preserves the later receipt. I did not reinterpret or endorse historical AES conclusions or the inherited archive-reachability policy statement.

FAEST's new goal pointer resolves to an existing snapshot queue with matching `goal_id: GOAL-FAEST-001`, `batch_id: BATCH-0ed590`, and `opened_by: DEC-20260810-67d674`. The decision and queue describe an acquisition/design gate, preserve source-pinning and independent-review prerequisites, and assert no FAEST security conclusion. The pointer repair does not change goal status or any queued task state. This is a pointer/boundary check, not a fresh dispatch-readiness or claim-validation attestation.

### Advisory A1: clarify the current FAEST next action

Severity: low; non-blocking for the assigned custody and no-promotion joints. At `ledger/goals/GOAL-FAEST-001.yaml:103` and `:112`, dated historical notes still say the queue does not exist and that the path points at BATCH-001. The current `next_action` at line 235 still begins by directing creation of the queue and handoffs, although the corrected pointer names an existing queue. The dates identify the notes as historical, but the live next-action prose can send a later session back to already-done queue authoring.

Recommended additive remedy: retain those historical notes verbatim, add a dated correction explaining that the pointer now resolves and supersedes their present-tense interpretation, and give one current next action for the existing queue after queue/claim-overlay reconciliation. Do not infer task completion from raw queued states or create a duplicate queue. The Coordinator acknowledged this advisory and planned a subsequent annotation; no later annotation or merged head is reviewed by this report.

## Limits and procedure record

- Scope remains snapshot `4f15ab57`, regardless of subsequent parent merges or disjoint recovery work. No later working-tree change or sibling report was read.
- The Coordinator explicitly expanded historical read scope only for the nine AES archived paths at `cc660597` and the 5cad48 runner at `e6689b2`. This did not lift sibling-report blindness.
- All research artifacts were read through pinned Git blobs. The initial role/AGENTS read used the supplied worktree before the parent announced later merging; the contracts were then read from the frozen snapshot. Read-only memory guidance was consulted as required by session instructions and used only as a reminder about both-side hash provenance, which was independently checked here.
- The helper checks ran zero scientific experiments and made zero repository writes. One reporting-only inspection initially requested the nonexistent queue key `status` and raised `KeyError`; it was corrected to inspect the actual `state`-based queue. This does not affect the completed preservation checks or any scientific observation.
- No fresh full-ledger validation, full committed unittest-suite run, model probe, or preflight is claimed by this reviewer. The report gives the actual independent blob and function checks performed.
- The inspected PFDR summaries explicitly distinguish current hash consistency from unresolved historical archive custody. No historical violation, recovered completed archive, or scientific result is inferred from them.
- Deliverable authority: operational report bound to already allocated TASK-20260907-cbdf6e. At Coordinator direction no standalone VAL identifier is minted; the allocation tool does not support a VAL record type. The report must be archived by the Coordinator before durable downstream use.

```yaml
validation_report:
  task_id: TASK-20260907-cbdf6e
  run_ids:
  - RUN-ECDLP-5cad48-S2
  - RUN-ECDLP-a98ea9-S0
  - RUN-ECDLP-a98ea9-S1
  - RUN-ECDLP-a98ea9-S2
  - RUN-ECDLP-a98ea9-S2b
  - RUN-ECDLP-a98ea9-S2c
  - RUN-ECDLP-bbb42f-1
  - RUN-ECDLP-bbb42f-2
  - RUN-ECDLP-bbb42f-3
  - RUN-ECDLP-bbb42f-4
  - RUN-ECDLP-bbb42f-5
  - RUN-ECDLP-bbb42f-6
  - RUN-ECRANK-76a70d-armA-n6
  - RUN-ECRANK-76a70d-armB-determinism
  - RUN-ECRANK-76a70d-armB-n8
  - RUN-ECRANK-76a70d-armC-n10
  - RUN-ECRANK-76a70d-known-false
  - RUN-ECRANK-76a70d-planted
  - RUN-ECRANK-76a70d-scan-null
  - RUN-ECRANK-76a70d-smoke
  - RUN-MLKEM-980909-a
  - RUN-SSI-697354-a
  artifact_checks:
  - 18 original/replacement pairs preserved and hash verified
  - 163 preservation/hash/copy checks passed
  - 207 original-field comparisons passed
  - 9 AES historical archive pins passed
  - 5cad48 archival source pin passed
  metric_recomputations: []
  control_checks:
  - 13 adversarial malformed-identity rejection variants
  - source tamper rejected
  - missing timing rejected
  - replacement ID mismatch rejected
  - unregistered malformed source rejected
  heuristic_validation_checks: []
  cost_model_checks: []
  proof_architecture_checks: []
  verdict: passed
  limitations:
  - Administrative custody/code/scientific-boundary joints only
  - A1 low-severity FAEST annotation advisory
  - No scientific reexecution or validation
  - Exact resolved model and actual effort telemetry unavailable
  - Review binds 4f15ab57, not subsequent merged head
  artifact_paths:
  - /private/tmp/coordinator-a-recovery/independent-review.md
```

```yaml
review_attestation:
  task_id: TASK-20260907-cbdf6e
  joints_owned:
  - J1
  - J2
  - J3
  joint_verdicts:
    J1: holds
    J2: holds
    J3: holds
  requested_policy: review-adversarial
  requested_reasoning_effort: xhigh
  resolved_model_id: null
  actual_reasoning_effort_verified: false
  model_verified: false
  independent_session: true
  sources_read:
  - AGENTS.md
  - agents/validator.md
  - coordination/goals/GOAL-AES-001/batches/BATCH-004/archives/TASK-20260801-808/snapshot-receipt.json
  - coordination/goals/GOAL-AES-001/batches/BATCH-004/dispatch_queue.integrity-v2.json
  - coordination/goals/GOAL-AES-001/batches/BATCH-004/dispatch_queue.json
  - coordination/goals/GOAL-AES-001/batches/BATCH-004/tasks/TASK-20260801-806/od4_branching.py
  - coordination/goals/GOAL-AES-001/batches/BATCH-004/tasks/TASK-20260801-806/od4_branching_bound_report.md
  - coordination/goals/GOAL-AES-001/batches/BATCH-004/tasks/TASK-20260801-806/od4_results.json
  - coordination/goals/GOAL-AES-001/batches/BATCH-004/tasks/TASK-20260801-806/prescreen_od4.json
  - coordination/goals/GOAL-AES-001/batches/BATCH-004/tasks/TASK-20260801-807/od3_and_hole_ii_report.md
  - coordination/goals/GOAL-AES-001/batches/BATCH-004/tasks/TASK-20260801-807/od3_quantifier.py
  - coordination/goals/GOAL-AES-001/batches/BATCH-004/tasks/TASK-20260801-807/od3_results.json
  - coordination/goals/GOAL-AES-001/batches/BATCH-004/tasks/TASK-20260801-807/prescreen_od3.json
  - coordination/goals/GOAL-FAEST-001/batches/BATCH-0ed590/dispatch_queue.json
  - coordination/integrity/CORR-20260907-e6f0f7/artifact-provenance.json
  - coordination/integrity/CORR-20260907-e6f0f7/health-summary.json
  - coordination/integrity/CORR-20260907-e6f0f7/pfdr-receipt-current-byte-check.json
  - coordination/integrity/CORR-20260907-e6f0f7/pfdr-registry-current-byte-check.json
  - coordination/integrity/CORR-20260907-e6f0f7/review-plan.json
  - coordination/integrity/CORR-20260907-e6f0f7/validation-classification.json
  - docs/dynamic-subagent-dispatch.md
  - docs/task-lifecycle.md
  - experiments/EXP-ECDLP-5cad48/implementation/stage2.py
  - experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S2/command.txt
  - experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S2/environment.json
  - experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S2/manifest.yaml
  - experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S2/manifest_v2.yaml
  - experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S2/raw-result.json
  - experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S2/stderr.log
  - experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S2/stdout.log
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S0/command.txt
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S0/environment.json
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S0/manifest.yaml
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S0/manifest_v2.yaml
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S0/raw-result.json
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S0/stderr.log
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S0/stdout.log
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S0/transport-lemma.md
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S1/command.txt
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S1/environment.json
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S1/manifest.yaml
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S1/manifest_v2.yaml
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S1/raw-result.json
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S1/static-provenance-check.json
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S1/stderr.log
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S1/stdout.log
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2/command.txt
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2/environment.json
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2/manifest.yaml
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2/manifest_v2.yaml
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2/raw-result.json
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2/stderr.log
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2/stdout.log
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2b/command.txt
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2b/environment.json
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2b/manifest.yaml
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2b/manifest_v2.yaml
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2b/raw-result.json
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2b/stderr.log
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2b/stdout.log
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2c/command.txt
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2c/environment.json
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2c/manifest.yaml
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2c/manifest_v2.yaml
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2c/raw-result.json
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2c/stderr.log
  - experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2c/stdout.log
  - experiments/EXP-ECDLP-bbb42f/driver/isogeny_transfer_census.py
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-1/manifest.yaml
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-1/raw-result.json
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-1/results.json
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-2/manifest.yaml
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-2/raw-result.json
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-2/results.json
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-3/manifest.yaml
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-3/raw-result.json
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-3/results.json
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-4/manifest.yaml
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-4/raw-result.json
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-4/results.json
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-5/manifest.yaml
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-5/raw-result.json
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-5/results.json
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-6/manifest.yaml
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-6/raw-result.json
  - experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-6/results.json
  - experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-armA-n6/manifest.yaml
  - experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-armA-n6/manifest_integrity_v2.yaml
  - experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-armB-determinism/manifest.yaml
  - experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-armB-determinism/manifest_integrity_v2.yaml
  - experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-armB-n8/manifest.yaml
  - experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-armB-n8/manifest_integrity_v2.yaml
  - experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-armC-n10/manifest.yaml
  - experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-armC-n10/manifest_integrity_v2.yaml
  - experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-known-false/manifest.yaml
  - experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-known-false/manifest_integrity_v2.yaml
  - experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-planted/manifest.yaml
  - experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-planted/manifest_integrity_v2.yaml
  - experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-scan-null/manifest.yaml
  - experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-scan-null/manifest_integrity_v2.yaml
  - experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-smoke/manifest.yaml
  - experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-smoke/manifest_integrity_v2.yaml
  - experiments/EXP-MLKEM-980909/runs/RUN-MLKEM-980909-a/command.txt
  - experiments/EXP-MLKEM-980909/runs/RUN-MLKEM-980909-a/environment.json
  - experiments/EXP-MLKEM-980909/runs/RUN-MLKEM-980909-a/integrity-recovery.json
  - experiments/EXP-MLKEM-980909/runs/RUN-MLKEM-980909-a/manifest.yaml
  - experiments/EXP-MLKEM-980909/runs/RUN-MLKEM-980909-a/manifest_integrity_v2.yaml
  - experiments/EXP-MLKEM-980909/runs/RUN-MLKEM-980909-a/raw-result.json
  - experiments/EXP-MLKEM-980909/runs/RUN-MLKEM-980909-a/terminal_receipt.json
  - experiments/EXP-SSI-697354/runs/RUN-SSI-697354-a/command.txt
  - experiments/EXP-SSI-697354/runs/RUN-SSI-697354-a/integrity-recovery.json
  - experiments/EXP-SSI-697354/runs/RUN-SSI-697354-a/manifest.yaml
  - experiments/EXP-SSI-697354/runs/RUN-SSI-697354-a/manifest_integrity_v2.yaml
  - experiments/EXP-SSI-697354/runs/RUN-SSI-697354-a/stderr.log
  - experiments/EXP-SSI-697354/runs/RUN-SSI-697354-a/stderr.txt
  - experiments/EXP-SSI-697354/runs/RUN-SSI-697354-a/stdout.log
  - experiments/EXP-SSI-697354/runs/RUN-SSI-697354-a/stdout.txt
  - ledger/corrections/CORR-20260907-e6f0f7.yaml
  - ledger/corrections/schema-supersessions/20260907/ledger__evidence__EV-ECRANK-76a70d-285d90.integrity-v2.yaml
  - ledger/corrections/schema-supersessions/20260907/ledger__goals__GOAL-ECRANK-002__checkpoints__BATCH-5da478.integrity-v2.yaml
  - ledger/decisions/DEC-20260810-67d674.yaml
  - ledger/evidence/EV-ECRANK-76a70d-285d90.yaml
  - ledger/goals/GOAL-AES-001.yaml
  - ledger/goals/GOAL-ECRANK-002/checkpoints/BATCH-5da478.yaml
  - ledger/goals/GOAL-FAEST-001.yaml
  - orchestration/roles.yaml
  - plugins/crypto-autoresearcher-harness/skills/crypto-autoresearcher-harness/SKILL.md
  - templates/research-records.md
  - tools/run_supersession_registry.yaml
  - tools/schema_supersession_registry.yaml
  - tools/test_run_supersession.py
  - tools/validate_ledger.py
  - /Users/adamburan/.codex/memories/MEMORY.md
  - /Users/adamburan/.codex/memories/rollout_summaries/2026-08-09T01-50-03-2opE-crypto_autoresearcher_status_projection_supersession_fix.md
  source_read_note: List includes content/structured reads and byte-only SHA256/equality
    reads; read-source listing does not claim scientific analysis of every loaded
    blob. AES/5cad48 historical exceptions are explicitly bound above.
  read_sibling_reports: false
  blind_from_respected: null
  verdict: holds
```
