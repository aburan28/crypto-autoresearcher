# Executor observation: first native control failed

Experiment EXP-ISOU-e7eeb5, frozen approval DEC-20261015-d51f81. Source commit is retained in source-commit.txt. The native control ran from 2026-10-16T06:46:57Z to 06:46:58Z and returned 101. RUN-ISOU-ea3515 retains all native stdout, stderr, generated maps, rejection records and receipts. The P-192/50341 candidate RUN-ISOU-f9546d was not started because its control dependency failed.

The positive P-192/13 and P-521/7 construction and fresh independent replay entries both have status ACCEPTED. The test then reached its leaderboard assertion at tests/challenge_cli.rs:266 after its nine rejection-control assertions. The leaderboard retained zero winners because submission paths repeated the relative evidence-directory prefix when resolved against submissions.json. The actual native leaderboard rejection reasons preserve these doubled paths. This is a control-invocation failure; it is not a failed high-degree construction or a mathematical obstruction.

The invocation passed a relative run directory to the unchanged frozen shell adapter. A fresh control run with an absolute run directory is the next discriminating action, subject to an additive Coordinator amendment. Do not overwrite this failed run, silently retry it under the same ID, or start the dependent candidate from this result.

This observation makes no scientific promotion or worldwide degree claim. Native per-command elapsed time, hashes and RSS receipts are retained; they describe this shared host and do not establish a performance improvement. Native Codex exact model and reasoning-effort identifiers remain unavailable and unverified, as recorded in the frozen package.
