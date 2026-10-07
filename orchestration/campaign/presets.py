"""Named provider set-ups for `autoresearch campaign autopilot --preset`.

A preset is a (runtime, backends, delivery) triple and nothing more: it never
names a model.  Models come from `model-bindings.yaml` or the operator overlay
(`model-bindings.local.yaml`, or `--model` for one run), so a preset for an
unbound backend such as `openrouter` is runnable only once the operator has
bound it -- the CLI says so rather than guessing an id.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ..adapter import config as config_module


@dataclass(frozen=True)
class Preset:
    name: str
    runtime: str
    backends: tuple[str, ...]
    delivery: str = "interactive"
    batch_backend: str = "anthropic"
    about: str = ""
    needs: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "runtime": self.runtime, "backends": list(self.backends),
                "delivery": self.delivery, "batch_backend": self.batch_backend,
                "about": self.about, "needs": list(self.needs)}


_OVERLAY = ("a model id for this backend in orchestration/model-bindings.local.yaml "
            "or --model/--model-caps",)

PRESETS: dict[str, Preset] = {p.name: p for p in (
    Preset("anthropic", "claude_code", ("anthropic",),
           about="Claude Code against the Anthropic API; interactive only.",
           needs=("ANTHROPIC_API_KEY or a Claude Code login", "the `claude` CLI")),
    Preset("anthropic-batch", "claude_code", ("anthropic",), delivery="auto",
           about="Claude Code for tool-using actions; design/portfolio drafts go "
                 "through the Message Batches API first and are filed with the "
                 "draft attached.",
           needs=("ANTHROPIC_API_KEY", "the `claude` CLI")),
    Preset("anthropic-opencode", "opencode", ("anthropic",),
           about="OpenCode's native Anthropic provider.",
           needs=("ANTHROPIC_API_KEY", "the `opencode` CLI")),
    Preset("openrouter", "opencode", ("openrouter",),
           about="OpenCode through OpenRouter. The repository ships this backend "
                 "unbound; bind a model first.",
           needs=("OPENROUTER_API_KEY", "the `opencode` CLI") + _OVERLAY),
    Preset("openrouter-batch", "opencode", ("openrouter",), delivery="auto",
           about="OpenRouter for tool-using actions, Anthropic Message Batches "
                 "for the drafts.",
           needs=("OPENROUTER_API_KEY", "ANTHROPIC_API_KEY", "the `opencode` CLI")
           + _OVERLAY),
    Preset("openrouter-codex", "codex_cli", ("openrouter",),
           about="Codex CLI pointed at OpenRouter's OpenAI-compatible endpoint.",
           needs=("OPENROUTER_API_KEY", "the `codex` CLI") + _OVERLAY),
    Preset("abliterated", "opencode", ("abliteration",),
           about="OpenCode against Abliteration.ai (OpenAI-compatible).",
           needs=("ABLIT_API_KEY", "the `opencode` CLI")),
    Preset("abliterated-claude", "claude_code", ("abliteration-anthropic",),
           about="Claude Code against Abliteration.ai's Anthropic-compatible endpoint.",
           needs=("ABLIT_API_KEY", "the `claude` CLI")),
    Preset("abliterated-codex", "codex_cli", ("abliteration",),
           about="Codex CLI against Abliteration.ai.",
           needs=("ABLIT_API_KEY", "the `codex` CLI")),
    Preset("local", "opencode", ("local",),
           about="OpenCode against the local OpenAI-compatible server "
                 "(opencode.json provider `vllm`; LOCAL_LLM_BASE_URL for the adapter).",
           needs=("a server at LOCAL_LLM_BASE_URL", "the `opencode` CLI")),
    Preset("local-codex", "codex_cli", ("local",),
           about="Codex CLI against the local OpenAI-compatible server.",
           needs=("a server at LOCAL_LLM_BASE_URL", "the `codex` CLI")),
    Preset("zai", "opencode", ("zai",), about="OpenCode against Z.ai GLM.",
           needs=("ZAI_API_KEY", "the `opencode` CLI")),
    Preset("zai-claude", "claude_code", ("zai-anthropic",),
           about="Claude Code against Z.ai's Anthropic-compatible endpoint.",
           needs=("ZAI_API_KEY", "the `claude` CLI")),
    Preset("fireworks", "opencode", ("fireworks",), about="OpenCode against Fireworks.",
           needs=("FIREWORKS_API_KEY", "the `opencode` CLI")),
    Preset("fireworks-claude", "claude_code", ("fireworks-anthropic",),
           about="Claude Code against Fireworks' Anthropic-compatible endpoint.",
           needs=("FIREWORKS_API_KEY", "the `claude` CLI")),
    Preset("openai", "opencode", ("openai",), about="OpenCode against OpenAI.",
           needs=("OPENAI_API_KEY", "the `opencode` CLI")),
    Preset("codex", "codex_cli", ("openai",), about="Codex CLI against OpenAI.",
           needs=("OPENAI_API_KEY", "the `codex` CLI")),
    Preset("failover", "opencode", ("local", "zai", "fireworks", "openai", "anthropic"),
           about="The historical default: OpenCode with failover across every "
                 "bound backend, cheapest first.",
           needs=("the `opencode` CLI", "a key for each backend that should take part")),
)}

DEFAULT_PRESET = "failover"


def get(name: str) -> Preset:
    try:
        return PRESETS[name]
    except KeyError:
        raise KeyError(f"unknown preset {name!r}; one of {', '.join(sorted(PRESETS))}") from None


def describe() -> list[dict[str, Any]]:
    return [PRESETS[name].as_dict() for name in sorted(PRESETS)]


# --------------------------------------------------------------------------
# --model: a one-run operator binding
# --------------------------------------------------------------------------
CAP_KEYS = {"effort": "max_reasoning_effort", "context": "context_tokens",
            "output": "max_output_tokens"}


def parse_caps(text: str) -> dict[str, Any]:
    """`effort=high,context=200000,output=32000` -> a capabilities block.

    All three are required: they are the operator's assertion about the model,
    checked against the policy floors, and a missing one would otherwise be
    read as "unknown", which the resolver treats as a shortfall.
    """
    caps: dict[str, Any] = {}
    for item in filter(None, (part.strip() for part in text.split(","))):
        if "=" not in item:
            raise ValueError(f"--model-caps item {item!r} is not key=value")
        key, value = (s.strip() for s in item.split("=", 1))
        if key not in CAP_KEYS:
            raise ValueError(f"--model-caps key {key!r}; one of {', '.join(CAP_KEYS)}")
        if key == "effort":
            caps[CAP_KEYS[key]] = value
        else:
            if not value.isdigit() or int(value) <= 0:
                raise ValueError(f"--model-caps {key} must be a positive integer")
            caps[CAP_KEYS[key]] = int(value)
    missing = [k for k in CAP_KEYS if CAP_KEYS[k] not in caps]
    if missing:
        raise ValueError(f"--model-caps must declare {', '.join(missing)}")
    caps["tool_use"] = True
    caps["structured_output"] = True
    return caps


def write_model_overlay(path: Path, *, backends: list[str], model: str,
                        caps: dict[str, Any], env: dict[str, str] | None = None
                        ) -> Path:
    """Bind `model` to every policy its declared caps can serve, on `backends`.

    Layered over the operator's standing overlay, if any, so `--model` adds a
    binding for this run instead of discarding the others.  Provenance is
    `operator-supplied`: the id was typed, not probed.
    """
    import os
    env = os.environ if env is None else env
    base_cfg = config_module.load(env={**env, config_module.BINDINGS_OVERLAY_ENV: ""})
    standing = config_module.overlay_path(env)
    merged: dict[str, Any] = {"schema_version": "2.0",
                              "notes": f"--model {model} for one autopilot run",
                              "bindings": {}}
    if standing is not None and Path(standing).exists():
        loaded = yaml.safe_load(Path(standing).read_text(encoding="utf-8")) or {}
        merged["bindings"] = dict(loaded.get("bindings") or {})
    order = base_cfg.effort_order
    ceiling = order.index(caps["max_reasoning_effort"]) \
        if caps["max_reasoning_effort"] in order else -1
    if ceiling < 0:
        raise ValueError(f"--model-caps effort must be one of {', '.join(order)}")
    for backend in backends:
        base_cfg.backend(backend)  # unknown or forbidden names fail here
        table: dict[str, Any] = {}
        for policy_id, policy in base_cfg.policy_table.items():
            requires = policy.get("requires") or {}
            need = requires.get("reasoning_effort")
            if need in order and order.index(need) > ceiling:
                table[policy_id] = {"model": None, "provenance": "unbound"}
                continue
            table[policy_id] = {
                "model": model, "provenance": "operator-supplied", "last_probed": None,
                "capabilities": dict(caps),
                # No reasoning knobs: which parameter a model takes (adaptive
                # effort, a thinking budget, `reasoning_effort`) is not
                # something a command line should guess. The standing overlay
                # file is where an operator states it.
                "request": {"max_tokens": min(16000, caps["max_output_tokens"])}}
        merged["bindings"][backend] = table
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(merged, sort_keys=False), encoding="utf-8")
    return path
