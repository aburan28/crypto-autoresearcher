#!/usr/bin/env python3
"""One-attempt Modal VM controller with public-only staging and sealed collection."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import stat
import subprocess
import sys
import tarfile
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepare_context import relative_path, sha
from build_image import APP_NAME, ENVIRONMENT, file_bytes, write_json

SCHEMA = "classical.ecdlp.endpoint-reuse.modal-provider-context/v1"
MAX_PUBLIC_BYTES = 512 * 1024 * 1024
MAX_PUBLIC_FILES = 1024
ARCHIVE_PART_BYTES = 64 * 1024 * 1024
MAX_OUTPUT_BYTES = 50 * 1024 * 1024 * 1024


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha_file(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def frozen_protocol(path):
    value = json.loads(Path(path).read_bytes())
    body = {k: v for k, v in value.items() if k != "freeze"}
    digest = sha(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode())
    freeze = value.get("freeze", {})
    if value.get("schema") != "experiment.protocol/v1" or freeze.get("status") != "frozen" or freeze.get("protocol_sha256") != digest or freeze.get("filed_before_affected_data") is not True:
        raise ValueError("actual frozen protocol required")
    execution = value["execution"]
    if execution["backend"] != "modal" or execution["checkpoint"]["policy"] != "none" or execution["retries"]["max_attempts"] != 1:
        raise ValueError("Modal, no restore and exactly one attempt required")
    placement = execution["placement"]
    keys = ("sandbox_timeout_seconds", "command_timeout_seconds", "staging_timeout_seconds", "collection_grace_seconds")
    limits = {k: placement[k] for k in keys}
    if any(type(v) is not int or v <= 0 for v in limits.values()):
        raise ValueError("frozen positive integer operational deadlines required")
    if (limits["sandbox_timeout_seconds"] > 5400 or limits["command_timeout_seconds"] > 4200
            or limits["staging_timeout_seconds"] > 600 or limits["collection_grace_seconds"] > 600
            or limits["sandbox_timeout_seconds"] < sum(limits[k] for k in keys[1:])):
        raise ValueError("operational deadline exceeds route watchdogs or omits staging/collection time")
    if execution["timeout_seconds"] != 3600 or placement["child_timeout_seconds"] != 3600:
        raise ValueError("registered scientific watchdogs must stay 3600 seconds")
    return value, digest, limits


def inspect_public_tar(path):
    """Validate the entire archive before extraction; accept public regular files only."""
    names, sizes, digests, total = set(), {}, {}, 0
    with tarfile.open(path, "r:gz") as archive:
        for member in archive:
            rel = relative_path(member.name)
            if rel.parts[0] != "public" or len(rel.parts) < 2 or member.name in names or not member.isfile():
                raise ValueError("public archive requires unique regular files under public/")
            if {"private", ".git", "__pycache__", "credentials", "secrets"}.intersection(rel.parts):
                raise ValueError("forbidden public archive path")
            names.add(member.name)
            total += member.size
            if member.size < 0 or total > MAX_PUBLIC_BYTES or len(names) > MAX_PUBLIC_FILES:
                raise ValueError("public archive exceeds transport safety bound")
            sizes[member.name] = member.size
            stream = archive.extractfile(member)
            digest = hashlib.sha256()
            with stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
            digests[member.name] = digest.hexdigest()
    if not names or "public/inputs-manifest.json" not in names:
        raise ValueError("sealed public inputs manifest missing")
    with tarfile.open(path, "r:gz") as archive:
        manifest = json.loads(archive.extractfile("public/inputs-manifest.json").read())
    if manifest.get("schema") != "classical.ecdlp.endpoint-public-inputs/v1":
        raise ValueError("public input manifest schema required")
    declared = {"public/inputs-manifest.json"}
    for item in manifest["files"]:
        name = "public/" + str(relative_path(item["path"]))
        if name in declared or sizes.get(name) != item["bytes"] or digests.get(name) != item["sha256"]:
            raise ValueError("public archive file hash/size differs from sealed manifest")
        declared.add(name)
    if declared != names:
        raise ValueError("public archive contains missing or undeclared bytes")
    return {"files": len(names), "uncompressed_bytes": total}


def unpack_public(path, destination):
    inspect_public_tar(path)
    destination = Path(destination)
    if destination.exists():
        raise ValueError("fresh unpack destination required")
    destination.mkdir(parents=True)
    with tarfile.open(path, "r:gz") as archive:
        for member in archive:
            dest = destination / member.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(member) as source, dest.open("xb") as target:
                while block := source.read(1024 * 1024):
                    target.write(block)
            dest.chmod(0o444)


def image_receipt(path):
    value = json.loads(Path(path).read_bytes())
    if value.get("schema") != "classical.ecdlp.endpoint-reuse.modal-image-receipt/v1" or value.get("completed") is not True:
        raise ValueError("completed actual image build/software-probe receipt required")
    for key, prefix in (("app_id", "ap-"), ("image_id", "im-")):
        if not re.fullmatch(re.escape(prefix) + r"[A-Za-z0-9]+", value.get(key, "")):
            raise ValueError("real Modal identity required: " + key)
    for key in ("source_a_revision", "source_b_revision"):
        if not re.fullmatch(r"[a-f0-9]{40}", value.get(key, "")):
            raise ValueError("actual committed source revision required")
    for key in ("source_a_tree_sha256", "source_b_tree_sha256", "adapter_manifest_sha256", "context_manifest_sha256", "build_info_sha256", "build_provenance_sha256", "binary_sha256"):
        if not re.fullmatch(r"[a-f0-9]{64}", value.get(key, "")):
            raise ValueError("actual image/source hash required: " + key)
    if (value.get("runtime") != "vm" or value.get("block_network") is not True
            or value.get("requested_cpu") != [2, 2] or value.get("requested_memory_mib") != [12288, 12288]
            or value.get("app_name") != APP_NAME or value.get("environment_name") != ENVIRONMENT
            or value.get("software_probe", {}).get("returncode") != 0):
        raise ValueError("image receipt route/software probe differs")
    return value


def make_plan(receipt_path, protocol_path, bundle_path, inputs_manifest_sha256):
    receipt = image_receipt(receipt_path)
    protocol, protocol_hash, limits = frozen_protocol(protocol_path)
    if not re.fullmatch(r"[a-f0-9]{64}", inputs_manifest_sha256):
        raise ValueError("public manifest SHA-256 required")
    bundle = Path(bundle_path)
    bundle_shape = inspect_public_tar(bundle)
    with tarfile.open(bundle, "r:gz") as archive:
        manifest_bytes = archive.extractfile("public/inputs-manifest.json").read()
    if sha(manifest_bytes) != inputs_manifest_sha256:
        raise ValueError("bundle public manifest hash differs")
    manifest = json.loads(manifest_bytes)
    if manifest.get("protocol_sha256") != protocol_hash:
        raise ValueError("public bundle belongs to another protocol")
    for arm in protocol["arms"]:
        instrument = arm["instrument"]
        if instrument["commit"] != receipt["source_a_revision"] or instrument["binary_sha256"] != receipt["binary_sha256"] or instrument["threads"] != 1:
            raise ValueError("protocol must pin built native binary/source and one compute worker")
    # Placement identity keys are deliberately distinct from an OCI image digest.
    placement = protocol["execution"]["placement"]
    for key in ("app_id", "image_id"):
        if placement.get(key) != receipt[key]:
            raise ValueError("frozen placement identity differs: " + key)
    route = protocol.get("extensions", {}).get("modal_vm_route", {})
    for field, expected in (("native_source_a", receipt["source_a_revision"]), ("adapter_source_b", receipt["source_b_revision"]),
                            ("source_a_tree_sha256", receipt["source_a_tree_sha256"]), ("source_b_tree_sha256", receipt["source_b_tree_sha256"]),
                            ("adapter_manifest_sha256", receipt["adapter_manifest_sha256"]), ("context_manifest_sha256", receipt["context_manifest_sha256"])):
        if route.get(field) != expected:
            raise ValueError("frozen route pin differs: " + field)
    if route.get("build_info", {}).get("sha256") != receipt["build_info_sha256"] or route.get("image_receipt", {}).get("sha256") != sha_file(receipt_path):
        raise ValueError("frozen route build-info/image-receipt pin differs")
    if placement.get("runtime") != "vm" or placement.get("block_network") is not True or placement.get("requested_cpu_physical_cores") != [2, 2] or placement.get("requested_memory_mib") != [12288, 12288]:
        raise ValueError("frozen route resources/runtime/network differ")
    return {"schema": "classical.ecdlp.endpoint-reuse.modal-run-plan/v1", "measurement_started": False,
            "app_name": APP_NAME, "environment_name": ENVIRONMENT, "app_id": receipt["app_id"], "image_id": receipt["image_id"],
            "runtime": "vm", "block_network": True, "requested_cpu": [2, 2], "requested_memory_mib": [12288, 12288],
            "source_revision": receipt["source_a_revision"], "adapter_revision": receipt["source_b_revision"],
            **{k: receipt[k] for k in ("source_a_revision", "source_b_revision", "source_a_tree_sha256", "source_b_tree_sha256", "binary_sha256", "build_info_sha256", "build_provenance_sha256", "adapter_manifest_sha256")},
            "protocol_sha256": protocol_hash, "protocol_file_sha256": sha_file(protocol_path),
            "inputs_manifest_sha256": inputs_manifest_sha256, "public_bundle_sha256": sha_file(bundle),
            "public_bundle_bytes": bundle.stat().st_size, "public_bundle_shape": bundle_shape,
            "lifecycle": limits, "maximum_sandbox_creates": 1, "scientific_retries": 0, "restore": False,
            "l2_or_dedicated_physical_host_attested": False}


def deadline_call(call, deadline):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("operational transport deadline expired")
    pool = ThreadPoolExecutor(max_workers=1)
    future = pool.submit(call)
    try:
        return future.result(timeout=remaining)
    finally:
        pool.shutdown(wait=False, cancel_futures=True)


def stage_bytes(sb, data, remote, deadline):
    deadline_call(lambda: sb.filesystem.write_bytes(data, remote), deadline)
    observed = deadline_call(lambda: file_bytes(sb, remote), deadline)
    if sha(observed) != sha(data):
        raise ValueError("Sandbox stage readback differs: " + remote)
    return {"path": remote, "bytes": len(data), "sha256": sha(data), "readback_verified": True}


def engine_argv(plan):
    return ["python3", "/opt/study/modal/engine.py", "--public-root", "/work/input/public",
            "--inputs-manifest-sha256", plan["inputs_manifest_sha256"], "--protocol", "/work/stage/protocol.json",
            "--binary", "/usr/local/bin/endpoint_reuse", "--source-revision", plan["source_revision"],
            "--binary-sha256", plan["binary_sha256"], "--out", "/work/result/raw", "--provider-context", "/work/stage/provider-context.json"]


def sandbox_prepare(spec_path):
    """Non-scientific in-VM unpack and privilege preparation, before engine exec."""
    spec = json.loads(Path(spec_path).read_bytes())
    for name, expected in spec["stage_hashes"].items():
        if sha_file("/work/stage/" + str(relative_path(name))) != expected:
            raise ValueError("staged bytes differ before unpack")
    unpack_public("/work/stage/public.tar.gz", "/work/input")
    if sha_file("/work/input/public/inputs-manifest.json") != spec["plan"]["inputs_manifest_sha256"]:
        raise ValueError("unpacked public manifest differs")
    Path("/work/result").mkdir()
    Path("/work/tmp").mkdir(exist_ok=True)
    for path in [Path("/work"), *Path("/work").rglob("*")]:
        if path.is_symlink():
            raise ValueError("work tree links forbidden")
        os.chown(path, 1000, 1000)
    write_json("/work/stage/prepared.json", {"prepared": True, "inputs_manifest_sha256": spec["plan"]["inputs_manifest_sha256"]})


def sandbox_launch(spec_path):
    """Run exactly one engine process; retain both streams and seal failures too."""
    spec = json.loads(Path(spec_path).read_bytes())
    result = Path("/work/result")
    # A durable exclusive sentinel makes a second call refuse rather than rerun.
    with (result / "launch-started.json").open("x") as stream:
        json.dump({"started_at": utc(), "argv": spec["engine_argv"], "attempts": 1}, stream)
    invocation = ["env", "-i", "PATH=/usr/local/bin:/usr/bin:/bin", "HOME=/work", "TMPDIR=/work/tmp", "PYTHONDONTWRITEBYTECODE=1",
                  "setpriv", "--reuid=1000", "--regid=1000", "--clear-groups", "--no-new-privs", *spec["engine_argv"]]
    record = {"started_at": utc(), "argv": invocation, "attempts": 1, "resumed": False}
    code = 125
    try:
        with (result / "engine.stdout.log").open("xb") as stdout, (result / "engine.stderr.log").open("xb") as stderr:
            code = subprocess.call(invocation, cwd="/work", stdout=stdout, stderr=stderr)
        record["returncode"] = code
    except BaseException as error:
        record["error"] = {"type": type(error).__name__, "message": str(error)}
    finally:
        record["finished_at"] = utc()
        write_json(result / "engine-return.json", record)
        cleanup = quiesce_study_processes()
        write_json(result / "process-cleanup.json", cleanup)
        if not cleanup["quiescent"]:
            raise RuntimeError("UID1000 process quiescence not established; final seal refused")
        files = []
        for path in sorted(result.rglob("*")):
            if path.is_symlink() or (not path.is_file() and not path.is_dir()):
                raise ValueError("output tree contains unsupported type")
            if path.is_file():
                files.append({"path": path.relative_to(result).as_posix(), "bytes": path.stat().st_size, "sha256": sha_file(path)})
        write_json(result / "output-manifest.json", {"schema": "classical.ecdlp.endpoint-reuse.modal-output-manifest/v1",
                                                    "sealed_at": utc(), "engine_returncode": record.get("returncode"),
                                                    "study_uid1000_quiescent": True,
                                                    "process_cleanup_sha256": sha_file(result / "process-cleanup.json"),
                                                    "files": files, "includes_failure_and_partial_streams": True})
        seal_archive(result, Path("/work/seal"))
    return code


def study_processes():
    """UID1000 is reserved to this study in the single-purpose VM guest."""
    observations, errors = [], []
    for path in Path("/proc").iterdir():
        if not path.name.isdigit():
            continue
        try:
            text = (path / "status").read_text()
            fields = dict(line.split(":", 1) for line in text.splitlines() if ":" in line)
            uids = [int(value) for value in fields["Uid"].split()]
            if 1000 not in uids:
                continue
            state = fields["State"].split()[0]
            # /proc/PID/stat's command may contain spaces/parentheses.
            suffix = (path / "stat").read_text().rsplit(")", 1)[1].split()
            observations.append({"pid": int(path.name), "state": state, "uids": uids,
                                 "start_ticks": int(suffix[19]), "live": state not in {"Z", "X"}})
        except FileNotFoundError:
            continue
        except (OSError, ValueError, KeyError, IndexError) as error:
            errors.append({"pid": int(path.name), "type": type(error).__name__})
    return observations, errors


def quiesce_study_processes():
    record = {"schema": "classical.ecdlp.endpoint-reuse.modal-process-cleanup/v1", "started_at": utc(),
              "reserved_uid": 1000, "observations": [], "signals": [], "errors": [], "quiescent": False}
    for number, grace in ((signal.SIGTERM, 20), (signal.SIGKILL, 20)):
        observed, errors = study_processes()
        record["observations"].append({"phase": signal.Signals(number).name, "processes": observed})
        record["errors"].extend(errors)
        for item in observed:
            if not item["live"]:
                continue
            try:
                # Recheck identity immediately before signalling a possibly reused PID.
                current, current_errors = study_processes()
                record["errors"].extend(current_errors)
                if any(value["pid"] == item["pid"] and value["start_ticks"] == item["start_ticks"] and value["live"] for value in current):
                    os.kill(item["pid"], number)
                    record["signals"].append({"pid": item["pid"], "start_ticks": item["start_ticks"], "signal": int(number)})
            except ProcessLookupError:
                pass
            except OSError as error:
                record["errors"].append({"pid": item["pid"], "type": type(error).__name__})
        deadline = time.monotonic() + grace
        while True:
            observed, errors = study_processes()
            record["errors"].extend(errors)
            if not any(item["live"] for item in observed) or time.monotonic() >= deadline:
                break
            time.sleep(0.1)
        if not any(item["live"] for item in observed):
            break
    # Two observations after child shutdown establish stable quiescence before
    # any file hashing/archive creation; zombies cannot write files.
    for ordinal in range(2):
        observed, errors = study_processes()
        record["observations"].append({"phase": "final", "ordinal": ordinal, "processes": observed})
        record["errors"].extend(errors)
        if any(item["live"] for item in observed):
            break
    else:
        record["quiescent"] = not record["errors"]
    record["finished_at"] = utc()
    return record


def seal_archive(result, destination):
    """Seal the complete raw tree; split transport parts below the SDK file limit."""
    result, destination = Path(result), Path(destination)
    destination.mkdir()
    archive_path = destination / "output.tar.gz"
    with archive_path.open("xb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w|") as archive:
                for path in sorted(result.rglob("*")):
                    if path.is_symlink() or (not path.is_file() and not path.is_dir()):
                        raise ValueError("output archive links/nonregular files forbidden")
                    if not path.is_file():
                        continue
                    info = tarfile.TarInfo(path.relative_to(result).as_posix())
                    info.size, info.mtime, info.mode = path.stat().st_size, 0, 0o444
                    info.uid, info.gid, info.uname, info.gname = 0, 0, "", ""
                    with path.open("rb") as stream:
                        archive.addfile(info, stream)
    parts = []
    with archive_path.open("rb") as stream:
        ordinal = 0
        while data := stream.read(ARCHIVE_PART_BYTES):
            name = f"part-{ordinal:05d}.bin"
            (destination / name).write_bytes(data)
            parts.append({"path": name, "bytes": len(data), "sha256": sha(data)})
            ordinal += 1
    record = {"schema": "classical.ecdlp.endpoint-reuse.modal-output-archive/v1", "sealed_at": utc(),
              "archive_sha256": sha_file(archive_path), "archive_bytes": archive_path.stat().st_size,
              "output_manifest_sha256": sha_file(result / "output-manifest.json"), "parts": parts}
    write_json(destination / "archive-receipt.json", record)
    return record


def unpack_output(archive_path, destination, expected_manifest_sha256):
    """Validate all names/types/hashes before producing an unpacked local raw tree."""
    names, total, manifest = {}, 0, None
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive:
            name = str(relative_path(member.name))
            if name in names or not member.isfile() or member.size < 0:
                raise ValueError("unsafe output archive type or duplicate")
            total += member.size
            if total > MAX_OUTPUT_BYTES or len(names) >= 2000000:
                raise ValueError("output archive exceeds transport safety bound")
            digest = hashlib.sha256()
            with archive.extractfile(member) as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
            names[name] = {"path": name, "bytes": member.size, "sha256": digest.hexdigest()}
        if "output-manifest.json" not in names or names["output-manifest.json"]["sha256"] != expected_manifest_sha256:
            raise ValueError("archive output manifest identity differs")
    with tarfile.open(archive_path, "r:gz") as archive:
        manifest = json.loads(archive.extractfile("output-manifest.json").read())
    if manifest.get("schema") != "classical.ecdlp.endpoint-reuse.modal-output-manifest/v1":
        raise ValueError("wrong sealed output manifest schema")
    if manifest.get("study_uid1000_quiescent") is not True or names.get("process-cleanup.json", {}).get("sha256") != manifest.get("process_cleanup_sha256"):
        raise ValueError("sealed output requires actual process-quiescence evidence")
    with tarfile.open(archive_path, "r:gz") as archive:
        if json.loads(archive.extractfile("process-cleanup.json").read()).get("quiescent") is not True:
            raise ValueError("process cleanup did not establish quiescence")
    expected = {}
    for entry in manifest["files"]:
        name = str(relative_path(entry["path"]))
        if name in expected or name == "output-manifest.json" or names.get(name) != entry:
            raise ValueError("sealed output member hash/size differs")
        expected[name] = entry
    if set(names) != set(expected) | {"output-manifest.json"}:
        raise ValueError("sealed archive contains unmanifested output")
    destination = Path(destination)
    if destination.exists():
        raise ValueError("fresh output unpack directory required")
    destination.mkdir()
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive:
            target = destination / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(member) as source, target.open("xb") as stream:
                while block := source.read(1024 * 1024):
                    stream.write(block)
    return manifest


def collect_archive(sb, output, deadline, record, receipt_bytes):
    receipt = json.loads(receipt_bytes)
    if receipt.get("schema") != "classical.ecdlp.endpoint-reuse.modal-output-archive/v1":
        raise ValueError("wrong output archive receipt schema")
    (output / "archive-receipt.json").write_bytes(receipt_bytes)
    seen, total = set(), 0
    archive_path = output / "output.tar.gz"
    with archive_path.open("xb") as stream:
        for ordinal, part in enumerate(receipt["parts"]):
            name = str(relative_path(part["path"]))
            if name != f"part-{ordinal:05d}.bin" or name in seen or not 0 < part["bytes"] <= ARCHIVE_PART_BYTES:
                raise ValueError("invalid output archive part sequence")
            seen.add(name)
            remote = "/work/seal/" + name
            info = deadline_call(lambda: sb.filesystem.stat(remote), deadline)
            if getattr(info.type, "value", info.type) != "file" or info.size != part["bytes"]:
                raise ValueError("output archive part type/size differs")
            target = output / name
            deadline_call(lambda: sb.filesystem.copy_to_local(remote, target), deadline)
            if target.stat().st_size != part["bytes"] or sha_file(target) != part["sha256"]:
                raise ValueError("output archive part readback hash differs")
            with target.open("rb") as source:
                while block := source.read(1024 * 1024):
                    stream.write(block)
            total += part["bytes"]
            if total > MAX_OUTPUT_BYTES:
                raise ValueError("output archive exceeds transport bound")
            record["files"].append(part)
    if total != receipt["archive_bytes"] or sha_file(archive_path) != receipt["archive_sha256"]:
        raise ValueError("actual parent archive readback hash/length differs")
    manifest = unpack_output(archive_path, output / "tree", receipt["output_manifest_sha256"])
    record.update({"sealed": True, "complete": True, "archive_sha256": receipt["archive_sha256"],
                   "archive_bytes": total, "archive_receipt_sha256": sha(receipt_bytes),
                   "output_manifest_sha256": receipt["output_manifest_sha256"], "engine_returncode": manifest.get("engine_returncode"),
                   "tree_path": "tree", "raw_tree_files_verified": len(manifest["files"])})


def remote_files(sb, root, deadline):
    found = {}
    root_info = deadline_call(lambda: sb.filesystem.stat(root), deadline)
    if getattr(root_info.type, "value", root_info.type) != "directory":
        raise ValueError("remote result root must be a directory")
    pending = [root]
    while pending:
        folder = pending.pop()
        entries = deadline_call(lambda: sb.filesystem.list_files(folder), deadline)
        for entry in entries:
            name = entry.name
            if not name or "/" in name or "\\" in name or name in {".", ".."}:
                raise ValueError("unsafe remote filesystem name")
            remote = folder + "/" + name
            rel = PurePosixPath(remote).relative_to(PurePosixPath(root)).as_posix()
            relative_path(rel)
            kind = getattr(entry.type, "value", entry.type)
            if kind == "directory":
                pending.append(remote)
            elif kind == "file":
                if rel in found:
                    raise ValueError("duplicate remote file")
                found[rel] = entry.size
            else:
                raise ValueError("remote symlink/nonregular output forbidden")
    return found


def collect(sb, output, seconds=600):
    """Collect only; never launches/retries an engine or creates a Sandbox."""
    output = Path(output)
    if output.exists():
        raise ValueError("fresh collection directory required")
    output.mkdir(parents=True)
    deadline = time.monotonic() + seconds
    record = {"schema": "classical.ecdlp.endpoint-reuse.modal-collection/v1", "sandbox_id": sb.object_id,
              "started_at": utc(), "sealed": False, "complete": False, "files": []}
    try:
        try:
            archive_receipt = deadline_call(lambda: file_bytes(sb, "/work/seal/archive-receipt.json"), deadline)
        except Exception:
            archive_receipt = None
        if archive_receipt is not None:
            collect_archive(sb, output, deadline, record, archive_receipt)
            return record
        actual = remote_files(sb, "/work/result", deadline)
        manifest = None
        if "output-manifest.json" in actual:
            raw = deadline_call(lambda: file_bytes(sb, "/work/result/output-manifest.json"), deadline)
            (output / "output-manifest.json").write_bytes(raw)
            manifest = json.loads(raw)
            if manifest.get("schema") != "classical.ecdlp.endpoint-reuse.modal-output-manifest/v1":
                raise ValueError("wrong output manifest schema")
            expected = {}
            for entry in manifest["files"]:
                name = str(relative_path(entry["path"]))
                if name == "output-manifest.json" or name in expected or not re.fullmatch(r"[a-f0-9]{64}", entry["sha256"]):
                    raise ValueError("unsafe/duplicate output manifest entry")
                expected[name] = entry
            if set(actual) != set(expected) | {"output-manifest.json"}:
                raise ValueError("output manifest does not cover complete remote tree")
            record["sealed"] = True
            record["output_manifest_sha256"] = sha(raw)
        for name, size in sorted(actual.items()):
            if name == "output-manifest.json" and manifest is not None:
                continue
            target = output / name
            target.parent.mkdir(parents=True, exist_ok=True)
            remote = "/work/result/" + name
            # SDK streams to a local temporary file, avoiding a giant in-memory raw tree.
            deadline_call(lambda: sb.filesystem.copy_to_local(remote, target), deadline)
            item = {"path": name, "bytes": target.stat().st_size, "sha256": sha_file(target)}
            record["files"].append(item)
            if item["bytes"] != size or (manifest is not None and item != expected[name]):
                raise ValueError("collected size/hash differs: " + name)
        # A file snapshot preserves partial evidence; only exact parent-archive
        # collection proves the final seal required for automatic termination.
        record["complete"] = False
        if manifest is not None:
            record["engine_returncode"] = manifest.get("engine_returncode")
    except Exception as error:
        record["error"] = {"type": type(error).__name__, "message": str(error)}
    finally:
        record["finished_at"] = utc()
        write_json(output / "collection-receipt.json", record)
    return record


def run(receipt_path, protocol_path, bundle_path, inputs_manifest_sha256, output, modal_module=None):
    selected = make_plan(receipt_path, protocol_path, bundle_path, inputs_manifest_sha256)
    output = Path(output)
    if output.exists():
        raise ValueError("fresh controller output directory required")
    output.mkdir(parents=True)
    selected["sandbox_name"] = "ecdlp-" + uuid.uuid4().hex
    selected["engine_argv"] = engine_argv(selected)
    write_json(output / "plan.json", selected)
    record = {"schema": "classical.ecdlp.endpoint-reuse.modal-controller/v1", "started_at": utc(),
              "plan": selected, "sandbox_create_calls": 0, "engine_exec_calls": 0, "measurement_started": False,
              "termination_requested": False, "automatic_retry": False}
    sb = None
    if modal_module is None:
        import modal as modal_module
    try:
        if modal_module.__version__ != "1.6.2":
            raise ValueError("reviewed Modal SDK 1.6.2 required")
        app = modal_module.App.lookup(APP_NAME, environment_name=ENVIRONMENT, create_if_missing=False)
        if app.app_id != selected["app_id"]:
            raise ValueError("actual App differs from frozen image receipt")
        image = modal_module.Image.from_id(selected["image_id"])
        # Persist intent before the single possibly ambiguous create RPC.
        record["sandbox_create_calls"] = 1
        write_json(output / "create-intent.json", record)
        sb = modal_module.Sandbox.create("sleep", str(selected["lifecycle"]["sandbox_timeout_seconds"]), app=app,
                                        name=selected["sandbox_name"], image=image, runtime="vm", block_network=True,
                                        cpu=(2, 2), memory=(12288, 12288), timeout=selected["lifecycle"]["sandbox_timeout_seconds"],
                                        secrets=[], include_oidc_identity_token=False, workdir="/work")
        record["sandbox_id"] = sb.object_id
        record["app_id"] = app.app_id
        record["image_id"] = image.object_id
        write_json(output / "sandbox-created.json", record)
        deadline = time.monotonic() + selected["lifecycle"]["staging_timeout_seconds"]
        info = deadline_call(lambda: file_bytes(sb, "/opt/study/build-info.json"), deadline)
        adapter = deadline_call(lambda: file_bytes(sb, "/opt/study/adapter-manifest.json"), deadline)
        provenance = deadline_call(lambda: file_bytes(sb, "/opt/study/modal-image-build.json"), deadline)
        if sha(info) != selected["build_info_sha256"] or sha(adapter) != selected["adapter_manifest_sha256"] or sha(provenance) != selected["build_provenance_sha256"]:
            raise ValueError("actual Sandbox build/source differs from selected image")
        (output / "build-info.json").write_bytes(info)
        (output / "modal-image-build.json").write_bytes(provenance)
        context = {**selected, "schema": SCHEMA, "provider": "modal", "backend": "modal", "sandbox_id": sb.object_id,
                   "app_id": app.app_id, "image_id": image.object_id, "sdk_version": modal_module.__version__,
                   "build_info_path": "/opt/study/build-info.json", "adapter_manifest_path": "/opt/study/adapter-manifest.json",
                   "created_at": utc(), "no_workload_credentials": True, "isolation_level": "unknown"}
        write_json(output / "provider-context.json", context)
        context_bytes = (output / "provider-context.json").read_bytes()
        staged = [("public.tar.gz", Path(bundle_path).read_bytes()), ("protocol.json", Path(protocol_path).read_bytes()), ("provider-context.json", context_bytes)]
        spec = {"plan": selected, "engine_argv": selected["engine_argv"], "stage_hashes": {name: sha(data) for name, data in staged}}
        staged.append(("launch.json", json.dumps(spec, indent=2, allow_nan=False).encode() + b"\n"))
        record["staging"] = [stage_bytes(sb, data, "/work/stage/" + name, deadline) for name, data in staged]
        prep = deadline_call(lambda: sb.exec("python3", "/opt/study/modal/controller.py", "_prepare", "/work/stage/launch.json", timeout=max(1, int(deadline - time.monotonic()))), deadline)
        prep_code = deadline_call(prep.wait, deadline)
        (output / "prepare.stdout.log").write_text(deadline_call(prep.stdout.read, deadline))
        (output / "prepare.stderr.log").write_text(deadline_call(prep.stderr.read, deadline))
        if prep_code:
            raise ValueError("Sandbox public-stage preparation failed")
        record["engine_exec_calls"] = 1
        record["measurement_started"] = "submission_pending"
        write_json(output / "engine-intent.json", record)
        process = sb.exec("python3", "/opt/study/modal/controller.py", "_launch", "/work/stage/launch.json", timeout=selected["lifecycle"]["command_timeout_seconds"])
        record["measurement_started"] = True
        record["engine_command_returncode"] = process.wait()
    except Exception as error:
        record["error"] = {"type": type(error).__name__, "message": str(error)}
        record["submission_ambiguous"] = (record["sandbox_create_calls"] == 1 and sb is None) or record["measurement_started"] == "submission_pending"
    finally:
        if sb is not None:
            try:
                record["collection"] = collect(sb, output / "collected", selected["lifecycle"]["collection_grace_seconds"])
            except Exception as error:
                record["collection"] = {"complete": False, "error": {"type": type(error).__name__, "message": str(error)}}
            # Keep remote bytes alive after failed/unsealed collection; provider watchdog remains bounded.
            if record["collection"]["complete"]:
                try:
                    sb.terminate()
                    record["termination_requested"] = True
                except Exception as error:
                    record["termination_error"] = type(error).__name__
            else:
                record["sandbox_preserved_for_collection"] = True
        record["finished_at"] = utc()
        record["success"] = record.get("collection", {}).get("complete") is True and record["collection"].get("engine_returncode") == 0
        write_json(output / "controller-receipt.json", record)
    return record


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "_prepare":
        sandbox_prepare(sys.argv[2])
        return 0
    if len(sys.argv) == 3 and sys.argv[1] == "_launch":
        return sandbox_launch(sys.argv[2])
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="action", required=True)
    launch = sub.add_parser("run")
    launch.add_argument("--image-receipt", required=True, type=Path)
    launch.add_argument("--protocol", required=True, type=Path)
    launch.add_argument("--public-bundle", required=True, type=Path)
    launch.add_argument("--inputs-manifest-sha256", required=True)
    launch.add_argument("--out", type=Path)
    launch.add_argument("--plan-only", action="store_true")
    recovery = sub.add_parser("collect")
    recovery.add_argument("--sandbox-id", required=True)
    recovery.add_argument("--out", required=True, type=Path)
    recovery.add_argument("--seconds", type=int, default=600)
    a = p.parse_args()
    if a.action == "run":
        if not a.out and not a.plan_only:
            p.error("--out required for run")
        record = make_plan(a.image_receipt, a.protocol, a.public_bundle, a.inputs_manifest_sha256) if a.plan_only else run(a.image_receipt, a.protocol, a.public_bundle, a.inputs_manifest_sha256, a.out)
    else:
        if not re.fullmatch(r"sb-[A-Za-z0-9]+", a.sandbox_id) or not 1 <= a.seconds <= 600:
            p.error("actual Sandbox ID and 1..600 seconds required")
        import modal
        record = collect(modal.Sandbox.from_id(a.sandbox_id), a.out, a.seconds)
    print(json.dumps(record, indent=2))
    return 0 if (a.action == "run" and a.plan_only) or record.get("complete") or record.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
