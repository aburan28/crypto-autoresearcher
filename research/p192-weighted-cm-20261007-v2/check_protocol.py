#!/usr/bin/env python3
"""Static checks for the unexecuted P-192 weighted-CM protocol.

This validates protocol arithmetic, links, IDs, and pending state.  It never
enumerates a search box, factors a candidate norm, constructs an isogeny, or
runs a benchmark.
"""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
EXP_PATH = ROOT / "experiments/EXP-SCURVE-1a8daf/amendments/specification.v2.yaml"
RUN_PATH = ROOT / "research/p192-weighted-cm-20261007-v2/run-family.yaml"
DEC_PATH = ROOT / "ledger/decisions/DEC-20261007-0ed467.yaml"
AMENDMENT_PATH = ROOT / "experiments/EXP-SCURVE-1a8daf/amendments/protocol-amendment.v2.yaml"
MANIFEST_PATH = ROOT / "research/p192-weighted-cm-20261007-v2/SHA256SUMS"
RECEIPT_PATH = ROOT / "coordination/p192-weighted-cm-20261007/archives/TASK-20261007-66d44b/snapshot-receipt.json"
PRE_ARCHIVE_HEAD = "5c90176f2156b9e476e3ec16aab2fe05364633af"
YAML_PARSE_COMMAND = (
    "PYTHONDONTWRITEBYTECODE=1 python3 -c \"from pathlib import Path; import yaml; "
    "paths=['experiments/EXP-SCURVE-1a8daf/amendments/protocol-amendment.v2.yaml',"
    "'experiments/EXP-SCURVE-1a8daf/amendments/specification.v2.yaml',"
    "'ledger/corrections/CORR-20261007-f4d600.yaml',"
    "'ledger/decisions/DEC-20261007-0ed467.yaml',"
    "'ledger/handoffs/TASK-20261007-66d44b.yaml',"
    "'research/p192-weighted-cm-20261007-v2/run-family.yaml']; "
    "[yaml.safe_load(Path(p).read_text(encoding='utf-8')) for p in paths]\""
)
V1_PATHS = {
    "experiments/EXP-SCURVE-1a8daf/specification.yaml",
    "ledger/decisions/DEC-20261006-a39750.yaml",
    "ledger/hypotheses/H-SCURVE-ec34c4.yaml",
    "ledger/proposals/IDEA-20261006-767793.yaml",
    "ledger/questions/RQ-SCURVE-42f1a3.yaml",
    "research/p192-weighted-cm-20261006/ARTIFACT_INDEX.md",
    "research/p192-weighted-cm-20261006/README.md",
    "research/p192-weighted-cm-20261006/REPORT.md",
    "research/p192-weighted-cm-20261006/REPORT.pdf",
    "research/p192-weighted-cm-20261006/SHA256SUMS",
    "research/p192-weighted-cm-20261006/check_protocol.py",
    "research/p192-weighted-cm-20261006/protocol-flow.dot",
    "research/p192-weighted-cm-20261006/protocol-flow.png",
    "research/p192-weighted-cm-20261006/protocol-flow.svg",
    "research/p192-weighted-cm-20261006/run-family.yaml",
}
MANIFEST_PAYLOADS = {
    "experiments/EXP-SCURVE-1a8daf/amendments/protocol-amendment.v2.yaml",
    "experiments/EXP-SCURVE-1a8daf/amendments/specification.v2.yaml",
    "ledger/corrections/CORR-20261007-f4d600.yaml",
    "ledger/decisions/DEC-20261007-0ed467.yaml",
    "ledger/handoffs/TASK-20261007-66d44b.yaml",
    "research/p192-weighted-cm-20261007-v2/ARTIFACT_INDEX.md",
    "research/p192-weighted-cm-20261007-v2/README.md",
    "research/p192-weighted-cm-20261007-v2/REPORT.md",
    "research/p192-weighted-cm-20261007-v2/REPORT.pdf",
    "research/p192-weighted-cm-20261007-v2/check_protocol.py",
    "research/p192-weighted-cm-20261007-v2/protocol-flow.dot",
    "research/p192-weighted-cm-20261007-v2/protocol-flow.png",
    "research/p192-weighted-cm-20261007-v2/protocol-flow.svg",
    "research/p192-weighted-cm-20261007-v2/run-family.yaml",
}


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise AssertionError(f"{path}: expected mapping")
    return data


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        assert len(digest) == 64 and relative not in entries
        entries[relative] = digest
    return entries


def git_bytes(*arguments: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *arguments],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise AssertionError(f"git {' '.join(arguments)}: {detail}")
    return result.stdout


def git_commit(reference: str) -> str:
    return git_bytes("rev-parse", "--verify", f"{reference}^{{commit}}").decode("ascii").strip()


def git_changed_paths(commit: str) -> set[str]:
    output = git_bytes(
        "diff-tree", "--no-commit-id", "--no-renames", "--name-only", "-r", commit
    )
    return {line for line in output.decode("utf-8").splitlines() if line}


def git_blob(reference: str, relative: str) -> bytes:
    return git_bytes("show", f"{reference}:{relative}")


def count_pairs(v_max: int, x_max_inclusive: int) -> int:
    # t is odd.  Half the v values accept X/2+1 even x values and half accept
    # X/2 odd x values when V and X are even.
    assert v_max % 2 == 0 and x_max_inclusive % 2 == 0
    return (v_max // 2) * (x_max_inclusive + 1)


def main() -> int:
    exp = load(EXP_PATH)["experiment"]
    family = load(RUN_PATH)
    decision = load(DEC_PATH)["coordinator_decision"]
    amendment = load(AMENDMENT_PATH)["protocol_amendment"]

    assert exp["id"] == "EXP-SCURVE-1a8daf"
    assert exp["version"] == 2
    assert exp["amendment_decision"] == "DEC-20261007-0ed467"
    assert exp["amendment_path"] == str(AMENDMENT_PATH.relative_to(ROOT))
    assert exp["scientific_status"] == "not_started"
    assert exp["result_status"] == "no_result"
    assert exp["execution_authorized"] is False
    assert exp["approved_by"] == "coordinator"
    assert decision["execution_authorized"] is False
    assert decision["protocol_version"] == exp["version"]
    assert decision["knowledge_promotion"]["promoted"] == []
    assert decision["amendment_path"] == str(AMENDMENT_PATH.relative_to(ROOT))
    assert amendment["approval_decision"] == decision["id"]
    assert exp["approval_decision"] == decision["id"]
    assert amendment["version_from"] == 1
    assert amendment["version_to"] == 2
    assert amendment["confirmatory_status"] == "reset"
    assert amendment["affected_runs"] == []
    assert amendment["execution_authorized"] is False
    assert amendment["scientific_run_performed"] is False
    assert amendment["scientific_results"] == []
    v1 = amendment["version_1_binding"]
    assert v1["commit"] == "4b9207ea3751de5b1986e28b627ae4476f4ead4f"
    for path_key, hash_key in (
        ("specification_path", "specification_sha256"),
        ("run_family_path", "run_family_sha256"),
        ("report_path", "report_sha256"),
    ):
        bound_path = ROOT / v1[path_key]
        assert bound_path.is_file(), v1[path_key]
        assert sha256_file(bound_path) == v1[hash_key]
    v2 = amendment["version_2_binding"]
    assert v2["specification_path"] == str(EXP_PATH.relative_to(ROOT))
    assert v2["run_family_path"] == str(RUN_PATH.relative_to(ROOT))
    assert v2["report_path"] == "research/p192-weighted-cm-20261007-v2/REPORT.md"

    curve = exp["inputs"]["curve"]
    order = exp["inputs"]["cm_order"]
    p = int(curve["p"])
    a = int(curve["a"])
    n = int(curve["n"])
    t = int(curve["trace_t"])
    d = int(order["discriminant_D"])
    c = int(order["C"])
    assert a == p - 3
    assert n == p + 1 - t
    assert d == t * t - 4 * p
    assert d == -5 * 11 * 31 * c
    assert d % 4 == 1 and d % 8 == 5 and d < -4
    lower = (abs(d) + 3) // 4
    declared = int(exp["centered_norm_search"]["algebra"]
                   ["non_scalar_lower_bound"]["value"])
    assert declared == lower

    boxes = exp["centered_norm_search"]["boxes"]
    assert [box["canonical_shell_id"] for box in boxes] == [
        "BOX-0", "BOX-1-minus-BOX-0", "BOX-2-minus-BOX-1"
    ]
    prior = 0
    for box in boxes:
        count = count_pairs(int(box["v_max"]), int(box["x_max"]))
        assert count == int(box["raw_pair_count"])
        shell = int(box.get("shell_raw_pair_count", count))
        assert shell == count - prior
        prior = count

    reference = exp["centered_norm_search"]["scalar_sieve_reference_box"]
    assert reference["canonical_shell_id"] == "REF-0"
    reference_count = count_pairs(int(reference["v_max"]), int(reference["x_max"]))
    assert reference_count == int(reference["raw_pair_count"]) == 1025

    runs = family["runs"]
    assert family["family_status"] == "pending_not_executed"
    assert family["dispatch_status"] == "blocked_pending_implementation_and_fresh_decision"
    assert family["protocol_version"] == 2
    assert family["protocol_amendment_decision"] == "DEC-20261007-0ed467"
    assert family["protocol_amendment_path"] == str(AMENDMENT_PATH.relative_to(ROOT))
    assert family["scientific_results"] == []
    assert len(runs) == exp["planned_run_family"]["run_count"] == 8
    labels = [run["planned_run_label"] for run in runs]
    assert len(labels) == len(set(labels))
    assert all(run["status"] == "pending_not_executed" for run in runs)
    seen: set[str] = set()
    for expected_ordinal, run in enumerate(runs, 1):
        assert run["ordinal"] == expected_ordinal
        predecessor = run["predecessor"]
        if predecessor is not None:
            assert predecessor["planned_run_label"] in seen
        seen.add(run["planned_run_label"])

    assert family["native_source_pr"] == "https://github.com/aburan28/crypto/pull/1507"
    assert family["archive_reference_pr"] == "https://github.com/aburan28/crypto-autoresearcher/pull/1942"
    assert exp["budget"]["maximum_runs"] == 8
    assert exp["factor_bases_and_smoothness"]["algebraic_sieve_base"]["bound_inclusive"] == 65521
    mappable = exp["factor_bases_and_smoothness"]["mappable_base"]
    assert mappable["bound_inclusive"] == 113
    assert mappable["exact_members"] == [5, 11, 13, 23, 31, 37, 43, 73, 89, 101, 103, 107, 113]
    assert mappable["directed_orientation_count"] == 23
    demonstrated = mappable["current_demonstrated_kernel_codomain_frontier"]
    assert demonstrated["maximum_ell"] == 43
    assert demonstrated["exact_members"] == [5, 11, 13, 23, 31, 37, 43]
    assert demonstrated["directed_orientation_count"] == 11
    frontier_evidence = demonstrated["evidence"]
    assert frontier_evidence["artifact_commit"] == "aea4dbb0983a37f6463fdbde96e6884871586357"
    assert frontier_evidence["reviewed_descendant_commit"] == "315c7b417305db4f34ad01cb07c18ca2c55181ee"
    assert frontier_evidence["isogeny_routes_sha256"] == "719846b30348a718d4369c189be74b2d7e52b8de9eb7f0be7f591768183eeba6"
    admitted = mappable["admitted_map_support_at_protocol_freeze"]
    assert admitted["exact_members"] == []
    assert admitted["directed_orientation_count"] == 0
    assert exp["factor_bases_and_smoothness"]["large_prime_rules"]["bound_inclusive"] == 2147483647

    encoding = exp["relation_encoding_and_recombination"]
    fb_schema = encoding["factor_base_manifest_schema"]
    assert fb_schema["schema_value"] == "p192-wcm-factor-base-v1"
    assert json.loads(fb_schema["first_entry_fixture"]) == {
        "ell": 5,
        "kind": 1,
        "kronecker": 0,
        "positive_root_index": 0,
        "roots": [2],
    }
    assert "P192-WCM-FACT-v1" in encoding["factorization_certificate_bytes"]
    assert "candidate_certificate_sha256" in encoding["factorization_certificate_bytes"]
    assert "p192-wcm-coordinate-manifest-v1" in encoding["coordinate_manifest_schema"]
    assert "p192-wcm-kernel-proof-v1" in encoding["kernel_certificate_schema"]
    assert "p192-wcm-map-support-v1" in encoding["map_support_manifest_schema"]
    for run in runs[:6]:
        assert run["role"] == "composite_producer_and_isolated_verifier"
        assert run["independent_verifier_argv_template"][0] == "p192_weighted_cm_verify"
        assert "independent-verification.json" in run["required_outputs"]
        assert "independent-verifier-receipt.json" in run["required_outputs"]
    preflight = runs[0]
    assert "REF-0" in preflight["argv_template"]
    assert "factor-base.sha256" in preflight["required_outputs"]
    optimize = runs[4]
    assert "BOX0_DIR/manifest.yaml,BOX1_DIR/manifest.yaml,BOX2_DIR/manifest.yaml" in optimize["argv_template"]
    assert "--forbid-cost-inputs" in optimize["argv_template"]
    assert "0x5031393257434d31" in optimize["argv_template"]
    assert "lp-coordinate-manifest.json" in optimize["required_outputs"]
    assert "high-column-coordinate-manifest.json" in optimize["required_outputs"]
    assert "high-column-coordinate-manifest.sha256" in optimize["required_outputs"]
    assert "structural-candidate-panel.json" in optimize["required_outputs"]
    assert "structural-candidate-panel.sha256" in optimize["required_outputs"]
    for shell_run in runs[1:4]:
        assert "checkpoint-chain.jsonl" in shell_run["required_outputs"]
    checkpoint = exp["factor_bases_and_smoothness"]["checkpoint_schema"]
    assert "seen=next_candidate_index" in checkpoint
    assert "seen=duplicate+primitive" in checkpoint
    assert "protocol_commit is the final admitted protocol Git commit" in checkpoint
    maps = runs[5]
    assert maps["predecessor"]["artifact"] == "structural-candidate-panel.json"
    assert "--require-complete-panel-dispositions" in maps["argv_template"]
    assert "map-attempt-dispositions.jsonl" in maps["required_outputs"]
    assert "map-attempt-evidence.jsonl" in maps["required_outputs"]
    assert "realized-panel-ranking.json" in maps["required_outputs"]
    assert "selected-vectors.json" in maps["required_outputs"]
    assert "map-support.json" in maps["required_outputs"]
    assert "map-support.sha256" in maps["required_outputs"]
    assert "generator-subgroup-certificates.jsonl" in maps["required_outputs"]
    holdout = next(run for run in runs if run["planned_run_label"] == "P192-WCM-HOLDOUT")
    assert holdout["role"] == "blocked_pending_exact_consumer_amendment"
    assert holdout["argv_template"] is None
    assert holdout["independent_verifier_argv_template"] is None
    assert any("p192-interval-bsgs" in item for item in holdout["required_template_bindings"])
    assert any("no-speed-claim" in item for item in holdout["required_template_bindings"])
    assert any("5782965481073003825" in item for item in holdout["required_template_bindings"])
    assert "planted-point-subgroup-certificates.jsonl" in holdout["required_outputs"]
    replication = next(run for run in runs if run["planned_run_label"] == "P192-WCM-REPLICATION")
    assert replication["role"] == "blocked_pending_exact_consumer_amendment"
    assert replication["argv_template"] is None
    assert replication["independent_verifier_argv_template"] is None
    assert any("exactly two independent" in item for item in replication["required_template_bindings"])
    assert any("two distinct isolated" in item for item in replication["required_template_bindings"])
    assert "replication-instance-1-receipt.json" in replication["required_outputs"]
    assert "replication-instance-2-receipt.json" in replication["required_outputs"]

    for relative in (
        "ledger/questions/RQ-SCURVE-42f1a3.yaml",
        "ledger/proposals/IDEA-20261006-767793.yaml",
        "ledger/hypotheses/H-SCURVE-ec34c4.yaml",
        "ledger/decisions/DEC-20261007-0ed467.yaml",
        "experiments/EXP-SCURVE-1a8daf/amendments/protocol-amendment.v2.yaml",
        "experiments/EXP-SCURVE-1a8daf/amendments/specification.v2.yaml",
        "research/p192-weighted-cm-20261007-v2/run-family.yaml",
        "research/p192-weighted-cm-20261007-v2/REPORT.md",
        "research/p192-weighted-cm-20261007-v2/protocol-flow.dot",
        "research/p192-weighted-cm-20261007-v2/protocol-flow.svg",
        "research/p192-weighted-cm-20261007-v2/REPORT.pdf",
    ):
        assert (ROOT / relative).is_file(), relative

    manifest = load_manifest(MANIFEST_PATH)
    assert set(manifest) == MANIFEST_PAYLOADS
    for relative, expected_hash in manifest.items():
        assert sha256_file(ROOT / relative) == expected_hash, relative

    # The receipt is necessarily written after the archive commit it binds.
    # It is absent during the pre-commit check and mandatory in the published
    # two-commit branch, where the same checker validates its content binding.
    if RECEIPT_PATH.exists():
        receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        archived = MANIFEST_PAYLOADS | {str(MANIFEST_PATH.relative_to(ROOT))}
        receipt_relative = str(RECEIPT_PATH.relative_to(ROOT))
        assert receipt["task_id"] == "TASK-20261007-66d44b"
        assert receipt["experiment_id"] == "EXP-SCURVE-1a8daf"
        assert receipt["decision_id"] == "DEC-20261007-0ed467"
        assert receipt["correction_id"] == "CORR-20261007-f4d600"
        assert receipt["kind"] == "snapshot"
        assert receipt["binding_mode"] == "commit"
        assert receipt["status"] == "post_commit_verified"
        assert isinstance(receipt["commit_sha"], str) and len(receipt["commit_sha"]) == 40
        assert isinstance(receipt["parent_sha"], str) and len(receipt["parent_sha"]) == 40
        assert set(receipt["archive_artifact_paths"]) == archived
        assert set(receipt["changed_paths"]) == archived
        assert set(receipt["path_sha256"]) == archived
        assert set(receipt["path_size_bytes"]) == archived
        base_sync = receipt["base_sync"]
        assert base_sync["remote_ref"] == "origin/main"
        assert isinstance(base_sync["remote_main_sha"], str) and len(base_sync["remote_main_sha"]) == 40
        assert isinstance(base_sync["local_origin_main_sha"], str) and len(base_sync["local_origin_main_sha"]) == 40
        assert base_sync["remote_main_sha"] == base_sync["local_origin_main_sha"]
        assert base_sync["sync_method"] == "git_fetch_and_merge"
        assert base_sync["remote_query_command"] == "git ls-remote origin refs/heads/main"
        assert base_sync["remote_query_exit_status"] == 0
        assert base_sync["fetch_command"] == "git fetch origin main"
        assert base_sync["fetch_exit_status"] == 0
        assert base_sync["merge_command"] == "git merge --no-edit origin/main"
        assert base_sync["merge_exit_status"] == 0
        assert base_sync["remote_query_limitation"] is None
        synced_main = git_commit(base_sync["local_origin_main_sha"])
        assert synced_main == base_sync["local_origin_main_sha"]
        assert base_sync["pre_sync_head"] == "4b9207ea3751de5b1986e28b627ae4476f4ead4f"
        assert base_sync["merge_required"] is True
        assert base_sync["merge_outcome"] == "merged_origin_main"
        assert receipt["parent_sha"] == PRE_ARCHIVE_HEAD
        assert git_commit(base_sync["post_sync_head"]) == PRE_ARCHIVE_HEAD
        sync_parents = git_bytes(
            "show", "-s", "--format=%P", PRE_ARCHIVE_HEAD
        ).decode("ascii").split()
        assert sync_parents == [base_sync["pre_sync_head"], synced_main]
        assert subprocess.run(
            ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", synced_main, receipt["parent_sha"]],
            check=False,
        ).returncode == 0
        assert base_sync["merge_conflicts"] == []
        assert receipt["runs_launched"] == 0
        assert receipt["scientific_run_performed"] is False
        assert receipt["scientific_results"] == []
        assert receipt["no_scientific_result"] is True
        validation = receipt["validation"]
        assert validation["yaml_parse"]["status"] == "PASS"
        assert validation["yaml_parse"]["exit_status"] == 0
        assert validation["yaml_parse"]["command"] == YAML_PARSE_COMMAND
        assert validation["protocol_static_check"]["status"] == "PASS"
        assert validation["protocol_static_check"]["exit_status"] == 0
        assert validation["protocol_static_check"]["command"] == "PYTHONDONTWRITEBYTECODE=1 python3 research/p192-weighted-cm-20261007-v2/check_protocol.py"
        assert validation["sha256sums"]["status"] == "PASS"
        assert validation["sha256sums"]["exit_status"] == 0
        assert validation["sha256sums"]["command"] == "sha256sum -c research/p192-weighted-cm-20261007-v2/SHA256SUMS"
        ledger_validation = validation["ledger_sparse_worktree"]
        assert ledger_validation["command"] == "python3 tools/validate_ledger.py"
        assert ledger_validation["environment"] == {"PYTHONDONTWRITEBYTECODE": "1"}
        assert isinstance(ledger_validation["exit_status"], int)
        assert ledger_validation["exit_status"] != 0
        assert isinstance(ledger_validation["error_count"], int)
        assert ledger_validation["error_count"] > 0
        assert isinstance(ledger_validation["output_line_count"], int)
        assert ledger_validation["output_line_count"] > 0
        assert isinstance(ledger_validation["output_sha256"], str)
        digest = ledger_validation["output_sha256"]
        assert len(digest) == 64 and digest == digest.lower()
        assert all(character in "0123456789abcdef" for character in digest)
        assert isinstance(ledger_validation["limitation"], str) and ledger_validation["limitation"]
        assert ledger_validation["payload_attributable_errors"] == []
        assert ledger_validation["complete_checkout_pass_claimed"] is False

        archive_commit = git_commit(receipt["commit_sha"])
        assert archive_commit == receipt["commit_sha"]
        assert git_commit(receipt["parent_sha"]) == receipt["parent_sha"]
        parents = git_bytes("show", "-s", "--format=%P", archive_commit).decode("ascii").split()
        assert parents and parents[0] == receipt["parent_sha"]
        assert git_changed_paths(archive_commit) == archived
        assert subprocess.run(
            ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", archive_commit, "HEAD"],
            check=False,
        ).returncode == 0
        archive_message = git_bytes("log", "-1", "--format=%B", archive_commit).decode(
            "utf-8", "replace"
        )
        for identifier in (
            "TASK-20261007-66d44b",
            "RQ-SCURVE-42f1a3",
            "IDEA-20261006-767793",
            "H-SCURVE-ec34c4",
            "EXP-SCURVE-1a8daf",
            "DEC-20261006-a39750",
            "DEC-20261007-0ed467",
            "CORR-20261007-f4d600",
        ):
            assert identifier in archive_message
        for relative in archived:
            blob = git_blob(archive_commit, relative)
            assert hashlib.sha256(blob).hexdigest() == receipt["path_sha256"][relative], relative
            assert len(blob) == receipt["path_size_bytes"][relative]
            assert (ROOT / relative).read_bytes() == blob, relative

        v1_receipt = receipt["v1_binding"]
        v1_commit = git_commit(v1_receipt["commit"])
        assert v1_commit == "4b9207ea3751de5b1986e28b627ae4476f4ead4f"
        assert subprocess.run(
            ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", v1_commit, archive_commit],
            check=False,
        ).returncode == 0
        assert v1_receipt["ancestor_of_archive_commit"] is True
        assert set(receipt["v1_paths"]) == V1_PATHS
        assert set(v1_receipt["path_sha256"]) == V1_PATHS
        for relative, expected_hash in v1_receipt["path_sha256"].items():
            v1_blob = git_blob(v1_commit, relative)
            archive_blob = git_blob(archive_commit, relative)
            assert v1_blob == archive_blob, relative
            assert hashlib.sha256(v1_blob).hexdigest() == expected_hash, relative

        receipt_commit = git_bytes(
            "log", "-1", "--format=%H", "--", receipt_relative
        ).decode("ascii").strip()
        assert git_commit(receipt_commit) == receipt_commit
        receipt_parents = git_bytes(
            "show", "-s", "--format=%P", receipt_commit
        ).decode("ascii").split()
        assert receipt_parents and receipt_parents[0] == archive_commit
        assert git_changed_paths(receipt_commit) == {receipt_relative}
        assert git_blob(receipt_commit, receipt_relative) == RECEIPT_PATH.read_bytes()
        assert subprocess.run(
            ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", receipt_commit, "HEAD"],
            check=False,
        ).returncode == 0
    else:
        # Receipt absence is valid only while preparing the exact first archive
        # commit.  Once HEAD advances, publishing without the receipt-only
        # second commit is a hard failure.
        assert git_commit("HEAD") == PRE_ARCHIVE_HEAD

    print("PASS: protocol arithmetic, IDs, links, and all-pending state")
    print("PASS: no scientific result is recorded")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
