# Observable progress and continuation

Use the existing dispatcher as the source of task eligibility. The bundled
scripts/checkpoint.py invokes it with Git receipt verification and claim refs,
then renders a read-only JSON observation to stdout:

```sh
python3 <PLUGIN_ROOT>/scripts/checkpoint.py --repo <REPO_ROOT> \
  --queue <repository-relative-queue.json> --mode goal
```

Save stdout outside the ledger if a local comparison is useful; supply that
file with --previous on the next invocation. The comparison is scoped to the
same checkout, queue and mode. A new batch starts a new baseline; explain the
cross-batch transition with the committed goal decision. No supplied observation
is authority, and no checkpoint file approves work or changes goal status.

The output distinguishes ready unclaimed tasks, running tasks and claim owners,
deferred reasons, expired leases, terminal outcomes, and verified completed
archive receipts. It distinguishes newly completed tasks from failures and from
mere state changes. An unchanged result is explicitly unchanged.

This view does not infer mathematical progress or invent a next action. Pair
it with the goal/lane's committed next_action, responsible role, required review,
branch/PR and concrete impediment/recheck. Never call a live owner, released
claim, heartbeat, changed timestamp, pending CI, or increased output volume
completed work. A failed dispatcher yields an operational error, never an empty
successful checkpoint.

At a checkpoint say:
- Changed: task IDs, verified commits and evidence/decision IDs, or "none".
- Working: owner, task and expected bounded deliverable, or "none".
- Next: one committed action, responsible role, and why it reduces uncertainty.
- Impeded: exact condition, affected task/claim, recheck and clears_when.
- Scope: mode, goal, lane, queue, branch/PR and claim boundary.

During execution, perform the next eligible authorized action after reporting.
If no action is justified, leave the goal active and report the recheck.
Do not poll unchanged work rapidly or create a new task to disguise a stall.
