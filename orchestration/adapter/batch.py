"""Message Batches for the inference adapter.

A Message Batch takes the same request bodies the synchronous transport
builds, processes them asynchronously (most within an hour, all within 24
hours) at half the token price, and returns one result per request keyed by
``custom_id``. Nothing about a role, policy, or binding changes: a batched
request is resolved by the same resolver, built by ``build_request``, guarded
by the same cost policy, and recorded with the same receipt fields plus the
batch it travelled in.

Three things live here on top of the transport:

* ``choose_delivery`` -- the router. Given what the caller asked for
  (``interactive`` / ``batch`` / ``auto``), the deadline it stated, and the
  task's dispatch priority, it picks a delivery mode and says why. ``auto``
  batches only when the deadline leaves room beyond the provider's published
  latency envelope; an urgent task never waits on a batch.
* a write-once **registry** under ``coordination/inference-batches/<id>/``
  (``submission.json``, ``requests.jsonl``, ``results.jsonl``,
  ``collected.json``, ``escalations/``), so a batch submitted from one
  ephemeral session can be collected from any other, and so a result once
  collected is served from disk without another download.
* ``escalate`` -- for the case where a result became urgent after it was
  batched: the still-pending request is re-run synchronously now, the batch
  copy is marked superseded when it lands, and the batch is cancelled once
  nothing in it is still wanted, so a request is never paid for twice
  without a record saying so.

Standard library only, like the rest of the adapter. Delivery is a transport
fact, not a research-state transition: it never approves, promotes, or
reviews anything.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

from .config import REPO_ROOT, Config, ConfigError
from .prompt_cache import (PromptCachePolicy, apply_prompt_cache,
                           normalize_usage)
from .resolver import Resolution
from .transport import (RETRY_STATUS, Completion, Message, Tool,
                        TransportError, _default_opener, auth_headers,
                        build_request, parse_response)

DELIVERY_MODES = ("interactive", "batch", "auto")
PROCESSING_STATUSES = ("in_progress", "canceling", "ended")
RESULT_TYPES = ("succeeded", "errored", "canceled", "expired")
CUSTOM_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")
MAX_REQUESTS_PER_BATCH = 100_000
MAX_BATCH_BYTES = 256 * 1024 * 1024
BATCH_DIR_ENV = "AUTORESEARCH_BATCH_DIR"

# Messages API parameters the batch endpoint rejects outright. Checked before
# submission because the batch validates its requests asynchronously and
# reports a malformed one only when the whole batch has ended.
UNBATCHABLE_FIELDS = ("stream", "speed")

# The subset of a Messages request that `count_tokens` accepts; the preflight
# sends exactly these so a batch of 10,000 requests fails on shape now rather
# than in 24 hours.
COUNT_TOKENS_FIELDS = ("model", "messages", "system", "tools", "tool_choice",
                       "thinking")


class BatchError(TransportError):
    """A batch operation could not be completed or would violate a contract."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------
# delivery routing
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class DeliveryDecision:
    """Which transport a request takes, and the reason the record will carry."""
    delivery: str                       # "interactive" | "batch"
    reason: str
    requested: str                      # "interactive" | "batch" | "auto"
    backend: str
    deadline_seconds: float | None = None
    priority: int | None = None
    expected_latency_seconds: float | None = None
    max_latency_seconds: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def choose_delivery(config: Config, *, backend: str | None = None,
                    requested: str = "interactive",
                    deadline_seconds: float | None = None,
                    priority: int | None = None,
                    multi_turn: bool = False,
                    env: dict[str, str] | None = None) -> DeliveryDecision:
    """Pick between the synchronous Messages API and a Message Batch.

    ``requested`` is what the handoff asked for. ``interactive`` and ``batch``
    are honoured as written (``batch`` on a backend without the API is an
    error, never a silent fallback). ``auto`` chooses:

    * interactive when the backend has no batch endpoint, when the work is a
      multi-turn tool loop (each turn depends on the last, so there is nothing
      to batch), when the task's dispatch priority is at or above
      ``urgent_priority``, or when the stated deadline does not leave
      ``deadline_slack_seconds`` beyond the expected batch latency;
    * batch otherwise -- including when no deadline is stated at all, because
      a request nobody is waiting on is exactly what the half-price lane is
      for.
    """
    env = os.environ if env is None else env
    if requested not in DELIVERY_MODES:
        raise BatchError(f"unknown delivery mode {requested!r}; "
                         f"one of {', '.join(DELIVERY_MODES)}")
    backend_name = backend or config.default_backend(env)
    config.backend(backend_name)
    if deadline_seconds is not None and deadline_seconds < 0:
        raise BatchError("deadline_seconds must be non-negative")
    if priority is not None and (isinstance(priority, bool)
                                 or not isinstance(priority, int)
                                 or not 0 <= priority <= 100):
        raise BatchError("priority must be an integer 0..100")

    defaults = config.batch_defaults()
    expected = float(defaults["expected_latency_seconds"])
    maximum = float(defaults["max_latency_seconds"])
    slack = float(defaults["deadline_slack_seconds"])
    urgent = int(defaults["urgent_priority"])
    supported = config.supports_message_batches(backend_name)

    def decide(delivery: str, reason: str) -> DeliveryDecision:
        return DeliveryDecision(
            delivery=delivery, reason=reason, requested=requested,
            backend=backend_name, deadline_seconds=deadline_seconds,
            priority=priority, expected_latency_seconds=expected,
            max_latency_seconds=maximum)

    if requested == "interactive":
        return decide("interactive", "requested interactive delivery")
    if requested == "batch":
        if not supported:
            raise BatchError(
                f"backend {backend_name} does not provide the Message Batches "
                f"API; batch delivery cannot be served there and will not be "
                f"silently replaced by a synchronous call")
        if multi_turn:
            raise BatchError("a multi-turn tool loop cannot be batched: each "
                             "turn depends on the previous result")
        return decide("batch", "requested batch delivery")

    # requested == "auto"
    if not supported:
        return decide("interactive",
                      f"backend {backend_name} has no Message Batches API")
    if multi_turn:
        return decide("interactive", "multi-turn tool loop; nothing to batch")
    if priority is not None and priority >= urgent:
        return decide("interactive",
                      f"dispatch priority {priority} >= urgent_priority {urgent}")
    if deadline_seconds is None:
        return decide("batch", "no deadline stated; nobody is waiting on this "
                               "result, so it takes the half-price lane")
    if deadline_seconds < expected + slack:
        return decide("interactive",
                      f"deadline {deadline_seconds:.0f}s is inside the expected "
                      f"batch latency {expected:.0f}s + {slack:.0f}s slack")
    note = ""
    if deadline_seconds < maximum:
        note = (f"; a batch may take up to {maximum:.0f}s, so `batch escalate` "
                f"if it has not ended by the deadline")
    return decide("batch", f"deadline {deadline_seconds:.0f}s leaves room beyond "
                           f"the expected batch latency {expected:.0f}s{note}")


def delivery_from_handoff(config: Config, handoff: dict[str, Any], *,
                          backend: str | None = None,
                          priority: int | None = None,
                          env: dict[str, str] | None = None) -> DeliveryDecision:
    """Route straight from a handoff's ``inference`` block.

    ``delivery`` and ``deadline_seconds`` are optional on the block; a handoff
    written before they existed is interactive, exactly as it always was.
    """
    body = handoff.get("handoff", handoff)
    inference = body.get("inference") or {}
    requested = inference.get("delivery") or "interactive"
    deadline = inference.get("deadline_seconds")
    if deadline is not None and (isinstance(deadline, bool)
                                 or not isinstance(deadline, (int, float))):
        raise BatchError(
            f"handoff {body.get('id', '<unknown>')} inference.deadline_seconds "
            f"must be a number of seconds, got {deadline!r}")
    return choose_delivery(config, backend=backend, requested=requested,
                           deadline_seconds=deadline, priority=priority, env=env)


# --------------------------------------------------------------------------
# request construction
# --------------------------------------------------------------------------
@dataclass
class BatchEntry:
    """One request of a batch: the wire body plus what the registry records."""
    custom_id: str
    params: dict[str, Any]
    meta: dict[str, Any] = field(default_factory=dict)

    def to_wire(self) -> dict[str, Any]:
        return {"custom_id": self.custom_id, "params": self.params}


def validate_custom_id(custom_id: str) -> str:
    if not isinstance(custom_id, str) or not CUSTOM_ID_PATTERN.match(custom_id):
        raise BatchError(
            f"custom_id {custom_id!r} must match {CUSTOM_ID_PATTERN.pattern}: "
            f"1 to 64 characters from [a-zA-Z0-9_-]")
    return custom_id


def custom_id_for(task_id: str | None, index: int, label: str | None = None) -> str:
    """A valid, self-describing custom_id: ``<task>-<label|index>``.

    Task ids are the natural join key between a batch result and the ledger,
    and ``TASK-20260724-221`` already satisfies the character set; anything
    else is normalised and the whole thing truncated to the 64-character cap.
    """
    stem = re.sub(r"[^a-zA-Z0-9_-]", "-", task_id or "req")
    suffix = re.sub(r"[^a-zA-Z0-9_-]", "-", label) if label else f"{index:04d}"
    candidate = f"{stem}-{suffix}"
    if len(candidate) > 64:
        digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()[:8]
        candidate = f"{candidate[:55]}-{digest}"
    return validate_custom_id(candidate)


def build_batch_entry(config: Config, resolution: Resolution, *,
                      custom_id: str, system: str | None,
                      messages: list[Message], max_tokens: int | None = None,
                      tools: list[Tool] | None = None,
                      cache_policy: PromptCachePolicy | None = None,
                      task_id: str | None = None, role: str | None = None,
                      note: str | None = None,
                      env: dict[str, str] | None = None) -> BatchEntry:
    """Build one batch request through the ordinary request builder.

    The body is exactly what the synchronous call would have sent -- same
    model, effort, thinking budget, and provider knobs -- so the two delivery
    modes cannot drift apart. Prompt caching defaults to the one-hour TTL the
    provider recommends for batches, since a batch routinely outlives a
    five-minute cache entry.
    """
    env = os.environ if env is None else env
    validate_custom_id(custom_id)
    if not config.supports_message_batches(resolution.backend):
        raise BatchError(
            f"backend {resolution.backend} does not provide the Message "
            f"Batches API")
    _, _, body = build_request(
        config, resolution, system=system, messages=messages,
        max_tokens=max_tokens, tools=tools, env=env)
    policy = cache_policy or PromptCachePolicy(anthropic_ttl="1h")
    body = apply_prompt_cache(
        body, wire=resolution.wire, model=resolution.resolved_model_id,
        system=system, tools=tools, policy=policy)
    _check_batchable(body, custom_id)
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, default=str).encode("utf-8")).hexdigest()
    meta = {
        "custom_id": custom_id,
        "task_id": task_id,
        "role": role,
        "note": note,
        "requested_policy": resolution.requested_policy,
        "canonical_policy": resolution.policy,
        "backend": resolution.backend,
        "resolved_model_id": resolution.resolved_model_id,
        "model_verified": resolution.verified_model,
        "requested_reasoning_effort": resolution.requested_reasoning_effort,
        "reasoning_effort": resolution.reasoning_effort,
        "fallback_used": resolution.fallback_used,
        "fallback_reason": resolution.fallback_reason,
        "degraded_requirements": list(resolution.degraded_requirements),
        "independent_session": resolution.independent_session,
        "adapter_version": resolution.adapter_version,
        "config_digest": resolution.config_digest,
        "max_tokens": body.get("max_tokens"),
        "body_sha256": digest,
    }
    return BatchEntry(custom_id=custom_id, params=body, meta=meta)


def _check_batchable(body: dict[str, Any], custom_id: str) -> None:
    for name in UNBATCHABLE_FIELDS:
        if name in body:
            raise BatchError(
                f"request {custom_id}: `{name}` is not accepted by the batch "
                f"endpoint")
    if not isinstance(body.get("max_tokens"), int) or body["max_tokens"] < 1:
        raise BatchError(
            f"request {custom_id}: a batched request needs max_tokens >= 1")


def check_entries(entries: list[BatchEntry]) -> int:
    """Uniqueness and size limits, before any byte leaves the machine."""
    if not entries:
        raise BatchError("a batch needs at least one request")
    if len(entries) > MAX_REQUESTS_PER_BATCH:
        raise BatchError(
            f"{len(entries)} requests exceed the {MAX_REQUESTS_PER_BATCH} per "
            f"batch limit; split the submission")
    seen: set[str] = set()
    for entry in entries:
        validate_custom_id(entry.custom_id)
        if entry.custom_id in seen:
            raise BatchError(f"duplicate custom_id {entry.custom_id!r} in one batch")
        seen.add(entry.custom_id)
        _check_batchable(entry.params, entry.custom_id)
    size = len(json.dumps({"requests": [e.to_wire() for e in entries]},
                          default=str).encode("utf-8"))
    if size > MAX_BATCH_BYTES:
        raise BatchError(f"batch body is {size} bytes, over the "
                         f"{MAX_BATCH_BYTES} byte limit; split the submission")
    return size


# --------------------------------------------------------------------------
# wire objects
# --------------------------------------------------------------------------
@dataclass
class MessageBatch:
    id: str
    processing_status: str
    request_counts: dict[str, int]
    created_at: str | None = None
    expires_at: str | None = None
    ended_at: str | None = None
    cancel_initiated_at: str | None = None
    archived_at: str | None = None
    results_url: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "MessageBatch":
        if not isinstance(payload, dict) or not payload.get("id"):
            raise BatchError(f"batch response carries no id: {str(payload)[:300]}")
        status = payload.get("processing_status")
        if status not in PROCESSING_STATUSES:
            raise BatchError(
                f"batch {payload['id']} reports unknown processing_status "
                f"{status!r}; known: {', '.join(PROCESSING_STATUSES)}")
        counts = {k: int(v) for k, v in (payload.get("request_counts") or {}).items()}
        return cls(
            id=str(payload["id"]), processing_status=status, request_counts=counts,
            created_at=payload.get("created_at"), expires_at=payload.get("expires_at"),
            ended_at=payload.get("ended_at"),
            cancel_initiated_at=payload.get("cancel_initiated_at"),
            archived_at=payload.get("archived_at"),
            results_url=payload.get("results_url"), raw=payload)

    @property
    def ended(self) -> bool:
        return self.processing_status == "ended"

    @property
    def total(self) -> int:
        return sum(self.request_counts.values())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("raw", None)
        return data

    def summary(self) -> str:
        counts = ", ".join(f"{k}={v}" for k, v in sorted(self.request_counts.items()))
        line = f"{self.id}  {self.processing_status}  [{counts}]"
        if self.expires_at and not self.ended:
            line += f"  expires {self.expires_at}"
        if self.ended_at:
            line += f"  ended {self.ended_at}"
        return line


@dataclass
class BatchResult:
    """One line of the results file, parsed."""
    custom_id: str
    type: str                               # succeeded | errored | canceled | expired
    completion: Completion | None = None
    error: dict[str, Any] | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_line(cls, line: dict[str, Any], wire: str) -> "BatchResult":
        custom_id = line.get("custom_id")
        result = line.get("result") or {}
        kind = result.get("type")
        if not custom_id or kind not in RESULT_TYPES:
            raise BatchError(f"malformed batch result line: {str(line)[:300]}")
        completion = None
        error = None
        if kind == "succeeded":
            message = result.get("message") or {}
            completion = parse_response(wire, message)
            completion.usage = normalize_usage(wire, message)
        elif kind == "errored":
            error = result.get("error") or {}
        return cls(custom_id=str(custom_id), type=kind, completion=completion,
                   error=error, raw=line)

    @property
    def retryable(self) -> bool:
        """Expired and server-side errors may be resubmitted; a validation
        error means the request itself must change first."""
        if self.type == "expired":
            return True
        if self.type == "errored":
            inner = (self.error or {}).get("error") or self.error or {}
            return inner.get("type") not in ("invalid_request_error", "invalid_request")
        return False


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------
def _endpoint(config: Config, backend_name: str, env: dict[str, str]
              ) -> tuple[str, dict[str, str], dict[str, Any]]:
    """(base_url, headers, wire protocol) for a batch-capable backend."""
    if not config.supports_message_batches(backend_name):
        raise BatchError(
            f"backend {backend_name} does not provide the Message Batches API; "
            f"backends that do: {', '.join(_batch_backends(config)) or 'none'}")
    backend = config.backend(backend_name)
    protocol = config.wire_protocol(backend["wire"])
    base_url = config.base_url(backend_name, env)
    api_key = env.get(backend["api_key_env"], "")
    if not api_key and not backend.get("api_key_optional"):
        raise BatchError(
            f"backend {backend_name} needs credentials in "
            f"${backend['api_key_env']}, which is unset")
    headers = {"content-type": "application/json"}
    headers.update({k: str(v) for k, v in (protocol.get("static_headers") or {}).items()})
    headers.update(auth_headers(protocol, backend, api_key))
    return base_url, headers, protocol


def _batch_backends(config: Config) -> list[str]:
    return sorted(name for name in config.backend_table
                  if config.supports_message_batches(name))


def _call(config: Config, method: str, url: str, headers: dict[str, str],
          body: dict[str, Any] | None, *, timeout: float, max_retries: int,
          opener: Callable[..., Any] | None,
          sleep: Callable[[float], None]) -> bytes:
    """One guarded HTTP call with the transport's retry discipline."""
    config.assert_inference_target_allowed(
        url, (body or {}).get("model"), context="outbound batch request")
    opener = opener or _default_opener(config)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    last_error: Exception | None = None
    for attempt in range(max(1, max_retries)):
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with opener(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as exc:               # noqa: PERF203
            detail = exc.read().decode("utf-8", "replace")[:2000]
            last_error = BatchError(f"HTTP {exc.code} from {method} {url}: {detail}")
            if exc.code not in RETRY_STATUS:
                raise last_error from exc
        except urllib.error.URLError as exc:
            last_error = BatchError(f"network error contacting {url}: {exc.reason}")
        if attempt < max_retries - 1:
            sleep(2.0 ** attempt)
    raise last_error or BatchError(f"{method} {url} failed")


def _call_json(config: Config, *args: Any, **kwargs: Any) -> dict[str, Any]:
    raw = _call(config, *args, **kwargs)
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BatchError(f"batch endpoint returned non-JSON: {raw[:200]!r}") from exc
    if not isinstance(payload, dict):
        raise BatchError(f"batch endpoint returned {type(payload).__name__}, not an object")
    return payload


def _timeouts(config: Config) -> tuple[float, int]:
    defaults = config.providers.get("defaults", {})
    return (float(defaults.get("request_timeout_seconds", 600)),
            int(defaults.get("max_retries", 3)))


def _batches_url(base_url: str, protocol: dict[str, Any], *parts: str) -> str:
    url = base_url + protocol["batches_path"]
    for part in parts:
        url += "/" + part
    return url


def _check_batch_id(batch_id: str) -> str:
    if not isinstance(batch_id, str) or not re.match(r"^[A-Za-z0-9_-]{1,128}$", batch_id):
        raise BatchError(f"malformed batch id {batch_id!r}")
    return batch_id


# --------------------------------------------------------------------------
# registry (write-once, one directory per provider batch id)
# --------------------------------------------------------------------------
def registry_dir(config: Config, env: dict[str, str] | None = None,
                 override: str | Path | None = None) -> Path:
    """Where submissions, results, and escalations are recorded.

    Keyed by the provider's batch id, which is globally unique, so N
    concurrent worktrees never write the same path; and write-once per file,
    so a record is never edited after the fact.
    """
    env = os.environ if env is None else env
    if override:
        return Path(override)
    if env.get(BATCH_DIR_ENV):
        return Path(env[BATCH_DIR_ENV])
    configured = Path(str(config.batch_defaults()["registry_dir"]))
    return configured if configured.is_absolute() else REPO_ROOT / configured


def _write_once(path: Path, data: Any, *, jsonl: bool = False) -> Path:
    if path.exists():
        raise FileExistsError(
            f"{path} already exists; batch records are write-once -- a "
            f"correction is a new file, never an edit")
    path.parent.mkdir(parents=True, exist_ok=True)
    if jsonl:
        text = "".join(json.dumps(line, sort_keys=True, default=str) + "\n"
                       for line in data)
    else:
        text = json.dumps(data, indent=2, sort_keys=True, default=str) + "\n"
    path.write_text(text, encoding="utf-8")
    return path


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if raw:
            lines.append(json.loads(raw))
    return lines


def batch_dir(registry: Path, batch_id: str) -> Path:
    return registry / _check_batch_id(batch_id)


def load_submission(registry: Path, batch_id: str) -> dict[str, Any] | None:
    path = batch_dir(registry, batch_id) / "submission.json"
    return _read_json(path) if path.exists() else None


def load_requests(registry: Path, batch_id: str) -> dict[str, BatchEntry]:
    path = batch_dir(registry, batch_id) / "requests.jsonl"
    if not path.exists():
        return {}
    entries = {}
    for line in _read_jsonl(path):
        entry = BatchEntry(custom_id=line["custom_id"], params=line["params"],
                           meta=line.get("meta") or {})
        entries[entry.custom_id] = entry
    return entries


def local_state(registry: Path, batch_id: str) -> dict[str, Any]:
    """What this checkout already knows about a batch, without the network."""
    directory = batch_dir(registry, batch_id)
    escalations = sorted(p.stem for p in (directory / "escalations").glob("*.json"))
    return {
        "id": batch_id,
        "known": (directory / "submission.json").exists(),
        "collected": (directory / "collected.json").exists(),
        "cancelled": (directory / "cancel.json").exists(),
        "escalated": escalations,
        "directory": str(directory),
    }


def local_batches(registry: Path) -> list[dict[str, Any]]:
    """Every batch this checkout has a submission record for, newest last."""
    if not registry.exists():
        return []
    rows = []
    for directory in sorted(registry.iterdir()):
        if not (directory / "submission.json").is_file():
            continue
        submission = _read_json(directory / "submission.json")
        state = local_state(registry, directory.name)
        rows.append({**state,
                     "backend": submission.get("backend"),
                     "submitted_at": submission.get("submitted_at"),
                     "expires_at": (submission.get("batch") or {}).get("expires_at"),
                     "task_id": submission.get("task_id"),
                     "note": submission.get("note"),
                     "requests": len(submission.get("requests") or [])})
    rows.sort(key=lambda r: r.get("submitted_at") or "")
    return rows


# --------------------------------------------------------------------------
# operations
# --------------------------------------------------------------------------
def preflight(config: Config, backend_name: str, entry: BatchEntry, *,
              env: dict[str, str] | None = None,
              opener: Callable[..., Any] | None = None,
              sleep: Callable[[float], None] = time.sleep) -> dict[str, Any]:
    """Validate one request's shape through ``count_tokens`` before batching.

    The batch endpoint validates asynchronously and reports a malformed
    request only when the whole batch has ended -- up to a day later.
    Counting tokens for one representative request costs nothing and catches
    a bad model id, thinking configuration, or message shape now. It is a
    shape check, not a guarantee: parameters outside ``COUNT_TOKENS_FIELDS``
    are not exercised.
    """
    env = os.environ if env is None else env
    base_url, headers, protocol = _endpoint(config, backend_name, env)
    path = protocol.get("count_tokens_path")
    if not path:
        raise BatchError(f"wire protocol {config.backend(backend_name)['wire']} "
                         f"declares no count_tokens_path; cannot preflight")
    url = base_url + path
    config.assert_inference_target_allowed(url, context="preflight endpoint")
    body = {k: v for k, v in entry.params.items() if k in COUNT_TOKENS_FIELDS}
    timeout, retries = _timeouts(config)
    payload = _call_json(config, "POST", url, headers, body, timeout=timeout,
                         max_retries=retries, opener=opener, sleep=sleep)
    return {"custom_id": entry.custom_id,
            "input_tokens": payload.get("input_tokens"), "raw": payload}


def submit(config: Config, backend_name: str, entries: list[BatchEntry], *,
           env: dict[str, str] | None = None,
           opener: Callable[..., Any] | None = None,
           sleep: Callable[[float], None] = time.sleep,
           registry: Path | None = None,
           task_id: str | None = None, note: str | None = None,
           decision: DeliveryDecision | None = None,
           preflight_result: dict[str, Any] | None = None) -> MessageBatch:
    """Create a batch and record the submission write-once.

    The registry record is what makes the batch collectable from any later
    session: it maps each ``custom_id`` back to its task, role, policy, and
    resolved model, and keeps the exact request bodies so an escalation can
    re-run one verbatim.
    """
    env = os.environ if env is None else env
    check_entries(entries)
    base_url, headers, protocol = _endpoint(config, backend_name, env)
    url = _batches_url(base_url, protocol)
    config.assert_inference_target_allowed(url, context="batch submission endpoint")
    for entry in entries:
        config.assert_inference_target_allowed(
            entry.params.get("model"), context=f"batch request {entry.custom_id} model")
    timeout, retries = _timeouts(config)
    payload = _call_json(
        config, "POST", url, headers, {"requests": [e.to_wire() for e in entries]},
        timeout=timeout, max_retries=retries, opener=opener, sleep=sleep)
    batch = MessageBatch.from_payload(payload)

    registry = registry or registry_dir(config, env)
    directory = batch_dir(registry, batch.id)
    _write_once(directory / "submission.json", {
        "schema_version": "1.0",
        "batch": batch.to_dict(),
        "backend": backend_name,
        "base_url": base_url,
        "submitted_at": _now(),
        "task_id": task_id,
        "note": note,
        "delivery": decision.to_dict() if decision else None,
        "preflight": preflight_result,
        "config_digest": config.digest,
        "requests": [e.meta or {"custom_id": e.custom_id} for e in entries],
    })
    _write_once(directory / "requests.jsonl",
                [{"custom_id": e.custom_id, "params": e.params, "meta": e.meta}
                 for e in entries], jsonl=True)
    return batch


def retrieve(config: Config, backend_name: str, batch_id: str, *,
             env: dict[str, str] | None = None,
             opener: Callable[..., Any] | None = None,
             sleep: Callable[[float], None] = time.sleep) -> MessageBatch:
    env = os.environ if env is None else env
    base_url, headers, protocol = _endpoint(config, backend_name, env)
    url = _batches_url(base_url, protocol, _check_batch_id(batch_id))
    timeout, retries = _timeouts(config)
    payload = _call_json(config, "GET", url, headers, None, timeout=timeout,
                         max_retries=retries, opener=opener, sleep=sleep)
    return MessageBatch.from_payload(payload)


def list_batches(config: Config, backend_name: str, *, limit: int = 20,
                 after_id: str | None = None, before_id: str | None = None,
                 env: dict[str, str] | None = None,
                 opener: Callable[..., Any] | None = None,
                 sleep: Callable[[float], None] = time.sleep
                 ) -> tuple[list[MessageBatch], dict[str, Any]]:
    """One page of the workspace's batches plus the pagination cursor."""
    env = os.environ if env is None else env
    base_url, headers, protocol = _endpoint(config, backend_name, env)
    query = [f"limit={int(limit)}"]
    if after_id:
        query.append(f"after_id={_check_batch_id(after_id)}")
    if before_id:
        query.append(f"before_id={_check_batch_id(before_id)}")
    url = _batches_url(base_url, protocol) + "?" + "&".join(query)
    timeout, retries = _timeouts(config)
    payload = _call_json(config, "GET", url, headers, None, timeout=timeout,
                         max_retries=retries, opener=opener, sleep=sleep)
    batches = [MessageBatch.from_payload(item) for item in payload.get("data") or []]
    page = {"has_more": bool(payload.get("has_more")),
            "first_id": payload.get("first_id"), "last_id": payload.get("last_id")}
    return batches, page


def cancel(config: Config, backend_name: str, batch_id: str, *,
           env: dict[str, str] | None = None,
           opener: Callable[..., Any] | None = None,
           sleep: Callable[[float], None] = time.sleep,
           registry: Path | None = None, reason: str | None = None) -> MessageBatch:
    """Cancel a batch. Requests already processed keep their results."""
    env = os.environ if env is None else env
    base_url, headers, protocol = _endpoint(config, backend_name, env)
    url = _batches_url(base_url, protocol, _check_batch_id(batch_id), "cancel")
    timeout, retries = _timeouts(config)
    payload = _call_json(config, "POST", url, headers, {}, timeout=timeout,
                         max_retries=retries, opener=opener, sleep=sleep)
    batch = MessageBatch.from_payload(payload)
    registry = registry or registry_dir(config, env)
    record = batch_dir(registry, batch.id) / "cancel.json"
    if not record.exists():
        _write_once(record, {"batch": batch.to_dict(), "cancelled_at": _now(),
                             "reason": reason})
    return batch


def delete(config: Config, backend_name: str, batch_id: str, *,
           env: dict[str, str] | None = None,
           opener: Callable[..., Any] | None = None,
           sleep: Callable[[float], None] = time.sleep) -> dict[str, Any]:
    """Delete an ended batch from the provider. The local registry is kept:
    it is the record of what was asked and answered."""
    env = os.environ if env is None else env
    base_url, headers, protocol = _endpoint(config, backend_name, env)
    url = _batches_url(base_url, protocol, _check_batch_id(batch_id))
    timeout, retries = _timeouts(config)
    return _call_json(config, "DELETE", url, headers, None, timeout=timeout,
                      max_retries=retries, opener=opener, sleep=sleep)


def wait(config: Config, backend_name: str, batch_id: str, *,
         timeout_seconds: float, poll_interval: float | None = None,
         env: dict[str, str] | None = None,
         opener: Callable[..., Any] | None = None,
         sleep: Callable[[float], None] = time.sleep,
         clock: Callable[[], float] = time.monotonic,
         on_poll: Callable[[MessageBatch], None] | None = None) -> MessageBatch:
    """Poll until the batch ends or the caller's wall-clock budget runs out.

    A budget stop returns the last status rather than raising: the batch is
    still running and still collectable later, which is the whole point.
    """
    interval = float(poll_interval if poll_interval is not None
                     else config.batch_defaults()["poll_interval_seconds"])
    deadline = clock() + float(timeout_seconds)
    while True:
        batch = retrieve(config, backend_name, batch_id, env=env, opener=opener,
                         sleep=sleep)
        if on_poll:
            on_poll(batch)
        if batch.ended or clock() >= deadline:
            return batch
        sleep(max(1.0, min(interval, deadline - clock())))


def results(config: Config, backend_name: str, batch: MessageBatch, *,
            env: dict[str, str] | None = None,
            opener: Callable[..., Any] | None = None,
            sleep: Callable[[float], None] = time.sleep
            ) -> Iterator[tuple[dict[str, Any], BatchResult]]:
    """Stream (raw line, parsed result) pairs for an ended batch.

    The results path is composed from the configured base URL rather than
    taken from the response: a ``results_url`` pointing anywhere but the
    backend we submitted to is refused, so the cost-policy guard on the
    endpoint cannot be bypassed by a redirecting gateway.
    """
    env = os.environ if env is None else env
    if not batch.ended:
        raise BatchError(f"batch {batch.id} is {batch.processing_status}; results "
                         f"are available only once it has ended")
    base_url, headers, protocol = _endpoint(config, backend_name, env)
    url = _batches_url(base_url, protocol, _check_batch_id(batch.id), "results")
    if batch.results_url:
        from urllib.parse import urlsplit
        ours, theirs = urlsplit(base_url), urlsplit(batch.results_url)
        if (ours.scheme, ours.netloc) != (theirs.scheme, theirs.netloc):
            raise BatchError(
                f"batch {batch.id} results_url {batch.results_url!r} is not on "
                f"the configured backend {base_url}; refusing to follow it")
    timeout, retries = _timeouts(config)
    raw = _call(config, "GET", url, headers, None, timeout=timeout,
                max_retries=retries, opener=opener, sleep=sleep)
    wire = config.backend(backend_name)["wire"]
    for text in raw.decode("utf-8").splitlines():
        text = text.strip()
        if not text:
            continue
        try:
            line = json.loads(text)
        except json.JSONDecodeError as exc:
            raise BatchError(f"malformed results line: {text[:200]}") from exc
        yield line, BatchResult.from_line(line, wire)


@dataclass
class Collected:
    batch: MessageBatch
    results: dict[str, BatchResult]
    receipts: dict[str, dict[str, Any]]
    from_disk: bool
    superseded: list[str] = field(default_factory=list)

    def summary(self) -> str:
        kinds: dict[str, int] = {}
        for result in self.results.values():
            kinds[result.type] = kinds.get(result.type, 0) + 1
        counts = ", ".join(f"{k}={v}" for k, v in sorted(kinds.items()))
        source = "from disk" if self.from_disk else "downloaded"
        line = f"{self.batch.id}  {len(self.results)} results ({counts})  {source}"
        if self.superseded:
            line += f"  superseded by escalation: {', '.join(self.superseded)}"
        return line


def result_receipt(meta: dict[str, Any], result: BatchResult, batch_id: str, *,
                   collected_at: str, superseded_by_escalation: bool = False
                   ) -> dict[str, Any]:
    """The inference receipt for one batched request.

    Same fields as a synchronous receipt's ``response`` block, so a manifest
    built from either is read the same way, plus the batch provenance.
    """
    completion = result.completion
    receipt: dict[str, Any] = {
        "inference_receipt": {
            "task_id": meta.get("task_id"),
            "role": meta.get("role"),
            "recorded_at": collected_at,
            "resolution": {k: v for k, v in meta.items()
                           if k not in ("custom_id", "task_id", "role", "note",
                                        "max_tokens", "body_sha256")},
            "delivery": {
                "mode": "batch",
                "batch_id": batch_id,
                "custom_id": result.custom_id,
                "result_type": result.type,
                "body_sha256": meta.get("body_sha256"),
                "superseded_by_escalation": superseded_by_escalation,
            },
        }
    }
    if completion is not None:
        receipt["inference_receipt"]["response"] = {
            "reported_model": completion.model,
            "stop_reason": completion.stop_reason,
            "usage": completion.usage,
            "latency_seconds": None,            # asynchronous: not a latency
            "output_characters": len(completion.text),
            "tool_calls": [call.name for call in completion.tool_calls],
            "model_matches_resolution": (
                completion.model == meta.get("resolved_model_id")
                if completion.model and meta.get("resolved_model_id") else None),
        }
    elif result.error is not None:
        receipt["inference_receipt"]["error"] = result.error
    return receipt


def collect(config: Config, backend_name: str, batch_id: str, *,
            env: dict[str, str] | None = None,
            opener: Callable[..., Any] | None = None,
            sleep: Callable[[float], None] = time.sleep,
            registry: Path | None = None) -> Collected:
    """Fetch (once) and record the results of an ended batch.

    Idempotent: the first call downloads ``results.jsonl`` and writes
    ``collected.json``; every later call, in any session, answers from disk.
    A request that was escalated while the batch ran is still recorded, with
    its batch copy marked ``superseded_by_escalation`` so no reader can take
    the two answers for one question as independent.
    """
    env = os.environ if env is None else env
    registry = registry or registry_dir(config, env)
    directory = batch_dir(registry, batch_id)
    entries = load_requests(registry, batch_id)
    wire = config.backend(backend_name)["wire"]
    escalated = {p.stem for p in (directory / "escalations").glob("*.json")}

    results_path = directory / "results.jsonl"
    collected_path = directory / "collected.json"
    if results_path.exists() and collected_path.exists():
        recorded = _read_json(collected_path)
        batch = MessageBatch.from_payload(recorded["batch"] | {"type": "message_batch"})
        parsed = {line["custom_id"]: BatchResult.from_line(line, wire)
                  for line in _read_jsonl(results_path)}
        return Collected(batch=batch, results=parsed,
                         receipts=recorded.get("receipts") or {}, from_disk=True,
                         superseded=sorted(set(parsed) & escalated))

    batch = retrieve(config, backend_name, batch_id, env=env, opener=opener, sleep=sleep)
    if not batch.ended:
        raise BatchError(
            f"batch {batch.id} is {batch.processing_status} "
            f"({batch.request_counts.get('processing', 0)} still processing); "
            f"`batch wait` or come back later -- or `batch escalate` the "
            f"requests you need now")
    collected_at = _now()
    lines: list[dict[str, Any]] = []
    parsed: dict[str, BatchResult] = {}
    receipts: dict[str, dict[str, Any]] = {}
    for line, result in results(config, backend_name, batch, env=env,
                                opener=opener, sleep=sleep):
        lines.append(line)
        parsed[result.custom_id] = result
        meta = entries[result.custom_id].meta if result.custom_id in entries else {}
        receipts[result.custom_id] = result_receipt(
            meta, result, batch.id, collected_at=collected_at,
            superseded_by_escalation=result.custom_id in escalated)
    _write_once(results_path, lines, jsonl=True)
    _write_once(collected_path, {
        "schema_version": "1.0",
        "batch": batch.to_dict(),
        "collected_at": collected_at,
        "result_types": {cid: r.type for cid, r in sorted(parsed.items())},
        "missing": sorted(set(entries) - set(parsed)),
        "unknown": sorted(set(parsed) - set(entries)),
        "receipts": receipts,
    })
    return Collected(batch=batch, results=parsed, receipts=receipts, from_disk=False,
                     superseded=sorted(set(parsed) & escalated))


@dataclass
class Escalation:
    custom_id: str
    completion: Completion
    receipt: dict[str, Any]
    path: Path


def escalate(config: Config, backend_name: str, batch_id: str, *,
             custom_ids: list[str] | None = None,
             env: dict[str, str] | None = None,
             opener: Callable[..., Any] | None = None,
             sleep: Callable[[float], None] = time.sleep,
             registry: Path | None = None,
             cancel_remaining: bool = False,
             reason: str | None = None
             ) -> tuple[list[Escalation], MessageBatch]:
    """Run still-pending batched requests synchronously, now.

    For a result that became urgent after submission. The stored request body
    is sent verbatim to the synchronous endpoint, the answer is recorded as a
    write-once escalation, and the batch is cancelled when nothing in it is
    still wanted (everything escalated, or ``cancel_remaining``), so the
    second payment is bounded and recorded. If the batch has already ended
    there is nothing to escalate: collect it instead.
    """
    env = os.environ if env is None else env
    registry = registry or registry_dir(config, env)
    directory = batch_dir(registry, batch_id)
    entries = load_requests(registry, batch_id)
    if not entries:
        raise BatchError(
            f"no requests.jsonl for {batch_id} under {registry}; an escalation "
            f"re-runs the recorded request body and there is none")
    batch = retrieve(config, backend_name, batch_id, env=env, opener=opener, sleep=sleep)
    if batch.ended:
        raise BatchError(f"batch {batch.id} has already ended; `batch collect` it "
                         f"instead of paying for a second run")

    wanted = list(custom_ids) if custom_ids else sorted(entries)
    unknown = [c for c in wanted if c not in entries]
    if unknown:
        raise BatchError(f"custom_id(s) not in batch {batch_id}: {', '.join(unknown)}")
    already = {p.stem for p in (directory / "escalations").glob("*.json")}

    base_url, headers, protocol = _endpoint(config, backend_name, env)
    url = base_url + protocol["path"]
    config.assert_inference_target_allowed(url, context="escalation endpoint")
    timeout, retries = _timeouts(config)
    wire = config.backend(backend_name)["wire"]
    done: list[Escalation] = []
    for custom_id in wanted:
        if custom_id in already:
            continue
        entry = entries[custom_id]
        started = time.time()
        payload = _call_json(config, "POST", url, headers, entry.params,
                             timeout=timeout, max_retries=retries,
                             opener=opener, sleep=sleep)
        completion = parse_response(wire, payload)
        completion.usage = normalize_usage(wire, payload)
        completion.latency_seconds = round(time.time() - started, 3)
        recorded_at = _now()
        receipt = {
            "inference_receipt": {
                "task_id": entry.meta.get("task_id"),
                "role": entry.meta.get("role"),
                "recorded_at": recorded_at,
                "resolution": {k: v for k, v in entry.meta.items()
                               if k not in ("custom_id", "task_id", "role", "note",
                                            "max_tokens", "body_sha256")},
                "delivery": {
                    "mode": "interactive",
                    "escalated_from_batch": batch_id,
                    "custom_id": custom_id,
                    "body_sha256": entry.meta.get("body_sha256"),
                    "reason": reason,
                },
                "response": {
                    "reported_model": completion.model,
                    "stop_reason": completion.stop_reason,
                    "usage": completion.usage,
                    "latency_seconds": completion.latency_seconds,
                    "output_characters": len(completion.text),
                    "tool_calls": [call.name for call in completion.tool_calls],
                    "model_matches_resolution": (
                        completion.model == entry.meta.get("resolved_model_id")
                        if completion.model and entry.meta.get("resolved_model_id")
                        else None),
                },
            }
        }
        path = _write_once(directory / "escalations" / f"{custom_id}.json", {
            **receipt, "completion": {"text": completion.text,
                                      "tool_calls": [asdict(c) for c in completion.tool_calls],
                                      "raw": payload}})
        done.append(Escalation(custom_id=custom_id, completion=completion,
                               receipt=receipt, path=path))
        already.add(custom_id)

    if cancel_remaining or already >= set(entries):
        why = reason or ("every request escalated" if already >= set(entries)
                         else "cancel_remaining requested")
        batch = cancel(config, backend_name, batch_id, env=env, opener=opener,
                       sleep=sleep, registry=registry, reason=why)
    return done, batch


def escalation_completion(registry: Path, batch_id: str, custom_id: str
                          ) -> dict[str, Any] | None:
    path = batch_dir(registry, batch_id) / "escalations" / f"{custom_id}.json"
    return _read_json(path) if path.exists() else None
