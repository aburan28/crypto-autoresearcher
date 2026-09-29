"""MathCode formalizer: a natural-language claim in, candidate Lean source out.

The formal lane already had a verifier (:mod:`orchestration.formal.lean_worker`)
and no producer, so every task returned ``missing theorem file`` unless a human
hand-wrote the Lean.  This module is that producer: it drives the MathCode
terminal agent (https://github.com/math-ai-org/mathcode) to turn
``FormalProofTask.claim`` into a Lean 4 file, and hands the file to the existing
worker unchanged.

Three properties are deliberate.

**The engine is untrusted.**  MathCode is a language model with a Lean REPL
attached.  Nothing it emits is evidence.  Its output is a *proposal* whose only
route to evidence is ``lake build`` plus the axiom audit plus an independent
semantic-fidelity review, exactly as before this module existed.

**The engine runs outside the workspace.**  MathCode is an autonomous coding
agent that writes files where it is run, and ``LeanWorker`` scans *every*
``.lean`` file under the workspace.  Letting the agent loose in ``formal/``
would let one abandoned scratch file carrying ``sorry`` mark every later task in
the workspace ``INVALID``.  Each attempt therefore gets its own directory
outside the workspace, and only the one selected file is staged in.

**An unfinished proof is not a contract violation.**  A candidate whose only
forbidden constructs are ``sorry``/``admit`` is an incomplete formalization: it
is never staged (that would poison the workspace scan), it is kept in the
attempt directory, and the unproved sites are reported as the proof obligation a
``find_proof_gap`` successor should attack.  A candidate carrying a custom
``axiom`` or ``unsafe`` is a different thing — an attempt to smuggle in an
assumption — and is reported as invalid.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Mapping, Sequence

from .lean_worker import INCOMPLETE_PROOF_LABELS, forbidden_sites, scan_forbidden_text
from .models import FormalProofTask, FormalTaskKind

Runner = Callable[..., subprocess.CompletedProcess[str]]
Which = Callable[[str], str | None]

ENGINE_NAME = "mathcode"

#: Where MathCode writes its formalizations, relative to the process cwd.
OUTPUT_DIRNAME = "LeanFormalizations"

#: Attempt directories live here, under the repository root but outside any
#: Lean workspace.  Generated scratch is never committed; see .gitignore.
DEFAULT_ATTEMPT_ROOT = ".formal-attempts"

_LOG_LIMIT = 20_000


class FormalizationFailure(str, Enum):
    """Why a formalization attempt produced no staged theorem file.

    Only ``INCOMPLETE_PROOF`` and ``FORBIDDEN_CONSTRUCT`` say anything about the
    Lean the engine wrote.  Every other member is an infrastructure fact about
    the engine, and AGENTS.md rule 3 forbids reading any of them as negative
    mathematical evidence about the claim.
    """

    ENGINE_UNAVAILABLE = "engine_unavailable"
    ENGINE_ERROR = "engine_error"
    TIMEOUT = "timeout"
    NO_OUTPUT = "no_output"
    THEOREM_NAME_MISSING = "theorem_name_missing"
    INCOMPLETE_PROOF = "incomplete_proof"
    FORBIDDEN_CONSTRUCT = "forbidden_construct"

    @property
    def is_infrastructure(self) -> bool:
        return self not in (
            FormalizationFailure.INCOMPLETE_PROOF,
            FormalizationFailure.FORBIDDEN_CONSTRUCT,
        )


@dataclass(frozen=True)
class MathCodeConfig:
    """Resolved engine settings, recorded verbatim in every attempt record."""

    binary: str = ENGINE_NAME
    effort: str = "high"
    timeout_seconds: int = 1800
    attempt_root: str = DEFAULT_ATTEMPT_ROOT
    #: MATHCODE_* knobs passed to the engine process.  Documented at
    #: https://math-ai-org.github.io/mathcode/ ; the defaults buy the fast
    #: persistent REPL and structured Lean feedback, which is what makes an
    #: unattended attempt worth running at all.
    engine_env: Mapping[str, str] = field(
        default_factory=lambda: {
            "MATHCODE_LEAN_REPL": "1",
            "MATHCODE_USE_LSP": "1",
            "MATHCODE_AGENT_PROVE": "1",
        }
    )

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "MathCodeConfig":
        env = os.environ if environ is None else environ
        base = cls()
        engine_env = dict(base.engine_env)
        # Anything the operator already exported wins over our default, so a
        # session can turn tree proving on without editing code.
        for key, value in env.items():
            if key.startswith("MATHCODE_"):
                engine_env[key] = value
        timeout = env.get("AUTORESEARCH_MATHCODE_TIMEOUT")
        return cls(
            binary=env.get("AUTORESEARCH_MATHCODE_BIN", base.binary),
            effort=env.get("AUTORESEARCH_MATHCODE_EFFORT", base.effort),
            timeout_seconds=int(timeout) if timeout else base.timeout_seconds,
            attempt_root=env.get("AUTORESEARCH_FORMAL_ATTEMPT_ROOT", base.attempt_root),
            engine_env=engine_env,
        )


@dataclass(frozen=True)
class FormalizationAttempt:
    """One bounded engine invocation and what it left on disk.

    Never authoritative.  ``staged`` only means a candidate file was placed in
    the workspace for the verifier to judge.
    """

    task_id: str
    engine: str
    staged: bool
    theorem_file: str
    attempt_dir: str
    prompt_sha256: str
    source_sha256: str | None = None
    source_path: str | None = None
    harvested_files: Sequence[str] = ()
    unproved_sites: Sequence[str] = ()
    forbidden_constructs: Sequence[str] = ()
    exit_code: int | None = None
    duration_seconds: float | None = None
    engine_version: str | None = None
    engine_env: Mapping[str, str] = field(default_factory=dict)
    failure: FormalizationFailure | None = None
    blocking_reason: str | None = None
    log: str = ""

    @property
    def infrastructure_failure(self) -> bool:
        return self.failure is not None and self.failure.is_infrastructure

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "crypto.autoresearch.formalization_attempt.v1",
            "task_id": self.task_id,
            "engine": self.engine,
            "engine_version": self.engine_version,
            "engine_env": dict(self.engine_env),
            "staged": self.staged,
            "theorem_file": self.theorem_file,
            "attempt_dir": self.attempt_dir,
            "prompt_sha256": self.prompt_sha256,
            "source_sha256": self.source_sha256,
            "source_path": self.source_path,
            "harvested_files": list(self.harvested_files),
            "unproved_sites": list(self.unproved_sites),
            "forbidden_constructs": list(self.forbidden_constructs),
            "exit_code": self.exit_code,
            "duration_seconds": self.duration_seconds,
            "failure": self.failure.value if self.failure else None,
            "infrastructure_failure": self.infrastructure_failure,
            "blocking_reason": self.blocking_reason,
        }


_KIND_INSTRUCTION: Mapping[FormalTaskKind, str] = {
    FormalTaskKind.FORMALIZE_CLAIM: (
        "Encode the claim as a single Lean 4 theorem and prove it. Do not weaken "
        "the statement to make it provable; if you cannot prove the faithful "
        "statement, leave the proof unfinished rather than proving something else."
    ),
    FormalTaskKind.FIND_PROOF_GAP: (
        "Encode the claim faithfully, then drive the proof as far as it goes and "
        "stop at the smallest lemma you cannot discharge. Leave exactly that "
        "obligation open and state it as a named lemma so it can be attacked "
        "separately."
    ),
    FormalTaskKind.FORMAL_COUNTEREXAMPLE: (
        "Attempt to REFUTE the claim: state its negation as the theorem and prove "
        "the negation, or exhibit a concrete finite counterexample and prove that "
        "it falsifies the claim."
    ),
    FormalTaskKind.PROOF_GENERALIZATION: (
        "State the most general theorem you can actually prove that still implies "
        "the claim, and make every assumption it needs an explicit hypothesis of "
        "the theorem rather than a global assumption."
    ),
}


class MathCodeFormalizer:
    """Drive the MathCode CLI for one formal task.

    Has no ledger, Coordinator, or campaign dependency, and cannot mark anything
    verified: the most it can do is put a candidate file where the verifier will
    look for it.
    """

    def __init__(
        self,
        repo_root: str | Path,
        *,
        config: MathCodeConfig | None = None,
        runner: Runner = subprocess.run,
        which: Which = shutil.which,
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.config = config or MathCodeConfig.from_env()
        self.runner = runner
        self.which = which

    # -- engine discovery -------------------------------------------------

    def resolve_binary(self) -> str | None:
        """Absolute path to the ``mathcode`` launcher, or None if not installed."""

        return self.which(self.config.binary)

    def engine_version(self) -> str | None:
        """Whatever the engine reports for ``--version``, or None.

        None is recorded as None.  A version string is never invented for a
        provenance block.
        """

        binary = self.resolve_binary()
        if binary is None:
            return None
        try:
            result = self.runner(
                [binary, "--version"],
                cwd=self.repo_root,
                text=True,
                capture_output=True,
                timeout=60,
                check=False,
                env=self._process_env(),
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if result.returncode != 0:
            return None
        return (result.stdout or "").strip() or None

    # -- prompt -----------------------------------------------------------

    def build_prompt(self, task: FormalProofTask) -> str:
        """The exact text handed to the engine, hashed into the attempt record."""

        leaf = task.theorem_name.rsplit(".", 1)[-1]
        return "\n".join(
            (
                "You are producing a Lean 4 artifact for an automated verification "
                "pipeline. The file you write is compiled with `lake build` against "
                "Mathlib and then audited with `#print axioms`.",
                "",
                f"CLAIM ({task.claim_id}):",
                task.claim.strip(),
                "",
                f"TASK: {_KIND_INSTRUCTION[task.kind]}",
                "",
                "OUTPUT CONTRACT:",
                f"- Write one self-contained Lean 4 file named `{Path(task.theorem_file).name}`.",
                "- Begin it with `import Mathlib`.",
                f"- Name the top-level result `{leaf}`"
                + (
                    f", placed so that its fully qualified name is `{task.theorem_name}`."
                    if leaf != task.theorem_name
                    else "."
                ),
                "- Use no `axiom` declaration and no `unsafe` declaration: an assumption "
                "the audit cannot see makes the artifact worthless.",
                "- State assumptions as explicit hypotheses of the theorem.",
                "- Prefer an honestly unfinished proof over a vacuous or weakened "
                "statement. A statement that is true but does not capture the claim "
                "is a failure of this task, not a partial success.",
            )
        )

    # -- the attempt ------------------------------------------------------

    def formalize(self, task: FormalProofTask) -> FormalizationAttempt:
        """Run the engine once and stage a clean candidate into the workspace."""

        workspace = self._workspace(task)
        theorem_path = self._theorem_path(workspace, task)
        prompt = self.build_prompt(task)
        prompt_sha = _sha256_text(prompt)
        attempt_dir = self._new_attempt_dir(task)

        def attempt(**overrides: object) -> FormalizationAttempt:
            base = dict(
                task_id=task.task_id,
                engine=ENGINE_NAME,
                staged=False,
                theorem_file=task.theorem_file,
                attempt_dir=str(attempt_dir),
                prompt_sha256=prompt_sha,
                engine_env=dict(self.config.engine_env),
            )
            base.update(overrides)
            return FormalizationAttempt(**base)  # type: ignore[arg-type]

        (attempt_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

        binary = self.resolve_binary()
        if binary is None:
            return attempt(
                failure=FormalizationFailure.ENGINE_UNAVAILABLE,
                blocking_reason=(
                    f"{self.config.binary} not found on PATH; install MathCode "
                    "(docs/mathcode-integration.md) — no formalization was attempted"
                ),
            )

        version = self.engine_version()
        started = time.monotonic()
        try:
            result = self.runner(
                [binary, "--effort", self.config.effort, "-p", prompt],
                cwd=attempt_dir,
                text=True,
                capture_output=True,
                timeout=self.config.timeout_seconds,
                check=False,
                env=self._process_env(),
            )
        except subprocess.TimeoutExpired:
            return attempt(
                engine_version=version,
                duration_seconds=round(time.monotonic() - started, 3),
                failure=FormalizationFailure.TIMEOUT,
                blocking_reason=(
                    f"engine exceeded {self.config.timeout_seconds}s; this is a budget "
                    "fact about the attempt, not evidence about the claim"
                ),
            )
        except OSError as exc:
            return attempt(
                engine_version=version,
                duration_seconds=round(time.monotonic() - started, 3),
                failure=FormalizationFailure.ENGINE_ERROR,
                blocking_reason=f"could not execute {binary}: {exc}",
            )

        duration = round(time.monotonic() - started, 3)
        log = _truncate(_join_streams(result))
        harvested = self._harvest(attempt_dir)
        common = dict(
            engine_version=version,
            duration_seconds=duration,
            exit_code=result.returncode,
            harvested_files=tuple(str(p.relative_to(attempt_dir)) for p in harvested),
            log=log,
        )

        if not harvested:
            reason = (
                f"engine exited {result.returncode} and wrote no Lean file"
                if result.returncode != 0
                else f"engine exited 0 but wrote no Lean file under {OUTPUT_DIRNAME}/"
            )
            return attempt(
                failure=(
                    FormalizationFailure.ENGINE_ERROR
                    if result.returncode != 0
                    else FormalizationFailure.NO_OUTPUT
                ),
                blocking_reason=reason,
                **common,
            )

        selected = self._select(harvested, task.theorem_name)
        if selected is None:
            return attempt(
                failure=FormalizationFailure.THEOREM_NAME_MISSING,
                blocking_reason=(
                    f"no generated file declares `{task.theorem_name.rsplit('.', 1)[-1]}`; "
                    "the engine answered a different question than the task asked"
                ),
                **common,
            )

        source = selected.read_text(encoding="utf-8")
        common["source_path"] = str(selected.relative_to(attempt_dir))
        common["source_sha256"] = _sha256_text(source)

        constructs = scan_forbidden_text(source)
        if constructs:
            sites = tuple(f"{label}:{line}" for label, line in forbidden_sites(source))
            incomplete_only = set(constructs) <= INCOMPLETE_PROOF_LABELS
            return attempt(
                forbidden_constructs=constructs,
                unproved_sites=sites,
                failure=(
                    FormalizationFailure.INCOMPLETE_PROOF
                    if incomplete_only
                    else FormalizationFailure.FORBIDDEN_CONSTRUCT
                ),
                blocking_reason=(
                    "proof incomplete: unfinished obligations remain at "
                    + ", ".join(sites)
                    if incomplete_only
                    else "generated source declares "
                    + ", ".join(sorted(set(constructs) - INCOMPLETE_PROOF_LABELS))
                    + "; an assumption the axiom audit cannot see is not admissible"
                ),
                **common,
            )

        theorem_path.parent.mkdir(parents=True, exist_ok=True)
        theorem_path.write_text(source, encoding="utf-8")
        return attempt(staged=True, **common)

    # -- internals --------------------------------------------------------

    def _workspace(self, task: FormalProofTask) -> Path:
        workspace = (self.repo_root / task.workspace).resolve()
        if self.repo_root not in workspace.parents and workspace != self.repo_root:
            raise ValueError("formal workspace escapes repository root")
        return workspace

    def _theorem_path(self, workspace: Path, task: FormalProofTask) -> Path:
        # FormalProofTask already rejects absolute paths and `..` segments; this
        # re-checks after resolution so a symlinked subdirectory cannot land a
        # generated file outside the workspace.
        theorem_path = (workspace / task.theorem_file).resolve()
        if workspace not in theorem_path.parents:
            raise ValueError("theorem file escapes formal workspace")
        return theorem_path

    def _new_attempt_dir(self, task: FormalProofTask) -> Path:
        if set(task.task_id) & set("/\\") or task.task_id in (".", ".."):
            raise ValueError(f"task_id is used as a directory name: {task.task_id!r}")
        root = Path(self.config.attempt_root)
        if not root.is_absolute():
            root = self.repo_root / root
        # Retries never overwrite a previous attempt: the artifacts of a failed
        # formalization are the record of what was tried.
        for suffix in ("",) + tuple(f".{n}" for n in range(2, 1000)):
            candidate = root / f"{task.task_id}{suffix}"
            if not candidate.exists():
                candidate.mkdir(parents=True)
                return candidate
        raise RuntimeError(f"too many formalization attempts for {task.task_id}")

    def _process_env(self) -> dict[str, str]:
        env = dict(os.environ)
        env.update(self.config.engine_env)
        return env

    @staticmethod
    def _harvest(attempt_dir: Path) -> tuple[Path, ...]:
        """Lean files the engine wrote, preferring its documented output dir."""

        outputs = attempt_dir / OUTPUT_DIRNAME
        search_root = outputs if outputs.is_dir() else attempt_dir
        return tuple(sorted(p for p in search_root.rglob("*.lean") if p.is_file()))

    @staticmethod
    def _select(candidates: Sequence[Path], theorem_name: str) -> Path | None:
        """Pick the file that declares the requested theorem, newest first.

        Matching is on the unqualified name because the declaration inside the
        file is `theorem foo`, however many namespaces enclose it.
        """

        leaf = theorem_name.rsplit(".", 1)[-1]
        declaring = [
            path
            for path in candidates
            if any(
                f"{keyword} {leaf}" in path.read_text(encoding="utf-8")
                for keyword in ("theorem", "lemma", "def")
            )
        ]
        if not declaring:
            return None
        return max(declaring, key=lambda path: path.stat().st_mtime)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _join_streams(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stdout or "") + (result.stderr or "")


def _truncate(text: str, limit: int = _LOG_LIMIT) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... [truncated {len(text) - limit} characters]"


__all__ = [
    "ENGINE_NAME",
    "FormalizationAttempt",
    "FormalizationFailure",
    "MathCodeConfig",
    "MathCodeFormalizer",
]
