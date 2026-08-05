"""AutoLab execution backend.

The adapter deliberately treats AutoLab as an untrusted execution substrate:
it receives a frozen task bundle, writes only inside a dedicated run directory,
and returns artifacts plus a machine-readable receipt. Promotion into the
research ledger remains the responsibility of the normal validator/red-team
pipeline.
"""
from __future__ import annotations

import hashlib
import json
import os
import shlex
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence


class AutoLabExecutionError(RuntimeError):
    """AutoLab could not be launched or returned an invalid result."""


@dataclass(frozen=True)
class AutoLabConfig:
    command: tuple[str, ...] = ("autolab", "run")
    timeout_seconds: int = 3600
    max_retries: int = 1
    output_flag: str = "--output-dir"
    task_flag: str = "--task"
    extra_args: tuple[str, ...] = ()
    env: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "AutoLabConfig":
        source = os.environ if env is None else env
        command = tuple(shlex.split(source.get("AUTOLAB_COMMAND", "autolab run")))
        extra_args = tuple(shlex.split(source.get("AUTOLAB_EXTRA_ARGS", "")))
        return cls(
            command=command,
            timeout_seconds=int(source.get("AUTOLAB_TIMEOUT_SECONDS", "3600")),
            max_retries=int(source.get("AUTOLAB_MAX_RETRIES", "1")),
            output_flag=source.get("AUTOLAB_OUTPUT_FLAG", "--output-dir"),
            task_flag=source.get("AUTOLAB_TASK_FLAG", "--task"),
            extra_args=extra_args,
        )


@dataclass(frozen=True)
class AutoLabResult:
    task_id: str
    run_dir: Path
    returncode: int
    duration_seconds: float
    attempts: int
    stdout_path: Path
    stderr_path: Path
    receipt_path: Path
    artifacts: tuple[Path, ...]
    task_digest: str

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0


class AutoLabExecutor:
    """Run a frozen crypto-autoresearcher task through AutoLab.

    The executor is intentionally CLI-based so the integration does not couple
    the long-lived research ledger to AutoLab's Python internals. Operators can
    adapt to different AutoLab releases with ``AUTOLAB_COMMAND`` and the flag
    environment variables without changing historical task bundles.
    """

    def __init__(self, repo_root: Path, config: AutoLabConfig | None = None):
        self.repo_root = Path(repo_root).resolve()
        self.config = config or AutoLabConfig.from_env()

    def execute(
        self,
        task: Mapping[str, Any],
        *,
        run_root: Path | None = None,
        environment: Mapping[str, str] | None = None,
    ) -> AutoLabResult:
        task_id = str(task.get("task_id") or task.get("id") or "").strip()
        if not task_id:
            raise AutoLabExecutionError("task must contain task_id or id")

        root = Path(run_root or self.repo_root / "runs" / "autolab").resolve()
        run_dir = root / task_id
        run_dir.mkdir(parents=True, exist_ok=False)

        task_path = run_dir / "task.json"
        canonical = json.dumps(task, sort_keys=True, separators=(",", ":"))
        task_path.write_text(canonical + "\n", encoding="utf-8")
        digest = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        stdout_path = run_dir / "stdout.log"
        stderr_path = run_dir / "stderr.log"
        receipt_path = run_dir / "execution-receipt.json"
        command = self._build_command(task_path, run_dir)
        env = os.environ.copy()
        env.update(self.config.env)
        if environment:
            env.update(environment)
        env.update({
            "CRYPTO_AUTORESEARCHER_TASK_ID": task_id,
            "CRYPTO_AUTORESEARCHER_TASK_DIGEST": digest,
            "CRYPTO_AUTORESEARCHER_REPO_ROOT": str(self.repo_root),
            "CRYPTO_AUTORESEARCHER_RUN_DIR": str(run_dir),
        })

        started = time.monotonic()
        returncode = 1
        attempts = 0
        last_error: str | None = None
        for attempts in range(1, self.config.max_retries + 2):
            try:
                with stdout_path.open("ab") as stdout, stderr_path.open("ab") as stderr:
                    completed = subprocess.run(
                        command,
                        cwd=self.repo_root,
                        env=env,
                        stdout=stdout,
                        stderr=stderr,
                        timeout=self.config.timeout_seconds,
                        check=False,
                    )
                returncode = completed.returncode
                if returncode == 0:
                    break
                last_error = f"AutoLab exited with status {returncode}"
            except FileNotFoundError as exc:
                raise AutoLabExecutionError(
                    f"AutoLab executable not found: {command[0]!r}; set AUTOLAB_COMMAND"
                ) from exc
            except subprocess.TimeoutExpired:
                returncode = 124
                last_error = f"AutoLab timed out after {self.config.timeout_seconds}s"

        duration = time.monotonic() - started
        artifacts = tuple(self._discover_artifacts(run_dir))
        receipt = {
            "schema_version": "1.0",
            "executor": "autolab",
            "task_id": task_id,
            "task_digest": digest,
            "command": command,
            "returncode": returncode,
            "attempts": attempts,
            "duration_seconds": round(duration, 6),
            "stdout": stdout_path.name,
            "stderr": stderr_path.name,
            "artifacts": [str(path.relative_to(run_dir)) for path in artifacts],
            "status": "succeeded" if returncode == 0 else "failed",
            "error": last_error,
            "promotion": "requires-independent-validation",
        }
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        result = AutoLabResult(
            task_id=task_id,
            run_dir=run_dir,
            returncode=returncode,
            duration_seconds=duration,
            attempts=attempts,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            receipt_path=receipt_path,
            artifacts=artifacts,
            task_digest=digest,
        )
        if not result.succeeded:
            raise AutoLabExecutionError(
                f"AutoLab execution failed for {task_id}: {last_error}; receipt={receipt_path}"
            )
        return result

    def _build_command(self, task_path: Path, run_dir: Path) -> list[str]:
        return [
            *self.config.command,
            self.config.task_flag,
            str(task_path),
            self.config.output_flag,
            str(run_dir),
            *self.config.extra_args,
        ]

    @staticmethod
    def _discover_artifacts(run_dir: Path) -> Sequence[Path]:
        excluded = {"task.json", "stdout.log", "stderr.log", "execution-receipt.json"}
        return sorted(
            path for path in run_dir.rglob("*")
            if path.is_file() and path.name not in excluded
        )
