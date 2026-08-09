"""SQLite-backed, rebuildable local campaign coordination state.

The database stores short-lived peer heartbeats and an internal controller
lease only.  It is deliberately not a ledger cache with write authority: no
method touches dispatch queues, archive records, goals, hypotheses, evidence,
or experiment artifacts.
"""
from __future__ import annotations

import json
import math
import os
import sqlite3
import stat
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping

from .lease import LeaseManager
from .models import AgentPresence, ControllerLease


class CampaignStoreError(ValueError):
    """Raised for invalid derived coordination input or SQLite setup failures."""


class CampaignStore:
    """A small cross-client state store, partitioned by workspace and campaign.

    The process owns one connection protected by an ``RLock``.  SQLite's
    ``BEGIN IMMEDIATE`` transactions make lease acquisition atomic across
    daemon processes pointing at the same durable file; the lock also makes
    ``:memory:`` useful in focused tests.
    """

    MIN_TTL_SECONDS = 15
    MAX_TTL_SECONDS = 300
    DEFAULT_TTL_SECONDS = 60
    MAX_IDENTIFIER_LENGTH = 256
    MAX_METADATA_BYTES = 16_384
    MAX_ACTIVE_PRESENCES_PER_SCOPE = 256
    # The peer daemon is a same-host advisory service.  A local process can
    # still submit arbitrary *valid* GOAL scopes, so bound the entire live
    # footprint as well as each workspace/campaign partition.  Expired rows
    # are pruned in the same transaction before either quota is evaluated.
    MAX_ACTIVE_PRESENCES_TOTAL = 1_024

    def __init__(
        self,
        db_path: str | Path,
        *,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.path = (
            self._absolute_no_resolve(Path(db_path).expanduser())
            if str(db_path) != ":memory:"
            else None
        )
        self._clock = clock
        self._lock = threading.RLock()
        if self.path is not None:
            try:
                self._prepare_private_state_path(self.path)
            except OSError as exc:
                raise CampaignStoreError(f"cannot create campaign state directory: {exc}") from exc
            target = str(self.path)
        else:
            target = ":memory:"
        try:
            self._connection = sqlite3.connect(
                target,
                timeout=5.0,
                isolation_level=None,
                check_same_thread=False,
            )
        except sqlite3.Error as exc:
            raise CampaignStoreError(f"cannot open campaign state database: {exc}") from exc
        self._connection.row_factory = sqlite3.Row
        try:
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.execute("PRAGMA busy_timeout = 5000")
            if self.path is not None:
                self._connection.execute("PRAGMA journal_mode = WAL")
                self._connection.execute("PRAGMA synchronous = NORMAL")
            self._initialize()
            self._harden_database_files()
        except sqlite3.Error as exc:
            self._connection.close()
            raise CampaignStoreError(f"cannot initialize campaign state database: {exc}") from exc
        self.leases = LeaseManager(self)

    @staticmethod
    def _absolute_no_resolve(path: Path) -> Path:
        """Normalize a path without following an attacker-controlled symlink."""

        return Path(os.path.abspath(os.fspath(path)))

    @staticmethod
    def _existing_components(path: Path) -> Iterator[Path]:
        """Yield path components that already exist, without resolving links."""

        current = Path(path.anchor)
        for part in path.parts[1:]:
            current /= part
            # ``exists`` is false for a dangling symlink, so include lstat's
            # symlink case explicitly.
            if current.exists() or current.is_symlink():
                yield current

    @classmethod
    def _reject_symlink_components(cls, path: Path) -> None:
        for component in cls._existing_components(path):
            if stat.S_ISLNK(component.lstat().st_mode):
                raise CampaignStoreError(
                    f"campaign state path may not traverse symlink component {component}"
                )

    @classmethod
    def _prepare_private_state_path(cls, path: Path) -> None:
        """Create a user-private leaf directory and reject symlink redirection."""

        cls._reject_symlink_components(path)
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        cls._reject_symlink_components(path)
        parent_stat = path.parent.lstat()
        if not stat.S_ISDIR(parent_stat.st_mode):
            raise CampaignStoreError("campaign state parent is not a directory")
        # The final directory is controlled by this daemon and contains the
        # state file/WAL/SHM.  Harden it even if an inherited umask created it
        # broader than desired.
        os.chmod(path.parent, 0o700)
        if path.exists() or path.is_symlink():
            if path.is_symlink():
                raise CampaignStoreError("campaign state database may not be a symlink")
            if not stat.S_ISREG(path.lstat().st_mode):
                raise CampaignStoreError("campaign state database must be a regular file")

    def _harden_database_files(self) -> None:
        """Ensure SQLite's main and sidecar files stay readable only by this user."""

        if self.path is None:
            return
        for path in (
            self.path,
            Path(str(self.path) + "-wal"),
            Path(str(self.path) + "-shm"),
            Path(str(self.path) + "-journal"),
        ):
            if path.exists():
                if path.is_symlink():
                    raise CampaignStoreError("campaign state sidecar may not be a symlink")
                os.chmod(path, 0o600)

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    def __enter__(self) -> "CampaignStore":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _initialize(self) -> None:
        with self._lock:
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS agent_presence (
                    workspace_id TEXT NOT NULL,
                    campaign_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    checked_in_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    metadata_json TEXT NOT NULL,
                    PRIMARY KEY (workspace_id, campaign_id, agent_id, session_id)
                );
                CREATE INDEX IF NOT EXISTS agent_presence_live_idx
                    ON agent_presence (workspace_id, campaign_id, expires_at);

                CREATE TABLE IF NOT EXISTS campaign_leases (
                    workspace_id TEXT NOT NULL,
                    campaign_id TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    owner_session_id TEXT NOT NULL,
                    epoch INTEGER NOT NULL CHECK (epoch > 0),
                    acquired_at REAL NOT NULL,
                    renewed_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    source_commit TEXT,
                    PRIMARY KEY (workspace_id, campaign_id)
                );
                """
            )
            # A short-lived first implementation did not persist a per-process
            # lease incarnation.  Preserve the row/epoch for auditability but
            # mark it invalid (empty session) so it cannot survive as a live
            # owner after the split-brain fencing upgrade.
            columns = {
                str(row["name"])
                for row in self._connection.execute("PRAGMA table_info(campaign_leases)")
            }
            if "owner_session_id" not in columns:
                self._connection.execute(
                    "ALTER TABLE campaign_leases "
                    "ADD COLUMN owner_session_id TEXT NOT NULL DEFAULT ''"
                )

    @contextmanager
    def _transaction(self, *, write: bool = False) -> Iterator[sqlite3.Connection]:
        """Run one atomic database interaction while serializing this process."""

        with self._lock:
            connection = self._connection
            committed = False
            try:
                connection.execute("BEGIN IMMEDIATE" if write else "BEGIN")
                yield connection
                connection.execute("COMMIT")
                committed = True
                if write:
                    self._harden_database_files()
            except BaseException:
                if not committed:
                    try:
                        connection.execute("ROLLBACK")
                    except sqlite3.Error:
                        pass
                raise

    def _now(self) -> float:
        value = self._clock()
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            raise CampaignStoreError("clock must return a finite UNIX timestamp")
        return float(value)

    @classmethod
    def _identifier(cls, value: str, name: str) -> str:
        if not isinstance(value, str):
            raise CampaignStoreError(f"{name} must be a string")
        normalized = value.strip()
        if not normalized or len(normalized) > cls.MAX_IDENTIFIER_LENGTH:
            raise CampaignStoreError(
                f"{name} must contain 1..{cls.MAX_IDENTIFIER_LENGTH} nonblank characters"
            )
        if any(ord(character) < 32 or ord(character) == 127 for character in normalized):
            raise CampaignStoreError(f"{name} may not contain control characters")
        return normalized

    @classmethod
    def _optional_identifier(cls, value: str | None, name: str) -> str | None:
        return None if value is None else cls._identifier(value, name)

    @classmethod
    def _scope(cls, workspace_id: str, campaign_id: str) -> tuple[str, str]:
        return cls._identifier(workspace_id, "workspace_id"), cls._identifier(
            campaign_id, "campaign_id"
        )

    @classmethod
    def _ttl(cls, value: int) -> int:
        if not isinstance(value, int) or isinstance(value, bool):
            raise CampaignStoreError("ttl_seconds must be an integer")
        if not cls.MIN_TTL_SECONDS <= value <= cls.MAX_TTL_SECONDS:
            raise CampaignStoreError(
                f"ttl_seconds must be between {cls.MIN_TTL_SECONDS} and {cls.MAX_TTL_SECONDS}"
            )
        return value

    @classmethod
    def _metadata_json(cls, metadata: Mapping[str, Any] | None) -> str:
        if metadata is None:
            metadata = {}
        if not isinstance(metadata, Mapping):
            raise CampaignStoreError("metadata must be a JSON-object mapping")
        try:
            encoded = json.dumps(
                dict(metadata),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            )
        except (TypeError, ValueError) as exc:
            raise CampaignStoreError(f"metadata must be JSON-safe: {exc}") from exc
        if len(encoded.encode("utf-8")) > cls.MAX_METADATA_BYTES:
            raise CampaignStoreError(
                f"metadata exceeds {cls.MAX_METADATA_BYTES} UTF-8 bytes"
            )
        return encoded

    @staticmethod
    def _presence_from_row(row: sqlite3.Row) -> AgentPresence:
        try:
            metadata = json.loads(row["metadata_json"])
        except (KeyError, TypeError, json.JSONDecodeError) as exc:  # defensive corruption check
            raise CampaignStoreError("stored agent presence metadata is malformed") from exc
        if not isinstance(metadata, dict):
            raise CampaignStoreError("stored agent presence metadata is not a JSON object")
        return AgentPresence(
            workspace_id=str(row["workspace_id"]),
            campaign_id=str(row["campaign_id"]),
            agent_id=str(row["agent_id"]),
            session_id=str(row["session_id"]),
            checked_in_at=float(row["checked_in_at"]),
            expires_at=float(row["expires_at"]),
            metadata=metadata,
        )

    @staticmethod
    def _lease_from_row(row: sqlite3.Row) -> ControllerLease:
        return ControllerLease(
            workspace_id=str(row["workspace_id"]),
            campaign_id=str(row["campaign_id"]),
            owner_id=str(row["owner_id"]),
            owner_session_id=str(row["owner_session_id"] or ""),
            epoch=int(row["epoch"]),
            acquired_at=float(row["acquired_at"]),
            renewed_at=float(row["renewed_at"]),
            expires_at=float(row["expires_at"]),
            source_commit=(str(row["source_commit"]) if row["source_commit"] else None),
        )

    def check_in(
        self,
        workspace_id: str,
        campaign_id: str,
        agent_id: str,
        *,
        session_id: str,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        metadata: Mapping[str, Any] | None = None,
    ) -> AgentPresence:
        """Idempotently upsert one short-lived local agent heartbeat."""

        workspace, campaign = self._scope(workspace_id, campaign_id)
        agent = self._identifier(agent_id, "agent_id")
        session = self._identifier(session_id, "session_id")
        ttl = self._ttl(ttl_seconds)
        metadata_json = self._metadata_json(metadata)
        now = self._now()
        presence = AgentPresence(
            workspace_id=workspace,
            campaign_id=campaign,
            agent_id=agent,
            session_id=session,
            checked_in_at=now,
            expires_at=now + ttl,
            metadata=json.loads(metadata_json),
        )
        with self._transaction(write=True) as connection:
            # Presence is derived telemetry.  Remove stale rows opportunistically
            # before adding a live heartbeat so crashed clients cannot create an
            # unbounded SQLite accumulation over a long-running daemon.
            connection.execute("DELETE FROM agent_presence WHERE expires_at <= ?", (now,))
            existing = connection.execute(
                """
                SELECT 1 FROM agent_presence
                 WHERE workspace_id = ? AND campaign_id = ?
                   AND agent_id = ? AND session_id = ?
                """,
                (workspace, campaign, agent, session),
            ).fetchone()
            if existing is None:
                count = connection.execute(
                    """
                    SELECT COUNT(*) FROM agent_presence
                     WHERE workspace_id = ? AND campaign_id = ?
                    """,
                    (workspace, campaign),
                ).fetchone()[0]
                if int(count) >= self.MAX_ACTIVE_PRESENCES_PER_SCOPE:
                    raise CampaignStoreError(
                        "too many live peer sessions in this workspace/campaign scope"
                    )
                total = connection.execute(
                    "SELECT COUNT(*) FROM agent_presence"
                ).fetchone()[0]
                if int(total) >= self.MAX_ACTIVE_PRESENCES_TOTAL:
                    raise CampaignStoreError(
                        "too many live peer sessions across this local daemon"
                    )
            connection.execute(
                """
                INSERT INTO agent_presence (
                    workspace_id, campaign_id, agent_id, session_id,
                    checked_in_at, expires_at, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(workspace_id, campaign_id, agent_id, session_id) DO UPDATE SET
                    checked_in_at = excluded.checked_in_at,
                    expires_at = excluded.expires_at,
                    metadata_json = excluded.metadata_json
                """,
                (
                    presence.workspace_id,
                    presence.campaign_id,
                    presence.agent_id,
                    presence.session_id,
                    presence.checked_in_at,
                    presence.expires_at,
                    metadata_json,
                ),
            )
        return presence

    record_check_in = check_in

    def check_out(
        self,
        workspace_id: str,
        campaign_id: str,
        agent_id: str,
        *,
        session_id: str,
    ) -> bool:
        """Remove exactly one local session early; absence is idempotent."""

        workspace, campaign = self._scope(workspace_id, campaign_id)
        agent = self._identifier(agent_id, "agent_id")
        session = self._identifier(session_id, "session_id")
        with self._transaction(write=True) as connection:
            cursor = connection.execute(
                """
                DELETE FROM agent_presence
                 WHERE workspace_id = ? AND campaign_id = ?
                   AND agent_id = ? AND session_id = ?
                """,
                (workspace, campaign, agent, session),
            )
        return cursor.rowcount > 0

    def list_agents(
        self,
        workspace_id: str,
        campaign_id: str,
        *,
        include_stale: bool = True,
    ) -> list[AgentPresence]:
        """List presence rows ordered deterministically, optionally live only."""

        workspace, campaign = self._scope(workspace_id, campaign_id)
        now = self._now()
        condition = "" if include_stale else " AND expires_at > ?"
        parameters: tuple[object, ...] = (workspace, campaign)
        if not include_stale:
            parameters += (now,)
        with self._transaction() as connection:
            rows = connection.execute(
                """
                SELECT workspace_id, campaign_id, agent_id, session_id,
                       checked_in_at, expires_at, metadata_json
                  FROM agent_presence
                 WHERE workspace_id = ? AND campaign_id = ?
                """
                + condition
                + " ORDER BY checked_in_at ASC, agent_id ASC, session_id ASC",
                parameters,
            ).fetchall()
        return [self._presence_from_row(row) for row in rows]

    def live_agents(self, workspace_id: str, campaign_id: str) -> list[AgentPresence]:
        """Return only rows whose TTL has not expired at read time."""

        return self.list_agents(workspace_id, campaign_id, include_stale=False)


__all__ = ["CampaignStore", "CampaignStoreError"]
