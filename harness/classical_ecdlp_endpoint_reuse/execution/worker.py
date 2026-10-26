#!/usr/bin/env python3
"""Generic isolab image entrypoint: verify code and versioned public inputs."""
from __future__ import annotations
import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import time
from urllib.parse import urlsplit

HEX64 = re.compile(r"[0-9a-f]{64}")


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def safe_unpack(bundle, output):
    output = Path(output)
    if output.exists():
        raise ValueError("fresh public-input directory required")
    with tarfile.open(bundle, "r:gz") as tar:
        members = tar.getmembers()
        if len(members) > 10000 or sum(x.size for x in members) > 134217728:
            raise ValueError("public input archive exceeds declared bounds")
        seen = set()
        for member in members:
            name = PurePosixPath(member.name)
            if name.is_absolute() or ".." in name.parts or not name.parts or name.parts[0] != "public" or str(name) != member.name:
                raise ValueError("unsafe public input member")
            if member.name in seen or not member.isfile() or member.size > 1048576:
                raise ValueError("only unique bounded regular public files are allowed")
            seen.add(member.name)
        if "public/inputs-manifest.json" not in seen:
            raise ValueError("the public input manifest is absent")
        output.mkdir(parents=True)
        for member in members:
            dest = output / member.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open("xb") as target:
                source = tar.extractfile(member)
                if source is None:
                    raise ValueError("public input member is unreadable")
                while True:
                    chunk = source.read(1048576)
                    if not chunk:
                        break
                    target.write(chunk)
    return output / "public"


def verify_build(root, expected_build_sha, expected_source):
    root = Path(root)
    info_path = root / "build-info.json"
    if sha_file(info_path) != expected_build_sha:
        raise ValueError("image build-info hash differs from launch pins")
    info = json.loads(info_path.read_text())
    if info.get("schema") != "classical.ecdlp.endpoint-reuse.image-build/v1" or info["source_revision"] != expected_source:
        raise ValueError("image build identity differs from launch pins")
    for relative, expected in info["source_and_public_input_sha256"].items():
        name = PurePosixPath(relative)
        if name.is_absolute() or ".." in name.parts or sha_file(root / name) != expected:
            raise ValueError("a code-image file differs from build-info")
    binary = Path(info["binary"])
    if str(binary) != "/usr/local/bin/endpoint_reuse" or sha_file(binary) != info["binary_sha256"]:
        raise ValueError("observed production executable differs from build-info")
    return info


def seal_manifest(out, flow, info, protocol_hash, inputs_hash):
    out = Path(out)
    if flow.get("protocol_sha256", protocol_hash) != protocol_hash or flow.get("inputs_manifest_sha256", inputs_hash) != inputs_hash:
        raise ValueError("algorithm summary belongs to different protocol or inputs")
    return {"schema": "classical.ecdlp.endpoint-reuse.raw-manifest.v1", "flow": flow,
            "protocol_sha256": protocol_hash, "inputs_manifest_sha256": inputs_hash,
            "source_revision": info["source_revision"], "binary_sha256": info["binary_sha256"],
            "post_manifest_records": ["upload-status.json"],
            "files": [{"path": path.relative_to(out).as_posix(), "bytes": path.stat().st_size,
                       "sha256": sha_file(path)} for path in sorted(out.rglob("*")) if path.is_file()]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--payload-base64", required=True)
    a = p.parse_args()
    payload = json.loads(base64.b64decode(a.payload_base64, validate=True))
    if payload.get("schema") != "classical.ecdlp.endpoint-reuse.worker-payload/v1":
        p.error("wrong payload schema")
    for name in ("build_info_sha256", "public_bundle_sha256", "inputs_manifest_sha256", "protocol_bytes_sha256"):
        if not isinstance(payload.get(name), str) or HEX64.fullmatch(payload[name]) is None:
            p.error("actual SHA-256 launch pins are required")
    if re.fullmatch(r"[0-9a-f]{40}", payload.get("source_revision", "")) is None:
        p.error("actual immutable code source revision required")
    root = Path("/opt/study")
    info = verify_build(root, payload["build_info_sha256"], payload["source_revision"])
    protocol_raw = base64.b64decode(payload["protocol_base64"], validate=True)
    if hashlib.sha256(protocol_raw).hexdigest() != payload["protocol_bytes_sha256"]:
        p.error("protocol bytes differ from the launch request")
    protocol_path = Path("/work/protocol.json")
    with protocol_path.open("xb") as stream:
        stream.write(protocol_raw)
    sys.path.insert(0, str(root / "execution"))
    from run_experiment import protocol_read
    _, protocol_hash = protocol_read(protocol_path)
    uri = urlsplit(payload["public_bundle_s3_uri"])
    version = payload["public_bundle_s3_version_id"]
    if uri.scheme != "s3" or not uri.netloc or not uri.path.lstrip("/").startswith("inputs/") or uri.query or uri.fragment or not version or version == "null":
        p.error("a real version-pinned S3 inputs object is required")
    import boto3
    reply = boto3.client("s3").get_object(Bucket=uri.netloc, Key=uri.path.lstrip("/"), VersionId=version)
    if reply.get("VersionId") != version or reply["ContentLength"] > 67108864:
        p.error("input object version/size differs from launch pins")
    bundle = Path("/work/public-inputs.tar.gz")
    length = 0
    with bundle.open("xb") as stream:
        while True:
            chunk = reply["Body"].read(1048576)
            if not chunk:
                break
            length += len(chunk)
            if length > 67108864:
                raise ValueError("public input bundle exceeds bound")
            stream.write(chunk)
    if length != reply["ContentLength"] or sha_file(bundle) != payload["public_bundle_sha256"]:
        p.error("public input bundle content differs from launch pins")
    public = safe_unpack(bundle, "/work/inputs")
    argv = [sys.executable, str(root / "execution/run_experiment.py"),
            "--public-root", str(public), "--inputs-manifest-sha256", payload["inputs_manifest_sha256"],
            "--protocol", str(protocol_path), "--binary", info["binary"],
            "--source-revision", info["source_revision"], "--binary-sha256", info["binary_sha256"],
            "--out", os.environ["ISOLAB_OUTPUT_DIR"]]
    stdout_path, stderr_path = Path("/work/adapter.stdout.log"), Path("/work/adapter.stderr.log")
    from datetime import datetime, timezone
    started = datetime.now(timezone.utc).isoformat()
    signalled = {"number": None}
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        child = subprocess.Popen(argv, stdout=stdout, stderr=stderr)
        def forward(number, frame):
            signalled["number"] = number
            try:
                os.kill(child.pid, number)
            except ProcessLookupError:
                pass
        for number in (signal.SIGTERM, signal.SIGINT):
            signal.signal(number, forward)
        pid, status, usage = os.wait4(child.pid, 0)
        child.returncode = os.waitstatus_to_exitcode(status)
    out = Path(os.environ["ISOLAB_OUTPUT_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    for src, name in ((stdout_path, "adapter.stdout.log"), (stderr_path, "adapter.stderr.log"),
                      (protocol_path, "launch-protocol-bytes.json"), (root / "build-info.json", "build-info.json")):
        with (out / name).open("xb") as target:
            with src.open("rb") as source:
                shutil.copyfileobj(source, target)
    worker_record = {"schema": "classical.ecdlp.endpoint-reuse.worker-execution.v1",
                     "started_at": started, "finished_at": datetime.now(timezone.utc).isoformat(),
                     "argv": argv, "exitcode": child.returncode, "received_signal": signalled["number"],
                     "source_revision": info["source_revision"], "binary_sha256": info["binary_sha256"],
                     "protocol_sha256": protocol_hash,
                     "build_info_sha256": payload["build_info_sha256"],
                     "declared_image_uri": payload["image_uri"], "observed_image_id": None,
                     "input_fetch": {"uri": payload["public_bundle_s3_uri"], "version_id": reply["VersionId"],
                                     "bytes": length, "sha256": sha_file(bundle),
                                     "inputs_manifest_sha256": payload["inputs_manifest_sha256"]},
                     "rusage": {"user_seconds": usage.ru_utime, "system_seconds": usage.ru_stime,
                                "maxrss_raw": usage.ru_maxrss, "maxrss_unit": "KiB",
                                "maxrss_bytes": usage.ru_maxrss * 1024,
                                "scope": "entire orchestrator child including its waited-for native descendants"},
                     "clock": {"wall_valid": False, "reason": "No observed L2 grade is supplied by this wrapper."}}
    (out / "worker-execution.json").write_text(json.dumps(worker_record, indent=2) + "\n")
    original = out / "algorithm-raw-manifest.json"
    flow = json.loads(original.read_text())["flow"] if original.exists() else {
        "complete": False, "planned": 768, "attempted": None, "completed": None,
        "reason": "The algorithm adapter did not seal its final execution summary."}
    manifest = seal_manifest(out, flow, info, protocol_hash, payload["inputs_manifest_sha256"])
    (out / "raw-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    from storage import upload_tree
    upload = upload_tree(out)
    return child.returncode if upload["payload_upload_complete"] and upload["receipt_put_returned"] else 70


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        # Keep a refusal when possible without exposing SDK credentials or headers.
        out_env = os.environ.get("ISOLAB_OUTPUT_DIR")
        if out_env:
            out = Path(out_env)
            out.mkdir(parents=True, exist_ok=True)
            refusal = {"schema": "classical.ecdlp.endpoint-reuse.worker-refusal.v1",
                       "error_type": type(error).__name__, "measurement_success_claimed": False,
                       "reason": "Code/input/launcher preflight or adapter failed; retain worker logs and review the exact launch pins."}
            path = out / "worker-refusal.json"
            if not path.exists():
                path.write_text(json.dumps(refusal, indent=2) + "\n")
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from storage import upload_tree
            upload_tree(out)
        raise SystemExit(70)
