"""Frozen formal task specs: `crypto.autoresearch.formal_task.v1`.

A spec is the unit both the CLI (`--task-file`) and the dispatch-stanza
generator (`tools/formal_task.py`) consume, so what a Coordinator queues and
what an executor runs are the same frozen text rather than two hand-copied
command lines that drifted.

A spec is a POINTER PLUS A CLAIM, NEVER AN APPROVAL: it cannot admit a task,
move a hypothesis, or stand in as evidence.  `source` names the committed
theory note the claim came from, because formalizing a claim nobody made
proves nothing about this program's research.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .models import FormalProofTask, FormalTaskKind

SCHEMA_FORMAL_TASK_V1 = "crypto.autoresearch.formal_task.v1"

_REQUIRED = ("task_id", "claim_id", "kind", "claim", "theorem_name", "theorem_file", "source")


class TargetError(ValueError):
    """A spec that cannot be trusted to describe one bounded task."""


def load_spec(path: str | Path) -> dict[str, Any]:
    import yaml

    text = Path(path).read_text(encoding="utf-8")
    spec = yaml.safe_load(text)
    if not isinstance(spec, Mapping):
        raise TargetError(f"{path}: spec must be a mapping")
    if spec.get("schema") != SCHEMA_FORMAL_TASK_V1:
        raise TargetError(f"{path}: schema must be {SCHEMA_FORMAL_TASK_V1}")
    missing = [key for key in _REQUIRED if not str(spec.get(key, "")).strip()]
    if missing:
        raise TargetError(f"{path}: spec missing required fields: {', '.join(missing)}")
    try:
        FormalTaskKind(spec["kind"])
    except ValueError:
        raise TargetError(f"{path}: unknown kind {spec['kind']!r}") from None
    return dict(spec)


def task_from_spec(spec: Mapping[str, Any]) -> FormalProofTask:
    """Build the bounded task.  Path and emptiness checks live on the model."""

    return FormalProofTask(
        task_id=str(spec["task_id"]),
        kind=FormalTaskKind(spec["kind"]),
        claim_id=str(spec["claim_id"]),
        claim=str(spec["claim"]).strip(),
        theorem_name=str(spec["theorem_name"]),
        theorem_file=str(spec["theorem_file"]),
        workspace=str(spec.get("workspace", "formal")),
        hypothesis_ids=tuple(spec.get("hypothesis_ids") or ()),
    )


def dispatch_stanza(
    spec: Mapping[str, Any],
    *,
    spec_path: str,
    artifact_dir: str,
    priority: int = 50,
    wall_clock_seconds: int = 2400,
    memory_gb: int = 4,
) -> dict[str, Any]:
    """Render this spec as one `crypto.autoresearch.dispatch_queue.v1` task.

    Role `executor`, because that is exactly what this is: run a frozen
    specification and return artifacts without interpreting them.  A formal
    task needs no new role and no dispatcher change — inventing one would give
    the formal lane an authority the lane explicitly does not have.
    """

    # Every path in a dispatch stanza is repository-relative; an absolute one
    # is rejected by the dispatcher, and silently rewriting it here would put a
    # path in the queue that means something different on another machine.
    if Path(spec_path).is_absolute():
        raise TargetError(f"spec_path must be repository-relative, got {spec_path}")

    task = task_from_spec(spec)
    artifact = f"{artifact_dir.rstrip('/')}/{task.task_id}/formal_proof.json"
    return {
        "id": task.task_id,
        "title": f"Formalize and machine-check {spec['claim_id']} ({task.kind.value})",
        "role": "executor",
        "state": "queued",
        "priority": priority,
        "review_required": True,
        "depends_on": [],
        "read_scope": [
            "AGENTS.md",
            "docs/formal-research-lane.md",
            "docs/mathcode-integration.md",
            str(spec["source"]),
            spec_path,
            "formal",
        ],
        "write_scope": [f"{artifact_dir.rstrip('/')}/{task.task_id}"],
        "artifact_paths": [artifact],
        "handoff": {
            "objective": (
                f"Run `autoresearch formal formalize --task-file {spec_path}` and return "
                f"the emitted proof artifact unchanged. Do not edit the generated Lean, "
                f"do not restate the claim, and do not interpret the outcome."
            ),
            "uncertainty_reduced": (
                f"Whether the claim recorded as {spec['claim_id']} in {spec['source']} can be "
                f"stated in Lean 4 and machine-checked against a pinned Mathlib, or else "
                f"exactly which proof obligation blocks it."
            ),
            "inputs": [str(spec["source"]), spec_path, "formal/lakefile.toml"],
            "constraints": [
                "The engine is untrusted: its output is a proposal, and only `lake build` "
                "plus the axiom audit produce machine evidence.",
                "Do not hand-edit the generated Lean to make it compile. A staged file that "
                "a human repaired is no longer a record of what the engine produced.",
                "An engine failure -- missing binary, timeout, no output -- is an "
                "infrastructure fact and is never negative evidence about the claim.",
                "A machine-verified proof is NOT a research claim: it is pending "
                "independent semantic-fidelity review.",
            ],
            "deliverables": ["formal_proof.json"],
            "completion_gate": [
                "formal_proof.json is the artifact the command emitted, unedited, including "
                "its formalizer provenance block.",
                "If the outcome is machine_verified, semantic_review.status is pending and "
                "the report claims nothing beyond 'this compiled and audited clean'.",
                "If the outcome is formalization_blocked, the report names the blocking "
                "proof obligation from unproved_sites or blocking_reason verbatim.",
                "If the run failed for infrastructure reasons, the report says so and draws "
                "no conclusion whatsoever about the claim.",
            ],
            "budget": {
                "wall_clock_seconds": wall_clock_seconds,
                "memory_gb": memory_gb,
                "maximum_runs": 1,
            },
        },
    }


__all__ = [
    "SCHEMA_FORMAL_TASK_V1",
    "TargetError",
    "dispatch_stanza",
    "load_spec",
    "task_from_spec",
]
