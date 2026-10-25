"""Fixed software checks; no producer, search, census or scientific trial."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module('pr2415_validator', ROOT / 'tools/validate_ledger.py')


def result_literal(path, error):
    """Evaluate only the manifest's literal result expression, never main."""
    tree = ast.parse(path.read_text())
    assignments = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'manifest'
                           for t in node.targets)]
    if len(assignments) != 1:
        raise AssertionError('Expected one manifest constructor')
    run = assignments[0].value.values[0]
    index = next(i for i, key in enumerate(run.keys) if key.value == 'result')
    expression = ast.Expression(run.values[index])
    for node in ast.walk(expression):
        if not isinstance(node, (ast.Expression, ast.Dict, ast.List, ast.Constant,
                                 ast.Name, ast.Load)):
            raise AssertionError('Manifest fixture must remain literal')
        if isinstance(node, ast.Name) and node.id != 'error':
            raise AssertionError('Unexpected name in manifest fixture')
    return eval(compile(expression, str(path), 'eval'), {'__builtins__': {}},
                {'error': error})


def validate_synthetic(result, error):
    with tempfile.TemporaryDirectory(prefix='pr2415-software-schema-') as tmp:
        directory = Path(tmp)
        for name in ('command.txt', 'environment.json', 'stdout.log',
                     'stderr.log', 'raw-result.json'):
            (directory / name).write_text('{}\n')
        manifest = {'run': {
            'id': 'RUN-SOFTWARE-PR2415', 'experiment_id': 'EXP-SOFTWARE-PR2415',
            'status': 'failed' if error else 'completed',
            'code': {'commit': 'synthetic-unit-test', 'command': ['software-fixture']},
            'environment': {'scope': 'synthetic unit test'},
            'inputs': {'scope': 'no scientific inputs'},
            'timing': {'scope': 'not a measurement'}, 'result': result,
        }}
        path = directory / 'manifest.yaml'
        path.write_text(yaml.safe_dump(manifest))
        context = VALIDATOR.Ctx(set())
        VALIDATOR.check_run(str(path), context)
        return context.errors


class RuntimeDraftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binding = json.loads((HERE / 'draft-source-bindings.json').read_text())
        cls.original = ROOT / cls.binding['original_runtime']['path']

    def test_original_success_manifest_rejected(self):
        errors = validate_synthetic(result_literal(self.original, None), None)
        self.assertEqual(len(errors), 1)
        self.assertIn('certificate.kind', errors[0])

    def test_original_failure_manifest_rejected(self):
        errors = validate_synthetic(result_literal(self.original, 'fixed failure'),
                                    'fixed failure')
        self.assertEqual(len(errors), 1)
        self.assertIn('certificate.kind', errors[0])

    def test_draft_success_and_failure_manifests_pass(self):
        for error in (None, 'fixed failure'):
            with self.subTest(error=error):
                result = result_literal(HERE / 'native_runtime_draft.py', error)
                self.assertEqual(result['certificate']['kind'], 'none')
                self.assertIsNone(result['outcome'])
                self.assertEqual(result['error'], error)
                self.assertEqual(validate_synthetic(result, error), [])

    def test_original_bindings_preserved(self):
        for name in ('original_runtime', 'original_plan'):
            binding = self.binding[name]
            self.assertEqual(hashlib.sha256((ROOT / binding['path']).read_bytes()).hexdigest(),
                             binding['sha256'])

    def test_proposed_source_and_input_hashes_match(self):
        for kind in ('proposed_source_sha256', 'input_sha256'):
            for path, expected in self.binding[kind].items():
                with self.subTest(path=path):
                    self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
                                     expected)
        self.assertFalse(self.binding['execution_authorized'])
        self.assertFalse(self.binding['executable'])
        self.assertFalse(self.binding['frozen'])
        self.assertIsNone(self.binding['approved_by'])

    def test_draft_refuses_before_binding_or_runner(self):
        module = load_module('pr2415_runtime_draft', HERE / 'native_runtime_draft.py')
        runner = Mock(side_effect=AssertionError('runner must not execute'))
        module.binding = Mock(side_effect=AssertionError('binding must not execute'))
        with self.assertRaisesRegex(RuntimeError, 'Unapproved PR2415 source draft'):
            module.main('EXP-ECDLP-ad0ffe', runner)
        module.binding.assert_not_called()
        runner.assert_not_called()


if __name__ == '__main__':
    unittest.main()
