from __future__ import annotations

import hashlib
from pathlib import Path
import hashlib

import pytest
import subprocess

from orchestration.campaign.checkpoint import checkpoint_by_batch, checkpoints
from orchestration.campaign.projection import ProjectionError, load_materialized_goal


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_flat_goal_projection_is_hash_bound_and_read_only(tmp_path: Path) -> None:
    _write(
        tmp_path / "ledger/goals/GOAL-TEST-001.yaml",
        """research_goal:
  id: GOAL-TEST-001
  status: active
  next_action: inspect the current evidence
""",
    )

    first = load_materialized_goal(tmp_path, "GOAL-TEST-001")
    second = load_materialized_goal(tmp_path, "GOAL-TEST-001")

    assert first.layout == "flat"
    assert first.record["status"] == "active"
    assert first.projection_hash == second.projection_hash
    assert first.source_files[0].path == "ledger/goals/GOAL-TEST-001.yaml"
    assert not (tmp_path / ".local").exists()


def test_sharded_goal_projection_merges_write_once_checkpoint_files(tmp_path: Path) -> None:
    _write(
        tmp_path / "ledger/goals/GOAL-TEST-002/goal.yaml",
        """research_goal:
  id: GOAL-TEST-002
  status: paused
  batch_checkpoints:
    - batch_id: BATCH-base
      note: base
""",
    )
    _write(
        tmp_path / "ledger/goals/GOAL-TEST-002/checkpoints/BATCH-b.yaml",
        """batch_checkpoint:
  batch_id: BATCH-b
  note: second
""",
    )
    _write(
        tmp_path / "ledger/goals/GOAL-TEST-002/checkpoints/BATCH-a.yaml",
        """batch_checkpoint:
  batch_id: BATCH-a
  note: first
""",
    )

    goal = load_materialized_goal(tmp_path, "GOAL-TEST-002")
    views = checkpoints(goal)

    assert goal.layout == "sharded"
    assert [entry["batch_id"] for entry in goal.record["batch_checkpoints"]] == [
        "BATCH-base",
        "BATCH-a",
        "BATCH-b",
    ]
    assert [view.batch_id for view in views] == ["BATCH-base", "BATCH-a", "BATCH-b"]
    assert checkpoint_by_batch(goal, "BATCH-a") == views[1]
    assert all(view.source_projection_hash == goal.projection_hash for view in views)
    assert len(goal.source_files) == 3


def _write_schema_supersession(
    tmp_path: Path, shard: Path, replacement: Path
) -> Path:
    registry = tmp_path / "tools/schema_supersession_registry.yaml"
    source_hash = hashlib.sha256(shard.read_bytes()).hexdigest()
    replacement_hash = hashlib.sha256(replacement.read_bytes()).hexdigest()
    _write(
        registry,
        f"""schema: schema-supersession-registry-v1
records:
  - kind: goal_checkpoint
    superseded_path: {shard.relative_to(tmp_path).as_posix()}
    superseded_sha256: {source_hash}
    superseding_path: {replacement.relative_to(tmp_path).as_posix()}
    superseding_sha256: {replacement_hash}
    defect: malformed checkpoint
    registered: '2026-08-08'
""",
    )
    return registry


def test_sharded_projection_uses_registered_schema_supersession(tmp_path: Path) -> None:
    head = tmp_path / "ledger/goals/GOAL-TEST-007/goal.yaml"
    shard = tmp_path / "ledger/goals/GOAL-TEST-007/checkpoints/BATCH-a.yaml"
    replacement = tmp_path / (
        "ledger/corrections/schema-supersessions/20260808/"
        "ledger__goals__GOAL-TEST-007__checkpoints__BATCH-a.v2.yaml"
    )
    _write(
        head,
        """research_goal:
  id: GOAL-TEST-007
  status: active
""",
    )
    _write(shard, "checkpoint_id: BATCH-a\n")
    _write(
        replacement,
        """batch_checkpoint:
  checkpoint_id: BATCH-a
  note: corrected
""",
    )
    registry = _write_schema_supersession(tmp_path, shard, replacement)

    goal = load_materialized_goal(tmp_path, "GOAL-TEST-007")
    views = checkpoints(goal)

    assert goal.record["batch_checkpoints"] == [
        {"checkpoint_id": "BATCH-a", "note": "corrected"}
    ]
    assert views[0].batch_id == "BATCH-a"
    assert checkpoint_by_batch(goal, "BATCH-a") == views[0]
    assert {source.path for source in goal.source_files} == {
        "ledger/goals/GOAL-TEST-007/goal.yaml",
        "ledger/goals/GOAL-TEST-007/checkpoints/BATCH-a.yaml",
        "ledger/corrections/schema-supersessions/20260808/"
        "ledger__goals__GOAL-TEST-007__checkpoints__BATCH-a.v2.yaml",
        registry.relative_to(tmp_path).as_posix(),
    }


def test_projection_refuses_dirty_schema_supersession_registry_in_git_worktree(
    tmp_path: Path,
) -> None:
    head = tmp_path / "ledger/goals/GOAL-TEST-008/goal.yaml"
    shard = tmp_path / "ledger/goals/GOAL-TEST-008/checkpoints/BATCH-a.yaml"
    replacement = tmp_path / (
        "ledger/corrections/schema-supersessions/20260808/"
        "ledger__goals__GOAL-TEST-008__checkpoints__BATCH-a.v2.yaml"
    )
    _write(head, "research_goal:\n  id: GOAL-TEST-008\n")
    _write(shard, "checkpoint_id: BATCH-a\n")
    _write(replacement, "batch_checkpoint:\n  batch_id: BATCH-a\n")
    registry = _write_schema_supersession(tmp_path, shard, replacement)
    for arguments in (
        ("init", "-q"),
        ("config", "user.email", "tests@example.invalid"),
        ("config", "user.name", "Campaign Tests"),
        ("add", "."),
        ("commit", "-qm", "fixture"),
    ):
        subprocess.run(["git", "-C", str(tmp_path), *arguments], check=True)

    clean = load_materialized_goal(tmp_path, "GOAL-TEST-008")
    assert clean.source_commit is not None
    registry.write_text(registry.read_text(encoding="utf-8") + "# local edit\n",
                        encoding="utf-8")

    with pytest.raises(ProjectionError, match="does not byte-match"):
        load_materialized_goal(tmp_path, "GOAL-TEST-008")


def test_sharded_projection_prefers_registered_supersession_before_parsing(
    tmp_path: Path,
) -> None:
    head = tmp_path / "ledger/goals/GOAL-TEST-009/goal.yaml"
    shard = tmp_path / "ledger/goals/GOAL-TEST-009/checkpoints/BATCH-a.yaml"
    replacement = tmp_path / (
        "ledger/corrections/schema-supersessions/20260808/"
        "ledger__goals__GOAL-TEST-009__checkpoints__BATCH-a.v2.yaml"
    )
    _write(head, "research_goal:\n  id: GOAL-TEST-009\n")
    _write(shard, "batch_checkpoint:\n  batch_id: BATCH-a\n  note: original\n")
    _write(replacement, "batch_checkpoint:\n  batch_id: BATCH-a\n  note: corrected\n")
    _write_schema_supersession(tmp_path, shard, replacement)

    goal = load_materialized_goal(tmp_path, "GOAL-TEST-009")

    assert goal.record["batch_checkpoints"] == [
        {"batch_id": "BATCH-a", "note": "corrected"}
    ]


def test_projection_rejects_schema_supersession_path_escape(tmp_path: Path) -> None:
    head = tmp_path / "ledger/goals/GOAL-TEST-010/goal.yaml"
    shard = tmp_path / "ledger/goals/GOAL-TEST-010/checkpoints/BATCH-a.yaml"
    _write(head, "research_goal:\n  id: GOAL-TEST-010\n")
    _write(shard, "batch_checkpoint:\n  batch_id: BATCH-a\n")
    source_hash = hashlib.sha256(shard.read_bytes()).hexdigest()
    _write(
        tmp_path / "tools/schema_supersession_registry.yaml",
        f"""schema: schema-supersession-registry-v1
records:
  - kind: goal_checkpoint
    superseded_path: ledger/goals/GOAL-TEST-010/checkpoints/BATCH-a.yaml
    superseded_sha256: {source_hash}
    superseding_path: ../outside.yaml
    superseding_sha256: {'0' * 64}
    defect: malformed checkpoint
    registered: '2026-08-08'
""",
    )

    with pytest.raises(ProjectionError, match="repository-relative"):
        load_materialized_goal(tmp_path, "GOAL-TEST-010")


def test_checkpoint_view_declines_conflicting_legacy_ids(tmp_path: Path) -> None:
    _write(
        tmp_path / "ledger/goals/GOAL-TEST-011.yaml",
        """research_goal:
  id: GOAL-TEST-011
  batch_checkpoints:
    - batch_id: BATCH-a
      checkpoint_id: BATCH-b
""",
    )

    goal = load_materialized_goal(tmp_path, "GOAL-TEST-011")
    views = checkpoints(goal)

    assert views[0].batch_id is None
    assert checkpoint_by_batch(goal, "BATCH-a") is None
    assert checkpoint_by_batch(goal, "BATCH-b") is None


def test_projection_refuses_ambiguous_or_malformed_legacy_layout(tmp_path: Path) -> None:
    _write(
        tmp_path / "ledger/goals/GOAL-TEST-003.yaml",
        "research_goal:\n  id: GOAL-TEST-003\n",
    )
    _write(
        tmp_path / "ledger/goals/GOAL-TEST-003/goal.yaml",
        "research_goal:\n  id: GOAL-TEST-003\n",
    )

    with pytest.raises(ProjectionError, match="ambiguous"):
        load_materialized_goal(tmp_path, "GOAL-TEST-003")

    with pytest.raises(ProjectionError, match="safe GOAL"):
        load_materialized_goal(tmp_path, "../../not-a-goal")


def test_projection_refuses_dirty_goal_sources_in_a_git_worktree(tmp_path: Path) -> None:
    path = tmp_path / "ledger/goals/GOAL-TEST-004.yaml"
    _write(
        path,
        """research_goal:
  id: GOAL-TEST-004
  status: active
""",
    )
    for arguments in (
        ("init", "-q"),
        ("config", "user.email", "tests@example.invalid"),
        ("config", "user.name", "Campaign Tests"),
        ("add", "ledger/goals/GOAL-TEST-004.yaml"),
        ("commit", "-qm", "fixture"),
    ):
        subprocess.run(["git", "-C", str(tmp_path), *arguments], check=True)

    clean = load_materialized_goal(tmp_path, "GOAL-TEST-004")
    assert clean.source_commit is not None
    _write(
        path,
        """research_goal:
  id: GOAL-TEST-004
  status: paused
""",
    )
    with pytest.raises(ProjectionError, match="does not byte-match"):
        load_materialized_goal(tmp_path, "GOAL-TEST-004")


def test_projection_refuses_untracked_goal_source_in_a_git_worktree(tmp_path: Path) -> None:
    _write(tmp_path / "README.md", "fixture\n")
    for arguments in (
        ("init", "-q"),
        ("config", "user.email", "tests@example.invalid"),
        ("config", "user.name", "Campaign Tests"),
        ("add", "README.md"),
        ("commit", "-qm", "fixture"),
    ):
        subprocess.run(["git", "-C", str(tmp_path), *arguments], check=True)
    _write(
        tmp_path / "ledger/goals/GOAL-TEST-005.yaml",
        "research_goal:\n  id: GOAL-TEST-005\n  status: active\n",
    )

    with pytest.raises(ProjectionError, match="not a tracked HEAD blob"):
        load_materialized_goal(tmp_path, "GOAL-TEST-005")


@pytest.mark.skipif(not hasattr(Path, "symlink_to"), reason="platform has no symlink support")
def test_projection_refuses_tracked_symlink_source_even_when_git_is_clean(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-goal.yaml"
    _write(
        outside,
        "research_goal:\n  id: GOAL-TEST-006\n  status: active\n",
    )
    source = tmp_path / "ledger/goals/GOAL-TEST-006.yaml"
    source.parent.mkdir(parents=True)
    source.symlink_to(outside)
    for arguments in (
        ("init", "-q"),
        ("config", "user.email", "tests@example.invalid"),
        ("config", "user.name", "Campaign Tests"),
        ("add", "ledger/goals/GOAL-TEST-006.yaml"),
        ("commit", "-qm", "tracked symlink fixture"),
    ):
        subprocess.run(["git", "-C", str(tmp_path), *arguments], check=True)

    with pytest.raises(ProjectionError, match="symlink"):
        load_materialized_goal(tmp_path, "GOAL-TEST-006")
