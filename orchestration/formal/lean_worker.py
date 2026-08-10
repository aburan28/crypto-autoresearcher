"""Bounded Lean verification worker.

The worker intentionally has no ledger or Coordinator dependency.  It verifies
files in a formal workspace and returns evidence for an independent reviewer
and the canonical Coordinator to interpret.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Callable, Sequence

from .models import FormalProofResult, FormalProofTask, FormalStatus

Runner = Callable[..., subprocess.CompletedProcess[str]]

_FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("sorry", re.compile(r"\bsorry\b")),
    ("admit", re.compile(r"\badmit\b")),
    ("custom_axiom", re.compile(r"^\s*axiom\s+", re.MULTILINE)),
    ("unsafe", re.compile(r"\bunsafe\b")),
)


class LeanWorker:
    """Run reproducible Lean build and axiom-audit checks for one task."""

    def __init__(
        self,
        repo_root: str | Path,
        *,
        runner: Runner = subprocess.run,
        timeout_seconds: int = 900,
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.runner = runner
        self.timeout_seconds = timeout_seconds

    def verify(self, task: FormalProofTask) -> FormalProofResult:
        workspace = (self.repo_root / task.workspace).resolve()
        if self.repo_root not in workspace.parents and workspace != self.repo_root:
            raise ValueError("formal workspace escapes repository root")
        theorem_path = (workspace / task.theorem_file).resolve()
        if workspace not in theorem_path.parents:
            raise ValueError("theorem file escapes formal workspace")
        if not theorem_path.is_file():
            return self._blocked(task, f"missing theorem file: {task.theorem_file}")

        forbidden = self._scan_forbidden(workspace)
        build = self._run(["lake", "build"], cwd=workspace)
        if build.returncode != 0:
            return FormalProofResult(
                task_id=task.task_id,
                status=FormalStatus.FORMALIZATION_BLOCKED,
                build_passed=False,
                axiom_audit_passed=False,
                forbidden_constructs=forbidden,
                theorem_file=task.theorem_file,
                theorem_name=task.theorem_name,
                build_log=self._log(build),
                blocking_reason="lake build failed",
            )

        if forbidden:
            return FormalProofResult(
                task_id=task.task_id,
                status=FormalStatus.INVALID,
                build_passed=True,
                axiom_audit_passed=False,
                forbidden_constructs=forbidden,
                theorem_file=task.theorem_file,
                theorem_name=task.theorem_name,
                build_log=self._log(build),
                blocking_reason="forbidden proof construct detected",
            )

        audit_file = workspace / "AxiomAudit.lean"
        if not audit_file.is_file():
            return self._blocked(task, "missing AxiomAudit.lean", build_log=self._log(build))

        audit = self._run(["lake", "env", "lean", "AxiomAudit.lean"], cwd=workspace)
        status = (
            FormalStatus.MACHINE_VERIFIED
            if audit.returncode == 0
            else FormalStatus.FORMALIZATION_BLOCKED
        )
        return FormalProofResult(
            task_id=task.task_id,
            status=status,
            build_passed=True,
            axiom_audit_passed=audit.returncode == 0,
            forbidden_constructs=(),
            theorem_file=task.theorem_file,
            theorem_name=task.theorem_name,
            build_log=self._log(build),
            audit_log=self._log(audit),
            blocking_reason=None if audit.returncode == 0 else "axiom audit failed",
        )

    def _run(self, command: Sequence[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
        return self.runner(
            list(command),
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=self.timeout_seconds,
            check=False,
        )

    @staticmethod
    def _log(result: subprocess.CompletedProcess[str]) -> str:
        return (result.stdout or "") + (result.stderr or "")

    @staticmethod
    def _scan_forbidden(workspace: Path) -> tuple[str, ...]:
        findings: list[str] = []
        for path in sorted(workspace.rglob("*.lean")):
            text = path.read_text(encoding="utf-8")
            for label, pattern in _FORBIDDEN_PATTERNS:
                if pattern.search(text):
                    findings.append(f"{label}:{path.relative_to(workspace)}")
        return tuple(findings)

    @staticmethod
    def _blocked(
        task: FormalProofTask,
        reason: str,
        *,
        build_log: str = "",
    ) -> FormalProofResult:
        return FormalProofResult(
            task_id=task.task_id,
            status=FormalStatus.FORMALIZATION_BLOCKED,
            build_passed=False,
            axiom_audit_passed=False,
            forbidden_constructs=(),
            theorem_file=task.theorem_file,
            theorem_name=task.theorem_name,
            build_log=build_log,
            blocking_reason=reason,
        )
