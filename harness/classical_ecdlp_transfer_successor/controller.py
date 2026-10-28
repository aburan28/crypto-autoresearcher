#!/usr/bin/env python3
"""Stage one committed transfer-study program in the existing native Modal VM.

The source-A native image and source-B2 transport primitives remain unchanged.
Only the seven committed transfer modules, their frozen manifest, protocol and public
compute plan are staged. This controller creates and invokes at most one Sandbox.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

NATIVE_A = "fe01ccd832832488c58abeef17548b0a8db6035f"
IMAGE_B = "de6ed88850fc8bad17ccbabfad8b66a791e478e5"
TRANSPORT_PATH = "harness/classical_ecdlp_endpoint_reuse/modal/controller.py"
TRANSPORT_SHA = "7bba4e977e9e076cc7e7ea3ec1ab04d60ce5da3033df7f68116a12602419b4fe"
SOURCE_SCHEMA = "classical.ecdlp.transfer-study.source-manifest/v1"
CONTEXT_SCHEMA = "classical.ecdlp.transfer-study.modal-provider-context/v1"
SOURCE_NAMES = {"curve.py", "constructor.py", "cohort.py", "compute.py", "verify.py", "controller.py", "driver.py"}
SOURCE_PREFIX = "harness/classical_ecdlp_transfer_successor"
EXPERIMENT_ID = "EXP-ECDLP-8dc19d"
RUN_ID = "RUN-ECDLP-994f70"
APP_ID = "ap-EAHJ6SjvmeY99EQ2I47duh"
IMAGE_ID = "im-zz2zzbG7JE9xilcBO1QJMh"
EXPECTED_KEYS = {"candidate_attempts_planned", "baseline_attempts_planned", "total_attempts_planned",
                 "fixture_count_planned", "arm_ids"}
HEX64 = re.compile(r"[a-f0-9]{64}\Z")
REVISION = re.compile(r"[a-f0-9]{40}\Z")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def transport(repo=None):
    path = (Path(repo).resolve() / TRANSPORT_PATH) if repo is not None else Path("/opt/study/modal/controller.py")
    if sha_file(path) != TRANSPORT_SHA:
        raise ValueError("source-B2 transport helper differs")
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("_transfer_study_b2_transport", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_payload(repo, manifest_path):
    """Read the source closure from Git objects, then check live controller bytes."""
    repo = Path(repo).resolve()
    raw = Path(manifest_path).read_bytes()
    manifest = json.loads(raw)
    if (manifest.get("schema") != SOURCE_SCHEMA
            or not REVISION.fullmatch(manifest.get("source_revision_c", ""))
            or manifest.get("native_source_a") != NATIVE_A
            or manifest.get("image_adapter_source_b") != IMAGE_B
            or set(manifest.get("files", {})) != SOURCE_NAMES):
        raise ValueError("actual seven-module committed transfer source manifest required")
    helper = transport(repo)
    prefix = str(helper.relative_path(manifest.get("source_prefix", SOURCE_PREFIX)))
    subprocess.run(["git", "merge-base", "--is-ancestor", manifest["source_revision_c"], "HEAD"],
                   cwd=repo, check=True, capture_output=True)
    files = {}
    for name, digest in manifest["files"].items():
        if not isinstance(digest, str) or not HEX64.fullmatch(digest):
            raise ValueError("source SHA-256 required")
        relative = prefix + "/" + name
        data = subprocess.check_output(["git", "show", manifest["source_revision_c"] + ":" + relative], cwd=repo)
        if sha(data) != digest:
            raise ValueError("committed transfer source differs: " + relative)
        current = repo / relative
        if current.is_symlink() or current.read_bytes() != data:
            raise ValueError("working source differs from committed source: " + relative)
        files[name] = data
    if sha_file(__file__) != manifest["files"]["controller.py"]:
        raise ValueError("executing controller differs from source manifest")
    return manifest, raw, files


def expected_counts(value):
    if (not isinstance(value, dict) or set(value) != EXPECTED_KEYS
            or any(type(value[key]) is not int or value[key] <= 0 for key in EXPECTED_KEYS - {"arm_ids"})
            or value["total_attempts_planned"] != value["candidate_attempts_planned"] + value["baseline_attempts_planned"]
            or not isinstance(value["arm_ids"], list) or len(value["arm_ids"]) != 11
            or any(not isinstance(arm, str) or not arm for arm in value["arm_ids"])
            or len(set(value["arm_ids"])) != 11):
        raise ValueError("exact positive planned counts and eleven fixed arm IDs required")
    return value


def make_plan(repo, receipt_path, protocol_path, compute_plan_path, manifest_path, prior_exclusions_path):
    helper = transport(repo)
    receipt = helper.image_receipt(receipt_path)
    protocol, protocol_hash, limits = helper.frozen_protocol(protocol_path)
    if EXPERIMENT_ID is None or protocol.get("protocol_id") != EXPERIMENT_ID:
        raise ValueError("this driver is bound to its allocated transfer experiment")
    manifest, source_raw, sources = source_payload(repo, manifest_path)
    compute_plan = json.loads(Path(compute_plan_path).read_bytes())
    counts = expected_counts(compute_plan.get("expected"))
    exclusions_path = Path(prior_exclusions_path)
    if (exclusions_path.is_symlink() or not exclusions_path.is_file()
            or not 0 < exclusions_path.stat().st_size <= 1024 * 1024):
        raise ValueError("bounded regular prior-cohort exclusions JSON required")
    exclusions = json.loads(exclusions_path.read_bytes())
    if not isinstance(exclusions, dict) or exclusions.get("schema") != "classical.ecdlp.transfer-study.exclusions/v1":
        raise ValueError("prior-cohort exclusions schema required")
    exclusions_hash = sha_file(exclusions_path)
    extension = protocol.get("extensions", {}).get("transfer_study", {})
    expected = {"source_manifest_sha256": sha(source_raw),
                "image_receipt_sha256": sha_file(receipt_path),
                "compute_plan_sha256": sha_file(compute_plan_path),
                "prior_exclusions_sha256": exclusions_hash,
                "source_revision_c": manifest["source_revision_c"], "expected": counts}
    if any(extension.get(key) != value for key, value in expected.items()):
        raise ValueError("frozen transfer source/image/compute-plan/exclusions binding differs")
    if (compute_plan.get("schema") != "classical.ecdlp.transfer-study.compute-plan/v1"
            or compute_plan.get("status") != "frozen"
            or compute_plan.get("experiment_id") != EXPERIMENT_ID
            or compute_plan.get("run_id") != RUN_ID
            or compute_plan.get("source_manifest_sha256") != sha(source_raw)
            or compute_plan.get("cohort", {}).get("exclusion_file_sha256") != exclusions_hash):
        raise ValueError("frozen transfer compute plan required")
    if (receipt["source_a_revision"] != NATIVE_A or receipt["source_b_revision"] != IMAGE_B
            or receipt["app_id"] != APP_ID or receipt["image_id"] != IMAGE_ID):
        raise ValueError("preserved source-A/source-B2 image required")
    for key in ("binary_sha256", "build_info_sha256", "adapter_manifest_sha256"):
        if manifest.get(key) != receipt[key]:
            raise ValueError("transfer source/image identity differs: " + key)
    placement = protocol["execution"]["placement"]
    for key in ("app_id", "image_id"):
        if placement.get(key) != receipt[key]:
            raise ValueError("frozen Modal identity differs: " + key)
    if (placement.get("runtime") != "vm" or placement.get("block_network") is not True
            or placement.get("requested_cpu_physical_cores") != [2, 2]
            or placement.get("requested_memory_mib") != [12288, 12288]
            or placement.get("all_clocks_wall_valid") is not False):
        raise ValueError("frozen VM/resources/network/clock placement differs")
    if (len(protocol["arms"]) != 11
            or {arm["id"] for arm in protocol["arms"]} != set(counts["arm_ids"])):
        raise ValueError("official transfer arms differ from the frozen compute plan")
    for arm in protocol["arms"]:
        if arm["instrument"].get("commit") != manifest["source_revision_c"] or arm["instrument"].get("threads") != 1:
            raise ValueError("all transfer arms require committed Python source and one thread")
    plan = {"schema": "classical.ecdlp.transfer-study.modal-run-plan/v1",
            "experiment_id": protocol["protocol_id"], "measurement_started": False,
            "fresh_cohort_generated": False, "expected": counts,
            "app_name": helper.APP_NAME, "environment_name": helper.ENVIRONMENT,
            "app_id": receipt["app_id"], "image_id": receipt["image_id"],
            "runtime": "vm", "block_network": True,
            "requested_cpu": [2, 2], "requested_memory_mib": [12288, 12288],
            "source_revision": manifest["source_revision_c"], "adapter_revision": IMAGE_B,
            "native_image_source_revision": NATIVE_A,
            **{key: receipt[key] for key in ("source_a_revision", "source_b_revision", "source_a_tree_sha256",
                "source_b_tree_sha256", "binary_sha256", "build_info_sha256", "build_provenance_sha256",
                "adapter_manifest_sha256")},
            "source_revision_c": manifest["source_revision_c"], "source_manifest_sha256": sha(source_raw),
            "protocol_sha256": protocol_hash, "protocol_file_sha256": sha_file(protocol_path),
            "compute_plan_sha256": sha_file(compute_plan_path), "prior_exclusions_sha256": exclusions_hash,
            "staged_source_sha256": manifest["files"], "native_binary_executed": False,
            "lifecycle": limits, "maximum_sandbox_creates": 1, "scientific_retries": 0,
            "restore": False, "all_clocks_wall_valid": False, "l2_or_dedicated_physical_host_attested": False}
    return plan, sources, source_raw


def engine_argv(plan):
    # Includes the fresh cohort draw and every candidate/reference attempt.
    return ["/usr/bin/timeout", "--signal=TERM", "--kill-after=30", "3600",
            "python3", "/work/source/compute.py", "--protocol", "/work/stage/compute-plan.json",
            "--source-manifest", "/work/source/source-manifest.json",
            "--provider-context", "/work/stage/provider-context.json",
            "--prior-exclusions", "/work/stage/prior-exclusions.json", "--output-dir", "/work/result/raw"]


def valid_probe(probe, expected):
    return (probe.get("probe_passed") is True and probe.get("scientific_submission") is False
            and probe.get("candidate_evaluations_allowed") == 0 and probe.get("cohort_draws_allowed") == 0
            and valid_plan_probe(probe.get("plan", {}), expected))


def valid_plan_probe(value, expected):
    runtime = value.get("runtime_facts", {})
    access = runtime.get("input_access", {})
    return (value.get("measurement_started") is False and value.get("fresh_cohort_generated") is False
            and value.get("candidate_attempts_executed") == 0
            and all(value.get(key) == item for key, item in expected.items())
            and value.get("provider_runtime_requirements_enforced") is True
            and runtime.get("resuid") == [1000, 1000, 1000]
            and runtime.get("resgid") == [1000, 1000, 1000]
            and runtime.get("supplementary_groups") == []
            and runtime.get("environment_values_collected") is False
            and set(access) == SOURCE_NAMES | {"protocol", "source_manifest", "provider_context", "prior_exclusions"}
            and all(item.get("exists") is True and item.get("writable") is False for item in access.values()))


def run_plan_probe(argv, output, expected, runner=subprocess.run):
    """Observe the exact unprivileged plan-only entrypoint; permit no candidate evaluations."""
    invocation = ["env", "-i", "PATH=/usr/local/bin:/usr/bin:/bin", "HOME=/work", "TMPDIR=/work/tmp",
                  "PYTHONDONTWRITEBYTECODE=1", "setpriv", "--reuid=1000", "--regid=1000", "--clear-groups",
                  "--no-new-privs", *argv, "--plan-only"]
    record = {"schema": "classical.ecdlp.transfer-study.engine-plan-probe/v1",
              "argv": invocation, "purpose": "unprivileged_import_source_plan_identity_and_count_check_without_cohort_draw",
              "candidate_evaluations_allowed": 0, "cohort_draws_allowed": 0, "scientific_submission": False,
              "invocation_attempts": 1, "returncode": None, "probe_passed": False}
    try:
        result = runner(invocation, cwd="/work", capture_output=True, text=True, timeout=120)
        record.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
        parsed = json.loads(result.stdout)
        record["plan"] = parsed
        record["probe_passed"] = result.returncode == 0 and valid_plan_probe(parsed, expected)
    except Exception as error:
        record["error"] = {"type": type(error).__name__, "message": str(error)}
    write_json(output, record)
    Path(output).chmod(0o444)
    if not record["probe_passed"]:
        raise ValueError("unprivileged engine plan-only probe failed; scientific launch refused")
    return record


def sandbox_prepare(spec_path):
    helper = transport()
    spec = json.loads(Path(spec_path).read_bytes())
    for relative, digest in spec["stage_hashes"].items():
        path = Path("/work") / str(helper.relative_path(relative))
        if path.is_symlink() or sha_file(path) != digest:
            raise ValueError("staged source/plan/context differs before preparation")
    protocol, protocol_hash, _ = helper.frozen_protocol("/work/stage/protocol.json")
    plan = spec["plan"]
    extension = protocol.get("extensions", {}).get("transfer_study", {})
    manifest_path = Path("/work/source/source-manifest.json")
    manifest = json.loads(manifest_path.read_bytes())
    if (protocol.get("protocol_id") != EXPERIMENT_ID or protocol_hash != plan["protocol_sha256"]
            or sha_file(manifest_path) != extension.get("source_manifest_sha256")
            or sha_file("/work/stage/compute-plan.json") != extension.get("compute_plan_sha256")
            or sha_file("/work/stage/prior-exclusions.json") != extension.get("prior_exclusions_sha256")
            or set(manifest["files"]) != SOURCE_NAMES):
        raise ValueError("remote frozen source/protocol/compute-plan binding differs")
    if spec["engine_argv"] != engine_argv(plan) or plan["engine_argv"] != spec["engine_argv"]:
        raise ValueError("remote fixed compute argv differs")
    for name, digest in manifest["files"].items():
        if sha_file(Path("/work/source") / name) != digest:
            raise ValueError("remote transfer source differs")
    # Root-owned immutable parents prevent UID1000 renaming code or protocol.
    os.chown("/work", 0, 0)
    Path("/work").chmod(0o755)
    for directory in (Path("/work/source"), Path("/work/stage")):
        for path in [directory, *directory.rglob("*")]:
            if path.is_symlink():
                raise ValueError("work source/plan links forbidden")
            os.chown(path, 0, 0)
            path.chmod(0o555 if path.is_dir() else 0o444)
    for directory in (Path("/work/result"), Path("/work/tmp")):
        directory.mkdir(exist_ok=directory.name == "tmp")
        os.chown(directory, 1000, 1000)
        directory.chmod(0o755)
    # Same cleared environment and UID as science; no prepare/evaluate in probe.
    Path("/work/stage").chmod(0o755)
    try:
        run_plan_probe(spec["engine_argv"], "/work/stage/engine-plan-probe.json", plan["expected"])
    finally:
        Path("/work/stage").chmod(0o555)


def run(repo, receipt_path, protocol_path, compute_plan_path, manifest_path, prior_exclusions_path, output, modal_module=None):
    helper = transport(repo)
    plan, sources, source_raw = make_plan(repo, receipt_path, protocol_path, compute_plan_path, manifest_path, prior_exclusions_path)
    output = Path(output)
    if output.exists():
        raise ValueError("fresh controller output directory required")
    output.mkdir(parents=True)
    # Retain the exact upload inputs alongside the actual provider receipts.
    # These are only the allowlisted committed modules and the frozen public plan.
    (output / "source-manifest.json").write_bytes(source_raw)
    (output / "protocol.json").write_bytes(Path(protocol_path).read_bytes())
    (output / "compute-plan.json").write_bytes(Path(compute_plan_path).read_bytes())
    (output / "prior-exclusions.json").write_bytes(Path(prior_exclusions_path).read_bytes())
    source_snapshot = output / "staged-source"
    source_snapshot.mkdir()
    for name, data in sources.items():
        (source_snapshot / name).write_bytes(data)
    plan["sandbox_name"] = "ecdlp-transfer-" + uuid.uuid4().hex
    plan["engine_argv"] = engine_argv(plan)
    write_json(output / "plan.json", plan)
    record = {"schema": "classical.ecdlp.transfer-study.modal-controller/v1", "started_at": helper.utc(),
              "plan": plan, "sandbox_create_calls": 0, "engine_exec_calls": 0,
              "plan_probe_exec_calls": 0, "measurement_started": False,
              "termination_requested": False, "automatic_retry": False}
    sb = None
    if modal_module is None:
        import modal as modal_module
    try:
        if modal_module.__version__ != "1.6.2":
            raise ValueError("reviewed Modal SDK1.6.2 required")
        app = modal_module.App.lookup(plan["app_name"], environment_name=plan["environment_name"], create_if_missing=False)
        if app.app_id != plan["app_id"]:
            raise ValueError("actual App differs from frozen image")
        image = modal_module.Image.from_id(plan["image_id"])
        record["sandbox_create_calls"] = 1
        write_json(output / "create-intent.json", record)
        sb = modal_module.Sandbox.create("sleep", str(plan["lifecycle"]["sandbox_timeout_seconds"]),
            app=app, name=plan["sandbox_name"], image=image, runtime="vm", block_network=True,
            cpu=(2, 2), memory=(12288, 12288), timeout=plan["lifecycle"]["sandbox_timeout_seconds"],
            secrets=[], include_oidc_identity_token=False, workdir="/work")
        record.update(sandbox_id=sb.object_id, app_id=app.app_id, image_id=image.object_id)
        write_json(output / "sandbox-created.json", record)
        deadline = time.monotonic() + plan["lifecycle"]["staging_timeout_seconds"]
        for name, key in (("build-info.json", "build_info_sha256"), ("adapter-manifest.json", "adapter_manifest_sha256"),
                          ("modal-image-build.json", "build_provenance_sha256")):
            data = helper.deadline_call(lambda: helper.file_bytes(sb, "/opt/study/" + name), deadline)
            if sha(data) != plan[key]:
                raise ValueError("actual code image differs: " + name)
            (output / name).write_bytes(data)
        context = {**plan, "schema": CONTEXT_SCHEMA, "provider": "modal", "backend": "modal",
                   "sandbox_id": sb.object_id, "sdk_version": modal_module.__version__,
                   "build_info_path": "/opt/study/build-info.json", "adapter_manifest_path": "/opt/study/adapter-manifest.json",
                   "created_at": helper.utc(), "no_workload_credentials": True, "isolation_level": "unknown"}
        write_json(output / "provider-context.json", context)
        staged = {"stage/compute-plan.json": Path(compute_plan_path).read_bytes(),
                  "stage/prior-exclusions.json": Path(prior_exclusions_path).read_bytes(),
                  "stage/protocol.json": Path(protocol_path).read_bytes(),
                  "stage/provider-context.json": (output / "provider-context.json").read_bytes(),
                  "source/source-manifest.json": source_raw,
                  **{"source/" + name: data for name, data in sources.items()}}
        spec = {"plan": plan, "engine_argv": plan["engine_argv"],
                "stage_hashes": {name: sha(data) for name, data in staged.items()}}
        staged["stage/launch.json"] = json.dumps(spec, indent=2, allow_nan=False).encode() + b"\n"
        record["staging"] = [helper.stage_bytes(sb, data, "/work/" + name, deadline) for name, data in staged.items()]
        prep = helper.deadline_call(lambda: sb.exec("python3", "/work/source/controller.py", "_prepare",
            "/work/stage/launch.json", timeout=max(1, int(deadline - time.monotonic()))), deadline)
        record["prepare_returncode"] = helper.deadline_call(prep.wait, deadline)
        for channel in ("stdout", "stderr"):
            (output / ("prepare." + channel + ".log")).write_text(helper.deadline_call(getattr(prep, channel).read, deadline))
        try:
            probe_raw = helper.deadline_call(lambda: helper.file_bytes(sb, "/work/stage/engine-plan-probe.json"), deadline)
            (output / "engine-plan-probe.json").write_bytes(probe_raw)
            probe = json.loads(probe_raw)
            record["plan_probe_exec_calls"] = 1 if isinstance(probe.get("returncode"), int) else None
            record["engine_plan_probe"] = {"sha256": sha(probe_raw), "probe_passed": probe.get("probe_passed"),
                                          "returncode": probe.get("returncode")}
        except Exception as error:
            record["plan_probe_exec_calls"] = None
            record["plan_probe_readback_error"] = {"type": type(error).__name__, "message": str(error)}
            probe = {}
        if record["prepare_returncode"] or not valid_probe(probe, plan["expected"]):
            raise ValueError("Sandbox staged-source/public-plan preparation failed")
        record["engine_exec_calls"] = 1
        record["measurement_started"] = "submission_pending"
        write_json(output / "engine-intent.json", record)
        # The unchanged B2 launch primitive enforces its own exclusive sentinel,
        # env-i/setpriv, UID1000 quiescence and complete failure-tree sealing.
        process = sb.exec("python3", "/opt/study/modal/controller.py", "_launch", "/work/stage/launch.json",
                          timeout=plan["lifecycle"]["command_timeout_seconds"])
        record["measurement_started"] = True
        record["engine_command_returncode"] = process.wait()
    except Exception as error:
        record["error"] = {"type": type(error).__name__, "message": str(error)}
        record["submission_ambiguous"] = ((record["sandbox_create_calls"] == 1 and sb is None)
                                           or record["measurement_started"] == "submission_pending")
    finally:
        if sb is not None:
            try:
                record["collection"] = helper.collect(sb, output / "collected", plan["lifecycle"]["collection_grace_seconds"])
            except Exception as error:
                record["collection"] = {"complete": False, "error": {"type": type(error).__name__, "message": str(error)}}
            if record["collection"].get("complete"):
                try:
                    sb.terminate()
                    record["termination_requested"] = True
                except Exception as error:
                    record["termination_error"] = type(error).__name__
            else:
                record["sandbox_preserved_for_collection"] = True
        record["finished_at"] = helper.utc()
        record["success"] = ("error" not in record and record.get("engine_command_returncode") == 0
            and record.get("collection", {}).get("complete") is True
            and record["collection"].get("engine_returncode") == 0)
        write_json(output / "controller-receipt.json", record)
    return record


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "_prepare":
        sandbox_prepare(sys.argv[2])
        return 0
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="action", required=True)
    launch = sub.add_parser("run")
    for name in ("repo-root", "image-receipt", "protocol", "compute-plan", "source-manifest", "prior-exclusions"):
        launch.add_argument("--" + name, required=True, type=Path)
    launch.add_argument("--out", type=Path)
    launch.add_argument("--plan-only", action="store_true")
    recovery = sub.add_parser("collect")
    recovery.add_argument("--repo-root", required=True, type=Path)
    recovery.add_argument("--sandbox-id", required=True)
    recovery.add_argument("--out", required=True, type=Path)
    recovery.add_argument("--seconds", type=int, default=600)
    a = p.parse_args()
    if a.action == "collect":
        if not re.fullmatch(r"sb-[A-Za-z0-9]+", a.sandbox_id) or not 1 <= a.seconds <= 600:
            p.error("actual Sandbox ID and1..600seconds required")
        import modal
        result = transport(a.repo_root).collect(modal.Sandbox.from_id(a.sandbox_id), a.out, a.seconds)
    else:
        args = (a.repo_root, a.image_receipt, a.protocol, a.compute_plan, a.source_manifest, a.prior_exclusions)
        if a.plan_only:
            result = make_plan(*args)[0]
        else:
            if a.out is None:
                p.error("fresh --out required")
            result = run(*args, a.out)
    print(json.dumps(result, indent=2))
    return 0 if (a.action == "run" and a.plan_only) or result.get("complete") or result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
