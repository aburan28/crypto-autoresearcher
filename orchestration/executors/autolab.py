"""AutoLab execution backend.

The adapter deliberately treats AutoLab as an untrusted execution substrate:
it receives a frozen task bundle, is asked to write inside a dedicated run
directory, and returns artifacts plus a machine-readable receipt. Promotion
into the research ledger remains the responsibility of the normal
validator/red-team pipeline.

What this module does NOT do, stated plainly because the receipt is destined
for a ledger that scopes every claim to what was actually tested:

* It does not sandbox AutoLab. The child runs with ``cwd`` at the repository
  root and inherits the parent environment, so ``--output-dir`` is a request,
  not a confinement. A ``write_scope`` in the task bundle is passed through
  for the executed tool to honour; nothing here enforces it.
* It does not produce a run record. ``execution-receipt.json`` is a pre-ledger
  staging artifact. The immutable run-record schema lives in
  ``harness/runner.py`` (``experiments/<EXP>/runs/<RUN-ID>/manifest.yaml`` and
  siblings), is what ``tools/check_run_immutability.py`` and
  ``tools/validate_ledger.py`` enforce, and is what an evidence record cites.
  Converting a receipt into a ``RUN-*`` record — including independent
  re-verification of any solution certificate per
  ``docs/claims-and-verification.md`` — is a separate, deliberate step.
* It does not re-verify claims. Artifacts are captured, never interpreted.

For historical AutoLab packages already ported into harness layout, see
``tools/port_autolab_experiments.py`` (``$AUTOLAB_ROOT``), which is a distinct
integration from the live execution path implemented here.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shlex
import signal
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

# A run directory name is a single path segment under the run root. This is a
# safety constraint, not the project's ID policy: it rejects "..", separators,
# NUL, and absolute paths so an attacker-supplied or malformed task_id cannot
# steer writes out of the run root. Callers that need the TASK-YYYYMMDD-<tok>
# convention enforced should check it before handing the task over.
_SAFE_TASK_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

# Top-level names the executor owns. Compared against the path RELATIVE to the
# run directory, so an AutoLab tree that happens to contain sub/task.json still
# reports that file as an artifact.
_RESERVED_NAMES = frozenset(
    {"task.json", "stdout.log", "stderr.log", "execution-receipt.json"}
)


class AutoLabExecutionError(RuntimeError):
    """AutoLab could not be launched or returned an invalid result.

    ``result`` carries the :class:`AutoLabResult` when the failure happened
    after the receipt was written, so callers can reach artifacts, duration and
    the receipt path without re-parsing the message string. It is ``None`` for
    failures that precede execution (bad task, bad configuration).
    """

    def __init__(self, message: str, result: "AutoLabResult | None" = None):
        super().__init__(message)
        self.result = result


@dataclass(frozen=True)
class AutoLabConfig:
    command: tuple[str, ...] = ("autolab", "run")
    timeout_seconds: int = 3600
    max_retries: int = 1
    output_flag: str = "--output-dir"
    task_flag: str = "--task"
    extra_args: tuple[str, ...] = ()
    env: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Without these checks a negative max_retries makes the attempt loop
        # empty: nothing runs, and the receipt still reports a failure that
        # never happened. Fabricated failure records are exactly what
        # AGENTS.md rule 5 forbids.
        if not self.command:
            raise AutoLabExecutionError("command must not be empty")
        if self.max_retries < 0:
            raise AutoLabExecutionError(
                f"max_retries must be >= 0, got {self.max_retries}"
            )
        if self.timeout_seconds <= 0:
            raise AutoLabExecutionError(
                f"timeout_seconds must be > 0, got {self.timeout_seconds}"
            )

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "AutoLabConfig":
        source = os.environ if env is None else env
        command = tuple(shlex.split(source.get("AUTOLAB_COMMAND", "autolab run")))
        extra_args = tuple(shlex.split(source.get("AUTOLAB_EXTRA_ARGS", "")))
        return cls(
            command=command,
            timeout_seconds=cls._int(source, "AUTOLAB_TIMEOUT_SECONDS", 3600),
            max_retries=cls._int(source, "AUTOLAB_MAX_RETRIES", 1),
            output_flag=source.get("AUTOLAB_OUTPUT_FLAG", "--output-dir"),
            task_flag=source.get("AUTOLAB_TASK_FLAG", "--task"),
            extra_args=extra_args,
            env=cls._child_env(source.get("AUTOLAB_ENV", "")),
        )

    @staticmethod
    def _int(source: Mapping[str, str], name: str, default: int) -> int:
        raw = source.get(name)
        if raw is None or raw == "":
            return default
        try:
            return int(raw)
        except ValueError as exc:
            raise AutoLabExecutionError(
                f"{name} must be an integer, got {raw!r}"
            ) from exc

    @staticmethod
    def _child_env(raw: str) -> dict[str, str]:
        """Parse ``AUTOLAB_ENV="KEY=value OTHER=value"`` into a mapping."""
        parsed: dict[str, str] = {}
        for item in shlex.split(raw):
            key, sep, value = item.partition("=")
            if not sep or not key:
                raise AutoLabExecutionError(
                    f"AUTOLAB_ENV entries must be KEY=value, got {item!r}"
                )
            parsed[key] = value
        return parsed


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
    status: str = "succeeded"

    @property
    def succeeded(self) -> bool:
        return self.status == "succeeded"

    @property
    def timed_out(self) -> bool:
        return self.status == "timed_out"


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
        if not _SAFE_TASK_ID.match(task_id):
            raise AutoLabExecutionError(
                f"task_id {task_id!r} is not a safe run-directory name: expected "
                "[A-Za-z0-9][A-Za-z0-9._-]* with no path separators"
            )

        root = Path(run_root or self.repo_root / "runs" / "autolab").resolve()
        run_dir = root / task_id
        # Defence in depth: the regex above already rejects separators, so a
        # failure here means the constraint and the check drifted apart.
        if run_dir.resolve().parent != root:
            raise AutoLabExecutionError(
                f"refusing to run outside the run root: {run_dir} is not under {root}"
            )
        try:
            run_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError as exc:
            raise AutoLabExecutionError(
                f"run directory already exists at {run_dir}; AutoLab run "
                "directories are write-once, so a rerun needs a fresh task id"
            ) from exc

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
        status = "not_run"
        last_error: str | None = None
        for attempts in range(1, self.config.max_retries + 2):
            try:
                returncode = self._spawn(command, env, stdout_path, stderr_path)
            except FileNotFoundError:
                # Infrastructure failure, not a result: AGENTS.md rule 3 keeps
                # this out of the "failed" bucket. The receipt is still written
                # so the run directory is a complete record of what happened.
                status = "not_run"
                last_error = (
                    f"AutoLab executable not found: {command[0]!r}; set AUTOLAB_COMMAND"
                )
                break
            except subprocess.TimeoutExpired:
                returncode = 124
                status = "timed_out"
                last_error = f"AutoLab timed out after {self.config.timeout_seconds}s"
                continue
            if returncode == 0:
                status = "succeeded"
                break
            status = "failed"
            last_error = f"AutoLab exited with status {returncode}"

        duration = time.monotonic() - started
        artifacts = tuple(self._discover_artifacts(run_dir))
        receipt = {
            "schema_version": "1.1",
            "executor": "autolab",
            "task_id": task_id,
            "experiment_id": task.get("experiment_id"),
            "task_digest": digest,
            # Recorded verbatim, including AUTOLAB_EXTRA_ARGS. Do not pass
            # secrets there: this file is meant to be archived.
            "command": command,
            "returncode": returncode,
            "attempts": attempts,
            "timed_out": status == "timed_out",
            "timeout_seconds": self.config.timeout_seconds,
            "duration_seconds": round(duration, 6),
            "git": self._git_state(),
            "environment": self._environment(),
            "stdout": stdout_path.name,
            "stderr": stderr_path.name,
            "artifacts": [str(path.relative_to(run_dir)) for path in artifacts],
            # succeeded | failed | timed_out | not_run. timed_out and not_run
            # are infrastructure outcomes and are never negative mathematical
            # evidence (AGENTS.md rule 3).
            "status": status,
            "error": last_error,
            "promotion": "requires-independent-validation",
            # Set when a receipt has been converted into an immutable run
            # record under experiments/<EXP>/runs/. Null means this execution
            # is not citable by an evidence record yet.
            "ledger_run_id": None,
        }
        receipt_path.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

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
            status=status,
        )
        if not result.succeeded:
            raise AutoLabExecutionError(
                f"AutoLab execution failed for {task_id}: {last_error}; "
                f"receipt={receipt_path}",
                result,
            )
        return result

    def _spawn(
        self,
        command: Sequence[str],
        env: Mapping[str, str],
        stdout_path: Path,
        stderr_path: Path,
    ) -> int:
        """Run one attempt, killing the whole process group on timeout.

        ``subprocess.run(timeout=...)`` only kills the direct child, so a tool
        launched with ``--workers N`` leaves its workers writing into the run
        directory after the receipt is sealed. A new session plus a group kill
        closes that window.
        """
        new_session = os.name == "posix"
        with stdout_path.open("ab") as stdout, stderr_path.open("ab") as stderr:
            process = subprocess.Popen(
                list(command),
                cwd=self.repo_root,
                env=dict(env),
                stdout=stdout,
                stderr=stderr,
                start_new_session=new_session,
            )
            try:
                return process.wait(timeout=self.config.timeout_seconds)
            except subprocess.TimeoutExpired:
                self._terminate(process, new_session)
                raise

    @staticmethod
    def _terminate(process: "subprocess.Popen[bytes]", new_session: bool) -> None:
        try:
            if new_session:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            else:
                process.kill()
        except OSError:
            # Group kill can fail if the leader is already reaped; the direct
            # kill is still worth attempting and is a no-op on a dead child.
            process.kill()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            pass

    def _git_state(self) -> dict[str, Any]:
        """Commit and dirty flag, mirroring ``harness.runner.git_state``.

        Untracked files are ignored on purpose: the run outputs being written
        are untracked and do not affect reproducibility.
        """
        commit = self._git("rev-parse", "HEAD")
        if commit is None:
            return {"commit": "unknown", "dirty": None}
        porcelain = self._git("status", "--porcelain", "--untracked-files=no")
        return {"commit": commit or "unknown", "dirty": bool(porcelain)}

    def _git(self, *args: str) -> str | None:
        try:
            completed = subprocess.run(
                ["git", *args],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return None
        if completed.returncode != 0:
            return None
        return completed.stdout.strip()

    @staticmethod
    def _environment() -> dict[str, str]:
        return {
            "operating_system": platform.platform(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
        }

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
        return sorted(
            path for path in run_dir.rglob("*")
            if path.is_file() and str(path.relative_to(run_dir)) not in _RESERVED_NAMES
        )
