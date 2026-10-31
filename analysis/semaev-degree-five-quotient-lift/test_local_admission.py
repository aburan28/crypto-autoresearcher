"""Deterministic admission controls; never execute scientific workers."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location('launcher', Path(__file__).with_name('launch_local_panel.py'))
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class Clock:
    def __init__(self): self.now = 0
    def __call__(self): return self.now
    def sleep(self, seconds): self.now += seconds


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan = dict(memory_bytes=100, reserve_bytes=10, locks=[],
                         admission_wait_seconds=10, admission_poll_seconds=5)
        self.clock = Clock()

    def admit(self, readings):
        values = iter(readings)
        return launcher.wait_for_memory(self.plan, self.root, lambda: next(values),
                                        self.clock, self.clock.sleep)

    def test_default_refuses_once_without_samples(self):
        self.plan.pop('admission_wait_seconds')
        result = self.admit([109])
        self.assertFalse(result['admitted'])
        self.assertEqual(self.clock.now, 0)
        self.assertFalse((self.root / 'admission-samples').exists())

    def test_recovery_preserves_each_sample_and_threshold(self):
        result = self.admit([109, 110])
        self.assertTrue(result['admitted'])
        self.assertEqual(result['wait_seconds'], 5)
        samples = [json.loads(p.read_text()) for p in sorted((self.root / 'admission-samples').glob('*.json'))]
        self.assertEqual([x['available_bytes'] for x in samples], [109, 110])
        self.assertEqual([x['admitted'] for x in samples], [False, True])
        self.assertTrue(all(x['process_cap_bytes'] == 100 and x['reserve_bytes'] == 10 for x in samples))

    def test_deadline_is_not_extended_even_if_memory_recovers_late(self):
        result = self.admit([0, 0, 200])
        self.assertFalse(result['admitted'])
        self.assertTrue(result['wait_expired'])
        self.assertEqual(self.clock.now, 10)

    def test_invalid_wait_policy_rejected(self):
        for value in [-1, 3601, True, 1.5]:
            self.plan['admission_wait_seconds'] = value
            with self.assertRaises(ValueError): self.admit([200])

    def main_fixture(self):
        request = self.root / 'request.json'
        request.write_text(json.dumps({'memory_bytes': 100}))
        self.plan.update(python='unused', driver='unused', bundle='unused',
                         request=str(request), output_root=str(self.root / 'output'),
                         locks=[str(self.root / 'lock1'), str(self.root / 'lock2')],
                         hashes={str(request): launcher.sha(request)})
        plan = self.root / 'plan.json'
        plan.write_text(json.dumps(self.plan))
        protocol = self.root / 'protocol.json'
        protocol.write_text(json.dumps({'freeze': {'status': 'frozen', 'protocol_sha256': 'fixture'},
                                       'links': {'plan_sha256': launcher.sha(plan)}}))
        return request, ['launcher', '--plan', str(plan), '--protocol', str(protocol)]

    def run_main(self, readings, on_sleep=None):
        request, argv = self.main_fixture()
        def sleep(seconds):
            for name in self.plan['locks']:
                with open(name, 'a') as handle:
                    with self.assertRaises(BlockingIOError):
                        launcher.fcntl.flock(handle, launcher.fcntl.LOCK_EX | launcher.fcntl.LOCK_NB)
            self.clock.sleep(seconds)
            if on_sleep: on_sleep(request)
        child = Mock(pid=123)
        child.wait.return_value = 0
        with patch('sys.argv', argv), patch.object(launcher, 'available_memory', side_effect=readings), \
             patch.object(launcher.time, 'monotonic', self.clock), patch.object(launcher.time, 'sleep', sleep), \
             patch.object(launcher.subprocess, 'Popen', return_value=child) as popen:
            if on_sleep:
                with self.assertRaises(AssertionError): launcher.main()
                popen.assert_not_called()
                return
            result = launcher.main()
            return result, popen

    def test_locks_held_during_wait_and_one_child_after_recovery(self):
        result, popen = self.run_main([0, 110])
        self.assertEqual(result, 0)
        popen.assert_called_once()
        self.assertEqual(len(popen.call_args.kwargs['pass_fds']), 2)
        self.assertTrue((self.root / 'output' / 'terminal.json').exists())

    def test_wait_expiry_never_starts_worker(self):
        result, popen = self.run_main([0, 0, 0])
        self.assertEqual(result, 73)
        popen.assert_not_called()
        self.assertFalse((self.root / 'output' / 'child.json').exists())

    def test_changed_input_during_wait_never_reaches_worker(self):
        self.run_main([0, 110], lambda request: request.write_text('{"memory_bytes": 99}'))

    def test_existing_owner_prevents_memory_wait_and_worker(self):
        _, argv = self.main_fixture()
        with open(self.plan['locks'][0], 'a') as owner:
            launcher.fcntl.flock(owner, launcher.fcntl.LOCK_EX | launcher.fcntl.LOCK_NB)
            with patch('sys.argv', argv), patch.object(launcher, 'available_memory') as memory, \
                 patch.object(launcher.subprocess, 'Popen') as popen:
                with self.assertRaises(BlockingIOError): launcher.main()
                memory.assert_not_called()
                popen.assert_not_called()


if __name__ == '__main__': unittest.main()
