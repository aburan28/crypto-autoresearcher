"""FC0-EXT-PKG-SSI-001 scaffolding (TASK-20260730-059).

In-repo typed stubs / state-machine skeleton against frozen Verify and
W/R/B/M_tail lifetime interfaces. Not CollimationSieve. Not cryptographic
Verify. Zero curve/isogeny/quantum-circuit computation.
"""

from .types import CleanupResult, FailureChannel, HandleState, OpaqueHandle, PublicInstance, CandidateSecret
from .verify import Verify
from .lifetime_hooks import LifetimeRegistry
from .state_machine import StageLiveSetTracker

__all__ = [
    "CleanupResult",
    "FailureChannel",
    "HandleState",
    "OpaqueHandle",
    "PublicInstance",
    "CandidateSecret",
    "Verify",
    "LifetimeRegistry",
    "StageLiveSetTracker",
]
