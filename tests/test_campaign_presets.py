"""Presets name a runtime and backends, never a model; --model is a declared binding."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml

from orchestration import adapter
from orchestration.adapter import config as config_module
from orchestration.campaign import cli as campaign_cli
from orchestration.campaign import presets, workers


@pytest.fixture(scope="module")
def cfg():
    return adapter.load()


def test_every_preset_is_runtime_compatible_and_names_no_model(cfg) -> None:
    for preset in presets.PRESETS.values():
        workers.check_compatibility(cfg, preset.runtime, list(preset.backends))
        assert preset.delivery in ("interactive", "batch", "auto")
        assert cfg.supports_message_batches(preset.batch_backend)
        assert "model" not in preset.as_dict()
    assert presets.get(presets.DEFAULT_PRESET).backends[0] == "local"
    with pytest.raises(KeyError):
        presets.get("bedrock")


def test_parse_caps_requires_all_three_figures() -> None:
    caps = presets.parse_caps("effort=high, context=200000,output=32000")
    assert caps == {"max_reasoning_effort": "high", "context_tokens": 200000,
                    "max_output_tokens": 32000, "tool_use": True, "structured_output": True}
    for bad in ("effort=high", "effort=high,context=x,output=1", "effort=high,context=1",
                "speed=fast,context=1,output=1", "effort"):
        with pytest.raises(ValueError):
            presets.parse_caps(bad)


def test_model_overlay_binds_what_the_caps_can_serve(tmp_path: Path, cfg) -> None:
    env = {config_module.BINDINGS_OVERLAY_ENV: ""}
    path = presets.write_model_overlay(
        tmp_path / "overlay.yaml", backends=["openrouter"], model="vendor/m",
        caps=presets.parse_caps("effort=high,context=200000,output=32000"), env=env)
    merged = config_module.load(bindings_overlay=path, env=env)
    bound = adapter.resolve(merged, "coordinator-orchestration-code", backend="openrouter")
    assert bound.resolved_model_id == "vendor/m"
    assert bound.model_provenance == "operator-supplied" and bound.verified_model is False
    # `max` effort is above the declared ceiling, so the breakthrough tier stays unbound.
    with pytest.raises(adapter.ResolutionError):
        adapter.resolve(merged, "review-breakthrough", backend="openrouter",
                        independent_session=True)
    doc = yaml.safe_load(path.read_text())
    assert doc["bindings"]["openrouter"]["review-breakthrough"] == {
        "model": None, "provenance": "unbound"}
    assert "reasoning" not in doc["bindings"]["openrouter"]["research-deep"]["request"]

    # Layered over a standing overlay rather than replacing it.
    standing = tmp_path / "standing.yaml"
    standing.write_text(yaml.safe_dump({"schema_version": "2.0", "bindings": {
        "local": {"executor-mechanical": {"model": "ollama-thing",
                                          "provenance": "operator-supplied"}}}}))
    layered = presets.write_model_overlay(
        tmp_path / "layered.yaml", backends=["openrouter"], model="vendor/m",
        caps=presets.parse_caps("effort=max,context=200000,output=32000"),
        env={config_module.BINDINGS_OVERLAY_ENV: str(standing)})
    doc = yaml.safe_load(layered.read_text())
    assert doc["bindings"]["local"]["executor-mechanical"]["model"] == "ollama-thing"
    assert doc["bindings"]["openrouter"]["review-breakthrough"]["model"] == "vendor/m"
    with pytest.raises(ValueError):
        presets.write_model_overlay(tmp_path / "x.yaml", backends=["openrouter"],
                                    model="m", env=env,
                                    caps={**presets.parse_caps(
                                        "effort=high,context=1,output=1"),
                                        "max_reasoning_effort": "turbo"})
    with pytest.raises(Exception):
        presets.write_model_overlay(tmp_path / "y.yaml", backends=["bedrock"], model="m",
                                    caps=presets.parse_caps(
                                        "effort=high,context=1,output=1"), env=env)


def _run(capsys, *argv: str) -> tuple[int, str, str]:
    code = campaign_cli.main(["autopilot", *argv])
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_cli_lists_presets_and_refuses_mismatches(tmp_path: Path, capsys, monkeypatch) -> None:
    monkeypatch.setenv(config_module.BINDINGS_OVERLAY_ENV, "")
    code, out, _ = _run(capsys, "--list-presets")
    assert code == 0
    listed = json.loads(out)
    assert listed["default"] == "failover"
    assert {p["name"] for p in listed["presets"]} >= {
        "anthropic-batch", "openrouter", "abliterated", "abliterated-claude", "local"}

    code, _, err = _run(capsys, "--preset", "nope", "--dry-run")
    assert code == 2 and "unknown preset" in err

    code, _, err = _run(capsys, "--runtime", "claude_code", "--backend", "openrouter",
                        "--repo", str(tmp_path), "--dry-run")
    assert code == 2 and "cannot use backend" in err

    code, _, err = _run(capsys, "--preset", "openrouter", "--model", "v/m",
                        "--repo", str(tmp_path), "--dry-run")
    assert code == 2 and "--model-caps" in err


def test_cli_dry_run_reports_the_plan_without_a_binary(tmp_path: Path, capsys, monkeypatch) -> None:
    monkeypatch.setenv(config_module.BINDINGS_OVERLAY_ENV, "")
    (tmp_path / "orchestration").mkdir()
    (tmp_path / "orchestration/research-priority.yaml").write_text("ecc_areas: [ICEX]\n")
    code, out, _ = _run(capsys, "--preset", "anthropic-batch", "--repo", str(tmp_path),
                        "--state-dir", str(tmp_path / "state"), "--dry-run")
    assert code == 0
    report = json.loads(out)
    assert report["model_calls"] == 0 and report["advisory_only"] is True
    plan = report["plan"]
    assert (plan["runtime"], plan["backends"], plan["delivery"]) == (
        "claude_code", ["anthropic"], "auto")
    assert plan["coordinator_candidates"][0]["backend"] == "anthropic"

    code, out, _ = _run(capsys, "--preset", "openrouter", "--model", "vendor/m",
                        "--model-caps", "effort=high,context=200000,output=32000",
                        "--repo", str(tmp_path), "--state-dir", str(tmp_path / "state"),
                        "--dry-run")
    assert code == 0
    plan = json.loads(out)["plan"]
    assert plan["coordinator_candidates"] == [
        {"backend": "openrouter", "model": "openrouter/vendor/m", "model_verified": False}]
    assert plan["bindings_overlay"].endswith("model-overlay.yaml")


def test_cli_live_run_without_the_binary_or_binding_says_which(
        tmp_path: Path, capsys, monkeypatch) -> None:
    monkeypatch.setenv(config_module.BINDINGS_OVERLAY_ENV, "")
    monkeypatch.setattr(shutil, "which", lambda _name: None)
    code, _, err = _run(capsys, "--preset", "abliterated-claude", "--once",
                        "--repo", str(tmp_path), "--state-dir", str(tmp_path / "state"))
    assert code == 2 and "claude CLI is unavailable" in err

    monkeypatch.setattr(shutil, "which", lambda name: f"/bin/{name}")
    code, _, err = _run(capsys, "--preset", "openrouter", "--once",
                        "--repo", str(tmp_path), "--state-dir", str(tmp_path / "state"))
    assert code == 2 and "no model bound" in err and "model-bindings.local" in err
