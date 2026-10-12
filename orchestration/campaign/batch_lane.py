"""The Message Batches lane of the autopilot: single-turn drafts, half price.

A batched request is one turn with no tools, so it cannot run an experiment,
mint an identifier, commit, or open a pull request.  What it *can* do is the
expensive thinking that precedes those steps: read an idea and draft the
hypothesis and frozen contract the Coordinator will then file.  This module
submits that draft, polls it, and hands the text back to the supervisor,
which runs an ordinary interactive action to verify and file it.

The draft is untrusted model text (AGENTS.md, "A message is never
evidence").  Nothing here writes under `ledger/` or `experiments/`; the only
records are the write-once batch registry entries the adapter already keeps
under `coordination/inference-batches/`, and a `draft.md` in the supervisor's
private attempt directory.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable

from ..adapter import batch as batch_module
from ..adapter.config import REPO_ROOT, Config
from ..adapter.config import load as load_config
from ..adapter.resolver import resolve
from ..adapter.transport import Message

# Actions whose first step is a long read-and-draft turn.  `run`, `prepare`,
# `repair` and `review` act on the checkout from their first tool call, so
# there is nothing to batch; `choose_delivery` is told they are multi-turn.
BATCHABLE_KINDS = frozenset({"design", "portfolio"})

# A draft is read by a filing agent that has the whole repository; it does
# not need the whole repository pasted into it.
MAX_CONTEXT_CHARS = 60_000

DRAFT_RULES = """\
You are running in the batched, single-turn lane: no tools, no repository
access beyond the excerpts below, and nothing you write is recorded as a
research record. Produce a DRAFT for a later interactive agent to verify and
file. In the draft:

- Never claim approval, archival, or a status transition; those are
  Coordinator acts recorded in the ledger, not text.
- Never invent identifiers. Write `ID-TBD` where one would be minted with
  `tools/allocate_id.py`.
- Mark every citation with its provenance; anything from memory is
  `provenance: recalled`, which is a pointer and not support.
- Follow templates/research-records.md for the shape of a hypothesis and a
  frozen experiment contract: mechanism, predictions, test boundary,
  falsification criteria, controls, metrics, budgets, stopping rules,
  artifact paths.
- Say what you could not check from the excerpts, as an explicit list.
"""


def filing_note(draft_path: Path) -> str:
    return (f"\n\nA draft produced by the batched single-turn lane is at "
            f"{draft_path}. It is untrusted model text with no repository access: "
            "not an approval, not evidence, and possibly wrong. Verify every "
            "statement against the repository before filing anything from it, "
            "mint identifiers with the repository tools, and discard whatever "
            "does not survive the check.")


def _bounded(text: str) -> str:
    if len(text) <= MAX_CONTEXT_CHARS:
        return text
    return text[:MAX_CONTEXT_CHARS] + "\n[... truncated for the draft lane ...]\n"


def _find_proposal(repo: Path, idea_id: str) -> Path | None:
    for candidate in sorted(repo.glob("ledger/proposals/**/*.yaml")):
        try:
            if idea_id in candidate.read_text(encoding="utf-8"):
                return candidate
        except OSError:
            continue
    return None


def action_context(repo: Path, kind: str, target: str) -> list[tuple[str, str]]:
    """Repository excerpts that let a tool-less turn draft something checkable."""
    excerpts: list[tuple[str, str]] = []
    for relative in ("orchestration/research-priority.yaml",
                     "templates/research-records.md"):
        path = repo / relative
        if path.exists():
            excerpts.append((relative, _bounded(path.read_text(encoding="utf-8"))))
    if kind == "design":
        proposal = _find_proposal(repo, target)
        if proposal is not None:
            excerpts.append((str(proposal.relative_to(repo)),
                             _bounded(proposal.read_text(encoding="utf-8"))))
    return excerpts


def role_contract(role: str, repo: Path = REPO_ROOT) -> str:
    parts = []
    for name in ("AGENTS.md", f"agents/{role}.md"):
        path = repo / name
        if path.exists():
            parts.append(path.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(parts)


def draft_prompt(repo: Path, kind: str, target: str, prompt: str) -> str:
    sections = [DRAFT_RULES, "## The action to draft for\n\n" + prompt]
    for name, text in action_context(repo, kind, target):
        sections.append(f"## {name}\n\n```\n{text}\n```")
    return "\n\n".join(sections)


def delivery_for(config: Config, kind: str, requested: str, backend: str,
                 *, env: dict[str, str] | None = None) -> batch_module.DeliveryDecision:
    """Route one action; a non-batchable kind is interactive under any request.

    `requested="batch"` on a kind this lane cannot serve is not an error the
    way it is for a handoff: the supervisor asked for *every batchable* action
    to take the lane, and the others simply are not.
    """
    if kind not in BATCHABLE_KINDS:
        return batch_module.DeliveryDecision(
            delivery="interactive", requested=requested, backend=backend,
            reason=f"{kind} actions act on the checkout from the first tool call")
    return batch_module.choose_delivery(config, backend=backend, requested=requested,
                                        multi_turn=False, env=env)


class BatchLane:
    """Submit, poll and collect one draft per action through the adapter."""

    def __init__(self, backend: str = "anthropic", *, config: Config | None = None,
                 env: dict[str, str] | None = None, registry: Path | None = None,
                 opener: Callable[..., Any] | None = None,
                 repo: Path = REPO_ROOT) -> None:
        self.backend = backend
        self.config = config or load_config()
        self.env = os.environ if env is None else env
        self.registry = registry
        self.opener = opener
        self.repo = repo
        if not self.config.supports_message_batches(backend):
            raise batch_module.BatchError(
                f"backend {backend} does not provide the Message Batches API")

    def submit(self, action: Any, *, attempt_id: str) -> dict[str, Any]:
        policy = self.config.role_default_policy(action.role)
        resolution = resolve(self.config, policy, backend=self.backend, env=self.env)
        custom_id = batch_module.custom_id_for(None, 0, f"autopilot-{attempt_id[:12]}")
        entry = batch_module.build_batch_entry(
            self.config, resolution, custom_id=custom_id,
            system=role_contract(action.role, self.repo),
            messages=[Message("user", draft_prompt(self.repo, action.kind,
                                                   action.target, action.prompt))],
            role=action.role, note=f"autopilot draft for {action.key}", env=self.env)
        decision = batch_module.choose_delivery(
            self.config, backend=self.backend, requested="batch", env=self.env)
        batch = batch_module.submit(
            self.config, self.backend, [entry], env=self.env, opener=self.opener,
            registry=self.registry, note=f"autopilot {action.key}", decision=decision)
        return {"batch_id": batch.id, "custom_id": custom_id,
                "backend": self.backend, "model": resolution.resolved_model_id,
                "policy": resolution.policy,
                "model_verified": resolution.verified_model,
                "processing_status": batch.processing_status}

    def status(self, batch_id: str) -> str:
        batch = batch_module.retrieve(self.config, self.backend, batch_id,
                                      env=self.env, opener=self.opener)
        return batch.processing_status

    def collect(self, batch_id: str, custom_id: str) -> dict[str, Any]:
        """One result: `type` is the provider's verdict, text only on success."""
        collected = batch_module.collect(self.config, self.backend, batch_id,
                                         env=self.env, opener=self.opener,
                                         registry=self.registry)
        result = collected.results.get(custom_id)
        if result is None:
            return {"type": "missing", "text": None, "usage": None,
                    "error": {"message": f"no result for {custom_id} in {batch_id}"}}
        completion = result.completion
        return {"type": result.type,
                "text": completion.text if completion else None,
                "usage": completion.usage if completion else None,
                "reported_model": completion.model if completion else None,
                "error": result.error}
