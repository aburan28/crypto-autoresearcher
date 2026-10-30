#!/usr/bin/env python3
"""Check and bind the pinned, named Lake build and imported axiom log.

This records fresh command outputs from this run. The logs are not remote
attestation, and this does not claim the full workspace verifier passed.
"""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
FORMAL = ROOT / "formal"
PRODUCER = "6409590d9bf26201956095e87f36f25d346cba68"
INPUTS = [
    "formal/CryptoResearch/Binstd/EncodedDivisors.lean",
    "formal/targets/binstd-encoded-divisors.yaml",
    "formal/lake-manifest.json",
    "formal/lean-toolchain",
    "formal/lakefile.toml",
]
NAMES = [
    "modulus17_no_small_monic_divisor",
    "factor8a_no_small_monic_divisor",
    "factor8b_no_small_monic_divisor",
    "archived_trial_counts",
    "reducible_control_witnesses",
    "reducible_controls_rejected",
    "archived_no_small_monic_divisors",
]


def git(*args):
    return subprocess.check_output(["git", *map(str, args)], cwd=ROOT, text=True).strip()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--check", action="store_true",
                    help="verify the existing receipt without changing it")
args = parser.parse_args()
output = HERE / "lake-named-validation.json"
existing = json.loads(output.read_text()) if args.check else None
if not args.check:
    assert not output.exists(), "receipt already exists; use --check"

assert subprocess.run(["git", "diff", "--quiet", PRODUCER, "HEAD", "--", *INPUTS],
                      cwd=ROOT).returncode == 0
for path in INPUTS:
    frozen = subprocess.check_output(["git", "show", f"{PRODUCER}:{path}"], cwd=ROOT)
    assert (ROOT / path).read_bytes() == frozen, path
manifest = json.loads((FORMAL / "lake-manifest.json").read_text())
packages = []
for pkg in manifest["packages"]:
    checkout = FORMAL / ".lake/packages" / pkg["name"]
    head = subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"],
                                   text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(checkout), "status", "--porcelain",
                                     "--untracked-files=no"], text=True).strip()
    assert head == pkg["rev"] and not dirty, pkg["name"]
    packages.append({"name": pkg["name"], "revision": head, "tracked_clean": True})

log_files = [
    "binstd-lake-no-build-02.log", "binstd-lake-no-build-02.exit",
    "binstd-lake-named-20261027.log", "binstd-lake-named-20261027.exit",
    "binstd-lake-audit-20261027.log", "binstd-lake-audit-20261027.exit",
    "BinstdLakeAudit.lean",
]
assert (HERE / "binstd-lake-no-build-02.exit").read_text().strip() == "3"
assert "target is out-of-date and needs to be rebuilt" in (
    HERE / "binstd-lake-no-build-02.log").read_text()
assert (HERE / "binstd-lake-named-20261027.exit").read_text().strip() == "0"
assert "Built CryptoResearch.Binstd.EncodedDivisors" in (
    HERE / "binstd-lake-named-20261027.log").read_text()
assert (HERE / "binstd-lake-audit-20261027.exit").read_text().strip() == "0"

axiom_lines = (HERE / "binstd-lake-audit-20261027.log").read_text().splitlines()
assert len(axiom_lines) == len(NAMES)
for name, line in zip(NAMES, axiom_lines):
    assert f"CryptoResearch.Binstd.EncodedDivisors.{name}'" in line
    if name == "archived_trial_counts":
        assert line.endswith("does not depend on any axioms")
    else:
        assert line.endswith("depends on axioms: [propext]")

audit_source = (HERE / "BinstdLakeAudit.lean").read_text()
assert audit_source.startswith("import CryptoResearch.Binstd.EncodedDivisors\n")
for name in NAMES:
    assert ("#print axioms CryptoResearch.Binstd.EncodedDivisors." + name) in audit_source

receipt = {
    "schema": "binstd.lake_named_validation.v1",
    "producer_revision": PRODUCER,
    "review_branch_revision": (existing["review_branch_revision"] if args.check
                               else git("rev-parse", "HEAD")),
    "toolchain": (FORMAL / "lean-toolchain").read_text().strip(),
    "input_sha256": {path: sha256(ROOT / path) for path in INPUTS},
    "frozen_inputs_unchanged_since_producer": True,
    "manifest_packages": packages,
    "commands": [
        {"argv": ["lake", "--no-build", "build", "+CryptoResearch.Binstd.EncodedDivisors"],
         "cwd": "formal", "timeout_seconds": 180,
         "exit_code": 3, "meaning": "exact dependencies materialized; target out of date"},
        {"argv": ["lake", "build", "+CryptoResearch.Binstd.EncodedDivisors"],
         "cwd": "formal", "timeout_seconds": 180,
         "exit_code": 0, "meaning": "named module built"},
        {"argv": ["lake", "env", "lean", "-j", "1", "-s", "16384",
                  "/home/ec2-user/scratch/validation-continuation-20261023/BinstdLakeAudit.lean"],
         "cwd": "formal", "timeout_seconds": 120,
         "exit_code": 0, "meaning": "seven imported axiom queries completed",
         "replay_input": "research/binstd_end_to_end_20261026/lake-named-20261027/BinstdLakeAudit.lean"},
    ],
    "artifact_sha256": {name: sha256(HERE / name) for name in log_files},
    "axiom_results": {name: ([] if name == "archived_trial_counts" else ["propext"])
                      for name in NAMES},
    "named_module_build": "passed",
    "full_workspace_build": "not_verified",
    "formal_target_verifier": "not_verified",
    "polynomial_bridge": "not_proved_by_this_module",
    "execution_authentication": "local command output and file hashes; no independent kernel binary recheck",
}
content = json.dumps(receipt, indent=2) + "\n"
if args.check:
    revision = existing["review_branch_revision"]
    assert len(revision) == 40
    subprocess.run(["git", "cat-file", "-e", f"{revision}^{{commit}}"],
                   cwd=ROOT, check=True)
    assert output.read_text() == content, "receipt differs from frozen evidence"
else:
    output.write_text(content)
print("PASS: nine exact clean dependencies, named Lake module, seven axiom lines")
