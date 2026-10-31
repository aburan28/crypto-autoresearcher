#!/usr/bin/env python3
"""Prepare reviewable, noncanonical admission bytes; never authorize or run.

--prospective creates the exact hypothetical approved/frozen specification and
plan bytes required by the official read-only preapproval probe. Their preview
location and authority.json make explicit that no Coordinator approval occurred.
Only use that mode after the real protocol freeze and fresh public-input seal.
The default produces an explicitly incomplete review-required draft.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from experiment_execution import GENERATED
from research_dispatch import validate_queue
sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepare_context import committed_files
from build_protocol import NATIVE_SOURCE_A, validate_receipt

EXP = "EXP-ECDLP-2b4ff1"
GOAL = "GOAL-ECDLP-e70832"
PREFIX = "harness/classical_ecdlp_endpoint_reuse"
PROTOCOL = f"experiments/{EXP}/protocol.modal-vm.v1.json"
SPEC = f"experiments/{EXP}/specification.yaml"
PLAN = f"experiments/{EXP}/trial-plan.json"
DRIVER = PREFIX + "/modal/admission_driver.py"
IDS = {"corrective_decision": "DEC-20261027-cea721", "approval_decision": "DEC-20261027-6b094c",
       "executor_task": "TASK-20261027-c35737", "archive_task": "TASK-20261027-913f6b",
       "design_archive_task": "TASK-20261027-f11de9", "batch": "BATCH-b1c6e1", "run": "RUN-ECDLP-b883bf"}
TRIAL_ARTIFACTS = ["manifest.yaml", "raw-result.json", "modal-evidence.tar.gz", "modal-evidence-manifest.json"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_bytes())


def write(root, path, value):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    return target


def inference(role):
    return {"policy": "executor-implementation" if role == "executor" else "coordinator-orchestration-code",
            "reasoning_effort": "high", "fallback_allowed": False, "degraded_allowed": False,
            "independent_session_required": False, "delivery": "interactive"}


def source_draft():
    # Reuse the source package's explicit allowlist, including vendor metadata
    # and the fixed native self-test include. Adapter working bytes are merely
    # draft pins; official preapproval later requires them committed at origin.
    native = committed_files(ROOT, NATIVE_SOURCE_A, PREFIX)
    files = {PREFIX + "/" + name: hashlib.sha256(data).hexdigest() for name, data in native.items()}
    for path in sorted((ROOT / PREFIX / "modal").glob("*.py")):
        if not path.name.startswith("test_"):
            files[path.relative_to(ROOT).as_posix()] = digest(path)
    return files


def validate_transport_binding_paths(protocol, inputs, bindings):
    route = protocol["extensions"]["modal_vm_route"]
    for name in ("image_receipt", "build_info"):
        expected = route[name]
        if (bindings.get(name) != expected["path"]
                or inputs.get(expected["path"]) != expected["sha256"]):
            raise ValueError("transport path/hash differs from frozen protocol: " + name)


def build(args):
    if args.out.exists():
        raise ValueError("fresh noncanonical preparation directory required")
    if args.out.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("admission previews must stay outside the canonical checkout")
    ids = {**IDS, **(load(args.ids) if args.ids else {})}
    protocol = load(args.protocol)
    sources = load(args.source_pins) if args.source_pins else source_draft()
    inputs = load(args.input_pins) if args.input_pins else {}
    bindings = load(args.bindings) if args.bindings else {}
    prospective = args.prospective
    if prospective:
        if not all((args.source_pins, args.input_pins, args.bindings)):
            raise ValueError("prospective mode requires actual source-pins, input-pins and transport bindings")
        freeze = protocol.get("freeze", {})
        body = {k: v for k, v in protocol.items() if k != "freeze"}
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
        if (freeze.get("status") != "frozen" or freeze.get("filed_before_affected_data") is not True
                or freeze.get("protocol_sha256") != hashlib.sha256(canonical).hexdigest()):
            raise ValueError("actual prospective protocol must already be frozen correctly")
        for key in ("image_receipt", "build_info", "public_bundle", "inputs_manifest"):
            value = bindings.get(key)
            if not isinstance(value, str) or value not in inputs:
                raise ValueError("transport binding missing from exact input pins: " + key)
        if inputs.get(PROTOCOL) != digest(args.protocol):
            raise ValueError("exact frozen successor protocol must be bound in input pins")
        validate_transport_binding_paths(protocol, inputs, bindings)
        for path in sources:
            if Path(path).is_absolute() or ".." in Path(path).parts:
                raise ValueError("source closure requires repository-relative paths")
        required_sources = source_draft()
        if any(sources.get(path) != expected for path, expected in required_sources.items()):
            raise ValueError("source pins must cover exact allowlisted native A and every current Modal adapter source")
        for files in (sources, inputs):
            if not isinstance(files, dict) or not files:
                raise ValueError("nonempty exact source/input pin mappings required")
            for path, expected in files.items():
                local = Path(path) if Path(path).is_absolute() else ROOT / path
                if not re.fullmatch(r"[0-9a-f]{64}", expected) or digest(local) != expected:
                    raise ValueError("source/input bytes differ: " + path)
        resolve = lambda path: Path(path) if Path(path).is_absolute() else ROOT / path
        receipt = load(resolve(bindings["image_receipt"]))
        info = load(resolve(bindings["build_info"]))
        validate_receipt(receipt, info, inputs[bindings["build_info"]])
        route = protocol["extensions"]["modal_vm_route"]
        placement = protocol["execution"]["placement"]
        if (route["native_source_a"] != receipt["source_a_revision"]
                or route["adapter_source_b"] != receipt["source_b_revision"]
                or route["adapter_manifest_sha256"] != receipt["adapter_manifest_sha256"]
                or any(placement[name] != receipt[name] for name in ("app_id", "image_id"))
                or any(arm["instrument"]["commit"] != receipt["source_a_revision"]
                       or arm["instrument"]["binary_sha256"] != receipt["binary_sha256"] for arm in protocol["arms"])):
            raise ValueError("actual image/source/binary identity differs from frozen route")
    if DRIVER not in sources:
        raise ValueError("admission driver must be included in source closure")
    queue_path = f"coordination/goals/{GOAL}/batches/{ids['batch']}/dispatch_queue.json"
    handoff_path = f"ledger/handoffs/{ids['executor_task']}.yaml"
    run_root = f"experiments/{EXP}/runs/{ids['run']}"
    trial_paths = [run_root + "/" + name for name in [*GENERATED, *TRIAL_ARTIFACTS]]
    archive_receipt = f"coordination/goals/{GOAL}/batches/{ids['batch']}/archives/{ids['archive_task']}/snapshot-receipt.json"
    spec_doc = load(ROOT / SPEC)
    spec = spec_doc["experiment"]
    spec.update(version=2, status="approved" if prospective else "review_required",
                approved_by=ids["approval_decision"] if prospective else None,
                frozen=prospective, execution_authorized=prospective)
    spec["variable_ledger"] = copy.deepcopy(protocol["variable_ledger"])
    spec["execution_plan"] = {
        "protocol_hashes": [protocol["freeze"]["protocol_sha256"]] if prospective else [],
        "protocol": {"path": PROTOCOL, "sha256": digest(args.protocol)},
        "source_sha256": sources, "input_sha256": inputs,
        "trial_plan": PLAN, "backend": "modal", "runtime": "vm",
        "binding_status": "prospective exact bytes for read-only preapproval only" if prospective else "incomplete draft; actual image/source/frozen protocol/fresh public inputs required",
    }
    spec["input_bindings"] = {name: {"path": path, "sha256": inputs[path]} for name, path in bindings.items() if path in inputs}
    spec["provider_correction"] = {"decision": ids["corrective_decision"], "original_protocol_preserved": "experiments/" + EXP + "/protocol.json",
                                   "all_clocks_wall_valid": False, "scientific_design_changed": False}
    spec_target = write(args.out, SPEC, spec_doc)
    argv = ["python3", DRIVER, "run", "--image-receipt", bindings.get("image_receipt", "UNBOUND_IMAGE_RECEIPT"),
            "--protocol", PROTOCOL, "--public-bundle", bindings.get("public_bundle", "UNBOUND_PUBLIC_BUNDLE"),
            "--inputs-manifest-sha256", inputs.get(bindings.get("inputs_manifest"), "UNBOUND_INPUTS_SHA256"),
            "--run-id", ids["run"], "--out", "{run_dir}"]
    checker = ["python3", DRIVER, "check", "--out", "{run_dir}"]
    plan = {"schema": "crypto.autoresearch.trial_plan.v1", "experiment_id": EXP, "hypothesis_id": "H-ECDLP-3509c4",
            "task_id": ids["executor_task"], "specification": SPEC, "specification_sha256": digest(spec_target),
            "queue": queue_path, "frozen": prospective, "approved_by": ids["approval_decision"] if prospective else None,
            "source_sha256": sources, "input_sha256": inputs, "stop_on_invalid_output": True,
            "trials": [{"id": "modal-parent-six-arm-study", "run_id": ids["run"], "depends_on": [],
                        "argv": argv, "check_argv": checker, "artifacts": TRIAL_ARTIFACTS, "memory_mb": 12288,
                        "watchdog_seconds": 5700,
                        "watchdog_reason": "Controller lifecycle maximum5400 seconds plus300 seconds to seal local retained evidence; scientific global/child watchdogs remain3600 seconds. Machine protection, no scientific extension or retry.",
                        "parameters": {"native_children": 768, "curves": 64, "replicates": 2, "targets_per_cell": 64,
                                       "unique_public_target_ids": 8192, "all_clocks_wall_valid": False}}]}
    plan_target = write(args.out, PLAN, plan)
    execution = {"mode": "experiments", "kind": "run", "experiment_id": EXP, "trial_plan": PLAN,
                 "trial_plan_sha256": digest(plan_target), "approved_by": ids["approval_decision"]}
    handoff = {"id": ids["executor_task"], "from": "coordinator", "to": "executor", "role": "executor",
               "objective": "Execute the existing registered six-arm study once on the explicitly admitted Modal VM and preserve every outcome.",
               "uncertainty_reduced": "Actual complete counted work, public answer correctness, endpoint causality/cap behavior and memory at the fixed finite scope.",
               "inputs": [PROTOCOL, SPEC, PLAN, *sorted(sources), *sorted(inputs)],
               "constraints": ["Prospective preview is not approval or dispatch authority. Require archived Coordinator approval, selector ready and a published live claim before the supervisor launches.",
                               "One Sandbox create/engine attempt, no scientific retries or restoration, original six arms/costs/sample/seeds/caps/stopping unchanged.",
                               "Only the sealed public bundle enters the VM; retain private labels until actual output seal; block workload networking and run as UID/GID1000.",
                               "All clocks stay wall_valid=false. Record unknown physical isolation without claiming L2/dedicated hardware or an OCI registry digest.",
                               "Transport checker is not public witness verification or scientific review; retain incomplete outcomes and perform those separate checks before any qualified comparison."],
               "deliverables": trial_paths, "artifact_paths": trial_paths, "archived_by": ids["archive_task"],
               "inference": inference("executor"), "budget": {"maximum_runs": 1, "memory_gb": 12},
               "completion_gate": ["Exact one-attempt outputs or preserved operational refusal, with all supervisor and sealed controller artifacts.",
                                   "Actual returned parent archive SHA-256 and member hashes agree with in-guest seal; no fabricated missing rows or scientific conclusion."],
               "return_format": "Artifact hashes, transport and execution statuses, counts and limitations; no official hypothesis verdict.",
               "execution": execution, "prospective_only": True}
    executor = {"id": ids["executor_task"], "title": "Execute the frozen Modal VM observation study", "role": "executor",
                "state": "queued", "priority": 90, "review_required": False, "depends_on": [],
                "read_scope": sorted({PREFIX + "/", SPEC, PROTOCOL, PLAN, *[path for path in inputs if not Path(path).is_absolute()]}), "write_scope": [run_root + "/"],
                "artifact_paths": trial_paths, "archived_by": ids["archive_task"], "handoff": handoff}
    archive_handoff = {"id": ids["archive_task"], "from": "coordinator", "to": "coordinator", "role": "coordinator",
                       "objective": "Archive all supervisor and Modal evidence bytes including censored/failed outcomes.",
                       "uncertainty_reduced": "Immutable source/output custody without scientific promotion.",
                       "inputs": [run_root + "/"], "constraints": ["No scientific trial or interpretation; exact-path snapshot only."],
                       "deliverables": [archive_receipt], "artifact_paths": [archive_receipt],
                       "completion_gate": ["Actual committed archive receipt and every declared path hash verify."],
                       "budget": {"maximum_runs": 0}, "inference": inference("coordinator")}
    archive = {"id": ids["archive_task"], "title": "Archive the complete Modal observation custody chain", "role": "coordinator",
               "state": "queued", "priority": 80, "review_required": False, "depends_on": [ids["executor_task"]],
               "read_scope": [run_root + "/"], "write_scope": [str(Path(archive_receipt).parent) + "/"],
               "artifact_paths": [archive_receipt], "archived_by": ids["archive_task"], "handoff": archive_handoff,
               "archive": {"kind": "snapshot", "binding_mode": "content_at_commit", "source_task_ids": [ids["executor_task"]],
                           "commit_sha": None, "parent_sha": None, "path_sha256": {}, "record_ids": [EXP, ids["run"]]}}
    queue = {"schema": "crypto.autoresearch.dispatch_queue.v1", "goal_id": GOAL,
             "objective": "Prospective provider correction and one fixed six-arm count/memory observation study.",
             "max_concurrent": 1, "tasks": [executor, archive]}
    validate_queue(queue)
    write(args.out, queue_path, queue)
    write(args.out, handoff_path, {"handoff": handoff})
    write(args.out, f"ledger/handoffs/{ids['archive_task']}.yaml", {"handoff": archive_handoff})
    packet = {"schema": "crypto.autoresearch.preapproval_packet.v1", "experiment_id": EXP,
              "approval_decision_id": ids["approval_decision"], "specification": SPEC, "trial_plan": PLAN,
              "queue": queue_path, "handoff": handoff_path,
              "preview": {name: str(args.out / path) for name, path in {"specification": SPEC, "trial_plan": PLAN, "queue": queue_path, "handoff": handoff_path}.items()},
              "source_ref": args.source_ref, "lane_id": ids["batch"],
              "execution_route": {"kind": "implementation", "reason": "New source-bound Modal VM controller and transport; executor-implementation owns complete receipts and bounded recovery. No runbook mechanical-tier readiness is claimed."}}
    write(args.out, "preapproval-packet.json", packet)
    write(args.out, "ids.json", ids)
    write(args.out, "authority.json", {"canonical_files_written": False, "approval_recorded": False, "scientific_data_generated": False,
                                        "projected_approval_states_for_read_only_probe": prospective, "frozen_protocol_input": prospective,
                                        "execution_authorized": False, "live_claim_created": False})
    print(json.dumps({"packet": str(args.out / "preapproval-packet.json"), "canonical_files_written": False,
                      "approval_recorded": False, "queue_structure": "valid", "prospective": prospective}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-ref", default="origin/experiment/classical-ecdlp-endpoint-reuse-20261026")
    parser.add_argument("--source-pins", type=Path)
    parser.add_argument("--input-pins", type=Path)
    parser.add_argument("--bindings", type=Path)
    parser.add_argument("--ids", type=Path)
    parser.add_argument("--prospective", action="store_true")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
