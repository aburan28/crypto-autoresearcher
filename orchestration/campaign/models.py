"""Small, dependency-free runtime models for campaign observation.

The Research Loop v2 proposal deliberately distinguishes authoritative ledger
records from derived runtime coordination.  These dataclasses model only the
latter: an expiring local-agent presence record and an advisory controller
lease.  Neither object is a research record and neither can change a goal,
queue, hypothesis, experiment, or archive.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


def utc_timestamp(value: float) -> str:
    """Render a stored UNIX timestamp as an explicit UTC RFC 3339 value."""

    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )


@dataclass(frozen=True)
class AgentPresence:
    """One expiring, non-authoritative agent heartbeat.

    The primary key is ``(workspace_id, campaign_id, agent_id, session_id)``.
    Keeping the session in the key prevents a stale process from replacing a
    newer session merely because it reused an opaque agent identifier.
    """

    workspace_id: str
    campaign_id: str
    agent_id: str
    session_id: str
    checked_in_at: float
    expires_at: float
    metadata: Mapping[str, Any]

    def is_live(self, now: float) -> bool:
        return self.expires_at > now

    def as_dict(self, *, now: float | None = None) -> dict[str, Any]:
        """Return a transport-safe, explicitly advisory presence summary."""

        payload: dict[str, Any] = {
            "workspace_id": self.workspace_id,
            "campaign_id": self.campaign_id,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "checked_in_at": utc_timestamp(self.checked_in_at),
            "expires_at": utc_timestamp(self.expires_at),
            "metadata": copy.deepcopy(dict(self.metadata)),
        }
        if now is not None:
            payload["live"] = self.is_live(now)
        # The peer-MCP server validates and supplies these compact fields.  A
        # direct store caller may use other metadata, which stays nested.
        for key in (
            "runtime",
            "role",
            "state",
            "summary",
            "write_scope",
            "task_id",
            "source_commit",
        ):
            if key in self.metadata:
                payload[key] = copy.deepcopy(self.metadata[key])
        return payload


@dataclass(frozen=True)
class ControllerLease:
    """A derived, epoch-protected local controller lease.

    A valid lease is necessary for a future controller process to avoid a
    split-brain runtime, but it is never sufficient to grant Coordinator
    authority.  Archive and ledger rules remain separately authoritative.
    """

    workspace_id: str
    campaign_id: str
    owner_id: str
    owner_session_id: str
    epoch: int
    acquired_at: float
    renewed_at: float
    expires_at: float
    source_commit: str | None = None

    def is_live(self, now: float) -> bool:
        # A pre-session-id row from an older local runtime is intentionally
        # not a valid controller lease after migration: it cannot establish a
        # per-process incarnation and therefore cannot fence split brain.
        return bool(self.owner_session_id) and self.expires_at > now

    def as_dict(self, *, now: float | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "workspace_id": self.workspace_id,
            "campaign_id": self.campaign_id,
            "owner_id": self.owner_id,
            "owner_session_id": self.owner_session_id,
            "epoch": self.epoch,
            "acquired_at": utc_timestamp(self.acquired_at),
            "renewed_at": utc_timestamp(self.renewed_at),
            "expires_at": utc_timestamp(self.expires_at),
            "source_commit": self.source_commit,
            "advisory_only": True,
            "authority": "none",
        }
        if now is not None:
            payload["live"] = self.is_live(now)
        return payload


__all__ = ["AgentPresence", "ControllerLease", "utc_timestamp"]
