"""Packaging-only CI Put/Get proof and two fixed historical object downloads.

No collector, native trial, report-prefix write or credential export. Run only
from an exactly published source commit selected by workflow_dispatch.
"""
import argparse
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import gzip
from hashlib import sha256, shake_256
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[6]
REMOTE = "s3://setec-astronomy-artifacts/store"
OLD_RUN = "experiments/EXP-ECDLP-d6d8e8/runs/RUN-ECDLP-ea49a6"


def validate_pointer(pointer):
    digest = pointer.get("sha256")
    if (pointer.get("schema") != "crypto.autoresearch.blob_pointer.v1"
            or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
            or pointer.get("uri") != f"{REMOTE}/sha256/{digest[:2]}/{digest}"
            or pointer.get("encoding") != "gzip"):
        raise ValueError("invalid fixed canonical pointer")
    if any(type(pointer.get(key)) is not int or pointer[key] <= 0 for key in ("size", "content_size")):
        raise ValueError("invalid object sizes")
    return digest


def verify_object(pointer, path):
    """Verify both stored bytes and decompressed logical bytes, without math."""
    digest = validate_pointer(pointer)
    if path.stat().st_size != pointer["size"] or sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError("stored object digest/size mismatch")
    logical, size = sha256(), 0
    with gzip.open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            logical.update(block)
            size += len(block)
            if size > pointer["content_size"]:
                raise ValueError("logical object exceeds declared size")
    if (logical.hexdigest(), size) != (pointer["content_sha256"], pointer["content_size"]):
        raise ValueError("logical object digest/size mismatch")
    return dict(stored_sha256=digest, stored_bytes=path.stat().st_size,
                content_sha256=logical.hexdigest(), content_bytes=size,
                uri=pointer["uri"], fresh_get_verified=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-source-sha", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.expected_source_sha):
        raise ValueError("require exact published SHA")
    actual = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    if actual != args.expected_source_sha or os.environ.get("GITHUB_SHA", actual) != actual:
        raise ValueError("probe source commit mismatch")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    proof = dict(schema="prym-ci-storage-readiness/v1", task_id="TASK-20261026-351ddf",
                 source_commit=actual, run_id=os.environ.get("GITHUB_RUN_ID"),
                 workflow="reports-s3.yml", canonical_remote=REMOTE,
                 recorded_at=datetime.now(timezone.utc).isoformat(), python=platform.python_version(),
                 scientific_attempts=0, reports_prefix_writes=0,
                 credentials_exported=False, state="failed", stage="load_adapter", objects=[])
    try:
        module_path = ROOT / "research/prym_factor_base_width_20261025/execute_with_storage.py"
        spec = importlib.util.spec_from_file_location("ci_width_storage", module_path)
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        proof["probe_source_sha256"] = sha256(Path(__file__).read_bytes()).hexdigest()
        proof["adapter_sha256"] = sha256(module_path.read_bytes()).hexdigest()
        proof["stage"] = "native_pointer_probe"
        # The frozen positive control exercises CLI push/remote verify/fresh GET
        # and native pointer roundtrip. Its object can already exist remotely.
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            if adapter.main(["probe"]):
                raise RuntimeError("native packaging control refused")
        probe_dir = ROOT / "research/prym_factor_base_width_20261025"
        probe = json.loads((probe_dir / "probe-result.json").read_text())
        if probe.get("status") != "passed":
            raise RuntimeError("native packaging control failed")
        shutil.copyfile(probe_dir / "probe-result.json", output / "native-probe.json")
        shutil.copyfile(probe_dir / "probe-native/payload.bin.gz.blob.json", output / "native-probe.blob.json")

        proof["stage"] = "fresh_conditional_put_and_get"
        # A distinct public nonce avoids mistaking HEAD/GET of the old positive
        # control for proof that this identity can actually PutObject now.
        nonce = uuid.uuid4().hex
        seed = f"prym-width-ci-public-storage-control-v1|{actual}|{nonce}"
        payload = shake_256(seed.encode()).digest(90000)
        fresh_dir = probe_dir / "ci-fresh-delivery"
        fresh_dir.mkdir(exist_ok=False)
        source = fresh_dir / "public-payload.bin"
        source.write_bytes(payload)
        publisher = adapter.Publisher(fresh_dir / "canonical")
        publisher.initialize()
        digest = sha256(payload).hexdigest()
        with redirect_stderr(io.StringIO()):
            sent = publisher.remote.put(digest, source, len(payload))
            if sent is not True:
                raise RuntimeError("fresh public object was not newly uploaded")
            uri = publisher.put(source, digest)
        proof["fresh_write"] = dict(public_seed=seed, sha256=digest, bytes=len(payload),
                                    new_conditional_put_confirmed=True, uri=uri,
                                    canonical_cli_manifest_verified=True,
                                    fresh_get_sha256_verified=publisher.entries[-1]["fresh_get_sha256_verified"])
        shutil.copyfile(fresh_dir / "canonical/.artifacts.json", output / "fresh-write.artifacts.json")
        proof["stage"] = "hydrate_two_fixed_historical_objects"
        for name in ("raw-result.json", "events.jsonl"):
            pointer_path = ROOT / OLD_RUN / (name + ".gz.blob.json")
            pointer_bytes = pointer_path.read_bytes()
            pointer = json.loads(pointer_bytes)
            validate_pointer(pointer)
            target = output / (name + ".gz")
            with redirect_stderr(io.StringIO()):
                publisher.remote.get(pointer["sha256"], target)
            record = verify_object(pointer, target)
            if pointer_path.read_bytes() != pointer_bytes:
                raise RuntimeError("historical pointer changed")
            record.update(pointer_path=str(pointer_path.relative_to(ROOT)),
                          pointer_sha256=sha256(pointer_bytes).hexdigest(), local_file=target.name)
            proof["objects"].append(record)
        proof.update(state="passed", stage="complete", actual_put_get_verified=True,
                     historical_objects_hydrated=2,
                     limits="CI identity only; no local credentials, scientific approval or computation proof supplied.")
    except (Exception, SystemExit) as error:
        # Retain a safe failure record; remote/SDK exceptions may carry URLs or
        # credential diagnostics, so never export their full message or env.
        proof["error_type"] = type(error).__name__
    finally:
        (output / "storage-readiness.json").write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps({"state": proof["state"], "stage": proof["stage"],
                      "source_commit": actual, "scientific_attempts": 0}))
    return 0 if proof["state"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
