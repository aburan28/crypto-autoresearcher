"""Read-only helpers over materialized legacy goal checkpoints.

This module intentionally does *not* write proposal-era campaign checkpoints.
Until a checkpoint has travelled through the Coordinator archive lifecycle, a
runtime database must not manufacture an equivalent research-state transition.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from .projection import MaterializedGoal, canonical_json, sha256


@dataclass(frozen=True)
class CheckpointView:
    """A hash-bound view of one existing legacy batch checkpoint."""

    goal_id: str
    batch_id: str | None
    index: int
    entry: dict[str, Any]
    source_projection_hash: str
    checkpoint_hash: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "crypto.autoresearch.checkpoint_view.v1",
            "goal_id": self.goal_id,
            "batch_id": self.batch_id,
            "index": self.index,
            "entry": copy.deepcopy(self.entry),
            "source_projection_hash": self.source_projection_hash,
            "checkpoint_hash": self.checkpoint_hash,
            "advisory_only": True,
        }


def checkpoints(goal: MaterializedGoal) -> tuple[CheckpointView, ...]:
    """Return existing checkpoint entries without imposing new semantics."""

    values = goal.record.get("batch_checkpoints") or []
    if not isinstance(values, list):
        return ()
    result: list[CheckpointView] = []
    for index, raw in enumerate(values):
        if not isinstance(raw, dict):
            # Authoritative ledger validation will diagnose malformed legacy
            # content.  A derived observer must not reinterpret it as a valid
            # checkpoint.
            continue
        entry = copy.deepcopy(raw)
        batch_id = entry.get("batch_id")
        checkpoint_id = entry.get("checkpoint_id")
        if isinstance(batch_id, str):
            # Some legacy checkpoint records use ``checkpoint_id`` instead of
            # ``batch_id``.  When both are present, fail closed on a conflict
            # rather than silently choosing an identifier for lookup.
            if isinstance(checkpoint_id, str) and checkpoint_id != batch_id:
                batch_id = None
        elif isinstance(checkpoint_id, str):
            batch_id = checkpoint_id
        else:
            batch_id = None
        payload = {
            "schema": "crypto.autoresearch.checkpoint_view.v1",
            "goal_id": goal.goal_id,
            "index": index,
            "entry": entry,
            "source_projection_hash": goal.projection_hash,
        }
        result.append(
            CheckpointView(
                goal_id=goal.goal_id,
                batch_id=batch_id,
                index=index,
                entry=entry,
                source_projection_hash=goal.projection_hash,
                checkpoint_hash=sha256(payload),
            )
        )
    return tuple(result)


def checkpoint_by_batch(goal: MaterializedGoal, batch_id: str) -> CheckpointView | None:
    """Find one projected legacy batch checkpoint by its existing identifier."""

    for view in checkpoints(goal):
        if view.batch_id == batch_id:
            return view
    return None


__all__ = ["CheckpointView", "checkpoint_by_batch", "checkpoints", "canonical_json"]
