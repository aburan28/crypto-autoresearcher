"""Planted storage/receipt controls; never evaluates a scientific relation."""
from copy import deepcopy
from hashlib import sha256, shake_256
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from execute_with_storage import (DeliveryFailure, Publisher, ROOT, artifact_store,
                                  native, storage_adapter)
from research_dispatch import DispatchError, GitRepositoryVerifier


class PlantedStore:
    def put(self, source, expected):
        if artifact_store.sha256_file(source) != expected:
            raise DeliveryFailure('bad planted digest')
        path = artifact_store.cache_dir()/'sha256'/expected[:2]/expected
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(Path(source).read_bytes())
        return 's3://setec-astronomy-artifacts/store/sha256/'+expected[:2]+'/'+expected


class FailedStore:
    def put(self, source, expected):
        raise OSError('planted upload failure')


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.environment = patch.dict('os.environ', {'CRYPTO_AR_BLOB_CACHE': str(self.root/'cache')})
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.temp.cleanup()

    def payload(self, directory):
        directory.mkdir(parents=True)
        content = shake_256(b'planted-public-storage-control').digest(90000)
        (directory/'payload.bin').write_bytes(content)
        return content

    def test_pointer_roundtrip_and_tampered_content_commitment(self):
        directory = self.root/'native'
        content = self.payload(directory)
        with storage_adapter(PlantedStore()):
            storage = artifact_store.compact(directory, ['payload.bin'])
        entry = storage['payload.bin']
        self.assertTrue(entry['path'].endswith('.gz.blob.json'))
        self.assertFalse((directory/'payload.bin.gz').exists())
        self.assertTrue(artifact_store.stored_matches(directory, 'payload.bin', entry, sha256(content).hexdigest()))
        self.assertEqual(artifact_store.read_bytes(directory/'payload.bin'), content)
        pointer = directory/entry['path']
        bad = json.loads(pointer.read_text());bad['content_sha256'] = '0'*64
        pointer.write_text(json.dumps(bad))
        self.assertFalse(artifact_store.stored_matches(directory, 'payload.bin', entry, sha256(content).hexdigest()))

    def test_offload_failure_keeps_recoverable_bytes_and_refuses_seal(self):
        directory = self.root/'failure'
        content = self.payload(directory)
        with storage_adapter(FailedStore()):
            with self.assertRaises(DeliveryFailure):
                artifact_store.compact(directory, ['payload.bin'])
        self.assertEqual(artifact_store.gunzip_digest(directory/'payload.bin.gz'), (sha256(content).hexdigest(), len(content)))
        self.assertFalse((directory/'payload.bin.gz.blob.json').exists())

    def test_publisher_rejects_forged_digest_before_upload(self):
        source = self.root/'source';source.write_bytes(b'planted')
        publisher = Publisher.__new__(Publisher)
        with self.assertRaises(DeliveryFailure):
            publisher.put(source, '0'*64)

    def test_empty_delivery_retains_fixed_manifest_coverage(self):
        publisher = Publisher.__new__(Publisher)
        publisher.directory = self.root/'empty-delivery'
        publisher.initialize()
        manifest = json.loads((publisher.directory/'.artifacts.json').read_text())
        self.assertEqual(manifest['files'], {})
        self.assertTrue((publisher.directory/'.gitignore').is_file())

    def test_native_receipt_accepts_preseal_pointer_and_rejects_stale_storage_path(self):
        trial = {'id': 'planted', 'run_id': 'CONTROL', 'artifacts': ['payload.bin']}
        plan = {'specification': 'experiments/CONTROL/specification.yaml', 'trials': [trial]}
        directory = self.root/'experiments/CONTROL/runs/CONTROL'
        content = self.payload(directory)
        with storage_adapter(PlantedStore()):
            storage = artifact_store.compact(directory, ['payload.bin'])
        names = set(native.GENERATED)-{'execution-receipt.json'}
        for name in names:
            (directory/name).write_bytes(b'planted metadata')
        hashes = {name: native.sha256(directory/name) for name in names}
        hashes['payload.bin'] = sha256(content).hexdigest()
        receipt = dict(schema=native.RECEIPT_SCHEMA, plan_sha256='planted-plan', trial_id='planted',
                       run_id='CONTROL', status='output_validated', returncode=0, check_returncode=0,
                       artifact_sha256=hashes, artifact_storage=storage)
        path = directory/'execution-receipt.json';path.write_text(json.dumps(receipt))
        self.assertEqual(native.trial_state(self.root, plan, trial, 'planted-plan'), 'output_validated')
        bad = deepcopy(receipt);bad['artifact_storage']['payload.bin']['path'] = 'payload.bin.gz'
        path.write_text(json.dumps(bad))
        self.assertEqual(native.trial_state(self.root, plan, trial, 'planted-plan'), 'needs_reconciliation')

    def test_git_content_at_commit_binds_stored_pointer_bytes(self):
        repository = self.root/'repository';repository.mkdir()
        logical = 'experiments/CONTROL/runs/CONTROL/payload.bin'
        directory = repository/Path(logical).parent
        self.payload(directory)
        with storage_adapter(PlantedStore()):
            entry = artifact_store.compact(directory, ['payload.bin'])['payload.bin']
        pointer = directory/entry['path']
        def git(*args):
            return subprocess.check_output(['git', '-C', str(repository), *args], stderr=subprocess.DEVNULL).decode().strip()
        git('init', '-q');git('add', '.')
        git('-c', 'user.name=Planted control', '-c', 'user.email=control@example.invalid', 'commit', '-qm', 'PLANTED-ARCHIVE')
        task = dict(id='PLANTED-ARCHIVE', archive=dict(kind='snapshot', binding_mode='content_at_commit',
                    commit_sha=git('rev-parse', 'HEAD'), parent_sha=None, record_ids=[], source_task_ids=[],
                    path_sha256={logical: artifact_store.sha256_file(pointer)}))
        GitRepositoryVerifier(repository).verify_archive(task, [logical])
        task['archive']['path_sha256'][logical] = '0'*64
        with self.assertRaises(DispatchError):
            GitRepositoryVerifier(repository).verify_archive(task, [logical])


if __name__ == '__main__':
    unittest.main()
