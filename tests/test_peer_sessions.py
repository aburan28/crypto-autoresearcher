"""Concurrency and MCP integration checks for advisory session coordination."""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import threading

import pytest

from orchestration.campaign.peer_sessions import SessionBoard
from orchestration.campaign.store import CampaignStore, CampaignStoreError
from orchestration.campaign.session_tools import repository_fingerprint


class Clock:
    def __init__(self):
        self.value = 1_700_000_000.0

    def __call__(self):
        return self.value


@pytest.fixture
def board(tmp_path):
    clock = Clock()
    store = CampaignStore(tmp_path / 'state' / 'peer.sqlite', clock=clock)
    try:
        yield SessionBoard(store, 'repository-test'), clock
    finally:
        store.close()


def test_registration_retry_revisions_and_close(board):
    b, _ = board
    first = b.register('a', {'summary': 'hello'})
    assert b.register('a', {'summary': 'hello'}) == first
    with pytest.raises(CampaignStoreError, match='already exists'):
        b.register('a', {'summary': 'different'})
    updated = b.update('a', first['incarnation'], 1, {'summary': 'updated'})
    assert updated['revision'] == 2
    with pytest.raises(CampaignStoreError, match='stale session revision'):
        b.update('a', first['incarnation'], 1, {'summary': 'late'})
    assert b.close('a', first['incarnation'], 2)
    assert not b.close('a', first['incarnation'], 2)
    assert b.sessions() == []


def test_expiry_and_stale_incarnation(board):
    b, clock = board
    first = b.register('same-id', {})
    clock.value += 301
    assert b.sessions() == []
    second = b.register('same-id', {})
    assert first['incarnation'] != second['incarnation']
    for action in (
        lambda: b.update('same-id', first['incarnation'], 1, {}),
        lambda: b.publish('same-id', first['incarnation'], 'late', 'note', {}),
        lambda: b.close('same-id', first['incarnation'], 1),
    ):
        with pytest.raises(CampaignStoreError, match='stale session incarnation'):
            action()
    assert b.sessions()[0]['incarnation'] == second['incarnation']


def test_update_retry_deduplication_and_conflicting_event_id(board):
    b, _ = board
    session = b.register('a', {})
    args = ('a', session['incarnation'], 'message-1', 'note', {'message': 'hello'})
    first = b.publish(*args)
    again = b.publish(*args)
    assert first['cursor'] == again['cursor']
    assert not first['duplicate'] and again['duplicate']
    with pytest.raises(CampaignStoreError, match='different content'):
        b.publish('a', session['incarnation'], 'message-1', 'note', {'message': 'changed'})
    assert len(b.read()['events']) == 2  # joined + one note


def test_bounded_feed_pagination_recipient_filter_and_history_gap(board):
    b, _ = board
    b.MAX_EVENTS = 4
    session = b.register('a', {})
    for i in range(6):
        b.publish('a', session['incarnation'], str(i), 'note',
                  {'message': str(i), 'recipient_session_id': 'other'})
    page = b.read(limit=2, recipient='reader')
    assert page['history_gap'] and page['has_more']
    assert page['events'] == [] and page['next_cursor'] > 0
    last = b.read(page['next_cursor'], 2, page['stream_id'], 'reader')
    assert not last['has_more'] and last['next_cursor'] > page['next_cursor']
    assert len(b.read(limit=100)['events']) == 4


def test_expired_feed_reports_gap_and_stream_resets(board):
    b, clock = board
    b.register('a', {})
    original = b.read()
    clock.value += b.EVENT_RETENTION_SECONDS + 1
    page = b.read()
    assert page['events'] == [] and page['history_gap']
    assert b.read(stream_id='unrelated-stream')['reset_required']
    assert b.read(after_cursor=original['latest_cursor'] + 1)['reset_required']


def test_restart_keeps_stream_cursor_and_events(tmp_path):
    db = tmp_path / 'state' / 'peer.sqlite'
    with CampaignStore(db) as store:
        b = SessionBoard(store, 'repo')
        b.register('a', {})
        first = b.read()
    with CampaignStore(db) as store:
        b = SessionBoard(store, 'repo')
        assert b.read()['stream_id'] == first['stream_id']
        assert b.read()['events'] == first['events']


def test_multiple_connections_serialize_simultaneous_revisions(tmp_path):
    path = tmp_path / 'state' / 'peer.sqlite'
    with CampaignStore(path) as one, CampaignStore(path) as two:
        a, b = SessionBoard(one, 'repo'), SessionBoard(two, 'repo')
        registered = a.register('shared', {})
        barrier = threading.Barrier(2)
        def write(board):
            barrier.wait()
            try:
                return board.update('shared', registered['incarnation'], 1, {'summary': 'new'})['revision']
            except CampaignStoreError:
                return 'conflict'
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(write, (a, b)))
        assert sorted(map(str, results)) == ['2', 'conflict']
        assert len(a.read()['events']) == 2


def test_simultaneous_publish_retry_has_one_event(tmp_path):
    path = tmp_path / 'state' / 'peer.sqlite'
    with CampaignStore(path) as one, CampaignStore(path) as two:
        a, b = SessionBoard(one, 'repo'), SessionBoard(two, 'repo')
        session = a.register('shared', {})
        def publish(board):
            return board.publish('shared', session['incarnation'], 'retry-id', 'note', {'message': 'same'})
        with ThreadPoolExecutor(max_workers=2) as pool:
            events = list(pool.map(publish, (a, b)))
        assert events[0]['cursor'] == events[1]['cursor']
        assert sum(e['duplicate'] for e in events) == 1


def test_session_capacity_and_invalid_limits(board):
    b, _ = board
    b.MAX_SESSIONS = 1
    b.register('one', {})
    with pytest.raises(CampaignStoreError, match='full'):
        b.register('two', {})
    for args in ({'after_cursor': -1}, {'after_cursor': True}, {'limit': 0}, {'limit': 101}):
        with pytest.raises(CampaignStoreError):
            b.read(**args)


@pytest.fixture
def anyio_backend():
    return 'asyncio'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


@pytest.mark.anyio
async def test_worktrees_share_mcp_status_and_updates(tmp_path):
    fastmcp = pytest.importorskip('fastmcp')
    from orchestration.campaign.mcp_server import build_server, workspace_fingerprint
    repo = tmp_path / 'repo'
    repo.mkdir()
    git(repo, 'init', '-q')
    git(repo, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
        'commit', '--allow-empty', '-qm', 'fixture')
    linked = tmp_path / 'linked'
    git(repo, 'worktree', 'add', '--detach', str(linked), 'HEAD')
    assert workspace_fingerprint(repo) != workspace_fingerprint(linked)
    repository_id = repository_fingerprint(repo)
    assert repository_id == repository_fingerprint(linked)
    with CampaignStore(tmp_path / 'state' / 'peer.sqlite') as store:
        app = build_server(repo_root=repo, store=store)
        async with fastmcp.Client(app) as first, fastmcp.Client(app) as second:
            async def call(client, name, **kwargs):
                result = await client.call_tool(name, {'expected_repository_id': repository_id, **kwargs})
                return result.data
            a = await call(first, 'register_session', session_id='codex-a', runtime='codex',
                           checkout_root=str(repo), summary='Editing a module', write_scope=['orchestration'])
            b = await call(second, 'register_session', session_id='claude-b', runtime='claude-code',
                           checkout_root=str(linked), summary='Reviewing the module',
                           write_scope=['orchestration/campaign/store.py'])
            assert len(b['sessions']) == 2
            assert b['overlaps'][0]['kind'] == 'potential_merge_overlap'
            initial = await call(second, 'read_updates')
            waiting = asyncio.create_task(call(second, 'read_updates',
                after_cursor=initial['next_cursor'], stream_id=initial['stream_id'], wait_seconds=2))
            await asyncio.sleep(0.1)
            note = await call(first, 'publish_update', session_id='codex-a',
                              incarnation=a['session']['incarnation'], event_id='progress-1',
                              message='Module review is ready', recipient_session_id='claude-b')
            received = await waiting
            assert received['events'][0]['content']['message'] == 'Module review is ready'
            assert note['authority'] == 'none'
            changed = await call(first, 'update_session', session_id='codex-a',
                                 incarnation=a['session']['incarnation'], expected_revision=1, state='waiting')
            assert changed['session']['revision'] == 2
            with pytest.raises(Exception, match='stale session revision'):
                await call(first, 'update_session', session_id='codex-a',
                           incarnation=a['session']['incarnation'], expected_revision=1, state='completed')
            with pytest.raises(Exception, match='expected_repository_id'):
                await first.call_tool('list_sessions', {'expected_repository_id': 'repository-wrong'})
            with pytest.raises(Exception, match='not a worktree'):
                await call(second, 'register_session', session_id='wrong', runtime='other', checkout_root=str(tmp_path))
            await call(first, 'close_session', session_id='codex-a', incarnation=a['session']['incarnation'],
                       expected_revision=2)
            assert (await call(second, 'list_sessions'))['session_count'] == 1
