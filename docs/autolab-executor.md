# AutoLab executor

AutoLab is integrated as an **execution backend**, not as the research control
plane. Crypto-autoresearcher still owns hypothesis selection, task scoping,
evidence classification, independent validation, red-team review, and ledger
promotion.

This is the *live execution* path. It is distinct from
`tools/port_autolab_experiments.py`, which imports historical AutoLab packages
already produced elsewhere into harness layout from `$AUTOLAB_ROOT` and is
verified in CI. The two share a name and nothing else: different inputs,
different configuration, different outputs.

## Boundary

The executor:

1. freezes the task as canonical `task.json` and digests it;
2. validates `task_id` as a single safe path segment, then creates a
   write-once run directory at `runs/autolab/<task-id>/`;
3. launches the configured AutoLab CLI with `cwd` at the repository root,
   in its own process group;
4. captures stdout, stderr, attempts, duration, exit status, git revision,
   interpreter environment, and discovered artifacts;
5. writes `execution-receipt.json` with the task digest and an explicit
   `requires-independent-validation` promotion state.

AutoLab output is therefore evidence awaiting review, never a theorem or ledger
conclusion by itself.

### What the executor does not do

Stated plainly, because the receipt is destined for a ledger that scopes every
claim to what was actually tested:

- **It does not sandbox AutoLab.** The child process runs at the repository
  root and inherits the parent environment; `--output-dir` is a request, not a
  confinement. A `write_scope` in the task bundle is passed through for the
  executed tool to honour — nothing in this module enforces it. Run untrusted
  AutoLab builds under an external sandbox (container, user namespace, seccomp)
  if the write scope has to be guaranteed.
- **It does not produce a run record.** `execution-receipt.json` is a
  pre-ledger staging artifact. The immutable run-record schema lives in
  `harness/runner.py` (`experiments/<EXP>/runs/<RUN-ID>/manifest.yaml` and
  siblings) and is what `tools/check_run_immutability.py` and
  `tools/validate_ledger.py` enforce, and what an evidence record cites per
  AGENTS.md rule 6. `runs/` at the repository root is gitignored precisely so
  receipts cannot drift into the ledger by accident.
- **It does not re-verify claims.** A solve or relation asserted in AutoLab
  output carries no weight until a certificate is independently re-verified
  per `docs/claims-and-verification.md`. Artifacts are captured, never
  interpreted.

### Receipt status values

`status` distinguishes results from infrastructure, because AGENTS.md rule 3
makes timeouts and crashes non-evidence:

| status      | meaning                                              |
| ----------- | ---------------------------------------------------- |
| `succeeded` | AutoLab exited 0                                     |
| `failed`    | AutoLab exited non-zero — a result, in scope          |
| `timed_out` | killed at `timeout_seconds`; never negative evidence  |
| `not_run`   | the executable was missing; never negative evidence   |

`ledger_run_id` stays `null` until the receipt has been converted into a
`RUN-*` record under `experiments/`. A `null` there means the execution is not
yet citable by an evidence record.

## Configuration

The default invocation is:

```bash
autolab run --task <run-dir>/task.json --output-dir <run-dir>
```

The command and flags are configurable for different AutoLab releases:

```bash
export AUTOLAB_COMMAND="python -m autolab run"
export AUTOLAB_TASK_FLAG="--task"
export AUTOLAB_OUTPUT_FLAG="--output-dir"
export AUTOLAB_EXTRA_ARGS="--workers 4"
export AUTOLAB_TIMEOUT_SECONDS=7200
export AUTOLAB_MAX_RETRIES=2
export AUTOLAB_ENV="AUTOLAB_SEED=7 AUTOLAB_MODE=bounded"
```

`AUTOLAB_ENV` is a shell-quoted `KEY=value` list injected into the child
environment. `AUTOLAB_MAX_RETRIES` must be `>= 0` and `AUTOLAB_TIMEOUT_SECONDS`
`> 0`; malformed values are rejected at construction rather than producing a
receipt for an execution that never happened.

The full command line — including `AUTOLAB_EXTRA_ARGS` — is recorded verbatim
in the receipt, which is meant to be archived. **Do not pass secrets there**;
use `AUTOLAB_ENV` or the caller's `environment=` argument instead.

## Python usage

```python
from pathlib import Path
from orchestration.executors import AutoLabExecutor, AutoLabExecutionError

executor = AutoLabExecutor(Path.cwd())
try:
    result = executor.execute({
        "task_id": "TASK-20260805-a1f151",
        "experiment_id": "EXP-XYZ-9c2b04",
        "role": "executor",
        "hypothesis": "The proposed relation-density gain survives a fixed-seed control.",
        "write_scope": ["experiments/EXP-XYZ/results/**"],
    })
except AutoLabExecutionError as exc:
    # `exc.result` carries the receipt path, artifacts, and duration whenever
    # the failure happened after execution started; it is None for a rejected
    # task or configuration.
    if exc.result is not None:
        print(exc.result.status, exc.result.receipt_path)
    raise

print(result.receipt_path)
```

Each `task_id` owns its run directory exactly once. A rerun needs a fresh id —
the executor refuses to reopen an existing directory rather than append to a
record that has already been read.

## Expected promotion flow

```text
Coordinator freezes task
        ↓
AutoLab executor runs bounded work
        ↓
Artifacts + execution receipt (runs/autolab/<task-id>/, gitignored)
        ↓
Conversion into an immutable RUN-* record under experiments/<EXP>/runs/
        ↓
Validator reproduces or rejects
        ↓
Red team searches for counterexamples
        ↓
Coordinator may promote scoped evidence to the ledger
```

The conversion step is deliberate and not yet automated: nothing under
`runs/autolab/` is visible to the ledger validators, so a receipt that is never
converted is simply not evidence.

A future queue adapter can call `AutoLabExecutor.execute()` for tasks whose
`executor` field is `autolab`; the class is intentionally independent of a
particular queue schema so existing frozen handoffs remain valid.
