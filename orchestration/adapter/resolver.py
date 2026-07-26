"""Strict policy resolution.

The rule from AGENTS.md is "never silently downgrade a requested policy". This
module is where that stops being prose:

  * an unknown policy, an unbound model, or an unmet requirement raises;
  * a substitution happens only when the caller passes the permission the
    handoff granted (`fallback_allowed`, `degraded_allowed`);
  * every substitution is carried in the returned record, so the run manifest
    shows what was asked for and what actually answered.
"""
from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from typing import Any

from .config import ADAPTER_VERSION, Config, ConfigError


class ResolutionError(RuntimeError):
    """The requested policy cannot be served under the granted permissions."""


class GovernanceError(ResolutionError):
    """A role-permission rule blocks this resolution, whatever the backend."""


@dataclass(frozen=True)
class Attempt:
    """One (policy, backend) pair the resolver considered, and why it failed."""
    policy: str
    backend: str
    reasons: list[str]


@dataclass(frozen=True)
class Resolution:
    """What answered, what was asked for, and every gap between the two."""
    requested_policy: str
    policy: str
    backend: str
    provider: str
    wire: str
    resolved_model_id: str
    model_provenance: str
    model_last_probed: str | None
    requested_reasoning_effort: str      # what was asked for (policy or override)
    reasoning_effort: str                # what is actually sent
    fallback_used: bool
    fallback_reason: str | None
    degraded_requirements: list[str]
    rejected_attempts: list[Attempt]
    may_change_official_state: bool
    independent_session_required: bool
    independent_session: bool
    base_url: str
    api_key_env: str
    policy_reasoning_effort: str = ""       # the policy default, before override
    reasoning_effort_overridden: bool = False
    reasoning_effort_capped: bool = False   # the backend could not go that deep
    request: dict[str, Any] = field(default_factory=dict)
    adapter_version: str = ADAPTER_VERSION
    config_digest: str = ""

    @property
    def verified_model(self) -> bool:
        return self.model_provenance == "runtime-verified" or bool(
            self.model_last_probed)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["rejected_attempts"] = [asdict(a) for a in self.rejected_attempts]
        data["verified_model"] = self.verified_model
        return data

    def summary(self) -> str:
        effort = f"effort={self.reasoning_effort}"
        if self.reasoning_effort_overridden:
            effort += f", overriding {self.policy_reasoning_effort}"
        if self.reasoning_effort_capped:
            effort += f", CAPPED from {self.requested_reasoning_effort}"
        line = (f"{self.requested_policy} -> {self.backend}:"
                f"{self.resolved_model_id} ({effort})")
        if self.fallback_used:
            line += f"  FALLBACK: {self.fallback_reason}"
        if self.degraded_requirements:
            line += f"  DEGRADED: {'; '.join(self.degraded_requirements)}"
        if not self.verified_model:
            line += "  [model id unverified — run `doctor --probe`]"
        return line


def _effort_rank(order: list[str], effort: str | None) -> int:
    try:
        return order.index(effort)  # type: ignore[arg-type]
    except ValueError:
        return -1


def _shortfalls(config: Config, policy: dict[str, Any],
                binding: dict[str, Any]) -> list[str]:
    """Requirements the binding does not meet, as human-readable reasons."""
    requires = policy.get("requires") or {}
    caps = binding.get("capabilities") or {}
    order = config.effort_order
    gaps: list[str] = []

    need = requires.get("reasoning_effort")
    ceiling = caps.get("max_reasoning_effort")
    if _effort_rank(order, ceiling) < _effort_rank(order, need):
        gaps.append(
            f"reasoning_effort: policy requires {need}, binding ceiling is "
            f"{ceiling}")

    for flag in ("tool_use", "structured_output"):
        if requires.get(flag) and not caps.get(flag):
            gaps.append(f"{flag}: required by policy, not declared by binding")

    for req_key, cap_key, label in (
            ("min_context_tokens", "context_tokens", "context window"),
            ("min_output_tokens", "max_output_tokens", "max output tokens")):
        need_n = requires.get(req_key)
        have_n = caps.get(cap_key)
        if need_n and (have_n is None or have_n < need_n):
            gaps.append(f"{label}: policy requires >= {need_n}, binding declares {have_n}")

    return gaps


def policy_effort(policy: dict[str, Any]) -> str:
    """What this policy asks the model to spend, defaulting to its floor."""
    requires = policy.get("requires") or {}
    return policy.get("reasoning_effort") or requires.get("reasoning_effort")


def _applied_effort(config: Config, policy: dict[str, Any],
                    binding: dict[str, Any], override: str | None = None) -> str:
    """The effort actually sent to the provider.

    Never above what was asked for, never above what the binding claims. The
    request and the capability floor are separate: a policy may deliberately
    ask for less thinking than the model can do (the Executor does), which is
    calibration, not a downgrade.
    """
    order = config.effort_order
    want = override or policy_effort(policy)
    ceiling = (binding.get("capabilities") or {}).get("max_reasoning_effort")
    if _effort_rank(order, ceiling) < 0:
        return want
    return min(want, ceiling, key=lambda e: _effort_rank(order, e))


def resolve(config: Config, requested_policy: str, *,
            backend: str | None = None,
            fallback_allowed: bool = False,
            degraded_allowed: bool = False,
            independent_session: bool = False,
            originating_agent: str | None = None,
            assigned_agent: str | None = None,
            reasoning_effort: str | None = None,
            env: dict[str, str] | None = None) -> Resolution:
    """Resolve a policy to a concrete model on a concrete backend.

    `fallback_allowed` permits substituting the policy's declared
    `fallback_policy` or another backend that fully meets the requirements.
    `degraded_allowed` additionally permits a binding that misses a
    requirement; the gap is recorded in `degraded_requirements` and must be
    covered by a coordinator-approved inference amendment.

    `reasoning_effort` overrides the policy default for this one task -- the
    per-task calibration knob. It is bounded by the binding ceiling and always
    recorded, so a task never runs at an effort its manifest does not state.
    """
    env = os.environ if env is None else env
    canonical = config.canonical_policy(requested_policy)
    policy = config.policy_table[canonical]

    if reasoning_effort is not None and reasoning_effort not in config.effort_order:
        raise ResolutionError(
            f"unknown reasoning effort {reasoning_effort!r}; lattice is "
            f"{config.effort_order}")

    # -- governance gates: independent of any backend ----------------------
    if policy.get("independent_session_required") and not independent_session:
        raise GovernanceError(
            f"policy {canonical} requires an independent session; the caller "
            f"did not assert one (pass --independent-session / "
            f"independent_session=True)")
    if (originating_agent and assigned_agent
            and originating_agent == assigned_agent
            and policy.get("independent_session_required")):
        raise GovernanceError(
            f"policy {canonical} forbids the originating agent "
            f"({originating_agent}) from reviewing its own claim")

    target_backend = backend or config.default_backend(env)
    config.backend(target_backend)  # validates the name

    # -- candidate order ---------------------------------------------------
    candidates: list[tuple[str, str]] = [(canonical, target_backend)]
    if fallback_allowed:
        declared = policy.get("fallback_policy")
        if declared:
            candidates.append((config.canonical_policy(declared), target_backend))
        for other in config.backend_fallback_order():
            if other != target_backend:
                candidates.append((canonical, other))

    rejected: list[Attempt] = []
    for index, (policy_id, backend_id) in enumerate(candidates):
        binding = config.binding(backend_id, policy_id)
        reasons = _binding_blockers(config, policy_id, backend_id, binding)
        if reasons:
            rejected.append(Attempt(policy_id, backend_id, reasons))
            continue
        return _build(config, requested_policy, canonical, policy_id, backend_id,
                      binding, fallback_used=index > 0,
                      fallback_reason=_fallback_reason(rejected) if index else None,
                      degraded=[], independent_session=independent_session,
                      rejected=rejected, env=env, override=reasoning_effort)

    # -- last resort: an explicitly permitted, recorded downgrade ----------
    if degraded_allowed and not policy.get("degradable", True):
        raise GovernanceError(
            f"policy {canonical} is not degradable: it may not run on a binding "
            f"that misses a stated requirement, whatever permission the handoff "
            f"grants. Use a backend that meets it, or do not make the claim.")
    if degraded_allowed:
        binding = config.binding(target_backend, canonical)
        hard = _hard_blockers(binding)
        if not hard:
            gaps = _shortfalls(config, policy, binding)
            return _build(config, requested_policy, canonical, canonical,
                          target_backend, binding, fallback_used=True,
                          fallback_reason="degraded resolution explicitly permitted",
                          degraded=gaps, independent_session=independent_session,
                          rejected=rejected, env=env, override=reasoning_effort)

    raise ResolutionError(
        f"cannot resolve policy {requested_policy!r} "
        f"(canonical {canonical}) on backend {target_backend!r}:\n"
        + "\n".join(f"  - {a.policy} @ {a.backend}: {'; '.join(a.reasons)}"
                    for a in rejected)
        + ("\n  fallback was not permitted by the handoff"
           if not fallback_allowed else "")
        + ("\n  a recorded downgrade is available with degraded_allowed=True "
           "(requires a coordinator inference amendment)"
           if not degraded_allowed else ""))


def _hard_blockers(binding: dict[str, Any] | None) -> list[str]:
    """Failures no permission can wave through: nothing to call."""
    if binding is None:
        return ["no binding configured"]
    if not binding.get("model"):
        return ["model is unbound (model: null) — set an identifier and probe it"]
    return []


def _binding_blockers(config: Config, policy_id: str, backend_id: str,
                      binding: dict[str, Any] | None) -> list[str]:
    hard = _hard_blockers(binding)
    if hard:
        return hard
    return _shortfalls(config, config.policy_table[policy_id], binding)


def _fallback_reason(rejected: list[Attempt]) -> str:
    first = rejected[0]
    return (f"{first.policy} @ {first.backend} unavailable: "
            f"{'; '.join(first.reasons)}")


def _build(config: Config, requested: str, canonical: str, policy_id: str,
           backend_id: str, binding: dict[str, Any], *, fallback_used: bool,
           fallback_reason: str | None, degraded: list[str],
           independent_session: bool, rejected: list[Attempt],
           env: dict[str, str], override: str | None = None) -> Resolution:
    policy = config.policy_table[policy_id]
    backend = config.backend(backend_id)
    canonical_policy = config.policy_table[canonical]
    requested_effort = override or policy_effort(canonical_policy)
    applied = _applied_effort(config, policy, binding, override)
    return Resolution(
        requested_policy=requested,
        policy=policy_id,
        backend=backend_id,
        provider=backend.get("display_name", backend_id),
        wire=backend["wire"],
        resolved_model_id=binding["model"],
        model_provenance=binding.get("provenance", "operator-supplied"),
        model_last_probed=binding.get("last_probed"),
        requested_reasoning_effort=requested_effort,
        reasoning_effort=applied,
        policy_reasoning_effort=policy_effort(canonical_policy),
        reasoning_effort_overridden=override is not None,
        reasoning_effort_capped=(applied != requested_effort),
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
        degraded_requirements=degraded,
        rejected_attempts=rejected,
        may_change_official_state=bool(policy.get("may_change_official_state")),
        independent_session_required=bool(policy.get("independent_session_required")),
        independent_session=independent_session,
        base_url=config.base_url(backend_id, env),
        api_key_env=backend["api_key_env"],
        request=dict(binding.get("request") or {}),
        config_digest=config.digest,
    )


def resolve_handoff(config: Config, handoff: dict[str, Any], **overrides: Any
                    ) -> Resolution:
    """Resolve straight from a `handoff:` record's `inference:` block.

    Keeps the ledger the single source of truth for what a task was permitted
    to run on, instead of re-deriving permissions at the call site.
    """
    body = handoff.get("handoff", handoff)
    inference = body.get("inference") or {}
    if not inference.get("policy"):
        raise ConfigError(
            f"handoff {body.get('id', '<unknown>')} has no inference.policy")
    kwargs: dict[str, Any] = {
        "fallback_allowed": bool(inference.get("fallback_allowed")),
        "degraded_allowed": bool(inference.get("degraded_allowed")),
        "independent_session": bool(inference.get("independent_session_required")),
        "originating_agent": body.get("from"),
        "assigned_agent": body.get("to"),
        # Per-task calibration, authored by the Coordinator in the handoff.
        "reasoning_effort": inference.get("reasoning_effort"),
    }
    kwargs.update(overrides)
    return resolve(config, inference["policy"], **kwargs)
