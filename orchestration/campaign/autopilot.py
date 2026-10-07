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
import statistics
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from ..adapter.config import Config
from ..adapter.config import load as load_config
from ..adapter.resolver import ResolutionError, resolve
from . import workers


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


def _trial_coverage_transition(before: str, after: str) -> dict:
    """Count only hash-validated runner output on the same frozen trial plan.

    The runner deliberately leaves publication and scientific review unverified;
    this transition cannot establish a discovery or an independent relation.
    """
    try:
        previous, current = json.loads(before), json.loads(after)
        left, right = previous["coverage"], current["coverage"]
        if left["plan_sha256"] != right["plan_sha256"]:
            return {"output_validated_delta": None, "reason": "trial plan changed"}
        return {"output_validated_delta":
                right["output_validated"] - left["output_validated"],
                "before": left["output_validated"],
                "after": right["output_validated"],
                "plan_sha256": right["plan_sha256"]}
    except (ValueError, TypeError, KeyError):
        return {"output_validated_delta": None, "reason": "coverage unavailable"}


def _usage(event_file: Path, runtime: str = "opencode") -> dict[str, float | int | None]:
    """Read the runtime's JSON events; unknown usage remains null, never zero."""
    return workers.usage(runtime, event_file)


def _has_tool_events(path: Path, runtime: str = "opencode") -> bool:
    return workers.has_tool_events(runtime, path)


def _has_error_events(path: Path, runtime: str = "opencode") -> bool:
    return workers.has_error_events(runtime, path)


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


def candidates(role: str, backends: list[str], runtime: str = "opencode",
               config: Config | None = None) -> list[tuple[str, str, dict]]:
    """Only bindings meeting the declared role policy can enter failover."""
    config = config or load_config()
    policy = config.role_default_policy(role)
    eligible = []
    for backend in backends:
        try:
            binding = resolve(config, policy, backend=backend)
        except ResolutionError:
            continue
        eligible.append((backend,
                         workers.model_reference(runtime, backend, binding.resolved_model_id),
                         binding.to_dict()))
    return eligible


def invoke_worker(action: Action, repo: Path, attempt_dir: Path,
                  *, backends: list[str], timeout: int, runtime: str = "opencode",
                  attach: str | None = None,
                  run_command: Callable[..., subprocess.CompletedProcess] = _run_worker,
                  config: Config | None = None,
                  env: dict[str, str] | None = None) -> dict:
    """Fail over only before any observed tool effect or checkout change.

    A late failure may already have written a receipt or published a PR. It is
    reconciled on the next cycle; the same task is never blindly replayed.
    """
    env = os.environ if env is None else env
    binary = workers.binary_for(runtime)
    if not shutil.which(binary):
        return {"ok": False, "reason": f"{binary} CLI unavailable", "attempts": []}
    options = candidates(action.role, backends, runtime)
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
                command = workers.build_command(runtime, action.prompt, model,
                                                attach=attach, env=env)
                extra: dict = {}
                if runtime != "opencode":
                    model_id = resolution.get("resolved_model_id") or model
                    extra["env"] = {**env, **workers.runtime_env(
                        config or load_config(), runtime, backend, model_id, env=env)}
                result = run_command(
                    command, cwd=repo, stdout=stdout,
                    stderr=stderr, timeout=timeout, check=False, **extra)
                code = result.returncode
            except subprocess.TimeoutExpired:  # injected runners may still raise
                code = 124
        if code == 0 and _has_error_events(out, runtime):
            code = 1
        changed = before != _git_state(repo)
        tools_used = _has_tool_events(out, runtime)
        attempt = {"runtime": runtime, "backend": backend, "model": model,
                   "policy": resolution["policy"],
                   "model_verified": resolution["verified_model"],
                   "fallback_used": index > 0, "exit_code": code,
                   "wall_seconds": round(time.monotonic() - started, 3),
                   "checkout_changed": changed, "tool_events": tools_used,
                   "stdout": str(out), "stderr": str(err), **_usage(out, runtime)}
        attempts.append(attempt)
        if code == 0:
            return {"ok": True, "reason": "worker returned; evidence unreviewed",
                    "attempts": attempts}
        if changed or tools_used:
            return {"ok": False, "reason": "ambiguous partial action; reconcile before retry",
                    "attempts": attempts}
    return {"ok": False, "reason": "all eligible models failed before a tool effect",
            "attempts": attempts}


def invoke_opencode(action: Action, repo: Path, attempt_dir: Path,
                    *, backends: list[str], timeout: int, attach: str | None = None,
                    run_command: Callable[..., subprocess.CompletedProcess] = _run_worker
                    ) -> dict:
    """The original OpenCode-only entry point, kept for its callers."""
    return invoke_worker(action, repo, attempt_dir, backends=backends, timeout=timeout,
                         runtime="opencode", attach=attach, run_command=run_command)


def _save(path: Path, data: dict) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _event(state_dir: Path, event: dict) -> None:
    with (state_dir / "events.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def _write_draft(attempt_dir: Path, action: Action, pending: dict, result: dict) -> Path:
    path = attempt_dir / "draft.md"
    header = {"action": action.key, "batch_id": pending["batch_id"],
              "custom_id": pending["custom_id"], "backend": pending.get("backend"),
              "model": pending.get("model"), "policy": pending.get("policy"),
              "model_verified": pending.get("model_verified"),
              "reported_model": result.get("reported_model"),
              "usage": result.get("usage"),
              "status": "untrusted draft; no repository access; not evidence"}
    path.write_text("<!-- " + json.dumps(header, sort_keys=True) + " -->\n\n"
                    + (result.get("text") or ""), encoding="utf-8")
    return path


def _poll_batches(state: dict, state_dir: Path, batch_lane, *, now: float,
                  retry_seconds: int) -> Action | None:
    """Advance the draft lane by at most one filing action per poll.

    A provider error while polling leaves the batch pending: the submission
    record exists and the batch keeps running whatever this process can see.
    """
    from .batch_lane import filing_note
    for key, pending in list(state["pending_batches"].items()):
        try:
            status = batch_lane.status(pending["batch_id"])
        except Exception as exc:
            _event(state_dir, {"time": now, "event": "batch_poll_error", "key": key,
                               "batch_id": pending["batch_id"],
                               "error": f"{type(exc).__name__}: {exc}"})
            continue
        if status != "ended":
            continue
        try:
            result = batch_lane.collect(pending["batch_id"], pending["custom_id"])
        except Exception as exc:
            result = {"type": "collect_error", "text": None, "usage": None,
                      "error": {"message": f"{type(exc).__name__}: {exc}"}}
        del state["pending_batches"][key]
        action = Action(pending["kind"], pending["target"], pending["prompt"],
                        pending["role"])
        attempt_dir = state_dir / "attempts" / pending["attempt_id"]
        attempt_dir.mkdir(parents=True, exist_ok=True)
        if result.get("type") == "succeeded" and result.get("text"):
            draft = _write_draft(attempt_dir, action, pending, result)
            _event(state_dir, {"time": now, "event": "batch_collected", "key": key,
                               "batch_id": pending["batch_id"], "draft": str(draft),
                               "usage": result.get("usage"),
                               "attempt_id": pending["attempt_id"]})
            return Action(action.kind, action.target,
                          action.prompt + filing_note(draft), action.role)
        _event(state_dir, {"time": now, "event": "batch_failed", "key": key,
                           "batch_id": pending["batch_id"],
                           "result_type": result.get("type"),
                           "error": result.get("error"),
                           "attempt_id": pending["attempt_id"]})
        state["cooldowns"][key] = now + retry_seconds
    return None


def supervise(repo: Path, state_dir: Path, *, backends: list[str],
              max_actions: int | None = None, idle_seconds: int = 60,
              retry_seconds: int = 300, timeout: int = 7200,
              attach: str | None = None, runtime: str = "opencode",
              delivery: str = "interactive", batch_lane=None,
              batch_poll_seconds: int = 300, wait_batches: int = 0,
              selector: Callable[..., Action | None] = select_next,
              invoke: Callable[..., dict] = invoke_worker,
              clock: Callable[[], float] = time.time,
              sleeper: Callable[[float], None] = time.sleep) -> dict:
    """Continue after completed actions and process restarts, without busy polling.

    With `delivery` other than `interactive` and a `batch_lane`, a batchable
    action is first submitted as a single-turn draft; when the batch ends the
    same action runs interactively with the draft attached for verification.
    """
    if delivery != "interactive" and batch_lane is None:
        raise ValueError("a batch lane is required for delivery=" + delivery)
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
        state.setdefault("pending_batches", {})
        state.setdefault("batches_submitted", 0)
        if state.get("inflight"):
            interrupted = state["inflight"]
            _event(state_dir, {"time": clock(), "event": "interrupted_action",
                               "action": interrupted, "evidence": "unverified"})
            state["cooldowns"][interrupted["key"]] = clock() + 86400
            state["pending_reconcile"] = interrupted
            state["inflight"] = None
            _save(state_path, state)
        count = 0
        loop_started = clock()
        next_poll = 0.0
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
            excluded |= set(state["pending_batches"])
            pending = state.get("pending_reconcile")
            drafted = None
            if state["pending_batches"] and batch_lane is not None and not pending \
                    and now >= next_poll:
                drafted = _poll_batches(state, state_dir, batch_lane, now=now,
                                        retry_seconds=retry_seconds)
                next_poll = now + batch_poll_seconds
                _save(state_path, state)
            if drafted is not None:
                action = drafted
            elif pending and "review:" + pending["target"] not in excluded:
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
                _event(state_dir, {"time": now, "event": "idle", "excluded": sorted(excluded),
                                   "pending_batches": sorted(state["pending_batches"])})
                if state["pending_batches"] and batch_lane is not None:
                    # Nothing else is runnable but a draft is still being
                    # served; wait for it rather than declare the queue empty.
                    waiting = clock() - loop_started
                    if max_actions is None or waiting < wait_batches:
                        pause = min(idle_seconds, batch_poll_seconds)
                        if max_actions is not None:
                            pause = min(pause, max(1, int(wait_batches - waiting)))
                        sleeper(pause)
                        continue
                if max_actions is not None:
                    break
                sleeper(idle_seconds)
                continue
            attempt_id = uuid.uuid4().hex
            attempt_dir = state_dir / "attempts" / attempt_id
            attempt_dir.mkdir(parents=True)
            if drafted is None and batch_lane is not None and delivery != "interactive":
                from .batch_lane import delivery_for
                decision = delivery_for(batch_lane.config, action.kind, delivery,
                                        batch_lane.backend)
                if decision.delivery == "batch":
                    try:
                        submitted = batch_lane.submit(action, attempt_id=attempt_id)
                    except Exception as exc:
                        submitted = None
                        _event(state_dir, {"time": now, "event": "batch_submit_error",
                                           "action": action.as_dict(),
                                           "attempt_id": attempt_id,
                                           "error": f"{type(exc).__name__}: {exc}"})
                        state["cooldowns"][action.key] = clock() + retry_seconds
                    if submitted is not None:
                        state["pending_batches"][action.key] = {
                            **action.as_dict(), "attempt_id": attempt_id,
                            "submitted_at": now, **submitted}
                        state["batches_submitted"] += 1
                        _event(state_dir, {"time": now, "event": "batch_submitted",
                                           "action": action.as_dict(),
                                           "attempt_id": attempt_id,
                                           "delivery": decision.to_dict(), **submitted})
                    _save(state_path, state)
                    count += 1
                    continue
            state["inflight"] = {**action.as_dict(), "key": action.key,
                                 "attempt_id": attempt_id}
            if action.kind == "run":
                state["inflight"]["execution_before"] = _execution_snapshot(
                    repo, action.target)
            _save(state_path, state)
            _event(state_dir, {"time": now, "event": "started", "action": action.as_dict(),
                               "attempt_id": attempt_id, "drafted": drafted is not None})
            started = time.monotonic()
            try:
                result = invoke(action, repo, attempt_dir, backends=backends,
                                timeout=timeout, attach=attach, runtime=runtime)
            except Exception as exc:
                result = {"ok": False, "reason": f"supervisor error: {type(exc).__name__}: {exc}",
                          "attempts": []}
            after = _execution_snapshot(repo, action.target) if action.kind == "run" else None
            event = {"time": clock(), "event": "finished", "action": action.as_dict(),
                     "attempt_id": attempt_id, "wall_seconds": round(time.monotonic()-started, 3),
                     "result": result}
            if after is not None:
                event["trial_coverage"] = _trial_coverage_transition(
                    state["inflight"]["execution_before"], after)
            _event(state_dir, event)
            state["attempts"] += 1
            state["completed_actions"] += int(bool(result.get("ok")))
            ambiguous = result.get("reason", "").startswith("ambiguous partial action")
            run_changed = (action.kind == "run" and
                           state["inflight"].get("execution_before") != after)
            if ambiguous or (action.kind == "run" and
                             (result.get("ok") or run_changed)):
                state["pending_reconcile"] = state["inflight"]
                state["pending_reconcile"]["execution_advanced"] = run_changed
                state["pending_reconcile"]["worker_ok"] = bool(result.get("ok"))
                state["cooldowns"][action.key] = clock() + (
                    retry_seconds if run_changed and result.get("ok") else 86400)
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
            if (result.get("ok") and action.kind != "review"
                    and state.get("pending_reconcile") is None):
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


def report(state_dir: Path, *, now: float | None = None) -> dict:
    """Stream action telemetry, keeping unknown scientific outcomes explicit."""
    if now is None:
        now = time.time()
    events = state_dir / "events.jsonl"
    actions = workers = no_progress = interrupted = model_attempts = failovers = 0
    batch_submitted = batch_collected = batch_failed = 0
    recent_actions = recent_designs = recent_runs = 0
    recent_validated_delta = recent_coverage_known = recent_coverage_unknown = 0
    known_cost = cost_total = token_coverage = tokens_in = tokens_out = 0
    recent_known_cost = recent_cost_total = recent_model_attempts = 0
    recent_token_coverage = recent_tokens_in = recent_tokens_out = 0
    last_finished: float | None = None
    handoff_delays: list[float] = []
    if events.exists():
        with events.open(encoding="utf-8") as stream:
            for line in stream:
                try:
                    row = json.loads(line)
                except ValueError:
                    # A killed writer may leave a trailing partial line. Its
                    # successor is reconciled from the checkpoint on restart.
                    continue
                kind = row.get("event")
                stamp = row.get("time")
                recent = isinstance(stamp, (int, float)) and now - 86400 <= stamp <= now
                if kind == "started":
                    if last_finished is not None and isinstance(stamp, (int, float)):
                        if recent and stamp >= last_finished:
                            handoff_delays.append(stamp - last_finished)
                    last_finished = None
                elif kind == "finished":
                    last_finished = stamp if isinstance(stamp, (int, float)) else None
                    actions += 1
                    workers += bool(row.get("result", {}).get("ok"))
                    if recent:
                        recent_actions += 1
                        action_kind = row.get("action", {}).get("kind")
                        recent_designs += action_kind == "design"
                        recent_runs += action_kind == "run"
                        if action_kind == "run":
                            delta = row.get("trial_coverage", {}).get("output_validated_delta")
                            if isinstance(delta, int):
                                recent_validated_delta += delta
                                recent_coverage_known += 1
                            else:
                                recent_coverage_unknown += 1
                    for attempt in row.get("result", {}).get("attempts", []):
                        model_attempts += 1
                        recent_model_attempts += recent
                        failovers += bool(attempt.get("fallback_used"))
                        if attempt.get("cost_usd") is not None:
                            known_cost += 1
                            cost_total += attempt["cost_usd"]
                            if recent:
                                recent_known_cost += 1
                                recent_cost_total += attempt["cost_usd"]
                        if (attempt.get("input_tokens") is not None
                                and attempt.get("output_tokens") is not None):
                            token_coverage += 1
                            tokens_in += attempt["input_tokens"]
                            tokens_out += attempt["output_tokens"]
                            if recent:
                                recent_token_coverage += 1
                                recent_tokens_in += attempt["input_tokens"]
                                recent_tokens_out += attempt["output_tokens"]
                elif kind == "no_progress":
                    no_progress += 1
                elif kind == "interrupted_action":
                    interrupted += 1
                elif kind == "batch_submitted":
                    batch_submitted += 1
                elif kind == "batch_collected":
                    batch_collected += 1
                elif kind in ("batch_failed", "batch_submit_error"):
                    batch_failed += 1
    return {"actions_attempted": actions,
            "actions_last_24h": recent_actions,
            "design_actions_last_24h": recent_designs,
            "run_actions_last_24h": recent_runs,
            "runner_output_validated_trial_delta_24h": (
                recent_validated_delta if recent_coverage_known else None),
            "runner_coverage_24h": f"{recent_coverage_known}/{recent_runs}",
            "runner_coverage_unknown_24h": recent_coverage_unknown,
            "next_action_latency_seconds_median_24h": (
                round(statistics.median(handoff_delays), 3) if handoff_delays else None),
            "workers_returned": workers,
            "no_progress_actions": no_progress,
            "interrupted_actions": interrupted,
            "batch_drafts_submitted": batch_submitted,
            "batch_drafts_collected": batch_collected,
            "batch_drafts_failed": batch_failed,
            "verified_discoveries": None, "independent_relations": None,
            "model_attempts": model_attempts,
            "failovers": failovers,
            "measured_cost_usd": round(cost_total, 8) if known_cost else None,
            "cost_coverage": f"{known_cost}/{model_attempts}",
            "measured_cost_usd_last_24h": (
                round(recent_cost_total, 8) if recent_known_cost else None),
            "cost_coverage_last_24h": f"{recent_known_cost}/{recent_model_attempts}",
            "measured_input_tokens": tokens_in if token_coverage else None,
            "measured_output_tokens": tokens_out if token_coverage else None,
            "token_coverage": f"{token_coverage}/{model_attempts}",
            "measured_input_tokens_last_24h": (
                recent_tokens_in if recent_token_coverage else None),
            "measured_output_tokens_last_24h": (
                recent_tokens_out if recent_token_coverage else None),
            "token_coverage_last_24h":
                f"{recent_token_coverage}/{recent_model_attempts}"}
