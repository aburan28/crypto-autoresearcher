# Initial packet archive ownership and publication

Owner: Coordinator control plane (parent /root), TASK-20261026-50b7bd.
This bootstraps the already prepared prospective authority records. It is not
the implementation snapshot TASK-20261026-971954 and does not complete any
downstream task. No agent is dispatched by this card. Archive alone.

The exact initial archive paths are in initial-archive-paths.json. They include
opening DEC-20261026-bb4afd, all seven initial handoffs including this archival
card, native contract, queue/plans, review/blind statements, source bindings,
orientation/validation, inference overlay/resolutions/history, these archive
instructions and the path list. No old setup, owner code, problem record or
shared tool belongs to this commit. Future task artifacts are absent and must
not be asserted. The source tree prior to this archive is d260643baf6d450cb1c5e398e1d9b2b4cd720fc2;
origin/main6a69b2d02ecd53f1649bcf56e23e4ffe91d953ad is already its ancestor.

1. Freeze this exact path list and confirm all source paths exist. Rerun queue
   and focus metadata checks, YAML parsing, branch merge hygiene and diff check.
   Current full-ledger100 external errors remain reported; do not call the
   whole ledger clean. Confirm no owner source or scientific cell changed.
2. Create archives/TASK-20261026-50b7bd/initial-packet-receipt.json with schema
   crypto.autoresearch.archive_receipt.v1, kind snapshot, binding_mode
   content_at_commit, goal/batch/task IDs, parent SHA, exact declared_paths,
   record_ids listed by the path manifest, and SHA256 for every listed source
   path except the receipt itself. Include role coordinator, purpose planning
   publication, scientific_calls0 and actual native Coordinator provenance.
   commit_sha may be null with the established no-self-reference explanation.
   Do not invent an archive commit, dispatch receipt, ownership reservation or
   completed implementation/reviewer status.
3. Stage only the declared path list, including the new receipt. Inspect the
   staged names and commit once with message naming TASK-20261026-50b7bd,
   DEC-20261026-bb4afd and TASK-20261026-{589ad5,971954,391e68,e48b18,022037,9fec07}.
4. Verify the actual commit parent and exact changed-path set against the list,
   read each source blob from that Git tree and recompute its SHA256. Verify
   every receipt source hash. Record the actual commit SHA, receipt SHA256 and
   path/hash verification in initial-publication-verification.json beside the
   receipt, subsequently publish that verification. Do not put the receipt's
   own hash inside itself. A working-tree checksum alone does not verify Git.
5. Push research/smallroot-owner-continuation-20261026. Open/update a stacked PR
   based on research/joint-smallroot-reach-audit-20261024 naming all IDs.
   Record actual push/PR receipt. Auto-merge is unavailable while base is a
   feature branch; retarget to main and request auto-merge after audit PR2547
   lands. Required hosted Actions currently fail to start for account billing
   availability; no bypass or successful merge is implied.
6. Parent has already prepared the new disjoint lane locally, without claiming
   the producer. Its exact lane side file is included in the initial path list.
   Publish it with the packet. If reconstructing from a clean tree, the command is:

```sh
python3 tools/goal_lanes.py open-lane GOAL-PFDR-fd09e0 BATCH-ee839d --queue coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/dispatch_queue.json --decision DEC-20261026-bb4afd --objective 'Native joint-smallroot preparation; zero scientific calls' --branch research/smallroot-owner-continuation-20261026 --as coordinator-smallroot-native-ee839d
```

Publish the lane. Acquire an actual owner Conductor task for exactly
experiments/joint-smallroot-native/; a successful check alone is not the task.
Claim the goal task within max_concurrent2 before dispatch. Record gate
receipts additively before changing producer blocked to queued. Re-render
Ready Tasks with --claims refs. Neither initial publication nor lane creation
authorizes science; the implementation card remains zero scientific runs.
