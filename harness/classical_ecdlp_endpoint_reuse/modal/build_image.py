#!/usr/bin/env python3
"""Build/probe the committed code-only Modal image; never run study targets."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepare_context import canonical, committed_files, sha, validate_context

BASE = "debian:bookworm-slim@sha256:7ff6ba31527b9e336162fa061746c366c4b2032f4d2cff2078bea43f78efe3f8"
PACKAGES = ["g++", "gcc", "libc6-dev", "python3", "python3-boto3", "ca-certificates", "procps", "util-linux"]
APP_NAME = "classical-ecdlp-validation"
ENVIRONMENT = "main"


def utc():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def provenance(root):
    """Called in the image after the original build-only script has completed."""
    root = Path(root)
    build_info = (root / "build-info.json").read_bytes()
    context = json.loads((root / "context-manifest.json").read_bytes())
    compilers = {}
    for name in ("gcc", "g++"):
        path = Path(shutil.which(name)).resolve()
        compilers[name] = {"path": str(path), "sha256": sha(path.read_bytes()),
                           "version": subprocess.check_output([name, "--version"], text=True).splitlines()[0]}
    value = {"schema": "classical.ecdlp.endpoint-reuse.modal-image-build/v1",
             "source_a_revision": context["source_a_revision"], "source_b_revision": context["source_b_revision"], "adapter_revision": context["source_b_revision"],
             "source_a_tree_sha256": context["source_a_tree_sha256"], "source_b_tree_sha256": context["source_b_tree_sha256"],
             "adapter_manifest_sha256": sha((root / "adapter-manifest.json").read_bytes()),
             "context_manifest_sha256": sha((root / "context-manifest.json").read_bytes()),
             "build_info_sha256": sha(build_info), "binary_sha256": json.loads(build_info)["binary_sha256"],
             "compiler_executables": compilers, "scientific_workload_executed": False}
    write_json(root / "modal-image-build.json", value)
    return value


def plan(context, repo):
    manifest, context_hash = validate_context(context)
    # Recheck every selected source byte against the declared committed objects.
    native = committed_files(repo, manifest["source_a_revision"], manifest["package_path"])
    adapter = committed_files(repo, manifest["source_b_revision"], manifest["package_path"], adapter=True)
    if {item["path"] for item in manifest["files"]} != set(native) | set(adapter) | {"adapter-manifest.json"}:
        raise ValueError("context file set differs from committed code-only selection")
    expected_adapter = {"schema": "classical.ecdlp.endpoint-reuse.modal-adapter-manifest/v1",
                        "source_a_revision": manifest["source_a_revision"], "source_b_revision": manifest["source_b_revision"],
                        "adapter_revision": manifest["source_b_revision"], "files": {k: sha(v) for k, v in sorted(adapter.items())}}
    expected_adapter_bytes = json.dumps(expected_adapter, indent=2, allow_nan=False).encode() + b"\n"
    if ((Path(context) / "payload/adapter-manifest.json").read_bytes() != expected_adapter_bytes
            or manifest["adapter_manifest_sha256"] != sha(expected_adapter_bytes)):
        raise ValueError("adapter manifest differs from committed adapter closure")
    for rel, data in {**native, **adapter}.items():
        if (Path(context) / "payload" / rel).read_bytes() != data:
            raise ValueError("context differs from committed blob: " + rel)
    for item in manifest["files"]:
        rel = item["path"]
        expected_commit = manifest["source_a_revision"] if rel in native else manifest["source_b_revision"] if rel in adapter else None
        if item.get("source_commit") != expected_commit:
            raise ValueError("context per-file source commit differs: " + rel)
    expected_a = sha(canonical({k: sha(v) for k, v in sorted(native.items())}))
    expected_b = sha(canonical({k: sha(v) for k, v in sorted(adapter.items())}))
    if manifest["source_a_tree_sha256"] != expected_a or manifest["source_b_tree_sha256"] != expected_b:
        raise ValueError("source tree digest differs from committed objects")
    return {"schema": "classical.ecdlp.endpoint-reuse.modal-image-plan/v1", "base_image": BASE,
            "app_name": APP_NAME, "environment_name": ENVIRONMENT, "context_manifest_sha256": context_hash,
            "packages": PACKAGES, "copy": True, "source_revision": manifest["source_a_revision"],
            "source_a_revision": manifest["source_a_revision"], "source_b_revision": manifest["source_b_revision"], "adapter_revision": manifest["source_b_revision"],
            "source_a_tree_sha256": expected_a, "source_b_tree_sha256": expected_b,
            "adapter_manifest_sha256": manifest["adapter_manifest_sha256"],
            "runtime": "vm", "block_network": True, "requested_cpu": [2, 2], "requested_memory_mib": [12288, 12288],
            "scientific_workload_executed": False, "image_identity_kind": "Modal Image object ID, not OCI digest"}


def file_bytes(sb, remote):
    kind = sb.filesystem.stat(remote).type
    if getattr(kind, "value", kind) != "file":
        raise ValueError("expected regular remote file: " + remote)
    return sb.filesystem.read_bytes(remote)


def build(context, repo, output, modal_module=None):
    output = Path(output)
    if output.exists():
        raise ValueError("fresh build receipt directory required")
    selected = plan(context, repo)
    output.mkdir(parents=True)
    write_json(output / "plan.json", selected)
    if modal_module is None:
        import modal as modal_module
    receipt = {**selected, "schema": "classical.ecdlp.endpoint-reuse.modal-image-receipt/v1",
               "started_at": utc(), "sdk_version": modal_module.__version__, "completed": False,
               "l2_or_dedicated_physical_host_attested": False}
    sb = None
    try:
        if modal_module.__version__ != "1.6.2":
            raise ValueError("reviewed Modal SDK 1.6.2 required")
        app = modal_module.App.lookup(APP_NAME, environment_name=ENVIRONMENT, create_if_missing=True)
        receipt["app_id"] = app.app_id
        revision = shlex.quote(selected["source_revision"])
        image = (modal_module.Image.from_registry(BASE).apt_install(*PACKAGES)
                 .add_local_dir(Path(context) / "payload", "/opt/study", copy=True)
                 .run_commands("python3 /opt/study/execution/image_build.py --source-revision " + revision,
                               "python3 /opt/study/modal/build_image.py --write-provenance /opt/study",
                               "mkdir -p /work/tmp && chown -R 1000:1000 /work && chmod -R a-w /opt/study && chmod 0555 /usr/local/bin/endpoint_reuse")
                 .env({"PYTHONDONTWRITEBYTECODE": "1"}))
        image.build(app)
        receipt["image_id"] = receipt["modal_image_id"] = image.object_id
        write_json(output / "image-built.json", receipt)
        sb = modal_module.Sandbox.create("sleep", "600", app=app, image=modal_module.Image.from_id(image.object_id),
                                         timeout=600, runtime="vm", block_network=True, cpu=(1, 1), memory=(1024, 1024),
                                         secrets=[], include_oidc_identity_token=False, workdir="/work")
        receipt["sandbox_id"] = sb.object_id
        info = file_bytes(sb, "/opt/study/build-info.json")
        extra = file_bytes(sb, "/opt/study/modal-image-build.json")
        (output / "build-info.json").write_bytes(info)
        (output / "modal-image-build.json").write_bytes(extra)
        observed = json.loads(extra)
        if observed["build_info_sha256"] != sha(info) or observed["binary_sha256"] != json.loads(info)["binary_sha256"]:
            raise ValueError("image build identity mismatch")
        for key in ("source_a_revision", "source_b_revision", "source_a_tree_sha256", "source_b_tree_sha256", "adapter_manifest_sha256", "context_manifest_sha256"):
            if observed[key] != selected[key]:
                raise ValueError("image source provenance mismatch: " + key)
        receipt.update({"build_info_sha256": sha(info), "build_provenance_sha256": sha(extra),
                        "binary_sha256": observed["binary_sha256"],
                        "compiler_executable_sha256": {k: v["sha256"] for k, v in observed["compiler_executables"].items()}})
        argv = ["env", "-i", "PATH=/usr/local/bin:/usr/bin:/bin", "HOME=/work", "setpriv", "--reuid=1000", "--regid=1000", "--clear-groups", "--no-new-privs", "/usr/local/bin/endpoint_reuse", "--self-test"]
        proc = sb.exec(*argv, timeout=300)
        stdout, stderr = proc.stdout.read(), proc.stderr.read()
        code = proc.wait()
        (output / "self-test.stdout.txt").write_text(stdout)
        (output / "self-test.stderr.txt").write_text(stderr)
        receipt["software_probe"] = {"purpose": "native_self_test_only", "scientific_measurement": False,
                                      "argv": argv, "stdout_sha256": sha(stdout.encode()), "stderr_sha256": sha(stderr.encode()), "returncode": code}
        if code:
            raise ValueError("native image self-test failed")
        receipt["completed"] = True
    except Exception as error:
        receipt["error"] = {"type": type(error).__name__, "message": str(error)}
        raise
    finally:
        if sb is not None:
            try:
                sb.terminate()
                receipt["probe_termination_requested"] = True
            except Exception as error:
                receipt["probe_termination_error"] = type(error).__name__
        receipt["finished_at"] = utc()
        write_json(output / "receipt.json", receipt)
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--write-provenance", type=Path)
    p.add_argument("--context", type=Path)
    p.add_argument("--repo", type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--plan-only", action="store_true")
    a = p.parse_args()
    if a.write_provenance:
        print(json.dumps(provenance(a.write_provenance)))
    elif not a.context or not a.repo or (not a.out and not a.plan_only):
        p.error("--context, --repo and --out required (out optional with --plan-only)")
    else:
        print(json.dumps(plan(a.context, a.repo) if a.plan_only else build(a.context, a.repo, a.out), indent=2))


if __name__ == "__main__":
    main()
