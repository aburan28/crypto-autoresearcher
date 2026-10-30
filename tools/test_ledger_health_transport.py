"""Frozen-data transport integrity; no experiment or reviewer execution."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

import yaml
import validate_ledger as ledger

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/ci-main-ledger-health-20261030/transport-preservation.json'


class LedgerHealthTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(REPORT.read_text())

    def test_all_archived_inputs_and_previous_corrections_are_unchanged(self):
        for name, digest in self.record['immutable_inputs_sha256'].items():
            with self.subTest(path=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)

    def test_every_scientific_and_approval_field_is_preserved(self):
        for item in self.record['changes']:
            with self.subTest(path=item['original']):
                old = yaml.safe_load((ROOT / item['previous_canonical']).read_text())[item['kind']]
                new = yaml.safe_load((ROOT / item['replacement']).read_text())[item['kind']]
                allowed = item['allowed_changed_fields']
                self.assertEqual({k: v for k, v in old.items() if k not in allowed},
                                 {k: v for k, v in new.items() if k not in allowed})
                if item['kind'] == 'idea':
                    previous = next(c for c in old['citations'] if c['ref'] == 'KR-IC-73db3f')
                    nearest = new['prior_art']['nearest'][0]
                    self.assertEqual(nearest['provenance'], previous['provenance'])
                    self.assertEqual(nearest['delta'], old['novelty_note'])
                elif item['kind'] == 'coordinator_decision':
                    self.assertEqual(new['knowledge_promotion'],
                                     {'promoted': [], 'not_warranted': old['knowledge_promotion']})

    def test_blind_plan_stays_external_with_only_existing_owner_added(self):
        item = next(x for x in self.record['changes'] if x['kind'] == 'handoff')
        old = yaml.safe_load((ROOT / item['original']).read_text())['handoff']
        new = yaml.safe_load((ROOT / item['replacement']).read_text())['handoff']
        self.assertIsInstance(new['review_plan'], str)
        source = yaml.safe_load((ROOT / old['review_plan']).read_text())['review_plan']
        target_file = ROOT / new['review_plan']
        target = yaml.safe_load(target_file.read_text())['review_plan']
        self.assertEqual(hashlib.sha256(target_file.read_bytes()).hexdigest(),
                         new['schema_transport']['review_plan_sha256'])
        owner = next(j['assigned_to'] for j in source['joints']
                     if j['joint'] == 'J1_blind_rederivation_and_cross_implementation')
        self.assertEqual(owner, old['id'])
        expected = copy.deepcopy(source)
        expected['blind_rederivation']['assigned_to'] = owner
        self.assertEqual(target, expected)
        self.assertIs(target['blind_rederivation']['required'], True)

    def test_all_five_views_pass_the_unchanged_native_record_checker(self):
        bindings = ledger.load_schema_supersessions()
        context = ledger.Ctx(set(), schema_supersessions=bindings)
        for item in self.record['changes']:
            ledger.check_ledger_record(str(ROOT / item['original']), item['kind'], context)
        self.assertEqual(context.errors, [])


if __name__ == '__main__':
    unittest.main()
