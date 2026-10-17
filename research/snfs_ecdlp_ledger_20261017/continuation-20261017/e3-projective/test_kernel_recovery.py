"""Deterministic known-answer software fixtures, not an ECDLP campaign."""
import unittest
from sage.all import EllipticCurve, GF
from kernel_recovery import recover


class KernelRecoveryFixtures(unittest.TestCase):
    def setUp(self):
        # E/F_17 has 19 points; G=(5,1) has order 19. All scalars are fixture data.
        self.curve = EllipticCurve(GF(17), [2, 2])
        self.g = self.curve(5, 1)
        self.images = [self.g, 4*self.g]
        self.relations = [[19, 0], [-4, 1]]
        self.vg, self.vq = [1, 0], [3, 1]

    def call(self, **changes):
        args = dict(curve=self.curve, subgroup_order=19, generator=self.g,
                    target=7*self.g, images=self.images, relations=self.relations,
                    generator_coordinates=self.vg, target_coordinates=self.vq)
        args.update(changes)
        return recover(**args)

    def test_full_index_recovers_known_answer(self):
        result = self.call()
        self.assertEqual(result["scalar"], 7)
        self.assertEqual(result["relation_index"], 19)

    def test_more_rows_can_certify_full_kernel(self):
        # First two independent rows generate index 38; the third supplies the
        # missing coset. Merely finding two independent relations is insufficient.
        self.assertEqual(self.call(relations=[[38, 0], [-4, 1], [19, 0]])["scalar"], 7)

    def test_independent_proper_sublattice_refused(self):
        with self.assertRaisesRegex(ValueError, "proper index"):
            self.call(relations=[[38, 0], [-4, 1]])

    def test_dependent_and_false_relations_refused(self):
        with self.assertRaisesRegex(ValueError, "full integer rank"):
            self.call(relations=[[19, 0], [38, 0]])
        with self.assertRaisesRegex(ValueError, "does not specialize"):
            self.call(relations=[[19, 0], [-3, 1]])

    def test_target_coordinates_and_group_order_refused(self):
        with self.assertRaisesRegex(ValueError, "coordinates"):
            self.call(target_coordinates=[2, 1])
        with self.assertRaisesRegex(ValueError, "prime order"):
            self.call(subgroup_order=17)


if __name__ == "__main__":
    unittest.main(verbosity=2)
