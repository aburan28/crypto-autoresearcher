"""Message Batches: routing, submission, registry, collection, escalation.

Every test runs against an in-memory fake of the batch endpoints; no test
touches the network. The properties guarded are the research contract's: a
batched request is built by the same resolver and request builder as a
synchronous one, every record is write-once, a result is joinable back to its
task from any session, an urgent escalation never leaves two unmarked answers
to one question, and the router never silently swaps the lane a handoff asked
for.
"""
from __future__ import annotations

import io
import json
import sys
import urllib.error
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
import yaml

from orchestration import adapter
from orchestration.adapter import batch as batch_module
from orchestration.adapter import cli as cli_module
from orchestration.adapter import config as config_module
from orchestration.adapter import manifest as manifest_module
from orchestration.adapter import transport as transport_module

REPO = Path(__file__).resolve().parents[1]
ENV = {"ANTHROPIC_API_KEY": "test-key"}
BASE = "https://api.anthropic.com"


@pytest.fixture(scope="module")
def cfg():
    return adapter.load()


# --------------------------------------------------------------------------
# an in-memory Message Batches endpoint
# --------------------------------------------------------------------------
class FakeBatchServer:
    """Just enough of /v1/messages/batches to exercise every code path."""

    def __init__(self, base: str = BASE):
        self.base = base
        self.batches: dict[str, dict] = {}
        self.requests: dict[str, list[dict]] = {}
        self.results: dict[str, list[dict]] = {}
        self.calls: list[tuple[str, str, dict | None]] = []
        self.counter = 0
        self.sync_model = "claude-haiku-4-5-20251001"
        self.fail_next: tuple[int, str] | None = None

    # -- helpers -----------------------------------------------------------
    def end(self, batch_id: str, results: list[dict] | None = None) -> None:
        batch = self.batches[batch_id]
        if results is None:
            results = [self.succeeded(r["custom_id"], r["params"]["model"])
                       for r in self.requests[batch_id]]
        self.results[batch_id] = results
        counts = {"processing": 0, "succeeded": 0, "errored": 0,
                  "canceled": 0, "expired": 0}
        for line in results:
            counts[line["result"]["type"]] += 1
        batch.update({"processing_status": "ended", "request_counts": counts,
                      "ended_at": "2026-10-05T01:00:00Z",
                      "results_url": f"{self.base}/v1/messages/batches/{batch_id}/results"})

    @staticmethod
    def succeeded(custom_id: str, model: str, text: str = "answer") -> dict:
        return {"custom_id": custom_id, "result": {"type": "succeeded", "message": {
            "id": "msg_1", "type": "message", "role": "assistant", "model": model,
            "content": [{"type": "text", "text": f"{text} for {custom_id}"}],
            "stop_reason": "end_turn", "stop_sequence": None,
            "usage": {"input_tokens": 10, "output_tokens": 5,
                      "cache_read_input_tokens": 4}}}}

    @staticmethod
    def errored(custom_id: str, kind: str = "invalid_request_error") -> dict:
        return {"custom_id": custom_id, "result": {"type": "errored", "error": {
            "type": "error", "error": {"type": kind, "message": "bad request"}}}}

    @staticmethod
    def expired(custom_id: str) -> dict:
        return {"custom_id": custom_id, "result": {"type": "expired"}}

    # -- the opener ----------------------------------------------------------
    def opener(self, request, timeout=None):
        method = request.get_method()
        url = request.full_url
        body = json.loads(request.data) if request.data else None
        self.calls.append((method, url, body))
        if self.fail_next:
            code, message = self.fail_next
            self.fail_next = None
            raise urllib.error.HTTPError(url, code, message, {}, io.BytesIO(
                json.dumps({"error": {"type": "api_error", "message": message}}).encode()))
        parts = urlsplit(url)
        path = parts.path
        if path == "/v1/messages/count_tokens" and method == "POST":
            assert "max_tokens" not in body and "temperature" not in body
            return self._ok({"input_tokens": 42})
        if path == "/v1/messages" and method == "POST":
            return self._ok({
                "id": "msg_sync", "type": "message", "role": "assistant",
                "model": body["model"],
                "content": [{"type": "text", "text": "sync answer"}],
                "stop_reason": "end_turn",
                "usage": {"input_tokens": 11, "output_tokens": 6}})
        if path == "/v1/messages/batches" and method == "POST":
            self.counter += 1
            batch_id = f"msgbatch_{self.counter:03d}"
            self.requests[batch_id] = body["requests"]
            self.batches[batch_id] = {
                "id": batch_id, "type": "message_batch",
                "processing_status": "in_progress",
                "request_counts": {"processing": len(body["requests"]), "succeeded": 0,
                                   "errored": 0, "canceled": 0, "expired": 0},
                "ended_at": None, "created_at": "2026-10-05T00:00:00Z",
                "expires_at": "2026-10-06T00:00:00Z", "cancel_initiated_at": None,
                "results_url": None}
            return self._ok(self.batches[batch_id])
        if path == "/v1/messages/batches" and method == "GET":
            query = parse_qs(parts.query)
            ids = sorted(self.batches, reverse=True)
            if "after_id" in query:
                ids = [i for i in ids if i < query["after_id"][0]]
            limit = int(query.get("limit", ["20"])[0])
            page = ids[:limit]
            return self._ok({"data": [self.batches[i] for i in page],
                             "has_more": len(ids) > limit,
                             "first_id": page[0] if page else None,
                             "last_id": page[-1] if page else None})
        segments = path.split("/")
        if len(segments) >= 5 and segments[3] == "batches":
            batch_id = segments[4]
            if batch_id not in self.batches:
                raise urllib.error.HTTPError(url, 404, "not found", {},
                                             io.BytesIO(b'{"error":"not found"}'))
            batch = self.batches[batch_id]
            if len(segments) == 5 and method == "GET":
                return self._ok(batch)
            if len(segments) == 5 and method == "DELETE":
                del self.batches[batch_id]
                return self._ok({"id": batch_id, "type": "message_batch_deleted"})
            if len(segments) == 6 and segments[5] == "cancel" and method == "POST":
                if batch["processing_status"] != "ended":
                    batch["processing_status"] = "canceling"
                    batch["cancel_initiated_at"] = "2026-10-05T00:30:00Z"
                return self._ok(batch)
            if len(segments) == 6 and segments[5] == "results" and method == "GET":
                lines = self.results.get(batch_id, [])
                payload = "".join(json.dumps(line) + "\n" for line in lines)
                return io.BytesIO(payload.encode("utf-8"))
        raise AssertionError(f"unexpected call {method} {url}")

    @staticmethod
    def _ok(payload: dict) -> io.BytesIO:
        return io.BytesIO(json.dumps(payload).encode("utf-8"))


@pytest.fixture
def server():
    return FakeBatchServer()


def _entries(cfg, n=2, policy="executor-mechanical", task_id="TASK-20260724-221"):
    resolution = adapter.resolve(cfg, policy, backend="anthropic", env=ENV)
    return resolution, [adapter.build_batch_entry(
        cfg, resolution, custom_id=batch_module.custom_id_for(task_id, i),
        system="ROLE", messages=[adapter.Message("user", f"question {i}")],
        task_id=task_id, role="executor", env=ENV) for i in range(n)]


# --------------------------------------------------------------------------
# configuration
# --------------------------------------------------------------------------
def test_only_the_first_party_backend_declares_message_batches(cfg):
    assert cfg.supports_message_batches("anthropic")
    for name in ("zai-anthropic", "fireworks-anthropic", "abliteration-anthropic",
                 "openai", "local"):
        assert not cfg.supports_message_batches(name), name


def test_batch_defaults_are_loaded_and_sane(cfg):
    defaults = cfg.batch_defaults()
    assert defaults["expected_latency_seconds"] <= defaults["max_latency_seconds"]
    assert 0 <= defaults["urgent_priority"] <= 100
    assert defaults["registry_dir"] == "coordination/inference-batches"


def test_config_rejects_batch_capability_without_a_batches_path(tmp_path):
    providers = yaml.safe_load((REPO / "orchestration/providers.yaml").read_text())
    providers["backends"]["zai"]["supports_message_batches"] = True
    path = tmp_path / "providers.yaml"
    path.write_text(yaml.safe_dump(providers))
    with pytest.raises(config_module.ConfigError, match="batches_path"):
        adapter.load(providers_path=path)


def test_config_rejects_a_bedrock_batches_path(tmp_path):
    providers = yaml.safe_load((REPO / "orchestration/providers.yaml").read_text())
    providers["wire_protocols"]["anthropic_messages"]["batches_path"] = (
        "/amazon-bedrock/batches")
    path = tmp_path / "providers.yaml"
    path.write_text(yaml.safe_dump(providers))
    with pytest.raises(config_module.ConfigError, match="forbidden by cost policy"):
        adapter.load(providers_path=path)


@pytest.mark.parametrize(("field", "value", "match"), [
    ("urgent_priority", 140, "0..100"),
    ("expected_latency_seconds", -1, "non-negative"),
    ("expected_latency_seconds", 999999, "exceeds max_latency_seconds"),
])
def test_config_rejects_malformed_batch_defaults(tmp_path, field, value, match):
    providers = yaml.safe_load((REPO / "orchestration/providers.yaml").read_text())
    providers["defaults"]["batch"][field] = value
    path = tmp_path / "providers.yaml"
    path.write_text(yaml.safe_dump(providers))
    with pytest.raises(config_module.ConfigError, match=match):
        adapter.load(providers_path=path)


# --------------------------------------------------------------------------
# the router
# --------------------------------------------------------------------------
def test_interactive_is_the_default_and_is_honoured(cfg):
    decision = adapter.choose_delivery(cfg, backend="anthropic", env=ENV)
    assert decision.delivery == "interactive" and decision.requested == "interactive"


def test_explicit_batch_on_a_backend_without_the_api_is_an_error_not_a_fallback(cfg):
    with pytest.raises(batch_module.BatchError, match="will not be silently replaced"):
        adapter.choose_delivery(cfg, backend="zai-anthropic", requested="batch", env=ENV)


def test_auto_batches_when_nobody_is_waiting(cfg):
    decision = adapter.choose_delivery(cfg, backend="anthropic", requested="auto", env=ENV)
    assert decision.delivery == "batch"
    assert "no deadline" in decision.reason


def test_auto_runs_now_when_the_deadline_is_inside_the_batch_envelope(cfg):
    defaults = cfg.batch_defaults()
    tight = defaults["expected_latency_seconds"] + defaults["deadline_slack_seconds"] - 1
    decision = adapter.choose_delivery(cfg, backend="anthropic", requested="auto",
                                       deadline_seconds=tight, env=ENV)
    assert decision.delivery == "interactive"
    roomy = defaults["expected_latency_seconds"] + defaults["deadline_slack_seconds"]
    decision = adapter.choose_delivery(cfg, backend="anthropic", requested="auto",
                                       deadline_seconds=roomy, env=ENV)
    assert decision.delivery == "batch"
    assert "batch escalate" in decision.reason      # inside the 24h maximum


def test_auto_never_batches_an_urgent_task(cfg):
    decision = adapter.choose_delivery(cfg, backend="anthropic", requested="auto",
                                       deadline_seconds=10 ** 6, priority=90, env=ENV)
    assert decision.delivery == "interactive"
    assert "urgent_priority" in decision.reason


def test_auto_falls_back_to_interactive_where_batching_is_impossible(cfg):
    assert adapter.choose_delivery(cfg, backend="zai", requested="auto",
                                   env=ENV).delivery == "interactive"
    assert adapter.choose_delivery(cfg, backend="anthropic", requested="auto",
                                   multi_turn=True, env=ENV).delivery == "interactive"


def test_router_rejects_nonsense(cfg):
    with pytest.raises(batch_module.BatchError, match="unknown delivery mode"):
        adapter.choose_delivery(cfg, backend="anthropic", requested="later", env=ENV)
    with pytest.raises(batch_module.BatchError, match="non-negative"):
        adapter.choose_delivery(cfg, backend="anthropic", requested="auto",
                                deadline_seconds=-5, env=ENV)
    with pytest.raises(batch_module.BatchError, match="0..100"):
        adapter.choose_delivery(cfg, backend="anthropic", requested="auto",
                                priority=101, env=ENV)


def test_handoff_without_delivery_fields_stays_interactive(cfg):
    handoff = {"handoff": {"id": "TASK-20260724-221", "to": "executor",
                           "inference": {"policy": "executor-implementation"}}}
    decision = adapter.delivery_from_handoff(cfg, handoff, backend="anthropic", env=ENV)
    assert decision.delivery == "interactive"


def test_handoff_delivery_fields_drive_the_router(cfg):
    handoff = {"handoff": {"id": "TASK-20260724-221", "to": "executor",
                           "inference": {"policy": "executor-implementation",
                                         "delivery": "auto",
                                         "deadline_seconds": 86400}}}
    decision = adapter.delivery_from_handoff(cfg, handoff, backend="anthropic", env=ENV)
    assert decision.delivery == "batch" and decision.deadline_seconds == 86400
    bad = deepcopy(handoff)
    bad["handoff"]["inference"]["deadline_seconds"] = "soon"
    with pytest.raises(batch_module.BatchError, match="deadline_seconds"):
        adapter.delivery_from_handoff(cfg, bad, backend="anthropic", env=ENV)


# --------------------------------------------------------------------------
# request construction
# --------------------------------------------------------------------------
def test_batch_entry_is_the_synchronous_request_body(cfg):
    resolution = adapter.resolve(cfg, "executor-mechanical", backend="anthropic", env=ENV)
    messages = [adapter.Message("user", "q")]
    _, _, sync_body = adapter.build_request(
        cfg, resolution, system="ROLE", messages=messages, env=ENV)
    entry = adapter.build_batch_entry(cfg, resolution, custom_id="TASK-1-0000",
                                      system="ROLE", messages=messages, env=ENV)
    assert entry.params["model"] == sync_body["model"] == resolution.resolved_model_id
    assert entry.params["max_tokens"] == sync_body["max_tokens"]
    assert entry.params["messages"] == sync_body["messages"]
    # the only difference: a one-hour cache TTL, because a batch outlives 5m
    assert entry.params["system"][0]["cache_control"] == {"type": "ephemeral", "ttl": "1h"}
    assert entry.meta["canonical_policy"] == "executor-mechanical"
    assert entry.meta["reasoning_effort"] == resolution.reasoning_effort
    assert len(entry.meta["body_sha256"]) == 64


def test_batch_entry_refuses_a_backend_without_the_api(cfg):
    resolution = adapter.resolve(cfg, "research-deep", backend="zai-anthropic", env={})
    with pytest.raises(batch_module.BatchError, match="does not provide"):
        adapter.build_batch_entry(cfg, resolution, custom_id="x", system=None,
                                  messages=[adapter.Message("user", "q")],
                                  env={"ZAI_API_KEY": "k"})


def test_batch_entry_still_passes_the_cost_policy_guard(cfg):
    resolution = adapter.resolve(cfg, "executor-mechanical", backend="anthropic", env=ENV)
    tampered = replace(resolution, resolved_model_id="amazon-bedrock/model")
    with pytest.raises(config_module.ConfigError, match="forbidden by cost policy"):
        adapter.build_batch_entry(cfg, tampered, custom_id="x", system=None,
                                  messages=[adapter.Message("user", "q")], env=ENV)


def test_custom_ids_are_valid_and_self_describing():
    assert batch_module.custom_id_for("TASK-20260724-221", 3) == "TASK-20260724-221-0003"
    assert batch_module.custom_id_for("TASK-20260724-221", 0, "q one") == \
        "TASK-20260724-221-q-one"
    long = batch_module.custom_id_for("T" * 70, 0)
    assert len(long) <= 64 and batch_module.CUSTOM_ID_PATTERN.match(long)
    with pytest.raises(batch_module.BatchError, match="custom_id"):
        batch_module.validate_custom_id("has space")


def test_check_entries_rejects_duplicates_and_unbatchable_fields(cfg):
    _, entries = _entries(cfg, 2)
    dup = batch_module.BatchEntry(entries[0].custom_id, dict(entries[0].params))
    with pytest.raises(batch_module.BatchError, match="duplicate custom_id"):
        batch_module.check_entries(entries + [dup])
    streamed = batch_module.BatchEntry("s", {**entries[0].params, "stream": True})
    with pytest.raises(batch_module.BatchError, match="`stream`"):
        batch_module.check_entries([streamed])
    with pytest.raises(batch_module.BatchError, match="at least one"):
        batch_module.check_entries([])


# --------------------------------------------------------------------------
# submit / status / collect, and the write-once registry
# --------------------------------------------------------------------------
def test_submit_records_the_submission_write_once(cfg, server, tmp_path):
    resolution, entries = _entries(cfg, 2)
    decision = adapter.choose_delivery(cfg, backend="anthropic", requested="batch", env=ENV)
    batch = batch_module.submit(cfg, "anthropic", entries, env=ENV, opener=server.opener,
                                registry=tmp_path, task_id="TASK-20260724-221",
                                decision=decision)
    assert batch.processing_status == "in_progress" and batch.total == 2
    method, url, body = server.calls[-1]
    assert (method, url) == ("POST", f"{BASE}/v1/messages/batches")
    assert [r["custom_id"] for r in body["requests"]] == [e.custom_id for e in entries]

    directory = tmp_path / batch.id
    submission = json.loads((directory / "submission.json").read_text())
    assert submission["backend"] == "anthropic"
    assert submission["delivery"]["delivery"] == "batch"
    assert [r["custom_id"] for r in submission["requests"]] == [e.custom_id for e in entries]
    assert submission["requests"][0]["resolved_model_id"] == resolution.resolved_model_id
    stored = batch_module.load_requests(tmp_path, batch.id)
    assert stored[entries[0].custom_id].params == entries[0].params
    with pytest.raises(FileExistsError, match="write-once"):
        batch_module._write_once(directory / "submission.json", {})


def test_submit_needs_credentials_and_a_batch_backend(cfg, server, tmp_path):
    _, entries = _entries(cfg, 1)
    with pytest.raises(batch_module.BatchError, match="needs credentials"):
        batch_module.submit(cfg, "anthropic", entries, env={}, opener=server.opener,
                            registry=tmp_path)
    with pytest.raises(batch_module.BatchError, match="does not provide"):
        batch_module.submit(cfg, "zai-anthropic", entries, env={"ZAI_API_KEY": "k"},
                            opener=server.opener, registry=tmp_path)
    assert server.calls == []


def test_preflight_sends_only_the_count_tokens_subset(cfg, server):
    _, entries = _entries(cfg, 1)
    result = batch_module.preflight(cfg, "anthropic", entries[0], env=ENV,
                                    opener=server.opener)
    assert result["input_tokens"] == 42
    method, url, body = server.calls[-1]
    assert url == f"{BASE}/v1/messages/count_tokens"
    assert set(body) <= set(batch_module.COUNT_TOKENS_FIELDS)


def test_retrieve_wait_and_collect(cfg, server, tmp_path):
    _, entries = _entries(cfg, 3)
    batch = batch_module.submit(cfg, "anthropic", entries, env=ENV,
                                opener=server.opener, registry=tmp_path)
    assert not batch_module.retrieve(cfg, "anthropic", batch.id, env=ENV,
                                     opener=server.opener).ended
    with pytest.raises(batch_module.BatchError, match="still processing"):
        batch_module.collect(cfg, "anthropic", batch.id, env=ENV,
                             opener=server.opener, registry=tmp_path)

    # wait() stops on its budget without raising: the batch stays collectable
    clock = iter([0.0, 0.0, 100.0, 100.0, 200.0, 200.0])
    slept = []
    still = batch_module.wait(cfg, "anthropic", batch.id, timeout_seconds=150,
                              poll_interval=60, env=ENV, opener=server.opener,
                              sleep=slept.append, clock=lambda: next(clock))
    assert not still.ended and slept

    server.end(batch.id, [
        server.succeeded(entries[0].custom_id, entries[0].params["model"]),
        server.errored(entries[1].custom_id),
        server.expired(entries[2].custom_id),
    ])
    ended = batch_module.wait(cfg, "anthropic", batch.id, timeout_seconds=1,
                              env=ENV, opener=server.opener, sleep=lambda s: None)
    assert ended.ended

    collected = batch_module.collect(cfg, "anthropic", batch.id, env=ENV,
                                     opener=server.opener, registry=tmp_path)
    assert not collected.from_disk
    ok = collected.results[entries[0].custom_id]
    assert ok.type == "succeeded" and ok.completion.text.endswith(entries[0].custom_id)
    assert ok.completion.usage["cache_read_input_tokens"] == 4
    assert collected.results[entries[1].custom_id].type == "errored"
    assert not collected.results[entries[1].custom_id].retryable   # fix it first
    assert collected.results[entries[2].custom_id].retryable       # expired: resubmit

    receipt = collected.receipts[entries[0].custom_id]["inference_receipt"]
    assert receipt["task_id"] == "TASK-20260724-221"
    assert receipt["delivery"] == {
        "mode": "batch", "batch_id": batch.id, "custom_id": entries[0].custom_id,
        "result_type": "succeeded", "body_sha256": entries[0].meta["body_sha256"],
        "superseded_by_escalation": False}
    assert receipt["response"]["model_matches_resolution"] is True
    assert receipt["response"]["latency_seconds"] is None
    assert receipt["resolution"]["canonical_policy"] == "executor-mechanical"
    assert (tmp_path / batch.id / "results.jsonl").exists()
    recorded = json.loads((tmp_path / batch.id / "collected.json").read_text())
    assert recorded["result_types"][entries[2].custom_id] == "expired"
    assert recorded["missing"] == [] and recorded["unknown"] == []

    # a second collection, from any session, is served from disk
    downloads = len(server.calls)
    again = batch_module.collect(cfg, "anthropic", batch.id, env=ENV,
                                 opener=server.opener, registry=tmp_path)
    assert again.from_disk and len(server.calls) == downloads
    assert again.results[entries[0].custom_id].completion.text == ok.completion.text
    assert again.receipts == collected.receipts


def test_results_url_off_the_configured_backend_is_refused(cfg, server, tmp_path):
    _, entries = _entries(cfg, 1)
    batch = batch_module.submit(cfg, "anthropic", entries, env=ENV,
                                opener=server.opener, registry=tmp_path)
    server.end(batch.id)
    server.batches[batch.id]["results_url"] = "https://elsewhere.invalid/results"
    with pytest.raises(batch_module.BatchError, match="refusing to follow"):
        batch_module.collect(cfg, "anthropic", batch.id, env=ENV,
                             opener=server.opener, registry=tmp_path)
    assert not (tmp_path / batch.id / "results.jsonl").exists()


def test_collect_records_results_for_requests_this_checkout_never_submitted(
        cfg, server, tmp_path):
    """Submitted elsewhere, collected here: still recorded, still joinable."""
    _, entries = _entries(cfg, 1)
    batch = batch_module.submit(cfg, "anthropic", entries, env=ENV,
                                opener=server.opener, registry=tmp_path / "other")
    server.end(batch.id)
    collected = batch_module.collect(cfg, "anthropic", batch.id, env=ENV,
                                     opener=server.opener, registry=tmp_path / "here")
    assert collected.results[entries[0].custom_id].type == "succeeded"
    recorded = json.loads((tmp_path / "here" / batch.id / "collected.json").read_text())
    assert recorded["unknown"] == [entries[0].custom_id]
    assert collected.receipts[entries[0].custom_id]["inference_receipt"]["task_id"] is None


def test_transport_retries_then_surfaces_http_errors(cfg, server):
    server.fail_next = (500, "boom")
    batch = batch_module.MessageBatch("msgbatch_x", "in_progress", {})
    with pytest.raises(batch_module.BatchError, match="HTTP 404"):
        batch_module.retrieve(cfg, "anthropic", batch.id, env=ENV,
                              opener=server.opener, sleep=lambda s: None)
    assert [c[0] for c in server.calls] == ["GET", "GET"]   # one retry, then the 404


def test_malformed_batch_payloads_are_errors(cfg):
    with pytest.raises(batch_module.BatchError, match="no id"):
        batch_module.MessageBatch.from_payload({"type": "message_batch"})
    with pytest.raises(batch_module.BatchError, match="unknown processing_status"):
        batch_module.MessageBatch.from_payload({"id": "x", "processing_status": "done"})
    with pytest.raises(batch_module.BatchError, match="malformed batch result"):
        batch_module.BatchResult.from_line({"custom_id": "x", "result": {"type": "lost"}},
                                           "anthropic_messages")


# --------------------------------------------------------------------------
# list / cancel / delete
# --------------------------------------------------------------------------
def test_list_merges_local_registry_and_remote_page(cfg, server, tmp_path):
    _, entries = _entries(cfg, 1)
    first = batch_module.submit(cfg, "anthropic", entries, env=ENV,
                                opener=server.opener, registry=tmp_path)
    second = batch_module.submit(cfg, "anthropic", entries, env=ENV,
                                 opener=server.opener, registry=tmp_path)
    rows = batch_module.local_batches(tmp_path)
    assert [r["id"] for r in rows] == [first.id, second.id]
    assert rows[0]["requests"] == 1 and not rows[0]["collected"]
    page, cursor = batch_module.list_batches(cfg, "anthropic", limit=1, env=ENV,
                                             opener=server.opener)
    assert [b.id for b in page] == [second.id] and cursor["has_more"]
    page, cursor = batch_module.list_batches(cfg, "anthropic", limit=1,
                                             after_id=cursor["last_id"], env=ENV,
                                             opener=server.opener)
    assert [b.id for b in page] == [first.id] and not cursor["has_more"]


def test_cancel_and_delete(cfg, server, tmp_path):
    _, entries = _entries(cfg, 1)
    batch = batch_module.submit(cfg, "anthropic", entries, env=ENV,
                                opener=server.opener, registry=tmp_path)
    cancelled = batch_module.cancel(cfg, "anthropic", batch.id, env=ENV,
                                    opener=server.opener, registry=tmp_path,
                                    reason="no longer needed")
    assert cancelled.processing_status == "canceling"
    record = json.loads((tmp_path / batch.id / "cancel.json").read_text())
    assert record["reason"] == "no longer needed"
    assert batch_module.local_state(tmp_path, batch.id)["cancelled"]
    server.end(batch.id, [{"custom_id": entries[0].custom_id,
                           "result": {"type": "canceled"}}])
    deleted = batch_module.delete(cfg, "anthropic", batch.id, env=ENV, opener=server.opener)
    assert deleted["type"] == "message_batch_deleted"
    assert (tmp_path / batch.id / "submission.json").exists()   # the record stays


# --------------------------------------------------------------------------
# escalation: a result that became urgent after it was batched
# --------------------------------------------------------------------------
def test_escalate_reruns_the_recorded_body_and_cancels_when_nothing_remains(
        cfg, server, tmp_path):
    _, entries = _entries(cfg, 2)
    batch = batch_module.submit(cfg, "anthropic", entries, env=ENV,
                                opener=server.opener, registry=tmp_path)
    done, state = batch_module.escalate(
        cfg, "anthropic", batch.id, custom_ids=[entries[0].custom_id], env=ENV,
        opener=server.opener, registry=tmp_path, reason="reviewer waiting")
    assert [e.custom_id for e in done] == [entries[0].custom_id]
    assert done[0].completion.text == "sync answer"
    method, url, body = next(c for c in server.calls if c[1] == f"{BASE}/v1/messages")
    assert body == entries[0].params                     # verbatim, not rebuilt
    assert state.processing_status == "in_progress"      # one request still wanted
    record = json.loads(done[0].path.read_text())
    assert record["inference_receipt"]["delivery"] == {
        "mode": "interactive", "escalated_from_batch": batch.id,
        "custom_id": entries[0].custom_id,
        "body_sha256": entries[0].meta["body_sha256"], "reason": "reviewer waiting"}

    # escalating the same request again is a no-op, not a second payment
    again, _ = batch_module.escalate(
        cfg, "anthropic", batch.id, custom_ids=[entries[0].custom_id], env=ENV,
        opener=server.opener, registry=tmp_path)
    assert again == []

    # once every request is escalated the batch is cancelled automatically
    rest, state = batch_module.escalate(cfg, "anthropic", batch.id, env=ENV,
                                        opener=server.opener, registry=tmp_path)
    assert [e.custom_id for e in rest] == [entries[1].custom_id]
    assert state.processing_status == "canceling"
    assert json.loads((tmp_path / batch.id / "cancel.json").read_text())["reason"] == \
        "every request escalated"


def test_escalate_marks_the_late_batch_copy_as_superseded(cfg, server, tmp_path):
    _, entries = _entries(cfg, 2)
    batch = batch_module.submit(cfg, "anthropic", entries, env=ENV,
                                opener=server.opener, registry=tmp_path)
    batch_module.escalate(cfg, "anthropic", batch.id, custom_ids=[entries[0].custom_id],
                          env=ENV, opener=server.opener, registry=tmp_path)
    server.end(batch.id)
    collected = batch_module.collect(cfg, "anthropic", batch.id, env=ENV,
                                     opener=server.opener, registry=tmp_path)
    assert collected.superseded == [entries[0].custom_id]
    receipt = collected.receipts[entries[0].custom_id]["inference_receipt"]
    assert receipt["delivery"]["superseded_by_escalation"] is True
    assert collected.receipts[entries[1].custom_id]["inference_receipt"]["delivery"][
        "superseded_by_escalation"] is False
    assert batch_module.escalation_completion(tmp_path, batch.id, entries[0].custom_id)


def test_escalate_refuses_an_ended_batch_and_unknown_requests(cfg, server, tmp_path):
    _, entries = _entries(cfg, 1)
    batch = batch_module.submit(cfg, "anthropic", entries, env=ENV,
                                opener=server.opener, registry=tmp_path)
    with pytest.raises(batch_module.BatchError, match="not in batch"):
        batch_module.escalate(cfg, "anthropic", batch.id, custom_ids=["nope"], env=ENV,
                              opener=server.opener, registry=tmp_path)
    server.end(batch.id)
    with pytest.raises(batch_module.BatchError, match="already ended"):
        batch_module.escalate(cfg, "anthropic", batch.id, env=ENV,
                              opener=server.opener, registry=tmp_path)
    with pytest.raises(batch_module.BatchError, match="no requests.jsonl"):
        batch_module.escalate(cfg, "anthropic", batch.id, env=ENV,
                              opener=server.opener, registry=tmp_path / "empty")


# --------------------------------------------------------------------------
# manifests, handoffs, and the dispatcher
# --------------------------------------------------------------------------
def test_inference_block_names_the_delivery_lane(cfg):
    resolution = adapter.resolve(cfg, "research-deep", backend="anthropic", env=ENV)
    block = manifest_module.inference_block(resolution)
    assert block["delivery"] == "interactive" and block["batch_id"] is None
    block = manifest_module.inference_block(resolution, delivery="batch",
                                            batch_id="msgbatch_1")
    assert block["delivery"] == "batch" and block["batch_id"] == "msgbatch_1"
    with pytest.raises(ValueError, match="names its batch_id"):
        manifest_module.inference_block(resolution, delivery="batch")
    assert manifest_module.deterministic_block()["delivery"] is None


def test_receipt_carries_a_delivery_record(cfg):
    resolution = adapter.resolve(cfg, "research-deep", backend="anthropic", env=ENV)
    data = manifest_module.receipt(resolution, delivery={"mode": "interactive"})
    assert data["inference_receipt"]["delivery"] == {"mode": "interactive"}
    assert "delivery" not in manifest_module.receipt(resolution)["inference_receipt"]


def test_dispatcher_validates_the_delivery_fields():
    sys.path.insert(0, str(REPO / "tools"))
    import research_dispatch
    good = {"inference": {"policy": "executor-implementation", "delivery": "auto",
                          "deadline_seconds": 7200}}
    research_dispatch.validate_inference(good, "executor", "task")
    for field, value, match in (("delivery", "eventually", "one of"),
                                ("deadline_seconds", "soon", "non-negative"),
                                ("deadline_seconds", -1, "non-negative")):
        bad = deepcopy(good)
        bad["inference"][field] = value
        with pytest.raises(research_dispatch.DispatchError, match=match):
            research_dispatch.validate_inference(bad, "executor", "task")


def test_handoff_template_documents_the_delivery_fields():
    template = (REPO / "templates/research-records.md").read_text()
    assert "delivery: interactive" in template and "deadline_seconds: null" in template


# --------------------------------------------------------------------------
# the command line, end to end
# --------------------------------------------------------------------------
@pytest.fixture
def cli(server, monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.delenv("AUTORESEARCH_BACKEND", raising=False)
    monkeypatch.setattr(batch_module, "_default_opener", lambda cfg: server.opener)
    monkeypatch.setattr(transport_module, "_default_opener", lambda cfg: server.opener)
    registry = tmp_path / "registry"

    def run(*argv: str) -> int:
        return cli_module.main(list(argv))

    run.registry = registry       # type: ignore[attr-defined]
    return run


def test_cli_submit_wait_collect_round_trip(cli, server, tmp_path, capsys):
    prompts = [tmp_path / "q1.md", tmp_path / "q2.md"]
    for path in prompts:
        path.write_text(f"prompt {path.stem}")
    assert cli("batch", "submit", "--policy", "executor-mechanical",
               "--backend", "anthropic", "--prompt-file", str(prompts[0]),
               "--prompt-file", str(prompts[1]), "--task-id", "TASK-20260724-221",
               "--registry", str(cli.registry), "--note", "two questions") == 0
    out, err = capsys.readouterr()
    assert "msgbatch_001  in_progress" in out
    assert "preflight ok" in err and "delivery: batch" in err
    submission = json.loads((cli.registry / "msgbatch_001" / "submission.json").read_text())
    assert [r["custom_id"] for r in submission["requests"]] == [
        "TASK-20260724-221-q1", "TASK-20260724-221-q2"]
    assert submission["note"] == "two questions" and submission["preflight"]["input_tokens"] == 42
    assert "ROLE" not in json.dumps(submission)        # no --role: no contract system prompt

    assert cli("batch", "status", "--all", "--registry", str(cli.registry)) == 0
    assert "in_progress" in capsys.readouterr()[0]
    assert cli("batch", "list", "--remote", "--registry", str(cli.registry)) == 0
    out = capsys.readouterr()[0]
    assert "open" in out and "not in local registry" not in out

    server.end("msgbatch_001")
    assert cli("batch", "wait", "msgbatch_001", "--timeout-seconds", "1",
               "--registry", str(cli.registry)) == 0
    assert "ended" in capsys.readouterr()[0]
    assert cli("batch", "collect", "msgbatch_001", "--json",
               "--registry", str(cli.registry)) == 0
    results = json.loads(capsys.readouterr()[0])
    assert results["TASK-20260724-221-q1"]["type"] == "succeeded"
    assert results["TASK-20260724-221-q1"]["text"].endswith("q1")
    assert cli("batch", "collect", "msgbatch_001", "--print",
               "--registry", str(cli.registry)) == 0
    out = capsys.readouterr()[0]
    assert "from disk" in out and "answer for TASK-20260724-221-q2" in out


def test_cli_submit_from_a_handoff_honours_its_delivery_block(cli, server, tmp_path, capsys):
    handoff = tmp_path / "TASK-20261005-abc123.yaml"
    handoff.write_text(yaml.safe_dump({"handoff": {
        "id": "TASK-20261005-abc123", "from": "coordinator", "to": "executor",
        "inference": {"policy": "executor-mechanical", "delivery": "auto",
                      "deadline_seconds": 600}}}))
    prompt = tmp_path / "q.md"
    prompt.write_text("do it")
    receipts = tmp_path / "receipts"
    # 600s cannot wait for a batch: the router runs it now and says so
    assert cli("batch", "submit", "--task", str(handoff), "--backend", "anthropic",
               "--prompt-file", str(prompt), "--registry", str(cli.registry),
               "--receipt-dir", str(receipts)) == 0
    out, err = capsys.readouterr()
    assert "delivery: interactive" in err and "sync answer" in out
    assert not (cli.registry).exists()
    receipt = json.loads(next(receipts.glob("*.json")).read_text())["inference_receipt"]
    assert receipt["task_id"] == "TASK-20261005-abc123"
    assert receipt["delivery"]["decision"]["delivery"] == "interactive"
    assert receipt["role"] == "executor"
    # a system prompt was assembled from the role contract
    sync_body = next(c[2] for c in server.calls if c[1] == f"{BASE}/v1/messages")
    assert "agents/executor" in str(config_module.REPO_ROOT / "agents/executor.md")
    assert sync_body["system"]

    # with a roomy deadline the same handoff is batched
    assert cli("batch", "submit", "--task", str(handoff), "--backend", "anthropic",
               "--prompt-file", str(prompt), "--registry", str(cli.registry),
               "--deadline-seconds", "86400") == 0
    out, err = capsys.readouterr()
    assert "delivery: batch" in err and "msgbatch_001" in out
    submission = json.loads((cli.registry / "msgbatch_001" / "submission.json").read_text())
    assert submission["task_id"] == "TASK-20261005-abc123"
    assert submission["requests"][0]["role"] == "executor"


def test_cli_escalate_and_cancel(cli, server, tmp_path, capsys):
    prompts = tmp_path / "p.jsonl"
    prompts.write_text(json.dumps({"custom_id": "urgent-one", "prompt": "a"}) + "\n"
                       + json.dumps({"custom_id": "can-wait", "prompt": "b"}) + "\n")
    assert cli("batch", "submit", "--policy", "executor-mechanical",
               "--backend", "anthropic", "--prompts-jsonl", str(prompts),
               "--no-preflight", "--registry", str(cli.registry)) == 0
    capsys.readouterr()
    assert cli("batch", "escalate", "msgbatch_001", "--custom-id", "urgent-one",
               "--reason", "needed for review", "--registry", str(cli.registry)) == 0
    out = capsys.readouterr()[0]
    assert "urgent-one" in out and "escalated" in out and "in_progress" in out
    assert cli("batch", "cancel", "msgbatch_001", "--reason", "rest unneeded",
               "--registry", str(cli.registry)) == 0
    assert "canceling" in capsys.readouterr()[0]
    with pytest.raises(SystemExit, match="--yes"):
        cli("batch", "delete", "msgbatch_001", "--registry", str(cli.registry))
    assert "msgbatch_001" in server.batches                    # nothing deleted


def test_cli_plan_is_offline(cli, server, capsys):
    assert cli("batch", "plan", "--delivery", "auto", "--deadline-seconds", "300",
               "--backend", "anthropic", "--json") == 0
    decision = json.loads(capsys.readouterr()[0])
    assert decision["delivery"] == "interactive"
    assert server.calls == []


def test_cli_dry_run_submits_nothing(cli, server, tmp_path, capsys):
    prompt = tmp_path / "q.md"
    prompt.write_text("hello")
    assert cli("batch", "submit", "--policy", "executor-mechanical", "--backend",
               "anthropic", "--prompt-file", str(prompt), "--dry-run",
               "--registry", str(cli.registry)) == 0
    body = json.loads(capsys.readouterr()[0])
    assert body["requests"][0]["custom_id"] == "req-0000"
    assert [c[0] for c in server.calls] == ["POST"]            # the preflight only
    assert server.calls[0][1].endswith("/count_tokens")
    assert not cli.registry.exists()


def test_cli_reports_batch_errors_as_exit_code_2(cli, capsys):
    assert cli("batch", "plan", "--delivery", "batch", "--backend", "zai-anthropic") == 2
    assert "does not provide the Message Batches API" in capsys.readouterr()[1]
