"""Finite arithmetic regression fixtures; no solver, campaign or sampled trials."""
import itertools
import math
import unittest
from collections import Counter
from fractions import Fraction


def negacyclic(a, b, modulus):
    n = len(a)
    out = [0] * n
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[(i + j) % n] += x * y * (1 if i + j < n else -1)
    return tuple(x % modulus for x in out)


def encode_wots(digits, base):
    checksum = sum(base - 1 - x for x in digits)
    width = 1
    while base ** width <= len(digits) * (base - 1):
        width += 1
    encoded = tuple((checksum // base ** i) % base for i in reversed(range(width)))
    return tuple(digits) + encoded


class StaticCounterexamples(unittest.TestCase):
    def test_even_challenges_share_nonzero_kernel(self):
        for bits in (1, 2, 4):
            modulus = 2 ** bits
            kernel = (modulus // 2,) * 8
            for challenge in itertools.product((0, 1), repeat=8):
                if sum(challenge) % 2 == 0:
                    self.assertEqual(negacyclic(challenge, kernel, modulus), (0,) * 8)
            self.assertNotEqual(kernel, (0,) * 8)

    def test_invertible_challenge_random_rhs_is_consistent(self):
        identity = (1, 0, 0, 0)
        for rhs in itertools.product(range(4), repeat=4):
            self.assertEqual(negacyclic(identity, rhs, 4), rhs)

    def test_sign_truncation_does_not_truncate_support(self):
        count = math.comb(256, 39)
        self.assertGreater(count, 2 ** 153)
        self.assertLess(count, 2 ** 154)
        self.assertAlmostEqual(math.log2(count), 153.76030421645666)

    def test_fresh_shares_retain_joint_secret(self):
        for secret in (0, 1):
            shares = [(r, secret ^ r) for r in (0, 1)]
            self.assertEqual(Counter(x for x, _ in shares), Counter({0: 1, 1: 1}))
            self.assertEqual({x ^ y for x, y in shares}, {secret})

    def test_zero_matrix_public_observation_cannot_identify_s1(self):
        # Fixed rho, A=0 and s2=0 give t=0, hence the same rounded t1.
        secrets = ((0,) * 8, (1,) + (0,) * 7)
        observed = [negacyclic((0,) * 8, s, 8380417) for s in secrets]
        self.assertNotEqual(secrets[0], secrets[1])
        self.assertEqual(observed[0], observed[1])
        self.assertEqual(tuple(x >> 13 for x in observed[0]), (0,) * 8)

    def test_fixed_target_and_pair_collision_are_different(self):
        h, n = 16, 256
        fixed = 1 - (1 - Fraction(1, 2 ** h)) ** n
        self.assertLess(fixed, Fraction(1, 250))
        pair_expectation = Fraction(n * (n - 1), 2 * 2 ** h)
        self.assertGreater(pair_expectation, Fraction(49, 100))
        self.assertEqual(math.sqrt(2 ** h / 0.25), 2 * math.sqrt(2 ** h))

    def test_structured_payload_is_publicly_distinguishable(self):
        honest_prefixes = tuple(itertools.product((0, 1), repeat=4))
        self.assertEqual(sum(p == (0, 0, 0, 0) for p in honest_prefixes), 1)
        self.assertEqual(Fraction(1, len(honest_prefixes)), Fraction(1, 16))

    def test_ring_degree_changes_crt_structure(self):
        self.assertNotEqual((257 - 1) % (2 * 256), 0)
        self.assertEqual(sum(pow(a, 256, 257) == 256 for a in range(257)), 0)
        self.assertEqual((3329 - 1) % (2 * 64), 0)
        self.assertEqual(sum(pow(a, 64, 3329) == 3328 for a in range(3329)), 64)

    def test_target_embedding_can_break_rotation(self):
        # L = span_Z((2,0,0),(0,2,0),(1,0,1)); first-coordinate
        # rotation of the target row is not in this target embedding.
        member = lambda x: (x[0] - x[2]) % 2 == 0 and x[1] % 2 == 0
        self.assertTrue(member((1, 0, 1)))
        self.assertFalse(member((0, 1, 1)))

    def test_alarm_confirmation_counterexample(self):
        p, epsilon, k = Fraction(1, 2 ** 14), Fraction(1, 100), 6
        alarm_probability = p + (1 - p) * epsilon
        multiplier = 1 + k * alarm_probability
        false_to_true = (1 - p) * epsilon ** (k + 1) / p
        self.assertLess(multiplier, Fraction(107, 100))
        self.assertLess(false_to_true, Fraction(1, 10 ** 9))
        self.assertGreater((1 + epsilon / p) * k, 900)

    def test_parallel_efficiency_and_planted_ratio_directions(self):
        serial, workers, efficiency = 2 ** 20, 16, Fraction(1, 2)
        elapsed = serial / (workers * efficiency)
        self.assertEqual(math.log2(elapsed), 20 - 4 - (-1))
        self.assertLess(Fraction(12, 10), Fraction(12, 4))

    def test_cbd2_exact_moments(self):
        law = Counter(a + b - c - d for a, b, c, d in itertools.product((0, 1), repeat=4))
        variance = sum(Fraction(n * x * x, 16) for x, n in law.items())
        fourth = sum(Fraction(n * x ** 4, 16) for x, n in law.items())
        self.assertEqual(variance, 1)
        self.assertEqual(fourth, Fraction(5, 2))
        self.assertEqual(fourth / variance ** 2 - 3, Fraction(-1, 2))
        self.assertEqual(sum(Fraction(x * x, 5) for x in range(-2, 3)), 2)

    def test_dimension_and_memory_contracts(self):
        for dimension in (50, 70):
            self.assertNotEqual(dimension % 4, 0)
        self.assertEqual(17 ** 8 * 16, 111612119056)
        self.assertGreater(17 ** 8 * 16, 32 * 2 ** 30)
        self.assertGreater(17 ** 8, 41 ** 4)

    def test_wots_full_encoding_is_antichain(self):
        for base, length in ((4, 3), (16, 2)):
            encodings = [encode_wots(d, base) for d in itertools.product(range(base), repeat=length)]
            self.assertEqual(len(set(encodings)), len(encodings))
            for a in encodings:
                for b in encodings:
                    if a != b:
                        self.assertFalse(all(x <= y for x, y in zip(a, b)))

    def test_multiple_disclosures_reach_from_minimum(self):
        observed = (2, 7)
        reachable = set().union(*(set(range(i, 16)) for i in observed))
        self.assertEqual(reachable, set(range(min(observed), 16)))
        self.assertNotEqual(reachable, set(range(max(observed), 16)))

    def test_address_headroom_and_layer_parameters(self):
        self.assertEqual(64 - (66 - 66 // 22), 1)
        self.assertEqual(64 - (68 - 68 // 17), 0)
        self.assertNotEqual(8 % 3, 0)
        self.assertNotEqual(9 % 4, 0)
        self.assertEqual(2 - 2, 0)
        self.assertEqual(sum(2 ** (3 * j) for j in range(0)), 0)

    def test_collision_statistics_and_cost_ratio(self):
        expected = Fraction(10 ** 6, 2 ** 64)
        self.assertLess(expected, Fraction(6, 10 ** 14))
        upper = -math.expm1(math.log(0.05) / 10 ** 6)
        self.assertGreater(upper, 2.99e-6)
        self.assertLess(upper, 3e-6)
        self.assertEqual(Fraction(2 ** (32 - 24), 64), 4)
        self.assertEqual(Fraction(2 ** (32 - 24), 8), 32)

    def test_importance_sampling_requires_nominal_support(self):
        nominal = {x for x in itertools.product((0, 1), repeat=4) if sum(x) == 1}
        proposal = {x for x in itertools.product((0, 1), repeat=4) if sum(x) == 2}
        self.assertTrue(nominal)
        self.assertTrue(proposal)
        self.assertTrue(nominal.isdisjoint(proposal))
        # The nominal indicator expectation is 1; every proposal draw gives 0.
        self.assertEqual(sum(x in nominal for x in proposal), 0)

    def test_key_relabeling_preserves_tail(self):
        rates = [Fraction(1, 100), Fraction(2, 100), Fraction(9, 100)]
        tail_ratio = lambda x: max(x) / sorted(x)[len(x) // 2]
        for permuted in itertools.permutations(rates):
            self.assertEqual(tail_ratio(permuted), tail_ratio(rates))


if __name__ == '__main__':
    unittest.main()
