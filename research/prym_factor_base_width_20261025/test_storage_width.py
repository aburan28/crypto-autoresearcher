"""Local planted storage packaging controls; no network, native launch or relations."""
from contextlib import redirect_stderr
from hashlib import sha256, shake_256
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import execute_with_storage as width


class WidthStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='software-storage-', dir=width.HERE)
        self.directory = Path(self.temp.name)
        self.environment = patch.dict(os.environ, {'CRYPTO_AR_BLOB_CACHE': str(self.directory/'cache')})
        self.environment.start()
        self.plan = self.directory/'planted-plan.json'
        self.bound = dict(experiment_id=width.EXPERIMENT, trials=[dict(run_id=width.RUN)])
        self.plan.write_text(json.dumps(self.bound))

    def tearDown(self):
        self.environment.stop()
        self.temp.cleanup()

    def test_delivery_contract_matches_fixed_module(self):
        contract = json.loads((width.HERE/'contract.json').read_text())
        self.assertEqual(contract['experiment_id'], width.EXPERIMENT)
        self.assertEqual(contract['run_id'], width.RUN)
        self.assertEqual(contract['delivery_directory'], str(width.DELIVERY.relative_to(width.ROOT)))
        self.assertEqual(contract['frozen_adapter_sha256'], width.FROZEN_ADAPTER_SHA256)
        self.assertEqual(contract['rebound_module_constants_only'], ['EXPERIMENT', 'RUN', 'DELIVERY', 'HERE'])
        self.assertEqual(contract['modes'], ['run', 'probe'])
        self.assertEqual(len(contract['required_delivery_outputs']), 3)
        self.assertFalse(contract['historical_mode'])
        self.assertFalse(contract['execution_authorized'])

    def test_wrong_experiment_run_and_trial_count_refused_before_io(self):
        cases = [dict(experiment_id='EXP-ECDLP-wrong', trials=[dict(run_id=width.RUN)]),
                 dict(experiment_id=width.EXPERIMENT, trials=[dict(run_id='RUN-ECDLP-wrong')]),
                 dict(experiment_id=width.EXPERIMENT, trials=[])]
        for wrong in cases:
            self.plan.write_text(json.dumps(wrong))
            with patch.object(width._adapter, 'Publisher') as publisher:
                with patch.object(width.native, 'main') as native_main:
                    with self.assertRaises(width.DeliveryFailure):
                        width.run(self.plan, 'planted-owner', 1)
                    publisher.assert_not_called()
                    native_main.assert_not_called()

    def test_only_new_instance_identity_destination_constants_rebound(self):
        before = width.FROZEN_ADAPTER.read_bytes()
        self.assertEqual(sha256(before).hexdigest(), width.FROZEN_ADAPTER_SHA256)
        self.assertEqual(width._adapter.EXPERIMENT, 'EXP-ECDLP-a9b6a5')
        self.assertEqual(width._adapter.RUN, 'RUN-ECDLP-967315')
        self.assertEqual(width._adapter.HERE, width.HERE)
        self.assertEqual(width._adapter.DELIVERY, width.ROOT/'experiments/EXP-ECDLP-a9b6a5/artifact-deliveries/RUN-ECDLP-967315')
        self.assertEqual(width._adapter.ROOT, width.ROOT)
        self.assertEqual(width._adapter.MINIMUM, 65537)
        self.assertEqual(width._adapter.REMOTE, 's3://setec-astronomy-artifacts/store')
        self.assertIs(width.run, width._adapter.run)
        self.assertIs(width.Publisher, width._adapter.Publisher)
        self.assertIs(width.storage_adapter, width._adapter.storage_adapter)
        self.assertIn("EXPERIMENT = 'EXP-ECDLP-d6d8e8'", before.decode())
        self.assertIn("RUN = 'RUN-ECDLP-ea49a6'", before.decode())
        self.assertEqual(width.FROZEN_ADAPTER.read_bytes(), before)

    def test_fixed_native_route_is_mocked_and_failure_code_propagates(self):
        with patch.object(width._adapter, 'Publisher') as publisher:
            with patch.object(width.native, 'main', return_value=17) as native_main:
                self.assertEqual(width.run(self.plan, 'planted-owner', 3), 17)
                publisher.assert_called_once_with(width.DELIVERY)
                publisher.return_value.initialize.assert_called_once_with()
                native_main.assert_called_once_with([
                    'run', '--repo', str(width.ROOT), '--plan', str(self.plan.resolve()),
                    '--owner', 'planted-owner', '--epoch', '3'])

    def test_mocked_success_custody_uses_new_run_and_delivery_only(self):
        receipt_path = width.ROOT/f'experiments/{width.EXPERIMENT}/runs/{width.RUN}/execution-receipt.json'
        receipt = dict(artifact_sha256={'planted.bin': '1'*64}, artifact_storage={})
        read_text = Path.read_text

        def planted_read(path, *args, **kwargs):
            return json.dumps(receipt) if path == receipt_path else read_text(path, *args, **kwargs)

        with patch.object(Path, 'read_text', planted_read):
            with patch.object(width._adapter, 'Publisher') as publisher:
                publisher.return_value.entries = []
                with patch.object(width.native, 'main', return_value=0):
                    with patch.object(width.native, 'trial_state', return_value='output_validated'):
                        with patch.object(width.artifact_store, 'sha256_file', return_value='2'*64):
                            with patch.object(width._adapter, 'dump') as dump:
                                self.assertEqual(width.run(self.plan, 'planted-owner', 1), 0)
                                path, proof = dump.call_args.args
                                self.assertEqual(path, width.DELIVERY/'custody.json')
                                self.assertEqual(proof['experiment_id'], width.EXPERIMENT)
                                self.assertEqual(proof['run_id'], width.RUN)
                                self.assertTrue(proof['offload_before_native_receipt'])
                                self.assertTrue(proof['fresh_object_readback_verified'])

    def test_inherited_offload_failure_is_fatal_before_seal(self):
        payload = shake_256(b'planted-width-storage-failure-control').digest(90000)
        target = self.directory/'payload.bin'
        target.write_bytes(payload)
        publisher = Mock()
        publisher.put.side_effect = OSError('planted canonical upload failure')
        sealed = False

        def planted_native(argv):
            nonlocal sealed
            width.artifact_store.compact(self.directory, ['payload.bin'])
            sealed = True
            return 0

        with patch.object(width._adapter, 'Publisher', return_value=publisher):
            with patch.object(width.native, 'main', side_effect=planted_native):
                with self.assertRaises(width.DeliveryFailure):
                    width.run(self.plan, 'planted-owner', 1)
        self.assertFalse(sealed)
        self.assertEqual(width.artifact_store.gunzip_digest(self.directory/'payload.bin.gz'),
                         (sha256(payload).hexdigest(), len(payload)))
        self.assertFalse((self.directory/'payload.bin.gz.blob.json').exists())

    def test_cli_excludes_historical_and_requires_positive_epoch(self):
        for argv in [['historical'], ['run', '--owner', 'planted', '--epoch', '0']]:
            with patch.object(width, 'run') as run:
                with patch.object(width._adapter, 'probe') as probe:
                    with redirect_stderr(io.StringIO()):
                        with self.assertRaises(SystemExit) as error:
                            width.main(argv)
                    self.assertEqual(error.exception.code, 2)
                    run.assert_not_called()
                    probe.assert_not_called()

    def test_cli_probe_is_mocked_and_new_destination_only(self):
        planted = {'status': 'mocked-software-control'}
        from contextlib import redirect_stdout
        with patch.object(width._adapter, 'probe', return_value=planted) as probe:
            with patch.object(width._adapter, 'dump') as dump:
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(width.main(['probe']), 0)
                probe.assert_called_once_with()
                dump.assert_called_once_with(width.HERE/'probe-result.json', planted)


if __name__ == '__main__':
    unittest.main(verbosity=2)
