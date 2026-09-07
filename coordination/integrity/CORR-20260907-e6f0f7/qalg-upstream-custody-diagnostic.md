# GOAL-QALG-001 upstream custody diagnostic

Read-only investigation, 2026-09-07. No repository bytes changed. This finding is outside the originally diagnosed nine-queue repair scope and remains unresolved pending a new Coordinator-approved recovery contract. It asserts nothing about the mathematical merits of either hypothesis or its later review.

## Bound source

Queue: `coordination/goals/GOAL-QALG-001/batches/BATCH-dbf57a/dispatch_queue.json`.

Archive task: `TASK-20260814-8a0fea`, kind snapshot, binding_mode content_first.

Declared marker commit: `531fd399823d1375ca06873fb0089df806b4a394`.
First parent: `40bd26c39bd7e5c81736a585cff2d2cd3521fd5a`.
Receipt source: `coordination/goals/GOAL-QALG-001/batches/BATCH-dbf57a/archives/TASK-20260814-8a0fea/snapshot_commit_receipt.json`.
Receipt introducing commit: `cba5f732e178de848bea8e022f6f22930d4ecc30`, whose parent is the marker above.

The marker commit is empty, and its actual message contains every archive record ID. Its parent introduces exactly the 12 declared source artifacts. The receipt does not exist at the marker; the immediate successor introduces only the receipt. Current receipt hash equals the declared `5874780631ac0fc28e1370ab36a9159a3ee6bd66aa93e1c7cfbcc2cabe73f562`.

## Hash observations

Every one of the 12 declared source SHA256 values agrees with its file at the marker commit. Ten of those sources also agree with current bytes. Both hypotheses have since changed:

| Path | Original / marker SHA256 | Current SHA256 |
|---|---|---|
| ledger/hypotheses/H-CSIDH-3eaede.yaml | 6da4ef3b38a88ed479662f50bf1099a34686e766228eb6797fc1c85b782fd82d | 85020cd80eed382ebff71188ea08ec1f3fd2524b17f6a5622c4ccf70c34d4438 |
| ledger/hypotheses/H-MLKEM-36f511.yaml | b4bd827df687a2ee2aafb6993c72306dd2f4b109d728ecad98a79d198e2d2471 | cde8c141f82fbc506435cbd14e6fd11d085c9a7eeb9e43ba8287d9c69a27d1b0 |

H-CSIDH changed `proposed` to `weakened` in `444755915e3ab16f4ff03c19bfa2d33eb02cbcb8`, citing `ledger/decisions/DEC-20260906-29caf8.yaml` and `ledger/evidence/EV-QALG-1b3395.yaml`.
H-MLKEM changed `proposed` to `supported` in `bf543e07fc6466171e77c4c6cd2b65a11f4d0bc0`, citing `ledger/decisions/DEC-20260906-cc4fb6.yaml` and `ledger/evidence/EV-QALG-8d85be.yaml`.
The observed diffs change status and its explanatory note. These are committed source observations, not independent endorsement of the decisions.

Other declared source paths, all matching the marker and current bytes:

- experiments/EXP-MLKEM-12d9b8/specification.yaml
- experiments/EXP-MLKEM-12d9b8/amendments/.gitkeep
- experiments/EXP-MLKEM-12d9b8/runs/.gitkeep
- ledger/handoffs/TASK-20260814-807901.yaml
- coordination/goals/GOAL-QALG-001/batches/BATCH-dbf57a/tasks/TASK-20260814-1b47ba/design-report.yaml
- experiments/EXP-CSIDH-c65945/specification.yaml
- experiments/EXP-CSIDH-c65945/amendments/.gitkeep
- experiments/EXP-CSIDH-c65945/runs/.gitkeep
- ledger/handoffs/TASK-20260814-a82a19.yaml
- coordination/goals/GOAL-QALG-001/batches/BATCH-dbf57a/tasks/TASK-20260814-bdf473/design-report.yaml

A text search found no H-CSIDH-3eaede entry in tools/schema_supersession_registry.yaml or tools/run_supersession_registry.yaml.

## Commands actually run

Working directory: `/Volumes/SSD990/crypto-autoresearcher/.worktrees/coordinator-a-recovery`.

- Python json.load read the queue and printed the complete TASK-20260814-8a0fea entry.
- `rg -n 'H-CSIDH-3eaede' tools/schema_supersession_registry.yaml tools/run_supersession_registry.yaml`
- `git log -4 --format='%H %s' -- ledger/hypotheses/H-CSIDH-3eaede.yaml`
- Python subprocess executed `git show -s --format=%H%n%P%n%B 531fd399823d1375ca06873fb0089df806b4a394` and `git diff-tree --no-commit-id --name-only -r 531fd399823d1375ca06873fb0089df806b4a394`.
- Python iterated all 13 entries in archive.path_sha256, executed `git show 531fd399823d1375ca06873fb0089df806b4a394:<path>` for each, hashed successful stdout with hashlib.sha256, and separately hashed current pathlib.Path(path).read_bytes(). It printed expected-vs-historical and expected-vs-current equality for each; the receipt returned ABSENT at marker, all12 source historical checks passed, and only the two hypothesis current checks failed.
- `git show --format=fuller 444755915e3ab16f4ff03c19bfa2d33eb02cbcb8 -- ledger/hypotheses/H-CSIDH-3eaede.yaml`
- `git log -3 --format='%H %s' -- ledger/hypotheses/H-MLKEM-36f511.yaml`
- `git show -s --format='%H%n%P%n%B' cba5f732e`
- `git diff-tree --no-commit-id --name-only -r 40bd26c39bd7e5c81736a585cff2d2cd3521fd5a`
- `git diff-tree --no-commit-id --name-only -r cba5f732e`
- Python printed the current H-MLKEM SHA256 and executed `git diff 531fd399823d1375ca06873fb0089df806b4a394 HEAD -- ledger/hypotheses/H-MLKEM-36f511.yaml`.

No archive mutation or alternative queue render was attempted in this investigation.

## Recommendation and unresolved scope

This is not an AES-style erroneous queue pin: the source hashes accurately describe historical design-time bytes. Never retarget them to later hypothesis statuses or roll statuses back.

Changing the binding to commit mode is insufficient under the unchanged exact-path verifier: the marker changes zero paths, the parent changes12 source paths without the receipt, and the immediate successor changes only the receipt. A new marker alone likewise supplies no preservation package.

A new contract should recover a byte-preserved package containing all12 source files at the marker, the receipt from its actual successor, both current hypothesis variants, and exact path/revision/hash and status-transition mappings. Independently validate custody and archive it with new IDs and a present-day correction decision. Preserve the old queue and statuses. Until that work is approved, performed and reviewed, report the selected queue as an unresolved upstream custody impediment; do not claim historical repair or scientific validation.
