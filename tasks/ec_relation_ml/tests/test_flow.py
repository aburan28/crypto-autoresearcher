"""Mathematical and leakage failures, not timing acceptance tests."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from audit import connected_components
from bridge import (all_points, equations, features, from_case, generate,
                    relation_evaluation, scalar_roots, summation_polynomial,
                    validate_case, validate_splits)
from ec import Curve, RelationSystem, bsgs


class ExactRelationTests(unittest.TestCase):
    def setUp(self):
        self.curve = Curve(17,2,2,19,1,(5,1))
        self.p = self.curve.mul(5,self.curve.g)
        self.q = self.curve.mul(7,self.curve.g)

    def test_rank_does_not_imply_recovery(self):
        system = RelationSystem(self.curve,[self.p],{"q":self.q})
        self.assertEqual(system.insert([(2,self.p),(-1,self.q)],constant=-3),1)
        self.assertEqual(len(system.basis),1)
        self.assertEqual(system.recoveries(),{})
        self.assertEqual(system.insert([(1,self.p)],constant=-5),1)
        self.assertEqual(system.recoveries(),{"q":7})
        self.assertEqual(system.summary(),system.summary())

    def test_aliases_and_negations_add_no_information(self):
        system = RelationSystem(self.curve,[self.p,self.curve.neg(self.p),self.p],{"q":self.q})
        self.assertEqual(len(system.columns),2)
        self.assertEqual(system.insert([(3,self.p),(3,self.curve.neg(self.p))]),0)
        self.assertEqual(system.insert([(1,self.p)],constant=-5),1)
        self.assertEqual(system.insert([(2,self.p)],constant=-10),0)
        self.assertEqual(system.insert([(-1,self.curve.neg(self.p))],constant=-5),0)
        self.assertEqual(len(system.basis),1)

    def test_false_relations_and_invalid_points_rejected(self):
        system = RelationSystem(self.curve,[self.p],{"q":self.q})
        with self.assertRaisesRegex(ValueError,"false"):
            system.insert([(1,self.p),(1,self.q)])
        self.assertEqual(system.verified,0)
        with self.assertRaisesRegex(ValueError,"outside"):
            RelationSystem(self.curve,[(0,0)],{"q":self.q})

    def test_known_log_and_generator_sign(self):
        reverse = Curve(17,2,2,19,1,(5,16))
        system = RelationSystem(reverse,[],{"q":reverse.neg(reverse.g),"zero":None})
        self.assertEqual(system.recoveries(),{"q":18,"zero":0})
        self.assertEqual(len(system.basis),0)

    def test_cofactor_and_rank_two_torsion_rejected(self):
        with self.assertRaisesRegex(ValueError,"cofactor"):
            Curve(17,2,2,19,2,(5,1))
        found = False
        for a in range(19):
            for b in range(19):
                pts = all_points(19,a,b)
                if len(pts)==24 and (4*a**3+27*b*b)%19:
                    with self.assertRaisesRegex(ValueError,"ambiguous"):
                        Curve(19,a,b,5,5,pts[0])
                    found = True
                    break
            if found:
                break
        self.assertTrue(found)

    def test_generic_scalar_recovery(self):
        for scalar in range(self.curve.n):
            self.assertEqual(bsgs(self.curve,self.curve.mul(scalar,self.curve.g))["scalar"],scalar)

    def test_summation_identity_including_equal_x(self):
        points = [self.curve.mul(i,self.curve.g) for i in range(1,self.curve.n)]
        for p in points:
            for q in points:
                target = self.curve.add(p,q)
                if target is not None:
                    self.assertEqual(summation_polynomial(p[0],q[0],target[0],2,2)%17,0)


class DataBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = generate("quick",20261011)

    def test_fields_disjoint_and_cases_valid(self):
        validate_splits(self.cases)
        for case in self.cases:
            validate_case(case)
        self.assertEqual(len(self.cases),24)

    def test_alias_change_cannot_hide_split_leakage(self):
        case = copy.deepcopy(self.cases[0])
        case.update({"id":"different","split":"test","curve_uid":"renamed","field_block":"renamed"})
        with self.assertRaisesRegex(ValueError,"leaks"):
            validate_splits([self.cases[0],case])

    def test_features_ignore_truth_metadata_and_outcomes(self):
        case = copy.deepcopy(self.cases[0])
        before = features(case)
        case.update({"seed":1,"scalar":999,"planted_root":[1,2],"root_count":7,
                     "curve_uid":"bad","id":"bad","split":"test","group_calls":0})
        self.assertEqual(features(case),before)

    def test_x_roots_are_lifted_to_exact_relations(self):
        for case in self.cases:
            roots = scalar_roots(case)
            result = relation_evaluation(case,roots)
            self.assertLessEqual(result["independent_rank"],result["unknown_log_count"])
            self.assertEqual(result["roots_without_base_field_witness"],0)
            curve = from_case(case)
            for scalar in result["verified_target_scalars"].values():
                self.assertEqual(curve.mul(scalar,curve.g),tuple(case["target"]))

    def test_system_tampering_is_rejected(self):
        case = copy.deepcopy(self.cases[0])
        case["polynomials"][0][0][0] = (case["polynomials"][0][0][0]+1)%case["curve"]["p"]
        with self.assertRaisesRegex(ValueError,"not the declared"):
            validate_case(case)

    def test_overlapping_sources_form_connected_holdouts(self):
        rows = [{"source":"A","curve":"one"},{"source":"B","curve":"one"},
                {"source":"B","curve":"two"},{"source":"C","curve":"three"}]
        self.assertEqual(connected_components(rows,("source","curve")),[3,1])


if __name__=="__main__":
    unittest.main()
