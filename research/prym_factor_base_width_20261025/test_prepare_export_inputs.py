"""Planted cache hydration only; no network, target constructor or native launch."""
from hashlib import sha256
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import prepare_export_inputs as prepare
import test_export_width as planted_export


class PrepareExportInputsTests(unittest.TestCase):
    def setUp(self):
        # Reuse the explicitly planted complete native-shaped package builder.
        self.fixture = planted_export.WidthExportTests(methodName='test_complete_package_generic_check_export_and_files')
        self.fixture.setUp()
        self.directory = self.fixture.candidate
        self.output = self.fixture.root/'export-cache'
        self.environment = patch.dict(os.environ, {'CRYPTO_AR_BLOB_CACHE': str(self.fixture.root/'blob-cache')})
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.fixture.tearDown()

    def snapshot(self):
        return {p.name: p.read_bytes() for p in self.directory.iterdir() if p.is_file()}

    def offload_local(self, name):
        content_path = self.directory/name
        content = content_path.read_bytes()
        packed = self.directory/(name+'.gz')
        prepare.artifact_store.gzip_deterministic(content_path, packed)
        stored_hash = prepare.ep.sha256_file(packed)
        store = prepare.artifact_store.FileStore(self.fixture.root/'planted-file-store')
        uri = store.put(packed, stored_hash)
        pointer_path = self.directory/(name+'.gz.blob.json')
        pointer = dict(schema=prepare.artifact_store.POINTER_SCHEMA, sha256=stored_hash,
                       size=packed.stat().st_size, encoding='gzip', content_sha256=sha256(content).hexdigest(),
                       content_size=len(content), uri=uri)
        pointer_path.write_text(json.dumps(pointer))
        content_path.unlink()
        packed.unlink()
        receipt_path = self.directory/'execution-receipt.json'
        receipt = json.loads(receipt_path.read_text())
        receipt.setdefault('artifact_storage', {})[name] = {k: v for k, v in pointer.items() if k != 'schema'}
        receipt['artifact_storage'][name]['path'] = pointer_path.name
        receipt_path.write_text(json.dumps(receipt))
        return pointer_path

    def test_complete_physical_package_materializes_exact_seven_unchanged_files(self):
        before = self.snapshot()
        result = prepare.prepare(self.directory, self.output, software=True)
        self.assertEqual(set(p.name for p in self.output.iterdir()), set(prepare.REQUIRED))
        self.assertEqual(len(result['files']), 7)
        self.assertTrue(result['cache_is_ephemeral'])
        self.assertEqual(self.snapshot(), before)
        prepare.read_package(self.output, software=True)

    def test_real_local_pointer_hydration_and_export_package_validation(self):
        self.offload_local('raw-result.json')
        self.offload_local('events.jsonl')
        before = self.snapshot()
        with patch.object(prepare.artifact_store.S3Store, 'get', side_effect=AssertionError('network forbidden')):
            result = prepare.prepare(self.directory, self.output, software=True)
        self.assertEqual(self.snapshot(), before)
        self.assertTrue(result['originals_unchanged'])
        self.assertFalse(result['native_seal_modified'])
        prepare.read_package(self.output, software=True)

    def test_missing_and_bad_pointer_hydration_refused_original_untouched(self):
        pointer_path = self.offload_local('raw-result.json')
        before = self.snapshot()
        with patch.object(prepare.artifact_store, 'store_for_uri', side_effect=prepare.artifact_store.StoreError('planted missing storage')):
            with self.assertRaisesRegex(prepare.ep.Refused, 'hydration failed'):
                prepare.prepare(self.directory, self.output, software=True)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(self.output.exists())
        pointer = json.loads(pointer_path.read_text())
        pointer['content_sha256'] = '0'*64
        pointer_path.write_text(json.dumps(pointer))
        before = self.snapshot()
        with patch.object(prepare.artifact_store, 'read_bytes', side_effect=AssertionError('bad pointer must refuse first')):
            with self.assertRaisesRegex(prepare.ep.Refused, 'stored-form commitment'):
                prepare.prepare(self.directory, self.output, software=True)
        self.assertEqual(self.snapshot(), before)

    def test_destination_write_once_and_incomplete_cache_not_reused(self):
        self.output.mkdir()
        with patch.object(prepare.artifact_store, 'read_bytes') as hydration:
            with self.assertRaisesRegex(prepare.ep.Refused, 'already exists'):
                prepare.prepare(self.directory, self.output, software=True)
            hydration.assert_not_called()
        self.output.rmdir()
        prepare.prepare(self.directory, self.output, software=True)
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        with self.assertRaisesRegex(prepare.ep.Refused, 'already exists'):
            prepare.prepare(self.directory, self.output, software=True)
        self.assertEqual({p.name: p.read_bytes() for p in self.output.iterdir()}, before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
