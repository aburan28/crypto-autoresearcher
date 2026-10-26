#!/usr/bin/env python3
"""Scoped official checks for this new draft package, not a whole-ledger audit."""
import argparse
import json
from pathlib import Path
import sys

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--repo-root", type=Path, required=True)
p.add_argument("--package", type=Path, required=True)
p.add_argument("--ids", type=Path, required=True)
a = p.parse_args()
sys.path.insert(0, str(a.repo_root.resolve() / "tools"))
import validate_ledger as vl
# These are actual prospective files in an unpublished projected tree. Root is
# deliberately supplied for repository-relative links (not patched file tests).
# The canonical repository will repeat its ordinary checks after publication.
vl.REPO = str(a.package.resolve())
ctx = vl.Ctx(set())
ids = json.loads(a.ids.read_text())
scope = []
for kind, section, key in [("research_question", "questions", "question"),
                           ("hypothesis", "hypotheses", "hypothesis"),
                           ("coordinator_decision", "decisions", "design_decision"),
                           ("handoff", "handoffs", "capacity_task"),
                           ("handoff", "handoffs", "executor_task"),
                           ("handoff", "handoffs", "design_archive_task"),
                           ("handoff", "handoffs", "archive_task")]:
    path = a.package / "ledger" / section / (ids[key] + ".yaml")
    vl.check_ledger_record(str(path), kind, ctx)
    scope.append({"path": str(path.relative_to(a.package)), "method": "check_ledger_record", "record_type": kind})
spec = a.package / "experiments" / ids["experiment"] / "specification.yaml"
vl.check_experiment(str(spec), ctx)
scope.append({"path": str(spec.relative_to(a.package)), "method": "check_experiment"})
goal = a.package / "ledger/goals" / ids["goal"] / "goal.yaml"
body = vl.load_yaml(str(goal), ctx)["research_goal"]
for key in vl.GOAL_REQUIRED:
    if body.get(key) in (None, ""):
        ctx.err(str(goal), "missing required field " + key)
if not vl.GOAL_ID.fullmatch(body.get("id", "")) or body.get("status") not in vl.GOAL_STATUSES:
    ctx.err(str(goal), "goal identity/status invalid")
vl.check_ecc_budget_is_unlimited(str(goal), body, body["status"], ctx)
vl.check_budget_retirement(str(goal), body, ctx)
vl.check_goal_closure_quorum(str(goal), body, ctx)
scope.append({"path": str(goal.relative_to(a.package)), "method": "GOAL_REQUIRED/id/status/budget/closure"})
report = {"schema": "classical.ecdlp.endpoint-reuse.draft-record-check.v1", "scope": scope,
          "repository_path_context": str(a.package.resolve()),
          "errors": ctx.errors, "advisories": ctx.advisories, "whole_ledger_checked": False,
          "source_input_publication_or_execution_readiness_attested": False,
          "independent_scientific_review": False}
print(json.dumps(report, indent=2))
raise SystemExit(0 if not ctx.errors else 2)
