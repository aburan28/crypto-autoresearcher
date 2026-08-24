"""Command line for the inference adapter.

    python -m orchestration.adapter resolve  --policy research-deep
    python -m orchestration.adapter matrix
    python -m orchestration.adapter env      --runtime claude_code --backend zai-anthropic
    python -m orchestration.adapter doctor   --probe
    python -m orchestration.adapter models   --backend zai
    python -m orchestration.adapter complete --policy research-deep --prompt-file q.md
    python -m orchestration.adapter probe-codex-session --help

`resolve`, `matrix`, `env`, and offline `doctor` touch no network.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from pathlib import Path
from typing import Any

from . import config as config_module
from . import codex_runtime as codex_runtime_module
from . import manifest as manifest_module
from . import resolver as resolve_module
from . import transport as transport_module


def _load(args: argparse.Namespace) -> config_module.Config:
    return config_module.load(
        policies_path=Path(args.policies) if args.policies else None,
        providers_path=Path(args.providers) if args.providers else None,
        bindings_path=Path(args.bindings) if args.bindings else None)


def _resolve(cfg: config_module.Config, args: argparse.Namespace
             ) -> resolve_module.Resolution:
    policy = args.policy
    if getattr(args, "role", None) and not policy:
        policy = cfg.role_default_policy(args.role)
    if not policy:
        raise SystemExit("one of --policy or --role is required")
    return resolve_module.resolve(
        cfg, policy,
        backend=args.backend,
        fallback_allowed=args.allow_fallback,
        degraded_allowed=args.allow_degraded,
        independent_session=args.independent_session,
        originating_agent=getattr(args, "originating_agent", None),
        assigned_agent=getattr(args, "assigned_agent", None))


# --------------------------------------------------------------------------
def cmd_resolve(args: argparse.Namespace) -> int:
    cfg = _load(args)
    resolution = _resolve(cfg, args)
    if args.json:
        print(json.dumps(resolution.to_dict(), indent=2, sort_keys=True))
    else:
        print(resolution.summary())
        for attempt in resolution.rejected_attempts:
            print(f"  rejected {attempt.policy} @ {attempt.backend}: "
                  f"{'; '.join(attempt.reasons)}")
    if args.receipt:
        data = manifest_module.receipt(resolution, task_id=args.task_id,
                                       role=getattr(args, "role", None), config=cfg)
        print(f"receipt: {manifest_module.write_receipt(args.receipt, data)}",
              file=sys.stderr)
    return 0


def cmd_matrix(args: argparse.Namespace) -> int:
    """Which policies each backend can actually serve, and why not."""
    cfg = _load(args)
    backends = [args.backend] if args.backend else sorted(cfg.binding_table)
    width = max(len(p) for p in cfg.policy_table) + 2
    for backend in backends:
        print(f"\n{backend}  ({cfg.backend(backend).get('display_name', '')})")
        for policy_id in cfg.policy_table:
            binding = cfg.binding(backend, policy_id)
            reasons = resolve_module._binding_blockers(cfg, policy_id, backend, binding)
            if not reasons:
                mark = "OK  "
                detail = f"{binding['model']}  [{binding.get('provenance')}]"
            elif binding and binding.get("model"):
                mark = "DEGR"
                detail = f"{binding['model']}  needs: {'; '.join(reasons)}"
            else:
                mark = "--  "
                detail = "; ".join(reasons)
            print(f"  {mark} {policy_id:<{width}} {detail}")
    print("\nOK = serves the policy as written · DEGR = only with a recorded "
          "downgrade · -- = unusable")
    return 0


def cmd_env(args: argparse.Namespace) -> int:
    """Emit the environment that points a CLI runtime at a backend."""
    cfg = _load(args)
    runtime_name = args.runtime or cfg.default_runtime()
    runtime = cfg.runtime(runtime_name)
    backend_name = args.backend or cfg.default_backend()
    compatible = runtime.get("compatible_backends") or []
    if compatible and backend_name not in compatible:
        raise SystemExit(
            f"runtime {runtime_name} speaks {runtime.get('wire')}; backend "
            f"{backend_name} speaks {cfg.backend(backend_name)['wire']}. "
            f"Compatible backends: {', '.join(compatible)}")
    resolution = _resolve(cfg, argparse.Namespace(**{**vars(args),
                                                     "backend": backend_name}))
    env_map = runtime.get("env") or {}
    if not env_map:
        raise SystemExit(
            f"runtime {runtime_name} takes no environment configuration "
            f"(tool_loop={runtime.get('tool_loop')}); use `complete` instead")

    api_key = os.environ.get(resolution.api_key_env, "")
    exports = []
    if env_map.get("base_url"):
        exports.append((env_map["base_url"], resolution.base_url))
    if env_map.get("api_key"):
        exports.append((env_map["api_key"],
                        api_key or f"<set ${resolution.api_key_env}>"))
    if env_map.get("model"):
        exports.append((env_map["model"], resolution.resolved_model_id))
    exports.append(("AUTORESEARCH_BACKEND", resolution.backend))
    exports.append(("AUTORESEARCH_POLICY", resolution.requested_policy))

    for name, value in exports:
        print(f"export {name}={shlex.quote(str(value))}")
    print(f"# {resolution.summary()}", file=sys.stderr)
    if not api_key:
        print(f"# WARNING: ${resolution.api_key_env} is unset in this shell",
              file=sys.stderr)
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    """Config validity, credential presence, and (optionally) live model ids."""
    problems: list[str] = []
    try:
        cfg = _load(args)
    except config_module.ConfigError as exc:
        print(f"FAIL  configuration: {exc}")
        return 1
    print(f"OK    configuration loaded ({cfg.digest})")
    for name, path in cfg.paths.items():
        print(f"      {name}: {path}")

    backends = [args.backend] if args.backend else sorted(cfg.backend_table)
    for backend_name in backends:
        backend = cfg.backend(backend_name)
        key_env = backend["api_key_env"]
        has_key = bool(os.environ.get(key_env))
        if has_key or backend.get("api_key_optional"):
            print(f"OK    {backend_name}: credentials in ${key_env}"
                  if has_key else
                  f"OK    {backend_name}: no credentials required")
        else:
            print(f"WARN  {backend_name}: ${key_env} unset (backend unusable)")

        unverified = [p for p, b in (cfg.binding_table.get(backend_name) or {}).items()
                      if b.get("model") and b.get("provenance") == "operator-supplied"
                      and not b.get("last_probed")]
        if unverified:
            print(f"WARN  {backend_name}: unverified model ids for "
                  f"{', '.join(unverified)} — run with --probe")

        if args.probe and (has_key or backend.get("api_key_optional")):
            try:
                served = transport_module.list_models(cfg, backend_name)
            except transport_module.TransportError as exc:
                print(f"WARN  {backend_name}: model probe failed: {exc}")
                continue
            configured = {b.get("model") for b in
                          (cfg.binding_table.get(backend_name) or {}).values()
                          if b.get("model")}
            for model in sorted(configured):
                if model in served:
                    print(f"OK    {backend_name}: serves {model}")
                else:
                    problems.append(f"{backend_name} does not serve {model}")
                    print(f"FAIL  {backend_name}: {model} not in the served list "
                          f"({len(served)} models); closest: "
                          f"{', '.join(_closest(model, served))}")
    if problems:
        print(f"\n{len(problems)} configured model id(s) are not served as written.")
        return 1
    return 0


def _closest(model: str, served: list[str], limit: int = 3) -> list[str]:
    import difflib
    return difflib.get_close_matches(model, served, n=limit, cutoff=0.3) or ["none"]


def cmd_models(args: argparse.Namespace) -> int:
    cfg = _load(args)
    backend = args.backend or cfg.default_backend()
    for model in transport_module.list_models(cfg, backend):
        print(model)
    return 0


def cmd_complete(args: argparse.Namespace) -> int:
    cfg = _load(args)
    resolution = _resolve(cfg, args)
    prompt = (Path(args.prompt_file).read_text(encoding="utf-8")
              if args.prompt_file else sys.stdin.read())
    system = Path(args.system_file).read_text(encoding="utf-8") if args.system_file else None
    if args.role and not system:
        system = _role_contract(cfg, args.role)
    print(f"# {resolution.summary()}", file=sys.stderr)
    completion = transport_module.complete(
        cfg, resolution, system=system,
        messages=[transport_module.Message("user", prompt)],
        max_tokens=args.max_tokens)
    print(completion.text)
    if completion.model and completion.model != resolution.resolved_model_id:
        print(f"# WARNING: backend answered as {completion.model!r}, not the "
              f"resolved {resolution.resolved_model_id!r}", file=sys.stderr)
    if args.receipt:
        data = manifest_module.receipt(resolution, completion, task_id=args.task_id,
                                       role=args.role, config=cfg)
        print(f"# receipt: {manifest_module.write_receipt(args.receipt, data)}",
              file=sys.stderr)
    return 0


def cmd_probe_codex_session(args: argparse.Namespace) -> int:
    """Verify one new Codex exec session; never verify a backend catalog."""
    cfg = _load(args)
    try:
        codex_runtime_module.probe_codex_session(
            cfg=cfg,
            codex_bin=args.codex_bin,
            state_db=args.state_db,
            workdir=args.workdir,
            model=args.model,
            effort=args.effort,
            policy=args.policy,
            role=args.role,
            task_id=args.task_id,
            receipt=args.receipt,
            independent_session=args.independent_session,
            timeout_seconds=args.timeout_seconds,
            backend=args.backend,
        )
    except codex_runtime_module.CodexRuntimeProbeError as exc:
        suffix = f"; receipt={exc.receipt}" if exc.receipt_written else ""
        print(f"codex session probe failed: {', '.join(exc.codes)}{suffix}",
              file=sys.stderr)
        return 3
    print(f"verified exact Codex session; receipt={args.receipt}")
    return 0


def _role_contract(cfg: config_module.Config, role: str) -> str:
    """Assemble a system prompt from the runtime-neutral role contracts."""
    parts = []
    for name in ("AGENTS.md", f"agents/{role}.md"):
        path = config_module.REPO_ROOT / name
        if not path.exists():
            raise SystemExit(f"no role contract at {path}")
        parts.append(path.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(parts)


# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m orchestration.adapter",
        description="Resolve inference policies to backends and models.")
    parser.add_argument("--policies"), parser.add_argument("--providers")
    parser.add_argument("--bindings")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_selection(p: argparse.ArgumentParser) -> None:
        p.add_argument("--policy", help="policy id or legacy alias")
        p.add_argument("--role", help="resolve this role's default policy")
        p.add_argument("--backend", help="override the default backend")
        p.add_argument("--allow-fallback", action="store_true",
                       help="permit the declared fallback policy or another backend")
        p.add_argument("--allow-degraded", action="store_true",
                       help="permit a recorded downgrade (needs an inference amendment)")
        p.add_argument("--independent-session", action="store_true",
                       help="assert this runs in a session that did not originate the claim")
        p.add_argument("--originating-agent")
        p.add_argument("--assigned-agent")
        p.add_argument("--task-id")
        p.add_argument("--receipt", help="write an inference receipt to this path")

    p_resolve = sub.add_parser("resolve", help="resolve one policy")
    add_selection(p_resolve)
    p_resolve.add_argument("--json", action="store_true")
    p_resolve.set_defaults(func=cmd_resolve)

    p_matrix = sub.add_parser("matrix", help="policy x backend coverage")
    p_matrix.add_argument("--backend")
    p_matrix.set_defaults(func=cmd_matrix)

    p_env = sub.add_parser("env", help="emit shell exports for a CLI runtime")
    add_selection(p_env)
    p_env.add_argument("--runtime", help="claude_code | codex_cli | ...")
    p_env.set_defaults(func=cmd_env)

    p_doctor = sub.add_parser("doctor", help="validate config and credentials")
    p_doctor.add_argument("--backend")
    p_doctor.add_argument("--probe", action="store_true",
                          help="ask each backend whether it serves the configured ids")
    p_doctor.set_defaults(func=cmd_doctor)

    p_models = sub.add_parser("models", help="list models a backend serves")
    p_models.add_argument("--backend")
    p_models.set_defaults(func=cmd_models)

    p_complete = sub.add_parser("complete", help="single-turn completion")
    add_selection(p_complete)
    p_complete.add_argument("--prompt-file")
    p_complete.add_argument("--system-file")
    p_complete.add_argument("--max-tokens", type=int)
    p_complete.set_defaults(func=cmd_complete)

    p_codex = sub.add_parser(
        "probe-codex-session",
        help="verify one exact new Codex CLI session (not a backend catalog)",
        description=(
            "Create and verify one non-ephemeral read-only Codex exec session. "
            "The immutable receipt applies only to that session ID; it does "
            "not verify a backend catalog or mutate model bindings."))
    p_codex.add_argument("--codex-bin", required=True,
                         help="existing Codex executable path")
    p_codex.add_argument("--state-db", required=True,
                         help="existing Codex SQLite state DB (queried read-only)")
    p_codex.add_argument("--workdir", required=True,
                         help="existing repository directory")
    p_codex.add_argument("--backend", default="openai",
                         help="repository backend key (default: openai)")
    p_codex.add_argument("--model", required=True,
                         help="exact requested model identifier")
    p_codex.add_argument("--effort", required=True,
                         choices=config_module.DEFAULT_EFFORT_ORDER,
                         help="exact requested reasoning effort")
    p_codex.add_argument("--policy", required=True,
                         help="canonical policy ID or permanent alias")
    p_codex.add_argument("--role", required=True,
                         help="runtime-neutral role bound into the receipt")
    p_codex.add_argument("--task-id", required=True,
                         help="task identifier bound into the receipt")
    p_codex.add_argument("--receipt", required=True,
                         help="new immutable receipt path; existing paths fail")
    p_codex.add_argument(
        "--independent-session", action="store_true", required=True,
        help="required assertion: create a new non-ephemeral independent session")
    p_codex.add_argument("--timeout-seconds", type=int, default=300,
                         help="positive subprocess timeout (default: 300)")
    p_codex.set_defaults(func=cmd_probe_codex_session)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (config_module.ConfigError, resolve_module.ResolutionError,
            transport_module.TransportError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
