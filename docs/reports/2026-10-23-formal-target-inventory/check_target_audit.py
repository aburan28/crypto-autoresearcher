#!/usr/bin/env python3
"""Bind a pinned Lean target-name/axiom sweep to one repository commit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
EXPECTED_COMMIT = "d513b75233e1eb58b24c753ff51675b83b284b44"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def manifest_hash(repo: Path, paths: list[str]) -> str:
    manifest = "".join(f"{path} {sha256(repo / path)}\n" for path in paths)
    return hashlib.sha256(manifest.encode()).hexdigest()


def main() -> None:
    if not __debug__:
        raise RuntimeError("validation assertions require normal Python mode")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True, help="complete checkout at the pinned commit")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    assert git(repo, "rev-parse", "HEAD") == EXPECTED_COMMIT
    assert git(repo, "rev-parse", "--is-shallow-repository") == "false"

    specs: list[tuple[str, str, str]] = []
    for path in sorted((repo / "formal/targets").glob("*.yaml")):
        spec = yaml.safe_load(path.read_text())
        workspace = spec.get("workspace", "formal")
        theorem_file = repo / workspace / spec["theorem_file"]
        assert theorem_file.is_file(), path
        name = spec["theorem_name"]
        assert re.fullmatch(r"[A-Za-z_][A-Za-z0-9_'.]*", name), name
        specs.append((str(path.relative_to(repo)), workspace, name))
    main_specs = [(path, name) for path, workspace, name in specs if workspace == "formal"]
    scoped_specs = [(path, name) for path, workspace, name in specs if workspace == "formal/scoped-obstructions"]
    assert len(specs) == 83 and len(main_specs) == 82 and len(scoped_specs) == 1

    generated = "import CryptoResearch\n\n" + "".join(
        f"-- {path.rsplit('/', 1)[-1]}\n#check {name}\n#print axioms {name}\n"
        for path, name in main_specs
    )
    lean_source = HERE / "TargetBatchAudit.lean"
    assert lean_source.read_text() == generated, "target audit source differs from specs"

    log = (HERE / "evidence/main-target-batch.log").read_text()
    dependent = re.findall(r"'([^']+)' depends on axioms:\s*\[([^]]*)\]", log)
    independent = re.findall(r"'([^']+)' does not depend on any axioms", log)
    axiom_sets: dict[str, set[str]] = {}
    for name, content in dependent:
        assert name not in axiom_sets, name
        axiom_sets[name] = {item.strip() for item in content.split(",") if item.strip()}
    for name in independent:
        assert name not in axiom_sets, name
        axiom_sets[name] = set()
    assert len(dependent) == 74 and len(independent) == 8
    assert set(axiom_sets) == {name for _, name in main_specs}
    unexpected = {name: sorted(axioms - ALLOWED_AXIOMS)
                  for name, axioms in axiom_sets.items() if not axioms <= ALLOWED_AXIOMS}
    assert not unexpected, unexpected

    assert "Build completed successfully (8975 jobs)." in (HERE / "evidence/main-build.log").read_text()
    assert "axiom audit: 652 theorem(s), all standard axioms only" in (HERE / "evidence/main-axiom.log").read_text()
    assert "Build completed successfully." in (HERE / "evidence/scoped-build.log").read_text()
    scoped_log = (HERE / "evidence/scoped-axiom.log").read_text()
    assert f"zero-axiom audit passed: {scoped_specs[0][1]}" in scoped_log

    tracked_formal = git(repo, "ls-files", "formal").splitlines()
    assert len(tracked_formal) == 148
    spec_paths = [path for path, _, _ in specs]
    receipt = {
        "schema": "formal-target-declaration-audit-v1",
        "status": "pass",
        "main_commit": EXPECTED_COMMIT,
        "lean_main_toolchain": (repo / "formal/lean-toolchain").read_text().strip(),
        "lean_scoped_toolchain": (repo / "formal/scoped-obstructions/lean-toolchain").read_text().strip(),
        "formal_files_checked": len(tracked_formal),
        "formal_file_manifest_sha256": manifest_hash(repo, tracked_formal),
        "target_specs": len(specs),
        "target_spec_manifest_sha256": manifest_hash(repo, spec_paths),
        "target_theorem_files_present": len(specs),
        "main_target_names_resolved": len(main_specs),
        "main_targets_with_standard_axioms": len(dependent),
        "main_targets_with_no_axioms": len(independent),
        "main_workspace_build_jobs": 8975,
        "main_workspace_audited_theorems": 652,
        "scoped_target_names_zero_axiom_audited": len(scoped_specs),
        "checker_sha256": sha256(Path(__file__)),
        "batch_lean_source_sha256": sha256(lean_source),
        "evidence_sha256": {path.name: sha256(path) for path in sorted((HERE / "evidence").glob("*.log"))},
        "scope": "pinned build, declaration resolution, and axiom dependencies; no independent semantic review or experiment replay",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
