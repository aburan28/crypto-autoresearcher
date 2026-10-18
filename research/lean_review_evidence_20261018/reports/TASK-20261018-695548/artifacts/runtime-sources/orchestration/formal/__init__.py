"""Formal-methods lane for machine-checkable research artifacts.

The lane is advisory to the canonical Coordinator.  It can produce proof
evidence and diagnostics, but it cannot mutate authoritative campaign, ledger,
hypothesis, or claim state.

Two halves, both untrusted on their own:

- a **producer**, :class:`~orchestration.formal.mathcode.MathCodeFormalizer`,
  which turns a human claim into candidate Lean source;
- a **verifier**, :class:`~orchestration.formal.lean_worker.LeanWorker`, which
  is the only thing here whose output counts as machine evidence — and even
  then only pending independent semantic-fidelity review.

The names that bridge into Research Loop v2 (``integration``, ``pipeline``)
depend on the optional ``research-loop`` extra, so they are resolved lazily:
formalizing and verifying works on the base install, and only the routing
bridge needs pydantic.
"""

from typing import TYPE_CHECKING

from .lean_worker import LeanWorker
from .mathcode import (
    FormalizationAttempt,
    FormalizationFailure,
    MathCodeConfig,
    MathCodeFormalizer,
)
from .models import (
    FormalProofResult,
    FormalProofTask,
    FormalStatus,
    FormalTaskKind,
)

if TYPE_CHECKING:  # pragma: no cover - import-time typing only
    from .integration import (
        FormalSuccessorProposal,
        formal_route_features,
        formal_successor_contract,
        successors_from_formal_result,
        verification_outcome_from_formal_result,
    )
    from .pipeline import FormalRunRecord, formalize_and_verify

_LAZY = {
    "FormalSuccessorProposal": "integration",
    "formal_route_features": "integration",
    "formal_successor_contract": "integration",
    "successors_from_formal_result": "integration",
    "verification_outcome_from_formal_result": "integration",
    "FormalRunRecord": "pipeline",
    "formalize_and_verify": "pipeline",
}


def __getattr__(name: str) -> object:
    module_name = _LAZY.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module

    return getattr(import_module(f".{module_name}", __name__), name)


__all__ = [
    "FormalProofResult",
    "FormalProofTask",
    "FormalRunRecord",
    "FormalStatus",
    "FormalSuccessorProposal",
    "FormalTaskKind",
    "FormalizationAttempt",
    "FormalizationFailure",
    "LeanWorker",
    "MathCodeConfig",
    "MathCodeFormalizer",
    "formal_route_features",
    "formal_successor_contract",
    "formalize_and_verify",
    "successors_from_formal_result",
    "verification_outcome_from_formal_result",
]
