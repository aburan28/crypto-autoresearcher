"""Formal-methods lane for machine-checkable research artifacts.

The formal lane is advisory to the canonical Coordinator.  It can produce
proof evidence and diagnostics, but it cannot mutate authoritative campaign,
ledger, hypothesis, or claim state.
"""

from .lean_worker import LeanWorker
from .models import (
    FormalProofResult,
    FormalProofTask,
    FormalStatus,
    FormalTaskKind,
)

__all__ = [
    "FormalProofResult",
    "FormalProofTask",
    "FormalStatus",
    "FormalTaskKind",
    "LeanWorker",
]
