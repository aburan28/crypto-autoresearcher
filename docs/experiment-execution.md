# Execution-first experiments

Unqualified **run**, **run the harness**, **keep running**, and **run experiments**
use the single [`run`](../plugins/crypto-autoresearcher-harness/skills/run/SKILL.md)
skill. It executes existing programs and reports their outputs without an
agent-led protocol/schema-validation phase. Existing command-based experiments
keep their documented launchers; adopting the trial-plan format is not a run
prerequisite.

This document describes the process adapter and preparation of new trial plans.
Read those preparation details only when preparing or maintaining that adapter,
not as a checklist before every run. The runner retains its built-in checks.
The separate Coordinator archive/review workflow is needed before a scientific
state transition, not before returning execution results to the user.

## Boundary and responsibilities

The Coordinator still prepares/approves contracts, renders the existing
dispatcher, publishes claims, archives outputs, arranges independent review and
selects subsequent work. An executor may implement or repair the exact selected
experiment; a proposal-only document is not its completion gate.

`tools/experiment_execution.py` is a deterministic **per-task** process
supervisor. It runs an explicitly enumerated trial plan under one already
admitted executor claim, without model calls between seeds/cells. It is not a
second Coordinator, an auto-approval service, or an all-portfolio background
daemon. Concurrent experiments still use separate task sessions, the existing
`max_concurrent`/write-scope gates, and real machine headroom.

## Selection and legacy migration

```sh
python3 tools/newest_experiments.py --limit 3 --json
python3 tools/newest_experiments.py --limit 0 --include-blocked --json
python3 tools/newest_experiments.py --goal GOAL-... --limit 0 --include-blocked --json
```

ECC-first/newest-first ordering and approval/supersession filters are retained.
A selected `needs_implementation_or_plan` row is preparation work, **not launch
authority**. `ready` means unattempted trials remain, subject to the dispatcher.

An experiment directory or execution report alone no longer establishes
completion. Existing activity without a supported plan is reported as
`needs_reconciliation`, excluded from blind execution, and visible with
`--include-blocked`. Malformed plans are `needs_plan_repair`. Do not edit old
specifications, manifests, reports, archive bindings or run directories to make
them pass. The Coordinator reconciles known trials and remaining protocol work
through additive contracts/successors. Do not infer a trial count from how many
directories happen to exist. This change does not bulk-migrate historical data.

## Frozen trial-plan contract

For a new compatible experiment, freeze `experiments/<EXP-ID>/trial-plan.json`.
A named successor may use a different new plan path with an explicitly bound
handoff; automatic discovery only uses the standard path. No plan is rewritten
in place after execution.

A plan uses this shape (placeholders below are not executable records):

```json
{
  "schema": "crypto.autoresearch.trial_plan.v1",
  "experiment_id": "EXP-ECDLP-<allocated-token>",
  "task_id": "TASK-<date>-<allocated-token>",
  "frozen": true,
  "approved_by": "DEC-<date>-<allocated-token>",
  "specification": "experiments/<EXP-ID>/specification.yaml",
  "specification_sha256": "<sha256 of exact specification bytes>",
  "queue": "coordination/<lane>/dispatch_queue.json",
  "source_sha256": {
    "experiments/<EXP-ID>/driver.py": "<sha256>",
    "experiments/<EXP-ID>/check.py": "<sha256>",
    "experiments/<EXP-ID>/requirements.lock": "<sha256>"
  },
  "trials": [{
    "id": "baseline-b16-seed01",
    "run_id": "RUN-ECDLP-<allocated-token>",
    "argv": ["python3", "experiments/<EXP-ID>/driver.py", "--seed", "1", "--out", "{run_dir}"],
    "check_argv": ["python3", "experiments/<EXP-ID>/check.py", "{run_dir}"],
    "artifacts": ["manifest.yaml", "raw-result.json"],
    "memory_mb": 2048,
    "watchdog_seconds": null,
    "depends_on": []
  }]
}
```

Enumerate **all** required controls, seeds, parameter cells and comparisons
from the frozen scientific protocol, including fixed stopping rules. The
Coordinator/reviewer must check correspondence: syntactic validation cannot
prove that a manually authored list covers a mathematical protocol. A trial
can be a complete paired comparison. Dependent trials name earlier trial IDs;
a failed or unresolved control prevents dependent execution. No adaptive
search or automatic early-stopping policy is introduced here.

Required artifacts must exist as regular files and are nonempty by default.
A trial may optionally declare `"allow_empty_artifacts": ["counterexamples.jsonl"]`
when its frozen protocol gives an empty file a defined meaning. This list must
contain unique canonical relative paths already named in `artifacts`; reserved
supervisor paths, wildcard exemptions, and missing files are not allowed.
Listed files may also be nonempty. The independent `check_argv` still runs and
must validate the scientific meaning of their contents, including emptiness.
Empty files receive ordinary SHA-256 bindings, so later modification or deletion
still requires reconciliation. Adding this field changes the frozen plan hash
and requires the normal additive approval and claim bindings.

Allocate/check the run IDs before freezing with `tools/allocate_id.py`; IDs
and artifact paths must already appear in the committed handoff. Bind the
complete driver/checker source and dependency closure, not just an entrypoint.
These are reviewed, trusted experiment programs, not arbitrary user code in a
filesystem sandbox. The runtime/host must still provide the repository's
required environment isolation and any aggregate/GPU resource guards.

Add this **exact** object to the executor's committed handoff:

```json
"execution": {
  "mode": "experiments",
  "kind": "run",
  "experiment_id": "<EXP-ID>",
  "trial_plan": "experiments/<EXP-ID>/trial-plan.json",
  "trial_plan_sha256": "<sha256 of exact plan bytes>",
  "approved_by": "<the plan approval DEC-ID>"
}
```

The plan does not hash the queue, avoiding a hash cycle. The queue binds the
plan; both must match committed HEAD bytes before execution. The existing
queue validator remains responsible for handoff/approval/prerequisite/archive
integrity. Approval authority is not created by putting strings in this object.

For **each** run include all of these exact paths in task `artifact_paths`,
inside its declared `write_scope`, and in the snapshot's coverage:

```text
experiments/<EXP-ID>/runs/<RUN-ID>/
  launch.json
  execution-receipt.json
  command.txt
  environment.json
  stdout.log
  stderr.log
  check.stdout.log
  check.stderr.log
  manifest.yaml
  raw-result.json
  <every other declared driver artifact>
```

The driver writes the canonical manifest and raw results. The checker must
validate real results, mathematical invariants, controls and manifest semantics;
merely checking that JSON exists is insufficient. The supervisor's operational
receipt never replaces the canonical manifest or independent scientific review.

## Launch and progress

First follow the existing lifecycle: preflight, freeze/approve/publish the
handoff, validate its queue with claims across refs, and publish the executor
claim through `tools/goal_lanes.py`. Then the claimed executor runs:

```sh
python3 tools/experiment_execution.py status --plan experiments/<EXP-ID>/trial-plan.json
python3 tools/experiment_execution.py run --plan experiments/<EXP-ID>/trial-plan.json \
  --owner <published-claim-owner> --epoch <published-claim-epoch>
```

`--repo` selects an explicit checkout. The supervisor checks committed sources
and their hashes, the current frozen specification, the exact handoff binding,
the live owner/epoch, publication visibility in origin tracking refs, zero-run
restrictions and exact archive coverage. It re-renders the existing dispatcher
with `--claims refs --now ...` before each trial. It accepts executor/run tasks
only: Coordinator, proposal, review and zero-run tasks are refused.

No inference is used for polling. Trials run serially within one task. A
same-host cross-worktree lock prevents a second local supervisor for that task;
the worker inherits the lock descriptor. Existing cross-host Git claims are a
feed, not a distributed lock server: fetch/publish discipline and collision
reconciliation still apply. This does **not** claim global exactly-once launch.
Remote revocations become visible when refs are fetched; local claim expiry is
checked while a process runs. Size the published claim for the protocol. Expiry
stops its process group and requires proper successor authorization, not a
self-renewed claim.

POSIX process groups and per-process address-space limits (`memory_mb`) are
required. That limit is **not aggregate RSS or GPU memory enforcement**; size
concurrency and use existing host/cgroup protections where required. An optional
per-command watchdog requires an explicit `watchdog_reason`; it is a machine
protection, not a campaign spending cap. SIGINT/SIGTERM and watchdog expiry kill
the owned process group and preserve a failure receipt where possible. SIGKILL
or host loss may leave only launch artifacts; those require reconciliation.
Programs must not detach children into other sessions.

Exit codes: `0` for successful status inspection or all trial outputs validated;
`2` for authorization/contract/infrastructure impediments; `3` for a plan with
remaining failed/uncertain/dependency-blocked trials; `130` for interruption.

## Completion is not closure

Coverage reports required, output-validated, remaining, unattempted and
reconciliation/dependency-blocked trials. Completion requires successful process
and checker outcomes plus the exact hash-bound artifact set for **every**
required trial. A directory, report, zero exit code alone, missing output or
modified artifact cannot satisfy it. Valid negative observations count exactly
like valid positive ones. No outcome is rerun until it looks favorable.

An existing run directory is never reused, even when empty. A retry needs a
new immutable run ID and explicit additive authorization after confirming the
prior worker is no longer active. Retain the stable scientific trial identity
and original seed/parameters; distinguish retries from new replications. Do not
silently replace failures or successes. The present adapter does not
self-authorize recovery or translate legacy results into receipts.

After measurement, the Coordinator snapshots and verifies the exact package,
publishes the branch/PR, and dispatches independent review under the existing
gates. `publication_verified` and `scientific_review_verified` deliberately
remain false in the supervisor's coverage view: it has not established either.
Unrelated already-authorized experiments may proceed; dependent scientific
promotions must wait. Evidence archival never closes a research direction.

## Tests

```sh
python3 -m unittest discover -s tests -p 'test_experiment_execution.py' -v
python3 -m pytest tests/test_newest_experiments.py
```

The new suite uses real subprocesses and temporary Git repositories, with a
simulated dispatcher transport. It tests the adapter contract, not a real
campaign's full archive/review lifecycle. Run repository CI and a separately
approved representative integration trial before broad deployment.
