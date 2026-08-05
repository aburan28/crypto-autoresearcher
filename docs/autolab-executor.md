# AutoLab executor

AutoLab is integrated as an **execution backend**, not as the research control
plane. Crypto-autoresearcher still owns hypothesis selection, task scoping,
evidence classification, independent validation, red-team review, and ledger
promotion.

## Boundary

The executor:

1. freezes the task as canonical `task.json`;
2. launches the configured AutoLab CLI in the repository root;
3. confines outputs to `runs/autolab/<task-id>/`;
4. captures stdout, stderr, retries, duration, exit status, and artifacts;
5. writes `execution-receipt.json` with the task digest and an explicit
   `requires-independent-validation` promotion state.

AutoLab output is therefore evidence awaiting review, never a theorem or ledger
conclusion by itself.

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
```

## Python usage

```python
from pathlib import Path
from orchestration.executors import AutoLabExecutor

executor = AutoLabExecutor(Path.cwd())
result = executor.execute({
    "task_id": "TASK-20260805-001",
    "role": "executor",
    "hypothesis": "The proposed relation-density gain survives a fixed-seed control.",
    "write_scope": ["experiments/EXP-XYZ/results/**"],
})

print(result.receipt_path)
```

## Expected promotion flow

```text
Coordinator freezes task
        ↓
AutoLab executor runs bounded work
        ↓
Artifacts + execution receipt
        ↓
Validator reproduces or rejects
        ↓
Red team searches for counterexamples
        ↓
Coordinator may promote scoped evidence to the ledger
```

A future queue adapter can call `AutoLabExecutor.execute()` for tasks whose
`executor` field is `autolab`; the class is intentionally independent of a
particular queue schema so existing frozen handoffs remain valid.
