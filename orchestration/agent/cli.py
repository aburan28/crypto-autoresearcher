"""Command line for the `api_direct` runtime.

    python -m orchestration.agent plan --task ledger/handoffs/TASK-....yaml
    python -m orchestration.agent run  --task ... --out coordination/.../agent

`plan` performs the full resolution and scope derivation without contacting a
backend, so what a task is permitted to do can be reviewed before it runs.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .. import role_registry
from ..adapter import config as config_module
from ..adapter import resolver as resolver_module
from . import runner as runner_module
from .tools import TaskScope, ToolJournal, build_tools


def _prepare(args: argparse.Namespace):
    task = runner_module.load_task(args.task)
    role = task.get("role")
    if not role:
        raise SystemExit("task names no role")
    roles_doc = role_registry.load_roles()
    tool_names = role_registry.expected_tools(roles_doc, role, runner_module.RUNTIME)
    cfg = config_module.load()
    scope = runner_module.task_scope(
        task, repo_root=runner_module.REPO,
        api_config=roles_doc.get(runner_module.RUNTIME) or {})
    return task, role, roles_doc, tool_names, cfg, scope


def cmd_plan(args: argparse.Namespace) -> int:
    task, role, roles_doc, tool_names, cfg, scope = _prepare(args)
    print(f"task:    {scope.task_id}")
    print(f"role:    {role}")
    if tool_names is None:
        missing = role_registry.missing_capabilities(
            roles_doc, role, runner_module.RUNTIME)
        print(f"REFUSED: this runtime cannot provide {', '.join(missing)}")
        return 1

    resolution = resolver_module.resolve_handoff(cfg, task["handoff"],
                                                 backend=args.backend)
    print(f"model:   {resolution.summary()}")
    print(f"tools:   {', '.join(tool_names)}")
    print(f"commands:{' ' + ', '.join(scope.allowed_commands) if scope.allowed_commands else ' none'}")
    print(f"write:   {', '.join(scope.write_scope) or 'NOTHING — the task declares no write scope'}")
    print(f"read:    {', '.join(scope.read_scope) or 'the whole repository'}")
    prompt = runner_module.system_prompt(role, roles_doc)
    brief = runner_module.task_brief(task, scope, tool_names)
    print(f"prompt:  {len(prompt)} characters of role contract, "
          f"{len(brief)} of task brief")
    if args.show_prompt:
        print("\n--- system ---\n" + prompt + "\n--- task ---\n" + brief)
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    run = runner_module.run_task(
        args.task, backend=args.backend, checkpoint_path=args.checkpoint,
        max_steps=args.max_steps)
    print(f"# {run.resolution.summary()}", file=sys.stderr)
    print(f"# stop_reason={run.stop_reason} steps={run.steps} "
          f"wall={run.wall_seconds}s usage={run.usage}", file=sys.stderr)
    if run.files_written:
        print(f"# wrote: {', '.join(run.files_written)}", file=sys.stderr)
    for denial in (e for e in run.journal if "denied" in e):
        print(f"# DENIED {denial['tool']}: {denial['denied']}", file=sys.stderr)
    if run.model_disagreements:
        print(f"# WARNING: backend answered as "
              f"{', '.join(run.model_disagreements)}, not the resolved "
              f"{run.resolution.resolved_model_id}", file=sys.stderr)
    print(run.final_text)
    if args.out:
        written = runner_module.write_artifacts(run, args.out)
        for label, path in written.items():
            print(f"# {label}: {path}", file=sys.stderr)
    return 0 if run.completed else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m orchestration.agent",
        description="Execute a dispatched task under the api_direct runtime.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_plan = sub.add_parser("plan", help="resolve and show limits without running")
    p_plan.add_argument("--task", required=True)
    p_plan.add_argument("--backend")
    p_plan.add_argument("--show-prompt", action="store_true")
    p_plan.set_defaults(func=cmd_plan)

    p_run = sub.add_parser("run", help="run the task")
    p_run.add_argument("--task", required=True)
    p_run.add_argument("--backend")
    p_run.add_argument("--out", help="directory for transcript, receipt, journal")
    p_run.add_argument("--checkpoint", help="sqlite path; enables resuming")
    p_run.add_argument("--max-steps", type=int)
    p_run.set_defaults(func=cmd_run)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (config_module.ConfigError, resolver_module.ResolutionError,
            runner_module.UnsupportedRole, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
