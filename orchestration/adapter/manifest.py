"""Inference blocks and receipts for run manifests.

`AGENTS.md` requires every run to retain the requested model policy, the
resolved runtime model identifier, the reasoning effort, and whether a fallback
was used. This module is the single writer of that block, so a manifest can
never disagree with what the resolver actually did.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import ADAPTER_VERSION, Config
from .resolver import Resolution
from .transport import Completion

POLICY_ENV = "AUTORESEARCH_POLICY"
BACKEND_ENV = "AUTORESEARCH_BACKEND"
FALLBACK_ENV = "AUTORESEARCH_FALLBACK_ALLOWED"
DEGRADED_ENV = "AUTORESEARCH_DEGRADED_ALLOWED"
INDEPENDENT_ENV = "AUTORESEARCH_INDEPENDENT_SESSION"


def inference_block(resolution: Resolution) -> dict[str, Any]:
    """The `run.inference` block for a manifest driven by a model."""
    return {
        "requested_policy": resolution.requested_policy,
        "canonical_policy": resolution.policy,
        "backend": resolution.backend,
        "provider": resolution.provider,
        "resolved_model_id": resolution.resolved_model_id,
        "model_provenance": resolution.model_provenance,
        "model_verified": resolution.verified_model,
        "requested_reasoning_effort": resolution.requested_reasoning_effort,
        "reasoning_effort": resolution.reasoning_effort,
        "fallback_used": resolution.fallback_used,
        "fallback_reason": resolution.fallback_reason,
        "degraded_requirements": list(resolution.degraded_requirements),
        "independent_session": resolution.independent_session,
        "adapter_version": resolution.adapter_version,
        "config_digest": resolution.config_digest,
    }


def deterministic_block(policy: str = "executor-implementation",
                        note: str = "deterministic harness execution — "
                                    "no model in the loop") -> dict[str, Any]:
    """For runs whose result comes from code, not from a model.

    Recorded explicitly rather than left blank: "no model was involved" is a
    reproducibility fact about the run, and it is what makes the run's numbers
    independent of any inference backend.
    """
    return {
        "requested_policy": policy,
        "canonical_policy": policy,
        "backend": None,
        "provider": None,
        "resolved_model_id": None,
        "model_provenance": "not-applicable",
        "model_verified": True,
        "requested_reasoning_effort": None,
        "reasoning_effort": None,
        "fallback_used": False,
        "fallback_reason": None,
        "degraded_requirements": [],
        "independent_session": False,
        "adapter_version": ADAPTER_VERSION,
        "config_digest": None,
        "note": note,
    }


def block_from_env(env: dict[str, str] | None = None) -> dict[str, Any]:
    """Build the manifest block from the environment the run was launched in.

    With no `AUTORESEARCH_POLICY` set the run is deterministic and says so. A
    resolution failure is recorded in the manifest rather than swallowed: an
    unresolvable policy is an evidence-integrity fact about that run.
    """
    env = dict(os.environ if env is None else env)
    policy = env.get(POLICY_ENV)
    if not policy:
        return deterministic_block()
    from . import config as config_module
    from . import resolver as resolve_module
    try:
        cfg = config_module.load()
        resolution = resolve_module.resolve(
            cfg, policy,
            backend=env.get(BACKEND_ENV) or None,
            fallback_allowed=_flag(env, FALLBACK_ENV),
            degraded_allowed=_flag(env, DEGRADED_ENV),
            # Never asserted on the run's behalf: independence is a fact about
            # how the session was launched, so the launcher has to state it.
            independent_session=_flag(env, INDEPENDENT_ENV),
            env=env)
        return inference_block(resolution)
    except Exception as exc:                      # recorded, never hidden
        block = deterministic_block(policy, note="policy resolution failed")
        block["resolution_error"] = f"{type(exc).__name__}: {exc}"
        block["model_verified"] = False
        return block


def _flag(env: dict[str, str], name: str) -> bool:
    return env.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def receipt(resolution: Resolution, completion: Completion | None = None, *,
            task_id: str | None = None, role: str | None = None,
            config: Config | None = None) -> dict[str, Any]:
    """A standalone inference receipt for a dispatched agent task."""
    data: dict[str, Any] = {
        "inference_receipt": {
            "task_id": task_id,
            "role": role,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "resolution": resolution.to_dict(),
        }
    }
    if config is not None:
        data["inference_receipt"]["config_paths"] = config.paths
    if completion is not None:
        data["inference_receipt"]["response"] = {
            "reported_model": completion.model,
            "stop_reason": completion.stop_reason,
            "usage": completion.usage,
            "latency_seconds": completion.latency_seconds,
            "output_characters": len(completion.text),
            "tool_calls": [call.name for call in completion.tool_calls],
            "model_matches_resolution": (
                completion.model == resolution.resolved_model_id
                if completion.model else None),
        }
    return data


def write_receipt(path: str | Path, data: dict[str, Any]) -> Path:
    """Write a receipt without overwriting: receipts are immutable records."""
    target = Path(path)
    if target.exists():
        raise FileExistsError(
            f"{target} already exists; inference receipts are immutable — "
            f"write a new receipt instead of overwriting")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n",
                      encoding="utf-8")
    return target
