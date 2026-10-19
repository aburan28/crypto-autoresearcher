#!/usr/bin/env python3
"""Render (do NOT write) crypto-autoresearcher's generated formal root module, to show
which modules AxiomAudit.lean's `import CryptoResearch` reaches. Read-only."""
import sys
from pathlib import Path
repo = Path(sys.argv[1])
sys.path.insert(0, str(repo))
from orchestration.formal.workspace import render_root, modules  # noqa: E402
ws = repo / "formal"
mods = modules(ws)
print(f"{len(mods)} module(s) under formal/CryptoResearch/")
print("includes CryptoResearch.Quotient.TranslationDescent:", "CryptoResearch.Quotient.TranslationDescent" in mods)
print("root on disk exists:", (ws / "CryptoResearch.lean").exists())
print("---- rendered root ----")
print(render_root(ws))
