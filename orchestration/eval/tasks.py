"""Eval task definitions and the sandbox each trial runs in.

Every trial gets a fresh sandbox: a throwaway directory holding the role
contract, the harness, and the task's fixtures. The agent under test never sees
the real repository, so an eval can never write into `ledger/`, `experiments/`,
or `knowledge/`. Measuring a research harness must not itself become an input
to the research.

Fixtures are generated from seeds, so a task with a verifiable answer has one
this file knows and the agent must derive.
"""
from __future__ import annotations

import json
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
WORK_DIR = "work"


@dataclass
class EvalTask:
    id: str
    kind: str                      # capability | protocol | discipline
    role: str
    summary: str
    handoff: dict[str, Any]
    graders: list[dict[str, Any]]
    fixtures: list[dict[str, Any]] = field(default_factory=list)
    max_steps: int | None = None
    tags: list[str] = field(default_factory=list)
    # `dev` is what you tune against; `held_out` is what says whether the
    # tuning generalised. Tuning against held_out spends the only unbiased
    # measurement you have.
    split: str = "dev"

    @property
    def policy(self) -> str | None:
        return (self.handoff.get("inference") or {}).get("policy")


@dataclass
class Suite:
    name: str
    description: str
    tasks: list[EvalTask]

    def filter(self, kinds: list[str] | None = None,
               ids: list[str] | None = None,
               splits: list[str] | None = None) -> "Suite":
        tasks = [t for t in self.tasks
                 if (not kinds or t.kind in kinds)
                 and (not ids or t.id in ids)
                 and (not splits or t.split in splits)]
        return Suite(self.name, self.description, tasks)


def load_suite(path: str | Path) -> Suite:
    document = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    suite = document["suite"]
    tasks = []
    for entry in suite["tasks"]:
        tasks.append(EvalTask(
            id=entry["id"], kind=entry["kind"], role=entry["role"],
            summary=entry.get("summary", ""),
            handoff=entry["handoff"], graders=entry["graders"],
            fixtures=entry.get("fixtures") or [],
            max_steps=entry.get("max_steps"),
            tags=entry.get("tags") or [],
            split=entry.get("split", "dev")))
    _validate(tasks)
    return Suite(suite["name"], suite.get("description", ""), tasks)


def _validate(tasks: list[EvalTask]) -> None:
    from .graders import REGISTRY
    seen: set[str] = set()
    for task in tasks:
        if task.id in seen:
            raise ValueError(f"duplicate eval task id {task.id}")
        seen.add(task.id)
        if task.kind not in ("capability", "protocol", "discipline"):
            raise ValueError(f"{task.id}: unknown kind {task.kind!r}")
        if task.split not in ("dev", "held_out"):
            raise ValueError(f"{task.id}: unknown split {task.split!r}")
        if not task.graders:
            raise ValueError(f"{task.id}: a task with no graders cannot be scored")
        for spec in task.graders:
            if spec["type"] not in REGISTRY:
                raise ValueError(f"{task.id}: unknown grader {spec['type']!r}")
        budget = task.handoff.get("budget") or {}
        if not budget.get("wall_clock_seconds"):
            raise ValueError(f"{task.id}: handoff has no wall_clock_seconds budget")


# --------------------------------------------------------------------------
# fixtures
# --------------------------------------------------------------------------
def _fixture_ecdlp_instance(sandbox: Path, spec: dict[str, Any],
                            seed_offset: int = 0) -> dict[str, Any]:
    """Write a toy ECDLP instance, withholding the scalar the agent must find.

    `seed_offset` rotates the instance without changing the task. A suite whose
    fixtures never move eventually measures familiarity with those fixtures
    rather than the ability that produced the first score.
    """
    sys.path.insert(0, str(REPO))
    from harness.toycurve import generate_instance

    instance = generate_instance(seed=int(spec["seed"]) + seed_offset,
                                 field_bits=int(spec["field_bits"]))
    public = {"p": instance.p, "a": instance.a, "b": instance.b,
              "P": list(instance.P), "Q": list(instance.Q), "n": instance.n,
              "field_bits": int(spec["field_bits"])}
    target = sandbox / spec.get("path", f"{WORK_DIR}/instance.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(public, indent=2) + "\n", encoding="utf-8")
    # The answer stays out of the sandbox; the grader recomputes it anyway.
    return {"withheld_k": instance.k}


def _fixture_file(sandbox: Path, spec: dict[str, Any],
                  seed_offset: int = 0) -> dict[str, Any]:
    target = sandbox / spec["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    content = spec.get("content", "")
    if isinstance(content, (dict, list)):
        content = (json.dumps(content, indent=2) if str(spec["path"]).endswith(".json")
                   else yaml.safe_dump(content, sort_keys=False))
    target.write_text(content, encoding="utf-8")
    return {}


FIXTURES = {"ecdlp_instance": _fixture_ecdlp_instance, "file": _fixture_file}


def build_sandbox(task: EvalTask, root: Path, *, repo: Path = REPO,
                  seed_offset: int = 0) -> tuple[Path, dict[str, Any]]:
    """Create the throwaway repository this trial runs against."""
    sandbox = Path(root)
    sandbox.mkdir(parents=True, exist_ok=True)
    (sandbox / WORK_DIR).mkdir(exist_ok=True)

    shutil.copy2(repo / "AGENTS.md", sandbox / "AGENTS.md")
    (sandbox / "agents").mkdir(exist_ok=True)
    shutil.copy2(repo / "agents" / f"{task.role}.md",
                 sandbox / "agents" / f"{task.role}.md")
    # The harness travels with the sandbox so a task may legitimately import
    # and run it; the eval measures using it, not reimplementing it.
    shutil.copytree(repo / "harness", sandbox / "harness",
                    ignore=shutil.ignore_patterns("__pycache__"))

    secrets: dict[str, Any] = {}
    for spec in task.fixtures:
        kind = spec["type"]
        if kind not in FIXTURES:
            raise KeyError(f"unknown fixture {kind!r}")
        secrets.update(FIXTURES[kind](sandbox, spec, seed_offset))
    return sandbox, secrets


def sandbox_task(task: EvalTask, sandbox: Path) -> dict[str, Any]:
    """The dispatch-queue shape the agent runner consumes."""
    handoff = dict(task.handoff)
    handoff.setdefault("id", task.id)
    handoff.setdefault("to", task.role)
    handoff.setdefault("from", "eval-harness")
    return {
        "id": task.id,
        "role": task.role,
        "handoff": handoff,
        "read_scope": [],                       # the sandbox is the whole world
        "write_scope": handoff.get("write_scope") or [WORK_DIR],
    }
