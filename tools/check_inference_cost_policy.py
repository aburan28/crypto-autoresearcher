#!/usr/bin/env python3
"""Offline guard for the repository's no-Bedrock cost policy."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from orchestration import adapter  # noqa: E402

OPENCODE_CONFIG = REPO / "opencode.json"
FORBIDDEN = "bedrock"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def _scalar_values(value: object, label: str):
    """Yield every scalar in a provider declaration with its configuration path."""
    if isinstance(value, dict):
        for key, child in value.items():
            child_label = f"{label}.{key}"
            yield child_label, key
            yield from _scalar_values(child, child_label)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _scalar_values(child, f"{label}[{index}]")
    else:
        yield label, value


def _assert_allowed(config: adapter.Config, label: str, value: object) -> None:
    try:
        config.assert_inference_target_allowed(value, context=label)
    except adapter.ConfigError as exc:
        fail(str(exc))


def check_opencode(config: adapter.Config, opencode: dict[str, object]) -> None:
    """Reject every OpenCode selector, including nested provider settings.

    ``disabled_providers: [amazon-bedrock]`` is the intentional denial-list
    sentinel and is checked separately.  Every provider declaration itself is
    executable routing configuration, so both keys and nested scalar values
    must be free of the forbidden token.
    """
    disabled = [str(value).casefold()
                for value in opencode.get("disabled_providers", [])]
    if "amazon-bedrock" not in disabled:
        fail("opencode.json must disable provider 'amazon-bedrock'")

    targets: list[tuple[str, object]] = [
        ("model", opencode.get("model")),
        ("small_model", opencode.get("small_model")),
    ]
    agents = opencode.get("agent") or {}
    if not isinstance(agents, dict):
        fail("opencode.json agent must be a mapping")
    targets.extend(
        (f"agent.{name}.model", body.get("model"))
        for name, body in agents.items()
        if isinstance(body, dict)
    )
    providers = opencode.get("provider") or {}
    if not isinstance(providers, dict):
        fail("opencode.json provider must be a mapping")
    targets.extend(
        (f"provider.{name}", name)
        for name in providers
    )
    for label, value in targets:
        _assert_allowed(config, label, value)

    for label, value in _scalar_values(providers, "provider"):
        _assert_allowed(config, label, value)


def main() -> None:
    config = adapter.load()
    tokens = config.forbidden_provider_substrings
    if FORBIDDEN not in tokens:
        fail("orchestration/providers.yaml must forbid the token 'bedrock'")

    try:
        opencode = json.loads(OPENCODE_CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {OPENCODE_CONFIG.relative_to(REPO)}: {exc}")

    if not isinstance(opencode, dict):
        fail("opencode.json must contain a JSON object")
    check_opencode(config, opencode)

    print("OK: Bedrock is disabled before inference in adapter and OpenCode config")


if __name__ == "__main__":
    main()
