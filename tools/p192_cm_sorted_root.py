#!/usr/bin/env python3
"""Independently verify the EXP-SCURVE-647ade v3 canonical-set root.

This tool does not enumerate CM exponent vectors and does not repair the
immutable v2 run.  It verifies two producer-materialized, sorted binary member
streams using the byte contract frozen in the v2-to-v3 protocol amendment.
Python byte ordering is unsigned lexicographic ordering, matching Rust's
``[u8; 26]::Ord``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


EXPERIMENT_ID = "EXP-SCURVE-647ade"
PROTOCOL_VERSION = 3
GENERATOR_PRIMES = (5, 11, 31, 13, 23, 37, 43, 73, 89, 101, 103, 107, 113)
RAMIFIED_COORDINATES = 3
VECTOR_LENGTH = len(GENERATOR_PRIMES)
MEMBER_SIZE = VECTOR_LENGTH * 2
MAX_DEGREE = 1 << 48
EXPECTED_COUNT = 4_974_348
EXPECTED_STREAM_BYTES = EXPECTED_COUNT * MEMBER_SIZE
DOMAIN = b"p192-cm-canonical-set-root/v1\0"
LEGACY_BLAKE3_DIAGNOSTIC = (
    "xor=fa31a647dec55822513049a87cdb4174231c9da27174ffb826fd250e8ca4573e;"
    "sum=8eedade908d10e620136a0e5547b1331766409131afa4c7bf3fcab2439451806"
)
ROOT_RE = re.compile(r"[0-9a-f]{64}\Z")
CHUNK_MEMBERS = 65_536


class VerificationError(ValueError):
    """The supplied stream violates the frozen v3 byte or membership contract."""


@dataclass(frozen=True)
class StreamVerification:
    path: str
    member_count: int
    stream_bytes: int
    stream_sha256: str
    canonical_set_root_sha256: str
    zero_member_count: int
    strict_unsigned_lexicographic_order: bool
    all_members_semantically_valid: bool


def encode_member(exponents: Sequence[int]) -> bytes:
    """Encode one exponent vector as thirteen signed little-endian i16s."""
    if len(exponents) != VECTOR_LENGTH:
        raise VerificationError(
            f"member has {len(exponents)} exponents, expected {VECTOR_LENGTH}"
        )
    encoded = bytearray()
    for coordinate, exponent in enumerate(exponents):
        if isinstance(exponent, bool) or not isinstance(exponent, int):
            raise VerificationError(f"coordinate {coordinate} is not an integer")
        if not -(1 << 15) <= exponent < (1 << 15):
            raise VerificationError(f"coordinate {coordinate} is outside signed i16")
        encoded.extend(exponent.to_bytes(2, "little", signed=True))
    assert len(encoded) == MEMBER_SIZE
    return bytes(encoded)


def decode_member(member: bytes) -> tuple[int, ...]:
    if len(member) != MEMBER_SIZE:
        raise VerificationError(
            f"member is {len(member)} bytes, expected exactly {MEMBER_SIZE}"
        )
    return struct.unpack("<13h", member)


def validate_member(member: bytes, index: int | None = None) -> tuple[int, ...]:
    """Decode and enforce the frozen boundary and conjugation convention."""
    where = "member" if index is None else f"member {index}"
    exponents = decode_member(member)
    if any(exponent < 0 for exponent in exponents[:RAMIFIED_COORDINATES]):
        raise VerificationError(f"{where} has a negative ramified exponent")

    for exponent in exponents[RAMIFIED_COORDINATES:]:
        if exponent:
            if exponent < 0:
                raise VerificationError(
                    f"{where} violates first-nonzero-split-positive canonicalization"
                )
            break

    degree = 1
    for prime, exponent in zip(GENERATOR_PRIMES, exponents, strict=True):
        for _ in range(abs(exponent)):
            if degree > MAX_DEGREE // prime:
                raise VerificationError(f"{where} exceeds the 2^48 norm boundary")
            degree *= prime
    return exponents


def root_for_sorted_members(members: Sequence[bytes]) -> str:
    """Small-fixture helper implementing the exact authoritative preimage."""
    previous: bytes | None = None
    root = hashlib.sha256()
    root.update(DOMAIN)
    root.update(struct.pack("<Q", len(members)))
    for index, member in enumerate(members):
        validate_member(member, index)
        if previous is not None and previous >= member:
            kind = "duplicate" if previous == member else "out-of-order"
            raise VerificationError(f"member {index} is {kind}")
        root.update(member)
        previous = member
    return root.hexdigest()


def _stable_file_identity(stat: os.stat_result) -> tuple[int, int, int, int]:
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns


def verify_sorted_stream(
    path: Path,
    *,
    expected_count: int = EXPECTED_COUNT,
    expected_root: str | None = None,
    require_zero: bool = True,
) -> StreamVerification:
    """Verify one raw, already-sorted member stream and compute its v3 root."""
    path = Path(path)
    if path.is_symlink():
        raise VerificationError(f"refusing symlink stream: {path}")
    if expected_count < 0 or expected_count >= 1 << 64:
        raise VerificationError("expected count does not fit u64")
    if expected_root is not None and ROOT_RE.fullmatch(expected_root) is None:
        raise VerificationError("expected root must be 64 lowercase hexadecimal chars")

    try:
        with path.open("rb") as stream:
            before = os.fstat(stream.fileno())
            if before.st_size % MEMBER_SIZE:
                raise VerificationError(
                    f"stream length {before.st_size} is not divisible by {MEMBER_SIZE}"
                )
            count = before.st_size // MEMBER_SIZE
            if count != expected_count:
                raise VerificationError(
                    f"stream has {count} members, expected {expected_count}"
                )

            root = hashlib.sha256()
            root.update(DOMAIN)
            root.update(struct.pack("<Q", count))
            stream_digest = hashlib.sha256()
            previous: bytes | None = None
            zero_count = 0
            member_index = 0
            read_size = MEMBER_SIZE * CHUNK_MEMBERS

            while chunk := stream.read(read_size):
                if len(chunk) % MEMBER_SIZE:
                    raise VerificationError("a stream read ended inside a member")
                root.update(chunk)
                stream_digest.update(chunk)
                for offset in range(0, len(chunk), MEMBER_SIZE):
                    member = chunk[offset : offset + MEMBER_SIZE]
                    if previous is not None and previous >= member:
                        kind = "duplicate" if previous == member else "out-of-order"
                        raise VerificationError(f"member {member_index} is {kind}")
                    validate_member(member, member_index)
                    if member == bytes(MEMBER_SIZE):
                        zero_count += 1
                    previous = member
                    member_index += 1

            after = os.fstat(stream.fileno())
    except OSError as error:
        raise VerificationError(f"cannot read stream {path}: {error}") from error

    if _stable_file_identity(before) != _stable_file_identity(after):
        raise VerificationError("stream identity, size, or modification time changed while read")
    if member_index != count:
        raise VerificationError(f"read {member_index} members from a {count}-member stream")
    if require_zero and zero_count != 1:
        raise VerificationError(f"all-zero member occurs {zero_count} times, expected once")

    root_hex = root.hexdigest()
    if expected_root is not None and root_hex != expected_root:
        raise VerificationError(
            f"authoritative root {root_hex} does not match expected {expected_root}"
        )
    return StreamVerification(
        path=str(path.resolve()),
        member_count=count,
        stream_bytes=before.st_size,
        stream_sha256=stream_digest.hexdigest(),
        canonical_set_root_sha256=root_hex,
        zero_member_count=zero_count,
        strict_unsigned_lexicographic_order=True,
        all_members_semantically_valid=True,
    )


def verify_pair(
    forward_path: Path,
    reverse_path: Path,
    *,
    expected_count: int = EXPECTED_COUNT,
    expected_root: str | None = None,
) -> dict[str, object]:
    """Verify independent traversal streams and require identical roots."""
    forward_path = Path(forward_path)
    reverse_path = Path(reverse_path)
    try:
        forward_stat = forward_path.stat()
        reverse_stat = reverse_path.stat()
        forward_identity = (
            forward_path.resolve(),
            forward_stat.st_dev,
            forward_stat.st_ino,
        )
        reverse_identity = (
            reverse_path.resolve(),
            reverse_stat.st_dev,
            reverse_stat.st_ino,
        )
    except OSError as error:
        raise VerificationError(f"cannot stat traversal streams: {error}") from error
    if (
        forward_identity[0] == reverse_identity[0]
        or forward_identity[1:] == reverse_identity[1:]
    ):
        raise VerificationError(
            "forward and reverse streams must be distinct files, not one path or hardlink"
        )
    forward = verify_sorted_stream(
        forward_path, expected_count=expected_count, expected_root=expected_root
    )
    reverse = verify_sorted_stream(
        reverse_path, expected_count=expected_count, expected_root=expected_root
    )
    if forward.canonical_set_root_sha256 != reverse.canonical_set_root_sha256:
        raise VerificationError("forward and reverse authoritative roots differ")
    return {
        "schema": "p192-cm-sorted-root-verification/v1",
        "experiment_id": EXPERIMENT_ID,
        "protocol_version": PROTOCOL_VERSION,
        "domain_ascii_nul_terminated": DOMAIN[:-1].decode("ascii") + r"\0",
        "domain_hex": DOMAIN.hex(),
        "member_encoding": "13 signed i16 little-endian; 26 bytes; no framing",
        "generator_coordinate_order": list(GENERATOR_PRIMES),
        "ordering": "unsigned-byte lexicographic; strict; no duplicates",
        "count_prefix": "u64 little-endian",
        "expected_member_count": expected_count,
        "expected_stream_bytes": expected_count * MEMBER_SIZE,
        "forward": asdict(forward),
        "reverse": asdict(reverse),
        "roots_match": True,
        "expected_root": expected_root,
        "expected_root_checked": expected_root is not None,
        "legacy_canonical_set_digest": LEGACY_BLAKE3_DIAGNOSTIC,
        "legacy_digest_role": "producer diagnostic only; not recomputed or authoritative",
        "status": "pass",
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forward", type=Path, required=True)
    parser.add_argument("--reverse", type=Path, required=True)
    parser.add_argument(
        "--expected-root",
        help="optional externally pinned 64-character lowercase SHA-256 root",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = verify_pair(
            args.forward,
            args.reverse,
            expected_root=args.expected_root,
        )
    except VerificationError as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
