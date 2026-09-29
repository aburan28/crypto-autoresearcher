#!/usr/bin/env python3
"""Bounded streaming primitives for the prospective spectral runner.

The helpers in this module never construct a complete encoded artifact.  A
single scientific record may be materialized by its caller as the current
bounded cell, but reads, encodes, hashes, and writes cross the filesystem in
chunks no larger than :data:`MAX_CHUNK_BYTES`.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, BinaryIO, Callable, Iterable, Iterator


MAX_CHUNK_BYTES = 64 * 1024
_TEXT_CHARS_PER_CHUNK = MAX_CHUNK_BYTES // 8


class StreamingEncodingError(ValueError):
    """A value cannot be represented without changing canonical semantics."""


class GuardedDigestWriter:
    """Hash every bounded fragment during the same pass that writes it."""

    def __init__(
        self,
        handle: BinaryIO,
        *,
        check: Callable[[], None] | None = None,
        on_progress: Callable[[dict[str, Any]], None] | None = None,
        purpose: str = "stream_write",
    ) -> None:
        self.handle = handle
        self.check = check
        self.on_progress = on_progress
        self.purpose = purpose
        self.digest = hashlib.sha256()
        self.bytes_written = 0
        self.fragments_written = 0

    def write(self, fragment: bytes) -> None:
        if not isinstance(fragment, bytes):
            raise TypeError("stream fragments must be bytes")
        if len(fragment) > MAX_CHUNK_BYTES:
            raise StreamingEncodingError(
                f"stream fragment is {len(fragment)} bytes; cap is {MAX_CHUNK_BYTES}"
            )
        if self.on_progress is not None:
            self.on_progress(
                {
                    "event": "stream_fragment_pending",
                    "phase": self.purpose,
                    "fragment_index": self.fragments_written,
                    "fragment_bytes": len(fragment),
                }
            )
        if self.check is not None:
            self.check()
        if fragment:
            self.handle.write(fragment)
            self.digest.update(fragment)
            self.bytes_written += len(fragment)
        self.fragments_written += 1

    def write_text(self, text: str) -> None:
        """Encode bounded character slices, avoiding one whole-string bytes copy."""
        if not isinstance(text, str):
            raise TypeError("text fragment must be str")
        for offset in range(0, len(text), _TEXT_CHARS_PER_CHUNK):
            encoded = text[offset : offset + _TEXT_CHARS_PER_CHUNK].encode("utf-8")
            if len(encoded) > MAX_CHUNK_BYTES:
                raise StreamingEncodingError("bounded UTF-8 fragment exceeded the byte cap")
            self.write(encoded)
        if not text:
            self.write(b"")

    def hexdigest(self) -> str:
        return self.digest.hexdigest()


def _write_json_string(writer: GuardedDigestWriter, value: str) -> None:
    writer.write(b'"')
    for offset in range(0, len(value), _TEXT_CHARS_PER_CHUNK):
        # Each independently escaped interior concatenates to the same JSON
        # string.  The outer quotes are written exactly once.
        escaped = json.dumps(
            value[offset : offset + _TEXT_CHARS_PER_CHUNK],
            ensure_ascii=False,
            separators=(",", ":"),
        )[1:-1]
        writer.write_text(escaped)
    writer.write(b'"')


def write_json_value(writer: GuardedDigestWriter, value: Any) -> None:
    """Write deterministic JSON recursively without whole-document encoding.

    Mapping keys must already be strings.  Refusing integer keys prevents the
    silent key conversion that would otherwise make JSON-as-YAML change the
    manifest's document semantics.
    """
    if value is None:
        writer.write(b"null")
    elif value is True:
        writer.write(b"true")
    elif value is False:
        writer.write(b"false")
    elif isinstance(value, str):
        _write_json_string(writer, value)
    elif isinstance(value, int) and not isinstance(value, bool):
        writer.write(str(value).encode("ascii"))
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise StreamingEncodingError("non-finite floats are not canonical JSON")
        writer.write(repr(value).encode("ascii"))
    elif isinstance(value, (list, tuple)):
        writer.write(b"[")
        for index, item in enumerate(value):
            if index:
                writer.write(b",")
            write_json_value(writer, item)
        writer.write(b"]")
    elif isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise StreamingEncodingError("JSON-as-YAML mapping keys must be strings")
        writer.write(b"{")
        for index, key in enumerate(sorted(value)):
            if index:
                writer.write(b",")
            _write_json_string(writer, key)
            writer.write(b":")
            write_json_value(writer, value[key])
        writer.write(b"}")
    else:
        raise StreamingEncodingError(f"unsupported canonical JSON value: {type(value).__name__}")


def write_json_document(writer: GuardedDigestWriter, value: Any) -> None:
    write_json_value(writer, value)
    writer.write(b"\n")


def append_jsonl(
    path: Path,
    value: Any,
    *,
    check: Callable[[], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
    purpose: str = "spool_append",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab") as handle:
        writer = GuardedDigestWriter(
            handle, check=check, on_progress=on_progress, purpose=purpose
        )
        write_json_document(writer, value)
        handle.flush()
        os.fsync(handle.fileno())


def iter_jsonl(
    path: Path,
    *,
    check: Callable[[], None] | None = None,
    maximum_record_bytes: int = 64 * 1024 * 1024,
) -> Iterator[Any]:
    """Read at most 64 KiB at a time and retain only the current JSON record."""
    if not path.exists():
        return
    pending = bytearray()
    with path.open("rb") as handle:
        while True:
            if check is not None:
                check()
            chunk = handle.read(MAX_CHUNK_BYTES)
            if not chunk:
                break
            pending.extend(chunk)
            if len(pending) > maximum_record_bytes and b"\n" not in pending:
                raise StreamingEncodingError(
                    f"JSONL record exceeds {maximum_record_bytes} bytes"
                )
            while True:
                newline = pending.find(b"\n")
                if newline < 0:
                    break
                raw = bytes(pending[:newline])
                del pending[: newline + 1]
                if raw:
                    yield json.loads(raw)
        if pending:
            yield json.loads(bytes(pending))


def copy_file(
    source: Path,
    writer: GuardedDigestWriter,
    *,
    check: Callable[[], None] | None = None,
) -> None:
    with source.open("rb") as handle:
        while True:
            if check is not None:
                check()
            chunk = handle.read(MAX_CHUNK_BYTES)
            if not chunk:
                break
            writer.write(chunk)


def stream_json_array(
    writer: GuardedDigestWriter,
    values: Iterable[Any],
) -> None:
    writer.write(b"[")
    for index, value in enumerate(values):
        if index:
            writer.write(b",")
        write_json_value(writer, value)
    writer.write(b"]")


def bounded_graph_size(value: Any, *, maximum_bytes: int) -> int:
    """Conservatively bound a deliberately small in-memory manifest graph."""
    total = 0
    stack = [value]
    while stack:
        current = stack.pop()
        if current is None or isinstance(current, (bool, int, float)):
            total += 32
        elif isinstance(current, str):
            total += len(current.encode("utf-8")) + 16
        elif isinstance(current, dict):
            if any(not isinstance(key, str) for key in current):
                raise StreamingEncodingError("manifest mapping keys must be strings")
            total += 64
            stack.extend(current.keys())
            stack.extend(current.values())
        elif isinstance(current, (list, tuple)):
            total += 64
            stack.extend(current)
        else:
            raise StreamingEncodingError(
                f"unsupported manifest graph value: {type(current).__name__}"
            )
        if total > maximum_bytes:
            raise StreamingEncodingError(
                f"small manifest graph exceeds its {maximum_bytes}-byte lifetime guard"
            )
    return total


def hash_file(
    path: Path,
    *,
    check: Callable[[], None] | None = None,
) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            if check is not None:
                check()
            chunk = handle.read(MAX_CHUNK_BYTES)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()
