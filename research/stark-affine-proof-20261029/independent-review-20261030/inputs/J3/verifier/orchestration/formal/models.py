"""Closed-ish dependency-free contracts for the formal research lane."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Mapping, Sequence


class FormalTaskKind(str, Enum):
    FORMALIZE_CLAIM = "formalize_claim"
    FIND_PROOF_GAP = "find_proof_gap"
    FORMAL_COUNTEREXAMPLE = "formal_counterexample"
    PROOF_GENERALIZATION = "proof_generalization"


class FormalStatus(str, Enum):
    MACHINE_VERIFIED = "machine_verified"
    FORMALIZATION_BLOCKED = "formalization_blocked"
    FORMALLY_REFUTED = "formally_refuted"
    INVALID = "invalid"


@dataclass(frozen=True)
class FormalProofTask:
    """One bounded formalization or proof-checking task.

    ``claim`` is the human research claim. ``theorem_name`` and
    ``theorem_file`` identify the Lean proposition intended to encode it.
    Semantic equivalence is *not* established by compilation and must be
    reviewed independently before the Coordinator promotes the result.
    """

    task_id: str
    kind: FormalTaskKind
    claim_id: str
    claim: str
    theorem_name: str
    theorem_file: str
    workspace: str = "formal"
    hypothesis_ids: Sequence[str] = field(default_factory=tuple)
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = {
            "task_id": self.task_id,
            "claim_id": self.claim_id,
            "claim": self.claim,
            "theorem_name": self.theorem_name,
            "theorem_file": self.theorem_file,
            "workspace": self.workspace,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing:
            raise ValueError(f"formal proof task missing required fields: {', '.join(missing)}")
        theorem = Path(self.theorem_file)
        if theorem.is_absolute() or ".." in theorem.parts:
            raise ValueError("theorem_file must stay inside the formal workspace")


@dataclass(frozen=True)
class FormalProofResult:
    task_id: str
    status: FormalStatus
    build_passed: bool
    axiom_audit_passed: bool
    forbidden_constructs: Sequence[str]
    theorem_file: str
    theorem_name: str
    build_log: str = ""
    audit_log: str = ""
    blocking_reason: str | None = None
    needs_semantic_review: bool = True

    @property
    def machine_verified(self) -> bool:
        return (
            self.status is FormalStatus.MACHINE_VERIFIED
            and self.build_passed
            and self.axiom_audit_passed
            and not self.forbidden_constructs
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "crypto.autoresearch.formal_proof_result.v1",
            "task_id": self.task_id,
            "status": self.status.value,
            "build_passed": self.build_passed,
            "axiom_audit_passed": self.axiom_audit_passed,
            "forbidden_constructs": list(self.forbidden_constructs),
            "theorem_file": self.theorem_file,
            "theorem_name": self.theorem_name,
            "blocking_reason": self.blocking_reason,
            "needs_semantic_review": self.needs_semantic_review,
        }
