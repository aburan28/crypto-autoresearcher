"""Execute eval trials against the real runtime.

An eval that ran a special code path would measure the special code path. Each
trial goes through `orchestration.agent.runner.run_task` exactly as a dispatched
research task does -- same resolution, same tool loop, same scope enforcement --
only pointed at a throwaway sandbox.

Failures are results. A trial that crashed, timed out, or exhausted its budget
is recorded as such and counted against the arm; it is never dropped for being
inconvenient.
"""
from __future__ import annotations

import json
import tempfile
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from ..adapter import config as config_module
from ..adapter import resolver as resolver_module
from . import fingerprint as fingerprint_module
from . import graders as graders_module
from . import report as report_module
from .tasks import EvalTask, Suite, build_sandbox, sandbox_task


@dataclass
class TrialResult:
    task_id: str
    trial: int
    passed: bool
    score: float
    stop_reason: str
    steps: int
    wall_seconds: float
    usage: dict[str, int] = field(default_factory=dict)
    denials: int = 0
    verdicts: list[graders_module.Verdict] = field(default_factory=list)
    final_text: str = ""
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id, "trial": self.trial, "passed": self.passed,
            "score": self.score, "stop_reason": self.stop_reason,
            "steps": self.steps, "wall_seconds": self.wall_seconds,
            "usage": self.usage, "denials": self.denials, "error": self.error,
            "verdicts": [{"grader": v.grader, "passed": v.passed,
                          "detail": v.detail, "critical": v.critical}
                         for v in self.verdicts],
        }


def run_trial(task: EvalTask, trial: int, *, config: config_module.Config,
              backend: str | None = None, repo: Path | None = None,
              opener: Callable[..., Any] | None = None,
              keep_sandbox: Path | None = None,
              seed_offset: int = 0) -> TrialResult:
    from ..agent import runner as agent_runner

    repo = repo or Path(agent_runner.REPO)
    root = (Path(keep_sandbox) / f"{task.id}-{trial}" if keep_sandbox
            else Path(tempfile.mkdtemp(prefix=f"eval-{task.id}-{trial}-")))
    started = time.monotonic()
    try:
        sandbox, _secrets = build_sandbox(task, root, repo=repo,
                                          seed_offset=seed_offset)
        dispatch = sandbox_task(task, sandbox)
        run = agent_runner.run_task(
            dispatch, config=config, backend=backend, repo_root=sandbox,
            max_steps=task.max_steps, opener=opener)
    except Exception as exc:                          # recorded, never swallowed
        return TrialResult(
            task_id=task.id, trial=trial, passed=False, score=0.0,
            stop_reason="trial_error", steps=0,
            wall_seconds=round(time.monotonic() - started, 3),
            error=f"{type(exc).__name__}: {exc}\n{traceback.format_exc(limit=3)}")

    context = graders_module.GradingContext(
        sandbox=Path(root), final_text=run.final_text, journal=run.journal,
        stop_reason=run.stop_reason, files_written=run.files_written,
        task={"id": task.id, "kind": task.kind, "role": task.role})
    verdicts = graders_module.run_graders(context, task.graders)

    return TrialResult(
        task_id=task.id, trial=trial,
        passed=graders_module.trial_passed(verdicts),
        score=graders_module.trial_score(verdicts),
        stop_reason=run.stop_reason, steps=run.steps,
        wall_seconds=run.wall_seconds, usage=run.usage,
        denials=len([e for e in run.journal if "denied" in e]),
        verdicts=verdicts, final_text=run.final_text)


def run_suite(suite: Suite, *, config: config_module.Config | None = None,
              backend: str | None = None, trials: int = 3,
              repo: Path | None = None,
              opener: Callable[..., Any] | None = None,
              keep_sandbox: Path | None = None,
              seed_offset: int = 0,
              progress: Callable[[TrialResult], None] | None = None
              ) -> tuple[report_module.RunSummary, list[TrialResult]]:
    config = config or config_module.load()
    resolved_backend = backend or config.default_backend()

    # Refuse before spending anything if the arm cannot serve the suite: a
    # benchmark run against a silently different model measures nothing.
    for task in suite.tasks:
        if task.policy:
            resolver_module.resolve(
                config, task.policy, backend=backend,
                fallback_allowed=bool((task.handoff.get("inference") or {})
                                      .get("fallback_allowed")),
                independent_session=True)

    all_trials: list[TrialResult] = []
    summaries: list[report_module.TaskSummary] = []
    for task in suite.tasks:
        results = []
        for index in range(trials):
            result = run_trial(task, index, config=config, backend=backend,
                               repo=repo, opener=opener, keep_sandbox=keep_sandbox,
                               seed_offset=seed_offset)
            results.append(result)
            all_trials.append(result)
            if progress:
                progress(result)
        summaries.append(report_module.summarise_task(task.id, task.kind, results))
    return (report_module.RunSummary(suite.name, resolved_backend, summaries),
            all_trials)


def write_results(summary: report_module.RunSummary, trials: list[TrialResult],
                  out_dir: str | Path, *, suite_path: str | None = None,
                  config: config_module.Config | None = None) -> dict[str, Path]:
    """Eval results are immutable records, like everything else here.

    They are evidence about the harness and its backends. They are NOT
    mathematical evidence about ECDLP and must never be cited as such, which is
    why they live outside `ledger/`.
    """
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)
    written = {}
    for name, payload in (
            ("summary.json", {**summary.to_dict(),
                              "suite_path": suite_path,
                              "config_digest": config.digest if config else None,
                              # Without this a score cannot be attributed to a
                              # version of the thing being tuned.
                              "fingerprint": fingerprint_module.harness_fingerprint(
                                  suite_path=suite_path,
                                  config_digest=config.digest if config else None),
                              "scope": "evidence about the harness and backend, "
                                       "not about ECDLP"}),
            ("trials.json", [t.to_dict() for t in trials])):
        path = directory / name
        if path.exists():
            raise FileExistsError(f"{path} already exists; eval records are immutable")
        path.write_text(json.dumps(payload, indent=2, default=str) + "\n",
                        encoding="utf-8")
        written[name] = path
    report_path = directory / "report.txt"
    if report_path.exists():
        raise FileExistsError(f"{report_path} already exists; eval records are immutable")
    report_path.write_text(report_module.render(summary) + "\n", encoding="utf-8")
    written["report.txt"] = report_path
    return written
