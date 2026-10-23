#!/usr/bin/env python3
"""Check the additive 84-target audit against named main formal and source files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
MAIN = "969e051e204ab8c5668157ebeeb00734a1f074b1"
OLD_MAIN = "d513b75233e1eb58b24c753ff51675b83b284b44"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def manifest_hash(repo: Path, paths: list[str]) -> str:
    manifest = "".join(f"{path} {sha256(repo / path)}\n" for path in paths)
    return hashlib.sha256(manifest.encode()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True, help="full-history checkout with the named main formal tree")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    require(git(repo, "rev-parse", "--is-shallow-repository") == "false", "shallow checkout")
    formal_tree = git(repo, "rev-parse", f"{MAIN}:formal")
    require(git(repo, "rev-parse", "HEAD:formal") == formal_tree, "working head formal tree differs from main")
    require(not git(repo, "status", "--porcelain", "--untracked-files=no", "--", "formal"), "tracked formal files edited")
    require(
        git(repo, "rev-parse", f"{OLD_MAIN}:formal/scoped-obstructions")
        == git(repo, "rev-parse", f"{MAIN}:formal/scoped-obstructions"),
        "scoped workspace differs from prior audited tree",
    )

    specs: list[tuple[str, str, str]] = []
    sources: set[str] = set()
    task_ids: set[str] = set()
    claim_ids: set[str] = set()
    theorem_names: set[str] = set()
    source_status_counts: dict[str, int] = {}
    for path in sorted((repo / "formal/targets").glob("*.yaml")):
        spec = yaml.safe_load(path.read_text())
        source = spec["source"]
        source_path = Path(source)
        require(not source_path.is_absolute() and ".." not in source_path.parts,
                f"invalid source path: {path}")
        require((repo / source_path).is_file(), f"missing source file: {path}")
        sources.add(source)
        require(isinstance(spec.get("claim"), str) and bool(spec["claim"].strip()),
                f"missing claim text: {path}")
        for field, seen in (("task_id", task_ids), ("claim_id", claim_ids),
                            ("theorem_name", theorem_names)):
            value = spec[field]
            require(isinstance(value, str) and bool(value), f"invalid {field}: {path}")
            require(value not in seen, f"duplicate {field}: {value}")
            seen.add(value)
        status = spec["source_status"]
        source_status_counts[status] = source_status_counts.get(status, 0) + 1
        workspace = spec.get("workspace", "formal")
        theorem_file = repo / workspace / spec["theorem_file"]
        require(theorem_file.is_file(), f"missing theorem file: {path}")
        name = spec["theorem_name"]
        require(bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_'.]*", name)), f"bad theorem name: {name}")
        specs.append((str(path.relative_to(repo)), workspace, name))
    main_specs = [(path, name) for path, workspace, name in specs if workspace == "formal"]
    scoped_specs = [(path, name) for path, workspace, name in specs if workspace == "formal/scoped-obstructions"]
    require(len(specs) == 84 and len(main_specs) == 83 and len(scoped_specs) == 1, "unexpected target inventory")
    for source in sorted(sources):
        source_blob = subprocess.check_output(["git", "-C", str(repo), "show", f"{MAIN}:{source}"])
        require(sha256(repo / source) == hashlib.sha256(source_blob).hexdigest(),
                f"source file differs from named main: {source}")
    require(
        any(path.endswith("endosweep-dk-exact-batch5-discriminants.yaml") and
            name == "CryptoResearch.Endosweep.DkExactBatch5.exact_discriminants"
            for path, name in main_specs),
        "batch-five target is absent",
    )

    generated = "import CryptoResearch\n\n" + "".join(
        f"-- {path.rsplit('/', 1)[-1]}\n#check {name}\n#print axioms {name}\n"
        for path, name in main_specs
    )
    lean_source = HERE / "CurrentMainTargetBatchAudit.lean"
    require(lean_source.read_text() == generated, "batch source differs from named target specs")
    theorem_type_lines = ["import CryptoResearch", "import Lean", "open Lean Elab Command", ""]
    for path, name in main_specs:
        theorem_type_lines.extend([
            f"-- {path.rsplit('/', 1)[-1]}",
            "run_cmd do",
            f"  let target := `{name}",
            "  match (← getEnv).find? target with",
            '  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"',
            '  | _ => throwError "requested declaration is not a theorem: {target}"',
            "",
        ])
    theorem_type_source = HERE / "CurrentMainTheoremTypeAudit.lean"
    require(theorem_type_source.read_text() == "\n".join(theorem_type_lines),
            "theorem-type audit source differs from specs")

    evidence = HERE / "evidence"
    build_log = evidence / "current-main-build.log"
    batch_log = evidence / "current-main-target-batch.log"
    axiom_log = evidence / "current-main-axiom.log"
    direct_source = HERE / "Batch5DirectAudit.lean"
    direct_log = evidence / "batch5-direct-audit.log"
    negative_source = HERE / "Batch5OneDigitNegative.lean"
    negative_log = evidence / "batch5-one-digit-negative.log"
    require(
        direct_source.read_text().startswith("import CryptoResearch.Endosweep.DkExactBatch5\n"),
        "direct audit imports a different module",
    )
    require(
        "'CryptoResearch.Endosweep.DkExactBatch5.gost_gost512_holds' does not depend on any axioms"
        in direct_log.read_text(),
        "batch-five closed arithmetic lemma not audited",
    )
    require(
        "'CryptoResearch.Endosweep.DkExactBatch5.exact_discriminants' depends on axioms: "
        "[propext, Classical.choice, Quot.sound]" in direct_log.read_text(),
        "batch-five direct target audit missing or nonstandard",
    )
    require(
        "gost_gost512.DK = -13385875930186158025707328510606370342278593159599812299594802231247670399530044646980189164659750563715843068347356607340041418160354034446174174038908692"
        in negative_source.read_text(),
        "negative control source was changed",
    )
    require("is false" in negative_log.read_text() and "error:" in negative_log.read_text(),
            "one-digit false claim was not rejected")
    require("Build completed successfully (8976 jobs)." in build_log.read_text(), "main workspace build incomplete")
    require("Built CryptoResearch.Endosweep.DkExactBatch5" in build_log.read_text(), "batch-five module not built")
    match = re.search(r"axiom audit: (\d+) theorem\(s\), all standard axioms only", axiom_log.read_text())
    require(match is not None, "project axiom audit incomplete")
    theorem_count = int(match.group(1))
    require(theorem_count >= 653, "project axiom audit count below prior main plus new theorem")

    log = batch_log.read_text()
    require("error:" not in log.lower(), "Lean batch contains an error")
    dependent = re.findall(r"'([^']+)' depends on axioms:\s*\[([^]]*)\]", log)
    independent = re.findall(r"'([^']+)' does not depend on any axioms", log)
    axiom_sets: dict[str, set[str]] = {}
    for name, content in dependent:
        require(name not in axiom_sets, f"duplicate target: {name}")
        axiom_sets[name] = {item.strip() for item in content.split(",") if item.strip()}
    for name in independent:
        require(name not in axiom_sets, f"duplicate target: {name}")
        axiom_sets[name] = set()
    require(set(axiom_sets) == {name for _, name in main_specs}, "target axiom outputs differ from specs")
    unexpected = {name: sorted(axioms - ALLOWED_AXIOMS)
                  for name, axioms in axiom_sets.items() if not axioms <= ALLOWED_AXIOMS}
    require(not unexpected, f"nonstandard axioms: {unexpected}")
    theorem_type_log = evidence / "current-main-theorem-type.log"
    type_names = re.findall(r"^theorem type passed: ([A-Za-z_][A-Za-z0-9_'.]*)$",
                            theorem_type_log.read_text(), flags=re.MULTILINE)
    require(len(type_names) == len(main_specs) and set(type_names) == set(axiom_sets),
            "one or more target declarations are not audited as theorems")
    type_negative_source = HERE / "CurrentMainTheoremTypeNegative.lean"
    type_negative_log = evidence / "current-main-theorem-type-negative.log"
    require(type_negative_source.read_text() ==
            "import CryptoResearch.Endosweep.DkExactBatch5\n"
            "import Lean\n"
            "open Lean Elab Command\n"
            "run_cmd do\n"
            "  let target := `CryptoResearch.Endosweep.DkExactBatch5.gost_gost512\n"
            "  match (← getEnv).find? target with\n"
            '  | some (.thmInfo _) => logInfo m!"theorem type passed: {target}"\n'
            '  | _ => throwError "requested declaration is not a theorem: {target}"\n',
            "theorem-type negative control source changed")
    require("error: requested declaration is not a theorem: "
            "CryptoResearch.Endosweep.DkExactBatch5.gost_gost512"
            in type_negative_log.read_text(), "known definition was not rejected")

    tracked_formal = git(repo, "ls-files", "formal").splitlines()
    require(len(tracked_formal) == 150, "unexpected tracked formal file count")
    spec_paths = [path for path, _, _ in specs]
    batch_five_source = repo / "research/endosweep_dk_exact_batch5_20261023"
    source_tree = git(repo, "rev-parse", f"{MAIN}:research/endosweep_dk_exact_batch5_20261023")
    require(git(repo, "rev-parse", "HEAD:research/endosweep_dk_exact_batch5_20261023")
            == source_tree, "batch-five source tree differs from named main")
    require(not git(repo, "status", "--porcelain", "--untracked-files=no", "--",
                    "research/endosweep_dk_exact_batch5_20261023"),
            "tracked batch-five source files edited")
    source_manifest = batch_five_source / "SHA256SUMS"
    source_entries = []
    for line in source_manifest.read_text().splitlines():
        digest, relative = line.split("  ", 1)
        require(bool(re.fullmatch(r"[0-9a-f]{64}", digest)), "invalid source manifest digest")
        require(not Path(relative).is_absolute() and ".." not in Path(relative).parts,
                "invalid source manifest path")
        require(sha256(batch_five_source / relative) == digest, f"source hash mismatch: {relative}")
        source_entries.append(relative)
    require(len(source_entries) == 13, "unexpected source archive manifest")
    source_sha_log = evidence / "batch5-source-sha.log"
    source_tests_log = evidence / "batch5-source-tests.log"
    require(source_sha_log.read_text().count(": OK") == 13, "source hash check log incomplete")
    require("17 passed, 1 skipped" in source_tests_log.read_text(), "source test result differs")
    target_receipt_path = evidence / "batch5-target-verification.json"
    target_receipt = json.loads(target_receipt_path.read_text())
    verification = target_receipt.get("verification") or {}
    provenance = target_receipt.get("provenance") or {}
    require(target_receipt.get("schema") == "crypto.autoresearch.formal_verification.v1",
            "unexpected per-target verifier schema")
    require(verification.get("status") == "machine_verified" and
            verification.get("build_passed") is True and
            verification.get("axiom_audit_passed") is True and
            verification.get("forbidden_constructs") == [],
            "batch-five per-target verifier did not pass")
    require(verification.get("theorem_name") ==
            "CryptoResearch.Endosweep.DkExactBatch5.exact_discriminants",
            "per-target verifier checked a different theorem")
    require(target_receipt.get("semantic_review") == {"required": True, "status": "pending"},
            "per-target semantic review status changed")
    require(target_receipt.get("infrastructure_failure") is None,
            "per-target verifier had an infrastructure failure")
    require("target axiom audit passed: CryptoResearch.Endosweep.DkExactBatch5.exact_discriminants"
            in target_receipt.get("audit_log", ""), "requested-theorem audit missing")
    require(git(repo, "rev-parse", f"{provenance['source_commit']}:formal") == formal_tree,
            "per-target verifier's formal tree differs from named main")
    require(git(repo, "rev-parse", f"{provenance['source_commit']}:research/endosweep_dk_exact_batch5_20261023")
            == source_tree, "per-target verifier's source tree differs from named main")
    require(provenance.get("task_spec_sha256") == sha256(
        repo / "formal/targets/endosweep-dk-exact-batch5-discriminants.yaml"),
        "per-target task spec hash differs")
    require(provenance.get("theorem_sha256") == sha256(
        repo / "formal/CryptoResearch/Endosweep/DkExactBatch5.lean"),
        "per-target theorem hash differs")
    require(provenance.get("lean_toolchain_sha256") == sha256(repo / "formal/lean-toolchain")
            and provenance.get("lake_manifest_sha256") == sha256(repo / "formal/lake-manifest.json"),
            "per-target toolchain or dependency manifest hash differs")
    receipt = {
        "schema": "formal-target-declaration-audit-v1",
        "status": "pass",
        "main_commit": MAIN,
        "audited_checkout_head": git(repo, "rev-parse", "HEAD"),
        "formal_tree": formal_tree,
        "batch_five_source_tree": source_tree,
        "scoped_tree_unchanged_from_prior_audit": True,
        "lean_main_toolchain": (repo / "formal/lean-toolchain").read_text().strip(),
        "formal_files_checked": len(tracked_formal),
        "formal_file_manifest_sha256": manifest_hash(repo, tracked_formal),
        "target_specs": len(specs),
        "target_spec_manifest_sha256": manifest_hash(repo, spec_paths),
        "source_paths_checked_against_named_main": len(sources),
        "source_manifest_sha256": manifest_hash(repo, sorted(sources)),
        "unique_task_ids": len(task_ids),
        "unique_claim_ids": len(claim_ids),
        "unique_theorem_names": len(theorem_names),
        "source_status_counts": dict(sorted(source_status_counts.items())),
        "target_theorem_files_present": len(specs),
        "main_target_names_resolved": len(main_specs),
        "main_target_theorems_confirmed": len(type_names),
        "main_targets_with_standard_axioms": len(dependent),
        "main_targets_with_no_axioms": len(independent),
        "main_workspace_build_jobs": 8976,
        "main_workspace_audited_theorems": theorem_count,
        "scoped_target_names_zero_axiom_audited_on_identical_prior_tree": len(scoped_specs),
        "batch_five_source_files_hashed": len(source_entries),
        "batch_five_source_manifest_sha256": sha256(source_manifest),
        "batch_five_source_tests": "17 passed, 1 skipped (cypari2/PARI primality replay unavailable)",
        "batch_five_per_target_verification": "machine_verified; semantic review pending",
        "checker_sha256": sha256(Path(__file__)),
        "batch_lean_source_sha256": sha256(lean_source),
        "theorem_type_lean_source_sha256": sha256(theorem_type_source),
        "theorem_type_negative_lean_source_sha256": sha256(type_negative_source),
        "batch_five_direct_lean_source_sha256": sha256(direct_source),
        "batch_five_negative_lean_source_sha256": sha256(negative_source),
        "evidence_sha256": {p.name: sha256(p) for p in
                            (build_log, batch_log, axiom_log, theorem_type_log, type_negative_log,
                             direct_log, negative_log,
                             source_sha_log, source_tests_log, target_receipt_path)},
        "scope": "named-main formal tree build and target axiom sweep; no independent semantic review or experiment replay",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
