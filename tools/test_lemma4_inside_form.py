"""Pins the refutation of Lemma 4's inside form, and the bugs it survived.

Two of these tests exist because an implementation of this exact quantity was
WRONG in a way that still produced plausible integers -- once in a blind read
whose artifacts were lost (`CORR-20260921-942a62`), and twice in
`tools/lemma4_inside_form.py` itself during the same session that wrote it. A
refuted lemma that the campaign records as a dependency is not something to
leave resting on an unpinned hand-rolled eliminator.
"""

import unittest

from lemma4_inside_form import (
    WITNESS_F1,
    WITNESS_F2,
    check_witness,
    cross_check_eliminator,
    deg,
    field_equations,
    first_fall_degree,
    first_fall_degree_by_enumeration,
    least_degree_in_ideal,
    poly_add,
    poly_mul_mono,
    reduce_fe,
    survey_random_multilinear_pairs,
    witness_system,
)


class TestTheRefutation(unittest.TestCase):
    def test_inside_form_is_violated_on_the_witness(self):
        r = check_witness()
        self.assertEqual(r["d_F_inside"], 3)
        self.assertEqual(r["d_prime_F"], 2)
        self.assertFalse(r["inside_form_holds"])

    def test_refutation_does_not_depend_on_the_general_routine(self):
        """The four explicit facts must settle it by themselves.

        If this passes and `test_inside_form_is_violated_on_the_witness` fails,
        the refutation stands and the general routine broke.
        """
        r = check_witness()
        self.assertTrue(r["refutation_stands_without_general_routine"])
        self.assertEqual(r["falls_found_at_D2"], [])
        self.assertEqual(r["scalar_combinations_tested_at_D2"], 31)
        self.assertEqual(r["degree_one_products_found"], [])
        self.assertTrue(r["d_F_at_most_3_witness"]["is_a_fall_at_3"])

    def test_the_stated_cofactors_really_are_a_degree_2_fall(self):
        """Recompute g_1 = 1, g_2 = X_1 + 1 from scratch."""
        x1 = (1, 0, 0)
        g2f2 = poly_add(poly_mul_mono(WITNESS_F2, x1), WITNESS_F2)
        self.assertEqual(deg(reduce_fe(WITNESS_F1)), 2)
        self.assertEqual(deg(reduce_fe(g2f2)), 2)
        total = poly_add(reduce_fe(WITNESS_F1), reduce_fe(g2f2))
        self.assertTrue(total)
        self.assertEqual(deg(total), 1)
        self.assertEqual(sorted(total), [(0, 0, 1), (0, 1, 0)])  # X_2 + X_3


class TestTheEliminatorAgreesWithLiteralEnumeration(unittest.TestCase):
    def test_no_disagreement_on_random_tiny_systems(self):
        c = cross_check_eliminator()
        self.assertEqual(c["disagree"], 0, c["mismatches"])
        self.assertGreaterEqual(c["decisions"], 40)

    def test_condition_one_equality_is_enforced(self):
        """The bug the oracle caught, pinned as its own case.

        `f_1 = f_2 = X_1X_2` over `F_2` in two variables: every admissible
        product is `X_1X_2` of degree 2, so NO degree can be the maximum of a
        witness and the quantity is undefined. An eliminator that only hunts for
        a low-degree element in the span reports a fall at `D = 3`, where nothing
        of degree 3 exists at all.
        """
        f = frozenset({(1, 1)})
        system = [f, f] + field_equations(2)
        self.assertIsNone(first_fall_degree(system, fake=True, n=2, dmax=4))
        self.assertIsNone(
            first_fall_degree_by_enumeration(system, fake=True, n=2, dmax=4)
        )


class TestTheGeReadingScopeNote(unittest.TestCase):
    def test_least_ideal_degree_finds_the_degree_one_element(self):
        """The ideal contains `X_2 + X_3`, so the least degree is 1, not 2.

        Pinned because the first implementation reduced basis-first and read
        degrees off the reduced basis, which returned 2: a reduced basis need
        not contain a minimal-degree element even when the span does.
        """
        self.assertEqual(least_degree_in_ideal(witness_system(), fake=False), 1)
        self.assertEqual(least_degree_in_ideal(witness_system(), fake=True), 1)


class TestTheFailureIsNotPathological(unittest.TestCase):
    def test_a_substantial_fraction_of_random_pairs_violate_it(self):
        """A floor, not an exact count -- the point is that it is not rare.

        Asserted as a floor for the reason the repository asserts corpus floors:
        an exact number here would pin an implementation detail of the sampler
        rather than the fact being claimed.
        """
        s = survey_random_multilinear_pairs(trials=200, seed=20260916)
        self.assertEqual(s["undetermined"], 0)
        self.assertGreater(s["d_F_exceeds_d_prime_F"], s["trials"] // 20)
        self.assertEqual(
            s["d_F_exceeds_d_prime_F"] + s["equal"] + s["d_F_below_d_prime_F"],
            s["trials"],
        )


class TestWhatIsNotClaimed(unittest.TestCase):
    def test_the_witness_polynomials_are_ordinary(self):
        """Neither generator is a unit, both are multilinear of degree 2.

        Pinned because the cheapest dismissal of a counterexample is that it is
        degenerate, and these two are not.
        """
        for f in (WITNESS_F1, WITNESS_F2):
            self.assertEqual(deg(f), 2)
            self.assertEqual(f, reduce_fe(f))          # already multilinear
            self.assertNotIn((0, 0, 0), f)             # no constant term
            self.assertEqual(len(f), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
