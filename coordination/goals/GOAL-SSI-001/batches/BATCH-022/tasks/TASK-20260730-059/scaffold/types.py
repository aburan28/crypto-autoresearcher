"""Opaque roles and enums for FC0-EXT-PKG-SSI-001 scaffolding.

All encodings are abstract scaffolding tokens. No numeric bit-widths, no
curve/group encodings, no CollimationSieve types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import itertools


class CleanupResult(Enum):
    """Frozen CleanupResult enum from lifetime_hooks_interface.yaml."""

    ok = "ok"
    cleanup_failure = "cleanup_failure"


class FailureChannel(Enum):
    """Named F_* constituents from the frozen interface checklist."""

    F_input = "F_input"
    F_oracle = "F_oracle"
    F_cleanup = "F_cleanup"
    F_stop = "F_stop"
    F_recovery = "F_recovery"
    F_tail = "F_tail"
    F_verify = "F_verify"
    F = "F"


class HandleState(Enum):
    """Lifetime state-machine states for a single object handle."""

    unborn = "unborn"
    live = "live"
    last_used = "last_used"
    cleaned = "cleaned"
    destroyed = "destroyed"


class ObjectClass(Enum):
    W = "W"
    R = "R"
    B = "B"
    M_tail = "M_tail"


_HANDLE_SEQ = itertools.count(1)


@dataclass(frozen=True)
class PublicInstance:
    """Abstract public-instance role for Verify(x, k_prime).

    Encoding is a scaffolding token only. Not a curve point or CSIDH public key.
    """

    token: str
    well_formed: bool = True
    # Synthetic accept token for no-crypto unit tests only; never a crypto secret.
    scaffold_accept_token: Optional[str] = None


@dataclass(frozen=True)
class CandidateSecret:
    """Abstract candidate-secret role for Verify(x, k_prime).

    Encoding is a scaffolding token only. Not an isogeny secret or key.
    """

    token: str
    well_formed: bool = True


@dataclass
class OpaqueHandle:
    """Opaque object handle returned by birth_* hooks."""

    object_id: str
    object_class: ObjectClass
    state: HandleState = HandleState.live
    stage_at_birth: str = ""
    handle_serial: int = field(default_factory=lambda: next(_HANDLE_SEQ))
    notes: dict = field(default_factory=dict)

    def mark(self, new_state: HandleState) -> None:
        self.state = new_state
