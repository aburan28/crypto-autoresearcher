"""Optional Frontier-CS / Harbor backend for the eval harness.

Frontier-CS (https://github.com/FrontierCS/Frontier-CS) is an external benchmark
of unsolved, open-ended, *verifiable* computer-science problems. Harbor is the
agent-evaluation framework it ships adapters for. This module lets the harness
measure its own agent arms against that benchmark and fold the numbers into the
same immutable record shape the internal suite produces, so an arm can be
compared on one axis instead of two incompatible ones.

Why bother, given `evals/suites/*` already exist: the internal suites are
written by the same program they grade. They can tell you an arm follows the
protocol and does not fabricate; they cannot tell you whether it is any good at
hard problems nobody has solved. Frontier-CS is scored by a verifier this
repository did not write, which is exactly the property the internal suites lack.

SCOPE, and it is not negotiable. A Frontier-CS score is evidence about an
`(agent, model)` arm. It is NOT mathematical evidence about ECDLP, it never
promotes a hypothesis, and it never appears in `ledger/`. A high score on
`algorithmic/0` says nothing about the discrete logarithm problem. Records land
under `evals/` with an explicit scope string, same as the internal runner.

Nothing here is required. Frontier-CS needs Python 3.11+, Docker 24+, and API
credentials; when any of that is missing `probe()` says so and the caller
reports unavailability. It never substitutes a guess for a measurement, and a
missing benchmark is never recorded as a zero — an absent number and a bad
number are different facts.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

import yaml

from orchestration.adapter import config as config_module

from . import graders as graders_module
from . import report as report_module
from .runner import TrialResult

# Frontier-CS tracks, per its CLI. `2.0` is the agent-native track whose tasks
# accept iterative `submit.sh` feedback during a trial.
TRACKS = ("algorithmic", "research", "2.0")

# Harbor reports `score` on 0-100. Internal grader scores are 0-1, and mixing
# the two silently would make every comparison wrong by a factor of 100.
SCORE_SCALE = 100.0

# Trial statuses Harbor reports that mean "the agent never got a fair run".
# These are infrastructure outcomes, not capability outcomes, and AGENTS.md
# rule 5 forbids reading them as evidence against the thing under test.
INFRA_STATUSES = frozenset({
    "AgentTimeoutError", "AgentExecutionError", "HarborInternalError",
    "DockerError", "SetupError",
})


def _assert_task_target_allowed(task: "HarborTask") -> None:
    """Use the adapter's single no-Bedrock authority before Harbor launches."""
    try:
        config_module.load().assert_inference_target_allowed(
            task.agent, task.model,
            context=f"Harbor task {task.id} inference target")
    except config_module.ConfigError as exc:
        raise ValueError(f"{task.id}: {exc}") from None


class HarborUnavailable(RuntimeError):
    """Frontier-CS/Harbor cannot run here. Not a score of zero."""


@dataclass
class HarborTask:
    """One Frontier-CS problem, pinned to an arm."""
    id: str
    track: str
    problem: str
    agent: str
    model: str
    policy: str | None = None       # harness policy alias this arm stands for
    timeout_seconds: int = 3600
    tags: list[str] = field(default_factory=list)
    split: str = "dev"

    def __post_init__(self) -> None:
        if self.track not in TRACKS:
            raise ValueError(
                f"{self.id}: unknown Frontier-CS track {self.track!r} "
                f"(expected one of {', '.join(TRACKS)})")
        _assert_task_target_allowed(self)


@dataclass
class HarborSuite:
    name: str
    description: str
    tasks: list[HarborTask]

    def filter(self, ids: Sequence[str] | None = None,
               tracks: Sequence[str] | None = None,
               splits: Sequence[str] | None = None) -> "HarborSuite":
        tasks = [t for t in self.tasks
                 if (not ids or t.id in ids)
                 and (not tracks or t.track in tracks)
                 and (not splits or t.split in splits)]
        return HarborSuite(self.name, self.description, tasks)


def load_suite(path: str | Path) -> HarborSuite:
    document = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    suite = document["harbor_suite"]
    tasks: list[HarborTask] = []
    seen: set[str] = set()
    for entry in suite["tasks"]:
        task = HarborTask(
            id=entry["id"], track=str(entry["track"]), problem=str(entry["problem"]),
            agent=entry["agent"], model=entry["model"],
            policy=entry.get("policy"),
            timeout_seconds=int(entry.get("timeout_seconds", 3600)),
            tags=entry.get("tags") or [], split=entry.get("split", "dev"))
        if task.id in seen:
            raise ValueError(f"duplicate harbor task id {task.id}")
        seen.add(task.id)
        tasks.append(task)
    return HarborSuite(suite["name"], suite.get("description", ""), tasks)


# --------------------------------------------------------------------------
# availability
# --------------------------------------------------------------------------
@dataclass
class Probe:
    available: bool
    frontier: str | None
    harbor: str | None
    docker: str | None
    missing: list[str]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"available": self.available, "frontier": self.frontier,
                "harbor": self.harbor, "docker": self.docker,
                "missing": self.missing, "notes": self.notes}

    def require(self) -> None:
        if not self.available:
            raise HarborUnavailable(
                "Frontier-CS/Harbor is not runnable here; missing: "
                + ", ".join(self.missing)
                + ". Install per https://github.com/FrontierCS/Frontier-CS "
                  "(Python 3.11+, Docker 24+, `uv sync`). No score is recorded.")


def probe(*, which: Callable[[str], str | None] = shutil.which,
          env: dict[str, str] | None = None) -> Probe:
    """Report what is and is not present. Never guesses, never installs."""
    env = os.environ if env is None else env
    frontier = which("frontier")
    harbor = which("harbor")
    docker = which("docker")

    missing: list[str] = []
    notes: list[str] = []
    if not frontier:
        missing.append("frontier CLI")
    if not docker:
        missing.append("docker")
    if not harbor:
        # Frontier-CS falls back to `uvx harbor` when harbor is not on PATH.
        if which("uvx"):
            notes.append("harbor not on PATH; will fall back to `uvx harbor`")
        else:
            missing.append("harbor (or uvx to run it)")
    if not env.get("OPENAI_API_KEY"):
        notes.append("OPENAI_API_KEY unset; arms served by OpenAI will fail")
    return Probe(available=not missing, frontier=frontier, harbor=harbor,
                 docker=docker, missing=missing, notes=notes)


# --------------------------------------------------------------------------
# running
# --------------------------------------------------------------------------
def build_command(task: HarborTask, *, frontier: str = "frontier") -> list[str]:
    """The exact Frontier-CS invocation, kept in one place so it is auditable."""
    # Re-check at the external-process boundary: HarborTask is mutable after
    # construction, and a mutated task must not reach ``frontier harbor``.
    _assert_task_target_allowed(task)
    return [frontier, "harbor", "trial", task.track, task.problem,
            "-a", task.agent, "-m", task.model, "--json"]


def parse_trial_json(payload: dict[str, Any], task: HarborTask, trial: int,
                     *, wall_seconds: float) -> TrialResult:
    """Map a Harbor trial payload onto the harness's TrialResult.

    Reusing TrialResult is deliberate: `report.summarise_task` is duck-typed, so
    Harbor results flow through the same summary, Wilson interval, regression
    and comparison code as internal ones. A parallel reporting path would drift.
    """
    status = str(payload.get("trial_status") or "completed")
    raw = payload.get("score")
    unbounded = payload.get("score_unbounded")

    # An infrastructure failure is not a capability measurement. Score it None
    # -> 0.0 but mark it so `passed` is False and the reason is legible; the
    # caller can filter these out rather than average them into a capability
    # number.
    infra = status in INFRA_STATUSES
    score = 0.0 if raw is None else float(raw) / SCORE_SCALE

    usage = {
        "input_tokens": int(payload.get("n_input_tokens") or 0),
        "cache_tokens": int(payload.get("n_cache_tokens") or 0),
        "output_tokens": int(payload.get("n_output_tokens") or 0),
    }

    detail = (f"score={raw} unbounded={unbounded} status={status} "
              f"cost_usd={payload.get('cost_usd')} "
              f"successful_submissions={payload.get('successful_submissions')}")
    verdicts = [graders_module.Verdict(
        grader="frontier_cs_verifier",
        passed=(not infra) and score > 0.0,
        detail=detail,
        critical=True)]
    if infra:
        verdicts.append(graders_module.Verdict(
            grader="infrastructure",
            passed=False,
            detail=f"{status}: infrastructure outcome, not evidence about the "
                   "arm's capability (AGENTS.md rule 5)",
            critical=False))

    return TrialResult(
        task_id=task.id, trial=trial,
        passed=(not infra) and score > 0.0,
        score=round(score, 6),
        stop_reason="completed" if status in ("completed", "success") else status,
        steps=int(payload.get("successful_submissions") or 0),
        wall_seconds=round(wall_seconds, 3),
        usage=usage, denials=0, verdicts=verdicts,
        final_text=json.dumps(payload, sort_keys=True),
        error=None if not infra else status)


def run_trial(task: HarborTask, trial: int, *, probe_result: Probe | None = None,
              runner: Callable[..., subprocess.CompletedProcess] | None = None
              ) -> TrialResult:
    """Run one Frontier-CS trial. Failures are recorded, never swallowed."""
    _assert_task_target_allowed(task)
    detected = probe_result or probe()
    detected.require()
    runner = runner or subprocess.run

    command = build_command(task, frontier=detected.frontier or "frontier")
    started = time.monotonic()
    try:
        completed = runner(command, capture_output=True, text=True,
                           timeout=task.timeout_seconds)
    except subprocess.TimeoutExpired:
        return TrialResult(
            task_id=task.id, trial=trial, passed=False, score=0.0,
            stop_reason="harness_timeout", steps=0,
            wall_seconds=round(time.monotonic() - started, 3),
            error=f"frontier trial exceeded {task.timeout_seconds}s")
    wall = time.monotonic() - started

    if completed.returncode != 0:
        return TrialResult(
            task_id=task.id, trial=trial, passed=False, score=0.0,
            stop_reason="frontier_error", steps=0, wall_seconds=round(wall, 3),
            error=f"exit {completed.returncode}: "
                  f"{(completed.stderr or '').strip()[:500]}")

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return TrialResult(
            task_id=task.id, trial=trial, passed=False, score=0.0,
            stop_reason="unparsable_output", steps=0, wall_seconds=round(wall, 3),
            error=f"frontier --json did not emit JSON: {exc}")

    return parse_trial_json(payload, task, trial, wall_seconds=wall)


def run_suite(suite: HarborSuite, *, trials: int = 1,
              probe_result: Probe | None = None,
              runner: Callable[..., subprocess.CompletedProcess] | None = None,
              progress: Callable[[TrialResult], None] | None = None
              ) -> tuple[report_module.RunSummary, list[TrialResult]]:
    detected = probe_result or probe()
    detected.require()

    all_trials: list[TrialResult] = []
    summaries: list[report_module.TaskSummary] = []
    for task in suite.tasks:
        results = []
        for index in range(trials):
            result = run_trial(task, index, probe_result=detected, runner=runner)
            results.append(result)
            all_trials.append(result)
            if progress:
                progress(result)
        # `kind` is the track, so the report groups by Frontier-CS track the way
        # it groups internal tasks by capability/protocol/discipline.
        summaries.append(report_module.summarise_task(task.id, task.track, results))

    arm = ",".join(sorted({f"{t.agent}:{t.model}" for t in suite.tasks})) or "none"
    return (report_module.RunSummary(f"frontier-cs::{suite.name}", arm, summaries),
            all_trials)
