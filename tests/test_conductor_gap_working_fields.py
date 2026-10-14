import csv
import json
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PANEL_DIR = ROOT / "research" / "conductor_gap_panel_20261014"


def matrix_multiply(left, right, modulus):
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(2)) % modulus
            for j in range(2)
        ]
        for i in range(2)
    ]


def matrix_power(matrix, exponent, modulus):
    answer = [[1, 0], [0, 1]]
    base = [[entry % modulus for entry in row] for row in matrix]
    while exponent:
        if exponent & 1:
            answer = matrix_multiply(answer, base, modulus)
        base = matrix_multiply(base, base, modulus)
        exponent >>= 1
    return answer


def matrix_vector(matrix, vector, modulus):
    return [
        sum(matrix[i][j] * vector[j] for j in range(2)) % modulus
        for i in range(2)
    ]


def distinct_prime_factors(value):
    factors = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            factors.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor += 1 if divisor == 2 else 2
    if value > 1:
        factors.append(value)
    return factors


def projectively_equal(left, right, modulus):
    return (left[0] * right[1] - left[1] * right[0]) % modulus == 0


class ConductorGapWorkingFieldTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel = json.loads((PANEL_DIR / "panel.json").read_text())
        cls.gaps = {
            (row["class_id"], int(row["edge_degree"])): row
            for row in cls.panel["gaps"]
        }

    def test_only_two_rows_claim_exact_abstract_representative_orbit(self):
        self.assertEqual(self.panel["schema"], "crypto.conductor-gap-panel/v2")
        exact_keys = {
            key for key, row in self.gaps.items()
            if row["working_field_status"]
            == "exact_abstract_cm_representative_x_orbit"
        }
        self.assertEqual(exact_keys, {("nist-k163", 45641), ("nist-k283", 1697)})
        self.assertEqual(self.panel["summary"]["exact_absolute_x_orbit_rows"], 2)
        self.assertEqual(self.panel["summary"]["concrete_kernel_x_orbit_rows"], 1)
        self.assertEqual(
            self.panel["summary"]["ambient_upper_bound_working_field_rows"], 41
        )
        for key, row in self.gaps.items():
            if key in exact_keys:
                self.assertIsInstance(row["working_field_certificate"], dict)
            else:
                self.assertEqual(
                    row["working_field_status"],
                    "certified_ambient_upper_bound_only",
                )
                self.assertIsNone(row["working_field_certificate"])
                self.assertIsNone(
                    row["exact_abstract_cm_representative_x_orbit_degree"]
                )
                self.assertEqual(row["concrete_kernel_x_orbit_status"],
                                 "not_certified")
                self.assertIsNone(row["concrete_kernel_x_orbit_degree"])

    def test_exact_cm_line_orbit_witnesses(self):
        fixtures = {
            ("nist-k163", 45641): {
                "mu": 1, "m": 163, "k": 20, "scalar": 7196,
                "concrete": True,
            },
            ("nist-k283", 1697): {
                "mu": -1, "m": 283, "k": 848, "scalar": 1669,
                "concrete": False,
            },
        }
        for key, fixture in fixtures.items():
            with self.subTest(key=key):
                row = self.gaps[key]
                ell = key[1]
                m = fixture["m"]
                k = fixture["k"]
                n = m * k
                self.assertEqual(math.gcd(m, k), 1)
                matrix = [[0, -2], [1, fixture["mu"]]]
                vector = [1, 0]
                identity = [[1, 0], [0, 1]]
                negative_identity = [[ell - 1, 0], [0, ell - 1]]
                q_matrix = matrix_power(matrix, m, ell)
                self.assertEqual(
                    q_matrix,
                    [[fixture["scalar"], 0], [0, fixture["scalar"]]],
                )
                self.assertTrue(
                    projectively_equal(matrix_vector(q_matrix, vector, ell),
                                       vector, ell)
                )
                certificate = row["working_field_certificate"]
                line_items = certificate["line_factor_exclusion_images"]
                self.assertEqual(
                    {int(item["prime_divisor"]) for item in line_items},
                    set(distinct_prime_factors(m)),
                )
                self.assertEqual(len(line_items), len(distinct_prime_factors(m)))
                for item in line_items:
                    prime = int(item["prime_divisor"])
                    exponent = m // prime
                    image = matrix_vector(
                        matrix_power(matrix, exponent, ell), vector, ell
                    )
                    self.assertFalse(projectively_equal(image, vector, ell))
                    self.assertEqual(int(item["exponent"]), exponent)
                    self.assertEqual([int(value) for value in item["image"]], image)

                full_matrix = matrix_power(matrix, n, ell)
                self.assertIn(full_matrix, (identity, negative_identity))
                full = matrix_vector(full_matrix, vector, ell)
                self.assertIn(full, ([1, 0], [ell - 1, 0]))
                self.assertEqual(
                    [int(value) for value in certificate["full_orbit_image"]], full
                )
                absolute_items = certificate["factor_exclusion_images"]
                self.assertEqual(
                    {int(item["prime_divisor"]) for item in absolute_items},
                    set(distinct_prime_factors(n)),
                )
                self.assertEqual(
                    len(absolute_items), len(distinct_prime_factors(n))
                )
                for item in absolute_items:
                    prime = int(item["prime_divisor"])
                    exponent = n // prime
                    image = matrix_vector(
                        matrix_power(matrix, exponent, ell), vector, ell
                    )
                    self.assertNotIn(image, ([1, 0], [ell - 1, 0]))
                    self.assertEqual(int(item["exponent"]), exponent)
                    self.assertEqual(
                        [int(value) for value in item["image"]], image
                    )
                self.assertEqual(
                    int(row["ambient_absolute_x_degree_upper_bound"]), n
                )
                self.assertEqual(
                    int(row["exact_abstract_cm_representative_x_orbit_degree"]),
                    n,
                )
                closure_sign = -1 if full_matrix == negative_identity else 1
                self.assertEqual(
                    certificate["absolute_x_orbit_closure_sign"], closure_sign
                )
                self.assertEqual(
                    int(certificate["exact_full_point_orbit_degree"]),
                    2 * n if closure_sign == -1 else n,
                )
                binding = certificate["concrete_point_binding"]
                if fixture["concrete"]:
                    self.assertEqual(
                        row["concrete_kernel_x_orbit_status"],
                        "certified_retained_relative_tower_witness",
                    )
                    self.assertEqual(int(row["concrete_kernel_x_orbit_degree"]), n)
                    self.assertEqual(
                        binding["status"], "certified_concrete_kernel_x_witness"
                    )
                    self.assertTrue(
                        binding["retained_input_replay_path"].endswith(
                            "verify163_45641_relative_witness.out"
                        )
                    )
                    self.assertEqual(
                        binding["arithmetic_independence"],
                        "not_independent_same_x_only_ladder_family",
                    )
                    self.assertEqual(
                        [int(value) for value in
                         binding["proper_divisor_exclusion_degrees"]],
                        [n // prime for prime in distinct_prime_factors(n)],
                    )
                    self.assertEqual(
                        binding["all_nonzero_kernel_multiples_status"],
                        "derived",
                    )
                else:
                    self.assertEqual(row["concrete_kernel_x_orbit_status"],
                                     "not_certified")
                    self.assertIsNone(row["concrete_kernel_x_orbit_degree"])
                    self.assertEqual(binding, {"status": "not_certified"})

    def test_csv_preserves_working_field_status(self):
        with (PANEL_DIR / "gap-panel.csv").open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 43)
        self.assertIn("working_field_status", rows[0])
        self.assertIn("working_field_certificate", rows[0])
        self.assertIn("concrete_kernel_x_orbit_status", rows[0])
        exact = [
            row for row in rows
            if row["working_field_status"]
            == "exact_abstract_cm_representative_x_orbit"
        ]
        self.assertEqual(len(exact), 2)


if __name__ == "__main__":
    unittest.main()
