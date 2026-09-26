"""A persistent, bounded-action supervisor over the existing run/coordinate skills.

The supervisor owns scheduling, never scientific authority.  A worker's exit
ends one action, not a campaign.  The ledger, runner admission, and Coordinator
still decide whether an experiment is approved and whether evidence is valid.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import signal
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from ..adapter.config import load as load_config
from ..adapter.resolver import ResolutionError, resolve


@dataclass(frozen=True)
class Action:
    kind: str
    target: str
    prompt: str
    role: str

    @property
    def key(self) -> str:
        return f"{self.kind}:{self.target}"

    def as_dict(self) -> dict[str, str]:
        return {"kind": self.kind, "target": self.target, "role": self.role,
                "prompt": self.prompt}


def select_next(repo: Path, *, excluded: set[str] | None = None) -> Action | None:
    """Use the existing ECC priority and coverage selectors, without inventing work."""
    from tools.ecc_priority import load_policy, open_ecc_ideas
    from tools.newest_experiments import newest_runnable

    excluded = excluded or set()
    rows = newest_runnable(repo, include_blocked=True)
    for row in rows:
        if (row["ecc"] and row["execution_state"] == "ready"
                and f"run:{row['id']}" not in excluded):
            return Action("run", row["id"],
                f"Use the repository $run skill for {row['id']} only. Run its existing "
                "approved program with declared controls and seeds; preserve all "
                "attempts and receipts. Respect the handoff's inference policy and "
                "ownership. Report completed, failed, and impeded trials.", "executor")

    policy = load_policy(repo / "orchestration" / "research-priority.yaml")
    for idea in open_ecc_ideas(policy, repo=repo):
        if f"design:{idea['id']}" not in excluded:
            return Action("design", idea["id"],
                f"As the top-level dispatcher, use /coordinate and "
                f"/design-experiment for {idea['id']}. Dispatch the Coordinator "
                "subagent for its reserved decisions. "
                "Rank it under the current ECC priority, specify a falsifiable "
                "hypothesis and complete frozen protocol, and record Coordinator "
                "approval under the standing user authorization. Archive and "
                "publish by the repository contract. Do not launch scientific trials.",
                "coordinator")

    # These approved specifications need their existing launcher or a prepared
    # plan. The run skill itself checks for a documented launcher first.
    for row in rows:
        if (row["ecc"] and row["execution_state"] == "needs_implementation_or_plan"
                and f"prepare:{row['id']}" not in excluded):
            return Action("prepare", row["id"],
                f"As the top-level dispatcher, use /coordinate and dispatch "
                f"the Coordinator to prepare approved {row['id']}: inspect its "
                "existing documented launcher first, then arrange the smallest "
                "missing implementation or trial plan. Do not run trials in "
                "this coordination action. Preserve the frozen contract.",
                "coordinator")

    for row in rows:
        if (row["ecc"] and row["execution_state"] in
                ("needs_plan_repair", "needs_reconciliation")
                and f"repair:{row['id']}" not in excluded):
            return Action("repair", row["id"],
                f"Use /coordinate to diagnose {row['execution_state']} for "
                f"{row['id']}. Preserve existing immutable attempts, create a "
                "scoped repair or amendment if justified, and do not run "
                "scientific trials in this action.", "coordinator")

    for row in rows:
        if row["execution_state"] == "ready" and f"run:{row['id']}" not in excluded:
            return Action("run", row["id"],
                f"Use the repository $run skill for {row['id']} only; run its "
                "existing approved program, preserve all attempts, and respect "
                "the handoff, claim and machine-resource limits.", "executor")
    for row in rows:
        if (row["execution_state"] == "needs_implementation_or_plan"
                and f"prepare:{row['id']}" not in excluded):
            return Action("prepare", row["id"],
                f"As the top-level dispatcher, use /coordinate and dispatch "
                f"the Coordinator to arrange the smallest missing preparation "
                f"for approved {row['id']}; check its existing launcher first. "
                "Do not launch scientific trials.", "coordinator")
    for row in rows:
        if (row["execution_state"] in ("needs_plan_repair", "needs_reconciliation")
                and f"repair:{row['id']}" not in excluded):
            return Action("repair", row["id"],
                f"Use /coordinate to diagnose {row['execution_state']} for "
                f"{row['id']}, preserving immutable attempts. Do not run trials.",
                "coordinator")

    # One bounded portfolio pass may rank a new idea; a repeated identical
    # result is cooled down rather than buying the same answer forever.
    if "portfolio:ecdlp" not in excluded:
        return Action("portfolio", "ecdlp",
            "As the top-level dispatcher, use /coordinate in portfolio mode "
            "and dispatch the Coordinator subagent. Select one justified ECC "
            "research action using the current goals and negative evidence. "
            "If there is no ranked action, record the concrete impediment and "
            "recheck; do not manufacture an experiment or claim progress. "
            "Do not launch scientific trials.", "coordinator")
    return None


def _git_state(repo: Path) -> str:
    result = subprocess.run(["git", "status", "--porcelain", "--untracked-files=normal"],
                            cwd=repo, text=True, capture_output=True, check=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, text=True,
                          capture_output=True, check=True).stdout.strip()
    return head + "\n" + result.stdout


def _source_signature(repo: Path) -> str:
    """A cheap signal for an external checkout update, never an evidence hash."""
    try:
        return hashlib.sha256(_git_state(repo).encode()).hexdigest()
    except (OSError, subprocess.CalledProcessError):
        return "non-git fixture"


def _execution_snapshot(repo: Path, exp_id: str) -> str:
    """Measure trial coverage without treating an agent's prose as progress."""
    from tools.newest_experiments import execution_progress
    try:
        return json.dumps(execution_progress(repo / "experiments" / exp_id, repo),
                          sort_keys=True)
    except (OSError, ValueError) as exc:
        return f"unavailable:{type(exc).__name__}"


def _usage(event_file: Path) -> dict[str, float | int | None]:
    """Read OpenCode JSON events; unknown usage remains null, never zero."""
    tokens_in = tokens_out = 0
    cost = 0.0
    seen_input = seen_output = seen_cost = False
    if event_file.exists():
        for line in event_file.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            part = (event.get("part") or (event.get("properties") or {}).get("part")
                    or {})
            if not isinstance(part, dict) or part.get("type") != "step-finish":
                continue
            tokens = part.get("tokens") or {}
            if isinstance(tokens, dict):
                if isinstance(tokens.get("input"), (int, float)):
                    tokens_in += int(tokens["input"])
                    seen_input = True
                if isinstance(tokens.get("output"), (int, float)):
                    tokens_out += int(tokens["output"])
                    seen_output = True
            if isinstance(part.get("cost"), (int, float)):
                cost += float(part["cost"])
                seen_cost = True
    return {"input_tokens": tokens_in if seen_input else None,
            "output_tokens": tokens_out if seen_output else None,
            "cost_usd": round(cost, 8) if seen_cost else None}


def _has_tool_events(path: Path) -> bool:
    if not path.exists():
        return False
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            part = (event.get("part") or (event.get("properties") or {}).get("part")
                    or {})
            kind = str(part.get("type", "")) if isinstance(part, dict) else ""
            if "tool" in kind.lower() or "tool" in str(event.get("type", "")).lower():
                return True
    return False


def _has_error_events(path: Path) -> bool:
    if not path.exists():
        return False
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") == "error":
                return True
    return False


def _run_worker(command: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Kill the whole CLI process group when a worker watchdog expires."""
    timeout = kwargs.pop("timeout")
    kwargs.pop("check", None)
    process = subprocess.Popen(command, start_new_session=True, **kwargs)
    try:
        code = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        code = 124
    return subprocess.CompletedProcess(command, code)


def candidates(role: str, backends: list[str]) -> list[tuple[str, str, dict]]:
    """Only bindings meeting the declared role policy can enter failover."""
    config = load_config()
    policy = config.role_default_policy(role)
    eligible = []
    for backend in backends:
        try:
            binding = resolve(config, policy, backend=backend)
        except ResolutionError:
            continue
        # OpenCode's custom local provider is named vllm in opencode.json.
        provider = "vllm" if backend == "local" else backend
        eligible.append((backend, f"{provider}/{binding.resolved_model_id}",
                         binding.to_dict()))
    return eligible


def invoke_opencode(action: Action, repo: Path, attempt_dir: Path,
                    *, backends: list[str], timeout: int, attach: str | None = None,
                    run_command: Callable[..., subprocess.CompletedProcess] = _run_worker
                    ) -> dict:
    """Fail over only before any observed tool effect or checkout change.

    A late failure may already have written a receipt or published a PR. It is
    reconciled on the next cycle; the same task is never blindly replayed.
    """
    if not shutil.which("opencode"):
        return {"ok": False, "reason": "opencode CLI unavailable", "attempts": []}
    options = candidates(action.role, backends)
    if not options:
        return {"ok": False, "reason": "no eligible binding for role policy",
                "attempts": []}
    attempts = []
    for index, (backend, model, resolution) in enumerate(options):
        out = attempt_dir / f"model-{index}.jsonl"
        err = attempt_dir / f"model-{index}.stderr"
        before = _git_state(repo)
        started = time.monotonic()
        with out.open("w", encoding="utf-8") as stdout, err.open("w", encoding="utf-8") as stderr:
            try:
                command = ["opencode", "run"]
                if attach:
                    command.extend(["--attach", attach])
                command.extend(["--format", "json", "--agent", "build",
                                "--model", model, action.prompt])
                result = run_command(
                    command, cwd=repo, stdout=stdout,
                    stderr=stderr, timeout=timeout, check=False)
                code = result.returncode
            except subprocess.TimeoutExpired:  # injected runners may still raise
                code = 124
        if code == 0 and _has_error_events(out):
            code = 1
        changed = before != _git_state(repo)
        tools_used = _has_tool_events(out)
        attempt = {"backend": backend, "model": model, "policy": resolution["policy"],
                   "model_verified": resolution["verified_model"],
                   "fallback_used": index > 0, "exit_code": code,
                   "wall_seconds": round(time.monotonic() - started, 3),
                   "checkout_changed": changed, "tool_events": tools_used,
                   "stdout": str(out), "stderr": str(err), **_usage(out)}
        attempts.append(attempt)
        if code == 0:
            return {"ok": True, "reason": "worker returned; evidence unreviewed",
                    "attempts": attempts}
        if changed or tools_used:
            return {"ok": False, "reason": "ambiguous partial action; reconcile before retry",
                    "attempts": attempts}
    return {"ok": False, "reason": "all eligible models failed before a tool effect",
            "attempts": attempts}


def _save(path: Path, data: dict) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _event(state_dir: Path, event: dict) -> None:
    with (state_dir / "events.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def supervise(repo: Path, state_dir: Path, *, backends: list[str],
              max_actions: int | None = None, idle_seconds: int = 60,
              retry_seconds: int = 300, timeout: int = 7200,
              attach: str | None = None,
              selector: Callable[..., Action | None] = select_next,
              invoke: Callable[..., dict] = invoke_opencode,
              clock: Callable[[], float] = time.time,
              sleeper: Callable[[float], None] = time.sleep) -> dict:
    """Continue after completed actions and process restarts, without busy polling."""
    repo = repo.resolve()
    state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(state_dir, 0o700)
    with (state_dir / "supervisor.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state_path = state_dir / "state.json"
        state = json.loads(state_path.read_text()) if state_path.exists() else {
            "attempts": 0, "completed_actions": 0, "cooldowns": {},
            "inflight": None, "pending_reconcile": None,
            "checkout_signature": _source_signature(repo)}
        if state.get("inflight"):
            interrupted = state["inflight"]
            _event(state_dir, {"time": clock(), "event": "interrupted_action",
                               "action": interrupted, "evidence": "unverified"})
            state["cooldowns"][interrupted["key"]] = clock() + 86400
            state["pending_reconcile"] = interrupted
            state["inflight"] = None
            _save(state_path, state)
        count = 0
        while max_actions is None or count < max_actions:
            now = clock()
            source = _source_signature(repo)
            if source != state.get("checkout_signature"):
                # An external checkout update may have produced new work. Keep
                # unsafe run/review cooldowns until reconciliation is complete.
                state["cooldowns"] = {key: until for key, until in state["cooldowns"].items()
                                      if key.startswith(("run:", "review:"))}
                state["checkout_signature"] = source
                _save(state_path, state)
            excluded = {key for key, until in state["cooldowns"].items() if until > now}
            pending = state.get("pending_reconcile")
            if pending and "review:" + pending["target"] not in excluded:
                action = Action("review", pending["target"],
                    f"As the top-level dispatcher, use /coordinate and dispatch "
                    f"the Coordinator to reconcile the last {pending['kind']} action "
                    f"for {pending['target']} (attempt {pending['attempt_id']}). "
                    "Inspect existing outputs, receipts, claims and branch state; "
                    "arrange independent evidence review and archive when warranted. "
                    "Do not rerun the experiment or presume its result is valid.",
                    "coordinator")
            elif pending:
                action = None
            else:
                action = selector(repo, excluded=excluded)
            if action is None:
                _event(state_dir, {"time": now, "event": "idle", "excluded": sorted(excluded)})
                if max_actions is not None:
                    break
                sleeper(idle_seconds)
                continue
            attempt_id = uuid.uuid4().hex
            attempt_dir = state_dir / "attempts" / attempt_id
            attempt_dir.mkdir(parents=True)
            state["inflight"] = {**action.as_dict(), "key": action.key,
                                 "attempt_id": attempt_id}
            if action.kind == "run":
                state["inflight"]["execution_before"] = _execution_snapshot(
                    repo, action.target)
            _save(state_path, state)
            _event(state_dir, {"time": now, "event": "started", "action": action.as_dict(),
                               "attempt_id": attempt_id})
            started = time.monotonic()
            try:
                result = invoke(action, repo, attempt_dir, backends=backends,
                                timeout=timeout, attach=attach)
            except Exception as exc:
                result = {"ok": False, "reason": f"supervisor error: {type(exc).__name__}: {exc}",
                          "attempts": []}
            event = {"time": clock(), "event": "finished", "action": action.as_dict(),
                     "attempt_id": attempt_id, "wall_seconds": round(time.monotonic()-started, 3),
                     "result": result}
            _event(state_dir, event)
            state["attempts"] += 1
            state["completed_actions"] += int(bool(result.get("ok")))
            if action.kind == "run" or result.get("reason", "").startswith(
                    "ambiguous partial action"):
                state["pending_reconcile"] = state["inflight"]
                advanced = (action.kind == "run" and
                    state["inflight"].get("execution_before") !=
                    _execution_snapshot(repo, action.target))
                state["pending_reconcile"]["execution_advanced"] = advanced
                state["pending_reconcile"]["worker_ok"] = bool(result.get("ok"))
                state["cooldowns"][action.key] = clock() + (
                    retry_seconds if advanced and result.get("ok") else 86400)
            elif action.kind == "review" and result.get("ok"):
                prior = state.get("pending_reconcile") or {}
                if prior.get("worker_ok") and prior.get("execution_advanced"):
                    # The runner's coverage has moved, and the Coordinator got
                    # a turn to archive/reconcile. Another ready trial may run.
                    state["cooldowns"].pop(prior.get("key"), None)
                state["pending_reconcile"] = None
                state["cooldowns"][action.key] = clock() + retry_seconds
            else:
                state["cooldowns"][action.key] = clock() + retry_seconds
            # Avoid buying the identical proposal every five minutes when a
            # successful worker exit did not actually change the worklist.
            if action.kind != "review" and state.get("pending_reconcile") is None:
                successor = selector(repo, excluded=set())
                if successor is not None and successor.key == action.key:
                    state["cooldowns"][action.key] = clock() + 86400
                    _event(state_dir, {"time": clock(), "event": "no_progress",
                                       "action": action.as_dict(),
                                       "recheck": "new checkout state or 24 hours"})
            state["inflight"] = None
            state["checkout_signature"] = _source_signature(repo)
            _save(state_path, state)
            count += 1
            if not result.get("ok") and max_actions is None:
                sleeper(idle_seconds)
        return state


def report(state_dir: Path) -> dict:
    """Report outcomes and costs without counting a worker exit as a discovery."""
    events = state_dir / "events.jsonl"
    rows = [json.loads(line) for line in events.read_text().splitlines()] if events.exists() else []
    finished = [row for row in rows if row["event"] == "finished"]
    attempts = [a for row in finished for a in row["result"].get("attempts", [])]
    known_cost = [a["cost_usd"] for a in attempts if a.get("cost_usd") is not None]
    tokens = [a for a in attempts if a.get("input_tokens") is not None
              and a.get("output_tokens") is not None]
    return {"actions_attempted": len(finished),
            "workers_returned": sum(bool(row["result"].get("ok")) for row in finished),
            "no_progress_actions": sum(row["event"] == "no_progress" for row in rows),
            "interrupted_actions": sum(row["event"] == "interrupted_action" for row in rows),
            "verified_discoveries": None, "independent_relations": None,
            "model_attempts": len(attempts),
            "failovers": sum(bool(a.get("fallback_used")) for a in attempts),
            "measured_cost_usd": round(sum(known_cost), 8) if known_cost else None,
            "cost_coverage": f"{len(known_cost)}/{len(attempts)}",
            "measured_input_tokens": sum(a["input_tokens"] for a in tokens) if tokens else None,
            "measured_output_tokens": sum(a["output_tokens"] for a in tokens) if tokens else None,
            "token_coverage": f"{len(tokens)}/{len(attempts)}"}
