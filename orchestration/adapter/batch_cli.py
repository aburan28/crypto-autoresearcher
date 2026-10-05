"""`python -m orchestration.adapter batch ...` -- Message Batches from the shell.

    batch plan      --delivery auto --deadline-seconds 7200 [--priority 40]
    batch submit    --role idea-generator --prompt-file q1.md --prompt-file q2.md
    batch submit    --task ledger/handoffs/TASK-....yaml --prompts-jsonl prompts.jsonl
    batch status    [ID ...] | --all
    batch list      [--remote]
    batch wait      ID --timeout-seconds 1800
    batch collect   ID [--print]
    batch escalate  ID [--custom-id C ...] [--cancel-remaining]
    batch cancel    ID
    batch delete    ID --yes

`plan` and `list` (without `--remote`) touch no network. Everything a batch
does is recorded write-once under the registry directory, so any later
session -- on any machine with the same checkout -- can `status`, `wait`,
`collect`, or `escalate` a batch it did not submit.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from . import batch as batch_module
from . import config as config_module
from . import manifest as manifest_module
from . import resolver as resolve_module
from . import transport as transport_module


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _load(args: argparse.Namespace) -> config_module.Config:
    return config_module.load(
        policies_path=Path(args.policies) if args.policies else None,
        providers_path=Path(args.providers) if args.providers else None,
        bindings_path=Path(args.bindings) if args.bindings else None)


def _registry(cfg: config_module.Config, args: argparse.Namespace) -> Path:
    return batch_module.registry_dir(cfg, override=getattr(args, "registry", None))


def _backend_for(cfg: config_module.Config, args: argparse.Namespace,
                 batch_id: str | None = None) -> str:
    """The backend a batch lives on: its submission record first, then flags."""
    if batch_id:
        submission = batch_module.load_submission(_registry(cfg, args), batch_id)
        if submission and submission.get("backend"):
            return str(submission["backend"])
    return getattr(args, "backend", None) or cfg.default_backend()


def _role_contract(role: str) -> str:
    parts = []
    for name in ("AGENTS.md", f"agents/{role}.md"):
        path = config_module.REPO_ROOT / name
        if not path.exists():
            raise SystemExit(f"no role contract at {path}")
        parts.append(path.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(parts)


def _load_handoff(path: str) -> dict[str, Any]:
    record = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        raise SystemExit(f"{path} is not a YAML mapping")
    return record


def _resolve(cfg: config_module.Config, args: argparse.Namespace
             ) -> tuple[resolve_module.Resolution, dict[str, Any] | None]:
    """Resolution plus the handoff body it came from (None for flag-driven)."""
    if getattr(args, "task", None):
        record = _load_handoff(args.task)
        body = record.get("handoff", record)
        resolution = resolve_module.resolve_handoff(
            cfg, record, backend=args.backend,
            **({"independent_session": True} if args.independent_session else {}))
        return resolution, body
    policy = args.policy
    if getattr(args, "role", None) and not policy:
        policy = cfg.role_default_policy(args.role)
    if not policy:
        raise SystemExit("one of --policy, --role, or --task is required")
    resolution = resolve_module.resolve(
        cfg, policy, backend=args.backend,
        fallback_allowed=args.allow_fallback,
        degraded_allowed=args.allow_degraded,
        independent_session=args.independent_session,
        originating_agent=getattr(args, "originating_agent", None),
        assigned_agent=getattr(args, "assigned_agent", None))
    return resolution, None


def _prompts(args: argparse.Namespace, task_id: str | None
             ) -> list[dict[str, Any]]:
    """[{custom_id, prompt, system?}] from --prompt-file, --prompts-jsonl, or stdin."""
    items: list[dict[str, Any]] = []
    for path in args.prompt_file or []:
        items.append({"prompt": Path(path).read_text(encoding="utf-8"),
                      "label": Path(path).stem})
    if args.prompts_jsonl:
        for raw in Path(args.prompts_jsonl).read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            line = json.loads(raw)
            if not isinstance(line, dict) or not line.get("prompt"):
                raise SystemExit(f"--prompts-jsonl line needs a `prompt`: {raw[:120]}")
            items.append(line)
    if not items:
        items.append({"prompt": sys.stdin.read()})
    explicit = list(args.custom_id or [])
    if explicit and len(explicit) != len(items):
        raise SystemExit(f"{len(explicit)} --custom-id values for {len(items)} prompts")
    for index, item in enumerate(items):
        if explicit:
            item["custom_id"] = explicit[index]
        elif not item.get("custom_id"):
            item["custom_id"] = batch_module.custom_id_for(
                task_id, index, item.get("label") if len(items) > 1 else None)
        batch_module.validate_custom_id(item["custom_id"])
    return items


def _print_decision(decision: batch_module.DeliveryDecision) -> None:
    print(f"# delivery: {decision.delivery} ({decision.reason})", file=sys.stderr)


def _result_line(result: batch_module.BatchResult) -> str:
    if result.completion is not None:
        c = result.completion
        usage = c.usage or {}
        return (f"{result.custom_id:<40} {result.type:<9} {c.model:<32} "
                f"in={usage.get('input_tokens', 0)} out={usage.get('output_tokens', 0)} "
                f"chars={len(c.text)} stop={c.stop_reason}")
    if result.error:
        inner = result.error.get("error") or result.error
        return (f"{result.custom_id:<40} {result.type:<9} "
                f"{inner.get('type', '?')}: {str(inner.get('message', ''))[:120]}")
    return f"{result.custom_id:<40} {result.type}"


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------
def cmd_plan(args: argparse.Namespace) -> int:
    cfg = _load(args)
    if args.task:
        decision = batch_module.delivery_from_handoff(
            cfg, _load_handoff(args.task), backend=args.backend, priority=args.priority)
        if args.delivery:
            decision = batch_module.choose_delivery(
                cfg, backend=args.backend, requested=args.delivery,
                deadline_seconds=(args.deadline_seconds
                                  if args.deadline_seconds is not None
                                  else decision.deadline_seconds),
                priority=args.priority)
    else:
        decision = batch_module.choose_delivery(
            cfg, backend=args.backend, requested=args.delivery or "auto",
            deadline_seconds=args.deadline_seconds, priority=args.priority)
    if args.json:
        print(json.dumps(decision.to_dict(), indent=2, sort_keys=True))
    else:
        print(f"{decision.delivery}: {decision.reason}")
    return 0


def cmd_submit(args: argparse.Namespace) -> int:
    cfg = _load(args)
    resolution, handoff = _resolve(cfg, args)
    task_id = args.task_id or (handoff or {}).get("id")
    role = args.role or (handoff or {}).get("to")
    system = (Path(args.system_file).read_text(encoding="utf-8")
              if args.system_file else (_role_contract(role) if role else None))
    items = _prompts(args, task_id)

    if handoff is not None and not args.delivery:
        decision = batch_module.delivery_from_handoff(
            cfg, {"handoff": handoff}, backend=resolution.backend,
            priority=args.priority)
        if args.deadline_seconds is not None:
            decision = batch_module.choose_delivery(
                cfg, backend=resolution.backend, requested=decision.requested,
                deadline_seconds=args.deadline_seconds, priority=args.priority)
    else:
        decision = batch_module.choose_delivery(
            cfg, backend=resolution.backend, requested=args.delivery or "batch",
            deadline_seconds=args.deadline_seconds, priority=args.priority)
    print(f"# {resolution.summary()}", file=sys.stderr)
    _print_decision(decision)

    if decision.delivery == "interactive":
        # The router decided this cannot wait: run each prompt now, through
        # the same request builder, and say so in every receipt.
        for item in items:
            completion = transport_module.complete(
                cfg, resolution, system=item.get("system") or system,
                messages=[transport_module.Message("user", item["prompt"])],
                max_tokens=args.max_tokens)
            print(f"### {item['custom_id']}\n{completion.text}\n")
            if args.receipt_dir:
                data = manifest_module.receipt(
                    resolution, completion, task_id=task_id, role=role, config=cfg,
                    delivery={"mode": "interactive", "custom_id": item["custom_id"],
                              "decision": decision.to_dict()})
                path = manifest_module.write_receipt(
                    Path(args.receipt_dir) / f"{item['custom_id']}.json", data)
                print(f"# receipt: {path}", file=sys.stderr)
        return 0

    entries = [batch_module.build_batch_entry(
        cfg, resolution, custom_id=item["custom_id"],
        system=item.get("system") or system,
        messages=[transport_module.Message("user", item["prompt"])],
        max_tokens=args.max_tokens, task_id=item.get("task_id") or task_id,
        role=role, note=item.get("note") or args.note) for item in items]
    size = batch_module.check_entries(entries)
    print(f"# {len(entries)} request(s), {size} bytes", file=sys.stderr)

    preflight_result = None
    if not args.no_preflight:
        preflight_result = batch_module.preflight(cfg, resolution.backend, entries[0])
        print(f"# preflight ok: {entries[0].custom_id} counts "
              f"{preflight_result.get('input_tokens')} input tokens", file=sys.stderr)
    if args.dry_run:
        print(json.dumps({"requests": [e.to_wire() for e in entries]}, indent=2))
        return 0

    batch = batch_module.submit(
        cfg, resolution.backend, entries, registry=_registry(cfg, args),
        task_id=task_id, note=args.note, decision=decision,
        preflight_result=preflight_result)
    print(batch.summary())
    print(f"# recorded under {batch_module.batch_dir(_registry(cfg, args), batch.id)}",
          file=sys.stderr)
    print(f"# next: python3 -m orchestration.adapter batch wait {batch.id} "
          f"--timeout-seconds 3600   (or `batch collect {batch.id}` later)",
          file=sys.stderr)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    cfg = _load(args)
    registry = _registry(cfg, args)
    ids = list(args.batch_id or [])
    if args.all:
        ids.extend(row["id"] for row in batch_module.local_batches(registry)
                   if not row["collected"] and not row["cancelled"]
                   and row["id"] not in ids)
    if not ids:
        print("no batch ids given and no open local batches", file=sys.stderr)
        return 0
    for batch_id in ids:
        batch = batch_module.retrieve(cfg, _backend_for(cfg, args, batch_id), batch_id)
        state = batch_module.local_state(registry, batch_id)
        flags = []
        if not state["known"]:
            flags.append("not submitted from this checkout")
        if state["collected"]:
            flags.append("collected")
        if state["escalated"]:
            flags.append(f"escalated: {', '.join(state['escalated'])}")
        print(batch.summary() + (f"  ({'; '.join(flags)})" if flags else ""))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    cfg = _load(args)
    registry = _registry(cfg, args)
    local = batch_module.local_batches(registry)
    known = {row["id"] for row in local}
    if args.json and not args.remote:
        print(json.dumps(local, indent=2, sort_keys=True))
        return 0
    if local:
        print(f"local registry ({registry}):")
        for row in local:
            state = ("collected" if row["collected"] else
                     "cancelled" if row["cancelled"] else "open")
            extra = f"  task={row['task_id']}" if row.get("task_id") else ""
            esc = f"  escalated={len(row['escalated'])}" if row["escalated"] else ""
            print(f"  {row['id']}  {state:<9} {row['requests']:>5} req  "
                  f"submitted {row['submitted_at']}{extra}{esc}")
    else:
        print(f"local registry ({registry}): empty")
    if args.remote:
        backend = args.backend or cfg.default_backend()
        batches, page = batch_module.list_batches(
            cfg, backend, limit=args.limit, after_id=args.after_id)
        print(f"\n{backend} ({len(batches)} shown"
              f"{', more available: pass --after-id ' + str(page['last_id']) if page['has_more'] else ''}):")
        for batch in batches:
            mark = "" if batch.id in known else "  (not in local registry)"
            print(f"  {batch.summary()}{mark}")
    return 0


def cmd_wait(args: argparse.Namespace) -> int:
    cfg = _load(args)
    backend = _backend_for(cfg, args, args.batch_id)

    def report(batch: batch_module.MessageBatch) -> None:
        print(f"# {batch.summary()}", file=sys.stderr)

    batch = batch_module.wait(
        cfg, backend, args.batch_id, timeout_seconds=args.timeout_seconds,
        poll_interval=args.poll_interval, on_poll=report)
    print(batch.summary())
    if not batch.ended:
        print(f"# wall-clock budget spent; the batch is still {batch.processing_status} "
              f"and remains collectable", file=sys.stderr)
        return 1
    return 0


def cmd_collect(args: argparse.Namespace) -> int:
    cfg = _load(args)
    backend = _backend_for(cfg, args, args.batch_id)
    collected = batch_module.collect(cfg, backend, args.batch_id,
                                     registry=_registry(cfg, args))
    if args.json:
        print(json.dumps({
            cid: {"type": r.type,
                  "text": r.completion.text if r.completion else None,
                  "usage": r.completion.usage if r.completion else None,
                  "model": r.completion.model if r.completion else None,
                  "stop_reason": r.completion.stop_reason if r.completion else None,
                  "error": r.error,
                  "superseded_by_escalation": cid in collected.superseded}
            for cid, r in sorted(collected.results.items())}, indent=2, sort_keys=True))
        return 0
    print(collected.summary())
    for custom_id, result in sorted(collected.results.items()):
        line = _result_line(result)
        if custom_id in collected.superseded:
            line += "  [superseded by escalation]"
        print(line)
        if args.print and result.completion is not None:
            print(result.completion.text)
            print()
    retryable = [cid for cid, r in collected.results.items() if r.retryable]
    if retryable:
        print(f"# resubmittable (expired or server error): {', '.join(sorted(retryable))}",
              file=sys.stderr)
    return 0


def cmd_cancel(args: argparse.Namespace) -> int:
    cfg = _load(args)
    backend = _backend_for(cfg, args, args.batch_id)
    batch = batch_module.cancel(cfg, backend, args.batch_id,
                                registry=_registry(cfg, args), reason=args.reason)
    print(batch.summary())
    print("# requests already processed keep their results; `batch collect` once "
          "it reports ended", file=sys.stderr)
    return 0


def cmd_escalate(args: argparse.Namespace) -> int:
    cfg = _load(args)
    backend = _backend_for(cfg, args, args.batch_id)
    done, batch = batch_module.escalate(
        cfg, backend, args.batch_id, custom_ids=args.custom_id or None,
        registry=_registry(cfg, args), cancel_remaining=args.cancel_remaining,
        reason=args.reason)
    for escalation in done:
        usage = escalation.completion.usage or {}
        print(f"{escalation.custom_id:<40} escalated  {escalation.completion.model:<32} "
              f"in={usage.get('input_tokens', 0)} out={usage.get('output_tokens', 0)} "
              f"-> {escalation.path}")
        if args.print:
            print(escalation.completion.text)
            print()
    if not done:
        print("# nothing to escalate: every requested custom_id was already escalated",
              file=sys.stderr)
    print(batch.summary())
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    cfg = _load(args)
    if not args.yes:
        raise SystemExit("deleting removes the provider's copy of the results; "
                         "pass --yes to confirm (the local registry is kept)")
    backend = _backend_for(cfg, args, args.batch_id)
    payload = batch_module.delete(cfg, backend, args.batch_id)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


# --------------------------------------------------------------------------
# parser
# --------------------------------------------------------------------------
def register(sub: argparse._SubParsersAction, add_selection) -> None:
    parser = sub.add_parser(
        "batch", help="Message Batches: submit, track, collect, escalate",
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    bsub = parser.add_subparsers(dest="batch_command", required=True)

    def add_registry(p: argparse.ArgumentParser) -> None:
        p.add_argument("--registry", help="override the write-once registry directory "
                                          f"(default: providers.yaml defaults.batch."
                                          f"registry_dir, or ${batch_module.BATCH_DIR_ENV})")

    def add_routing(p: argparse.ArgumentParser, default_delivery: str | None) -> None:
        p.add_argument("--delivery", choices=list(batch_module.DELIVERY_MODES),
                       default=default_delivery,
                       help="interactive | batch | auto (auto routes by deadline "
                            "and priority)")
        p.add_argument("--deadline-seconds", type=float,
                       help="when the result is needed; `auto` batches only if this "
                            "leaves room beyond the expected batch latency")
        p.add_argument("--priority", type=int,
                       help="dispatch priority 0..100; at or above urgent_priority "
                            "`auto` never batches")

    p = bsub.add_parser("plan", help="decide a delivery mode without sending anything")
    p.add_argument("--task", help="read delivery and deadline from this handoff")
    p.add_argument("--backend")
    p.add_argument("--json", action="store_true")
    add_routing(p, None)
    p.set_defaults(func=cmd_plan)

    p = bsub.add_parser("submit", help="resolve a policy and submit prompts as a batch")
    add_selection(p)
    p.add_argument("--task", help="resolve policy, permissions, delivery, and task id "
                                  "from this handoff record")
    p.add_argument("--prompt-file", action="append", help="one request per file")
    p.add_argument("--prompts-jsonl", help="one request per line: {\"prompt\", "
                                           "\"custom_id\"?, \"system\"?, \"label\"?}")
    p.add_argument("--system-file", help="system prompt; default is the role contract")
    p.add_argument("--custom-id", action="append",
                   help="explicit custom ids, one per prompt, in order")
    p.add_argument("--max-tokens", type=int)
    p.add_argument("--note", help="free-text note stored with the submission")
    p.add_argument("--no-preflight", action="store_true",
                   help="skip the count_tokens shape check of the first request")
    p.add_argument("--dry-run", action="store_true",
                   help="print the batch body after preflight and stop")
    p.add_argument("--receipt-dir", help="when the router runs interactively instead, "
                                         "write one receipt per prompt here")
    add_routing(p, None)
    add_registry(p)
    p.set_defaults(func=cmd_submit)

    p = bsub.add_parser("status", help="current processing status")
    p.add_argument("batch_id", nargs="*")
    p.add_argument("--all", action="store_true",
                   help="every open batch in the local registry")
    p.add_argument("--backend")
    add_registry(p)
    p.set_defaults(func=cmd_status)

    p = bsub.add_parser("list", help="batches known locally, and optionally remotely")
    p.add_argument("--remote", action="store_true",
                   help="also list the workspace's batches from the provider")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--after-id")
    p.add_argument("--backend")
    p.add_argument("--json", action="store_true")
    add_registry(p)
    p.set_defaults(func=cmd_list)

    p = bsub.add_parser("wait", help="poll until ended or the budget runs out")
    p.add_argument("batch_id")
    p.add_argument("--timeout-seconds", type=float, required=True)
    p.add_argument("--poll-interval", type=float)
    p.add_argument("--backend")
    add_registry(p)
    p.set_defaults(func=cmd_wait)

    p = bsub.add_parser("collect", help="download (once) and record the results")
    p.add_argument("batch_id")
    p.add_argument("--print", action="store_true", help="print each result's text")
    p.add_argument("--json", action="store_true")
    p.add_argument("--backend")
    add_registry(p)
    p.set_defaults(func=cmd_collect)

    p = bsub.add_parser("escalate", help="run pending requests synchronously now")
    p.add_argument("batch_id")
    p.add_argument("--custom-id", action="append",
                   help="only these requests (default: every request in the batch)")
    p.add_argument("--cancel-remaining", action="store_true",
                   help="cancel the batch even if some requests were not escalated")
    p.add_argument("--reason", help="why this became urgent; stored on the record")
    p.add_argument("--print", action="store_true")
    p.add_argument("--backend")
    add_registry(p)
    p.set_defaults(func=cmd_escalate)

    p = bsub.add_parser("cancel", help="cancel a running batch")
    p.add_argument("batch_id")
    p.add_argument("--reason")
    p.add_argument("--backend")
    add_registry(p)
    p.set_defaults(func=cmd_cancel)

    p = bsub.add_parser("delete", help="delete an ended batch from the provider")
    p.add_argument("batch_id")
    p.add_argument("--yes", action="store_true")
    p.add_argument("--backend")
    add_registry(p)
    p.set_defaults(func=cmd_delete)
