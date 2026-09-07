# Implementation notes: EXP-MLKEM-980909

Contract: `experiments/EXP-MLKEM-980909/specification.yaml`
(`approved_by: DEC-20260831-dfa5a6`, frozen).
Handoff: `ledger/handoffs/TASK-20260831-66f15c.yaml`.

## Pre-execution verification (before any run)

- Re-verified independently (not taking the coordinator's briefing on faith):
  - `coordination/goals/GOAL-MLKEM-005/batches/BATCH-266fa2/tasks/TASK-20260831-66f15c/`
    contains only `task_card.yaml`, `rt_ctrl_1_target.py`,
    `rt_ctrl_1_supervisor.py`, `verify_telemetry_receipt.py`,
    `inputs/fplll_strategies_default.json` — no `execution-report.yaml`, no
    `output/`. Genuinely unexecuted.
  - `coordination/goals/GOAL-MLKEM-005/batches/BATCH-266fa2/claims/TASK-20260831-66f15c.1.claim.json`
    has `expires_at: 2026-09-01T00:03:56Z` (expired, in the past relative to
    today, 2026-09-06) and no release record.
  - `coordination/goals/GOAL-MLKEM-005/batches/BATCH-266fa2/dispatch_queue.json`
    shows `"state": "queued"` for this task.
  - `grep -rl EXP-MLKEM-980909 ledger/decisions/` returns only
    `DEC-20260831-dfa5a6.yaml` (`decision: approve_controlled_successor`); no
    withdrawal.
  - All four frozen SHA-256 hashes in `task_card.yaml` (`strategies_sha256`,
    `runner_sha256` [supervisor], `worker_sha256`, `verifier_sha256`) were
    recomputed with `sha256sum` against the actual files and matched exactly,
    and the strategies hash also matched `specification.yaml`'s
    `inputs.strategy_sha256`.
  - Conclusion: this Coordinator's briefing was correct; proceeded to execute.

## Environment setup (deviation from an implicit assumption, not from the frozen contract)

The frozen contract and handoff pin `Python 3.13, fpylll 0.6.4, numpy 2.4.0,
psutil 7.2.2`, but say nothing about which host provides them, and the task
card's recorded prior command used a macOS `/Library/Frameworks/...` Python
path from a different machine — not reproducible here. This machine's
repository-default `python3` (3.11.15) had no `fpylll`. Built a fresh,
isolated venv from the system's `python3.13` package (installed
`libgmp-dev`, `libmpfr-dev`, `libfplll-dev 5.4.5-1.1build1`,
`python3.13-dev`, `python3.13-venv`, `build-essential` via `apt-get`, which
also upgraded the already-present `python3.13` package from 3.13.12 to
3.13.15), then `pip install numpy==2.4.0 psutil==7.2.2` followed by
`pip install fpylll==0.6.4` (built from source; ~3 minutes). All three
package versions matched the pin exactly; verified by import and
`__version__` before launching the self-test. `numpy==2.4.0` is a yanked
PyPI release (backward-compatibility bug per PyPI) but installed and
functioned correctly — recorded, not silently substituted.

## Execution

1. Controlled SIGTERM self-test (`--self-test-sigterm-after 8`, no BKZ) run
   first; independently verified PASS before the target was launched, per
   the frozen `controls` list.
2. The single authorized target run launched exactly once
   (`maximum_runs: 1`), in the background under this session's own
   supervision (not via a scheduler), monitored to completion via a
   condition-wait rather than fixed polling. Reached its terminal state at
   the 21600-second hard cap (`terminal_cause: hard_cap`); independently
   verified PASS.
3. No second run was launched. No worker or strategy bytes were changed
   after the self-test. No ledger record was edited. No interpretation of
   the outcome as support/refutation of any hypothesis was made.

## Deviations, failures, and unexpected observations (recorded, not discarded)

- See `runs/RUN-MLKEM-980909-001/execution_report.md` "Deviations" section
  for the full, itemized list (interpreter/dependency provenance, the yanked
  numpy release, the unmeasured `tours` field, and the 0.16-second CPU-hour
  budget overrun).
- The BKZ-55 tour at d=512 did not complete inside the 21600s cap on this
  host (4 logical CPUs, ~15 GB RAM). This is classified as an
  infrastructure/resource-budget outcome per `agents/executor.md`'s failure
  taxonomy (`resource_exhaustion`-shaped: the cap was reached before the
  measured quantity — a completed tour — was produced), NOT a
  `negative_observation`, exactly as the frozen `falsification_criterion`
  requires. Peak memory (~162 MB) was far below both the 16 GB budget ceiling
  and the host's actual ~15 GB, so this is not an INFEASIBLE-on-this-host
  memory finding — the binding constraint here was wall-clock time, not
  memory.

## Write scope

All writes for this task stayed inside `experiments/EXP-MLKEM-980909/` as
instructed. No file under `coordination/goals/GOAL-MLKEM-005/batches/BATCH-266fa2/tasks/TASK-20260831-66f15c/`
was modified (only read: the pinned scripts and strategies file were
executed in place, unmodified). No commit was made; artifacts are staged for
the Coordinator's snapshot task.
