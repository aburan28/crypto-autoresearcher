# Exact prospective admission and execution sequence

This is an implementation aid, not an approval or an admission receipt. All IDs are allocator-minted candidate IDs in `ids.json`, with read-only allocator checks in `id-checks.json`. The driver integrity tests are synthetic unit tests; no module measurement was launched by this task.

## Freeze and publish preparation

After all source changes stop, generate a new output directory (never reuse an earlier snapshot):

```sh
python3 /workspace/classical-ecdlp-lab/protocol/admission/prepare_packet.py \
  --repo-root /workspace/autoresearcher-execution \
  --lab-root /workspace/classical-ecdlp-lab \
  --out /workspace/classical-ecdlp-lab/protocol/admission/generated-final
```

The generated directory has `source/`, `draft/`, `preview/`, `preapproval-packet.json` and `canonical-bindings.json`. Copy the **contents** of `source/` and `draft/` into the repository, materialize the exact new source/experiment/ledger/coordination paths in the sparse checkout, commit only those paths, and push the actual branch. The driver source and config include all C++ source and input hashes; changes after generation require a new generated snapshot.

`draft/` deliberately contains an unapproved `review_required` specification, the new descriptive goal/question/hypothesis and its open lane. It does not record a past or future approval. The source ref in the packet is `origin/plan/direct-ecdlp-cancellation-20261025` and must actually contain these bytes.

## Genuine preapproval

From `/workspace/autoresearcher-execution`, invoke the unmodified repository tool:

```sh
python3 tools/experiment_preapproval.py \
  --packet /workspace/classical-ecdlp-lab/protocol/admission/generated-final/preapproval-packet.json \
  --repo-root /workspace/autoresearcher-execution
```

Preserve its stdout/stderr and exit code. Only `approvable: true` for these exact source/input/prospective bytes allows the Coordinator to approve. A refusal is repaired additively; no claim or direct module run substitutes for it.

## Coordinator archive and selector

After a genuine pass, the Coordinator archives `preview/specification.yaml`, `trial-plan.json`, `queue.json` and `handoff.yaml` at their corresponding paths in `canonical-bindings.json`. The archive handoff and approval decision are also prospective copies in `preview/`. The Coordinator records the actual preapproval receipt path/hash in its decision and relies on the current explicit user instruction plus standing experiment authorization, not on a self-grant from this adapter. Commit/push the exact approved package and check:

```sh
python3 tools/newest_experiments.py --experiment EXP-ECDLP-fe3337 --json
```

Require `execution_state: ready`. The earlier preapproval pass alone is not dispatch authority.

## Published claim and supervised batch

Use `tools/goal_lanes.py` to claim executor task `TASK-20261025-640fa7` on
`coordination/goals/GOAL-ECDLP-087fc3/batches/BATCH-2d999a/dispatch_queue.json`
with owner `executor-classical-pilot`, an actual session/branch and a lease longer than the protected trial. A 120-minute lease covers the one-hour supervisor watchdog and publication. `--publish --no-push` may be used to commit the genuine tool-generated claim, then the root can push with the configured GitHub credential helper. Never author a replacement claim manually or launch before the claim is visible in an origin tracking ref.

```sh
python3 tools/experiment_execution.py run \
  --plan experiments/EXP-ECDLP-fe3337/trial-plan.json \
  --owner executor-classical-pilot --epoch 1
```

Use the actual epoch returned by the claim, rather than assuming 1 if a prior claim exists. The driver refuses direct invocation without the real supervisor launch record, its current parent PID, exact argv and source-bound config. It builds/self-tests the five modules sequentially, then runs them with three concurrent module workers. The queue has one executor task and one batch trial; parallelism is inside that declared batch, not conflicting concurrent supervisors.

## Output custody and completion

There are 102 declared trial artifacts plus eight supervisor artifacts. All 64 JSONL part slots exist; unused slots are explicitly allowed to be empty. Each used slot is below 60 KiB and preserves complete verbatim lines. `parts-manifest.json` records the original full-stream byte count/hash and exact reconstruction. Oversized rows, capacity overflow, failed module output or failed control are retained as failures; rescue gzip files preserve complete original streams. Nothing is silently truncated. A rescue exceeding repository storage limits needs the canonical store and a genuine manifest/readback; inability to publish it is reported, not hidden.

The genuine supervisor performs its own output checker and run-schema completion. `output_validated` denotes output integrity, not a scientific finding. Check the resulting status and all module records before saying the batch completed.

Publish run records first. Then release the executor's actual claim with the exact epoch and `--outcome completed` only when every declared artifact exists; the release tool derives hashes itself. On an incomplete/invalid run, use the appropriate non-completed outcome and preserve its artifacts.

The post-run Coordinator archive task is `TASK-20261025-4c4ea5`. Its explicit `content_at_commit` binding is intentional: run records are published before the archive receipt, so the archive must verify their content at its own actual commit rather than pretending they all changed in that commit. Run this archive in isolation after its real claim. Its write-once receipt should list the 110 source artifact paths and hashes; commit it, bind the queue archive to that actual commit/parent and the hashes of the source artifacts plus receipt, and verify with the repository dispatcher. No scientific status transition is part of this observational archive.

Finally publish the descriptive source-linked report, graph and inspected PDF, retain null and failed outcomes, and produce the repository session receipt. The earlier eight-fixture pilot does not stand in for a blinded 192-target solver study or an asymptotic claim.
