#!/usr/bin/env python3
"""Additive post-run correction for the GP version capture gap in factor receipts."""

import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "gp_environment_correction.json"
if OUT.exists():
    raise FileExistsError("The additive correction is write-once")
receipts = {}
for name in ("prime239v2", "skip239_2682"):
    path = HERE / "factor_runs" / (name + ".json")
    raw = path.read_bytes()
    parsed = json.loads(raw)
    if parsed["gp_version"] != "":
        raise ValueError("The original receipt has no version capture gap")
    receipts[name] = hashlib.sha256(raw).hexdigest()
binary = Path(shutil.which("gp") or "").resolve()
if not binary.is_file():
    raise FileNotFoundError("gp")
result = subprocess.run(["gp", "--version"], capture_output=True, text=True, check=True)
record = {
    "schema": "nist-seed-factor-gp-environment-correction/v1",
    "reason": "factor_twists.py stored only gp --version stdout, while this installation writes its version banner to stderr",
    "scope": "post-run environment observation; does not prove exact binary identity at factor-run time",
    "captured_utc": datetime.now(timezone.utc).isoformat(),
    "original_receipt_sha256": receipts,
    "command": ["gp", "--version"],
    "exit_code": result.returncode,
    "stdout": result.stdout,
    "stderr": result.stderr,
    "resolved_binary_path": str(binary),
    "resolved_binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
    "resolved_binary_mtime_ns": binary.stat().st_mtime_ns,
}
OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
print(f"wrote {OUT}")
