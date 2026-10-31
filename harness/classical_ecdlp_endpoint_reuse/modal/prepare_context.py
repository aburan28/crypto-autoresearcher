#!/usr/bin/env python3
"""Materialize a code-only Modal image context exclusively from committed blobs."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

PREFIX = "harness/classical_ecdlp_endpoint_reuse"
FORBIDDEN = {"private", "public", "development", "__pycache__", ".git", ".pytest_cache", "build", "target", "archive", "evidence"}
CODE_SUFFIXES = {".py", ".c", ".h", ".hpp", ".cpp", ".inc"}
REQUIRED_A = {"implementation/build.py", "implementation/vendor-source.json", "implementation/tests/self_test.inc", "execution/image_build.py", "execution/run_experiment.py", "cohort/public_inputs.py", "protocol/seed_rules.py"}
REQUIRED_B = {"modal/engine.py", "modal/controller.py", "modal/build_image.py", "modal/prepare_context.py"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def relative_path(value):
    path = PurePosixPath(value)
    if not value or value == "." or path.is_absolute() or ".." in path.parts or str(path) != value or "\\" in value or "\x00" in value:
        raise ValueError("unsafe relative path")
    return path


def allowed(rel, adapter=False):
    path = relative_path(rel)
    if FORBIDDEN.intersection(path.parts):
        return False
    if adapter:
        return path.parts[0] == "modal" and len(path.parts) == 2 and path.suffix == ".py" and not path.name.startswith("test_")
    if rel == "implementation/tests/self_test.inc":
        return True
    if "tests" in path.parts or path.name.startswith("test_"):
        return False
    return (path.parts[0] in {"implementation", "execution", "verification", "cohort", "protocol"}
            and (path.suffix in CODE_SUFFIXES or rel in {"implementation/vendor-source.json", "implementation/vendor/LICENSE"}))


def committed_files(repo, revision, package_path, adapter=False):
    if not re.fullmatch(r"[a-f0-9]{40}", revision):
        raise ValueError("full committed SHA required")
    prefix = relative_path(package_path)
    listing = subprocess.check_output(["git", "ls-tree", "-r", "-z", revision, "--", str(prefix)], cwd=repo)
    result = {}
    for record in listing.split(b"\0"):
        if not record:
            continue
        meta, raw = record.split(b"\t", 1)
        mode, kind, blob = meta.decode().split()
        full = raw.decode("utf-8")
        rel = PurePosixPath(full).relative_to(prefix).as_posix()
        if not allowed(rel, adapter):
            continue
        if mode not in {"100644", "100755"} or kind != "blob":
            raise ValueError("selected source must be a regular committed blob: " + rel)
        data = subprocess.check_output(["git", "cat-file", "blob", blob], cwd=repo)
        result[rel] = data
    required = REQUIRED_B if adapter else REQUIRED_A
    if not required.issubset(result):
        raise ValueError("committed package lacks required source: " + ", ".join(sorted(required - result.keys())))
    return result


def prepare(repo, source_revision, adapter_revision, output, package_path=PREFIX):
    output = Path(output)
    if output.exists():
        raise ValueError("fresh output directory required")
    native = committed_files(repo, source_revision, package_path)
    adapter = committed_files(repo, adapter_revision, package_path, adapter=True)
    hashes_a = {k: sha(v) for k, v in sorted(native.items())}
    hashes_b = {k: sha(v) for k, v in sorted(adapter.items())}
    adapter_manifest = {"schema": "classical.ecdlp.endpoint-reuse.modal-adapter-manifest/v1",
                        "source_a_revision": source_revision, "source_b_revision": adapter_revision, "adapter_revision": adapter_revision, "files": hashes_b}
    adapter_bytes = json.dumps(adapter_manifest, indent=2, allow_nan=False).encode() + b"\n"
    files = {**native, **adapter, "adapter-manifest.json": adapter_bytes}
    manifest = {"schema": "classical.ecdlp.endpoint-reuse.modal-context/v1", "source_revision": source_revision,
                "source_a_revision": source_revision, "source_b_revision": adapter_revision, "adapter_revision": adapter_revision, "package_path": package_path,
                "source_a_tree_sha256": sha(canonical(hashes_a)), "source_b_tree_sha256": sha(canonical(hashes_b)),
                "adapter_manifest_sha256": sha(adapter_bytes), "private_input_files_included": False,
                "working_tree_bytes_used": False,
                "files": [{"path": k, "bytes": len(v), "sha256": sha(v),
                           "source_commit": adapter_revision if k in adapter else source_revision if k in native else None,
                           "origin": "committed_adapter_blob" if k in adapter else "committed_native_or_helper_blob" if k in native else "generated_adapter_manifest"}
                          for k, v in sorted(files.items())]}
    data = json.dumps(manifest, indent=2, allow_nan=False).encode() + b"\n"
    output.mkdir(parents=True)
    for name, body in files.items():
        dest = output / "payload" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(body)
    (output / "context-manifest.json").write_bytes(data)
    (output / "payload/context-manifest.json").write_bytes(data)
    return manifest


def validate_context(output):
    output = Path(output)
    raw = (output / "context-manifest.json").read_bytes()
    manifest = json.loads(raw)
    if manifest.get("schema") != "classical.ecdlp.endpoint-reuse.modal-context/v1":
        raise ValueError("wrong context schema")
    expected = {"context-manifest.json"}
    for entry in manifest["files"]:
        rel = relative_path(entry["path"])
        if str(rel) != "adapter-manifest.json" and not allowed(str(rel)) and not allowed(str(rel), adapter=True):
            raise ValueError("non-source context file forbidden")
        if str(rel) in expected:
            raise ValueError("duplicate context path")
        expected.add(str(rel))
        path = output / "payload" / str(rel)
        if path.is_symlink() or not path.is_file() or path.stat().st_size != entry["bytes"] or sha(path.read_bytes()) != entry["sha256"]:
            raise ValueError("context file hash/type differs: " + str(rel))
    actual = set()
    for path in (output / "payload").rglob("*"):
        if path.is_symlink():
            raise ValueError("context symlinks forbidden")
        if path.is_file():
            actual.add(path.relative_to(output / "payload").as_posix())
    if actual != expected or (output / "payload/context-manifest.json").read_bytes() != raw:
        raise ValueError("unmanifested context bytes")
    return manifest, sha(raw)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", required=True)
    p.add_argument("--package-path", default=PREFIX)
    p.add_argument("--source-revision", required=True)
    p.add_argument("--adapter-revision", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    print(json.dumps(prepare(a.repo, a.source_revision, a.adapter_revision, a.output, a.package_path), indent=2))


if __name__ == "__main__":
    main()
