"""The operator-local bindings overlay: merged, validated, never attesting."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from orchestration import adapter
from orchestration.adapter import config as config_module
from orchestration.adapter import resolver as resolver_module

REPO = Path(__file__).resolve().parents[1]
EXAMPLE = REPO / "orchestration" / "model-bindings.local.example.yaml"


def _overlay(tmp_path: Path, doc: dict) -> Path:
    path = tmp_path / "overlay.yaml"
    path.write_text(yaml.safe_dump(doc), encoding="utf-8")
    return path


def _openrouter_entry(model: str = "vendor/model-x", **extra) -> dict:
    entry = {"model": model, "provenance": "operator-supplied",
             "capabilities": {"max_reasoning_effort": "high", "tool_use": True,
                              "structured_output": True, "context_tokens": 200000,
                              "max_output_tokens": 32000}}
    entry.update(extra)
    return entry


def test_without_an_overlay_openrouter_stays_unbound():
    cfg = adapter.load()
    assert "bindings_overlay" not in cfg.paths
    with pytest.raises(resolver_module.ResolutionError, match="unbound"):
        adapter.resolve(cfg, "executor-mechanical", backend="openrouter", env={})


def test_overlay_binds_an_unbound_backend_and_changes_the_digest(tmp_path):
    base = adapter.load()
    overlay = _overlay(tmp_path, {"bindings": {"openrouter": {
        "executor-mechanical": _openrouter_entry()}}})
    cfg = adapter.load(bindings_overlay=overlay)
    assert cfg.paths["bindings_overlay"] == str(overlay)
    assert cfg.digest != base.digest
    resolution = adapter.resolve(cfg, "executor-mechanical", backend="openrouter", env={})
    assert resolution.resolved_model_id == "vendor/model-x"
    assert resolution.model_provenance == "operator-supplied"
    assert resolution.verified_model is False
    # Only the named policy changed; the rest of openrouter is still unbound.
    with pytest.raises(resolver_module.ResolutionError, match="unbound"):
        adapter.resolve(cfg, "research-deep", backend="openrouter", env={})
    # The committed tables are untouched by the merge.
    assert cfg.binding("anthropic", "executor-mechanical") == \
        base.binding("anthropic", "executor-mechanical")


def test_overlay_entry_replaces_the_committed_entry_whole(tmp_path):
    base = adapter.load()
    committed = base.binding("anthropic", "executor-mechanical")
    assert committed["capabilities"]
    overlay = _overlay(tmp_path, {"bindings": {"anthropic": {
        "executor-mechanical": {"model": "claude-overlay-id",
                                "provenance": "operator-supplied",
                                "capabilities": {"max_reasoning_effort": "low",
                                                 "tool_use": True}}}}})
    cfg = adapter.load(bindings_overlay=overlay)
    merged = cfg.binding("anthropic", "executor-mechanical")
    assert merged["model"] == "claude-overlay-id"
    assert "context_tokens" not in merged["capabilities"]  # not half-merged
    assert merged["overlay_source"] == str(overlay)


def test_overlay_may_not_claim_runtime_verified_or_touch_defaults(tmp_path):
    verified = _overlay(tmp_path, {"bindings": {"openrouter": {
        "executor-mechanical": _openrouter_entry(provenance="runtime-verified")}}})
    with pytest.raises(config_module.ConfigError, match="runtime-verified"):
        adapter.load(bindings_overlay=verified)
    defaults = _overlay(tmp_path, {"defaults": {"backend_fallback_order": ["openrouter"]},
                                   "bindings": {}})
    with pytest.raises(config_module.ConfigError, match="only `bindings`"):
        adapter.load(bindings_overlay=defaults)


def test_overlay_is_validated_like_the_committed_file(tmp_path):
    bedrock = _overlay(tmp_path, {"bindings": {"openrouter": {
        "executor-mechanical": _openrouter_entry(model="amazon/bedrock-thing")}}})
    with pytest.raises(config_module.ConfigError, match="(?i)bedrock"):
        adapter.load(bindings_overlay=bedrock)
    unknown_backend = _overlay(tmp_path, {"bindings": {"nowhere": {
        "executor-mechanical": _openrouter_entry()}}})
    with pytest.raises(config_module.ConfigError, match="unknown backend"):
        adapter.load(bindings_overlay=unknown_backend)


def test_env_variable_selects_or_disables_the_overlay(tmp_path):
    overlay = _overlay(tmp_path, {"bindings": {}})
    assert config_module.overlay_path({config_module.BINDINGS_OVERLAY_ENV: str(overlay)}) == overlay
    assert config_module.overlay_path({config_module.BINDINGS_OVERLAY_ENV: ""}) is None
    cfg = adapter.load(env={config_module.BINDINGS_OVERLAY_ENV: str(overlay)})
    assert cfg.paths["bindings_overlay"] == str(overlay)


def test_the_example_overlay_loads_and_leaves_breakthrough_unbound():
    cfg = adapter.load(bindings_overlay=EXAMPLE)
    for policy in ("coordinator-orchestration-code", "research-deep",
                   "executor-mechanical"):
        resolution = adapter.resolve(cfg, policy, backend="openrouter", env={})
        assert resolution.resolved_model_id.startswith("REPLACE-WITH")
        assert resolution.model_provenance == "operator-supplied"
    with pytest.raises(resolver_module.ResolutionError, match="unbound"):
        adapter.resolve(cfg, "review-breakthrough", backend="openrouter", env={},
                        independent_session=True)
