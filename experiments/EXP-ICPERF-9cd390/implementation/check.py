#!/usr/bin/env python3
"""Post-trial checker for EXP-ICPERF-9cd390: outputs exist and match the manifest.

    check.py RUN_DIR STEP

Checks presence and integrity only; it interprets no metric. The claims
trial additionally requires every preregistered claim id to be present.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXPECTED = {
    "build": ["crypto/build.log", "crypto/launch.tsv"],
    "stage0": ["crypto/geomfit.json"],
    "sweep": [f"crypto/chase-{b}-{p}.json" for b in ("1Mi", "16Mi", "256Mi", "1Gi", "8Gi")
              for p in ("4k", "2m")],
    "rho": ["crypto/receipt.json"],
    "ic-4k": ["crypto/chase.json", "crypto/targets_result.jsonl", "crypto/stdout.jsonl"],
    "ic-2m": ["crypto/chase.json", "crypto/targets_result.jsonl", "crypto/stdout.jsonl"],
    "claims": ["crypto/claims.json"],
}
CLAIM_IDS = {"G.scalars", "G.probes", "L1", "L1g", "T1.applied", "T1.null", "T1", "R", "D",
             "H1.k1271_regular", "H1.k1271_dense", "H1.k1500_dense", "H1.k1798_dense",
             "H1.k1798_dense_on_host_a1"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[2] not in EXPECTED:
        print("usage: check.py RUN_DIR STEP", file=sys.stderr)
        return 2
    run_dir, step = Path(sys.argv[1]), sys.argv[2]
    raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
    if raw.get("step") != step or raw.get("status") != "completed_valid":
        print(f"FAIL: step {raw.get('step')!r} status {raw.get('status')!r}", file=sys.stderr)
        return 1
    if (run_dir / "crypto" / "exit_status.txt").read_text().strip() != "0":
        print("FAIL: step exit status is not 0", file=sys.stderr)
        return 1
    outputs = raw.get("outputs_sha256") or {}
    for name in EXPECTED[step]:
        if name not in outputs or not (run_dir / name).is_file():
            print(f"FAIL: missing output {name}", file=sys.stderr)
            return 1
    for name, digest in outputs.items():
        if sha256(run_dir / name) != digest:
            print(f"FAIL: {name} changed after the run", file=sys.stderr)
            return 1
    if step == "claims":
        ids = {c["id"] for c in raw["claims"]["claims"]}
        if not CLAIM_IDS <= ids:
            print(f"FAIL: claims missing {sorted(CLAIM_IDS - ids)}", file=sys.stderr)
            return 1
    print(f"OK: {step}, {len(outputs)} outputs verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
