"""Run one dispatched task under the `api_direct` runtime.

This is the piece that lets a role execute outside Claude Code and Codex: the
same role contract, the same handoff, the same strict policy resolution, driven
by whichever inference API `model-bindings.yaml` points at.

What it refuses to do matters as much as what it does:

  * a role whose capabilities this runtime cannot provide is refused, not run
    with a quietly reduced tool surface;
  * writes outside the task's declared `write_scope` are denied by the tools;
  * an exhausted budget is reported as an exhausted budget, never as a result;
  * the receipt records the resolution, the journal, and any disagreement
    between the model we resolved and the model that answered.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml

from .. import role_registry
from ..adapter import config as config_module
from ..adapter import manifest as manifest_module
from ..adapter import resolver as resolver_module
from . import graph as graph_module
from .tools import TaskScope, ToolJournal, build_tools

RUNTIME = "api_direct"
REPO = role_registry.REPO


class UnsupportedRole(RuntimeError):
    """This runtime cannot provide every capability the role's contract needs."""


@dataclass
class TaskRun:
    task_id: str
    role: str
    stop_reason: str
    steps: int
    final_text: str
    resolution: Any
    usage: dict[str, int] = field(default_factory=dict)
    journal: list[dict[str, Any]] = field(default_factory=list)
    transcript: list[dict[str, Any]] = field(default_factory=list)
    model_disagreements: list[str] = field(default_factory=list)
    wall_seconds: float = 0.0

    @property
    def completed(self) -> bool:
        return self.stop_reason == graph_module.COMPLETED

    @property
    def files_written(self) -> list[str]:
        return [e["path"] for e in self.journal
                if e["tool"] in ("write_file", "edit_file") and "denied" not in e]


# --------------------------------------------------------------------------
def load_task(source: str | Path | dict[str, Any]) -> dict[str, Any]:
    """Accept a ledger handoff record, a dispatch-queue task, or either path."""
    if isinstance(source, (str, Path)):
        text = Path(source).read_text(encoding="utf-8")
        source = (json.loads(text) if str(source).endswith(".json")
                  else yaml.safe_load(text))
    if not isinstance(source, dict):
        raise ValueError("task source must be a mapping")
    if "handoff" in source and "id" in source:      # dispatch-queue task
        return source
    if "handoff" in source:                          # ledger handoff record
        body = source["handoff"]
        return {"id": body.get("id"), "role": body.get("to"), "handoff": body}
    return {"id": source.get("id"), "role": source.get("to"), "handoff": source}


def task_scope(task: dict[str, Any], *, repo_root: Path,
               api_config: dict[str, Any]) -> TaskScope:
    handoff = task["handoff"]
    write_scope = list(task.get("write_scope") or [])
    if not write_scope:
        # A ledger handoff names artifact paths rather than a scope; the
        # directories holding them are the narrowest scope that still lets the
        # task produce its declared deliverables.
        write_scope = sorted({str(Path(p).parent)
                              for p in (handoff.get("artifact_paths") or [])})
    return TaskScope(
        repo_root=repo_root,
        task_id=str(task.get("id") or "TASK-UNKNOWN"),
        read_scope=tuple(task.get("read_scope") or ()),
        write_scope=tuple(write_scope),
        allowed_commands=tuple(api_config.get("command_allowlist") or ()),
        command_timeout_seconds=int(api_config.get("command_timeout_seconds", 300)),
    )


def system_prompt(role: str, roles_doc: dict[str, Any], *,
                  repo_root: Path = REPO) -> str:
    """The role's own contract, assembled from the runtime-neutral sources."""
    spec = role_registry.role_spec(roles_doc, role)
    parts = []
    for name in ("AGENTS.md", spec["contract"]):
        path = repo_root / name
        if not path.exists():
            raise FileNotFoundError(f"missing role contract: {path}")
        parts.append(path.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(parts)


def task_brief(task: dict[str, Any], scope: TaskScope, tool_names: list[str]) -> str:
    """The task envelope, including the limits the tools will actually enforce."""
    handoff = task["handoff"]
    budget = handoff.get("budget") or {}

    def block(label: str, values: Any) -> str:
        if not values:
            return f"{label}: none stated"
        if isinstance(values, str):
            return f"{label}: {values}"
        return label + ":\n" + "\n".join(f"  - {v}" for v in values)

    return "\n\n".join([
        f"TASK {scope.task_id} — role: {task.get('role')}",
        block("Objective", handoff.get("objective")),
        block("Uncertainty to reduce", handoff.get("uncertainty_reduced")),
        block("Inputs", handoff.get("inputs")),
        block("Constraints", handoff.get("constraints")),
        block("Deliverables", handoff.get("deliverables")),
        block("Artifact paths you must produce", handoff.get("artifact_paths")),
        block("Completion gate", handoff.get("completion_gate")),
        block("Writable paths (enforced; writes elsewhere are denied)",
              list(scope.write_scope)),
        block("Readable paths (enforced)",
              list(scope.read_scope) or ["the whole repository"]),
        block("Tools available", tool_names),
        block("Commands you may run", list(scope.allowed_commands)),
        f"Budget: wall_clock_seconds={budget.get('wall_clock_seconds')}, "
        f"maximum_runs={budget.get('maximum_runs')}",
        "Write your deliverables with the file tools before finishing. "
        "Existing files cannot be overwritten — artifacts are immutable, so a "
        "correction is a new path. When you are done, reply with a short "
        "summary naming the paths you wrote; do not restate their contents.",
    ])


# --------------------------------------------------------------------------
def run_task(source: str | Path | dict[str, Any], *,
             config: config_module.Config | None = None,
             backend: str | None = None,
             repo_root: Path = REPO,
             checkpoint_path: str | Path | None = None,
             max_steps: int | None = None,
             model_factory: Callable[..., Any] | None = None,
             opener: Callable[..., Any] | None = None,
             clock: Callable[[], float] = time.monotonic) -> TaskRun:
    task = load_task(source)
    role = task.get("role")
    if not role:
        raise ValueError("task names no role")

    roles_doc = role_registry.load_roles()
    tool_names = role_registry.expected_tools(roles_doc, role, RUNTIME)
    if tool_names is None:
        missing = role_registry.missing_capabilities(roles_doc, role, RUNTIME)
        raise UnsupportedRole(
            f"the {RUNTIME} runtime cannot provide {', '.join(missing)}, which "
            f"role {role!r} requires. Run this task under a runtime that can "
            f"(see orchestration/roles.yaml) rather than with a reduced tool "
            f"surface.")

    config = config or config_module.load()
    resolution = resolver_module.resolve_handoff(config, task["handoff"],
                                                 backend=backend)

    api_config = roles_doc.get(RUNTIME) or {}
    scope = task_scope(task, repo_root=repo_root, api_config=api_config)
    journal = ToolJournal()
    tools = build_tools(scope, journal, tool_names)

    if model_factory is None:
        from ..adapter.langchain_model import ResolvedChatModel
        model = ResolvedChatModel(adapter_config=config, resolution=resolution,
                                  opener=opener)
    else:
        model = model_factory(config=config, resolution=resolution)

    budget = (task["handoff"].get("budget") or {})
    wall_clock = budget.get("wall_clock_seconds")
    started = clock()
    deadline = started + float(wall_clock) if wall_clock else None
    steps_limit = max_steps or int(api_config.get("max_steps", 40))

    checkpointer, closeable = graph_module.open_checkpointer(checkpoint_path)
    try:
        agent = graph_module.build_agent(
            model, tools, max_steps=steps_limit, deadline=deadline,
            checkpointer=checkpointer, clock=clock)
        from langchain_core.messages import HumanMessage, SystemMessage
        initial = {
            "messages": [SystemMessage(system_prompt(role, roles_doc,
                                                     repo_root=repo_root)),
                         HumanMessage(task_brief(task, scope, tool_names))],
            "steps": 0,
            "stop_reason": None,
        }
        state = agent.invoke(
            initial,
            config={"configurable": {"thread_id": scope.task_id},
                    "recursion_limit": steps_limit * 2 + 8})
    finally:
        if closeable is not None:
            closeable.close()

    messages = state.get("messages", [])
    final_text = ""
    for message in reversed(messages):
        if getattr(message, "type", "") == "ai" and message.content:
            final_text = message.content if isinstance(message.content, str) else str(
                message.content)
            break

    return TaskRun(
        task_id=scope.task_id,
        role=role,
        stop_reason=graph_module.final_stop_reason(state),
        steps=state.get("steps", 0),
        final_text=final_text,
        resolution=resolution,
        usage=model.usage_totals() if hasattr(model, "usage_totals") else {},
        journal=journal.entries,
        transcript=[_serialise(m) for m in messages],
        model_disagreements=(model.model_disagreements()
                             if hasattr(model, "model_disagreements") else []),
        wall_seconds=round(clock() - started, 3),
    )


def _serialise(message: Any) -> dict[str, Any]:
    content = message.content
    return {
        "type": getattr(message, "type", message.__class__.__name__),
        "content": content if isinstance(content, str) else str(content),
        "tool_calls": [{"name": c.get("name"), "args": c.get("args"),
                        "id": c.get("id")}
                       for c in (getattr(message, "tool_calls", None) or [])],
        "tool_call_id": getattr(message, "tool_call_id", None),
    }


def write_artifacts(run: TaskRun, out_dir: str | Path, *,
                    config: config_module.Config | None = None) -> dict[str, Path]:
    """Write the immutable record of an agent run.

    A run that stopped on budget still gets a full record: the point is that a
    reader can tell the difference without re-running anything.
    """
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}

    transcript = directory / "transcript.jsonl"
    if transcript.exists():
        raise FileExistsError(
            f"{transcript} already exists; agent run records are immutable")
    transcript.write_text(
        "".join(json.dumps(entry, default=str) + "\n" for entry in run.transcript),
        encoding="utf-8")
    written["transcript"] = transcript

    receipt = manifest_module.receipt(run.resolution, task_id=run.task_id,
                                      role=run.role, config=config)
    receipt["inference_receipt"]["runtime"] = RUNTIME
    receipt["inference_receipt"]["execution"] = {
        "stop_reason": run.stop_reason,
        "completed": run.completed,
        "steps": run.steps,
        "wall_seconds": run.wall_seconds,
        "usage": run.usage,
        "files_written": run.files_written,
        "denied_tool_calls": [e for e in run.journal if "denied" in e],
        "model_disagreements": run.model_disagreements,
    }
    written["receipt"] = manifest_module.write_receipt(
        directory / "inference-receipt.json", receipt)

    journal = directory / "tool-journal.json"
    if journal.exists():
        raise FileExistsError(f"{journal} already exists; run records are immutable")
    journal.write_text(json.dumps(run.journal, indent=2, default=str) + "\n",
                       encoding="utf-8")
    written["journal"] = journal
    return written
