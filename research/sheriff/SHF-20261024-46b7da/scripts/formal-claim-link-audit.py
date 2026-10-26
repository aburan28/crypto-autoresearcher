#!/usr/bin/env python3
"""Bind 84 Lean target receipts to pinned claim sources and exact IDs.

This checks file identity and explicit textual links. It does not prove that
the theorem models a run, that the run executed, or that timing was reproduced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
HEAD = "4647b1d072ffaebbbb85127bdc60343bbd372ec4"
FORMAL_TREE = "0dd2764cff0c0ec05c4938f12b334ec60376d9ff"
OUTPUT = HERE / "formal-claim-link-audit.json"
EXP_TOKEN = re.compile(r"EXP-[A-Za-z0-9-]+")
RUN_TOKEN = re.compile(r"RUN-[A-Za-z0-9-]+")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(checkout: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=checkout)


def blob(checkout: Path, path: str) -> bytes:
    return git(checkout, "show", f"{HEAD}:{path}")


def paths(checkout: Path, *args: str) -> list[str]:
    return git(checkout, "ls-tree", *args).decode().splitlines()


def authoritative_run_manifest(checkout: Path, run_id: str, all_paths: list[str]) -> dict:
    candidates = {
        path for path in all_paths
        if "/runs/" in path and path.endswith(("/manifest.yaml", "/manifest.json"))
        and run_id in path
    }
    grep = git(checkout, "grep", "-l", "-F", run_id, HEAD, "--", "experiments")
    candidates.update(
        value.split(":", 1)[1]
        for value in grep.decode().splitlines()
        if "/runs/" in value and value.endswith(("/manifest.yaml", "/manifest.json"))
    )
    matches = []
    for path in sorted(candidates):
        raw = blob(checkout, path)
        document = yaml.safe_load(raw)
        declared = document.get("run", {}).get("id") if isinstance(document.get("run"), dict) else document.get("run_id")
        if declared == run_id or run_id in path:
            matches.append({"path": path, "sha256": sha(raw), "declared_id": declared})
    assert len(matches) == 1, (run_id, matches)
    return matches[0]


def build(checkout: Path) -> dict:
    assert git(checkout, "rev-parse", f"{HEAD}:formal").decode().strip() == FORMAL_TREE
    all_paths = paths(checkout, "-r", "--name-only", HEAD, "--", "experiments")
    exp_ids = {
        name for name in paths(checkout, "-d", "--name-only", f"{HEAD}:experiments")
        if name.startswith("EXP-")
    }
    target_paths = [
        path for path in paths(checkout, "-r", "--name-only", HEAD, "--", "formal/targets")
        if path.endswith(".yaml")
    ]
    assert len(target_paths) == 84
    source_cache: dict[str, bytes] = {}
    rows = []
    for target_path in sorted(target_paths):
        target = Path(target_path).stem
        spec_raw = blob(checkout, target_path)
        spec = yaml.safe_load(spec_raw)
        assert spec["schema"] == "crypto.autoresearch.formal_task.v1"
        source_path = spec["source"]
        if source_path not in source_cache:
            source_cache[source_path] = blob(checkout, source_path)
        source_raw = source_cache[source_path]
        source_exp_id = source_path.split("/", 2)[1] if source_path.startswith("experiments/") else None
        assert source_exp_id is None or source_exp_id in exp_ids
        theorem_path = f"{spec['workspace'].rstrip('/')}/{spec['theorem_file']}"
        theorem_raw = blob(checkout, theorem_path)
        receipt_path = HERE / "formal-sweep" / "receipts" / f"{target}.json"
        receipt_raw = receipt_path.read_bytes()
        receipt = json.loads(receipt_raw)
        verification = receipt["verification"]
        provenance = receipt["provenance"]
        assert receipt["task"]["task_id"] == spec["task_id"]
        assert receipt["task"]["theorem_name"] == spec["theorem_name"]
        assert verification["status"] == "machine_verified"
        assert verification["build_passed"] and verification["axiom_audit_passed"]
        assert not verification["forbidden_constructs"]
        assert provenance["task_spec_sha256"] == sha(spec_raw)
        assert provenance["theorem_sha256"] == sha(theorem_raw)
        spec_text = spec_raw.decode(errors="replace")
        source_text = source_raw.decode(errors="replace")
        rows.append({
            "target": target,
            "claim_id": spec["claim_id"],
            "source_status": spec["source_status"],
            "target_spec_sha256": sha(spec_raw),
            "theorem_name": spec["theorem_name"],
            "theorem_file": theorem_path,
            "theorem_sha256": sha(theorem_raw),
            "verification_receipt_sha256": sha(receipt_raw),
            "source": source_path,
            "source_sha256": sha(source_raw),
            "exp_id_from_source_path": source_exp_id,
            "exp_ids_in_spec": sorted(set(EXP_TOKEN.findall(spec_text)) & exp_ids),
            "exp_ids_in_source": sorted(set(EXP_TOKEN.findall(source_text)) & exp_ids),
            "run_ids_in_spec": sorted(set(RUN_TOKEN.findall(spec_text))),
            "run_ids_in_source": sorted(set(RUN_TOKEN.findall(source_text))),
            "proof_scope": "machine-checked declaration; semantic fit and execution remain separate obligations",
        })
    assert len(rows) == 84 and len({row["target"] for row in rows}) == 84
    explicit_exp = sorted({item for row in rows for item in row["exp_ids_in_spec"] + row["exp_ids_in_source"] + ([row["exp_id_from_source_path"]] if row["exp_id_from_source_path"] else [])})
    explicit_run = sorted({item for row in rows for item in row["run_ids_in_spec"] + row["run_ids_in_source"]})
    manifests = {run_id: authoritative_run_manifest(checkout, run_id, all_paths) for run_id in explicit_run}
    return {
        "schema": "sheriff.formal_claim_link_audit/v1",
        "pinned_auto_head": HEAD,
        "formal_tree": FORMAL_TREE,
        "experiment_directories_with_exp_id": len(exp_ids),
        "target_count": len(rows),
        "unique_source_files": len(source_cache),
        "targets_with_exp_id_in_spec": sum(bool(row["exp_ids_in_spec"]) for row in rows),
        "targets_with_exp_id_in_source": sum(bool(row["exp_ids_in_source"]) for row in rows),
        "targets_with_experiment_source_path": sum(bool(row["exp_id_from_source_path"]) for row in rows),
        "targets_with_run_id_in_spec": sum(bool(row["run_ids_in_spec"]) for row in rows),
        "targets_with_run_id_in_source": sum(bool(row["run_ids_in_source"]) for row in rows),
        "explicit_exp_ids": explicit_exp,
        "explicit_run_ids": explicit_run,
        "run_manifests": manifests,
        "rows": rows,
        "interpretation": "Exact textual identifiers and source hashes show pointers only. They do not establish theorem-to-run semantic fidelity, execution proof, timing, or coverage of unreferenced experiments.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--auto-checkout", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(args.auto_checkout)
    if args.check:
        assert json.loads(OUTPUT.read_text()) == result
        print("84 pinned target/source/run links match")
    else:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(OUTPUT)


if __name__ == "__main__":
    main()
