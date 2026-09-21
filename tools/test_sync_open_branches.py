"""Tests for the periodic branch-sync decision logic.

Only the pure parts are covered: which pull requests are excluded, and the
comment-marker keying that stops a stuck branch from being reported every six
hours. The git and `gh` calls are exercised by running the tool with
`--dry-run`, not from a unit test.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sync_open_branches as sync  # noqa: E402


def pr(**overrides):
    base = {
        "number": 1,
        "headRefName": "feat/x",
        "baseRefName": "main",
        "isCrossRepository": False,
        "isDraft": False,
        "mergeable": "MERGEABLE",
        "labels": [],
    }
    base.update(overrides)
    return base


def test_ordinary_pull_request_is_synced():
    assert sync.skip_reason(pr(), "main") is None


def test_fork_is_skipped_because_the_token_cannot_push():
    reason = sync.skip_reason(pr(isCrossRepository=True), "main")
    assert reason and "fork" in reason


def test_opt_out_label_is_honoured():
    reason = sync.skip_reason(pr(labels=[{"name": sync.SKIP_LABEL}]), "main")
    assert reason and sync.SKIP_LABEL in reason


def test_unrelated_labels_do_not_opt_out():
    assert sync.skip_reason(pr(labels=[{"name": "research"}]), "main") is None


def test_pull_request_against_another_base_is_left_alone():
    reason = sync.skip_reason(pr(baseRefName="release"), "main")
    assert reason and "release" in reason


def test_conflicted_draft_is_left_to_its_author():
    reason = sync.skip_reason(pr(isDraft=True, mergeable="CONFLICTING"), "main")
    assert reason and "draft" in reason


def test_clean_draft_is_still_synced():
    assert sync.skip_reason(pr(isDraft=True), "main") is None


def test_marker_is_stable_for_one_base_tip():
    assert sync.marker(7, "a" * 40) == sync.marker(7, "a" * 40)


def test_marker_changes_when_the_base_moves():
    assert sync.marker(7, "a" * 40) != sync.marker(7, "b" * 40)


def test_marker_distinguishes_pull_requests():
    assert sync.marker(7, "a" * 40) != sync.marker(8, "a" * 40)


# Conflicts on a generated path are resolved by REMOVAL, so a false positive
# here deletes a tracked research artifact on a six-hourly schedule. Both
# directions are pinned: the generated files must still be recognised.


def test_generated_paths_are_recognised():
    assert sync.is_generated("knowledge/INDEX.md")
    assert sync.is_generated("coordination/goals/G/batches/B/dispatch_plan.json")
    assert sync.is_generated("coordination/goals/G/batches/B/plan/dispatch_plan.md")


def test_a_name_merely_ending_in_a_generated_name_is_not_generated():
    # Twenty of these are tracked reconciliation-campaign artifacts. A bare
    # endswith() matched every one of them and would have removed them.
    assert not sync.is_generated(
        "coordination/reconciliation/R/enforceability_repair_dispatch_plan.json")
    assert not sync.is_generated(
        "coordination/reconciliation/R/live_probe_dispatch_plan.md")
    assert not sync.is_generated("knowledge/OTHER_INDEX.md")
