"""Metadata-only conformance vectors, shared across the three repositories."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('curve_identity', Path(__file__).resolve().parents[1] / 'tools/curve_identity.py')
identity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(identity)

FIELD = {'characteristic': 2, 'degree': 13, 'element_encoding': 'unsigned integer; bit i is the coefficient of z^i', 'modulus_exponents': [13, 4, 3, 1, 0], 'representation': 'polynomial_basis'}

class IdentityTest(unittest.TestCase):
    def setUp(self):
        self.curve = {'model': 'test metadata only', 'a2': 0, 'a6': 1, 'subgroup_order': 7, 'cofactor': 4, 'generator': [1, 2], 'target_group': 'fixture'}

    def test_canonical_and_float_rejection(self):
        self.assertEqual(identity.canonical({'z': 'é', 'a': [1, None]}), '{"a":[1,null],"z":"é"}')
        with self.assertRaises(ValueError): identity.digest({'bad': 1.0})
        self.assertEqual(identity.digest({'b': 2, 'a': 1}), identity.digest({'a': 1, 'b': 2}))

    def test_all_representation_parameters_change_identity(self):
        original = identity.curve_identity(FIELD, self.curve, 'test')
        for key, value in [('generator', [2, 1]), ('subgroup_order', 11), ('a6', 2)]:
            c = {**self.curve, key: value}
            self.assertNotEqual(original['curve_uid'], identity.curve_identity(FIELD, c, 'test')['curve_uid'])
        f = {**FIELD, 'modulus_exponents': [13, 7, 0]}
        self.assertNotEqual(original['curve_uid'], identity.curve_identity(f, self.curve, 'test')['curve_uid'])

    def test_alias_is_not_hash_input_and_collision_detected(self):
        i = identity.curve_identity(FIELD, self.curve, 'test')
        m = {'field': FIELD, 'curve': {**self.curve, 'curve_id': i['curve_id']}}
        self.assertEqual(i, identity.inspect_manifest(m))
        m['curve']['generator'] = [8, 9]
        with self.assertRaises(ValueError): identity.inspect_manifest(m)

    def test_methods_share_curve_but_not_candidate(self):
        i = identity.curve_identity(FIELD, self.curve, 'test')
        m = {'field': FIELD, 'curve': {**self.curve, 'curve_id': i['curve_id']}, 'method': 'pollard-rho', 'factor_base': 'none', 'isogeny': 'none'}
        n = copy.deepcopy(m); n['method'] = 'index-calculus'; n['factor_base'] = {'artifact_sha256': 'a'*64}
        self.assertEqual(identity.inspect_manifest(m), identity.inspect_manifest(n))
        self.assertNotEqual(identity.candidate_identity(m), identity.candidate_identity(n))
        n['isogeny'] = {'map_sha256': 'b'*64}
        self.assertNotEqual(identity.candidate_identity(m), identity.candidate_identity(n))

    def test_prime_and_nonbinary_extension_namespaces(self):
        for p,n,prefix in [(17,1,'EC1P5'), (3,2,'EC1Q3D2')]:
            f = {**FIELD,'characteristic':p,'degree':n}
            self.assertTrue(identity.curve_identity(f,self.curve,'test')['curve_id'].startswith(prefix))
        with self.assertRaises(ValueError): identity.curve_identity({'degree':13}, self.curve, 'test')

if __name__ == '__main__': unittest.main()
