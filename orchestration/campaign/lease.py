"""Atomic, derived controller-lease operations.

This module is intentionally an internal control-plane primitive.  The
peer-facing MCP server may *observe* a lease, but it never exposes acquire,
renew, release, or assertion operations to arbitrary local agents.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from .models import ControllerLease

if TYPE_CHECKING:  # pragma: no cover - imported only by type checkers
    from .store import CampaignStore


class LeaseError(RuntimeError):
    """Base class for expected derived-lease failures."""


class LeaseConflictError(LeaseError):
    """Raised when a different live owner already holds a campaign lease."""


class LeaseNotOwnedError(LeaseError):
    """Raised when a stale, expired, or different owner touches a lease."""


class LeaseManager:
    """Lease operations backed by one :class:`CampaignStore` SQLite database."""

    def __init__(self, store: "CampaignStore") -> None:
        self._store = store

    def get(
        self,
        workspace_id: str,
        campaign_id: str,
        *,
        include_expired: bool = False,
    ) -> ControllerLease | None:
        """Return one lease observation, optionally including an expired row."""

        workspace, campaign = self._store._scope(workspace_id, campaign_id)
        with self._store._transaction() as connection:
            now = self._store._now()
            row = connection.execute(
                """
                SELECT workspace_id, campaign_id, owner_id, owner_session_id, epoch, acquired_at,
                       renewed_at, expires_at, source_commit
                  FROM campaign_leases
                 WHERE workspace_id = ? AND campaign_id = ?
                """,
                (workspace, campaign),
            ).fetchone()
        if row is None:
            return None
        lease = self._store._lease_from_row(row)
        if not include_expired and not lease.is_live(now):
            return None
        return lease

    inspect = get

    def acquire(
        self,
        workspace_id: str,
        campaign_id: str,
        owner_id: str,
        *,
        owner_session_id: str,
        ttl_seconds: int = 60,
        source_commit: str | None = None,
    ) -> ControllerLease:
        """Atomically acquire a lease or fail if another live owner holds it.

        Expired/released rows remain in SQLite so each successful owner gains a
        strictly increasing epoch.  That fencing token prevents a late owner
        from renewing a lease after a newer controller has taken over.
        """

        workspace, campaign = self._store._scope(workspace_id, campaign_id)
        owner = self._store._identifier(owner_id, "owner_id")
        session = self._store._identifier(owner_session_id, "owner_session_id")
        ttl = self._store._ttl(ttl_seconds)
        commit = self._store._optional_identifier(source_commit, "source_commit")
        with self._store._transaction(write=True) as connection:
            # Sample time only after SQLite grants the write transaction.  A
            # timestamp captured before a lock wait can otherwise let a stale
            # owner appear live or renew an expired lease.
            now = self._store._now()
            row = connection.execute(
                """
                SELECT workspace_id, campaign_id, owner_id, owner_session_id, epoch, acquired_at,
                       renewed_at, expires_at, source_commit
                  FROM campaign_leases
                 WHERE workspace_id = ? AND campaign_id = ?
                """,
                (workspace, campaign),
            ).fetchone()
            if row is not None:
                current = self._store._lease_from_row(row)
                if current.is_live(now):
                    if current.owner_id != owner or current.owner_session_id != session:
                        raise LeaseConflictError(
                            f"campaign {campaign!r} already has live owner "
                            f"{current.owner_id!r}/{current.owner_session_id!r} "
                            f"at epoch {current.epoch}"
                        )
                    # Idempotence applies only to the same per-process session;
                    # a second process reusing a stable owner label conflicts.
                    return current
                epoch = current.epoch + 1
            else:
                epoch = 1
            lease = ControllerLease(
                workspace_id=workspace,
                campaign_id=campaign,
                owner_id=owner,
                owner_session_id=session,
                epoch=epoch,
                acquired_at=now,
                renewed_at=now,
                expires_at=now + ttl,
                source_commit=commit,
            )
            cursor = connection.execute(
                """
                INSERT INTO campaign_leases (
                    workspace_id, campaign_id, owner_id, owner_session_id, epoch, acquired_at,
                    renewed_at, expires_at, source_commit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(workspace_id, campaign_id) DO UPDATE SET
                    owner_id = excluded.owner_id,
                    owner_session_id = excluded.owner_session_id,
                    epoch = excluded.epoch,
                    acquired_at = excluded.acquired_at,
                    renewed_at = excluded.renewed_at,
                    expires_at = excluded.expires_at,
                    source_commit = excluded.source_commit
                """,
                (
                    lease.workspace_id,
                    lease.campaign_id,
                    lease.owner_id,
                    lease.owner_session_id,
                    lease.epoch,
                    lease.acquired_at,
                    lease.renewed_at,
                    lease.expires_at,
                    lease.source_commit,
                ),
            )
        return lease

    def renew(
        self,
        workspace_id: str,
        campaign_id: str,
        owner_id: str,
        epoch: int,
        *,
        owner_session_id: str,
        ttl_seconds: int = 60,
        source_commit: str | None = None,
    ) -> ControllerLease:
        """Renew exactly the current live owner/epoch, never a stale lease."""

        workspace, campaign = self._store._scope(workspace_id, campaign_id)
        owner = self._store._identifier(owner_id, "owner_id")
        session = self._store._identifier(owner_session_id, "owner_session_id")
        if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1:
            raise LeaseNotOwnedError("epoch must be a positive integer")
        ttl = self._store._ttl(ttl_seconds)
        commit = self._store._optional_identifier(source_commit, "source_commit")
        with self._store._transaction(write=True) as connection:
            now = self._store._now()
            row = connection.execute(
                """
                SELECT workspace_id, campaign_id, owner_id, owner_session_id, epoch, acquired_at,
                       renewed_at, expires_at, source_commit
                  FROM campaign_leases
                 WHERE workspace_id = ? AND campaign_id = ?
                """,
                (workspace, campaign),
            ).fetchone()
            if row is None:
                raise LeaseNotOwnedError("no controller lease exists")
            current = self._store._lease_from_row(row)
            if (
                current.owner_id != owner
                or current.owner_session_id != session
                or current.epoch != epoch
                or not current.is_live(now)
            ):
                raise LeaseNotOwnedError("lease owner, epoch, or expiry no longer matches")
            lease = ControllerLease(
                workspace_id=workspace,
                campaign_id=campaign,
                owner_id=owner,
                owner_session_id=session,
                epoch=epoch,
                acquired_at=current.acquired_at,
                renewed_at=now,
                expires_at=now + ttl,
                source_commit=commit if commit is not None else current.source_commit,
            )
            cursor = connection.execute(
                """
                UPDATE campaign_leases
                   SET renewed_at = ?, expires_at = ?, source_commit = ?
                 WHERE workspace_id = ? AND campaign_id = ? AND owner_id = ? AND epoch = ?
                   AND owner_session_id = ? AND expires_at > ?
                """,
                (
                    lease.renewed_at,
                    lease.expires_at,
                    lease.source_commit,
                    workspace,
                    campaign,
                    owner,
                    epoch,
                    session,
                    now,
                ),
            )
            if cursor.rowcount != 1:  # defensive fencing guard
                raise LeaseNotOwnedError("lease expired before renewal completed")
        return lease

    def release(
        self,
        workspace_id: str,
        campaign_id: str,
        owner_id: str,
        epoch: int,
        *,
        owner_session_id: str,
    ) -> ControllerLease:
        """Expire a lease owned by the matching controller and epoch.

        Rows are retained to preserve epoch monotonicity.  The returned lease
        is expired and is useful only as an operation receipt.
        """

        workspace, campaign = self._store._scope(workspace_id, campaign_id)
        owner = self._store._identifier(owner_id, "owner_id")
        session = self._store._identifier(owner_session_id, "owner_session_id")
        if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1:
            raise LeaseNotOwnedError("epoch must be a positive integer")
        with self._store._transaction(write=True) as connection:
            now = self._store._now()
            row = connection.execute(
                """
                SELECT workspace_id, campaign_id, owner_id, owner_session_id, epoch, acquired_at,
                       renewed_at, expires_at, source_commit
                  FROM campaign_leases
                 WHERE workspace_id = ? AND campaign_id = ?
                """,
                (workspace, campaign),
            ).fetchone()
            if row is None:
                raise LeaseNotOwnedError("no controller lease exists")
            current = self._store._lease_from_row(row)
            if (
                current.owner_id != owner
                or current.owner_session_id != session
                or current.epoch != epoch
                or not current.is_live(now)
            ):
                raise LeaseNotOwnedError("lease owner or epoch no longer matches")
            lease = ControllerLease(
                workspace_id=workspace,
                campaign_id=campaign,
                owner_id=owner,
                owner_session_id=session,
                epoch=epoch,
                acquired_at=current.acquired_at,
                renewed_at=now,
                expires_at=now,
                source_commit=current.source_commit,
            )
            cursor = connection.execute(
                """
                UPDATE campaign_leases
                   SET renewed_at = ?, expires_at = ?
                 WHERE workspace_id = ? AND campaign_id = ? AND owner_id = ? AND epoch = ?
                   AND owner_session_id = ? AND expires_at > ?
                """,
                (now, now, workspace, campaign, owner, epoch, session, now),
            )
            if cursor.rowcount != 1:  # defensive fencing guard
                raise LeaseNotOwnedError("lease expired before release completed")
        return lease

    def assert_owner(
        self,
        workspace_id: str,
        campaign_id: str,
        owner_id: str,
        epoch: int,
        *,
        owner_session_id: str,
    ) -> ControllerLease:
        """Return the current lease only when this exact live owner still holds it."""

        owner = self._store._identifier(owner_id, "owner_id")
        session = self._store._identifier(owner_session_id, "owner_session_id")
        lease = self.get(workspace_id, campaign_id)
        if (
            lease is None
            or lease.owner_id != owner
            or lease.owner_session_id != session
            or lease.epoch != epoch
        ):
            raise LeaseNotOwnedError("lease owner, epoch, or expiry no longer matches")
        return lease


__all__ = ["LeaseConflictError", "LeaseError", "LeaseManager", "LeaseNotOwnedError"]
