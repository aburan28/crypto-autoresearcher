#!/usr/bin/env python3
"""Dependency-free contract tests for the portable plugin package."""
from __future__ import annotations

import json
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
REPO = PLUGIN.parents[1]
NAME = "crypto-autoresearcher-harness"


class PluginBundleTests(unittest.TestCase):
    def test_manifests_name_the_same_plugin(self) -> None:
        codex = json.loads(
            (PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        claude = json.loads(
            (PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(codex["name"], NAME)
        self.assertEqual(claude["name"], NAME)
        self.assertEqual(codex["skills"], "./skills/")
        # A peer endpoint is a per-checkout operational choice.  The plugin
        # itself stays offline until the user deliberately connects one using
        # the host-specific client snippet after starting the local daemon.
        self.assertNotIn("mcpServers", codex)
        self.assertRegex(codex["version"], r"^0\.2\.0\+codex\.[a-z0-9-]+$")
        self.assertEqual(claude["version"], "0.2.0")

    def test_explicit_peer_mcp_host_templates_share_loopback_endpoint(self) -> None:
        expected_url = "http://127.0.0.1:8765/mcp"
        claude = json.loads(
            (PLUGIN / "clients" / "claude-code.mcp.json").read_text(encoding="utf-8")
        )
        opencode = json.loads(
            (PLUGIN / "clients" / "opencode.json").read_text(encoding="utf-8")
        )
        codex = tomllib.loads(
            (PLUGIN / "clients" / "codex.toml").read_text(encoding="utf-8")
        )
        server_name = "crypto-autoresearcher-peer"
        self.assertEqual(claude["mcpServers"][server_name]["type"], "http")
        self.assertEqual(claude["mcpServers"][server_name]["url"], expected_url)
        self.assertEqual(opencode["mcp"][server_name]["type"], "remote")
        self.assertEqual(opencode["mcp"][server_name]["url"], expected_url)
        self.assertTrue(opencode["mcp"][server_name]["enabled"])
        self.assertEqual(codex["mcp_servers"][server_name]["url"], expected_url)

    def test_marketplaces_point_to_this_package(self) -> None:
        codex = json.loads(
            (REPO / ".agents" / "plugins" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        claude = json.loads(
            (REPO / ".claude-plugin" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(codex["name"], "crypto-autoresearcher")
        self.assertEqual(codex["plugins"][0]["name"], NAME)
        self.assertEqual(
            codex["plugins"][0]["source"]["path"],
            "./plugins/crypto-autoresearcher-harness",
        )
        self.assertEqual(claude["name"], "crypto-autoresearcher")
        self.assertEqual(claude["plugins"][0]["name"], NAME)
        self.assertEqual(
            claude["plugins"][0]["source"],
            "./plugins/crypto-autoresearcher-harness",
        )

    def test_repository_adapter_delegates_to_canonical_skill(self) -> None:
        canonical = PLUGIN / "skills" / NAME / "SKILL.md"
        adapter = REPO / ".agents" / "skills" / NAME / "SKILL.md"
        self.assertTrue(canonical.is_file())
        self.assertTrue(adapter.is_file())
        body = adapter.read_text(encoding="utf-8")
        self.assertIn(
            "plugins/crypto-autoresearcher-harness/skills/"
            "crypto-autoresearcher-harness/SKILL.md",
            body,
        )
        self.assertIn("Codex and OpenCode", body)

    def test_static_preflight_passes_for_each_host(self) -> None:
        script = PLUGIN / "scripts" / "preflight.py"
        for runtime in ("claude-code", "opencode", "codex"):
            with self.subTest(runtime=runtime):
                completed = subprocess.run(
                    [sys.executable, str(script), "--repo", str(REPO),
                     "--runtime", runtime],
                    cwd=REPO,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                self.assertEqual(completed.returncode, 0, completed.stdout)
                self.assertIn("READY:", completed.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
