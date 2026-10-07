"""The autopilot's Message Batches lane: draft asynchronously, file interactively.

The lane is exercised against the in-memory batch endpoint from
`tests/test_batch_inference.py`; the supervisor is exercised with a fake lane.
The properties guarded: a non-batchable action never takes the lane, a
submitted draft is excluded from re-selection while it runs, a finished draft
is handed to an interactive worker as untrusted text at a recorded path, and
a failed draft cools the action down rather than disappearing.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestration import adapter
from orchestration.adapter import batch as batch_module
from orchestration.campaign import autopilot, batch_lane
from tests.test_batch_inference import ENV, FakeBatchServer

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def cfg():
    return adapter.load()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_only_draftable_kinds_take_the_lane(cfg) -> None:
    for kind in ("run", "prepare", "repair", "review"):
        decision = batch_lane.delivery_for(cfg, kind, "batch", "anthropic", env=ENV)
        assert decision.delivery == "interactive"
    assert batch_lane.delivery_for(cfg, "design", "auto", "anthropic", env=ENV).delivery == "batch"
    assert batch_lane.delivery_for(cfg, "design", "batch", "anthropic", env=ENV).delivery == "batch"
    assert batch_lane.delivery_for(
        cfg, "design", "interactive", "anthropic", env=ENV).delivery == "interactive"
    # A backend without the API is never silently given a batch.
    assert batch_lane.delivery_for(cfg, "design", "auto", "zai", env=ENV).delivery == "interactive"
    with pytest.raises(batch_module.BatchError):
        batch_lane.delivery_for(cfg, "design", "batch", "zai", env=ENV)


def test_draft_prompt_carries_the_proposal_and_the_rules(tmp_path: Path) -> None:
    _write(tmp_path / "orchestration/research-priority.yaml", "ecc_areas: [ICEX]\n")
    _write(tmp_path / "ledger/proposals/x.yaml",
           "idea:\n  id: IDEA-20260926-abcdef\n  status: proposed\n  summary: toy\n")
    prompt = batch_lane.draft_prompt(tmp_path, "design", "IDEA-20260926-abcdef", "design it")
    assert "ID-TBD" in prompt and "provenance: recalled" in prompt
    assert "summary: toy" in prompt and "ecc_areas: [ICEX]" in prompt
    assert "## The action to draft for\n\ndesign it" in prompt
    portfolio = batch_lane.draft_prompt(tmp_path, "portfolio", "ecdlp", "rank")
    assert "summary: toy" not in portfolio


def test_real_lane_submits_polls_and_collects(cfg, tmp_path: Path) -> None:
    server = FakeBatchServer()
    lane = batch_lane.BatchLane("anthropic", config=cfg, env=ENV,
                                registry=tmp_path / "registry", opener=server.opener,
                                repo=REPO)
    action = autopilot.Action("design", "IDEA-20260926-abcdef", "design it", "coordinator")
    submitted = lane.submit(action, attempt_id="a" * 32)
    assert submitted["backend"] == "anthropic" and submitted["custom_id"].startswith("req-")
    assert lane.status(submitted["batch_id"]) == "in_progress"
    requests = server.requests[submitted["batch_id"]]
    assert len(requests) == 1
    body = requests[0]["params"]
    assert body["model"] == submitted["model"]
    assert "ID-TBD" in json.dumps(body["messages"])
    assert "coordinator" in json.dumps(body["system"]).lower()
    assert (tmp_path / "registry" / submitted["batch_id"] / "submission.json").exists()

    server.end(submitted["batch_id"])
    assert lane.status(submitted["batch_id"]) == "ended"
    collected = lane.collect(submitted["batch_id"], submitted["custom_id"])
    assert collected["type"] == "succeeded"
    assert collected["text"].startswith("answer for ")
    assert collected["usage"]["input_tokens"] == 10
    assert lane.collect(submitted["batch_id"], "nobody")["type"] == "missing"
    with pytest.raises(batch_module.BatchError):
        batch_lane.BatchLane("zai", config=cfg, env=ENV)


class FakeLane:
    def __init__(self, cfg, outcome: str = "succeeded") -> None:
        self.config = cfg
        self.backend = "anthropic"
        self.outcome = outcome
        self.submitted: list[autopilot.Action] = []
        self.ended = False

    def submit(self, action, *, attempt_id):
        self.submitted.append(action)
        return {"batch_id": f"msgbatch_{len(self.submitted)}", "custom_id": "req-x",
                "backend": "anthropic", "model": "model-x", "policy": "p",
                "model_verified": False, "processing_status": "in_progress"}

    def status(self, batch_id):
        return "ended" if self.ended else "in_progress"

    def collect(self, batch_id, custom_id):
        if self.outcome == "succeeded":
            return {"type": "succeeded", "text": "DRAFT TEXT", "usage": {"input_tokens": 3},
                    "reported_model": "model-x", "error": None}
        return {"type": self.outcome, "text": None, "usage": None,
                "error": {"message": "expired"}}


def test_supervisor_drafts_then_files_with_the_draft_attached(cfg, tmp_path: Path) -> None:
    design = autopilot.Action("design", "IDEA-1", "design it", "coordinator")
    lane = FakeLane(cfg)
    invoked = []

    def select(_repo, *, excluded):
        return None if design.key in excluded else design

    def invoke(action, _repo, _dir, **_kwargs):
        invoked.append(action)
        return {"ok": True, "attempts": []}

    state_dir = tmp_path / "state"
    first = autopilot.supervise(tmp_path, state_dir, backends=["anthropic"], max_actions=1,
                                delivery="auto", batch_lane=lane, selector=select,
                                invoke=invoke, clock=lambda: 1000.0)
    assert lane.submitted == [design] and invoked == []
    assert first["batches_submitted"] == 1
    assert set(first["pending_batches"]) == {"design:IDEA-1"}
    assert first["attempts"] == 0

    # Still processing: the action stays excluded and nothing is re-submitted.
    second = autopilot.supervise(tmp_path, state_dir, backends=["anthropic"], max_actions=1,
                                 delivery="auto", batch_lane=lane, selector=select,
                                 invoke=invoke, clock=lambda: 2000.0)
    assert len(lane.submitted) == 1 and invoked == []
    assert set(second["pending_batches"]) == {"design:IDEA-1"}

    lane.ended = True
    third = autopilot.supervise(tmp_path, state_dir, backends=["anthropic"], max_actions=1,
                                delivery="auto", batch_lane=lane, selector=select,
                                invoke=invoke, clock=lambda: 3000.0)
    assert len(invoked) == 1 and invoked[0].kind == "design"
    assert "untrusted model text" in invoked[0].prompt
    draft_path = Path(invoked[0].prompt.split(" is at ")[1].split(".")[0] + ".md")
    assert draft_path.exists() and "DRAFT TEXT" in draft_path.read_text()
    assert json.loads(draft_path.read_text().split("<!-- ", 1)[1].split(" -->", 1)[0])[
        "batch_id"] == "msgbatch_1"
    assert third["pending_batches"] == {} and third["attempts"] == 1
    metrics = autopilot.report(state_dir)
    assert metrics["batch_drafts_submitted"] == 1
    assert metrics["batch_drafts_collected"] == 1
    assert metrics["batch_drafts_failed"] == 0
    kinds = [json.loads(line)["event"] for line in
             (state_dir / "events.jsonl").read_text().splitlines()]
    assert kinds.count("batch_submitted") == 1 and kinds.count("started") == 1


def test_failed_draft_cools_the_action_down(cfg, tmp_path: Path) -> None:
    design = autopilot.Action("design", "IDEA-2", "design it", "coordinator")
    lane = FakeLane(cfg, outcome="expired")
    lane_calls = []
    select = lambda _repo, *, excluded: None if design.key in excluded else design
    invoke = lambda action, *_a, **_k: lane_calls.append(action) or {"ok": True, "attempts": []}
    state_dir = tmp_path / "state"
    autopilot.supervise(tmp_path, state_dir, backends=["anthropic"], max_actions=1,
                        delivery="batch", batch_lane=lane, selector=select, invoke=invoke,
                        clock=lambda: 1000.0)
    lane.ended = True
    state = autopilot.supervise(tmp_path, state_dir, backends=["anthropic"], max_actions=1,
                                delivery="batch", batch_lane=lane, selector=select,
                                invoke=invoke, retry_seconds=300, clock=lambda: 2000.0)
    assert lane_calls == []
    assert state["pending_batches"] == {}
    assert state["cooldowns"][design.key] == 2300
    assert autopilot.report(state_dir)["batch_drafts_failed"] == 1


def test_run_actions_stay_interactive_under_batch_delivery(cfg, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(autopilot, "_execution_snapshot", lambda *_: "same")
    run = autopilot.Action("run", "EXP-1", "run it", "executor")
    lane = FakeLane(cfg)
    invoked = []
    state = autopilot.supervise(
        tmp_path, tmp_path / "state", backends=["anthropic"], max_actions=1,
        delivery="batch", batch_lane=lane, selector=lambda *_a, **_k: run,
        invoke=lambda action, *_a, **_k: invoked.append(action) or {"ok": True, "attempts": []},
        clock=lambda: 1000.0)
    assert lane.submitted == [] and invoked == [run]
    assert state["pending_batches"] == {}


def test_wait_batches_polls_until_the_draft_lands(cfg, tmp_path: Path) -> None:
    design = autopilot.Action("design", "IDEA-3", "design it", "coordinator")
    lane = FakeLane(cfg)
    now = [1000.0]
    naps = []

    def sleeper(seconds):
        naps.append(seconds)
        now[0] += seconds
        if now[0] >= 1600:
            lane.ended = True

    invoked = []
    state = autopilot.supervise(
        tmp_path, tmp_path / "state", backends=["anthropic"], max_actions=2,
        delivery="auto", batch_lane=lane, batch_poll_seconds=300, wait_batches=3600,
        idle_seconds=60, selector=lambda _r, *, excluded: None if design.key in excluded else design,
        invoke=lambda action, *_a, **_k: invoked.append(action) or {"ok": True, "attempts": []},
        clock=lambda: now[0], sleeper=sleeper)
    assert len(lane.submitted) == 1 and len(invoked) == 1
    assert state["pending_batches"] == {} and state["attempts"] == 1
    assert naps and all(nap <= 60 for nap in naps)

    # Without a wait, a bounded invocation returns with the draft still pending.
    lane2 = FakeLane(cfg)
    pending = autopilot.supervise(
        tmp_path, tmp_path / "state2", backends=["anthropic"], max_actions=2,
        delivery="auto", batch_lane=lane2,
        selector=lambda _r, *, excluded: None if "design:IDEA-4" in excluded else
        autopilot.Action("design", "IDEA-4", "d", "coordinator"),
        invoke=lambda *_a, **_k: {"ok": True, "attempts": []}, clock=lambda: 5000.0)
    assert set(pending["pending_batches"]) == {"design:IDEA-4"}


def test_batch_delivery_requires_a_lane(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        autopilot.supervise(tmp_path, tmp_path / "s", backends=[], delivery="auto",
                            max_actions=1)
