"""Fixed physical BSGS table for TASK-20260908-3b05bc.

The table has exactly one backing store supplied by its caller.  Its three
wire domains are deliberately separate: logical points are 9-byte interchange
objects, hash preimages are 1 or 9 bytes, and physical records are 16-byte
``<IIII`` slots.  No Python point-index is retained beside the buffer.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import struct
from typing import Callable, Final


TASK_TABLE_DOMAIN: Final[bytes] = b"EXP-ECDLP-709063|table|v2"
UINT28_LIMIT: Final[int] = 1 << 28
SLOT_BYTES: Final[int] = 16
EMPTY: Final[int] = 0
AFFINE: Final[int] = 1
INFINITY: Final[int] = 2
_LOGICAL: Final[struct.Struct] = struct.Struct("<BII")
_SLOT: Final[struct.Struct] = struct.Struct("<IIII")


class TableValidationError(ValueError):
    """A caller supplied noncanonical table data or a malformed point."""


class ProgressCancelled(RuntimeError):
    """A supplied bounded progress hook requested a cooperative stop."""


def _uint28(value: int, label: str) -> int:
    if type(value) is not int or value < 0 or value >= UINT28_LIMIT:
        raise TableValidationError(f"{label} must be a non-bool uint28")
    return value


def _decoder_bytes(
    raw: bytes | bytearray | memoryview,
    *,
    accepted_lengths: tuple[int, ...],
    length_error: str,
    label: str,
) -> bytes:
    """Validate a public decoder carrier before coercing a mutable buffer."""
    if not isinstance(raw, (bytes, bytearray, memoryview)):
        raise TableValidationError(f"{label} decoder input must be bytes, bytearray, or memoryview")
    try:
        buffer = raw if isinstance(raw, memoryview) else memoryview(raw)
        byte_length = buffer.nbytes
    except (TypeError, ValueError, BufferError):
        raise TableValidationError(f"{label} decoder input is an invalid or released buffer") from None
    if byte_length not in accepted_lengths:
        raise TableValidationError(length_error)
    try:
        raw_bytes = bytes(buffer)
    except (TypeError, ValueError, BufferError):
        raise TableValidationError(f"{label} decoder input is invalid") from None
    if len(raw_bytes) != byte_length:
        raise TableValidationError(f"{label} decoder input byte count changed during coercion")
    return raw_bytes


@dataclass(frozen=True)
class LogicalPoint:
    """A logical point, distinct from hash and physical-slot encodings."""

    tag: int
    x: int
    y: int

    def __post_init__(self) -> None:
        if type(self.tag) is not int or self.tag not in (EMPTY, AFFINE):
            raise TableValidationError("logical tag must be 0 (O) or 1 (affine)")
        _uint28(self.x, "logical x")
        _uint28(self.y, "logical y")
        if self.tag == EMPTY and (self.x != 0 or self.y != 0):
            raise TableValidationError("logical O must have x=y=0")

    @classmethod
    def infinity(cls) -> "LogicalPoint":
        return cls(EMPTY, 0, 0)

    @classmethod
    def affine(cls, x: int, y: int) -> "LogicalPoint":
        return cls(AFFINE, x, y)

    @property
    def is_infinity(self) -> bool:
        return self.tag == EMPTY


@dataclass(frozen=True)
class PhysicalSlot:
    """A decoded fixed-width physical slot; ``None`` represents an empty slot."""

    state: int
    x: int = 0
    y: int = 0
    exponent: int = 0

    def __post_init__(self) -> None:
        if type(self.state) is not int or self.state not in (EMPTY, AFFINE, INFINITY):
            raise TableValidationError("physical state must be 0, 1, or 2")
        _uint28(self.x, "physical x")
        _uint28(self.y, "physical y")
        _uint28(self.exponent, "physical exponent")
        if self.state == EMPTY and (self.x != 0 or self.y != 0 or self.exponent != 0):
            raise TableValidationError("physical empty slot must be all zero")
        if self.state == INFINITY and (self.x != 0 or self.y != 0):
            raise TableValidationError("physical O slot must have x=y=0")

    @classmethod
    def empty(cls) -> "PhysicalSlot":
        return cls(EMPTY, 0, 0, 0)

    @classmethod
    def from_logical(cls, point: LogicalPoint, exponent: int) -> "PhysicalSlot":
        _uint28(exponent, "physical exponent")
        if point.is_infinity:
            return cls(INFINITY, 0, 0, exponent)
        return cls(AFFINE, point.x, point.y, exponent)

    def logical_point(self) -> LogicalPoint:
        if self.state == EMPTY:
            raise TableValidationError("physical empty has no logical point")
        if self.state == INFINITY:
            return LogicalPoint.infinity()
        return LogicalPoint.affine(self.x, self.y)


def encode_logical_point(point: LogicalPoint) -> bytes:
    """Return the 9-byte logical interchange encoding, never a slot encoding."""
    if not isinstance(point, LogicalPoint):
        raise TableValidationError("logical encoder requires LogicalPoint")
    return _LOGICAL.pack(point.tag, point.x, point.y)


def decode_logical_point(raw: bytes | bytearray | memoryview) -> LogicalPoint:
    raw_bytes = _decoder_bytes(
        raw,
        accepted_lengths=(_LOGICAL.size,),
        length_error="logical point must be exactly 9 bytes",
        label="logical point",
    )
    tag, x, y = _LOGICAL.unpack(raw_bytes)
    return LogicalPoint(tag, x, y)


def encode_hash_preimage(point: LogicalPoint) -> bytes:
    """Return the exact one- or nine-byte input to the table hash."""
    if not isinstance(point, LogicalPoint):
        raise TableValidationError("hash encoder requires LogicalPoint")
    if point.is_infinity:
        return b"\x00"
    return b"\x04" + point.x.to_bytes(4, "big") + point.y.to_bytes(4, "big")


def decode_hash_preimage(raw: bytes | bytearray | memoryview) -> LogicalPoint:
    raw_bytes = _decoder_bytes(
        raw,
        accepted_lengths=(1, 9),
        length_error="hash preimage must be O=00 or affine=04||x||y",
        label="hash preimage",
    )
    if raw_bytes == b"\x00":
        return LogicalPoint.infinity()
    if len(raw_bytes) != 9 or raw_bytes[0] != 4:
        raise TableValidationError("hash preimage must be O=00 or affine=04||x||y")
    return LogicalPoint.affine(
        int.from_bytes(raw_bytes[1:5], "big"), int.from_bytes(raw_bytes[5:9], "big")
    )


def encode_physical_slot(slot: PhysicalSlot) -> bytes:
    """Return one canonical 16-byte little-endian ``<IIII`` physical slot."""
    if not isinstance(slot, PhysicalSlot):
        raise TableValidationError("physical encoder requires PhysicalSlot")
    return _SLOT.pack(slot.x, slot.y, slot.exponent, slot.state)


def decode_physical_slot(raw: bytes | bytearray | memoryview) -> PhysicalSlot:
    raw_bytes = _decoder_bytes(
        raw,
        accepted_lengths=(SLOT_BYTES,),
        length_error="physical slot must be exactly 16 bytes",
        label="physical slot",
    )
    x, y, exponent, state = _SLOT.unpack(raw_bytes)
    return PhysicalSlot(state, x, y, exponent)


@dataclass(frozen=True)
class TableCounters:
    table_operations: int
    hash_calls: int
    hash_preimage_bytes: int
    probes: int
    bytes_read: int
    bytes_written: int
    occupied: int


@dataclass(frozen=True)
class TableResult:
    status: str
    exponent: int | None
    slot: int | None
    counters: TableCounters
    refusal: dict[str, object] | None = None

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "status": self.status,
            "exponent": self.exponent,
            "slot": self.slot,
            "counters": asdict(self.counters),
        }
        if self.refusal is not None:
            result["refusal"] = self.refusal
        return result


ProgressHook = Callable[[str, dict[str, int]], bool | None]


class FixedPhysicalTable:
    """Open-addressed table with a caller-owned, fixed physical buffer only."""

    def __init__(self, budget_bytes: int, buffer: bytearray) -> None:
        if type(budget_bytes) is not int or budget_bytes < 0:
            raise TableValidationError("budget_bytes must be a nonnegative non-bool integer")
        if type(buffer) is not bytearray:
            raise TableValidationError("caller must supply exactly one bytearray buffer")
        self._budget_bytes = budget_bytes
        self._slots = budget_bytes // SLOT_BYTES
        expected_length = SLOT_BYTES * self._slots
        if len(buffer) != expected_length:
            raise TableValidationError("buffer length must equal 16*floor(C/16)")
        if any(buffer):
            raise TableValidationError("new physical table buffer must be all zero")
        self._buffer = memoryview(buffer).cast("B")
        self._buffer_identity = id(buffer)
        self._capacity = (7 * self._slots) // 10
        self._occupied = 0
        self._table_operations = 0
        self._hash_calls = 0
        self._hash_preimage_bytes = 0
        self._probes = 0
        self._bytes_read = 0
        self._bytes_written = 0

    @property
    def budget_bytes(self) -> int:
        return self._budget_bytes

    @property
    def slots(self) -> int:
        return self._slots

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def occupied(self) -> int:
        return self._occupied

    @property
    def buffer_identity(self) -> int:
        return self._buffer_identity

    @property
    def buffer_length(self) -> int:
        return len(self._buffer)

    def counters(self) -> TableCounters:
        return TableCounters(
            table_operations=self._table_operations,
            hash_calls=self._hash_calls,
            hash_preimage_bytes=self._hash_preimage_bytes,
            probes=self._probes,
            bytes_read=self._bytes_read,
            bytes_written=self._bytes_written,
            occupied=self._occupied,
        )

    def buffer_sha256(self) -> str:
        return hashlib.sha256(self._buffer).hexdigest()

    def _event(self, hook: ProgressHook | None, name: str) -> None:
        if hook is None:
            return
        snapshot = asdict(self.counters())
        decision = hook(name, snapshot)
        if decision is False:
            raise ProgressCancelled(name)

    def _offset(self, slot: int) -> int:
        if type(slot) is not int or slot < 0 or slot >= self._slots:
            raise TableValidationError("physical slot address is out of range")
        offset = SLOT_BYTES * slot
        if offset + SLOT_BYTES > len(self._buffer):
            raise TableValidationError("physical slot address exceeds bounded buffer")
        return offset

    def _read_slot(self, slot: int) -> PhysicalSlot:
        offset = self._offset(slot)
        self._bytes_read += SLOT_BYTES
        return decode_physical_slot(self._buffer[offset:offset + SLOT_BYTES])

    def _write_slot(self, slot: int, record: PhysicalSlot) -> None:
        offset = self._offset(slot)
        encoded = encode_physical_slot(record)
        self._buffer[offset:offset + SLOT_BYTES] = encoded
        self._bytes_written += SLOT_BYTES

    def _hash_slot(self, point: LogicalPoint, hook: ProgressHook | None) -> int:
        if self._slots == 0:
            raise TableValidationError("zero-slot table has no hash address")
        self._event(hook, "table_hash")
        preimage = encode_hash_preimage(point)
        self._hash_calls += 1
        self._hash_preimage_bytes += len(preimage)
        digest = hashlib.sha256(TASK_TABLE_DOMAIN + preimage).digest()
        return int.from_bytes(digest[:8], "little") % self._slots

    def _refusal(self, status: str, before_sha256: str) -> TableResult:
        after_sha256 = self.buffer_sha256()
        return TableResult(
            status=status,
            exponent=None,
            slot=None,
            counters=self.counters(),
            refusal={
                "buffer_identity_before": self._buffer_identity,
                "buffer_identity_after": self._buffer_identity,
                "buffer_length_before": len(self._buffer),
                "buffer_length_after": len(self._buffer),
                "buffer_sha256_before": before_sha256,
                "buffer_sha256_after": after_sha256,
                "unchanged": before_sha256 == after_sha256,
            },
        )

    def insert(self, point: LogicalPoint, exponent: int, hook: ProgressHook | None = None) -> TableResult:
        """Insert one point/exponent pair under the frozen linear-probe policy."""
        if not isinstance(point, LogicalPoint):
            raise TableValidationError("insert requires a logical point")
        _uint28(exponent, "exponent")
        self._table_operations += 1
        before_sha256 = self.buffer_sha256()
        if self._occupied >= self._capacity:
            return self._refusal("TABLE_FULL", before_sha256)
        try:
            start = self._hash_slot(point, hook)
            for step in range(self._slots):
                self._event(hook, "table_probe")
                slot_index = (start + step) % self._slots
                self._probes += 1
                record = self._read_slot(slot_index)
                if record.state == EMPTY:
                    self._event(hook, "table_write")
                    self._write_slot(slot_index, PhysicalSlot.from_logical(point, exponent))
                    self._occupied += 1
                    return TableResult("INSERTED", exponent, slot_index, self.counters())
                if record.logical_point() == point:
                    if record.exponent == exponent:
                        return TableResult("DUPLICATE", exponent, slot_index, self.counters())
                    return self._refusal("COMPLETED_INVALID", before_sha256)
        except ProgressCancelled:
            return self._refusal("CANCELLED", before_sha256)
        return self._refusal("TABLE_FULL", before_sha256)

    def lookup(self, point: LogicalPoint, hook: ProgressHook | None = None) -> TableResult:
        """Look up a logical point without constructing an auxiliary index."""
        if not isinstance(point, LogicalPoint):
            raise TableValidationError("lookup requires a logical point")
        self._table_operations += 1
        before_sha256 = self.buffer_sha256()
        if self._slots == 0:
            return TableResult("NOT_FOUND", None, None, self.counters())
        try:
            start = self._hash_slot(point, hook)
            for step in range(self._slots):
                self._event(hook, "table_probe")
                slot_index = (start + step) % self._slots
                self._probes += 1
                record = self._read_slot(slot_index)
                if record.state == EMPTY:
                    return TableResult("NOT_FOUND", None, slot_index, self.counters())
                if record.logical_point() == point:
                    return TableResult("FOUND", record.exponent, slot_index, self.counters())
        except ProgressCancelled:
            return self._refusal("CANCELLED", before_sha256)
        return TableResult("NOT_FOUND", None, None, self.counters())
