"""Pins the refutation of Lemma 4's inside form, and the bugs it survived.

Two of these tests exist because an implementation of this exact quantity was
WRONG in a way that still produced plausible integers -- once in a blind read
whose artifacts were lost (`CORR-20260921-942a62`), and twice in
`tools/lemma4_inside_form.py` itself during the same session that wrote it. A
refuted lemma that the campaign records as a dependency is not something to
leave resting on an unpinned hand-rolled eliminator.
"""

import unittest

import random

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
    monomials_up_to,
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


class TestTheGeReadingVoidsOnlyOnePlacement(unittest.TestCase):
    """The `>=` void is narrower than this program first recorded it.

    `DEC-20260916-87fc5c`'s third limitation says flatly that the refutation is
    "void under the literal '>=' reading printed in 2015/984, under which the
    inequality holds and is empty". `AMD-EXP-SEMBIN-4fa22c-20260921-lemma4`'s
    `recorded_tension` T-1 flagged that the Nagao reader's own table disagrees,
    and declined to adjudicate. These tests adjudicate it arithmetically.

    The void covers the placement with `S_fe` INSIDE the true system and NOT the
    placement with it OUTSIDE. Both readings and both placements are pinned for
    both witnesses, so the four-way table cannot drift again: it is the table,
    and not any one cell of it, that the scope statement has to match.

    What these tests do NOT settle is a textual question -- which placement
    Lemma 4 as printed uses on the true side. That is read off a frozen source,
    not computed here.
    """

    WITNESSES = (
        ("A", [frozenset({(2, 1)}), frozenset({(1, 1), (1, 0)})], 2),
        ("B", [WITNESS_F1, WITNESS_F2], 3),
    )

    def test_the_ge_void_does_not_reach_the_outside_placement(self):
        for name, gens, n in self.WITNESSES:
            with self.subTest(witness=name):
                fake = first_fall_degree(gens + field_equations(n), fake=True, n=n)
                inside = least_degree_in_ideal(gens + field_equations(n), fake=False, n=n) + 1
                outside = least_degree_in_ideal(gens, fake=False, n=n) + 1
                self.assertEqual(fake, 2)
                # Inside: collapses onto d'_F, so the inequality holds and is empty.
                self.assertEqual(inside, 2)
                # Outside: still strictly above, so the refutation survives `>=`.
                self.assertEqual(outside, 3)
                self.assertGreater(outside, fake)

    def test_the_outside_value_is_exact_and_not_merely_an_upper_bound(self):
        """This is the load-bearing step, and the one a bound could have faked.

        `least_degree_in_ideal` searches cofactors only to a fixed degree, so it
        returns an UPPER bound: a longer search can only find something smaller.
        A smaller value for the outside placement would drag `d_F` down to 2 and
        void the refutation after all, so the whole finding rests on 2 being the
        exact least degree rather than the least degree found so far.

        For witness A it is exact, by an argument short enough to check by hand.
        Every generator of `(X^2 Y, XY + X)` is divisible by `X`, hence so is
        every element of the ideal, so nothing of degree 0 is in it. Degree 1
        would need `X` itself, which would need `g_1 X Y + g_2 (Y + 1) = 1`;
        modulo `Y + 1` that reads `g_1 X = 1`, impossible in a polynomial ring.
        So the least degree is at least 2, and `f_2 = X(Y + 1)` attains it.
        """
        f1, f2 = frozenset({(2, 1)}), frozenset({(1, 1), (1, 0)})
        gens = [f1, f2]
        self.assertEqual(least_degree_in_ideal(gens, fake=False, n=2), 2)

        # Widening the cofactor search cannot find anything smaller.
        for bound in (2, 4, 6):
            self.assertEqual(
                least_degree_in_ideal(gens, fake=False, n=2, cofactor_degree_bound=bound),
                2,
                msg=f"least ideal degree moved at cofactor bound {bound}",
            )

        # Every element of the ideal is divisible by X, checked directly over a
        # spanning set rather than argued: no product has a monomial free of X.
        for g in gens:
            for m in monomials_up_to(4, 2):
                prod = poly_mul_mono(g, m)
                for mono in prod:
                    self.assertGreaterEqual(
                        mono[0], 1, msg=f"{mono} in the ideal is not divisible by X"
                    )

    def test_the_equality_reading_refutes_both_placements(self):
        """Stated alongside so the two readings cannot be conflated.

        Under equality the refutation reaches both placements; under `>=` it
        reaches one. A scope note that names a reading without naming the
        placement is therefore underdetermined, which is how T-1 arose.
        """
        for name, gens, n in self.WITNESSES:
            with self.subTest(witness=name):
                fake = first_fall_degree(gens + field_equations(n), fake=True, n=n)
                for label, system in (
                    ("inside", gens + field_equations(n)),
                    ("outside", gens),
                ):
                    self.assertGreater(
                        first_fall_degree(system, fake=False, n=n),
                        fake,
                        msg=f"equality reading held for witness {name} {label}",
                    )


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


class TestTheFakeSidePlacementIsInert(unittest.TestCase):
    """Adjoining `S_fe` to the FAKE system changes nothing.

    This campaign spent a round treating "inside" versus "outside" as the
    distinction that decided Lemma 4's truth value, where those words referred
    to which side of `d'_F` the field equations sat on. They decide nothing
    there: every `X_i^2 + X_i` reduces to zero under the fake degree, so it
    contributes no product at any degree and drops out of all three of
    Definition 6's conditions. The placement that does decide the truth value is
    on the TRUE side, and that is what `TestTheRefutation` pins.

    Found independently by the blind read at `TASK-20260916-9da6e0`, which never
    read this module, and reproduced here against it.
    """

    def test_the_field_equations_reduce_to_nothing(self):
        for fe in field_equations(3):
            self.assertEqual(reduce_fe(fe), frozenset())

    def test_adjoining_them_does_not_move_the_fake_degree(self):
        bare = [WITNESS_F1, WITNESS_F2]
        self.assertEqual(
            first_fall_degree(bare, fake=True, n=3),
            first_fall_degree(bare + field_equations(3), fake=True, n=3),
        )

    def test_inertness_is_not_an_accident_of_the_witness(self):
        """300 random multilinear pairs, zero disagreements.

        A single instance cannot distinguish "inert" from "happens to agree
        here", and the claim being pinned is universal.
        """
        rng = random.Random(20260921)
        monos = list(monomials_up_to(3, 3, multilinear=True))
        for _ in range(300):
            fs = [
                frozenset(rng.sample(monos, rng.randint(1, 4)))
                for _ in range(2)
            ]
            self.assertEqual(
                first_fall_degree(fs, fake=True, n=3),
                first_fall_degree(fs + field_equations(3), fake=True, n=3),
                msg=f"fake-side placement moved d'_F on {sorted(map(sorted, fs))}",
            )


class TestTheSecondIndependentWitness(unittest.TestCase):
    """`f_1 = X^2 Y`, `f_2 = XY + X` over `F_2[X, Y]`.

    Constructed by the blind read at `TASK-20260916-9da6e0` without access to
    this module, and recomputed here by this module without reference to that
    reader's arithmetic. Agreement is therefore evidence about the quantities
    rather than about either implementation -- which is the point of a blind
    re-derivation as against a replication.

    It is a genuinely different object from `WITNESS_F1`/`WITNESS_F2`: two
    variables rather than three, and not multilinear.
    """

    F1 = frozenset({(2, 1)})              # X^2 Y
    F2 = frozenset({(1, 1), (1, 0)})      # XY + X

    def system(self, with_fe):
        gens = [self.F1, self.F2]
        return gens + field_equations(2) if with_fe else gens

    def test_the_reported_numbers_reproduce(self):
        self.assertEqual(first_fall_degree(self.system(True), fake=True, n=2), 2)
        self.assertEqual(first_fall_degree(self.system(False), fake=False, n=2), 3)

    def test_it_refutes_lemma_4_under_both_true_side_placements(self):
        fake = first_fall_degree(self.system(True), fake=True, n=2)
        for with_fe in (True, False):
            true = first_fall_degree(self.system(with_fe), fake=False, n=2)
            self.assertGreater(
                true,
                fake,
                msg=f"d_F <= d'_F held with S_fe {'inside' if with_fe else 'outside'}",
            )

    def test_this_witness_is_not_multilinear_unlike_the_first(self):
        """Pinned so the two witnesses cannot silently collapse into one.

        If a later refactor normalised generators into the Boolean quotient,
        this witness would become `XY`, and the test above would be checking a
        different object while still passing under a lenient assertion.
        """
        self.assertNotEqual(self.F1, reduce_fe(self.F1))
        self.assertEqual(deg(self.F1), 3)


class TestTheFirstWitnessRefutesBothPlacementsToo(unittest.TestCase):
    def test_both_true_side_placements_fail(self):
        """The inside placement is the harder one, and it fails as well.

        Adjoining `S_fe` to the true system can only add products, so it gives a
        fall more chances to appear and cannot raise `d_F` above its value
        without them. Refuting the inequality in that setting is therefore the
        stronger of the two statements, and it is the one this module's witness
        makes.
        """
        bare = [WITNESS_F1, WITNESS_F2]
        fake = first_fall_degree(witness_system(), fake=True, n=3)
        self.assertEqual(first_fall_degree(witness_system(), fake=False, n=3), 3)
        self.assertEqual(first_fall_degree(bare, fake=False, n=3), 3)
        self.assertGreater(3, fake)


if __name__ == "__main__":
    unittest.main(verbosity=2)
