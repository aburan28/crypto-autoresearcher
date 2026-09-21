"""Bounded advisory session snapshots and update feed shared through SQLite.

Incarnations and revisions prevent accidental stale writes. They are not
authentication: all reporters on this same-user local service remain untrusted.
"""
from __future__ import annotations

import json
import uuid
from typing import Any, Mapping

from .models import utc_timestamp
from .store import CampaignStore, CampaignStoreError


class SessionBoard:
    MAX_SESSIONS = 256
    MAX_EVENTS = 4096
    EVENT_RETENTION_SECONDS = 86400
    MAX_PAGE = 100

    def __init__(self, store: CampaignStore, repository_id: str):
        self.store = store
        self.scope = store._identifier(repository_id, 'repository_id')
        with store._transaction(write=True) as db:
            db.execute('''CREATE TABLE IF NOT EXISTS peer_sessions (
                repository_id TEXT NOT NULL, session_id TEXT NOT NULL,
                incarnation TEXT NOT NULL, revision INTEGER NOT NULL,
                updated_at REAL NOT NULL, expires_at REAL NOT NULL,
                metadata_json TEXT NOT NULL, PRIMARY KEY(repository_id, session_id))''')
            db.execute('''CREATE TABLE IF NOT EXISTS peer_updates (
                seq INTEGER PRIMARY KEY AUTOINCREMENT, repository_id TEXT NOT NULL,
                session_id TEXT NOT NULL, event_key TEXT NOT NULL,
                created_at REAL NOT NULL, expires_at REAL NOT NULL, payload_json TEXT NOT NULL,
                UNIQUE(repository_id, session_id, event_key))''')
            db.execute('''CREATE INDEX IF NOT EXISTS peer_updates_scope_seq
                ON peer_updates(repository_id, seq)''')
            db.execute('''CREATE TABLE IF NOT EXISTS peer_feed_state (
                repository_id TEXT PRIMARY KEY, stream_id TEXT NOT NULL,
                floor_seq INTEGER NOT NULL DEFAULT 0, last_seq INTEGER NOT NULL DEFAULT 0)''')
            db.execute('INSERT OR IGNORE INTO peer_feed_state(repository_id, stream_id) VALUES (?,?)',
                       (self.scope, uuid.uuid4().hex))

    def _prune(self, db, now):
        db.execute('DELETE FROM peer_sessions WHERE expires_at <= ?', (now,))
        cutoff = db.execute('SELECT seq FROM peer_updates ORDER BY seq DESC LIMIT 1 OFFSET ?',
                            (self.MAX_EVENTS - 1,)).fetchone()
        limit = int(cutoff['seq']) if cutoff else 0
        rows = db.execute('''SELECT repository_id, MAX(seq) AS watermark FROM peer_updates
            WHERE expires_at <= ? OR seq < ? GROUP BY repository_id''', (now, limit)).fetchall()
        for row in rows:
            db.execute('UPDATE peer_feed_state SET floor_seq=MAX(floor_seq,?) WHERE repository_id=?',
                       (row['watermark'], row['repository_id']))
        db.execute('DELETE FROM peer_updates WHERE expires_at <= ? OR seq < ?', (now, limit))

    def _session(self, row, now):
        return dict(json.loads(row['metadata_json']), session_id=row['session_id'],
                    incarnation=row['incarnation'], revision=row['revision'],
                    updated_at=utc_timestamp(row['updated_at']), expires_at=utc_timestamp(row['expires_at']),
                    live=row['expires_at'] > now, advisory_only=True, authority='none')

    def _event(self, db, session, kind, key, content, now):
        payload = {'kind': kind, 'author': session, 'content': content,
                   'advisory_only': True, 'authority': 'none'}
        encoded = self.store._metadata_json(payload)
        db.execute('''INSERT INTO peer_updates(repository_id,session_id,event_key,created_at,expires_at,payload_json)
            VALUES (?,?,?,?,?,?)''', (self.scope, session['session_id'], key, now,
                                     now + self.EVENT_RETENTION_SECONDS, encoded))
        seq = int(db.execute('SELECT last_insert_rowid()').fetchone()[0])
        db.execute('UPDATE peer_feed_state SET last_seq=? WHERE repository_id=?', (seq, self.scope))
        return dict(payload, cursor=seq, created_at=utc_timestamp(now))

    def register(self, session_id: str, metadata: Mapping[str, Any], ttl_seconds: int = 300):
        session_id = self.store._identifier(session_id, 'session_id')
        ttl = self.store._ttl(ttl_seconds)
        encoded = self.store._metadata_json(metadata)
        now = self.store._now()
        with self.store._transaction(write=True) as db:
            self._prune(db, now)
            existing = db.execute('SELECT * FROM peer_sessions WHERE repository_id=? AND session_id=?',
                                  (self.scope, session_id)).fetchone()
            if existing:
                if existing['metadata_json'] != encoded:
                    raise CampaignStoreError('session already exists; use its incarnation and revision to update it')
                return self._session(existing, now)
            total = db.execute('SELECT COUNT(*) FROM peer_sessions').fetchone()[0]
            if total >= self.MAX_SESSIONS:
                raise CampaignStoreError('local session board is full')
            db.execute('INSERT INTO peer_sessions VALUES (?,?,?,?,?,?,?)',
                       (self.scope, session_id, uuid.uuid4().hex, 1, now, now + ttl, encoded))
            row = db.execute('SELECT * FROM peer_sessions WHERE repository_id=? AND session_id=?',
                             (self.scope, session_id)).fetchone()
            session = self._session(row, now)
            self._event(db, session, 'joined', 'presence:' + session['incarnation'] + ':1', {}, now)
            self._prune(db, now)
            return session

    def _owned(self, db, session_id, incarnation, revision, now):
        self.store._identifier(session_id, 'session_id')
        self.store._identifier(incarnation, 'incarnation')
        row = db.execute('SELECT * FROM peer_sessions WHERE repository_id=? AND session_id=?',
                         (self.scope, session_id)).fetchone()
        if not row or row['expires_at'] <= now:
            raise CampaignStoreError('session absent or expired; register a new incarnation')
        if row['incarnation'] != incarnation:
            raise CampaignStoreError('stale session incarnation')
        if revision is not None:
            if type(revision) is not int or revision < 1 or row['revision'] != revision:
                raise CampaignStoreError('stale session revision; read the latest session before updating')
        return row

    def update(self, session_id, incarnation, revision, changes, ttl_seconds=300):
        ttl = self.store._ttl(ttl_seconds)
        now = self.store._now()
        with self.store._transaction(write=True) as db:
            row = self._owned(db, session_id, incarnation, revision, now)
            metadata = dict(json.loads(row['metadata_json']), **changes)
            encoded = self.store._metadata_json(metadata)
            db.execute('''UPDATE peer_sessions SET metadata_json=?,revision=revision+1,updated_at=?,expires_at=?
                WHERE repository_id=? AND session_id=?''', (encoded, now, now + ttl, self.scope, session_id))
            row = db.execute('SELECT * FROM peer_sessions WHERE repository_id=? AND session_id=?',
                             (self.scope, session_id)).fetchone()
            session = self._session(row, now)
            self._event(db, session, 'status', f'presence:{incarnation}:{session["revision"]}', {}, now)
            self._prune(db, now)
            return session

    def sessions(self, include_stale=False):
        now = self.store._now()
        with self.store._transaction() as db:
            rows = db.execute('''SELECT * FROM peer_sessions WHERE repository_id=?
                ORDER BY updated_at DESC, session_id LIMIT ?''', (self.scope, self.MAX_SESSIONS)).fetchall()
        return [self._session(row, now) for row in rows if include_stale or row['expires_at'] > now]

    def publish(self, session_id, incarnation, event_id, kind, content):
        event_id = self.store._identifier(event_id, 'event_id')
        encoded_content = self.store._metadata_json(content)
        now = self.store._now()
        key = f'user:{incarnation}:{event_id}'
        with self.store._transaction(write=True) as db:
            row = self._owned(db, session_id, incarnation, None, now)
            self._prune(db, now)
            previous = db.execute('''SELECT * FROM peer_updates WHERE repository_id=?
                AND session_id=? AND event_key=?''', (self.scope, session_id, key)).fetchone()
            if previous:
                payload = json.loads(previous['payload_json'])
                if payload['kind'] != kind or self.store._metadata_json(payload['content']) != encoded_content:
                    raise CampaignStoreError('event_id was already used with different content')
                return dict(payload, cursor=previous['seq'], created_at=utc_timestamp(previous['created_at']),
                            duplicate=True)
            event = self._event(db, self._session(row, now), kind, key, json.loads(encoded_content), now)
            self._prune(db, now)
            return dict(event, duplicate=False)

    def close(self, session_id, incarnation, revision):
        now = self.store._now()
        with self.store._transaction(write=True) as db:
            row = db.execute('SELECT * FROM peer_sessions WHERE repository_id=? AND session_id=?',
                             (self.scope, session_id)).fetchone()
            if not row:
                return False
            row = self._owned(db, session_id, incarnation, revision, now)
            session = self._session(row, now)
            self._event(db, session, 'left', f'close:{incarnation}', {}, now)
            db.execute('DELETE FROM peer_sessions WHERE repository_id=? AND session_id=?', (self.scope, session_id))
            self._prune(db, now)
            return True

    def read(self, after_cursor=0, limit=50, stream_id=None, recipient=None):
        if type(after_cursor) is not int or after_cursor < 0:
            raise CampaignStoreError('after_cursor must be a nonnegative integer')
        if type(limit) is not int or not 1 <= limit <= self.MAX_PAGE:
            raise CampaignStoreError(f'limit must be between 1 and {self.MAX_PAGE}')
        now = self.store._now()
        with self.store._transaction() as db:
            state = db.execute('SELECT * FROM peer_feed_state WHERE repository_id=?', (self.scope,)).fetchone()
            if (stream_id is not None and stream_id != state['stream_id']) or after_cursor > state['last_seq']:
                return {'stream_id': state['stream_id'], 'reset_required': True, 'events': [], 'next_cursor': 0}
            expired = db.execute('SELECT MAX(seq) FROM peer_updates WHERE repository_id=? AND expires_at<=?',
                                 (self.scope, now)).fetchone()[0] or 0
            floor = max(state['floor_seq'], expired)
            # Page the common stream first, then filter. The cursor advances even
            # past messages for other recipients, avoiding skipped/duplicate pages.
            rows = db.execute('''SELECT * FROM peer_updates WHERE repository_id=? AND seq>?
                AND expires_at>? ORDER BY seq LIMIT ?''',
                              (self.scope, after_cursor, now, limit + 1)).fetchall()
            page = rows[:limit]
            events = []
            for row in page:
                payload = json.loads(row['payload_json'])
                target = payload['content'].get('recipient_session_id')
                if recipient is None or target in (None, recipient):
                    events.append(dict(payload, cursor=row['seq'], created_at=utc_timestamp(row['created_at'])))
            return {'stream_id': state['stream_id'], 'reset_required': False,
                    'history_gap': after_cursor < floor, 'retained_after_cursor': floor,
                    'events': events, 'has_more': len(rows) > limit,
                    'next_cursor': page[-1]['seq'] if page else max(after_cursor, floor),
                    'latest_cursor': state['last_seq']}
