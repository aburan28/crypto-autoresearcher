"""Queue-driven coordinator for agents working in isolated Git worktrees.

The queue is a delivery mechanism, never the source of truth. Durable task,
lease, reservation, inbox-deduplication, candidate, and outbox state lives in a
transactional SQLite database. Queue delivery is at-least-once; coordinator
state effects are idempotent by message_id and fenced by task generation and
lease token.

The module intentionally uses only the Python standard library so it can sit
below the model/runtime adapters. ``SQLiteQueue`` is a local/dev transport;
production transports (SQS, NATS JetStream, Redis Streams, Postgres, etc.) can
implement the small ``QueueTransport`` protocol without changing coordinator
semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import secrets
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping, Protocol, Sequence


MESSAGE_SCHEMA = "crypto.autoresearch.coordinator.message.v1"
EVENT_SCHEMA = "crypto.autoresearch.coordinator.event.v1"
TASK_STATES = frozenset(
    {"pending", "running", "ready", "integrating", "merged", "failed", "blocked", "cancelled"}
)
TERMINAL_TASK_STATES = frozenset({"merged", "failed", "cancelled"})
DEFAULT_VISIBILITY_TIMEOUT_SECONDS = 60
DEFAULT_LEASE_SECONDS = 120
MAX_DELIVERY_ATTEMPTS = 8


class CoordinatorError(ValueError):
    """Raised when a message violates coordinator invariants."""


@dataclass(frozen=True)
class QueueDelivery:
    receipt: str
    message: dict[str, Any]
    attempt: int


class QueueTransport(Protocol):
    """Minimal at-least-once queue contract used by ``QueueCoordinator``."""

    def send(self, message: Mapping[str, Any]) -> None: ...

    def receive(self, *, visibility_timeout_seconds: int) -> QueueDelivery | None: ...

    def ack(self, receipt: str) -> None: ...

    def retry(self, receipt: str, *, delay_seconds: int = 0) -> None: ...

    def dead_letter(self, receipt: str, *, reason: str) -> None: ...


class SQLiteQueue:
    """Durable local queue implementing visibility timeout and redelivery.

    This adapter is deliberately simple: it is useful for one host and for
    deterministic tests. The coordinator itself does not depend on SQLite
    queue semantics; a remote queue only needs to implement ``QueueTransport``.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        name: str = "tasks",
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.path = str(path)
        self.name = _identifier(name, "queue name")
        self._clock = clock
        self._lock = threading.RLock()
        self._db = sqlite3.connect(self.path, isolation_level=None, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA busy_timeout = 5000")
        if self.path != ":memory:":
            self._db.execute("PRAGMA journal_mode = WAL")
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS queue_messages (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                queue_name TEXT NOT NULL,
                message_id TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                visible_at REAL NOT NULL,
                receipt TEXT,
                attempts INTEGER NOT NULL DEFAULT 0,
                dead_letter_reason TEXT,
                UNIQUE(queue_name, message_id)
            );
            CREATE INDEX IF NOT EXISTS queue_visible_idx
              ON queue_messages(queue_name, dead_letter_reason, visible_at, sequence);
            """
        )

    def _now(self) -> float:
        value = float(self._clock())
        if not math.isfinite(value):
            raise CoordinatorError("queue clock must be finite")
        return value

    def send(self, message: Mapping[str, Any]) -> None:
        if not isinstance(message, Mapping):
            raise CoordinatorError("queue message must be an object")
        body = dict(message)
        body["message_id"] = _identifier(body.get("message_id"), "message_id")
        _identifier(body.get("schema"), "schema")
        encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False)
        with self._lock:
            self._db.execute(
                "INSERT OR IGNORE INTO queue_messages(queue_name, message_id, payload_json, visible_at) VALUES (?, ?, ?, ?)",
                (self.name, body["message_id"], encoded, self._now()),
            )

    def receive(self, *, visibility_timeout_seconds: int) -> QueueDelivery | None:
        if visibility_timeout_seconds <= 0:
            raise CoordinatorError("visibility_timeout_seconds must be positive")
        now = self._now()
        receipt = uuid.uuid4().hex
        with self._lock:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                row = self._db.execute(
                    """
                    SELECT sequence, payload_json, attempts
                      FROM queue_messages
                     WHERE queue_name = ? AND dead_letter_reason IS NULL AND visible_at <= ?
                     ORDER BY sequence LIMIT 1
                    """,
                    (self.name, now),
                ).fetchone()
                if row is None:
                    self._db.execute("COMMIT")
                    return None
                attempt = int(row["attempts"]) + 1
                self._db.execute(
                    """UPDATE queue_messages
                          SET receipt = ?, attempts = ?, visible_at = ?
                        WHERE sequence = ? AND queue_name = ?""",
                    (
                        receipt,
                        attempt,
                        now + visibility_timeout_seconds,
                        int(row["sequence"]),
                        self.name,
                    ),
                )
                self._db.execute("COMMIT")
            except BaseException:
                self._db.execute("ROLLBACK")
                raise
        return QueueDelivery(
            receipt=receipt,
            message=json.loads(row["payload_json"]),
            attempt=attempt,
        )

    def ack(self, receipt: str) -> None:
        with self._lock:
            self._db.execute(
                "DELETE FROM queue_messages WHERE queue_name = ? AND receipt = ?",
                (self.name, receipt),
            )

    def retry(self, receipt: str, *, delay_seconds: int = 0) -> None:
        if delay_seconds < 0:
            raise CoordinatorError("delay_seconds cannot be negative")
        with self._lock:
            self._db.execute(
                "UPDATE queue_messages SET visible_at = ?, receipt = NULL WHERE queue_name = ? AND receipt = ?",
                (self._now() + delay_seconds, self.name, receipt),
            )

    def dead_letter(self, receipt: str, *, reason: str) -> None:
        normalized = reason.strip()
        if not normalized:
            raise CoordinatorError("dead-letter reason cannot be empty")
        with self._lock:
            self._db.execute(
                "UPDATE queue_messages SET dead_letter_reason = ?, receipt = NULL WHERE queue_name = ? AND receipt = ?",
                (normalized[:2000], self.name, receipt),
            )

    def close(self) -> None:
        self._db.close()


def _identifier(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise CoordinatorError(f"{name} must be 1..256 nonblank characters")
    value = value.strip()
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise CoordinatorError(f"{name} may not contain control characters")
    return value


def _string_list(value: Any, name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise CoordinatorError(f"{name} must be a list")
    result = [_identifier(item, f"{name}[]") for item in value]
    if len(result) != len(set(result)):
        raise CoordinatorError(f"{name} must not contain duplicates")
    return result


def validate_message(message: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(message, Mapping):
        raise CoordinatorError("queue message must be an object")
    body = dict(message)
    if body.get("schema") != MESSAGE_SCHEMA:
        raise CoordinatorError(f"schema must be {MESSAGE_SCHEMA}")
    for field in ("message_id", "kind", "run_id", "task_id"):
        body[field] = _identifier(body.get(field), field)
    generation = body.get("generation", 1)
    if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
        raise CoordinatorError("generation must be a positive integer")
    body["generation"] = generation
    payload = body.get("payload", {})
    if not isinstance(payload, Mapping):
        raise CoordinatorError("payload must be an object")
    body["payload"] = dict(payload)
    return body


def new_message(
    *,
    kind: str,
    run_id: str,
    task_id: str,
    payload: Mapping[str, Any],
    generation: int = 1,
) -> dict[str, Any]:
    return {
        "schema": MESSAGE_SCHEMA,
        "message_id": str(uuid.uuid4()),
        "kind": kind,
        "run_id": run_id,
        "task_id": task_id,
        "generation": generation,
        "payload": dict(payload),
    }


class CoordinatorState:
    """Authoritative transactional state for queue-driven coordination."""

    def __init__(
        self,
        path: str | Path,
        *,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.path = str(path)
        self._clock = clock
        self._lock = threading.RLock()
        self._db = sqlite3.connect(self.path, isolation_level=None, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA foreign_keys = ON")
        self._db.execute("PRAGMA busy_timeout = 5000")
        if self.path != ":memory:":
            self._db.execute("PRAGMA journal_mode = WAL")
            self._db.execute("PRAGMA synchronous = NORMAL")
        self._initialize()

    def _initialize(self) -> None:
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                run_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                generation INTEGER NOT NULL,
                state TEXT NOT NULL,
                base_sha TEXT NOT NULL,
                branch TEXT NOT NULL,
                worktree TEXT NOT NULL,
                agent_id TEXT,
                lease_token_hash TEXT,
                lease_expires_at REAL,
                head_sha TEXT,
                updated_at REAL NOT NULL,
                PRIMARY KEY(run_id, task_id)
            );
            CREATE TABLE IF NOT EXISTS task_dependencies (
                run_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                dependency_task_id TEXT NOT NULL,
                PRIMARY KEY(run_id, task_id, dependency_task_id)
            );
            CREATE TABLE IF NOT EXISTS resource_claims (
                run_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                generation INTEGER NOT NULL,
                resource TEXT NOT NULL,
                exclusive INTEGER NOT NULL,
                released_at REAL,
                PRIMARY KEY(run_id, task_id, generation, resource)
            );
            CREATE INDEX IF NOT EXISTS live_resource_claim_idx
              ON resource_claims(resource, released_at, exclusive);
            CREATE TABLE IF NOT EXISTS inbox_messages (
                message_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                processed_at REAL NOT NULL,
                result_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS outbox_messages (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL UNIQUE,
                payload_json TEXT NOT NULL,
                created_at REAL NOT NULL,
                published_at REAL
            );
            CREATE INDEX IF NOT EXISTS unpublished_outbox_idx
              ON outbox_messages(published_at, sequence);
            CREATE TABLE IF NOT EXISTS candidates (
                run_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                generation INTEGER NOT NULL,
                head_sha TEXT NOT NULL,
                submitted_at REAL NOT NULL,
                PRIMARY KEY(run_id, task_id, generation, head_sha)
            );
            """
        )

    def _now(self) -> float:
        value = float(self._clock())
        if not math.isfinite(value):
            raise CoordinatorError("coordinator clock must be finite")
        return value

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                yield self._db
                self._db.execute("COMMIT")
            except BaseException:
                self._db.execute("ROLLBACK")
                raise

    @staticmethod
    def _lease_hash(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _outbox(
        self,
        db: sqlite3.Connection,
        *,
        kind: str,
        body: Mapping[str, Any],
        now: float,
    ) -> None:
        payload = dict(body)
        payload.setdefault("schema", EVENT_SCHEMA)
        payload.setdefault("message_id", str(uuid.uuid4()))
        payload.setdefault("kind", kind)
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        db.execute(
            "INSERT INTO outbox_messages(message_id, payload_json, created_at) VALUES (?, ?, ?)",
            (payload["message_id"], encoded, now),
        )

    def process(
        self,
        message: Mapping[str, Any],
        *,
        lease_seconds: int = DEFAULT_LEASE_SECONDS,
    ) -> dict[str, Any]:
        body = validate_message(message)
        if lease_seconds <= 0:
            raise CoordinatorError("lease_seconds must be positive")
        now = self._now()
        with self.transaction() as db:
            duplicate = db.execute(
                "SELECT result_json FROM inbox_messages WHERE message_id = ?",
                (body["message_id"],),
            ).fetchone()
            if duplicate is not None:
                return json.loads(duplicate["result_json"])

            kind = body["kind"]
            if kind == "task.dispatch":
                result = self._dispatch(
                    db,
                    body,
                    now=now,
                    lease_seconds=lease_seconds,
                )
            elif kind == "task.heartbeat":
                result = self._heartbeat(
                    db,
                    body,
                    now=now,
                    lease_seconds=lease_seconds,
                )
            elif kind == "task.ready":
                result = self._ready(db, body, now=now)
            elif kind == "task.failed":
                result = self._terminal(db, body, now=now, state="failed")
            elif kind == "task.blocked":
                result = self._terminal(db, body, now=now, state="blocked")
            else:
                raise CoordinatorError(f"unsupported message kind {kind!r}")

            db.execute(
                "INSERT INTO inbox_messages(message_id, run_id, task_id, kind, processed_at, result_json) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    body["message_id"],
                    body["run_id"],
                    body["task_id"],
                    body["kind"],
                    now,
                    json.dumps(result, sort_keys=True, separators=(",", ":")),
                ),
            )
            return result

    def _task(
        self,
        db: sqlite3.Connection,
        body: Mapping[str, Any],
    ) -> sqlite3.Row | None:
        return db.execute(
            "SELECT * FROM tasks WHERE run_id = ? AND task_id = ?",
            (body["run_id"], body["task_id"]),
        ).fetchone()

    def _check_generation(
        self,
        row: sqlite3.Row,
        body: Mapping[str, Any],
    ) -> None:
        if int(row["generation"]) != int(body["generation"]):
            raise CoordinatorError(
                f"stale task generation {body['generation']}; "
                f"authoritative generation is {row['generation']}"
            )

    def _require_lease(
        self,
        row: sqlite3.Row,
        payload: Mapping[str, Any],
        *,
        now: float,
    ) -> None:
        token = _identifier(payload.get("lease_token"), "payload.lease_token")
        if row["lease_token_hash"] != self._lease_hash(token):
            raise CoordinatorError("lease token does not match the current task owner")
        expires = row["lease_expires_at"]
        if expires is None or float(expires) <= now:
            raise CoordinatorError("task lease has expired")

    def _dispatch(
        self,
        db: sqlite3.Connection,
        body: Mapping[str, Any],
        *,
        now: float,
        lease_seconds: int,
    ) -> dict[str, Any]:
        payload = body["payload"]
        agent_id = _identifier(payload.get("agent_id"), "payload.agent_id")
        base_sha = _identifier(payload.get("base_sha"), "payload.base_sha")
        branch = _identifier(payload.get("branch"), "payload.branch")
        worktree = _identifier(payload.get("worktree"), "payload.worktree")
        dependencies = _string_list(payload.get("depends_on"), "payload.depends_on")
        write_scope = _string_list(payload.get("write_scope"), "payload.write_scope")
        exclusive_resources = _string_list(
            payload.get("exclusive_resources"),
            "payload.exclusive_resources",
        )
        row = self._task(db, body)
        if row is not None:
            if int(body["generation"]) <= int(row["generation"]):
                raise CoordinatorError(
                    f"task already exists at generation {row['generation']}; "
                    "dispatch requires a higher generation"
                )
            if row["state"] not in TERMINAL_TASK_STATES | {"blocked"} and (
                row["lease_expires_at"] is None
                or float(row["lease_expires_at"]) > now
            ):
                raise CoordinatorError("cannot replace a task with a live lease")
            db.execute(
                "UPDATE resource_claims SET released_at = ? WHERE run_id = ? AND task_id = ? AND released_at IS NULL",
                (now, body["run_id"], body["task_id"]),
            )

        for dependency in dependencies:
            dep = db.execute(
                "SELECT state FROM tasks WHERE run_id = ? AND task_id = ?",
                (body["run_id"], dependency),
            ).fetchone()
            if dep is None or dep["state"] != "merged":
                raise CoordinatorError(f"dependency {dependency!r} is not merged")

        conflicts: list[str] = []
        for resource in exclusive_resources:
            hit = db.execute(
                """SELECT task_id FROM resource_claims
                    WHERE resource = ? AND released_at IS NULL AND exclusive = 1
                      AND NOT (run_id = ? AND task_id = ?) LIMIT 1""",
                (resource, body["run_id"], body["task_id"]),
            ).fetchone()
            if hit is not None:
                conflicts.append(f"{resource}:{hit['task_id']}")
        if conflicts:
            raise CoordinatorError(
                "exclusive resource conflict: " + ", ".join(sorted(conflicts))
            )

        lease_token = secrets.token_urlsafe(32)
        generation = int(body["generation"])
        db.execute(
            """INSERT INTO tasks(
                    run_id, task_id, generation, state, base_sha, branch, worktree,
                    agent_id, lease_token_hash, lease_expires_at, updated_at
               ) VALUES (?, ?, ?, 'running', ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(run_id, task_id) DO UPDATE SET
                 generation=excluded.generation, state='running',
                 base_sha=excluded.base_sha, branch=excluded.branch,
                 worktree=excluded.worktree, agent_id=excluded.agent_id,
                 lease_token_hash=excluded.lease_token_hash,
                 lease_expires_at=excluded.lease_expires_at,
                 head_sha=NULL, updated_at=excluded.updated_at""",
            (
                body["run_id"],
                body["task_id"],
                generation,
                base_sha,
                branch,
                worktree,
                agent_id,
                self._lease_hash(lease_token),
                now + lease_seconds,
                now,
            ),
        )
        db.execute(
            "DELETE FROM task_dependencies WHERE run_id = ? AND task_id = ?",
            (body["run_id"], body["task_id"]),
        )
        db.executemany(
            "INSERT INTO task_dependencies(run_id, task_id, dependency_task_id) VALUES (?, ?, ?)",
            [(body["run_id"], body["task_id"], dep) for dep in dependencies],
        )
        for resource in write_scope:
            db.execute(
                "INSERT INTO resource_claims(run_id, task_id, generation, resource, exclusive, released_at) VALUES (?, ?, ?, ?, 0, NULL)",
                (
                    body["run_id"],
                    body["task_id"],
                    generation,
                    "path:" + resource,
                ),
            )
        for resource in exclusive_resources:
            db.execute(
                "INSERT INTO resource_claims(run_id, task_id, generation, resource, exclusive, released_at) VALUES (?, ?, ?, ?, 1, NULL)",
                (body["run_id"], body["task_id"], generation, resource),
            )
        event = {
            "run_id": body["run_id"],
            "task_id": body["task_id"],
            "generation": generation,
            "agent_id": agent_id,
            "base_sha": base_sha,
            "branch": branch,
            "worktree": worktree,
            "lease_token": lease_token,
            "lease_expires_at": now + lease_seconds,
        }
        self._outbox(db, kind="agent.execute", body=event, now=now)
        return {"status": "dispatched", **event}

    def _heartbeat(
        self,
        db: sqlite3.Connection,
        body: Mapping[str, Any],
        *,
        now: float,
        lease_seconds: int,
    ) -> dict[str, Any]:
        row = self._task(db, body)
        if row is None:
            raise CoordinatorError("unknown task")
        self._check_generation(row, body)
        self._require_lease(row, body["payload"], now=now)
        if row["state"] != "running":
            raise CoordinatorError(
                f"cannot heartbeat task in state {row['state']!r}"
            )
        expires = now + lease_seconds
        db.execute(
            "UPDATE tasks SET lease_expires_at = ?, updated_at = ? WHERE run_id = ? AND task_id = ?",
            (expires, now, body["run_id"], body["task_id"]),
        )
        return {"status": "renewed", "lease_expires_at": expires}

    def _ready(
        self,
        db: sqlite3.Connection,
        body: Mapping[str, Any],
        *,
        now: float,
    ) -> dict[str, Any]:
        row = self._task(db, body)
        if row is None:
            raise CoordinatorError("unknown task")
        self._check_generation(row, body)
        self._require_lease(row, body["payload"], now=now)
        if row["state"] != "running":
            raise CoordinatorError(
                f"cannot submit candidate from state {row['state']!r}"
            )
        head_sha = _identifier(body["payload"].get("head_sha"), "payload.head_sha")
        db.execute(
            "UPDATE tasks SET state='ready', head_sha=?, updated_at=? WHERE run_id=? AND task_id=?",
            (head_sha, now, body["run_id"], body["task_id"]),
        )
        db.execute(
            "INSERT OR IGNORE INTO candidates(run_id, task_id, generation, head_sha, submitted_at) VALUES (?, ?, ?, ?, ?)",
            (
                body["run_id"],
                body["task_id"],
                body["generation"],
                head_sha,
                now,
            ),
        )
        self._outbox(
            db,
            kind="integration.requested",
            body={
                "run_id": body["run_id"],
                "task_id": body["task_id"],
                "generation": body["generation"],
                "base_sha": row["base_sha"],
                "head_sha": head_sha,
                "branch": row["branch"],
                "worktree": row["worktree"],
            },
            now=now,
        )
        return {"status": "ready", "head_sha": head_sha}

    def _terminal(
        self,
        db: sqlite3.Connection,
        body: Mapping[str, Any],
        *,
        now: float,
        state: str,
    ) -> dict[str, Any]:
        row = self._task(db, body)
        if row is None:
            raise CoordinatorError("unknown task")
        self._check_generation(row, body)
        self._require_lease(row, body["payload"], now=now)
        db.execute(
            "UPDATE tasks SET state=?, lease_expires_at=NULL, updated_at=? WHERE run_id=? AND task_id=?",
            (state, now, body["run_id"], body["task_id"]),
        )
        db.execute(
            "UPDATE resource_claims SET released_at=? WHERE run_id=? AND task_id=? AND generation=? AND released_at IS NULL",
            (
                now,
                body["run_id"],
                body["task_id"],
                body["generation"],
            ),
        )
        self._outbox(
            db,
            kind=f"task.{state}",
            body={
                "run_id": body["run_id"],
                "task_id": body["task_id"],
                "generation": body["generation"],
            },
            now=now,
        )
        return {"status": state}

    def unpublished_outbox(
        self,
        *,
        limit: int = 100,
    ) -> list[tuple[int, dict[str, Any]]]:
        rows = self._db.execute(
            "SELECT sequence, payload_json FROM outbox_messages WHERE published_at IS NULL ORDER BY sequence LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            (int(row["sequence"]), json.loads(row["payload_json"]))
            for row in rows
        ]

    def mark_outbox_published(self, sequence: int) -> None:
        with self.transaction() as db:
            db.execute(
                "UPDATE outbox_messages SET published_at=? WHERE sequence=? AND published_at IS NULL",
                (self._now(), sequence),
            )

    def task(self, run_id: str, task_id: str) -> dict[str, Any] | None:
        row = self._db.execute(
            "SELECT * FROM tasks WHERE run_id=? AND task_id=?",
            (run_id, task_id),
        ).fetchone()
        return dict(row) if row is not None else None

    def close(self) -> None:
        self._db.close()


class QueueCoordinator:
    """Consumes queue deliveries, commits authoritative state, then acknowledges."""

    def __init__(
        self,
        *,
        queue: QueueTransport,
        state: CoordinatorState,
        event_queue: QueueTransport | None = None,
        visibility_timeout_seconds: int = DEFAULT_VISIBILITY_TIMEOUT_SECONDS,
        lease_seconds: int = DEFAULT_LEASE_SECONDS,
        max_attempts: int = MAX_DELIVERY_ATTEMPTS,
    ) -> None:
        self.queue = queue
        self.state = state
        self.event_queue = event_queue
        self.visibility_timeout_seconds = visibility_timeout_seconds
        self.lease_seconds = lease_seconds
        self.max_attempts = max_attempts

    def consume_one(self) -> dict[str, Any] | None:
        delivery = self.queue.receive(
            visibility_timeout_seconds=self.visibility_timeout_seconds
        )
        if delivery is None:
            self.publish_outbox()
            return None
        try:
            result = self.state.process(
                delivery.message,
                lease_seconds=self.lease_seconds,
            )
        except CoordinatorError as exc:
            if delivery.attempt >= self.max_attempts:
                self.queue.dead_letter(delivery.receipt, reason=str(exc))
                return {
                    "status": "dead-lettered",
                    "error": str(exc),
                    "attempt": delivery.attempt,
                }
            self.queue.retry(
                delivery.receipt,
                delay_seconds=min(60, 2 ** max(0, delivery.attempt - 1)),
            )
            return {
                "status": "retry",
                "error": str(exc),
                "attempt": delivery.attempt,
            }
        # Ack only after the authoritative transaction commits. If ack fails,
        # redelivery is harmless because inbox_messages returns the same result.
        self.queue.ack(delivery.receipt)
        self.publish_outbox()
        return result

    def publish_outbox(self, *, limit: int = 100) -> int:
        if self.event_queue is None:
            return 0
        published = 0
        for sequence, event in self.state.unpublished_outbox(limit=limit):
            # Queue transports deduplicate by message_id when possible. If a
            # remote transport does not, downstream consumers use the same
            # inbox pattern as this coordinator.
            self.event_queue.send(event)
            self.state.mark_outbox_published(sequence)
            published += 1
        return published


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Consume queue messages for the worktree coordinator"
    )
    parser.add_argument(
        "--state-db",
        required=True,
        help="authoritative coordinator SQLite database",
    )
    parser.add_argument(
        "--queue-db",
        required=True,
        help="local SQLite queue transport",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="process at most one message and exit",
    )
    parser.add_argument("--poll-seconds", type=float, default=1.0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.poll_seconds <= 0:
        raise SystemExit("--poll-seconds must be positive")
    queue = SQLiteQueue(args.queue_db, name="coordinator-input")
    events = SQLiteQueue(args.queue_db, name="coordinator-events")
    state = CoordinatorState(args.state_db)
    coordinator = QueueCoordinator(
        queue=queue,
        state=state,
        event_queue=events,
    )
    try:
        while True:
            result = coordinator.consume_one()
            if result is not None:
                print(json.dumps(result, sort_keys=True))
            if args.once:
                return 0
            if result is None:
                time.sleep(args.poll_seconds)
    except KeyboardInterrupt:
        return 130
    finally:
        state.close()
        queue.close()
        events.close()


if __name__ == "__main__":
    raise SystemExit(main())
