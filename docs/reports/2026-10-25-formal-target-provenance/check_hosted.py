#!/usr/bin/env python3
"""Check archived 87-target hosted Lean receipts against a named main snapshot.

The receipt run is at HOSTED; MAIN identifies the named main snapshot. This
checks exact formal tree and declared-source identity across those commits,
plus every receipt's input hashes and machine-verification fields. It does not
judge claim meaning.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MAIN = "0b38ac1157f777cb4a77d35e53d7ed583c541eb4"
HOSTED = "5998553341fb29d3b9ca1a4c9ac6e58d96ca3ffa"
TREE = "96f334e856c87d397b5db720899d833a75db0352"


def git(*args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    ).stdout


def blob(commit: str, path: str) -> bytes:
    oid = git("rev-parse", f"{commit}:{path}").decode().strip()
    return git("cat-file", "blob", oid)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_directory_mentions(data: bytes, known_ids: list[str]) -> list[str]:
    """Independently scan pinned bytes for whole directory-ID tokens."""
    text = data.decode("utf-8")

    def token_char(char: str) -> bool:
        return ("A" <= char <= "Z" or "a" <= char <= "z"
                or "0" <= char <= "9" or char == "-")

    found = []
    for experiment_id in known_ids:
        start = 0
        while (offset := text.find(experiment_id, start)) != -1:
            end = offset + len(experiment_id)
            if ((offset == 0 or not token_char(text[offset - 1]))
                    and (end == len(text) or not token_char(text[end]))):
                found.append(experiment_id)
                break
            start = offset + 1
    return found


def main() -> None:
    if not __debug__:
        raise RuntimeError("receipt checks require ordinary Python; optimized execution is refused")
    inventory = json.loads((HERE / "provenance.json").read_text())
    corpus = json.loads((HERE / "corpus-pointer-coverage.json").read_text())
    audit = json.loads((HERE / "evidence/hosted-87/receipt-audit.json").read_text())
    rows = inventory["targets"]
    names = {Path(row["target"]).stem for row in rows}
    receipt_dir = HERE / "evidence/hosted-87/receipts"
    receipts = sorted(receipt_dir.glob("*.json"))
    assert inventory["main_commit"] == MAIN and inventory["formal_tree"] == TREE
    assert git("rev-parse", f"{MAIN}:formal").decode().strip() == TREE
    assert git("rev-parse", f"{HOSTED}:formal").decode().strip() == TREE
    assert len(rows) == len(names) == len(receipts) == 87
    assert {p.stem for p in receipts} == names
    sources = sorted({row["source_path"] for row in rows})
    assert len(sources) == 30
    experiment_tree = git("rev-parse", f"{MAIN}:experiments").decode().strip()
    directory_names = git("ls-tree", "-d", "--name-only", f"{MAIN}:experiments").decode().splitlines()
    experiment_ids = sorted(name for name in directory_names if name.startswith("EXP-"))
    assert corpus["schema"] == "crypto.validation.formal_corpus_pointer_coverage.v1"
    assert corpus["main_commit"] == MAIN and corpus["formal_tree"] == TREE
    assert corpus["experiments_tree"] == experiment_tree
    assert corpus["experiment_directory_ids"] == experiment_ids
    assert corpus["experiment_directory_count"] == len(experiment_ids) == 2781
    experiment_set = set(experiment_ids)
    pointers: dict[str, list[str]] = {}
    for row in rows:
        mentions = set(row["exp_directory_ids_in_spec"])
        mentions.update(row["exp_directory_ids_in_source"])
        for experiment_id in sorted(mentions & experiment_set):
            pointers.setdefault(experiment_id, []).append(Path(row["target"]).stem)
    assert corpus["exact_pointer_map"] == dict(sorted(pointers.items()))
    assert corpus["ids_with_exact_target_pointer"] == sorted(pointers)
    assert len(pointers) == 5
    assert corpus["ids_without_exact_target_pointer"] == sorted(experiment_set - pointers.keys())
    assert corpus["targets_with_exact_experiment_pointer"] == len({name for names in pointers.values() for name in names}) == 17
    diff = subprocess.run(
        ["git", "-C", str(ROOT), "diff", "--quiet", HOSTED, MAIN, "--", *sources],
        check=False, capture_output=True,
    )
    assert diff.returncode == 0, "declared source bytes changed since hosted run"
    assert (audit["schema"] == "crypto.validation.formal_receipt_audit.v1"
            and audit["checkout_head"] == HOSTED and audit["formal_tree"] == TREE
            and audit["expected_targets"] == audit["verified"] == 87
            and audit["pending"] == 0 and audit["errors"] == []
            and audit["pending_targets"] == [])
    workspace_hashes: dict[str, tuple[str, str]] = {}
    hashes: dict[str, str] = {}
    verified: list[str] = []
    for row in rows:
        name = Path(row["target"]).stem
        spec_bytes = blob(MAIN, row["spec_path"])
        source_bytes = blob(MAIN, row["source_path"])
        theorem_bytes = blob(MAIN, row["theorem_file"])
        spec = yaml.safe_load(spec_bytes)
        assert digest(spec_bytes) == row["spec_sha256"]
        assert digest(source_bytes) == row["source_sha256"]
        assert digest(theorem_bytes) == row["theorem_sha256"]
        assert (exact_directory_mentions(spec_bytes, experiment_ids)
                == row["exp_directory_ids_in_spec"])
        assert (exact_directory_mentions(source_bytes, experiment_ids)
                == row["exp_directory_ids_in_source"])
        assert spec["task_id"] == row["proof_task_id"]
        assert spec["claim_id"] == row["claim_id"]
        assert spec["source"] == row["source_path"]
        assert spec["workspace"].rstrip("/") + "/" + spec["theorem_file"] == row["theorem_file"]
        workspace = spec["workspace"]
        if workspace not in workspace_hashes:
            workspace_hashes[workspace] = (
                digest(blob(MAIN, workspace + "/lean-toolchain")),
                digest(blob(MAIN, workspace + "/lake-manifest.json")),
            )
        receipt_path = receipt_dir / f"{name}.json"
        raw = receipt_path.read_bytes()
        receipt = json.loads(raw)
        task = receipt["task"]
        result = receipt["verification"]
        provenance = receipt["provenance"]
        assert receipt["schema"] == "crypto.autoresearch.formal_verification.v1"
        assert task["task_id"] == spec["task_id"] == result["task_id"]
        assert task["claim_id"] == spec["claim_id"]
        assert task["theorem_name"] == spec["theorem_name"] == result["theorem_name"]
        assert task["theorem_file"] == spec["theorem_file"] == result["theorem_file"]
        assert task["workspace"] == workspace
        assert provenance["source_commit"] == HOSTED
        assert provenance["task_spec_sha256"] == digest(spec_bytes)
        assert provenance["theorem_sha256"] == digest(theorem_bytes)
        assert provenance["lean_toolchain_sha256"] == workspace_hashes[workspace][0]
        assert provenance["lake_manifest_sha256"] == workspace_hashes[workspace][1]
        assert result["status"] == "machine_verified"
        assert result["build_passed"] is True and result["axiom_audit_passed"] is True
        assert result["forbidden_constructs"] == [] and result["blocking_reason"] is None
        assert receipt["semantic_review"] == {"required": True, "status": "pending"}
        hashes[name] = digest(raw)
        verified.append(name)
    assert audit["receipt_sha256"] == hashes
    assert audit["verified_targets"] == verified
    print("PASS: 87/87 exact hosted machine receipts; formal tree and 30 declared sources match the named main snapshot; semantic review pending")


if __name__ == "__main__":
    main()
