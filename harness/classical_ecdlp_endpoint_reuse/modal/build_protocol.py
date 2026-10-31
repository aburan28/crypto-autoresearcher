#!/usr/bin/env python3
"""Prepare the additive Modal VM route of the existing six-arm experiment.

This command never freezes, approves, draws inputs, runs a solver, or calls an
account API. Without --draft it requires an observed Modal image receipt and
its exact build-info bytes. Fresh confirmation inputs are deliberately absent:
the existing custodian draws them only after source and protocol are committed
and frozen. The later admission plan binds those resulting public inputs.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
PREFIX = "harness/classical_ecdlp_endpoint_reuse"
ORIGINAL = "experiments/EXP-ECDLP-2b4ff1/protocol.json"
SUCCESSOR = "experiments/EXP-ECDLP-2b4ff1/protocol.modal-vm.v1.json"
ORIGINAL_SHA256 = "44f9f136c6ff86691ddf2ff2c9f0c6eef3c42cd1ba209b5736b8aac733ff9a74"
NATIVE_SOURCE_A = "fe01ccd832832488c58abeef17548b0a8db6035f"
ANALYSIS_SHA256 = "9e1293af171167065d966366cbc41d29457a9bd3b4be95e166870ddc44293abf"
ARMS = ["static_small", "static_full", "static_filled", "harvest", "harvest_disabled", "rho_reference"]
SHA = re.compile(r"[0-9a-f]{64}\Z")
COMMIT = re.compile(r"[0-9a-f]{40}\Z")
RECEIPT_SCHEMA = "classical.ecdlp.endpoint-reuse.modal-image-receipt/v1"
PROVIDER_RECORD_FIELDS = ["modal.app_id", "modal.sandbox_id", "modal.image_id", "modal.runtime", "modal.block_network", "uid", "gid", "source_b_revision", "build_info_sha256", "input_bundle_sha256", "output_archive_sha256"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def validate_receipt(receipt: dict, build_info: dict, build_info_sha256: str) -> None:
    if receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("completed") is not True:
        raise ValueError("Completed actual Modal image receipt required")
    for key in ("source_a_revision", "source_b_revision"):
        if not isinstance(receipt.get(key), str) or not COMMIT.fullmatch(receipt[key]):
            raise ValueError(f"Actual full Git commit required: {key}")
    if receipt.get("source_revision") != receipt["source_a_revision"]:
        raise ValueError("source_revision must remain the native source A")
    if receipt["source_a_revision"] != NATIVE_SOURCE_A:
        raise ValueError("Provider-only correction must preserve the registered native source A")
    for key in ("source_a_tree_sha256", "source_b_tree_sha256", "adapter_manifest_sha256",
                "context_manifest_sha256", "build_info_sha256", "binary_sha256"):
        if not isinstance(receipt.get(key), str) or not SHA.fullmatch(receipt[key]):
            raise ValueError(f"Observed SHA-256 required: {key}")
    for key, prefix in (("app_id", "ap-"), ("image_id", "im-")):
        if not isinstance(receipt.get(key), str) or not re.fullmatch(re.escape(prefix) + r"[A-Za-z0-9]+", receipt[key]):
            raise ValueError(f"Actual Modal object ID required: {key}")
    if receipt.get("modal_image_id", receipt["image_id"]) != receipt["image_id"]:
        raise ValueError("Conflicting Modal image IDs")
    if receipt.get("runtime") != "vm" or receipt.get("block_network") is not True:
        raise ValueError("Only a network-blocked Modal VM route is admitted")
    if receipt.get("requested_cpu") != [2, 2] or receipt.get("requested_memory_mib") != [12288, 12288]:
        raise ValueError("Resource request/limits must be two physical cores and 12288 MiB")
    if receipt["build_info_sha256"] != build_info_sha256:
        raise ValueError("Build-info bytes differ from the observed receipt")
    if (build_info.get("schema") != "classical.ecdlp.endpoint-reuse.image-build/v1"
            or build_info.get("confirmation_inputs_baked") is not False
            or build_info.get("scientific_workload_executed") is not False):
        raise ValueError("Exact code-only build-info schema and no-data flags required")
    if build_info.get("source_and_public_input_sha256", {}).get("protocol/analysis.py") != ANALYSIS_SHA256:
        raise ValueError("Packaged analysis must preserve the original committed analysis bytes")
    if build_info.get("source_revision") != receipt["source_a_revision"] or build_info.get("binary_sha256") != receipt["binary_sha256"]:
        raise ValueError("Native source/binary pins differ between receipt and build-info")
    compilers = receipt.get("compiler_executable_sha256")
    if not isinstance(compilers, dict) or not compilers or any(not isinstance(v, str) or not SHA.fullmatch(v) for v in compilers.values()):
        raise ValueError("Observed compiler executable hashes required")
    probe = receipt.get("software_probe")
    if not isinstance(probe, dict) or probe.get("returncode") != 0:
        raise ValueError("Successful code-only image software probe required")


def scientific_projection(protocol: dict) -> dict:
    """The exact original science, excluding the narrowly mutable route fields."""
    data = copy.deepcopy(protocol)
    for key in ("version", "created", "authors", "freeze", "amendments", "literature"):
        data.pop(key, None)
    for arm in data["arms"]:
        for key in ("commit", "binary_sha256"):
            arm["instrument"].pop(key, None)
    for key in ("backend", "queue"):
        data["execution"].pop(key, None)
    data["execution"]["placement"] = {key: data["execution"]["placement"][key]
                                       for key in ("maximum_active_cpus", "memory_gib", "child_timeout_seconds")}
    data["measurement"]["record"] = [key for key in data["measurement"]["record"] if key not in PROVIDER_RECORD_FIELDS]
    data["extensions"].pop("modal_vm_route", None)
    for factor in data["variable_ledger"]["factors"]:
        if factor["name"] == "source_build_binary":
            factor.pop("how")
    data["analysis_plan"].pop("frozen_before_data")
    return data


def build(original: dict, receipt: dict | None, *, receipt_sha256: str | None,
          receipt_binding_path: str, build_info_binding_path: str,
          correction_id: str, draft: bool) -> dict:
    if original.get("protocol_id") != "EXP-ECDLP-2b4ff1" or [a["id"] for a in original["arms"]] != ARMS:
        raise ValueError("This is only a provider correction of existing EXP-ECDLP-2b4ff1")
    if original.get("freeze", {}).get("status") != "draft":
        raise ValueError("Expected the preserved original review-required draft")
    if not re.fullmatch(r"DEC-\d{8}-[0-9a-f]{6}", correction_id):
        raise ValueError("Allocator-checked corrective decision ID required")
    data = copy.deepcopy(original)
    data["version"] = 2
    data["created"] = "2026-10-27"
    source_a = receipt["source_a_revision"] if receipt else None
    source_b = receipt["source_b_revision"] if receipt else None
    binary = receipt["binary_sha256"] if receipt else None
    for arm in data["arms"]:
        arm["instrument"].update(commit=source_a, binary_sha256=binary, image_digest=None)
    for factor in data["variable_ledger"]["factors"]:
        if factor["name"] == "source_build_binary":
            factor["how"] = "One native source-A executable for all six arms, actual binary/build-info and allowlisted source trees pinned before freeze; independently source-pinned Modal adapter B and actual Modal Image ID verified at launch. A Modal Image ID is not an OCI registry digest."
    # L2 is retained as the unachieved clock qualification threshold. Its
    # presence does not attest the VM or permit a clock under this route.
    data["measurement"]["record"] += PROVIDER_RECORD_FIELDS
    placement = {
        "required": "One source-bound CPU-only Modal VM Sandbox with its own guest kernel and blocked workload network; count-only primary admission. Physical-host exclusivity, whole-core placement and L2 are unknown and unclaimed. Every child clock is wall_valid=false.",
        "runtime": "vm", "block_network": True,
        "maximum_active_cpus": 4, "requested_cpu_physical_cores": [2, 2],
        "requested_memory_mib": [12288, 12288], "memory_gib": 12,
        "maximum_workers": 1, "native_threads": 1, "workload_uid": 1000,
        "child_timeout_seconds": 3600, "global_timeout_seconds": 3600,
        "sandbox_timeout_seconds": 5400, "command_timeout_seconds": 4200,
        "staging_timeout_seconds": 600, "collection_grace_seconds": 600,
        "all_clocks_wall_valid": False,
        "dedicated_physical_host_attested": False, "l2_attested": False,
        "app_id": receipt["app_id"] if receipt else None,
        "image_id": receipt["image_id"] if receipt else None,
        "app_name": receipt.get("app_name") if receipt else None,
        "environment_name": receipt.get("environment_name") if receipt else None,
        "sandbox_id_rule": "Observe and retain the actual sb-* ID after one create; no prospective Sandbox ID is invented. An ambiguous launch is reconciled against that same ID, never replaced under this run ID.",
        "secrets": [], "oidc_identity": None, "account_volumes": [],
    }
    data["execution"].update(backend="modal", queue="modal-sandbox", placement=placement)
    data["analysis_plan"]["frozen_before_data"] = not draft
    data["amendments"].append({
        "id": correction_id, "filed": "2026-10-27", "filed_before_affected_data": True,
        "reason": "Prospective provider and transport correction before any confirmation cohort; original Isolab route could not be admitted. Same experiment, scientific design, source A and analysis; no new cohort or measured outcome.",
        "changes": [
            "Use execution.backend=modal and actual source-bound network-blocked VM Sandbox identity instead of Isolab/EKS/IRSA or an OCI-registry assertion.",
            "Admit counted primary observations on the explicit VM boundary. Retain unknown physical isolation and mark every wall/CPU clock invalid for scientific timing.",
            "Stage only the post-freeze sealed public bundle through the SDK filesystem, verify exact content hashes in guest, retrieve a sealed parent output archive, and verify the actual returned archive hash before termination.",
            "Keep the original six arms, 64 curves, two replicates, 64 ordered targets, source-A native logic, private-label custody, seed laws, full cost accounting, caps, prefixes, statistics, stopping and one-attempt/no-restore rules unchanged.",
        ],
        "supersedes_fields": ["execution.backend", "execution.queue", "execution.placement", "arms[*].instrument", "variable_ledger.factors[source_build_binary].how"],
    })
    data["extensions"]["modal_vm_route"] = {
        "schema": "classical.ecdlp.endpoint-reuse.modal-route/v1",
        "preparation_status": "draft_missing_actual_pins" if draft else "observed_image_pins_pending_freeze_and_admission",
        "predecessor": {"path": ORIGINAL, "sha256": ORIGINAL_SHA256},
        "successor_path": SUCCESSOR, "corrective_decision_id": correction_id,
        "native_source_a": source_a, "adapter_source_b": source_b,
        "image_receipt": {"path": receipt_binding_path, "sha256": receipt_sha256},
        "build_info": {"path": build_info_binding_path, "sha256": receipt["build_info_sha256"] if receipt else None},
        "source_a_tree_sha256": receipt["source_a_tree_sha256"] if receipt else None,
        "source_b_tree_sha256": receipt["source_b_tree_sha256"] if receipt else None,
        "adapter_manifest_sha256": receipt["adapter_manifest_sha256"] if receipt else None,
        "context_manifest_sha256": receipt["context_manifest_sha256"] if receipt else None,
        "clock_policy": "All wall/CPU clock values retained as secondary diagnostic observations with wall_valid=false; no timing comparison, L2, dedicated physical host or physical-core pinning claim.",
        "input_transport": "SDK filesystem copy of only the sealed public input bundle; expected SHA-256 and member manifest verified inside the same Sandbox. No workload credentials, IRSA, versioned S3 input or in-guest account API is required.",
        "input_chronology": "Commit source A/B and analysis; build and pin observed image/binary; freeze and commit this protocol; lock source+protocol; only then draw fresh public nonce/private scalar root and the single registered cohort; retain scalar labels with the existing custodian until actual output seal. Bind resulting public hashes in the prospective admission plan.",
        "output_transport": "Worker seals parent output and records every member hash; controller retrieves archive bytes from this same Sandbox through SDK filesystem, checks observed archive SHA-256 against in-guest seal, safely unpacks and checks member hashes, then records readback receipt and termination. Future output hashes are observations, never preregistered fabricated values.",
        "output_archive_hash_rule": "SHA-256 of exact returned sealed archive bytes, recorded after execution with byte count, actual app/image/sandbox IDs, exit status and every member SHA-256; readback must agree with the in-guest seal.",
        "source_identity_rule": "Native instrument.commit means source A. Adapter/source bundle B has separate commit/tree hashes. Modal im-* means Image object identity; instrument.image_digest stays null.",
        "data_authority": "Preparation only; no approval, freeze, selector-ready state, live task claim or scientific execution authority is created by this builder.",
    }
    data["literature"] += [
        {"ref": "https://modal.com/docs/guide/sandbox-resources", "provenance": "retrieved", "claim": "CPU units are physical cores, one core equals two vCPU; explicit request/limit tuples bound CPU and memory. Two physical cores and 12288 MiB preserve this study's four-vCPU-equivalent/12-GiB resource ceiling.", "verified_by": "Modal route documentation source copies retrieved 2026-10-27; modal-route-feasibility/retrieval-manifest.json"},
        {"ref": "https://modal.com/docs/guide/sandbox-networking", "provenance": "retrieved", "claim": "VM runtime and blocked network provide the stated guest boundary; neither establishes dedicated physical hardware or L2.", "verified_by": "Modal route documentation source copies retrieved 2026-10-27"},
        {"ref": "https://modal.com/docs/guide/sandbox-files", "provenance": "retrieved", "claim": "Sandbox filesystem APIs permit explicit public-input staging and sealed-output collection; content hashes, custody and output readback remain the controller's responsibility.", "verified_by": "Modal route documentation source copies retrieved 2026-10-27"},
    ]
    if scientific_projection(data) != scientific_projection(original):
        raise ValueError("Provider correction changed the preserved scientific design")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-protocol", type=Path, default=ROOT / ORIGINAL)
    parser.add_argument("--image-receipt", type=Path)
    parser.add_argument("--build-info", type=Path)
    parser.add_argument("--receipt-binding-path", default=PREFIX + "/modal/receipts/image-build.json")
    parser.add_argument("--build-info-binding-path", default=PREFIX + "/modal/receipts/build-info.json")
    parser.add_argument("--correction-id", default="DEC-20261027-cea721")
    parser.add_argument("--draft", action="store_true", help="Prepare an explicitly unpinned, non-freezable preview")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("Refusing to overwrite any existing protocol; use a new preparation path")
    if sha(args.base_protocol) != ORIGINAL_SHA256:
        parser.error("Original protocol bytes changed; preserve predecessor and review the correction")
    if not args.draft and (not args.image_receipt or not args.build_info):
        parser.error("Observed --image-receipt and exact --build-info required outside explicit --draft mode")
    if bool(args.image_receipt) != bool(args.build_info):
        parser.error("--image-receipt and --build-info must be supplied together")
    receipt = read_json(args.image_receipt) if args.image_receipt else None
    if receipt:
        validate_receipt(receipt, read_json(args.build_info), sha(args.build_info))
    original = read_json(args.base_protocol)
    analysis = ROOT / PREFIX / "protocol/analysis.py"
    if sha(analysis) != original["analysis_plan"]["script"]["sha256"]:
        parser.error("Original analysis bytes changed")
    protocol = build(original, receipt, receipt_sha256=sha(args.image_receipt) if receipt else None,
                     receipt_binding_path=args.receipt_binding_path,
                     build_info_binding_path=args.build_info_binding_path,
                     correction_id=args.correction_id, draft=args.draft)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        stream.write(json.dumps(protocol, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    print(json.dumps({"protocol": str(args.out), "sha256": sha(args.out), "frozen": False,
                      "approved": False, "scientific_data_generated": False,
                      "actual_image_pins_present": receipt is not None}))


if __name__ == "__main__":
    main()
