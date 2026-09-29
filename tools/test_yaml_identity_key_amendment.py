#!/usr/bin/env python3
"""Synthetic regression controls for the two reviewed identity edge cases.

YAML_AMENDMENT_OLD optionally names the frozen c10 validator for reproducing
its failures. YAML_AMENDMENT_EVIDENCE retains observations in a new JSON file.
"""
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_run_supersession as fixtures
import test_yaml_identity_keys as previous
import validate_ledger as vl


def prior_module():
    path = os.environ.get('YAML_AMENDMENT_OLD')
    if not path:
        return None
    spec = importlib.util.spec_from_file_location('yaml_amendment_prior', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ReviewedEdgeTests(fixtures.SupersessionFixture):
    observe = previous.ScalarIdentityTests.observe

    def source(self, extra='', opted=False):
        return ('run:\n  id: RUN-SUP-001\n' +
                ('  process: {pid: 17}\n  process: {pid: 23}\n' if opted else '') +
                extra)

    def rejected(self, source, opted):
        result = self.observe(vl, source, opted, 'corrected')
        self.assertIsNone(result['identity'], result)
        self.assertFalse(result['accepted'], result)
        self.assertTrue(result['registry_errors'], result)
        # Replacement IDs may still be indexed for diagnostics despite errors.
        # Acceptance is governed by the integrity errors, not ctx.ids alone.

    def test_tagged_process_keys_in_both_orders(self):
        for tag in ('!!null', '!!int', '!!float', '!!bool'):
            for first, second in ((tag + ' process', 'process'),
                                  ('process', tag + ' process')):
                with self.subTest(first=first, second=second):
                    self.rejected(self.source(
                        f'  {first}: {{pid: 17}}\n  {second}: {{pid: 23}}\n'), True)

    def test_malformed_numeric_keys_reject_without_exception(self):
        for key in ("!!int ''", "!!float ''", '!!int +', '!!int -',
                    '!!float +', '!!float -'):
            for opted in (False, True):
                with self.subTest(key=key, opted=opted):
                    self.rejected(self.source(f'  other: {{{key}: x}}\n', opted), opted)

    def test_valid_process_keys_and_shape_controls(self):
        for key in ('process', '!!str process', '"process"'):
            source = self.source(f'  {key}: {{pid: 17}}\n  {key}: {{pid: 23}}\n')
            with self.subTest(key=key):
                result = self.observe(vl, source, True, 'corrected')
                self.assertEqual(result['identity'], 'RUN-SUP-001')
                self.assertTrue(result['accepted'], result)
                self.rejected(source, False)
        for source in (self.source('  process: {pid: 29}\n', True),
                       self.source('  process: []\n  process: {pid: 23}\n'),
                       self.source('  process: {pid: 17}\n  process: []\n')):
            self.rejected(source, True)

    def test_previous_semantic_collisions_still_reject(self):
        for left, right in previous.F1:
            for opted in (False, True):
                self.rejected(self.source(
                    f'  other:\n    {left}: first\n    {right}: second\n', opted), opted)

    def test_frozen_prior_failures(self):
        prior = prior_module()
        if prior is None:
            self.skipTest('YAML_AMENDMENT_OLD not set; frozen prior comparison optional')
        source = self.source('  !!null process: {pid: 17}\n  process: {pid: 23}\n')
        result = self.observe(prior, source, True, 'frozen-c10')
        self.assertEqual(result['identity'], 'RUN-SUP-001')
        self.assertTrue(result['accepted'], result)
        self.rejected(source, True)
        for key in ("!!int ''", "!!float ''", '!!int +'):
            for opted in (False, True):
                source = self.source(f'  other: {{{key}: x}}\n', opted)
                with self.subTest(key=key, opted=opted):
                    with self.assertRaises(IndexError) as failure:
                        self.observe(prior, source, opted, 'frozen-c10')
                    previous.CASES.append({'label': 'frozen-c10', 'source': source,
                                           'path': 'opted' if opted else 'ordinary',
                                           'exception': type(failure.exception).__name__,
                                           'message': str(failure.exception)})
                    self.rejected(source, opted)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReviewedEdgeTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    evidence = os.environ.get('YAML_AMENDMENT_EVIDENCE')
    if evidence:
        with open(evidence, 'x', encoding='utf-8') as handle:
            json.dump({'tests_run': result.testsRun,
                       'failures': len(result.failures), 'errors': len(result.errors),
                       'skipped': len(result.skipped), 'observations': previous.CASES},
                      handle, indent=2)
            handle.write('\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
