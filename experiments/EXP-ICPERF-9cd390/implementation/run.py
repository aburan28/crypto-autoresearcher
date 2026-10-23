#!/usr/bin/env python3
"""Trial driver for EXP-ICPERF-9cd390: one step of the crypto launcher.

The science lives in the crypto repository (Rust, `examples/ic_probe_latency.rs`
and `examples/koblitz_orbit_dlp_fast.rs`) behind the frozen step script
`research/ic_probe_latency_20261017/run_step.sh`. This driver only:

1. locates the crypto checkout (`$CRYPTO_ROOT`, else `../crypto` beside this
   repository);
2. refuses to run unless the launcher files hash to the frozen values below
   (the step script then checks every source and input it uses);
3. runs the step with its output under `RUN_DIR/crypto/`;
4. writes `raw-result.json` and `manifest.yaml` (file names and SHA-256 of
   every output). It computes no metric.

    run.py --step STEP --run-dir DIR [--arg K] [--dep DIR ...]

`--dep` passes another trial's run directory; the step reads its `crypto/`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

EXPERIMENT = "EXP-ICPERF-9cd390"
STUDY = "research/ic_probe_latency_20261017"
# Frozen launcher: crypto commit 286bc22cc (PR aburan28/crypto#2069).
PROTOCOL_COMMIT = "286bc22cc7c4f93a354b667981bf786f2f9fa671"
FROZEN = {
    f"{STUDY}/run_step.sh": "5483dc906224a0385221f5cf3c94dd10348faf57b72ce673dc0585df9d88df91",
    f"{STUDY}/sources.sha256": "415d0e8ed4a0811555bb7740ea032fb329ae9dca7276d2e9d53e03560be3f20f",
    f"{STUDY}/PROTOCOL.md": "8a2d32f46c940abca0dd825d85fddf948736c8a597e42c1299f7e23073f87b84",
}
STEPS = ("build", "stage0", "sweep", "rho", "ic-4k", "ic-2m", "claims")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def crypto_root() -> Path:
    env = os.environ.get("CRYPTO_ROOT")
    if env:
        return Path(env).resolve()
    return (Path(__file__).resolve().parents[3].parent / "crypto").resolve()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", required=True, choices=STEPS)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--arg", action="append", default=[])
    parser.add_argument("--dep", action="append", default=[], type=Path)
    args = parser.parse_args()

    root = crypto_root()
    run_dir = args.run_dir.resolve()
    result: dict = {"experiment_id": EXPERIMENT, "step": args.step, "crypto_root": str(root),
                    "protocol_commit": PROTOCOL_COMMIT}
    mismatches = [p for p, want in FROZEN.items()
                  if not (root / p).is_file() or sha256(root / p) != want]
    if mismatches:
        result.update(status="failed_infrastructure", reason=f"frozen launcher mismatch: {mismatches}")
        return finish(run_dir, result, {}, 2)
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    result["crypto_head"] = head

    out = run_dir / "crypto"
    argv = ["sh", str(root / STUDY / "run_step.sh"), args.step, str(out)]
    argv += [str(d.resolve() / "crypto") for d in args.dep] + args.arg
    result["argv"] = argv
    status = subprocess.run(argv).returncode
    result["exit_status"] = status
    result["status"] = "completed_valid" if status == 0 else "failed_execution"
    outputs = {}
    if out.is_dir():
        for path in sorted(p for p in out.rglob("*") if p.is_file()):
            outputs[path.relative_to(run_dir).as_posix()] = sha256(path)
    if args.step == "claims" and (out / "claims.json").is_file():
        result["claims"] = json.loads((out / "claims.json").read_text(encoding="utf-8"))
    return finish(run_dir, result, outputs, status)


def finish(run_dir: Path, result: dict, outputs: dict, status: int) -> int:
    result["outputs_sha256"] = outputs
    (run_dir / "raw-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                                             encoding="utf-8")
    lines = [f"experiment_id: {EXPERIMENT}", f"step: {result['step']}",
             f"status: {result['status']}", f"protocol_commit: {PROTOCOL_COMMIT}",
             f"crypto_head: {result.get('crypto_head', 'unknown')}", "outputs:"]
    lines += [f"  {name}: {digest}" for name, digest in outputs.items()] or ["  {}"]
    (run_dir / "manifest.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return status


if __name__ == "__main__":
    sys.exit(main())
