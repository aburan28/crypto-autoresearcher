"""Durable append-only phase and resource telemetry for a future bounded call.

Each record is one JSON line, written with O_APPEND and fsync before returning.
No absence of a record is interpreted as zero work or zero RSS.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

SCHEMA = "icperf-prime63-phase-v1"


def sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class TraceWriter:
    def __init__(self, path: str | Path, source: str | Path, stream: str):
        self.path = Path(path)
        self.source_sha256 = sha256(source)
        self.stream = stream
        self.sequence = 0
        self.last_mono_ns = 0
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, phase: str, event: str, **fields) -> dict:
        mono = time.monotonic_ns()
        if mono < self.last_mono_ns:
            raise RuntimeError("nonmonotonic_phase_clock")
        self.last_mono_ns = mono
        row = {"schema": SCHEMA, "stream": self.stream,
               "sequence": self.sequence, "pid": os.getpid(),
               "monotonic_ns": mono, "wall_time_ns": time.time_ns(),
               "source_sha256": self.source_sha256, "phase": phase,
               "event": event, "fields": fields}
        encoded = (json.dumps(row, sort_keys=True, separators=(",", ":"),
                              allow_nan=False) + "\n").encode("utf-8")
        fd = os.open(self.path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        try:
            if os.write(fd, encoded) != len(encoded):
                raise OSError("short_trace_write")
            os.fsync(fd)
        finally:
            os.close(fd)
        self.sequence += 1
        return row


def inspect(path: str | Path) -> dict:
    raw = Path(path).read_bytes()
    rows = []
    streams: dict[str, tuple[int, int]] = {}
    error = None
    if raw and not raw.endswith(b"\n"):
        error = "unterminated_final_record"
    for number, line in enumerate(raw.splitlines(), 1):
        try:
            row = json.loads(line)
            if row.get("schema") != SCHEMA:
                raise ValueError("trace_schema_mismatch")
            stream = row["stream"]
            previous = streams.get(stream)
            if previous is not None:
                if row["sequence"] != previous[0] + 1:
                    raise ValueError("trace_sequence_gap")
                if row["monotonic_ns"] < previous[1]:
                    raise ValueError("trace_clock_regression")
            elif row["sequence"] != 0:
                raise ValueError("trace_initial_sequence")
            streams[stream] = (row["sequence"], row["monotonic_ns"])
            rows.append(row)
        except (ValueError, KeyError, TypeError) as exc:
            error = f"record_{number}:{type(exc).__name__}:{exc}"
            break
    return {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw), "records": len(rows), "valid": error is None,
            "error": error, "streams": sorted(streams),
            "last_event": rows[-1]["event"] if rows else None}
