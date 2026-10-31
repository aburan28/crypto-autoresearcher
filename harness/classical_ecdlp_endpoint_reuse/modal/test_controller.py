"""Offline transport and source-boundary checks; no SDK/account/scientific execution."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import controller
import prepare_context
import build_image


def digest(data):
    return hashlib.sha256(data).hexdigest()


class FakeFilesystem:
    def __init__(self, files=None, links=()):
        self.files = dict(files or {})
        self.links = set(links)
        self.corrupt_write = False

    def stat(self, path):
        if path in self.links:
            return SimpleNamespace(type="symlink", size=0)
        if path in self.files:
            return SimpleNamespace(type="file", size=len(self.files[path]))
        if any(name.startswith(path + "/") for name in self.files) or path == "/work/result":
            return SimpleNamespace(type="directory", size=0)
        raise FileNotFoundError(path)

    def list_files(self, root):
        children = {}
        for path in self.files.keys() | self.links:
            if not path.startswith(root + "/"):
                continue
            rest = path[len(root) + 1:]
            name = rest.split("/", 1)[0]
            full = root + "/" + name
            kind = "directory" if "/" in rest else "symlink" if full in self.links else "file"
            children[name] = SimpleNamespace(name=name, type=kind, size=len(self.files.get(full, b"")))
        return list(children.values())

    def read_bytes(self, path):
        return self.files[path]

    def write_bytes(self, data, path):
        self.files[path] = bytes(data) + (b"corrupt" if self.corrupt_write else b"")

    def copy_to_local(self, remote, local):
        local = Path(local)
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(self.files[remote])


class FakeSandbox:
    object_id = "sb-TestSynthetic"

    def __init__(self, files=None, links=()):
        self.filesystem = FakeFilesystem(files, links)
        self.terminations = 0
        self.exec_calls = []

    def exec(self, *argv, **kwargs):
        self.exec_calls.append((argv, kwargs))
        return SimpleNamespace(wait=lambda: 0, stdout=SimpleNamespace(read=lambda: ""), stderr=SimpleNamespace(read=lambda: ""))

    def terminate(self):
        self.terminations += 1


def fake_modal(sandbox=None, create_error=None):
    calls = []

    def create(*args, **kwargs):
        calls.append((args, kwargs))
        if create_error:
            raise create_error
        return sandbox

    return SimpleNamespace(
        __version__="1.6.2",
        App=SimpleNamespace(lookup=lambda *args, **kwargs: SimpleNamespace(app_id="ap-TestSynthetic")),
        Image=SimpleNamespace(from_id=lambda value: SimpleNamespace(object_id=value)),
        Sandbox=SimpleNamespace(create=create),
    ), calls


def synthetic_plan():
    return {
        "app_id": "ap-TestSynthetic", "image_id": "im-TestSynthetic", "source_revision": "a" * 40,
        "binary_sha256": "b" * 64, "inputs_manifest_sha256": "c" * 64,
        "build_info_sha256": digest(b"synthetic-build-info"),
        "build_provenance_sha256": digest(b"synthetic-provenance"),
        "adapter_manifest_sha256": digest(b"synthetic-adapter-manifest"),
        "lifecycle": {"sandbox_timeout_seconds": 30, "staging_timeout_seconds": 10,
                      "command_timeout_seconds": 10, "collection_grace_seconds": 10},
    }


class TarSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def archive(self, extras=()):
        archive = self.root / "synthetic-public.tar.gz"
        with tarfile.open(archive, "w:gz") as stream:
            manifest = {"schema": "classical.ecdlp.endpoint-public-inputs/v1",
                        "files": [{"path": name.removeprefix("public/"), "bytes": len(data), "sha256": digest(data)}
                                  for name, data, kind in extras if kind == tarfile.REGTYPE]}
            members = [("public/inputs-manifest.json", json.dumps(manifest).encode(), tarfile.REGTYPE), *extras]
            for name, data, kind in members:
                item = tarfile.TarInfo(name)
                item.type = kind
                item.size = len(data) if kind == tarfile.REGTYPE else 0
                if kind in (tarfile.SYMTYPE, tarfile.LNKTYPE):
                    item.linkname = "../../escape"
                stream.addfile(item, io.BytesIO(data) if kind == tarfile.REGTYPE else None)
        return archive

    def test_valid_synthetic_public_archive_roundtrip(self):
        archive = self.archive([("public/targets.tsv", b"synthetic-only\n", tarfile.REGTYPE)])
        shape = controller.inspect_public_tar(archive)
        self.assertEqual(shape["files"], 2)
        target = self.root / "unpacked"
        controller.unpack_public(archive, target)
        self.assertEqual((target / "public/targets.tsv").read_bytes(), b"synthetic-only\n")

    def test_traversal_absolute_links_and_duplicates_refused(self):
        cases = [
            ("../escape", b"x", tarfile.REGTYPE),
            ("/public/escape", b"x", tarfile.REGTYPE),
            ("public/../escape", b"x", tarfile.REGTYPE),
            ("public/link", b"", tarfile.SYMTYPE),
            ("public/link", b"", tarfile.LNKTYPE),
            ("public/device", b"", tarfile.CHRTYPE),
            ("public/inputs-manifest.json", b"duplicate", tarfile.REGTYPE),
            ("public/private/labels.tsv", b"x", tarfile.REGTYPE),
        ]
        for member in cases:
            with self.subTest(member=member):
                with self.assertRaises(ValueError):
                    controller.inspect_public_tar(self.archive([member]))
        self.assertFalse((self.root / "escape").exists())

    def test_public_transport_bounds_enforced(self):
        archive = self.archive([("public/targets.tsv", b"123", tarfile.REGTYPE)])
        with patch.object(controller, "MAX_PUBLIC_BYTES", 4):
            with self.assertRaises(ValueError):
                controller.inspect_public_tar(archive)
        with patch.object(controller, "MAX_PUBLIC_FILES", 1):
            with self.assertRaises(ValueError):
                controller.inspect_public_tar(archive)


class SourceBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.native = {name: ("native:" + name).encode() for name in prepare_context.REQUIRED_A}
        self.adapter = {name: ("adapter:" + name).encode() for name in prepare_context.REQUIRED_B}
        self.context = self.root / "context"
        with patch.object(prepare_context, "committed_files", side_effect=[self.native, self.adapter]):
            prepare_context.prepare(self.root, "a" * 40, "b" * 40, self.context)

    def test_allowlist_rejects_public_private_development_and_test_output(self):
        for name in ("cohort/public/targets.tsv", "cohort/private/labels.tsv", "implementation/development/out.cpp",
                     "execution/evidence/notes.py", "implementation/tests/rows.jsonl", "modal/test_controller.py"):
            self.assertFalse(prepare_context.allowed(name, adapter=name.startswith("modal/")), name)
        self.assertTrue(prepare_context.allowed("implementation/tests/self_test.inc"))

    def test_symlink_in_context_refused(self):
        victim = self.context / "payload/execution/image_build.py"
        victim.unlink()
        victim.symlink_to(self.context / "payload/implementation/build.py")
        with self.assertRaises(ValueError):
            prepare_context.validate_context(self.context)

    def test_committed_symlink_blob_refused(self):
        record = ("120000 blob " + "d" * 40 + "\t" + prepare_context.PREFIX + "/implementation/build.py\0").encode()
        with patch.object(prepare_context.subprocess, "check_output", return_value=record):
            with self.assertRaisesRegex(ValueError, "regular committed blob"):
                prepare_context.committed_files(self.root, "a" * 40, prepare_context.PREFIX)

    def test_extra_allowlisted_source_bytes_refused_before_upload(self):
        path = "execution/uncommitted_extra.py"
        body = b"synthetic-uncommitted-code"
        (self.context / "payload" / path).write_bytes(body)
        manifest = json.loads((self.context / "context-manifest.json").read_bytes())
        manifest["files"].append({"path": path, "bytes": len(body), "sha256": digest(body)})
        raw = json.dumps(manifest).encode()
        (self.context / "context-manifest.json").write_bytes(raw)
        (self.context / "payload/context-manifest.json").write_bytes(raw)
        with patch.object(build_image, "committed_files", side_effect=[self.native, self.adapter]):
            with self.assertRaises(ValueError):
                build_image.plan(self.context, self.root)

    def test_manifested_extra_context_bytes_refused_before_upload(self):
        path = "cohort/private/synthetic-secret.txt"
        body = b"synthetic-test-marker"
        (self.context / "payload" / path).parent.mkdir(parents=True)
        (self.context / "payload" / path).write_bytes(body)
        manifest = json.loads((self.context / "context-manifest.json").read_bytes())
        manifest["files"].append({"path": path, "bytes": len(body), "sha256": digest(body)})
        raw = json.dumps(manifest).encode()
        (self.context / "context-manifest.json").write_bytes(raw)
        (self.context / "payload/context-manifest.json").write_bytes(raw)
        with patch.object(build_image, "committed_files", side_effect=[self.native, self.adapter]):
            with self.assertRaises(ValueError):
                build_image.plan(self.context, self.root)


class TransferSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def synthetic_sealed_files(self):
        result = self.root / "synthetic-result"
        result.mkdir()
        (result / "engine.stdout.log").write_bytes(b"synthetic partial stdout\n")
        (result / "engine.stderr.log").write_bytes(b"synthetic retained error\n")
        (result / "process-cleanup.json").write_text(json.dumps({"quiescent": True}))
        manifest = {"schema": "classical.ecdlp.endpoint-reuse.modal-output-manifest/v1", "engine_returncode": 3,
                    "study_uid1000_quiescent": True, "process_cleanup_sha256": digest((result / "process-cleanup.json").read_bytes()),
                    "files": [{"path": path.name, "bytes": path.stat().st_size, "sha256": digest(path.read_bytes())}
                              for path in sorted(result.iterdir())]}
        (result / "output-manifest.json").write_text(json.dumps(manifest))
        seal = self.root / "synthetic-seal"
        controller.seal_archive(result, seal)
        return {"/work/seal/" + path.name: path.read_bytes() for path in seal.iterdir()}

    def test_archive_readback_retains_complete_failure_tree(self):
        sb = FakeSandbox(self.synthetic_sealed_files())
        target = self.root / "collected"
        record = controller.collect(sb, target)
        self.assertTrue(record["complete"])
        self.assertTrue(record["sealed"])
        self.assertEqual(record["engine_returncode"], 3)
        self.assertEqual((target / "tree/engine.stderr.log").read_bytes(), b"synthetic retained error\n")
        self.assertEqual(digest((target / "output.tar.gz").read_bytes()), record["archive_sha256"])

    def test_archive_part_corruption_prevents_complete_collection(self):
        files = self.synthetic_sealed_files()
        name = "/work/seal/part-00000.bin"
        files[name] = bytes([files[name][0] ^ 1]) + files[name][1:]
        record = controller.collect(FakeSandbox(files), self.root / "collected")
        self.assertFalse(record["complete"])
        self.assertIn("hash", record["error"]["message"])
        self.assertFalse((self.root / "collected/tree").exists())

    def test_output_archive_traversal_refused_before_unpack(self):
        archive_path = self.root / "unsafe-output.tar.gz"
        with tarfile.open(archive_path, "w:gz") as archive:
            item = tarfile.TarInfo("../escape")
            item.size = 1
            archive.addfile(item, io.BytesIO(b"x"))
        target = self.root / "tree"
        with self.assertRaises(ValueError):
            controller.unpack_output(archive_path, target, "a" * 64)
        self.assertFalse(target.exists())
        self.assertFalse((self.root / "escape").exists())

    def test_stage_requires_exact_readback(self):
        sb = FakeSandbox()
        import time
        record = controller.stage_bytes(sb, b"synthetic", "/work/stage/test", time.monotonic() + 10)
        self.assertTrue(record["readback_verified"])
        sb.filesystem.corrupt_write = True
        with self.assertRaises(ValueError):
            controller.stage_bytes(sb, b"synthetic", "/work/stage/test", time.monotonic() + 10)

    def test_cleanup_signals_only_observed_reserved_uid_process(self):
        process = {"pid": 12345, "state": "S", "uids": [1000] * 4, "start_ticks": 99, "live": True}
        with patch.object(controller, "study_processes", side_effect=[([process], []), ([process], []), ([], []), ([], []), ([], [])]), \
                patch.object(controller.os, "kill") as kill:
            result = controller.quiesce_study_processes()
        self.assertTrue(result["quiescent"])
        kill.assert_called_once_with(12345, controller.signal.SIGTERM)

    def test_cleanup_scan_error_refuses_quiescence(self):
        with patch.object(controller, "study_processes", return_value=([], [{"pid": 12345, "type": "PermissionError"}])), \
                patch.object(controller.os, "kill") as kill:
            result = controller.quiesce_study_processes()
        self.assertFalse(result["quiescent"])
        kill.assert_not_called()

    def test_remote_symlink_refused(self):
        sb = FakeSandbox(links={"/work/result/link"})
        record = controller.collect(sb, self.root / "collected")
        self.assertFalse(record["complete"])
        self.assertIn("symlink", record["error"]["message"])

    def test_ambiguous_create_does_not_retry(self):
        module, calls = fake_modal(create_error=TimeoutError("synthetic ambiguous create"))
        with patch.object(controller, "make_plan", return_value=synthetic_plan()):
            record = controller.run("unused", "unused", "unused", "c" * 64, self.root / "run", module)
        self.assertEqual(len(calls), 1)
        self.assertEqual(record["sandbox_create_calls"], 1)
        self.assertEqual(record["engine_exec_calls"], 0)
        self.assertTrue(record["submission_ambiguous"])
        self.assertTrue((self.root / "run/create-intent.json").exists())
        self.assertTrue((self.root / "run/controller-receipt.json").exists())

    def test_failed_collection_keeps_sandbox_alive(self):
        sb = FakeSandbox({"/opt/study/build-info.json": b"synthetic-build-info",
                          "/opt/study/modal-image-build.json": b"synthetic-provenance",
                          "/opt/study/adapter-manifest.json": b"synthetic-adapter-manifest"})
        module, calls = fake_modal(sb)
        protocol = self.root / "protocol.json"
        bundle = self.root / "public.tar.gz"
        protocol.write_bytes(b"synthetic-protocol")
        bundle.write_bytes(b"synthetic-bundle")
        with patch.object(controller, "make_plan", return_value=synthetic_plan()), \
                patch.object(controller, "collect", return_value={"complete": False, "sealed": False, "error": {"type": "SyntheticError"}}):
            record = controller.run("unused", protocol, bundle, "c" * 64, self.root / "run", module)
        self.assertEqual(len(calls), 1)
        self.assertEqual(record["engine_exec_calls"], 1)
        self.assertEqual(sb.terminations, 0)
        self.assertTrue(record["sandbox_preserved_for_collection"])
        self.assertFalse(record["termination_requested"])


if __name__ == "__main__":
    unittest.main()
