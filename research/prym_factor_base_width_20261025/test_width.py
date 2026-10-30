"""Planted small-fixture software tests only. No p4099 acceptance calls."""
from copy import deepcopy
from itertools import product
import json
from hashlib import sha256
from pathlib import Path
import subprocess
import sys
import tempfile
import random
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT/'research/prym_experiment_design_20261019/implementation'))
from fixtures import describe, attach_ec1
from relations import Context, uid
from independent import verify_row, verify_fixture, dense_rank
import collect_width as producer
from check_width import check, check_certificate, reencode, projected_equation
from check_inputs import validate, public_projection, digest


class WidthSoftwareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture, _ = describe(101, 2, 21, 8)
        cls.fixture.update(software_control=True, width_binding={'source_order': [1, 2, 3, 4]})
        cls.blocks = []
        cls.cell = producer.collect(cls.fixture, [1, 2, 3, 4], cls.blocks.append)
        cls.panel = {'fixtures': [cls.fixture]}
        cls.result = dict(complete=True, secret_labels_present=False, new_m8_attempts=0, cells=[cls.cell])
        if not cls.cell['rows']:
            raise AssertionError('planted positive stream must exercise witnesses')
        if cls.cell['projection']['U'] <= 0:
            raise AssertionError('planted stream must exercise unknown matrix columns')
        cls.config = json.loads((HERE/'config.json').read_text())
        cls.target_panel = json.loads((HERE/'fixtures.json').read_text())

    def replay(self, result=None, blocks=None):
        return check({}, self.panel, self.result if result is None else result,
                     self.blocks if blocks is None else blocks, software=True)

    def rejects_cell(self, mutation):
        result = deepcopy(self.result)
        mutation(result['cells'][0])
        with self.assertRaises((ValueError, IndexError, StopIteration, ArithmeticError, KeyError)):
            self.replay(result=result)

    def test_full_small_planted_stream(self):
        checked = self.replay()
        self.assertEqual(checked[0]['attempts_replayed'], 4*56*64)
        self.assertGreater(checked[0]['rows_verified'], 0)
        self.assertEqual(sum(self.cell['reasons'].values()), 4*56*64)
        self.assertGreater(self.cell['reasons'].get('S', 0)+self.cell['reasons'].get('D', 0), 0)

    def test_alias_status_replayed_on_opposite_planted_sources(self):
        f = deepcopy(self.fixture)
        source = self.cell['rows'][0]['source_scalar']
        sources = [source, f['r']-source]
        f['width_binding']['source_order'] = sources
        blocks = []
        cell = producer.collect(f, sources, blocks.append)
        self.assertGreater(cell['reasons'].get('A', 0), 0)
        result = dict(complete=True, secret_labels_present=False, new_m8_attempts=0, cells=[cell])
        check({}, {'fixtures': [f]}, result, blocks, software=True)

    def test_false_source_label(self):
        self.rejects_cell(lambda c: c['rows'][0].update(source_scalar=c['rows'][0]['source_scalar']+1))

    def test_same_shape_seeded_uniform_false_source_label(self):
        # C-WIDTH-map-null: seeded uniform alternative in F_r excluding the
        # actual public source. This is validity control, not a random cover.
        row = deepcopy(self.cell['rows'][0])
        actual, r = row['source_scalar'], self.fixture['r']
        draw = random.Random('prym-width-map-null-v1').randrange(r-1)
        false_scalar = draw+int(draw >= actual)
        self.assertNotEqual(false_scalar, actual)
        row['source_scalar'] = false_scalar
        with self.assertRaises(ValueError):
            verify_row(self.fixture, row)

    def test_modified_lift(self):
        row = deepcopy(self.cell['rows'][0])
        row['constraints'][1][1] = (row['constraints'][1][1]+1) % 101
        with self.assertRaises((ValueError, StopIteration)):
            verify_row(self.fixture, row)

    def test_false_status_even_with_matching_length(self):
        blocks = deepcopy(self.blocks)
        s = blocks[0]['statuses']
        blocks[0]['statuses'] = ('+' if s[0] != '+' else 'B')+s[1:]
        with self.assertRaises(ValueError):
            self.replay(blocks=blocks)

    def test_dropped_status(self):
        blocks = deepcopy(self.blocks)
        blocks[0]['statuses'] = blocks[0]['statuses'][:-1]
        with self.assertRaises(ValueError):
            self.replay(blocks=blocks)

    def test_duplicated_status(self):
        blocks = deepcopy(self.blocks)
        blocks[0]['statuses'] += blocks[0]['statuses'][-1]
        with self.assertRaises(ValueError):
            self.replay(blocks=blocks)

    def test_dropped_source_block(self):
        with self.assertRaises((ValueError, StopIteration)):
            self.replay(blocks=self.blocks[:-1])

    def test_duplicate_source_block(self):
        with self.assertRaises(ValueError):
            self.replay(blocks=self.blocks+[self.blocks[-1]])

    def test_altered_branch_digest(self):
        blocks = deepcopy(self.blocks)
        blocks[0]['attempt_digest'] = '0'*64
        with self.assertRaises(ValueError):
            self.replay(blocks=blocks)

    def test_false_source_schedule(self):
        self.rejects_cell(lambda c: c.update(source_order=list(reversed(c['source_order']))))

    def test_false_known_anchor_U_and_map(self):
        for mutation in [lambda c: c['projection'].update(U=c['projection']['U']+1),
                         lambda c: c['projection']['native_to_projected'].__setitem__(0, ['known', 0]),
                         lambda c: c['projection']['public_derivations'].append(dict(point=[0, 0], scalar=1, public_source=1, sign=1))]:
            self.rejects_cell(mutation)

    def test_false_rank_augmented_rank_pivot(self):
        for mutation in [lambda c: c['projection'].update(rank=c['projection']['rank']+1),
                         lambda c: c['projection'].update(augmented_rank=c['projection']['augmented_rank']+1),
                         lambda c: c['projection'].update(pivots={})]:
            self.rejects_cell(mutation)

    def test_false_kernel(self):
        self.rejects_cell(lambda c: c['projection']['right_kernel'].append([0]*c['projection']['U']))
        empty = deepcopy(self.cell)
        empty['rows'] = []
        projection = producer.public_projection(Context(self.fixture), [1, 2, 3, 4])
        empty['projection'] = producer.finite_certificate([], projection, self.fixture['r'])
        self.assertGreater(empty['projection']['nullity'], 0)
        check_certificate(self.fixture, empty, [1, 2, 3, 4])
        empty['projection']['right_kernel'][0] = [0]*projection['U']
        with self.assertRaises(ValueError):
            check_certificate(self.fixture, empty, [1, 2, 3, 4])

    def test_false_matrix_rhs_row_index_checkpoint(self):
        for mutation in [lambda c: c['projection']['rhs'].__setitem__(0, (c['projection']['rhs'][0]+1) % self.fixture['r']),
                         lambda c: c['row_attempts'].__setitem__(0, 0),
                         lambda c: c['source_checkpoints'][0].update(attempt=0)]:
            self.rejects_cell(mutation)

    def test_signed_deck_AA(self):
        original = public_projection(self.fixture, [1, 2, 3, 4])
        M, transported_M = [], []
        for row in self.cell['rows']:
            other, witness = producer.transport(self.fixture, row)
            independently_other, independently_witness = reencode(self.fixture, row)
            self.assertEqual((other, witness), (independently_other, independently_witness))
            new = public_projection(other, [1, 2, 3, 4])
            self.assertEqual(original['unknown_points'], new['unknown_points'])
            a = projected_equation(row, original, self.fixture['r'])
            b = projected_equation(witness, new, self.fixture['r'])
            self.assertEqual(a, b)
            M.append(a[0]); transported_M.append(b[0])
        self.assertEqual(dense_rank(M, self.fixture['r']), dense_rank(transported_M, self.fixture['r']))

    def test_planted_positive_old8_embedding(self):
        # New labels are deliberately from a separate p101 SOFTWARE fixture.
        # The frozen p4099 old reference has zero rows, so its empirical witness
        # embedding is vacuous and never substituted for this positive test.
        extended, _ = describe(101, 2, 21, 16)
        extended['software_control'] = True
        self.assertEqual(self.fixture['factor_base'], extended['factor_base'][:8])
        row = deepcopy(self.cell['rows'][0])
        row['curve_uid'] = extended['uid']
        row['coefficients'] += [0]*8
        self.assertTrue(verify_row(extended, row))
        labels = self.cell['rows'][0]['base_labels']
        triple, options = tuple(t[0] for t in labels), tuple(t[2] for t in labels)
        old_context, new_context = Context(self.fixture), Context(extended)
        old_descriptor, _ = old_context.descriptor(row['source_scalar'], triple, options)
        new_descriptor, _ = new_context.descriptor(row['source_scalar'], triple, options)
        self.assertEqual(old_descriptor, new_descriptor)
        old_key, new_key = old_context.canonical_identity(old_descriptor), new_context.canonical_identity(new_descriptor)
        old_key.pop('curve_uid'); new_key.pop('curve_uid')
        self.assertEqual(old_key, new_key)
        reconstructed, reason = new_context.construct(new_descriptor)
        self.assertIsNone(reason)
        self.assertEqual(row, reconstructed)

    def test_equal_opposite_zero_projection(self):
        f = deepcopy(self.fixture)
        # A projection-only planted object need not be an eligible target base.
        point = deepcopy(f['factor_base'][2]['point'])
        f['factor_base'] = [dict(point=point, lift=[0, 0]),
                            dict(point=[point[0], -point[1] % 101], lift=[0, 0]),
                            dict(point=None, lift=None), dict(point=point, lift=[0, 0])]
        # Producer Context is not involved in this projection-only fixture.
        projection = public_projection(f, [])
        context = Context(self.fixture)
        context.base = [None if atom['point'] is None else tuple(atom['point']) for atom in f['factor_base']]
        self.assertEqual(producer.public_projection(context, []), projection)
        self.assertEqual(projection['U'], 1)
        self.assertEqual(projection['native_to_projected'][2], ['zero'])
        self.assertEqual(projection['native_to_projected'][0][1], projection['native_to_projected'][1][1])
        self.assertEqual(projection['native_to_projected'][0][2], -projection['native_to_projected'][1][2])
        row = dict(coefficients=[1, 1, 3, 0], source_scalar=1)
        self.assertEqual(projected_equation(row, projection, self.fixture['r']), ([0], 1))

    def test_target_input_checks_without_constructor(self):
        with patch.object(Context, 'construct', side_effect=AssertionError('target constructor forbidden')):
            result = validate(self.config, self.target_panel)
        self.assertEqual(result['derived_new_attempts_total'], 4587520)
        self.assertFalse(result['constructor_invoked'])

    def test_false_prefix_source_order_and_pointer(self):
        for mutate in [lambda p: p['fixtures'][0]['factor_base'][0]['lift'].__setitem__(0, 1),
                       lambda p: p['fixtures'][0]['width_binding']['source_order'].reverse(),
                       lambda p: p['historical_reference_sha256'].__setitem__(next(iter(p['historical_reference_sha256'])), '0'*64)]:
            panel = deepcopy(self.target_panel)
            mutate(panel)
            with self.assertRaises(ValueError):
                validate(self.config, panel)

    def test_target_collection_guard(self):
        with patch.object(Context, 'construct', side_effect=AssertionError('must refuse before construct')):
            with self.assertRaisesRegex(ValueError, 'native admission'):
                producer.collect(self.target_panel['fixtures'][0], [1], lambda event: None)

    def test_target_replay_guard(self):
        import check_width
        with patch.object(check_width, 'outcome', side_effect=AssertionError('target replay forbidden')):
            with self.assertRaisesRegex(ValueError, 'native admission'):
                check(self.config, self.target_panel, self.result, self.blocks)

    def test_native_refuses_before_any_target_constructor(self):
        import runtime_width
        with patch.object(runtime_width.native, 'binding', side_effect=ValueError('not approved')) as admission:
            with patch.object(Context, 'construct', side_effect=AssertionError('target constructor forbidden')) as construct:
                argv = ['collect_width.py', '--config', str(HERE/'config.json'), '--run-dir', str(HERE/'never-created-run')]
                with patch.object(sys, 'argv', argv):
                    with self.assertRaisesRegex(ValueError, 'not approved'):
                        runtime_width.main()
                admission.assert_called_once()
                construct.assert_not_called()
        self.assertFalse((HERE/'never-created-run').exists())

    def test_config_source_manifest_binding(self):
        import runtime_width
        bindings = json.loads((HERE/'source-bindings.json').read_text())
        plan = dict(source_sha256=deepcopy(bindings['source_sha256']), input_sha256=deepcopy(bindings['input_sha256']))
        relative = str((HERE/'source-bindings.json').relative_to(ROOT))
        plan['input_sha256'][relative] = sha256((HERE/'source-bindings.json').read_bytes()).hexdigest()
        with patch.object(runtime_width, 'validate_protocol_binding', return_value={}):
            runtime_width.validate_config_binding(plan, HERE/'config.json')
        plan['source_sha256'].pop(next(iter(plan['source_sha256'])))
        with self.assertRaisesRegex(ValueError, 'binding'):
            runtime_width.validate_config_binding(plan, HERE/'config.json')
        with self.assertRaisesRegex(ValueError, 'canonical'):
            runtime_width.validate_config_binding(plan, HERE/'another-config.json')

    def test_native_renderer_on_planted_retained_cell(self):
        from render_width import render
        import fitz
        with tempfile.TemporaryDirectory(prefix='software-render-', dir=HERE) as name:
            directory = Path(name)
            render(directory, self.result, 'PLANTED-SOFTWARE-ONLY')
            points = json.loads((directory/'graph-source.json').read_text())['points']
            self.assertEqual(points[0]['rank'], self.cell['projection']['rank'])
            self.assertEqual(points[0]['U'], self.cell['projection']['U'])
            self.assertIn('<svg', (directory/'graph.svg').read_text())
            with fitz.open(directory/'report.pdf') as pdf:
                text = ''.join(page.get_text() for page in pdf)
                self.assertIn('PLANTED-SOFTWARE-ONLY', text)
                self.assertIn('partial S', text)
                self.assertGreater(len(pdf[0].get_pixmap().samples), 0)

    def test_censored_source_retains_accepted_witness_bytes(self):
        original = Context.construct
        accepted = False

        def fail_after_positive(context, descriptor):
            nonlocal accepted
            if accepted:
                raise RuntimeError('planted interruption after a verified witness')
            value = original(context, descriptor)
            if value[0] is not None:
                accepted = True
            return value

        events = []
        with patch.object(Context, 'construct', fail_after_positive):
            with self.assertRaisesRegex(RuntimeError, 'planted interruption'):
                producer.collect(self.fixture, [1, 2, 3, 4], events.append)
        self.assertTrue(any(e['schema'] == 'prym-width-accepted-witness/v1' for e in events))
        self.assertEqual(events[-1]['schema'], 'prym-width-partial-source-block/v1')
        self.assertGreater(events[-1]['accepted_rows_so_far'], 0)
        self.assertIn('planted interruption', events[-1]['error'])

    def test_independent_checker_import_boundary(self):
        # Static module import closure: admission imports runtime_width, whose
        # producer import is deferred inside main(), never checker admission.
        import ast
        for name in ['check_width.py', 'check_inputs.py']:
            module = ast.parse((HERE/name).read_text())
            imported = [n.module for n in ast.walk(module) if isinstance(n, ast.ImportFrom)]
            self.assertNotIn('collect_width', imported)
            self.assertNotIn('relations', imported)
            self.assertNotIn('arithmetic', imported)
        child = subprocess.run([sys.executable, '-c',
                                'import check_width, runtime_width, sys; '
                                'assert not ({"collect_width", "relations", "arithmetic"} & set(sys.modules))'],
                               cwd=HERE, capture_output=True, text=True, check=False)
        self.assertEqual(child.returncode, 0, child.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
