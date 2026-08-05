from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from orchestration.executors.autolab import (
    AutoLabConfig,
    AutoLabExecutionError,
    AutoLabExecutor,
)


def _config(script: str, *, retries: int = 0) -> AutoLabConfig:
    return AutoLabConfig(
        command=(sys.executable, "-c", script),
        task_flag="--task",
        output_flag="--output-dir",
        max_retries=retries,
        timeout_seconds=10,
    )


def test_execute_writes_frozen_task_and_receipt(tmp_path: Path) -> None:
    script = (
        "import pathlib,sys; "
        "out=pathlib.Path(sys.argv[sys.argv.index('--output-dir')+1]); "
        "(out/'result.json').write_text('{\"score\": 7}')"
    )
    executor = AutoLabExecutor(tmp_path, _config(script))

    result = executor.execute(
        {"task_id": "TASK-001", "hypothesis": "bounded"},
        run_root=tmp_path / "runs",
    )

    assert result.succeeded
    assert [path.name for path in result.artifacts] == ["result.json"]
    frozen = json.loads((result.run_dir / "task.json").read_text())
    receipt = json.loads(result.receipt_path.read_text())
    assert frozen["task_id"] == "TASK-001"
    assert receipt["executor"] == "autolab"
    assert receipt["promotion"] == "requires-independent-validation"
    assert receipt["task_digest"] == result.task_digest


def test_execute_rejects_missing_task_id(tmp_path: Path) -> None:
    executor = AutoLabExecutor(tmp_path, _config("pass"))
    with pytest.raises(AutoLabExecutionError, match="task_id"):
        executor.execute({"hypothesis": "missing"}, run_root=tmp_path / "runs")


def test_execute_raises_after_nonzero_exit_but_keeps_receipt(tmp_path: Path) -> None:
    executor = AutoLabExecutor(tmp_path, _config("raise SystemExit(3)"))
    with pytest.raises(AutoLabExecutionError, match="status 3"):
        executor.execute({"task_id": "TASK-FAIL"}, run_root=tmp_path / "runs")

    receipt = json.loads(
        (tmp_path / "runs" / "TASK-FAIL" / "execution-receipt.json").read_text()
    )
    assert receipt["status"] == "failed"
    assert receipt["returncode"] == 3


@pytest.mark.parametrize(
    "task_id",
    ["../escaped", "../../escaped", "nested/id", "/absolute", ".", ".."],
)
def test_execute_rejects_task_ids_that_escape_the_run_root(
    tmp_path: Path, task_id: str
) -> None:
    executor = AutoLabExecutor(tmp_path, _config("pass"))
    run_root = tmp_path / "runs"

    with pytest.raises(AutoLabExecutionError, match="safe run-directory name"):
        executor.execute({"task_id": task_id}, run_root=run_root)

    assert not (tmp_path / "escaped").exists()
    assert not run_root.exists() or list(run_root.iterdir()) == []


def test_execute_writes_receipt_when_the_executable_is_missing(tmp_path: Path) -> None:
    config = AutoLabConfig(command=("crypto-autoresearcher-no-such-binary",),
                           max_retries=0, timeout_seconds=10)
    executor = AutoLabExecutor(tmp_path, config)

    with pytest.raises(AutoLabExecutionError, match="executable not found") as excinfo:
        executor.execute({"task_id": "TASK-MISSING"}, run_root=tmp_path / "runs")

    receipt = json.loads(
        (tmp_path / "runs" / "TASK-MISSING" / "execution-receipt.json").read_text()
    )
    # A missing binary is infrastructure, never a failed experiment.
    assert receipt["status"] == "not_run"
    assert receipt["ledger_run_id"] is None
    assert excinfo.value.result is not None
    assert excinfo.value.result.receipt_path.exists()


def test_timeout_is_recorded_as_timed_out_not_failed(tmp_path: Path) -> None:
    config = AutoLabConfig(
        command=(sys.executable, "-c", "import time; time.sleep(30)"),
        max_retries=0,
        timeout_seconds=1,
    )
    executor = AutoLabExecutor(tmp_path, config)

    with pytest.raises(AutoLabExecutionError, match="timed out") as excinfo:
        executor.execute({"task_id": "TASK-SLOW"}, run_root=tmp_path / "runs")

    receipt = json.loads(excinfo.value.result.receipt_path.read_text())
    assert receipt["status"] == "timed_out"
    assert receipt["timed_out"] is True
    assert receipt["timeout_seconds"] == 1
    assert excinfo.value.result.timed_out


def test_retries_until_success_and_counts_attempts(tmp_path: Path) -> None:
    marker = tmp_path / "attempts.txt"
    script = (
        "import pathlib,sys; "
        f"m=pathlib.Path({str(marker)!r}); "
        "n=len(m.read_text()) if m.exists() else 0; "
        "m.write_text('x'*(n+1)); "
        "sys.exit(0 if n >= 1 else 5)"
    )
    executor = AutoLabExecutor(tmp_path, _config(script, retries=2))

    result = executor.execute({"task_id": "TASK-RETRY"}, run_root=tmp_path / "runs")

    assert result.succeeded
    assert result.attempts == 2
    assert json.loads(result.receipt_path.read_text())["attempts"] == 2


def test_nested_artifacts_are_reported_even_with_reserved_names(tmp_path: Path) -> None:
    script = (
        "import pathlib,sys; "
        "out=pathlib.Path(sys.argv[sys.argv.index('--output-dir')+1]); "
        "(out/'sub').mkdir(); "
        "(out/'sub'/'task.json').write_text('{}'); "
        "(out/'sub'/'data.csv').write_text('x')"
    )
    executor = AutoLabExecutor(tmp_path, _config(script))

    result = executor.execute({"task_id": "TASK-NESTED"}, run_root=tmp_path / "runs")

    relative = sorted(str(p.relative_to(result.run_dir)) for p in result.artifacts)
    # Only the executor's own top-level files are excluded; a nested file that
    # happens to share a reserved name is still evidence.
    assert relative == ["sub/data.csv", "sub/task.json"]


def test_rerunning_a_task_id_is_refused_with_the_module_error(tmp_path: Path) -> None:
    executor = AutoLabExecutor(tmp_path, _config("pass"))
    executor.execute({"task_id": "TASK-ONCE"}, run_root=tmp_path / "runs")

    with pytest.raises(AutoLabExecutionError, match="write-once"):
        executor.execute({"task_id": "TASK-ONCE"}, run_root=tmp_path / "runs")


def test_receipt_records_git_state_and_environment(tmp_path: Path) -> None:
    executor = AutoLabExecutor(tmp_path, _config("pass"))

    result = executor.execute(
        {"task_id": "TASK-PROV", "experiment_id": "EXP-AREA-abc123"},
        run_root=tmp_path / "runs",
    )

    receipt = json.loads(result.receipt_path.read_text())
    assert receipt["experiment_id"] == "EXP-AREA-abc123"
    assert set(receipt["git"]) == {"commit", "dirty"}
    assert receipt["environment"]["python_version"]
    assert receipt["schema_version"] == "1.1"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_retries": -1},
        {"timeout_seconds": 0},
        {"timeout_seconds": -5},
        {"command": ()},
    ],
)
def test_config_rejects_values_that_would_fabricate_a_result(kwargs: dict) -> None:
    with pytest.raises(AutoLabExecutionError):
        AutoLabConfig(**kwargs)


def test_from_env_parses_command_flags_and_child_environment() -> None:
    config = AutoLabConfig.from_env({
        "AUTOLAB_COMMAND": "python -m autolab run",
        "AUTOLAB_EXTRA_ARGS": "--workers 4",
        "AUTOLAB_TIMEOUT_SECONDS": "60",
        "AUTOLAB_MAX_RETRIES": "3",
        "AUTOLAB_TASK_FLAG": "--task-file",
        "AUTOLAB_OUTPUT_FLAG": "--out",
        "AUTOLAB_ENV": "AUTOLAB_SEED=7 AUTOLAB_MODE=bounded",
    })

    assert config.command == ("python", "-m", "autolab", "run")
    assert config.extra_args == ("--workers", "4")
    assert config.timeout_seconds == 60
    assert config.max_retries == 3
    assert config.task_flag == "--task-file"
    assert config.output_flag == "--out"
    assert config.env == {"AUTOLAB_SEED": "7", "AUTOLAB_MODE": "bounded"}


def test_from_env_defaults_and_rejects_malformed_values() -> None:
    default = AutoLabConfig.from_env({})
    assert default.command == ("autolab", "run")
    assert default.env == {}

    with pytest.raises(AutoLabExecutionError, match="AUTOLAB_MAX_RETRIES"):
        AutoLabConfig.from_env({"AUTOLAB_MAX_RETRIES": "many"})
    with pytest.raises(AutoLabExecutionError, match="AUTOLAB_ENV"):
        AutoLabConfig.from_env({"AUTOLAB_ENV": "NOEQUALS"})


def test_child_receives_task_binding_environment(tmp_path: Path) -> None:
    script = (
        "import os,pathlib,sys; "
        "out=pathlib.Path(sys.argv[sys.argv.index('--output-dir')+1]); "
        "(out/'env.txt').write_text("
        "os.environ['CRYPTO_AUTORESEARCHER_TASK_ID']+'|'"
        "+os.environ['CRYPTO_AUTORESEARCHER_TASK_DIGEST']+'|'"
        "+os.environ.get('EXTRA_FROM_CALLER',''))"
    )
    executor = AutoLabExecutor(tmp_path, _config(script))

    result = executor.execute(
        {"task_id": "TASK-ENV"},
        run_root=tmp_path / "runs",
        environment={"EXTRA_FROM_CALLER": "yes"},
    )

    task_id, digest, extra = (result.run_dir / "env.txt").read_text().split("|")
    assert task_id == "TASK-ENV"
    assert digest == result.task_digest
    assert extra == "yes"
