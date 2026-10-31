#!/usr/bin/env python3
"""Prepare actual generic-isolab tool arguments offline; never dispatch them."""
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit

IMAGE = re.compile(r"[^\s]+@sha256:[0-9a-f]{64}")
HEX64 = re.compile(r"[0-9a-f]{64}")
MAX_BACKEND_ARGUMENT_BYTES = 8192


def prepare(image, source, build_info_path, protocol_path, input_uri, input_version,
            bundle_sha, manifest_sha, job_name, cpu=4, memory="12Gi", seconds=3600):
    if not IMAGE.fullmatch(image):
        raise ValueError("an actual published image at its registry digest is required")
    if not re.fullmatch(r"[0-9a-f]{40}", source):
        raise ValueError("a full actual code source revision is required")
    for value in (bundle_sha, manifest_sha):
        if not HEX64.fullmatch(value):
            raise ValueError("actual public bundle and manifest SHA-256 pins are required")
    uri = urlsplit(input_uri)
    if uri.scheme != "s3" or not uri.netloc or not uri.path.lstrip("/").startswith("inputs/") or uri.query or uri.fragment or not input_version or input_version == "null":
        raise ValueError("real version-pinned S3 inputs object required")
    if not re.fullmatch(r"[a-z0-9]([-a-z0-9]*[a-z0-9])?", job_name) or len(job_name) > 55:
        raise ValueError("invalid actual backend job name")
    if isinstance(cpu, bool) or not isinstance(cpu, int) or not 4 <= cpu <= 28 or cpu % 2:
        raise ValueError("request four or more even whole-core vCPUs")
    if not re.fullmatch(r"[1-9][0-9]*(Mi|Gi)", memory) or not 1 <= seconds <= 9999999:
        raise ValueError("invalid declared memory/deadline")
    build_raw, protocol_raw = Path(build_info_path).read_bytes(), Path(protocol_path).read_bytes()
    build, protocol = json.loads(build_raw), json.loads(protocol_raw)
    if build.get("schema") != "classical.ecdlp.endpoint-reuse.image-build/v1" or build["source_revision"] != source or not HEX64.fullmatch(build["binary_sha256"]):
        raise ValueError("actual built instrument identity is required")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run_experiment import protocol_read
    _, protocol_hash = protocol_read(protocol_path)
    for arm in protocol["arms"]:
        instrument = arm["instrument"]
        if instrument["commit"] != source or instrument["binary_sha256"] != build["binary_sha256"] or instrument.get("image_digest") != image:
            raise ValueError("protocol instrument/source/image differs from the actual launch pins")
    payload = {"schema": "classical.ecdlp.endpoint-reuse.worker-payload/v1",
               "source_revision": source, "image_uri": image,
               "build_info_sha256": hashlib.sha256(build_raw).hexdigest(),
               "public_bundle_s3_uri": input_uri, "public_bundle_s3_version_id": input_version,
               "public_bundle_sha256": bundle_sha, "inputs_manifest_sha256": manifest_sha,
               "protocol_bytes_sha256": hashlib.sha256(protocol_raw).hexdigest(),
               "protocol_content_encoding": "gzip",
               "protocol_gzip_base64": base64.b64encode(gzip.compress(protocol_raw, mtime=0)).decode()}
    command = ["python3", "/opt/study/execution/worker.py", "--payload-base64",
               base64.b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode()]
    if len(command[3].encode("utf-8")) > MAX_BACKEND_ARGUMENT_BYTES:
        raise ValueError("compressed worker payload exceeds backend 8192-byte command argument limit")
    request = {"job_name": job_name, "command": command, "image": image,
               "cpu": cpu, "memory": memory, "seconds": seconds, "retries": 0}
    shell_args = ["--image", image, "--name", job_name, "--cpu", str(cpu), "--memory", memory,
                  "--seconds", str(seconds), "--retries", "0", "--isolation-profile", "l2",
                  "--instance-type", "c8a.2xlarge", "--"] + command
    notes = {"schema": "classical.ecdlp.endpoint-reuse.prepared-launch/v1", "dispatched": False,
             "ready": False, "reason": "Offline preparation does not establish a registry object or an authorized live connection.",
             "tool": "isolab_k8s_run", "arguments": request, "protocol_sha256": protocol_hash,
             "official_shell_submit_job_arguments": shell_args,
             "generic_mcp_placement": "standard; instance_type/isolation_profile are not fields in this tool schema",
             "clock_qualification": "unknown; producer clocks remain wall_valid=false",
             "source_contract": "evidence/mcp-tools.json", "source_contract_commit": "ac14190f1ab825f0ab1760a093c43bdac8be5e61"}
    return request, notes


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("image", "source-revision", "build-info", "protocol", "input-uri", "input-version",
                 "input-bundle-sha256", "inputs-manifest-sha256", "job-name", "protocol-checker", "out"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--cpu", type=int, default=4)
    p.add_argument("--memory", default="12Gi")
    p.add_argument("--seconds", type=int, default=3600)
    a = p.parse_args()
    out = Path(a.out)
    note = out.with_suffix(out.suffix + ".prepared.json")
    if out.exists() or note.exists():
        p.error("fresh output paths required")
    # Run the repository's real semantic validator, never a local surrogate.
    checker = Path(a.protocol_checker).resolve()
    if checker.name != "experiment_protocol.py" or not checker.is_file():
        p.error("the actual tools/experiment_protocol.py checker is required")
    subprocess.run([sys.executable, str(checker), "validate", a.protocol], check=True)
    request, notes = prepare(a.image, a.source_revision, a.build_info, a.protocol,
                             a.input_uri, a.input_version, a.input_bundle_sha256,
                             a.inputs_manifest_sha256, a.job_name, a.cpu, a.memory, a.seconds)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(request, indent=2) + "\n")
    note.write_text(json.dumps(notes, indent=2) + "\n")
    print(json.dumps({"arguments_file": str(out), "metadata_file": str(note), "dispatched": False, "ready": False}))


if __name__ == "__main__":
    main()
