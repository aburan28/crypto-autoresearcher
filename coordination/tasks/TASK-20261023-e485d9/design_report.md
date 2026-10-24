# Held-out balanced-slot IC design

Prospective design only: no successor timings, approval or result exists. EXP-ICPERF-6c546e reuses H-ICPERF-a2284c and the unchanged native fixed-window generator/base worker. It corrects the original perfect treatment/middle-slot confounding identified in TASK-20261023-18b489 and composed by DEC-20261023-d70a08; every original record is preserved.

The fixed new workload uses bits12/14/16, held-out curve seeds3/4/5, solver seeds0/1, public target seed0,3 repetitions,3 arms (162 workers), m2, small_x, mitm, no acceleration, harvest off, window4. Each arm crosses slots0/1/2 exactly once within each exact curve/solver-seed across repetitions. Solver seeds reverse the orientation, yielding all6 permutations for each curve. This is an explicit crossing, not a claim of randomized slot assignment.

Source closure includes both benchmark drivers and all native package Python files. Inputs bind config/ic-target-balanced-benchmark.json and config/ic-target-balanced-environment.json. Environment/package/host metadata must match the precommitted lock; every child pins CPU0, with actual affinity and before/after load recorded. Pre/post process census is diagnostic and cannot prove host-wide isolation. Known concurrent scientific producers disqualify causal wall-time attribution; unobserved load remains a limitation.

The complete-solve wall boundary includes per-solve factor-base and fixed-window setup, failed attempts, LA/recovery and final solver verification. Driver harness_seconds ends before independent checking; supervisor/checker bookkeeping overlaps and is not added. Group-operation counts, wall/CPU seconds, table payload bytes and lifetime worker RSS remain distinct quantities. No cache setup is amortized across solves, no successful-only filtering, and all failures are preserved.

The original geometric paired ratio, A/A noise factor and numerical gate remain fixed:54 paired ratios `((reference_a_seconds+reference_b_seconds)/2)/candidate_seconds`; geometric mean;5000 bootstrap replicates with seed3065 sampling3 curve groups within each bit stratum while retaining both solver seeds/all3 repetitions. A qualified positive gate needs all162 valid workers, ratio greater than max(1.05,A/Afactor), lower95% bootstrap endpoint greater than1, balanced slots and environment/affinity checks. Invalid/censored/incomplete data cannot qualify. Original curve seeds0/1/2 never enter the new ratio or interval.

Prediction provenance explicitly lists the original observed grid, independent review and composition decision. P-balanced-new-curves is out-of-sample only for unseen exact curve seeds3/4/5; bit sizes and algorithm are reused and the proposal is informed by the original observation. This is not claimed as an independent discovery or crypto-scale transfer. The existing independent algebra report TASK-20261023-5301b1 is cited for the unchanged native identity, without pretending to conduct another blinded algebra review.

One fresh xhigh independent reviewer owns J-integrity and J-inference exactly. The reviewer independently computes metrics from raw rows without reading producer validation summaries, reports or tools/ic_target_benchmark.py analysis source at any time. It audits the successor source and reuses the prior committed hash-matched unchanged-base-worker audit. It exercises the old confounded schedule, wrong certificates/digests, missing rows/environment/affinity and an identical-time false-speedup control in scratch copies; no performance rerun is authorized. Every actual source read and blind_from compliance is attested.

No runbook or mechanical executor is claimed. The original real failed compile report is retained at coordination/tasks/TASK-20261023-675119/compile_report.yaml; it is not passed off as a successor compile. New clean runbook compilation requires a separately assigned task. This draft uses the implementation-tier execution route and records the missing runbook binding honestly.

## Reserved identities and exact paths

- Execution lane BATCH-b2dce4; final queue: coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-b2dce4/dispatch_queue.json.
- Approval DEC-20261023-6bcd2d; executor TASK-20261023-b6cb1a; run RUN-ICPERF-d566af.
- Raw snapshot TASK-20261023-55a603; independent reviewer TASK-20261023-6562b0; ledger TASK-20261023-e0567d.
- Later composition DEC-20261023-122e32 and EV-ICPERF-92c130 are reserved names, with no prewritten outcome.
- Future claim path claims/ic-target-balanced-6c546e.json is a reserved machine-readable record only, never populated from this expectation.
- Canonical draft: experiments/EXP-ICPERF-6c546e/specification.yaml; unapproved trial-plan.json beside it.
- Draft queue, compiler, packet and prospective copies: coordination/tasks/TASK-20261023-e485d9/{execution-queue.json,prepare_packet.py,preapproval-packet.json,preview/}.

## Admission commands

The packet compiler has run without science and both queue structural validation and specification schema checks pass. The read-only probe currently reports exactly two blockers: canonical draft bytes are not published at origin/codex/index-calculus-optimization, and BATCH-b2dce4 has not been opened as the lawful final queue lane. Source/config/environment hashes already match pushed bytes.

Root publishes the exact four declared producer artifacts and separately declared control-plane helpers/previews, closes the prior execution lane, opens/publishes BATCH-b2dce4 and its queue. Then run:

```sh
.venv/bin/python tools/experiment_preapproval.py --packet coordination/tasks/TASK-20261023-e485d9/preapproval-packet.json
```

Require approvable:true, then copy prospective bytes without rewriting: preview/specification.yaml and preview/trial-plan.json to canonical paths, preview/queue.json to the final queue, preview/TASK-*.yaml to ledger/handoffs/<same-name>, preview/DEC-20261023-6bcd2d.yaml to ledger/decisions/<same-name>. Publish exact approved bytes and verify custody. Require:

```sh
.venv/bin/python tools/newest_experiments.py --experiment EXP-ICPERF-6c546e --json
```

Only execution_state:ready permits the next live-claim step. Materialize the new experiment in sparse checkout, publish/fetch the actual executor claim, then use the supervisor with the actual owner/epoch:

```sh
.venv/bin/python tools/experiment_execution.py run --plan experiments/EXP-ICPERF-6c546e/trial-plan.json --owner <actual-owner> --epoch <actual-epoch>
```

The six flat trial artifacts are manifest.yaml, raw-result.json, instances.json, arms.jsonl, validation.json and balance-validation.json, plus all8 supervisor-generated artifacts. Checker outputs are created before final artifact existence checks. Raw artifacts are published before a fresh timestamped run report with editable graph/SVG and inspected PDF. Additional report files need their own exact archive declaration; do not silently widen raw snapshot scope. Independent review follows a verified raw snapshot and committed handoff/live claim.

No official measured bound, frontier, default, production-target or asymptotic claim is in scope. Existing canonical ECDLP frontier graphs remain unchanged; this prospective design supplies no verified new datum. Execution-proof support remains unavailable; hashes and solution certificates are not called zkVM execution verification.
