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
