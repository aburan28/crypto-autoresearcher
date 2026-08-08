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


def main() -> None:
    config = adapter.load()
    tokens = config.forbidden_provider_substrings
    if FORBIDDEN not in tokens:
        fail("orchestration/providers.yaml must forbid the token 'bedrock'")

    try:
        opencode = json.loads(OPENCODE_CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {OPENCODE_CONFIG.relative_to(REPO)}: {exc}")

    disabled = [str(value).casefold()
                for value in opencode.get("disabled_providers", [])]
    if "amazon-bedrock" not in disabled:
        fail("opencode.json must disable provider 'amazon-bedrock'")

    targets: list[tuple[str, object]] = [
        ("model", opencode.get("model")),
        ("small_model", opencode.get("small_model")),
    ]
    targets.extend(
        (f"agent.{name}.model", body.get("model"))
        for name, body in (opencode.get("agent") or {}).items()
        if isinstance(body, dict)
    )
    targets.extend(
        (f"provider.{name}", name)
        for name in (opencode.get("provider") or {})
    )
    for label, value in targets:
        if value is not None and FORBIDDEN in str(value).casefold():
            fail(f"{label} selects forbidden inference target {value!r}")

    print("OK: Bedrock is disabled before inference in adapter and OpenCode config")


if __name__ == "__main__":
    main()
