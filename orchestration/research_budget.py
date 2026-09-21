"""Research estimates are advisory; exceptional restrictions require stagnation review.

Process watchdogs protect a machine, not a campaign's spending. Missing progress
telemetry is never evidence of stagnation. This module validates a Coordinator's
explicit assessment; it does not infer scientific progress from elapsed time.
"""
from datetime import date
import math
import re
from pathlib import PurePosixPath
import subprocess

import yaml

MINIMUM_STAGNATION_DAYS = 90
MAXIMUM_REVIEW_AGE_DAYS = 7


def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite positive number")
    return float(value)


def enforce_research_budget(budget, *, today=None, repo_root=None, target_id=None):
    """Only an explicit, recent, evidence-citing months-long review enables caps.

    Existing numeric budgets alone are estimates. A malformed request to enforce
    is refused, rather than silently becoming a spending restriction.
    """
    mode = budget.get("enforcement", "advisory")
    if mode == "advisory":
        return False
    if mode != "stagnation":
        raise ValueError("budget.enforcement must be advisory or stagnation")
    review = budget.get("stagnation_review")
    if not isinstance(review, dict):
        raise ValueError("budget enforcement requires a documented stagnation_review")
    if review.get("assessed_by") != "coordinator" or review.get("no_progress") is not True:
        raise ValueError("stagnation requires explicit Coordinator assessment of no progress")
    if review.get("infrastructure_only") is not False:
        raise ValueError("infrastructure downtime or missing telemetry is not stagnation")
    for name in ("rationale", "next_action", "scope"):
        if not isinstance(review.get(name), str) or not review[name].strip():
            raise ValueError(f"stagnation_review.{name} is required")
    if not re.fullmatch(r"DEC-\d{8}-[0-9a-f]{6}", str(review.get("decision_id", ""))):
        raise ValueError("stagnation review requires a Coordinator decision ID")
    refs = review.get("evidence_refs")
    if not isinstance(refs, list) or not refs or not all(isinstance(r, str) and r.strip() for r in refs):
        raise ValueError("stagnation review requires evidence refs, not elapsed time alone")
    try:
        start = date.fromisoformat(review["last_progress_at"])
        end = date.fromisoformat(review["assessed_at"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("stagnation review requires ISO dates") from exc
    today = today or date.today()
    if not 0 <= (today - end).days <= MAXIMUM_REVIEW_AGE_DAYS:
        raise ValueError("stagnation review is stale or future-dated; reassess progress")
    if (end - start).days < MINIMUM_STAGNATION_DAYS:
        raise ValueError("research budget enforcement requires at least 90 days without progress")
    if repo_root is not None:
        # Enforcement binds committed authority, never an inline self-grant.
        decision_path = f"ledger/decisions/{review['decision_id']}.yaml"
        try:
            raw = subprocess.check_output(
                ["git", "-C", str(repo_root), "show", f"HEAD:{decision_path}"],
                stderr=subprocess.PIPE, text=True)
            decision = yaml.safe_load(raw)["coordinator_decision"]
            if (not isinstance(decision, dict)
                    or decision.get("id") != review["decision_id"]
                    or decision.get("decision") != "approve"
                    or decision.get("decided_by") != "coordinator"
                    or decision.get("stagnation_review") != review):
                raise ValueError("stagnation review differs from its committed Coordinator approval")
            if target_id is not None and target_id not in decision.get("target_ids", []):
                raise ValueError("stagnation approval does not cover this target")
            limits = {k: v for k, v in budget.items()
                      if k not in ("enforcement", "stagnation_review")}
            if decision.get("approved_budget") != limits:
                raise ValueError("stagnation limits differ from the committed approved budget")
            for ref in refs:
                path = PurePosixPath(ref)
                if path.is_absolute() or ".." in path.parts or "\\" in ref:
                    raise ValueError("stagnation evidence must use repository-relative paths")
                subprocess.run(["git", "-C", str(repo_root), "cat-file", "-e",
                                f"HEAD:{ref}"], check=True, capture_output=True)
        except (OSError, subprocess.CalledProcessError, KeyError, TypeError, yaml.YAMLError) as exc:
            raise ValueError("stagnation enforcement requires committed decision and evidence") from exc
    return True


def agent_wall_limit(handoff, *, repo_root=None):
    """Explicit watchdogs remain independent of advisory research estimates."""
    limits = handoff.get("runtime_limits") or {}
    watchdog = limits.get("wall_clock_seconds")
    if watchdog is not None:
        watchdog = positive(watchdog, "runtime_limits.wall_clock_seconds")
        if not isinstance(limits.get("reason"), str) or not limits["reason"].strip():
            raise ValueError("an explicit process watchdog requires runtime_limits.reason")
    budget = handoff.get("budget") or {}
    if enforce_research_budget(budget, repo_root=repo_root, target_id=handoff.get("id")):
        cap = positive(budget.get("wall_clock_seconds"), "budget.wall_clock_seconds")
        return min(watchdog, cap) if watchdog is not None else cap
    return watchdog
