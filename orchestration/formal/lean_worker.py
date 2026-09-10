"""Bounded Lean verification worker.

The worker intentionally has no ledger or Coordinator dependency.  It verifies
files in a formal workspace and returns evidence for an independent reviewer
and the canonical Coordinator to interpret.
"""
from __future__ import annotations

import re
import subprocess
import tempfile
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

#: Constructs that mean "this proof is not finished" rather than "this source
#: violates the lane contract".  A generated candidate carrying only these is an
#: incomplete formalization; see ``orchestration.formal.mathcode``.
INCOMPLETE_PROOF_LABELS: frozenset[str] = frozenset({"sorry", "admit"})


def _lean_code(text: str) -> str:
    """Mask nested comments and strings while preserving offsets and newlines."""
    out = list(text)
    i, depth, quoted = 0, 0, False
    while i < len(text):
        if depth:
            if text.startswith('/-', i):
                out[i:i+2] = '  '; depth += 1; i += 2; continue
            if text.startswith('-/', i):
                out[i:i+2] = '  '; depth -= 1; i += 2; continue
        elif quoted:
            if text[i] == "\\" and i + 1 < len(text):
                out[i:i+2] = '  '; i += 2; continue
            if text[i] == '"': quoted = False
        elif text.startswith('--', i):
            end = text.find('\n', i)
            if end < 0: end = len(text)
            out[i:end] = ' ' * (end - i); i = end; continue
        elif text.startswith('/-', i):
            out[i:i+2] = '  '; depth = 1; i += 2; continue
        elif text[i] == '"':
            quoted = True
        else:
            i += 1; continue
        if text[i] != '\n': out[i] = ' '
        i += 1
    return ''.join(out)


def target_audit_source(module: str, theorem: str) -> str:
    """Trusted audit: the requested declaration must exist and be a theorem."""
    return f'''import {module}
import Lean
open Lean Elab Command
run_cmd do
  let target := `{theorem}
  match (← getEnv).find? target with
  | some (.thmInfo _) => pure ()
  | _ => throwError "requested declaration is not a theorem: {{target}}"
  let axioms ← liftCoreM <| Lean.collectAxioms target
  let allowed := [``propext, ``Classical.choice, ``Quot.sound]
  let bad := axioms.filter (fun a => !allowed.contains a)
  unless bad.isEmpty do
    throwError "target axiom audit failed: {{bad.toList}}"
  logInfo m!"target axiom audit passed: {{target}}"
'''


def scan_forbidden_text(text: str) -> tuple[str, ...]:
    """Return the labels of forbidden constructs present in one Lean source.

    Shared by the authoritative workspace scan below and by the pre-stage scan
    in the formalizer adapter, so a generated candidate is judged by exactly
    the patterns that will judge it again after staging.
    """

    code = _lean_code(text)
    return tuple(label for label, pattern in _FORBIDDEN_PATTERNS if pattern.search(code))


def forbidden_sites(text: str) -> tuple[tuple[str, int], ...]:
    """Return ``(label, line_number)`` for every forbidden construct occurrence.

    Line numbers are 1-based and point at the unfinished obligation, which is
    the pointer a ``find_proof_gap`` successor needs.
    """

    text = _lean_code(text)
    sites: list[tuple[str, int]] = []
    for label, pattern in _FORBIDDEN_PATTERNS:
        for match in pattern.finditer(text):
            sites.append((label, text.count("\n", 0, match.start()) + 1))
    return tuple(sorted(sites, key=lambda site: (site[1], site[0])))


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

        module_parts = Path(task.theorem_file).with_suffix("").parts
        name_pattern = r"[A-Za-z_][A-Za-z0-9_']*"
        if (Path(task.theorem_file).suffix != ".lean"
                or not all(re.fullmatch(name_pattern, p) for p in module_parts)
                or not all(re.fullmatch(name_pattern, p) for p in task.theorem_name.split("."))):
            return self._blocked(task, "unsupported Lean module or theorem name")
        module = ".".join(module_parts)
        forbidden = self._scan_forbidden(workspace)
        # Build this module even when the project root forgot to import it.
        build = self._run(["lake", "build"], cwd=workspace)
        if build.returncode == 0:
            target_build = self._run(["lake", "build", f"+{module}"], cwd=workspace)
            build = subprocess.CompletedProcess(target_build.args, target_build.returncode,
                                                self._log(build) + self._log(target_build), "")
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
        target_log = ""
        target_ok = False
        if audit.returncode == 0:
            # Do not trust a successful project-wide audit to imply that the
            # requested theorem was included. Check it using harness code.
            with tempfile.NamedTemporaryFile(mode="w", suffix=".lean", prefix="TargetAudit-",
                                             dir=workspace, encoding="utf-8") as audit_source:
                audit_source.write(target_audit_source(module, task.theorem_name))
                audit_source.flush()
                target = self._run(["lake", "env", "lean", audit_source.name], cwd=workspace)
            target_log = self._log(target)
            target_ok = target.returncode == 0
        status = FormalStatus.MACHINE_VERIFIED if target_ok else FormalStatus.FORMALIZATION_BLOCKED
        return FormalProofResult(
            task_id=task.task_id,
            status=status,
            build_passed=True,
            axiom_audit_passed=target_ok,
            forbidden_constructs=(),
            theorem_file=task.theorem_file,
            theorem_name=task.theorem_name,
            build_log=self._log(build),
            audit_log=self._log(audit) + target_log,
            blocking_reason=None if target_ok else "project or requested-theorem axiom audit failed",
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
            rel = path.relative_to(workspace)
            if any(part.startswith(".") for part in rel.parts):
                continue  # dependency/build caches are checked through theorem axioms
            if path.is_symlink() or not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            findings.extend(
                f"{label}:{path.relative_to(workspace)}" for label in scan_forbidden_text(text)
            )
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
