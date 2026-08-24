"""Focused safety tests for derived local campaign coordination state."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import os
import stat
from pathlib import Path

import pytest

from orchestration.campaign.lease import LeaseConflictError, LeaseNotOwnedError
from orchestration.campaign.store import CampaignStore, CampaignStoreError


class Clock:
    def __init__(self, value: float = 1_700_000_000.0) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def test_check_ins_are_scoped_idempotent_and_expire(tmp_path: Path) -> None:
    clock = Clock()
    store = CampaignStore(tmp_path / "peer.sqlite", clock=clock)
    try:
        first = store.check_in(
            "workspace-A",
            "GOAL-TEST-001",
            "codex-agent",
            session_id="session-1",
            ttl_seconds=30,
            metadata={
                "runtime": "codex",
                "state": "working",
                "summary": "checking control coverage",
                "write_scope": ["reports/control.md"],
            },
        )
        clock.advance(5)
        renewed = store.record_check_in(
            "workspace-A",
            "GOAL-TEST-001",
            "codex-agent",
            session_id="session-1",
            ttl_seconds=30,
            metadata={"runtime": "codex", "state": "waiting"},
        )

        assert renewed.checked_in_at > first.checked_in_at
        assert renewed.expires_at > first.expires_at
        live = store.live_agents("workspace-A", "GOAL-TEST-001")
        assert len(live) == 1
        assert live[0].metadata["state"] == "waiting"
        assert store.live_agents("workspace-B", "GOAL-TEST-001") == []
        assert store.live_agents("workspace-A", "GOAL-OTHER-001") == []

        clock.advance(31)
        assert store.live_agents("workspace-A", "GOAL-TEST-001") == []
        stale = store.list_agents("workspace-A", "GOAL-TEST-001")
        assert len(stale) == 1
        assert stale[0].is_live(clock()) is False
    finally:
        store.close()


def test_check_out_is_session_specific_and_idempotent(tmp_path: Path) -> None:
    store = CampaignStore(tmp_path / "peer.sqlite", clock=Clock())
    try:
        for session in ("old-session", "new-session"):
            store.check_in(
                "workspace-A",
                "GOAL-TEST-001",
                "same-agent",
                session_id=session,
            )

        assert store.check_out(
            "workspace-A", "GOAL-TEST-001", "same-agent", session_id="old-session"
        )
        assert [agent.session_id for agent in store.live_agents("workspace-A", "GOAL-TEST-001")] == [
            "new-session"
        ]
        assert not store.check_out(
            "workspace-A", "GOAL-TEST-001", "same-agent", session_id="old-session"
        )
    finally:
        store.close()


def test_controller_lease_fences_a_stale_owner_after_expiry(tmp_path: Path) -> None:
    clock = Clock()
    store = CampaignStore(tmp_path / "peer.sqlite", clock=clock)
    try:
        first = store.leases.acquire(
            "workspace-A",
            "GOAL-TEST-001",
            "controller-one",
            owner_session_id="controller-one-session",
            ttl_seconds=30,
            source_commit="a" * 40,
        )
        assert first.epoch == 1
        assert store.leases.acquire(
            "workspace-A",
            "GOAL-TEST-001",
            "controller-one",
            owner_session_id="controller-one-session",
            ttl_seconds=30,
        ) == first
        with pytest.raises(LeaseConflictError):
            store.leases.acquire(
                "workspace-A",
                "GOAL-TEST-001",
                "controller-one",
                owner_session_id="different-controller-process",
                ttl_seconds=30,
            )
        with pytest.raises(LeaseConflictError):
            store.leases.acquire(
                "workspace-A",
                "GOAL-TEST-001",
                "controller-two",
                owner_session_id="controller-two-session",
                ttl_seconds=30,
            )

        clock.advance(31)
        with pytest.raises(LeaseNotOwnedError):
            store.leases.release(
                "workspace-A",
                "GOAL-TEST-001",
                "controller-one",
                first.epoch,
                owner_session_id="controller-one-session",
            )
        second = store.leases.acquire(
            "workspace-A",
            "GOAL-TEST-001",
            "controller-two",
            owner_session_id="controller-two-session",
            ttl_seconds=30,
            source_commit="b" * 40,
        )
        assert second.epoch == 2
        with pytest.raises(LeaseNotOwnedError):
            store.leases.renew(
                "workspace-A",
                "GOAL-TEST-001",
                "controller-one",
                first.epoch,
                owner_session_id="controller-one-session",
            )
        with pytest.raises(LeaseNotOwnedError):
            store.leases.assert_owner(
                "workspace-A",
                "GOAL-TEST-001",
                "controller-one",
                first.epoch,
                owner_session_id="controller-one-session",
            )

        renewed = store.leases.renew(
            "workspace-A",
            "GOAL-TEST-001",
            "controller-two",
            second.epoch,
            owner_session_id="controller-two-session",
            ttl_seconds=60,
        )
        assert renewed.epoch == second.epoch
        released = store.leases.release(
            "workspace-A",
            "GOAL-TEST-001",
            "controller-two",
            second.epoch,
            owner_session_id="controller-two-session",
        )
        assert not released.is_live(clock())
        assert store.leases.get("workspace-A", "GOAL-TEST-001") is None
        assert store.leases.get(
            "workspace-A", "GOAL-TEST-001", include_expired=True
        ) == released
    finally:
        store.close()


def test_concurrent_store_processes_can_only_acquire_one_live_lease(tmp_path: Path) -> None:
    database = tmp_path / "shared.sqlite"
    clock = Clock()
    first = CampaignStore(database, clock=clock)
    second = CampaignStore(database, clock=clock)
    barrier = Barrier(2)

    def acquire(store: CampaignStore, owner: str):
        barrier.wait()
        try:
            return store.leases.acquire(
                "workspace-A",
                "GOAL-TEST-001",
                owner,
                owner_session_id=f"{owner}-session",
            )
        except LeaseConflictError as exc:
            return exc

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(
                executor.map(
                    lambda args: acquire(*args),
                    ((first, "controller-one"), (second, "controller-two")),
                )
            )
        winners = [result for result in results if not isinstance(result, LeaseConflictError)]
        conflicts = [result for result in results if isinstance(result, LeaseConflictError)]
        assert len(winners) == 1
        assert winners[0].epoch == 1
        assert len(conflicts) == 1
    finally:
        first.close()
        second.close()


def test_sqlite_state_is_recoverable_across_a_clean_store_restart(tmp_path: Path) -> None:
    database = tmp_path / "shared" / "peer.sqlite"
    clock = Clock()
    with CampaignStore(database, clock=clock) as first:
        first.check_in(
            "workspace-A",
            "GOAL-TEST-001",
            "claude-agent",
            session_id="session-1",
            metadata={"runtime": "claude-code"},
        )
        lease = first.leases.acquire(
            "workspace-A",
            "GOAL-TEST-001",
            "controller",
            owner_session_id="controller-session",
            source_commit="f" * 40,
        )

    with CampaignStore(database, clock=clock) as restored:
        assert restored.live_agents("workspace-A", "GOAL-TEST-001")[0].agent_id == "claude-agent"
        assert restored.leases.get("workspace-A", "GOAL-TEST-001") == lease


def test_coordination_input_is_bounded_and_json_safe(tmp_path: Path) -> None:
    store = CampaignStore(tmp_path / "peer.sqlite", clock=Clock())
    try:
        with pytest.raises(CampaignStoreError, match="ttl_seconds"):
            store.check_in(
                "workspace-A", "GOAL-TEST-001", "agent", session_id="session", ttl_seconds=1
            )
        with pytest.raises(CampaignStoreError, match="metadata"):
            store.check_in(
                "workspace-A",
                "GOAL-TEST-001",
                "agent",
                session_id="session",
                metadata={"not_json": {1, 2, 3}},
            )
        with pytest.raises(CampaignStoreError, match="control"):
            store.check_in(
                "workspace\nA", "GOAL-TEST-001", "agent", session_id="session"
            )
    finally:
        store.close()


def test_next_checkin_prunes_expired_presences_before_persisting_new_session(tmp_path: Path) -> None:
    clock = Clock()
    store = CampaignStore(tmp_path / "peer.sqlite", clock=clock)
    try:
        for session in ("crashed-one", "crashed-two", "crashed-three"):
            store.check_in(
                "workspace-A", "GOAL-TEST-001", "agent", session_id=session, ttl_seconds=15
            )
        clock.advance(16)
        store.check_in(
            "workspace-A", "GOAL-TEST-001", "replacement", session_id="live", ttl_seconds=15
        )
        rows = store.list_agents("workspace-A", "GOAL-TEST-001", include_stale=True)
        assert [row.session_id for row in rows] == ["live"]
    finally:
        store.close()


def test_live_presence_total_is_bounded_across_arbitrary_goal_scopes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A local sender cannot retain an unbounded set of valid-looking GOAL IDs."""

    monkeypatch.setattr(CampaignStore, "MAX_ACTIVE_PRESENCES_TOTAL", 2)
    clock = Clock()
    store = CampaignStore(tmp_path / "peer.sqlite", clock=clock)
    try:
        for index in range(2):
            store.check_in(
                "workspace-A",
                f"GOAL-TEST-{index:03d}",
                f"agent-{index}",
                session_id=f"session-{index}",
                ttl_seconds=15,
            )
        with pytest.raises(CampaignStoreError, match="across this local daemon"):
            store.check_in(
                "workspace-A",
                "GOAL-TEST-999",
                "overflow-agent",
                session_id="overflow-session",
                ttl_seconds=15,
            )
        clock.advance(16)
        store.check_in(
            "workspace-A",
            "GOAL-TEST-999",
            "replacement-agent",
            session_id="replacement-session",
            ttl_seconds=15,
        )
        assert [row.campaign_id for row in store.live_agents("workspace-A", "GOAL-TEST-999")] == [
            "GOAL-TEST-999"
        ]
    finally:
        store.close()


@pytest.mark.skipif(os.name == "nt", reason="POSIX mode assertions")
def test_disk_state_leaf_and_database_are_user_private_and_reject_symlink_paths(tmp_path: Path) -> None:
    database = tmp_path / "private-state" / "peer.sqlite"
    store = CampaignStore(database, clock=Clock())
    try:
        store.check_in("workspace-A", "GOAL-TEST-001", "agent", session_id="session")
        assert stat.S_IMODE(database.parent.stat().st_mode) == 0o700
        assert stat.S_IMODE(database.stat().st_mode) == 0o600
    finally:
        store.close()

    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "state-link"
    link.symlink_to(target, target_is_directory=True)
    with pytest.raises(CampaignStoreError, match="symlink"):
        CampaignStore(link / "peer.sqlite", clock=Clock())
