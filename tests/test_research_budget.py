from datetime import date, timedelta
import subprocess

import pytest
import yaml

from orchestration.research_budget import agent_wall_limit, enforce_research_budget


def restriction(days=90):
    end = date.today()
    return {"wall_clock_seconds": 60, "enforcement": "stagnation",
            "stagnation_review": {
                "assessed_by": "coordinator", "decision_id": "DEC-20260906-abcdef",
                "assessed_at": end.isoformat(),
                "last_progress_at": (end - timedelta(days=days)).isoformat(),
                "no_progress": True, "infrastructure_only": False,
                "evidence_refs": ["coordination/example/assessment.md"],
                "scope": "one lane", "rationale": "reviewed lack of progress",
                "next_action": "retest a named alternative"}}


def test_ordinary_estimates_do_not_set_a_deadline():
    assert not enforce_research_budget({"wall_clock_seconds": 1, "maximum_runs": 1})
    assert agent_wall_limit({"budget": {"wall_clock_seconds": 1}}) is None
    assert agent_wall_limit({"budget": {"wall_clock_seconds": None}}) is None


def test_explicit_machine_watchdog_still_applies():
    assert agent_wall_limit({"budget": {"wall_clock_seconds": 1},
                             "runtime_limits": {"wall_clock_seconds": 30,
                                                "reason": "checkpoint worker"}}) == 30
    with pytest.raises(ValueError, match="reason"):
        agent_wall_limit({"runtime_limits": {"wall_clock_seconds": 30}})


def test_boundary_requires_months_not_days():
    with pytest.raises(ValueError, match="90 days"):
        enforce_research_budget(restriction(89))
    assert enforce_research_budget(restriction(90))
    assert agent_wall_limit({"budget": restriction(90)}) == 60


@pytest.mark.parametrize("field,value", [
    ("no_progress", False), ("infrastructure_only", True),
    ("infrastructure_only", None), ("evidence_refs", []),
    ("decision_id", "not-a-decision"), ("rationale", ""),
    ("last_progress_at", None),
])
def test_unknown_progress_or_missing_assessment_never_enforces(field, value):
    budget = restriction(120)
    budget["stagnation_review"][field] = value
    with pytest.raises(ValueError):
        enforce_research_budget(budget)


@pytest.mark.parametrize("offset", [-8, 1])
def test_stale_or_future_review_cannot_restrict_work(offset):
    budget = restriction(120)
    budget["stagnation_review"]["assessed_at"] = (date.today() + timedelta(days=offset)).isoformat()
    with pytest.raises(ValueError, match="stale or future"):
        enforce_research_budget(budget)


def test_new_progress_prevents_reusing_a_months_old_interval():
    budget = restriction(120)
    budget["stagnation_review"]["last_progress_at"] = date.today().isoformat()
    with pytest.raises(ValueError, match="90 days"):
        enforce_research_budget(budget)


def test_enforcement_requires_committed_matching_authority(tmp_path):
    budget = restriction()
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    with pytest.raises(ValueError, match="committed"):
        enforce_research_budget(budget, repo_root=tmp_path)
    path = tmp_path / "ledger/decisions/DEC-20260906-abcdef.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(yaml.safe_dump({"coordinator_decision": {
        "id": "DEC-20260906-abcdef", "target_ids": ["TASK-TEST"],
        "approved_budget": {"wall_clock_seconds": 60},
        "decision": "approve", "decided_by": "coordinator",
        "stagnation_review": budget["stagnation_review"]}}))
    evidence = tmp_path / budget["stagnation_review"]["evidence_refs"][0]
    evidence.parent.mkdir(parents=True)
    evidence.write_text("Synthetic test assessment, not research evidence.")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=Test",
                    "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture"], check=True)
    assert enforce_research_budget(budget, repo_root=tmp_path, target_id="TASK-TEST")
    with pytest.raises(ValueError, match="target"):
        enforce_research_budget(budget, repo_root=tmp_path, target_id="TASK-OTHER")
    with pytest.raises(ValueError, match="approved budget"):
        enforce_research_budget(dict(budget, wall_clock_seconds=1), repo_root=tmp_path)
    budget["stagnation_review"]["rationale"] = "uncommitted changed assessment"
    with pytest.raises(ValueError, match="differs"):
        enforce_research_budget(budget, repo_root=tmp_path)


def test_advisory_estimates_cannot_close_a_new_goal():
    from tools.validate_ledger import check_budget_retirement
    class Context:
        def __init__(self):
            self.errors = []
        def err(self, path, message):
            self.errors.append(message)
    ctx = Context()
    check_budget_retirement("test.yaml", {
        "id": "GOAL-TEST-abcdef", "status": "closed_at_budget",
        "closed_at": date.today().isoformat(),
        "campaign_budget": {"maximum_batches": 1}}, ctx)
    assert len(ctx.errors) == 1
    assert "advisory estimates" in ctx.errors[0]
