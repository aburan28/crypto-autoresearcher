#!/usr/bin/env python3
"""Preserve and repair the first R2 verifier attempt without rerunning R2."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/EXP-ECRANK-52d039/runs/RUN-ECRANK-52d039-R2-elliptic-interface"
VERIFIER = ROOT / "experiments/EXP-ECRANK-52d039/source/verifier.py"
RAW = RUN / "producer-raw.json"


def write_json(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def scientific(value):
    if isinstance(value, dict):
        return {k: scientific(v) for k, v in value.items() if k not in {"wall_seconds_internal", "wall_seconds", "started_at", "finished_at", "recorded_at"}}
    if isinstance(value, list):
        return [scientific(v) for v in value]
    return value


def main():
    for suffix in ("stdout.log", "stderr.log"):
        source = RUN / f"verifier.{suffix}"
        if source.exists():
            (RUN / f"verifier-attempt-1.{suffix}").write_bytes(source.read_bytes())
    proc = subprocess.run([sys.executable, str(VERIFIER), "r2", str(RAW)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=3600)
    (RUN / "verifier.stdout.log").write_text(proc.stdout, encoding="utf-8")
    (RUN / "verifier.stderr.log").write_text(proc.stderr, encoding="utf-8")
    try:
        verification = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        verification = {"agreement": False, "errors": [f"verifier JSON parse failed after retry: {exc}"], "independent_rederivation": False}
    produced = json.loads(RAW.read_text(encoding="utf-8"))
    combined = {"producer": produced, "verifier": verification, "agreement": bool(verification.get("agreement")), "scientific_projection_sha256": hashlib.sha256(json.dumps(scientific(produced), sort_keys=True, separators=(",", ":")).encode()).hexdigest()}
    write_json(RUN / "raw-result.json", combined)
    manifest = json.loads((RUN / "manifest.yaml").read_text(encoding="utf-8"))
    body = manifest["run"]
    body["status"] = "failed" if produced.get("status") == "failed_infrastructure" else ("completed" if verification.get("agreement") else "invalid")
    body["validity"] = "failed_infrastructure" if produced.get("status") == "failed_infrastructure" else ("completed_valid" if verification.get("agreement") else "completed_invalid")
    body["result"]["verifier_agreement"] = bool(verification.get("agreement"))
    body["result"]["verifier_errors"] = verification.get("errors", [])
    body["artifacts"].extend([f"experiments/EXP-ECRANK-52d039/runs/RUN-ECRANK-52d039-R2-elliptic-interface/{name}" for name in ("verifier-attempt-1.stdout.log", "verifier-attempt-1.stderr.log")])
    write_json(RUN / "manifest.yaml", manifest)
    print(json.dumps(verification, sort_keys=True, separators=(",", ":")))
    raise SystemExit(0 if verification.get("agreement") else 1)


if __name__ == "__main__":
    main()
