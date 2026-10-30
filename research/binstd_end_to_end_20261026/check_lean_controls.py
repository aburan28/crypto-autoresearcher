#!/usr/bin/env python3
"""Capture a pinned direct Lean compile and axiom audit for encoded controls.

The full Mathlib-backed workspace gate and independent statement review are
separate obligations. This helper records only the named Init-based module.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import pathlib
import platform
import subprocess
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
SOURCE = ROOT / "formal/CryptoResearch/Binstd/EncodedDivisors.lean"
EVIDENCE = HERE / "evidence.json"
OUTPUT = HERE / "lean-encoded-controls-validation.json"
TOOLCHAIN = "leanprover/lean4:v4.35.0-rc1"
NAMESPACE = "CryptoResearch.Binstd.EncodedDivisors."
THEOREMS = (
    "modulus17_no_small_monic_divisor",
    "factor8a_no_small_monic_divisor",
    "factor8b_no_small_monic_divisor",
    "archived_trial_counts",
    "reducible_control_witnesses",
    "reducible_controls_rejected",
    "archived_no_small_monic_divisors",
)


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str]) -> dict:
    start = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                            timeout=120, check=False)
    return {
        "command": command,
        "exit_code": result.returncode,
        "elapsed_seconds": round(time.monotonic() - start, 3),
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main() -> None:
    if (ROOT / "formal/lean-toolchain").read_text().strip() != TOOLCHAIN:
        raise RuntimeError("formal toolchain pin changed")
    source_sha_before = sha256(SOURCE)
    evidence_sha_before = sha256(EVIDENCE)
    base = ["elan", "run", TOOLCHAIN, "lean"]
    version = subprocess.check_output(base + ["--version"], text=True).strip()
    direct = run(base + [str(SOURCE)])
    if direct["exit_code"]:
        raise RuntimeError(f"direct Lean compile failed: {direct['stderr'][-1200:]}")
    audit_source = SOURCE.read_text() + "\n" + "\n".join(
        "#print axioms " + NAMESPACE + name for name in THEOREMS) + "\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".lean", prefix="binstd-axioms-",
                                     delete=False) as file:
        file.write(audit_source)
        audit_path = pathlib.Path(file.name)
    try:
        audit = run(base + [str(audit_path)])
    finally:
        audit_path.unlink(missing_ok=True)
    if audit["exit_code"]:
        raise RuntimeError(f"Lean axiom audit failed: {audit['stderr'][-1200:]}")
    lines = [line for line in audit["stdout"].splitlines()
             if "depends on axioms:" in line or "does not depend on any axioms" in line]
    if len(lines) != len(THEOREMS):
        raise RuntimeError(f"expected {len(THEOREMS)} axiom lines, got {lines!r}")
    for name, line in zip(THEOREMS, lines):
        if NAMESPACE + name not in line or not (
            line.endswith("depends on axioms: [propext]")
            or line.endswith("does not depend on any axioms")
        ):
            raise RuntimeError(f"unexpected axiom output: {line}")
    if sha256(SOURCE) != source_sha_before or sha256(EVIDENCE) != evidence_sha_before:
        raise RuntimeError("source or archived evidence changed during audit")
    receipt = {
        "schema": "binstd.encoded_divisor_lean_controls_validation.v1",
        "checked_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "toolchain": version,
        "platform": platform.platform(),
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": source_sha_before,
        "evidence": str(EVIDENCE.relative_to(ROOT)),
        "evidence_sha256": evidence_sha_before,
        "checker": str(pathlib.Path(__file__).resolve().relative_to(ROOT)),
        "checker_sha256": sha256(pathlib.Path(__file__)),
        "direct_compile": direct,
        "axiom_check": {"command": base + ["<temporary audit source>"],
                        "exit_code": audit["exit_code"],
                        "elapsed_seconds": audit["elapsed_seconds"],
                        "audit_source_sha256": hashlib.sha256(audit_source.encode()).hexdigest(),
                        "stdout": audit["stdout"], "stderr": audit["stderr"],
                        "lines": lines},
        "full_lake_workspace_build": False,
        "independent_semantic_review": False,
        "scope": "Kernel-checked exact encoded positive trials, counts and two reducible controls; no F2[X] irreducibility bridge",
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2) + "\n")
    print("direct Lean compile and seven axiom audits passed")
    print("source_sha256", receipt["source_sha256"])
    print("receipt_sha256", sha256(OUTPUT))


if __name__ == "__main__":
    main()
