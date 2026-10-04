#!/usr/bin/env python3
"""Synthetic scalar identity regressions; no committed run is executed.

Optional YAML_IDENTITY_OLD points to the frozen old validator extracted with
Git. YAML_IDENTITY_EVIDENCE writes the per-fixture observations to a new file.
"""
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_run_supersession as fixtures
import validate_ledger as vl

CASES = []
F1 = [('true', 'yes'), ('16', '0x10'), ('1', 'true')]
COLLISIONS = F1 + [
    ('016', '14'), ('+16', '16'), ('0b10000', '16'), ('1_6', '16'),
    ('TRUE', 'On'), ('false', 'OFF'), ('null', '~'), ('Null', 'NULL'),
    ('1', '1.0'), ('0', '-0.0'), ('-0', '+0'), ('false', '0'),
    ('!!int "16"', '0x10'), ('!!bool "true"', 'yes'),
    ('!!null "null"', '~'), ('!!float "1.0"', '1'),
    ('2001-12-15', '!!timestamp "2001-12-15"'),
    ('!!binary "YQ=="', '!!binary "YQ==\\n"'),
]
DISTINCT = [('"true"', 'yes'), ('"16"', '0x10'), ('"null"', '~'),
            ('!!str "one"', '1'), ('1', '2'), ('false', '2'),
            ('2001-12-15', '2001-12-16')]
TEXT_COLLISIONS = [('"true"', 'true'), ('"16"', '16'), ('"null"', 'null')]


def load_old():
    path = os.environ.get('YAML_IDENTITY_OLD')
    if not path:
        return None
    spec = importlib.util.spec_from_file_location('yaml_identity_old', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ScalarIdentityTests(fixtures.SupersessionFixture):
    def source(self, extra, opted):
        return ('run:\n  id: RUN-SUP-001\n' +
                ('  process: {pid: 1}\n  process: {pid: 2}\n' if opted else '') + extra)

    def observe(self, module, source, opted, label):
        self.superseded.write_text(source, encoding='utf-8')
        entry = self.registry()[str(self.superseded)]
        if opted:
            entry['superseded_id_extraction'] = {
                'kind': 'unique_nested_run_id_duplicate_process',
                'line_number': 2, 'exact_line': '  id: RUN-SUP-001'}
        identity = module._run_id_of(str(self.superseded), superseded_entry=entry)
        ctx = module.Ctx(set())
        registry = {str(self.superseded): entry}
        module.check_run_supersessions(ctx, registry)
        registry_errors = list(ctx.errors)
        module.check_run(str(self.superseded), ctx, registry)
        result = {'label': label, 'path': 'opted' if opted else 'ordinary',
                  'source': source, 'entry': entry,
                  'identity': identity, 'registry_errors': registry_errors,
                  'all_errors': ctx.errors, 'registered_ids': sorted(ctx.ids),
                  'accepted': not ctx.errors}
        CASES.append(result)
        return result

    def pair_cases(self, pairs, accepted):
        for a, b in pairs:
            for opted in (False, True):
                with self.subTest(a=a, b=b, opted=opted):
                    text = self.source(f'  other:\n    {a}: first\n    {b}: second\n', opted)
                    result = self.observe(vl, text, opted, 'new')
                    self.assertEqual(result['identity'], 'RUN-SUP-001' if accepted else None)
                    self.assertEqual(result['accepted'], accepted, result)
                    if not accepted:
                        self.assertTrue(result['registry_errors'])

    def test_safe_resolution_collision_families(self):
        for a, b in COLLISIONS:
            # Independently compare SafeLoader's constructed key values.
            left = next(iter(yaml.safe_load(f'{a}: x')))
            right = next(iter(yaml.safe_load(f'{b}: y')))
            self.assertEqual(left, right, (a, b))
        self.pair_cases(COLLISIONS, False)

    def test_distinct_scalar_and_quoted_string_controls(self):
        self.pair_cases(DISTINCT, True)

    def test_existing_textual_restrictions_remain(self):
        self.pair_cases(TEXT_COLLISIONS, False)

    def test_unsupported_ambiguous_and_complex_keys(self):
        for extra in ('  other: {!custom x: one}\n',
                      '  other: {!!python/name:os.system x: one}\n',
                      '  other: {? [a, b]: one}\n',
                      '  other: {? {a: b}: one}\n',
                      '  other: {.nan: one}\n',
                      '  other: {!!int nope: one}\n',
                      '  other: {!!bool nope: one}\n',
                      '  other: {!!timestamp nope: one}\n'):
            for opted in (False, True):
                with self.subTest(extra=extra, opted=opted):
                    result = self.observe(vl, self.source(extra, opted), opted, 'new-edge')
                    self.assertIsNone(result['identity'])
                    self.assertFalse(result['accepted'])

    def test_opted_structure_and_literal_process_exception(self):
        variants = ['  process: {pid: 3}\n', '  id: RUN-OTHER-001\n',
                    '  run_id: RUN-OTHER-001\n', '  note: a\n  note: b\n',
                    '  first: &x [1]\n  alias: *x\n',
                    '  defaults: &x {a: 1}\n  merged: {<<: *x}\n',
                    '---\nrun_id: RUN-OTHER-001\n',
                    '  other: {process: a, process: b}\n']
        for extra in variants:
            result = self.observe(vl, self.source(extra, True), True, 'new-structure')
            self.assertIsNone(result['identity'])
        result = self.observe(vl, self.source('', True), True, 'new-positive-exception')
        self.assertTrue(result['accepted'])
        self.assertIsNone(vl._run_id_of(str(self.superseded)))

    def test_ordinary_alias_policy_is_preserved(self):
        # Ordinary SafeLoader permits aliases; the opted extractor forbids them.
        result = self.observe(vl, self.source('  x: &x [1]\n  y: *x\n', False),
                              False, 'new-ordinary-alias')
        self.assertTrue(result['accepted'])

    def test_frozen_old_f1_end_to_end(self):
        old = load_old()
        if old is None:
            self.skipTest('set YAML_IDENTITY_OLD to the frozen historical validator')
        for a, b in F1:
            for opted in (False, True):
                source = self.source(f'  other:\n    {a}: first\n    {b}: second\n', opted)
                before = self.observe(old, source, opted, 'old-F1')
                after = self.observe(vl, source, opted, 'new-F1')
                self.assertEqual(before['identity'], 'RUN-SUP-001')
                self.assertTrue(before['accepted'])
                self.assertEqual(before['registered_ids'], ['RUN-SUP-001'])
                self.assertIsNone(after['identity'])
                self.assertFalse(after['accepted'])


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ScalarIdentityTests))
    evidence = os.environ.get('YAML_IDENTITY_EVIDENCE')
    if evidence:
        with open(evidence, 'x', encoding='utf-8') as out:
            json.dump({'tests_run': result.testsRun, 'failures': len(result.failures),
                       'errors': len(result.errors), 'skipped': len(result.skipped),
                       'cases': CASES}, out, indent=2)
            out.write('\n')
    raise SystemExit(not result.wasSuccessful())
