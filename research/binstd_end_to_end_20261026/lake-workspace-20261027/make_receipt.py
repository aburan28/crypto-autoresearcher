#!/usr/bin/env python3
"""Check immutable local evidence for the bounded full-workspace attempts."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FROZEN = "b2ff94a736b6b9cd387c581e10ca2c9ad5cfe177"
RUNS = [
    ("binstd-lake-root-20261027", 300, 124, "generated root missing"),
    ("binstd-lake-root-retry-20261027", 480, 143, "terminated after missing-root diagnosis"),
    ("binstd-lake-root-generated-20261027", 420, 124, "heavy certificate compiled; root timed out"),
    ("binstd-lake-root-final-20261027", 30, 124, "incremental module compiled; root timed out"),
]
INPUTS = (
    "formal/CryptoResearch/Binstd/EncodedDivisors.lean",
    "formal/targets/binstd-encoded-divisors.yaml",
    "formal/lake-manifest.json",
    "formal/lean-toolchain",
    "formal/lakefile.toml",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(rev: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{rev}:{path}"], cwd=ROOT, check=True,
        stdout=subprocess.PIPE,
    ).stdout


def build() -> dict:
    named = ROOT / "research/binstd_end_to_end_20261026/lake-named-20261027/lake-named-validation.json"
    named_data = json.loads(named.read_text())
    assert named_data["named_module_build"] == "passed"
    assert named_data["full_workspace_build"] == "not_verified"
    assert named_data["formal_target_verifier"] == "not_verified"

    input_hashes = {}
    for rel in INPUTS:
        live = (ROOT / rel).read_bytes()
        assert live == git_blob(FROZEN, rel), rel
        value = hashlib.sha256(live).hexdigest()
        assert value == named_data["input_sha256"][rel], rel
        input_hashes[rel] = value

    root_source = HERE / "generated-root.lean"
    assert root_source.read_bytes() == (ROOT / "formal/CryptoResearch.lean").read_bytes()
    imports = [line for line in root_source.read_text().splitlines() if line.startswith("import ")]
    assert len(imports) == 48
    assert "import CryptoResearch.Binstd.EncodedDivisors" in imports

    artifacts = {"generated-root.lean": digest(root_source)}
    runs = []
    for stem, seconds, expected_exit, meaning in RUNS:
        log_file, exit_file = HERE / f"{stem}.log", HERE / f"{stem}.exit"
        log = log_file.read_text()
        code = int(exit_file.read_text().strip())
        assert code == expected_exit, stem
        if "generated" not in stem and "final" not in stem:
            assert "formal/CryptoResearch.lean" in log and "no such file or directory" in log
        if "generated" in stem:
            assert "Built CryptoResearch.Semaev.BooleanParityDegreeThreeRankCertificate (343s)" in log
        if "final" in stem:
            assert "Built CryptoResearch.Semaev.ConcreteFirstFallWitness (13s)" in log
        artifacts[log_file.name] = digest(log_file)
        artifacts[exit_file.name] = digest(exit_file)
        runs.append({"command": ["timeout", str(seconds), "lake", "build"],
                     "cwd": "formal", "exit_code": code, "meaning": meaning})

    return {
        "schema": "binstd.lake_workspace_continuation.v1",
        "frozen_branch_revision": FROZEN,
        "producer_revision": named_data["producer_revision"],
        "named_validation_sha256": digest(named),
        "toolchain": named_data["toolchain"],
        "frozen_inputs_sha256": input_hashes,
        "generated_root_imports": len(imports),
        "runs": runs,
        "artifact_sha256": artifacts,
        "full_workspace_build": "incomplete_bounded_timeouts",
        "formal_target_verifier": "not_run",
        "project_axiom_audit": "not_run_after_workspace_build",
        "claim_boundary": "named BINSTD encoded computation only; no polynomial or Frobenius bridge",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build(), indent=2) + "\n"
    output = HERE / "workspace-build-receipt.json"
    if args.check:
        assert output.read_text() == content, "receipt differs from current evidence"
        print("workspace receipt matches logs, exits, frozen inputs and generated root")
    else:
        assert not output.exists(), "receipt exists; use --check"
        output.write_text(content)
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
