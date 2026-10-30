"""Publication I/O controls, using planted report bytes and no S3 calls."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from tools.report_publication_files import main, publication_files


class ReportPublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def manifest(self, directory, files):
        d = self.root/directory
        d.mkdir(parents=True, exist_ok=True)
        entries = {}
        for name, data in files.items():
            (d/name).write_bytes(data)
            entries[name] = dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        p = d/'.artifacts.json'
        p.write_text(json.dumps(dict(files=entries)))
        return str(p.relative_to(self.root))

    def test_changed_manifest_includes_ignored_experiment_report(self):
        p = self.manifest('experiments/EXP-X/reports/review-X', {'report.pdf': b'planted pdf'})
        names = publication_files([p, p], self.root)
        self.assertEqual(names, [p, 'experiments/EXP-X/reports/review-X/report.pdf'])

    def test_research_manifest_selects_only_pdfs(self):
        p = self.manifest('research/study', {'report.pdf': b'pdf', 'raw.npy': b'raw'})
        self.assertEqual(publication_files([p], self.root), ['research/study/report.pdf'])

    def test_docs_reports_and_direct_paths_remain_supported(self):
        p = self.manifest('docs/reports/study', {'graph.png': b'png'})
        names = publication_files([p, 'research/other/report.pdf', 'tools/program.py'], self.root)
        self.assertIn('docs/reports/study/graph.png', names)
        self.assertIn('research/other/report.pdf', names)
        self.assertNotIn('tools/program.py', names)

    def test_native_run_manifests_are_not_report_inputs(self):
        self.assertEqual(publication_files(['experiments/EXP-X/runs/RUN-X/.artifacts.json'], self.root), [])

    def test_missing_or_corrupted_report_is_rejected(self):
        p = self.manifest('research/study', {'report.pdf': b'abc'})
        target = self.root/'research/study/report.pdf'
        for data in [b'xyz', b'longer', None]:
            with self.subTest(data=data):
                if data is None:
                    target.unlink()
                else:
                    target.write_bytes(data)
                with self.assertRaises(ValueError):
                    publication_files([p], self.root)

    def test_escaping_or_malformed_entries_are_rejected(self):
        p = self.manifest('research/study', {'report.pdf': b'abc'})
        path = self.root/p
        for name, entry in [('../outside.pdf', {}), ('/outside.pdf', {}),
                            ('report.pdf', dict(bytes=True, sha256='0'*64))]:
            with self.subTest(name=name, entry=entry):
                path.write_text(json.dumps(dict(files={name: entry})))
                with self.assertRaises(ValueError):
                    publication_files([p], self.root)

    def test_input_path_may_not_escape_root(self):
        with self.assertRaises(ValueError):
            publication_files(['../outside.pdf'], self.root)

    def test_changed_selection_does_not_expand_unchanged_manifest(self):
        changed = self.manifest('research/changed', {'report.pdf': b'changed'})
        self.manifest('research/unchanged', {'report.pdf': b'unchanged'})
        self.assertEqual(publication_files([changed], self.root), ['research/changed/report.pdf'])
        all_manifests = [str(p.relative_to(self.root)) for p in self.root.rglob('.artifacts.json')]
        self.assertEqual(publication_files(all_manifests, self.root),
                         ['research/changed/report.pdf', 'research/unchanged/report.pdf'])

    def test_symlink_cannot_escape_publication_root(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside)/'report.pdf'
            target.write_bytes(b'abc')
            p = self.manifest('research/study', {'report.pdf': b'abc'})
            report = self.root/'research/study/report.pdf'
            report.unlink()
            report.symlink_to(target)
            for initial in [[p], ['research/study/report.pdf']]:
                with self.subTest(initial=initial), self.assertRaises(ValueError):
                    publication_files(initial, self.root)

    def test_cli_preserves_nul_paths_spaces_and_deduplication(self):
        p = self.manifest('experiments/EXP-X/reports/run-X', {'with space.pdf': b'pdf'})
        names = self.root/'files.z'
        names.write_bytes(os.fsencode(p)+b'\x00'+os.fsencode(p)+b'\x00')
        main(['--files', str(names), '--root', str(self.root)])
        self.assertEqual(names.read_bytes().split(b'\x00')[:-1],
                         [os.fsencode(p), b'experiments/EXP-X/reports/run-X/with space.pdf'])


if __name__ == '__main__':
    unittest.main()
