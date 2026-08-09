"""Formal-methods lane for machine-checkable research artifacts.

The formal lane is advisory to the canonical Coordinator.  It can produce
proof evidence and diagnostics, but it cannot mutate authoritative campaign,
ledger, hypothesis, or claim state.
"""

from .integration import (
    FormalSuccessorProposal,
    formal_route_features,
    formal_successor_contract,
    successors_from_formal_result,
    verification_outcome_from_formal_result,
)
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
    "FormalSuccessorProposal",
    "FormalTaskKind",
    "LeanWorker",
    "formal_route_features",
    "formal_successor_contract",
    "successors_from_formal_result",
    "verification_outcome_from_formal_result",
]
